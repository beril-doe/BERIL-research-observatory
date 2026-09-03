# Langfuse tracing

Every BERIL session in Claude Code is traced to a shared
[Langfuse Cloud](https://us.cloud.langfuse.com) project: one trace per
conversation turn (prompts, generations, tool calls, token usage), grouped by
session, tagged with your identity. On session end, the bound project's
`REPORT.md`, `RESEARCH_PLAN.md`, and `WORKLOG.md` are uploaded as media
attachments on the same session.

Tracing turns on when `.env` carries the flag and keys; without them the
hooks are skipped before any interpreter starts. Everything fails open: a
missing SDK, bad keys, or an unreachable Langfuse never blocks a session.

## Setup (per user, once)

1. Get the shared BERIL project keypair from a maintainer.
2. Add to `.env` in the repo root (gitignored; loaded by direnv for both
   `claude` and `codex`):

   ```bash
   TRACE_TO_LANGFUSE=true       # the single on/off switch for both harnesses
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
   ```

3. `uv sync` (installs the `langfuse` SDK the hooks use).

That's it for Claude Code. BERIL ships no Codex-specific wiring; Codex users
who want turn traces in the same project should use Langfuse's official
plugin (Node 22+, Codex 0.128+ — it reads the same `LANGFUSE_*` env vars):

```bash
codex plugin marketplace add langfuse/codex-observability-plugin
codex plugin add tracing@codex-observability-plugin
```

and enable it in `~/.codex/config.toml`:

```toml
[features]
plugin_hooks = true

[plugins."tracing@codex-observability-plugin"]
enabled = true
```

The artifact upload is Claude Code-only for now. (A Codex variant that fires
Claude-style hooks can wire `langfuse-run.sh` into a local, untracked
`.codex/hooks.json` the same way `.claude/settings.json` does.)

## How it's wired

| Piece | Where | When |
| --- | --- | --- |
| Turn traces | `.claude/hooks/langfuse_hook.py` (vendored from [Langfuse's Claude Code integration](https://langfuse.com/integrations/developer-tools/claude-code), plus user attribution) | `Stop` hook |
| Artifact upload | `.claude/hooks/langfuse_artifacts.py` | `SessionEnd` hook |

Both are launched through `.claude/hooks/langfuse-run.sh`, which skips them
(before any interpreter starts) unless the flag and keys are set, and detaches
the Stop hook so responses never wait on Langfuse.

The artifact hook resolves which project the session worked on via
`projects/<id>/runtime.json` (`beril_cli.project_resolution.project_from_runtime`)
and tags the upload `["beril", "artifacts", <project>]` with the session's
`session_id`, so files appear next to the conversation in the Sessions view.

Debug logs: `~/.claude/state/langfuse_hook.log` and
`~/.claude/state/langfuse_artifacts.log`. Set `CC_LANGFUSE_DEBUG=true` for
verbose turn-trace logging.

To verify a setup, don't trust the logs alone — count traces via Langfuse's
own API (borrowed from
[langfuse-retro-load](https://github.com/beril-doe/langfuse-retro-load)):

```bash
curl -s "$LANGFUSE_BASE_URL/api/public/observations?tag=claude-code&limit=1" \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['meta']['totalItems'])"
```

## What ends up in the cloud

Traces contain everything a session saw: prompts, responses, and tool inputs
*and outputs* — so anything a session `cat`s or an API returns (auth tokens,
unpublished data) lands in Langfuse Cloud. This is not hypothetical: live
credentials have turned up in BERIL transcripts before
(langfuse-retro-load#4). Don't enable tracing for sessions handling data
that must not leave the machine, and treat trace access accordingly.

The real local transcript path is *not* uploaded — trace metadata carries a
synthetic `<session_id>.jsonl` instead, since real paths leak usernames and
machine structure (langfuse-retro-load#3).

## Relation to retro-loaded history

[langfuse-retro-load](https://github.com/beril-doe/langfuse-retro-load)
backfills pre-hook sessions into the same project, tagged `retro-load` and
attributed by **pseudonymous pod account name** (a deliberate consent
decision there). Live traces default to your git email, so per-user analyses
will see two identities per person across the two eras — set
`LANGFUSE_USER_ID` in `.env` to your pod account name if you want them to
line up.

## Trust model of the shared keypair

Langfuse API keys are project-scoped with no write-only variant: **anyone
holding the secret key has full API access to the project** — they can read,
write, and delete anyone's traces. With one shared keypair, misuse cannot be
prevented technically, only deterred and detected:

- **Attribution**: every trace and upload carries a `user_id`
  (`LANGFUSE_USER_ID` > `git config user.email` > `$USER`), so junk or
  deletions are attributable. This is client-set, so it deters honest-ish
  mistakes, not a determined bad actor.
- **Distribution**: keys are handed out person-to-person, never committed.
  If a key leaks, rotate it in Langfuse project settings and redistribute.
- **Read access without keys**: teammates who only need to *view* traces
  should be invited as members of the Langfuse org in the UI — they never need
  the API keypair at all. Keep the keypair to people actively generating
  traces.

<!-- ponytail: shared keypair = trust the team. If enforcement is ever needed,
     the upgrade is a small write-only ingest proxy that holds the real keys
     server-side, or per-user Langfuse projects. -->
