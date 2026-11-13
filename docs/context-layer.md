# The Context Layer

BERIL keeps an indexed, searchable context layer over every submitted project
and the central docs (`docs/pitfalls.md`, `discoveries.md`, `performance.md`,
`research_ideas.md`). Agents use it to answer "what's known about X", "has this
been done", and "has anyone hit this error before" without reading every
project by hand. Results are pointers: the project files stay authoritative.

You reach it through BERIL with your `beril login`. There is no separate
account or key.

## Getting started

```bash
beril login              # paste a personal access token from <BERIL URL>/account/tokens
beril context doctor     # OK, or what's wrong and how to fix it
```

## Searching

```bash
beril context find "core genome fitness"          # semantic search across all projects and docs
beril context pitfalls "spark OOM"                # has this gotcha been hit before?
beril context discoveries "pangenome"             # findings, stale duplicates suppressed
beril context grep "kbase_ke_pangenome" --docs    # exact text, in the central docs
beril context ls beril/docs                       # browse
```

Every command takes `--json`. `beril context <command> --help` lists the
options. The `knowledge-context` skill is the agents' guide to using these well.

**Addresses.** Results name each resource as `<owner>/<project>/<path>`, with
central docs under `beril/docs/`. Pass one back with `--address` (or as `ls`'s
argument) to look there. Otherwise, scope a search with these flags:

- `--project` — one of *your own* projects. Add `--all-owners` for a project
  whoever owns it.
- `--owner` — one person's projects.
- `--all-owners` — everyone's projects.
- `--path` — a path within the project.
- `--docs` — the central docs.

**Limits worth knowing.**
- `find` returns the best `--limit` results (10 by default, 200 at most). It
  notes on stderr when more ranked results lie past that, so an absence from
  `find` isn't an absence from the context layer; use `grep` to check.
- `grep` returns at most `--node-limit` matches (256 by default). It warns
  when it reaches that cap.
- When BERIL is unreachable, `beril context` fails and says so. There is no
  offline mode.

## Reading a file whole

`find`, `grep` and `ls` return pointers and fragments. To read one project
file exactly as it was submitted:

```
GET /api/context/read?address=<owner>/<project>/<path>
```

`address` is the `<owner>/<project>/<path>` form every other read route
names a resource by. The response is JSON — `content`, `encoding` (`utf-8`,
or `base64` for a figure), `sha256`, `size`, `content_type`, `source`,
`modified_at` — or, with `Accept: application/octet-stream`, the raw bytes
with `X-Content-SHA256`, `X-Content-Source` and (when known)
`X-Content-Modified-At` headers. Reads are global for public projects, like
every other read; a file that does not exist, or a project you may not see,
is a 404.

**Readable files.** Only `REPORT.md`, `README.md`, `beril.yaml`,
`CORRECTIONS.md`, `REFUTATION_<n>.md` and anything under `figures/` can be
read whole; anything else is a 403. This is deliberately narrower than what
is ingested: it is the contract the wiki builds from (the report, its
metadata and errata, and the figures the report embeds). Reviews, plans and
memories stay reachable through `find`, `grep` and `ls`.

**Byte-exactness.** The bytes are the ones the project submitted, always.
The context store decomposes each document into fragments and reassembles
one on read; whether that round-trips byte for byte is not promised, and the
wiki verifies quotes and offsets against source bytes. So BERIL hashes what
the store returns against the `content_sha256` it recorded when the file
completed its ingest, and serves the store's copy (`source: context`) only
when they match. Otherwise — a differing hash, a file the store never
ingested (figures never are), a store that has lost the file — it serves the
lakehouse archive copy `/submit` wrote (`source: archive`,
`s3://cdm-lake/tenant-general-warehouse/microbialdiscoveryforge/projects/<project>/<path>`,
`BERIL_ARCHIVE_*` settings). The route's contract is the same either way; a
client that checks `sha256` can trust the bytes from both. Which source
answered is logged on the server. If the archive is needed and unreachable
(no credentials, endpoint down), the read is a 502.

## The submissions feed

What landed, and when — the "changed since" feed a downstream consumer (the
wiki curator) polls:

```
GET /api/context/submissions?since=<iso8601>&kind=approved,seeded&limit=100
```

```json
{
  "submissions": [
    {
      "project": "alpha",
      "owner_orcid": "0000-0001-2345-6789",
      "address": "0000-0001-2345-6789/alpha",
      "submitted_at": "2026-11-01T12:00:00+00:00",
      "kind": "approved",
      "batch_id": "…",
      "is_public": true,
      "files": [{"path": "REPORT.md", "sha256": "…"}, {"path": "beril.yaml", "sha256": "…"}],
      "removed": []
    }
  ],
  "next_since": "2026-11-01T12:00:00+00:00"
}
```

One entry per **completed** ingest batch (every file completed or was
withdrawn), oldest first, so an entry can be `read` at once; each file's
`sha256` is the hash `read` serves byte-exact. `since` is exclusive — pass
back the `next_since` you were given to see only what came after (on an
empty page it echoes your own cursor). `limit` is 100 by default, 1000 at
most. Entries are global for public projects; a private project's batches
are seen only by its owner and admins.

**`kind`.** `approved` is a `/submit` ingest: it passed the approval gate
(`beril.yaml` `status: complete`, an approval block naming the submitter,
report and review hashes matching). `seeded` is an admin import
(`POST /api/admin/context/import_files`) of a repo project that predates
`/submit` — it was never gated, so a consumer that wants only reviewed work
asks for `kind=approved`. A seeded project's address is under its **repo
owner**: the import lands in the namespace of the ORCiD the repo importer
assigned the project (`beril.yaml` or the README's authors), exactly where
that owner's own later `/submit` writes, so one project never has two
addresses. Projects the importer found no author for are refused by the
import and never appear.

## How projects get in

A project enters the context layer when `/submit` approves it and archives it
to the lakehouse. After the archive succeeds, `/submit` mirrors the approved
files into the context layer. That mirror is **best-effort**: it is skipped
when BERIL is unreachable or you aren't logged in, and it can fail, without
affecting the archive. `/submit` reports the outcome as `context_submission`
(`ok`, `skipped` or `failed`). To retry a skipped or failed mirror (as the
project's approver):

```bash
uv run knowledge/scripts/ingest_context.py --project <project_id> --json
```

This sends files that already landed nothing new, so it is safe to re-run.
Editing files in your checkout changes nothing in the context layer until the
project is submitted again.

## What BERIL accepts

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
