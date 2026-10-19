# OpenViking Knowledge Context

This branch uses OpenViking as the BERIL knowledge context layer. It ingests
curated project reports, a human-readable claims/evidence projection, numbered
refutations, and central docs, then exposes `find`, `overview`, and `read`
queries for agents and humans. Original project files remain authoritative;
results from the knowledge layer are pointers back to them.

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

BERIL runs a shared remote OpenViking server (currently the dev host
`https://beril-dev.kbase.us`). New users get an API key with a one-time setup —
see **[remote-openviking-setup.md](remote-openviking-setup.md)** for the full
walkthrough (log in, copy the `beril_session` cookie, run
`setup_remote_ov.py`). In short:

```bash
uv run knowledge/scripts/setup_remote_ov.py --cookie '<beril_session>'
# writes OPENVIKING_URL=https://beril-dev.kbase.us/ov + OPENVIKING_API_KEY to .env
```

To point anywhere manually, set both env vars:

```bash
# .env
OPENVIKING_URL=https://beril-dev.kbase.us/ov
OPENVIKING_API_KEY=<token>
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

`/submit` mirrors a completed project into the context service through BERIL
(`ingest_context.py --project <id> --json`, which POSTs a zip and a manifest to
`POST /api/context/ingest_files`). BERIL checks every submission before it
touches the project or the context store, and refuses one that fails any check
with a 4xx response whose `detail` names the problem:

| Check | Refused with |
|---|---|
| `beril.yaml`, `REPORT.md` and `REVIEW.md` are in every submission (removal-only ones too) | 422 |
| `beril.yaml` has `status: complete` and a `project_id` naming the project being ingested | 422 |
| `approval.by` is the submitting user's ORCiD | 403 |
| `approval.report_hash` / `review_hash` match the carried `REPORT.md` / `REVIEW.md` | 422 |
| Only allowed files are added (below); `!remove` lines may name any path | 422 |
| Entries are stored or deflated, not encrypted, not symlinks, and stay inside the archive | 400 |
| Within the size limits (below) | 413 |
| `force` is used only by a BERIL admin | 403 |

**Allowed files** — exactly what the mirror stages: `README.md`,
`RESEARCH_PLAN.md`, `REPORT.md`, `REVIEW.md`, `references.md`, `FINDINGS.md`,
`EXECUTIVE_SUMMARY.md`, `FAILURE_ANALYSIS.md`, `DESIGN_NOTES.md`,
`CORRECTIONS.md`, `beril.yaml`, `memories/<name>.md`, `REFUTATION_<n>.md`, and
the generated `PROJECT_METADATA.md` and `CLAIMS_CONTEXT.md`.

**Archive format** — a zip whose entries are stored or deflated
(`zipfile.ZIP_DEFLATED`, which `ingest_context.py` writes). bzip2, LZMA and
other compression methods are refused, as are encrypted entries. Only the
members the manifest names are extracted. This only matters if you build an
archive yourself.

**Size limits** (server settings, defaults shown):

| Limit | Setting | Default |
|---|---|---|
| Upload size | `BERIL_CONTEXT_MAX_ARCHIVE_BYTES` | 32 MiB |
| Manifest size | `BERIL_CONTEXT_MAX_MANIFEST_BYTES` | 1 MiB |
| Manifest entries | `BERIL_CONTEXT_MAX_INGEST_FILES` | 50 |
| Any one file | `BERIL_CONTEXT_MAX_FILE_BYTES` | 50 MiB |
| Named files, expanded | `BERIL_CONTEXT_MAX_EXPANDED_BYTES` | 128 MiB |
| Entries in the whole archive, listed or not | `BERIL_CONTEXT_MAX_ARCHIVE_ENTRIES` | 1000 |

The proxy in front of BERIL accepts request bodies up to 40 MiB on this path.

Through `/submit`, a refusal is reported as `"failed"` in the upload tool's
`context_submission` JSON, with the server's `detail` in the reason; the
lakehouse archive has still succeeded. The usual cause is a report or review
edited after approval: re-run `/berdl-review` and `/submit`.

The approval check is a consistency check, not proof: it ties every ingest to
its approver and to the approved bytes, but the submitter supplies the
`beril.yaml` it checks.

### Importing the repo's projects (admin)

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
