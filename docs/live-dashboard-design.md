# Live Project Dashboard — design

A single-file, dependency-free HTTP server that renders one in-progress project as a
live HTML page: where it is in the lifecycle, what the agent has done, and what exists
on disk. The operator opens it in a browser tab and watches the co-scientist work.

**Scope.** One project, one process, read-only, disposable. It is *not* the deployed
observatory (`ui/`), which is Postgres-backed, auth'd, and renders *finished* projects
imported from GitHub. This renders the working directory as it is right now.

**This document records decisions and the evidence behind them — mostly why things were
*not* built.** How the code works is documented in `tools/dashboard.py` itself, next to
the code, where it cannot drift. Nothing here should restate a docstring; if it does,
delete it here.

## Why a server, and why this one

The agent's primary runtime is a terminal inside JupyterHub. Per `PROJECT.md`, BERDL runs
on Kubernetes with ephemeral pods and no SSH, so a process bound to `127.0.0.1` in the
pod is unreachable from the operator's browser without a proxy.

`jupyter-server-proxy` solves it with no configuration: `setup_handlers()` registers
`url_path_join(base_url, r"/proxy/(\d+)(/.*|)")` **unconditionally at server startup**.
The port is a regex capture group, not a config key — nothing to register, no config
change, no Jupyter restart. Verified end-to-end against jupyter-server 2.20.0 +
jupyter-server-proxy 4.5.0 with no config file: an unrelated uvicorn on `:9911` was
reachable through the route.

Authentication is inherited, not implemented: `ProxyHandler.prepare()` runs
`web.authenticated(...)`, so the operator's existing MFA hub cookie authorizes and nobody
else can reach it.

**Detecting whether the proxy is enabled is harder than it looks**, and two obvious
implementations are both wrong. Asking `jupyter server extension list` cannot work: it
builds its config manager from a fixed three-tuple that structurally excludes
`~/.local/etc/jupyter`, so a `pip --user` install reads as "not enabled" while the running
server has it loaded. Reading only the shipped `jupyter-server-proxy.json` drop-in is also
wrong: `jupyter server extension disable` writes a *second* file,
`jupyter_server_proxy.json` (underscore), holding `false` into the same directory, and `_`
sorts after `-`, so it wins the real merge — reproduced, the naive probe returned "enabled"
for a disabled extension. `proxy_enabled()` therefore replicates jupyter_server's own merge.

## Two launchers, and the difference is deliberate

`tools/dashboard.py` carries a PEP 723 header declaring `mistune`. It is **inert to
`python3`** and honoured by `uv run` — verified: inside this project, `uv run
tools/dashboard.py` builds an isolated *script* env rather than reusing the repo venv.

| | markdown | env | needs network |
|---|---|---|---|
| `python3 tools/dashboard.py` — **the pod** | whatever the image ships (BERDL has mistune) | system | no |
| `uv run tools/dashboard.py` — **a laptop** | guaranteed | isolated script env | first run |

`uv run` does not inherit the interpreter's site-packages, so it is the wrong launcher for
the pod: it would re-fetch what the image already has and fail outright with no egress. Its
failure mode is *no dashboard*; the `python3` path's worst case is only degraded typography.
The skills therefore launch with `python3`.

Every third-party import stays inside a function behind `try/except`, enforced by
`test_module_level_imports_are_all_stdlib` — a top-level `import mistune` would pass the
whole suite locally and then fail to start on an image without it.

## Update transport — polling, not SSE

The page re-fetches its own URL every 4s and swaps `#root`. One route, one renderer, so no
drift between first paint and the Nth update.

**SSE was rejected, and not because it fails.** It demonstrably streams through the proxy —
measured 240 chunks over 120s, first byte at 0.09s. It is rejected because every
precondition fails *silently*:

- The streaming path is gated on `accept_header == "text/event-stream"` — raw string
  equality, no media-type parsing. Measured on otherwise-identical requests: exact header →
  240 chunks; `text/event-stream, */*` → **0 bytes in 130s**; header absent (which WHATWG
  explicitly permits a UA to do) → **0 bytes**.
- `_proxy_progressive` hard-caps at `request_timeout = 7200`, so a multi-hour run is
  guaranteed at least one forced disconnect no matter how you heartbeat.
- Cloudflare is confirmed live in front of the hub (`server: cloudflare`, `cf-ray`,
  `x-jupyterhub-version: 5.3.0`), adding a 125s origin read timeout.

A transport that fails silently is worse than one that is slightly late.

WebSockets are rejected outright: no server-side pings (tornado `websocket_ping_interval`
defaults to `None`; jupyter_server's own 30s interval covers kernel sockets only), no
auto-reconnect, and bidirectional capability a read-only page cannot use.

**Relative times must render client-side** from `data-epoch`. A server-rendered timestamp
freezes on a `304`, which would leave a green "alive" dot on a wedged agent — the exact
failure the dot exists to catch. It pays a second time in snapshot mode: the same code
ages an abandoned snapshot green → amber → grey against the *reader's* clock, so a stale
page reports itself.

**The snapshot cannot poll, and this is measured, not assumed.** Jupyter's `files/`
route answers `Content-Security-Policy: frame-ancestors 'none'; sandbox allow-scripts`
— no `allow-same-origin` — so the document has an opaque origin and `fetch` cannot send
the hub cookie. Scripts still run, which is why the page ships `REL_JS` there and
`POLL_JS` only in live mode. `POLL_JS`'s opening trailing-slash redirect is the more
dangerous half of that split: a snapshot lives at `…/dashboard.html`, so the line would
navigate the page to `dashboard.html/` and 404 it on load.

A manual reload does work — user-initiated top-level navigation is not the document
navigating itself — which is what makes "reload to refresh" an honest instruction.
Whether `<meta http-equiv="refresh">` would survive the same sandbox was **not**
tested; there is no browser on the image. If someone wants auto-refresh without the
extension, that is the experiment to run first.

## "The agent needs you" — and where the detail actually comes from

The dashboard says whether a human is currently blocking the run, and on what.
`.claude/hooks/agent_state.py` writes `projects/<id>/.agent-state.json`; the page
renders a chip, an amber strip, a `<title>` marker, a favicon dot and — opt-in — a
system notification.

**The documented shape is not the useful one, and that is a measured result.**
Claude Code 2.1.220 documents a `Notification` hook whose matcher filters on
`permission_prompt | agent_needs_input | idle_prompt | agent_completed`, and gives
no payload schema at all. Registering a throwaway logging hook and driving a real
session through a pty produced this, which no amount of reading the docs would have:

| Event | Fires | Carries |
|---|---|---|
| `PermissionRequest` | ~2s after the blocking call | `tool_name`, the whole `tool_input`, `permission_suggestions` |
| `Notification/permission_prompt` | ~6s after *that* | `message` — the constant `"Claude needs your permission"` |
| `Notification/idle_prompt` | exactly 60s after `Stop` | `"Claude is waiting for your input"` |
| `Stop` | end of every turn | `last_assistant_message`, `stop_hook_active` |
| `UserPromptSubmit` | on submit | `prompt` |

So the event the docs point at is both **later** and **less informative** than the
one they do not: the notification's message is a compile-time constant with no tool
and no argument in it. `PermissionRequest` is what records the detail. It is also
sound as a *trigger*, which was not obvious and had to be checked separately —
allowlisting `Bash(sw_vers:*)` and re-running the probe made it go silent, so it
fires only when a human is genuinely being asked, not on every permission decision.

`Notification` stays registered for one reason: `agent_needs_input` formats
`"<label> needs your input: <what>"`, which is real text that no `PermissionRequest`
precedes. Neither it nor `agent_completed` ever fired for the main session in any
probe — in the bundle both are emitted by the background-agent fleet tracker. The
hook therefore refuses to let a `Notification` overwrite a `waiting` that
`PermissionRequest` already described, since the later event knows strictly less.

Undocumented types also present in the matcher metadata, for whoever needs them
next: `auth_success`, `elicitation_dialog`, `elicitation_complete`,
`elicitation_response`.

**Nothing announces that a prompt was answered**, which is the second thing the
docs do not say and the one that produced a real bug report. Logging every hook
across an *approved* prompt gives the order:

```
PreToolUse  →  PermissionRequest  →  Notification  →  [human answers]  →  PostToolUse  →  Stop
```

`PreToolUse` fires *before* `PermissionRequest`, so it cannot mean granted.
`PostToolUse` is the first thing that happens only because a human said yes.
Without it the strip clears at `Stop` — the end of the whole turn — so approving
a `Skill` and watching the agent work for ten minutes under "the agent is waiting
for you" was the reported symptom. A banner that is wrong for minutes is worse
than no banner; the reader learns to ignore it.

That clear needs no project resolution: the state file records which session
wrote it, which is the whole question, and keeps one session from clearing
another's. It still costs 59ms against the resolving path's 78ms, of which 36ms
is bare `python3` startup — so this registration carries the same kind of shell
guard `beril-runtime.sh` uses and starts no interpreter when no state file
exists (6ms). The guard is nearly free rather than a compromise: between
`UserPromptSubmit` clearing the file and `Stop` writing the next one, a state
file exists *only* while a prompt is pending, which is exactly when it must run.

**A hidden tab now polls, at 15s rather than not at all.** The old guard —
`if(document.visibilityState==='visible')` around the `fetch` — made every channel
above impossible: the backgrounded tab is precisely the one that needs to learn the
agent is blocked, and the title and the favicon are painted from a response. A 304
still runs a full `scan()` at 6.8ms, so 15s hidden is ~1.6s of CPU per hour per tab,
less than a visible tab costs today.

**Three things are anchored outside `#root`, and each for a different failure.**
The strip, because inside `#root` it is destroyed and rebuilt every 4s and its
600ms pulse would restart each time — a flashing banner, WCAG 2.3.1, rather than
one highlight on the transition that earned it. The button, because
`requestPermission` needs a real user gesture and a handler bound to a node the
poll replaces would need re-binding. The title and favicon, because a 304 freezes
anything server-rendered — the same rule as relative times, and the same reason.

**The page must be able to stop believing itself.** "A human is blocked on this
*right now*" is the only present-tense claim it makes, and the only event that
retracts it is one Claude Code has to be alive to send. `SessionEnd` covers clean
exits; for a culled pod or a `SIGKILL` mid-prompt, `read_agent_state` downgrades
`waiting` to `unknown` after 30 minutes, or as soon as `runtime.json` turns out
never to have heard of the session that wrote the file. `turn_ended` never expires
— it describes the past, so it cannot become false.

That expiry has a trap worth naming, because the first version of its test walked
straight into it. Nothing on disk changes when a `waiting` ages out, so an etag
built from file mtimes alone keeps answering `304` and the browser keeps showing
the stale claim — the expiry would be invisible to the only reader it exists for.
The **resolved** state goes into the fingerprint, so the expiry invalidates its own
cache entry. The test that aged the file by rewriting it passed against a build
with no expiry in the etag at all; the one that only moves the clock does not.

**Notifications stay quiet far more than they speak.** `Stop` fires at the end of
every turn, so notifying on each is how a feature gets muted within a day:
`turn_ended` speaks only when the tab has been hidden more than 60s, `waiting`
always speaks, and everything is keyed on `(state, since)` so a re-render is not a
transition. Without that key the 4s poll would fire fifteen notifications a minute
about a single permission prompt. Those rules are executed rather than asserted —
`STATE_JS` runs against a DOM stub under node, which is the only way to drive the
clock and the visibility flag, the two inputs that decide every branch.

Known limits, not defects. Snapshot mode has no poll, so it reports the state it
was written with and updates on reload only. A **closed** tab gets nothing: that
needs a service worker and a push service, which a stdlib server in a pod cannot
be. Browsers throttle hidden-tab timers to ~1/min after ~5 minutes, so expect up to
a minute of latency when away.

## Artifacts come from the filesystem, not the worklog

Three page layouts were mocked. The chosen one keeps § Artifacts as a **filesystem scan**
rather than deriving it from `WORKLOG.md` links.

`worklog-capture` is agent-written prose under an explicit never-block rule, so it will
sometimes be incomplete. A monitoring page whose job is "did the thing actually get
produced" cannot treat the agent's self-report as ground truth — a figure written but never
logged still has to appear. The rejected alternative (one unified chronological spine, with
artifacts inline only) was more elegant and would have been silently blind to it.

## Opening files in Jupyter

JupyterLab renders every artifact type better than this page would, so document links open
files *there*. The routing is **not uniform**, and each branch is a measured property of
this image (jupyter-server 2.17.0, jupyterlab 4.4.10, notebook 7.4.7):

| Type | Route | Lands in |
|---|---|---|
| `.ipynb` | `lab/tree/<path>` | Notebook, with a kernel |
| `.csv` / `.tsv` | `lab/tree/<path>` | DataGrid viewer, read-only |
| `.json` | `lab/tree/<path>` | collapsible JSON tree |
| `.md` | *(no Jupyter link)* | **rendered in-process**, in the figure overlay |
| `.parquet` | *(no Jupyter link)* | relative link → browser downloads it |
| figures | *(no link)* | in-page lightbox |

Markdown and parquet are excluded for measured reasons — a blank pane from a missing
`markdownviewer-extension` and a disabled default file browser in the first case, a
`400 … is not UTF-8 encoded` error dialog in the second. Both are properties of a
*deployment*, not of Jupyter, so no URL fixes them. The full derivation, including the
`edit/<path>?factory=` route that looks correct and isn't, is in the `MARKDOWN_EXT` comment
in `tools/dashboard.py` — kept next to the constant it explains.

## What starts the dashboard

`.claude/statusline.sh`, and nothing else.

It used to be launched from skill prose, and that never fired during exploration —
which is most of a project's early life. The earliest copy sat in `/berdl_start`
Phase C, after the plan is written *and* approved; the other was four hops deep in
`worklog-capture` and `berdl_start` Phase 0 never mentioned a dashboard at all, so
the agent had no reason to think one existed. Observed blank through a real run.

The status line is the only place that reliably can. It already resolves the project
and derives the port, it already probes whether anything is listening, and it runs
every turn — so a dashboard lost to a pod restart comes back on its own, and the URL
appears where it is already being displayed rather than needing a second step to
surface it.

A display component with a side effect is unusual, so it is bounded: it fires only
when a project resolved **and** the port is closed, and the launcher exits 0 on
`EADDRINUSE`. The steady state is one 0.05 s socket check and nothing else. Both
bounds are pinned by tests, and `test_only_the_statusline_launches_the_dashboard`
fails if a skill grows its own launcher again — prose that drifts from the real one
and fires at the wrong moment is exactly what this replaced.

**A third bound was missing, and it was the one that mattered.** The launcher
spawned a *server* whenever the port was closed. Without `jupyter-server-proxy` that
server cannot bind: it wrote a snapshot, exited 0, and left the port closed — so the
next turn spawned it again. One process per turn, indefinitely, with the install
instructions accumulating in `.dash.log`, which is gitignored and which nobody has a
reason to open. The reported symptom was a dashboard that silently never appeared.

`can_serve_live()` now selects the launcher, and it sits **inside** the
not-listening branch rather than above the socket check, so the steady state is
unchanged — it only runs on turns that were about to spawn anyway (0.08 ms with the
extension enabled, 1.01 ms in the worst case, where no config directory has an
opinion and all of them are read). When it is false the status line spawns
`--static` instead: bounded work, no port, and a snapshot that is genuinely
refreshed each turn. Its stdout goes to `/dev/null` — it would otherwise repeat,
every turn, what the status line is already displaying — while stderr still reaches
the log.

## How the status line finds the project

`.claude/statusline.sh` renders a second line naming the project, its stage and this
dashboard's URL. It resolves the project from four signals, and for a project created
*during* a session only the last one can fire: Claude Code was launched before the
directory existed, `/berdl_start` only *offers* to create the `projects/<id>` branch, and
`/add-dir` is manual. The fourth is `projects/<id>/runtime.json` keyed by session id.

That file's only writer is `.claude/hooks/beril-runtime.sh`, which is registered on
**`SessionStart` and `PostToolUse`**. SessionStart alone was not enough — it fires before
Phase 0 scaffolds anything, so the intended path was the dead one and the line stayed blank
for a whole run. PostToolUse binds on the first write into any project;
`project_resolution._path_projects` finds it in `tool_input.file_path` with no explicit
binding.

Two things about that hook are easy to break and are pinned by tests:

- It **captures stdin into a variable first**. The cost guard reads the payload, and a
  pipeline that greps stdin would consume it, leaving the snapshot nothing to read.
- The guard applies to **tool events only**. A `SessionStart` payload for a session on
  branch `projects/<id>` at the repo root contains no `projects/` string — the branch is
  read by shelling out to git — so a blanket "skip unless the payload mentions `projects/`"
  would silently break the path that already worked.

Unguarded the hook costs ~103 ms on every `Write`/`Edit`; guarded, a write outside any
project costs ~16 ms (measured).

Everything stays keyed to `session_id` on purpose. Several sessions can run in one clone on
different projects, so any repo-wide signal — an env var, "whichever `beril.yaml` was
touched last" — hands all of them the same answer and flips under them as each one writes.

## Setup, and why it is not in `beril`

`jupyter-server-proxy` is **not on the BERDL image** — verified: none of the 22
drop-ins under `/opt/conda/etc/jupyter/jupyter_server_config.d/` is it. The copy
that made this work during development came from an unrelated `pip install --user`
months earlier, which is why it worked for its author and for nobody else.

`beril setup` installs and enables it at its "Live dashboard" step, verifies through the
same `proxy_enabled()` probe the dashboard gates on, and then states the two steps
it cannot do itself. It never runs implicitly: it mutates the user's environment and
ends in a server restart, so it only ever happens because someone typed it.

**`--user`, not `--sys-prefix`.** `/opt/conda` is an *overlay* mount — writable, and
reverted on every pod restart — while `$HOME` is a persistent volume. So `--user` is
both the only target that survives and the only one a non-admin should write to. It
also makes this a once-per-*user* cost rather than once per pod.

**Not a `beril` subcommand**, for the same reason. `/opt/conda/bin/beril` is a pinned
copy on that overlay: it carries only `{doctor, setup, start}` against the eleven
modules this checkout has, a user cannot update it, and which `beril_cli` wins
depends on the working directory. `tools/dashboard.py` is the checkout's own code and
always matches the branch. `.claude/hooks/dash_stop.py` solves the same problem the
same way, by putting the repo root on `sys.path` first.

The restart in step 2 is unavoidable: `jupyter_server` builds its handler table at
startup, so a newly enabled extension is invisible until the server restarts. Step 3
— `claude --resume` — is there because that restart kills the terminal Claude Code
runs in, and people reasonably assume it kills the session too. It does not.

## Failure modes

| Failure | Symptom | Fallback |
|---|---|---|
| `jupyter-server-proxy` absent | no live URL — the common case on a fresh pod | probe; `--static` launcher; snapshot + `beril setup` named in the status line *and* on the page |
| snapshot double-clicked | opens in JupyterLab's HTMLViewer; JS off until "Trust HTML" | page is fully readable as pure HTML+CSS; launcher says "right-click → Open in New Browser Tab" |
| snapshot left open for hours | it does not update, and looks like it might | banner says so; `relTimes` measures age against the reader's clock, so it visibly ages green → amber → grey rather than freezing |
| pod culled | page stops updating; `fetch` throws, loop keeps retrying | the agent died too, so there is nothing to serve; next session's launcher restores it from disk |
| file read mid-write | one card shows `—` | routine, not exceptional; self-heals next poll |
| no `WORKLOG.md` | timeline empty state | header, rail and all artifact sections still render |
| no `beril.yaml` | `stage inferred from files` | filesystem inference |
| port collision | ~1% per project pair | `EADDRINUSE` → prints the URL and exits 0, treating the squatter as an already-running dashboard |
| `main.css` missing | unstyled but readable | not handled |

## Deliberately cut

| Cut | Re-add when |
|---|---|
| SSE, WebSockets, heartbeats, reconnect logic | a human demonstrably notices 4s on events that land minutes apart |
| a service worker, so a *closed* tab can be notified | never — it also needs a push service, and a stdlib server in an ephemeral pod cannot be one |
| a modal, or anything that keeps flashing, for "agent needs you" | never — WCAG 2.3.1; one 600ms pulse on the transition is the ceiling |
| fastapi, uvicorn, jinja2, nbconvert, PyYAML | never — see the two-launcher section |
| `c.ServerProxy.servers` supervised registration | someone wants a permanent named URL and doesn't mind restarting Jupyter once |
| pidfile / flock / stop command | two dashboards must be mutually exclusive on one port — not a requirement |
| TOC, tabs, search, sortable tables, light mode | past ~6 sections, or >10 notebooks in a project |
| multi-project index | never — the deployed `ui/` is the index |
| live tail of the agent transcript | debugging needs it; a collapsed `<details>` link to `.dash.log` costs nothing |
| backfilling worklogs for the 78 existing projects | someone wants history; per-project git logs are already good narrative |

## Relationship to the planning workflow

#305 is merged and merged *into* this branch, so the approval and deviation chips
now read real values. `plan_approval` still returns `na`/`missing` and
`count_deviations` still returns `0` when those files are absent, which is most of
the 78 projects on disk — the page degrades rather than accusing them.

`plan_digest` here is a byte-identical twin of `beril_cli.approve_cmd.plan_digest`,
and the test that pins them together is no longer skipped: it now runs against the
real implementation. The rule is subtle enough to be worth restating — it excises
the `## Revision History` *section*, keeping whatever follows it. An earlier version
excised everything to end-of-file, which agreed on all four fixtures (each had
Revision History last) and disagreed on 53 of 73 real plans.

The merge itself needed one thing git could not see. #305 split `/berdl_start` into
`/research-plan` and `/execute-plan`, and taking main's version of that file — the
correct resolution — dropped the worklog hooks for the first three lifecycle
transitions, silently, because the skills they moved to are new files with no common
ancestor. `tests/test_skill_wiring.py` exists for exactly that failure and caught it:
416 passed, 1 failed on the merge commit. It reads worklog-capture's own transitions
table as its source of truth, so a table left naming a phase that no longer exists
fails as loudly as a missing hook.

A rename of the `analysis` status to `synthesized` is planned as its own PR;
`analysis` currently names the activity that happens during `active`. Until then
`STAGE_LABELS` relabels the rail for humans without touching the enum.
