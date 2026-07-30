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
failure the dot exists to catch.

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

## Failure modes

| Failure | Symptom | Fallback |
|---|---|---|
| `jupyter-server-proxy` absent | server runs, URL 404s — silent from the app's side | startup probe; no server started; static snapshot + install steps printed |
| snapshot double-clicked | opens in JupyterLab's HTMLViewer; JS off until "Trust HTML" | page is fully readable as pure HTML+CSS; launcher says "right-click → Open in New Browser Tab" |
| pod culled | page stops updating; `fetch` throws, loop keeps retrying | the agent died too, so there is nothing to serve; next session's launcher restores it from disk |
| file read mid-write | one card shows `—` | routine, not exceptional; self-heals next poll |
| no `WORKLOG.md` | timeline empty state | header, rail and all artifact sections still render |
| no `beril.yaml` | `stage inferred from files` | filesystem inference |
| port collision | ~1% per project pair | `bind()` fails, logs the busy port, exits 1 |
| `main.css` missing | unstyled but readable | not handled |

## Deliberately cut

| Cut | Re-add when |
|---|---|
| SSE, WebSockets, heartbeats, reconnect logic | a human demonstrably notices 4s on events that land minutes apart |
| fastapi, uvicorn, jinja2, nbconvert, PyYAML | never — see the two-launcher section |
| `c.ServerProxy.servers` supervised registration | someone wants a permanent named URL and doesn't mind restarting Jupyter once |
| pidfile / flock / stop command | two dashboards must be mutually exclusive on one port — not a requirement |
| TOC, tabs, search, sortable tables, light mode | past ~6 sections, or >10 notebooks in a project |
| multi-project index | never — the deployed `ui/` is the index |
| live tail of the agent transcript | debugging needs it; a collapsed `<details>` link to `.dash.log` costs nothing |
| backfilling worklogs for the 78 existing projects | someone wants history; per-project git logs are already good narrative |

## Relationship to the planning workflow

This targets `main` and **does not depend on** `feat/planning-workflow` (#305).
`plan_approval` returns `na`/`missing` and `count_deviations` returns `0` when those files
are absent, so the page degrades correctly on every project on disk today — none of which
has a `plan_approval` block. The chips start showing real values once that branch lands,
with no code change here.

Verified both directions: the suite passes on `main`, and passes rebased onto
`feat/planning-workflow` with the twin test active against the real
`beril_cli.approve_cmd`.

**Merge order is free**, with one follow-up either way: two mechanical conflicts
(`.claude/skills/berdl_start/SKILL.md`, `PROJECT.md`) and the Phase B/C hooks move to
`research-plan` / `execute-plan`. `tests/test_skill_wiring.py` fails loudly if that move is
missed — verified red on a simulated bad merge, green on the correct one. The rehearsed
resolution is preserved at `backup/worklog-capture-stacked`.

A rename of the `analysis` status to `synthesized` is planned as its own PR after #305
merges; `analysis` currently names the activity that happens during `active`. Until then
`STAGE_LABELS` relabels the rail for humans without touching the enum.
