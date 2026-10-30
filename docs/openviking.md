# OpenViking — Admin Reference

OpenViking is the store behind BERIL's knowledge context layer. It ingests
curated project reports, a human-readable claims/evidence projection, numbered
refutations, and central docs. Original project files remain authoritative;
results from the context layer are pointers back to them.

**This is the admin reference.** Users never talk to OpenViking or hold a key
for it: they search with `beril context` and their `beril login`, and projects
reach the store through `/submit`. See **[context-layer.md](context-layer.md)**.
Everything below — running a server, the interactive ingest modes, querying the
store directly — needs an admin key.

## Client Configuration

Copy the env template and edit if you need to point at a non-default server:

```bash
cp .env.example .env
```

The relevant entries:

- `OPENVIKING_URL` — defaults to `http://127.0.0.1:1933`, matching the host and
  port in `knowledge/openviking/ov.conf.example`.
- `OPENVIKING_API_KEY` — leave commented for local dev; set it only when the
  OpenViking server enforces client auth (typical for remote/prod deployments).

The three context scripts (`ingest_context.py`, `knowledge_query.py`,
`smoke_ingest_openviking.py`) are PEP 723 self-bootstrapping. Pass `.env` via
`uv run --env-file .env ...` and the scripts install their own deps in an
isolated venv — no `uv sync` needed.

### Remote OpenViking

BERIL's deployments run their own OpenViking server behind the webapp. The
scripts here reach it with an **admin key** — users have none. Set both env
vars:

```bash
# .env
OPENVIKING_URL=https://beril-dev.kbase.us/ov
OPENVIKING_API_KEY=<admin key>
```

`config.py::ContextConfig.from_env()` reads both via `os.getenv`, so any
process loading `.env` (direnv, `--env-file`, `export`) routes the scripts to
the remote endpoint without code changes. Read-only queries (`find`,
`overview`, `read`) don't touch `knowledge/state/context_manifest.json`, so
multiple clients can share a remote server safely. For ingestion, the manifest
is per-machine; pick one host as the writer or accept that `--changed` may
re-push files the server already has (idempotent, just wasted work).

Check reachability and auth at any time — this separates "server down" from
"bad key":

```bash
uv run --env-file .env knowledge/scripts/knowledge_query.py doctor
```

## Local Server Setup

Create the local config:

```bash
cp knowledge/openviking/ov.conf.example knowledge/openviking/ov.conf
```

Set the OpenRouter key in the ignored local config:

```bash
tmp=$(mktemp)
jq --arg key "$OPENROUTER_API_KEY" \
  '.embedding.dense.api_key=$key | .vlm.api_key=$key' \
  knowledge/openviking/ov.conf > "$tmp" && mv "$tmp" knowledge/openviking/ov.conf
```

Validate and start the server:

```bash
uv run openviking-server doctor --config knowledge/openviking/ov.conf
uv run openviking-server --config knowledge/openviking/ov.conf
```

`knowledge/openviking/ov.conf` and `knowledge/openviking/workspace/` are ignored
by git. The API key belongs only in the ignored local config, not in
`ov.conf.example`.

## Smoke Test

With the server running in another terminal:

```bash
uv run --env-file .env knowledge/scripts/smoke_ingest_openviking.py
```

By default this ingests the five most recently modified projects and prints up
to three query results for each.

## Ingestion

Run from the repo root:

```bash
uv run --env-file .env knowledge/scripts/ingest_context.py --all
uv run --env-file .env knowledge/scripts/ingest_context.py --changed
uv run --env-file .env knowledge/scripts/ingest_context.py --project <project_id>
uv run --env-file .env knowledge/scripts/ingest_context.py --docs
uv run --env-file .env knowledge/scripts/ingest_context.py --all --limit 5
```

Use `--all` for initial setup, `--changed` for routine refreshes, `--project`
after editing one project, and `--docs` after central docs edits. `--limit N`
caps how many projects a single `--all`/`--changed` run ingests and writes a
partial manifest so the rest stay pending — handy for smoke tests and for
resuming after rate-limit backoffs.

Per-project staging renders `claims.json` as `CLAIMS_CONTEXT.md`, with separate
labels for author status/confidence, supporting evidence, contradicting
evidence, resolution state, and computed artifact support. It also includes
`REFUTATION_N.md` so verdicts are searchable. The manifest hashes the original
`claims.json` and refutations, so `--changed` notices updates. `runtime.json` is
excluded from semantic scientific recall; inspect it directly with `/runtime`.

### Submitting through BERIL

What `POST /api/context/ingest_files` accepts (the checks on every `/submit`
mirror) is documented for users in
[context-layer.md § What BERIL accepts](context-layer.md#what-beril-accepts).

### Importing the repo's projects (admin)

> **Scope: a one-time backfill of the projects in this git repo.** This
> tooling exists only to ingest the set of projects currently under
> `projects/`. It is not an ongoing ingest path and not a way to submit new
> work: new and updated projects reach the context layer through `/submit`,
> under their own authors.

Projects that predate `/submit` are indexed by an admin, each **owned by its
author**, as if that author had submitted it. Two steps, on the target server:

1. **The repo import** (`/admin/import`, or the data-repo webhook) creates a
   project row per `projects/<id>/` and picks its owner by one rule
   (`app/importer.py` `owner_orcid`): the first author with an ORCiD in
   `beril.yaml`, else in an `Authors` section of `README.md`, then
   `RESEARCH_PLAN.md`, then any other top-level `.md` file. The BERIL admin
   account (`0009-0007-0287-2979`) never owns a project. An ORCiD with no
   account gets a stub user, which its person adopts at first login. A project
   with no ORCiD is owned by the sentinel user and **flagged**. A project whose
   owner changes under the rule is re-owned on the next import, even if its
   files haven't changed.
2. **The context import** stages each project the way the `/submit` mirror
   does and uploads it to `POST /api/admin/context/import_files`, which writes
   it into the owner's namespace with BERIL's admin key and records it under
   the owner's project and batch rows. A later `/submit` by that owner then
   skips whatever is unchanged.

```bash
# As an admin, logged in to the target server (`beril login --base-url …`):
uv run knowledge/scripts/import_projects.py --all --dry-run   # each project's owner; nothing written
uv run knowledge/scripts/import_projects.py --all             # import everything importable
uv run knowledge/scripts/import_projects.py <id> [<id> …]     # just these
```

Each project reports one of these outcomes:

- `imported`;
- `current` — nothing changed since the last import;
- `flagged` — no author ORCiD: fix the project's authors, re-run the repo
  import, then import again;
- `not_imported` — the repo import hasn't seen it;
- `in_progress` — still indexing when `--wait` ran out; it will land;
- `failed`.

When the repo import **re-owns** a project (the rule's answer changed), the
next context import writes it to the new owner. The old owner's copy is then
removed one file per request (`POST /api/admin/context/retire_file/{id}`).
Each removal is marked pending before anything is deleted, and is refused
until the new owner's copy of that file has landed. Two known limits:

- **A failed re-own can leave things half-moved.** The importer commits the
  owner change before copying files, so a copy failure leaves the project
  showing the new owner with files still stored under the old one. They stay
  readable, the import is marked `failed`, and the retry finishes the move.
- **A removal can race a reversal.** If the repo import re-owns the project
  back to the old owner during a delete (seconds), that file is removed from
  what is now the current namespace. The file is recorded `removed`, which is
  not "landed", so the next import (or the owner's `/submit`) re-sends it.

Re-running is safe. `--force` re-sends unchanged files. The same archive limits
and file allowlist as `/ingest_files` apply. The approval check does not, since
these projects never went through `/submit`. Poll a batch with
`GET /api/admin/context/import_status/{batch_id}`.

### Batching, pacing, and resume safety

The ingest path uses batch-style OpenViking calls: resources are queued with
`wait=False`, then processing is awaited periodically. Two env knobs tune the
pacing, both read at process start:

- `OV_INGEST_DRAIN_EVERY` (default `1`) — projects per drain batch. After this
  many `add_resource` calls the script blocks on `wait_processed` so OV's temp
  tier (`viking://temp/default/...`) can flush before more uploads pile up.
  `1` is the slow-and-steady default; bump it (e.g. `5`, `10`) when CBORG/OV
  are healthy and you want more throughput.
- `OV_INGEST_INTER_BATCH_PAUSE` (default `15` seconds) — sleep after each
  drain so CBORG/OpenAI rate-limit windows can refill. CBORG `gemini-3-flash`
  enforces 20 req/min and a single project can fire 5–10 VLM calls during
  semantic extraction, so the pause needs to be long enough for the sliding
  window to clear. Bump to `30+` if 429s still leak through; set to `0` only
  when the dependent services have headroom (the test suite does this).

The manifest (`knowledge/state/context_manifest.json`) is checkpointed at the
end of every drain batch, *after* `wait_processed` confirms OV has fully
processed the batch (not just synchronously finalized the upload). A manifest
entry therefore means "OV has fully processed this resource". A crash mid-run
loses at most one drain-batch worth of progress; re-running `--changed`
resumes at the failed project rather than restarting from the top.

Transient OV failures (`DeadlineExceeded`, `EmbeddingFailed`, `Internal`,
`Processing`, `ResourceExhausted`, `Unavailable`, `VLMFailed`) are retried up
to 3 times with linear backoff before propagating. Hard errors
(`InvalidArgument`, `NotFound`, `AlreadyExists`, …) still fail fast.

### Cancelling a run

OpenViking has no cancel/abort API, so cancelling means stopping the server
and clearing its on-disk queue:

```bash
uv run --env-file .env knowledge/scripts/cancel_openviking_ingest.py
uv run --env-file .env knowledge/scripts/cancel_openviking_ingest.py --purge-workspace --yes
```

Without `--purge-workspace` the script stops the server, drops `queue.db`,
and removes pending temp uploads — ingested data and the manifest survive, so
the next ingest resumes where the manifest left off. `--purge-workspace` is
destructive: it deletes the entire workspace and the state manifest, forcing
a full re-ingest.

## Querying

`knowledge_query.py` exposes the OpenViking surface needed for both fuzzy and
deterministic lookups:

```bash
# Semantic search
QUERY=knowledge/scripts/knowledge_query.py
uv run --env-file .env $QUERY find "query terms"
uv run --env-file .env $QUERY find "query terms" --project <project_id>
uv run --env-file .env $QUERY find "query terms" --docs

# Filter / time-bounded find (pass an OV filter tree as JSON)
uv run --env-file .env $QUERY find "query terms" --since 7d --time-field updated_at
uv run --env-file .env $QUERY find "query terms" \
  --filter '{"op":"must","field":"uri","conds":["viking://resources/projects/alpha/"]}'

# Exact pattern (e.g. all projects mentioning an author)
uv run --env-file .env $QUERY grep "Ada Lovelace" --uri viking://resources/projects/

# URI enumeration / structural navigation (glob pattern is relative to --uri)
uv run --env-file .env $QUERY glob '*' --uri viking://resources/projects/
uv run --env-file .env $QUERY ls viking://resources/projects/ --simple
uv run --env-file .env $QUERY tree viking://resources/projects/alpha/
uv run --env-file .env $QUERY stat viking://resources/projects/alpha/

# Resource access
uv run --env-file .env $QUERY overview viking://resources/projects/<project_id>/
uv run --env-file .env $QUERY read viking://resources/projects/<project_id>/REPORT.md
```

Target layout:

- Projects: `viking://resources/projects/<project_id>/`
- Central docs: `viking://resources/users/beril/docs/<doc_slug>/` (under the
  reserved `beril` house account; the old `viking://resources/docs/` root is
  retired and removed by `--docs`)

Per-project metadata (id, title, status, authors, branch, engine, dates) is
ingested as `PROJECT_METADATA.md` inside each project URI — search it with
`find` or `grep` rather than a global index.

## Project relations

Not supported. The pinned OpenViking client (0.4.22) has no relations API —
`link`, `unlink` and `relations` were removed from both its Python clients — so
`knowledge_query.py` no longer offers those commands, and ingest no longer turns
a `beril.yaml` `related_projects:` list into links. The field is left in place
but nothing reads it. To find related work, `find` on a project's theme.
