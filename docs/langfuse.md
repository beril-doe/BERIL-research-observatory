# Langfuse tracing

Every BERIL session in Claude Code is traced to a shared
[Langfuse Cloud](https://us.cloud.langfuse.com) project: one trace per
conversation turn (prompts, generations, tool calls, token usage), grouped by
session, tagged with your identity. On session end, the bound project's
`REPORT.md`, `RESEARCH_PLAN.md`, and `WORKLOG.md` are uploaded as media
attachments on the same session.

Nothing on your machine holds a Langfuse key. The hooks send everything to
the BERIL server's relay (`<beril>/lf`), authenticated with your `beril login`
token; the server holds the project keypair and forwards the writes. Tracing
turns on when `.env` carries the flag *and* you are logged in; without both,
the hooks are skipped before any interpreter starts. Everything fails open: a
missing SDK, an expired login, or an unreachable server never blocks a session.

## Setup (per user, once)

1. `beril login` — the same login that links OpenViking. There is nothing
   else to obtain.
2. Add to `.env` in the repo root (gitignored; loaded by direnv):

   ```bash
   TRACE_TO_LANGFUSE=true       # the on/off switch
   ```

3. `uv sync` (installs the `langfuse` SDK the hooks use).

That's it for Claude Code. BERIL ships no Codex-specific wiring; Codex users
who want turn traces in the same project can use Langfuse's official plugin
(Node 22+, Codex 0.128+), which reads `LANGFUSE_*` env vars — point it at the
relay the same way the hooks do (untested with the JS SDK, which uses the same
OTLP endpoint):

```bash
LANGFUSE_PUBLIC_KEY=beril
LANGFUSE_SECRET_KEY=<the "token" in ~/.beril/auth.json>
LANGFUSE_BASE_URL=<the "base_url" in ~/.beril/auth.json>/lf
```

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

The artifact upload is Claude Code-only for now.

## How it's wired

| Piece | Where | When |
| --- | --- | --- |
| Turn traces | `.claude/hooks/langfuse_hook.py` (vendored from [Langfuse's Claude Code integration](https://langfuse.com/integrations/developer-tools/claude-code), plus user attribution) | `Stop` hook |
| Artifact upload | `.claude/hooks/langfuse_artifacts.py` | `SessionEnd` hook |
| Relay | `ui/app/routes/langfuse.py` (BERIL webapp) | every request the two hooks make |

Both hooks are launched through `.claude/hooks/langfuse-run.sh`, which skips
them (before any interpreter starts) unless the flag is set and
`~/.beril/auth.json` exists, and detaches both so neither a response nor a
session exit waits on the relay (SessionEnd hooks get 1.5 s by default).

The hooks build the SDK client from the login record:
`Langfuse(base_url="<base_url>/lf", public_key="beril", secret_key=<token>)`.
A leftover `LANGFUSE_BASE_URL` in `.env` is ignored — the token never goes
anywhere but the relay.
The SDK only speaks HTTP Basic auth, so the BERIL personal access token
travels as the Basic *password*; the relay validates it against the user
table, replaces it with the server-held keypair, and forwards the request
unchanged. Only the three write paths the SDK uses exist on the relay —
OTLP trace export, media record creation, and media finalisation — so it is
write-only by construction. Media bytes go from your machine to the presigned
storage URL Langfuse returns, never through BERIL.

The artifact hook resolves which project the session worked on via
`projects/<id>/runtime.json` (`beril_cli.project_resolution.project_from_runtime`)
and tags the upload `["beril", "artifacts", <project>]` with the session's
`session_id`, so files appear next to the conversation in the Sessions view.

### Server side

The relay reads the keypair from the webapp's settings (`.env` on the server):

```bash
BERIL_LANGFUSE_PUBLIC_KEY=pk-lf-...
BERIL_LANGFUSE_SECRET_KEY=sk-lf-...
BERIL_LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
```

With the keys unset the relay answers 503 and the hooks log and move on.
Every forwarded write leaves an audit line in the webapp log:
`langfuse relay user=<beril user id> POST otel/v1/traces -> 200 (<bytes>)`.

### Debugging

Client logs: `~/.claude/state/langfuse_hook.log` and
`~/.claude/state/langfuse_artifacts.log`. Set `CC_LANGFUSE_DEBUG=true` for
verbose turn-trace logging.

To verify a setup end to end, don't trust the logs alone — a maintainer
holding the keypair can count traces via Langfuse's own API (borrowed from
[langfuse-retro-load](https://github.com/beril-doe/langfuse-retro-load)):

```bash
curl -s "$BERIL_LANGFUSE_BASE_URL/api/public/observations?tag=claude-code&limit=1" \
  -u "$BERIL_LANGFUSE_PUBLIC_KEY:$BERIL_LANGFUSE_SECRET_KEY" | python3 -c \
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
decision there). Live traces default to your ORCiD (from `beril login`), so
per-user analyses will see two identities per person across the two eras —
set `LANGFUSE_USER_ID` in `.env` to your pod account name if you want them to
line up.

## Trust model

Langfuse API keys are project-scoped with no write-only variant: anyone
holding the secret key has full API access to the project — read, write, and
delete anyone's traces. So the keypair never leaves the server:

- **Users hold only their BERIL token.** It is per-user, revocable from the
  account page, and already what OpenViking access is brokered with. Losing a
  laptop means revoking one token, not rotating the project.
- **The relay is write-only.** It exposes exactly the three paths the SDK
  writes to. Reading or deleting traces through it is impossible; teammates
  who need to *view* traces are invited to the Langfuse org in the UI.
- **Attribution.** `user_id` defaults to the ORCiD the relay just
  authenticated, but it is still set client-side inside the payload
  (`LANGFUSE_USER_ID` overrides it), so a determined user could mislabel
  their own writes. Every write is nonetheless tied to a validated token in
  the server's audit line.
- **Rotation.** Rotate in Langfuse project settings, update the server's
  `BERIL_LANGFUSE_*`, redeploy. Nothing to redistribute.

<!-- ponytail: user_id stays client-set. If attribution ever needs enforcing,
     the upgrade is parsing the OTLP body server-side (opentelemetry-proto)
     and overwriting the user.id attribute before forwarding. -->
