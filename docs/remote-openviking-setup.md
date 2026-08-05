# Remote OpenViking — New User Setup

The BERIL knowledge context layer (project reports + central docs, searchable
with `knowledge_query.py`) runs on a shared **remote OpenViking server**. Setup
is a single command: `beril login` validates your BERIL token and, in the same
step, provisions and caches your OpenViking credential — after that you can
query freely without running a local server.

> ⚠️ **The server currently runs on the dev host `https://beril-dev.kbase.us`.**
> This is temporary. When OpenViking moves to production, substitute the new
> base URL (or pass `--base-url <url>` to `beril login`).

## Prerequisites

- The repo cloned, with `uv` installed, and the `beril` CLI available.
- An ORCiD you can log in with, and a BERIL personal access token (create one at
  `https://beril-dev.kbase.us/account/tokens`).

## Step 1 — Log in

```bash
beril login --base-url https://beril-dev.kbase.us
```

Paste your personal access token when prompted (input doesn't echo), or pass it
with `--token`. `beril login` then:

1. validates the token against BERIL, and
2. provisions your OpenViking account (idempotent) and **caches the OpenViking
   URL + key in `~/.beril`** alongside your BERIL login.

That cached credential is what the query CLI reads — no browser cookie, no
manual `.env` editing.

## Step 2 — Verify

```bash
# Reachability + auth check — tells server-down apart from a bad key.
uv run knowledge/scripts/knowledge_query.py doctor

# A real query.
uv run knowledge/scripts/knowledge_query.py find "metal resistance"
```

A healthy `doctor` prints `OpenViking: OK`. No `--env-file` is required — the
query CLI resolves the credential from `~/.beril`.

## If OpenViking wasn't linked at login

`beril login` links OpenViking best-effort: if the server was briefly
unreachable (or you logged in before this was wired up), the login still
succeeds but OpenViking is left unlinked. Link it separately against your stored
token:

```bash
beril ov setup              # link now (idempotent)
beril ov status             # show the cached credential + server health
```

## Recovery & rotation

- **Check what's cached:** `beril ov status`.
- **Rotate / force a fresh key:** `beril ov setup --regenerate` (this
  invalidates the old key everywhere it's in use). This is also the recovery
  path for the 409 case below.
- **Populate `.env` instead** (CI, or a tool that reads env vars):
  `eval "$(beril ov print-env)"`, or paste the `beril ov print-env` output into
  `.env`.

## Configuration precedence

`ContextConfig.from_env` resolves the OpenViking credential in this order:

1. **Explicit env vars** — `OPENVIKING_URL` / `OPENVIKING_API_KEY` (from the
   shell or an `--env-file`). These always win, so CI and "point at a different
   server" keep working.
2. **The `~/.beril` cached credential** from `beril login` / `beril ov setup`.
3. **The local default URL** (`http://127.0.0.1:1933`) with no key.

## Troubleshooting

Run `knowledge_query.py doctor` first — its verdict tells you what's wrong:

| Verdict | Meaning | Fix |
|---|---|---|
| `OK` | Reachable, key valid | — |
| `UNREACHABLE` | Server down or wrong URL | Confirm `$SERVER/ov/health` responds in a browser; check network/VPN |
| `NO API KEY` | Reachable, but no key resolved | Run `beril ov setup` (or `beril login`) |
| `AUTH FAILED` | Reachable, but your key was rejected | Key expired/invalid → `beril ov setup --regenerate` |
| `UNHEALTHY` | Reachable, but the server reports itself unhealthy | Server-side — flag a maintainer / check the OV deployment |
| `ERROR` | Reachable, but an authenticated call failed unexpectedly | Retry; if it persists, check the OV server logs |

Other cases:

- **`Not logged in`** — run `beril login` first.
- **OpenViking not linked after login** — the server was unreachable during
  login; run `beril ov setup`.
- **`HTTP 409` / "key exists but BERIL holds none"** — OpenViking already has a
  user for your ORCiD but BERIL holds no key for it. Run
  `beril ov setup --regenerate` to mint and store a fresh key.
- **Quick server liveness, no auth needed:** `curl "$SERVER/ov/health"` should
  return `{"status":"ok","healthy":true,...}`.

## Security

`OPENVIKING_API_KEY` is a secret. The cached copy in `~/.beril/auth.json` is
written mode `0600`. If you populate `.env`, note that `.env` and `*.env` are
gitignored — never commit the key, and **never paste it into a chat**. If it
leaks, rotate it with `beril ov setup --regenerate`.

## See also

- `docs/openviking.md` — full query/ingest reference and local-server setup.
- The `knowledge-context` skill — how agents use the query toolkit.
