---
description: Show the runtime-provenance session history (runtime.json) for a project — read-only.
argument-hint: "[project_id]"
allowed-tools: Read
---

# Runtime provenance (`/runtime`)

Show the runtime-provenance history for a project — *how observed sessions ran*. **Read-only** — this never writes or modifies anything.

Arguments: `$ARGUMENTS`

## Steps

1. Resolve the project id from the first argument, or from the current working directory if inside `projects/{id}/`.
2. Read `projects/{project_id}/runtime.json`. If it does not exist, tell the user there is no runtime history yet and stop.
3. Present each `sessions[]` record separately: session id/observation time, `agent` (beril version, model, effort), `activity` (source, permission mode), `code` (git sha, dirty), `tenant`, `actor` (user, ORCID), and `documented_datasets_snapshot` (REPORT hash, observation time, and author-documented collections/tables). Any field may be absent.

This is **runtime / execution** provenance (who/what/when was observed) — distinct from *source / lineage* provenance. The documented dataset snapshot does not prove which queries executed. It is non-authoritative and excluded from OpenViking scientific recall. Do not edit `runtime.json` or any other file.
