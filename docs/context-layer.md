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
beril context read <owner>/<project>/REPORT.md    # one project file, byte-exact
beril context submissions --since 2026-11-01T00:00:00Z   # which projects came in, and when
beril context find "carbon yield" --source wiki   # the wiki, through the same API
```

Every command takes `--json`. `beril context <command> --help` lists the
options. The `knowledge-context` skill is the agents' guide to using these well.

**Reading a file.** `read` returns one project file as the server holds it, and
verifies its sha256 against the digest BERIL reports before printing or
writing anything; a mismatch is an error, not a warning. Text prints to
stdout exactly as stored (no added newline); `--out PATH` writes the raw bytes
(the only way to read a figure); `--json` prints the envelope (`address`,
`path`, `size`, `sha256`, `content_type`, `encoding` of `utf-8` or `base64`,
`content`, `source` of `context` or `archive`, `modified_at`). Only these
project files are readable, and any other path is refused with 403:
`REPORT.md`, `README.md`, `beril.yaml`, `CORRECTIONS.md`, `REFUTATION_<n>.md`
and `figures/**`. Any logged-in user may read any public project.

**The submissions feed.** `submissions` lists complete submission records,
oldest first: `approved` rows from `/submit`, `seeded` rows from an admin
import of existing projects, `docs` rows for the central digests. Each row
names the submission `id`, project, owner, `revision` (the sha256 of the
submitted `REPORT.md`), `submitted_at`, `archive_path` and every archived
file with its sha256 and size; the table shows the first 12 hex digits of the
revision. Filter with `--since ISO`, `--kind approved,seeded,docs` and
`--limit N`. A page ends with `next_since` (stderr, or in the `--json`
output); pass it back as `--since` for the next page. This is the "what
changed since" feed the wiki builds from. `read --revision <sha256>` reads a
file as of one of these records.

**The wiki as a source.** `find`, `read` and `ls` take `--source wiki` to look
at the wiki instead of the context layer, through the same API and login.
Wiki addresses are `wiki/<collection>/<slug>[#section]` and print like any
other; `read wiki/<collection>/<slug> --source wiki` returns the page. Without
`--source` nothing changes.

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
- `read` serves only the allowlisted files above; other project files
  (`RESEARCH_PLAN.md`, `memories/*`, ...) are searchable but not readable this
  way, so use `find --address ... --read-content` for them.
- `submissions` is one page per call. Keep passing `next_since` back until a
  page comes without one.
- When BERIL is unreachable, `beril context` fails and says so. There is no
  offline mode.

## How projects get in

A project enters the context layer when `/submit` approves it and archives it
to the lakehouse. After the archive succeeds, `/submit` does two independent
things, in this order, neither of which can fail the archive:

1. **The submission record** (`POST /api/context/submissions`). The upload tool
   posts a manifest of every archived file (path, sha256, size), the approval
   block, and the archive path, with a bundle of the wiki's text files
   (`REPORT.md`, `README.md`, `beril.yaml`, `CORRECTIONS.md`,
   `REFUTATION_*.md`) and `REVIEW.md` (BERIL checks the approval's
   `review_hash` against it and never serves it); then it uploads each figure the report embeds, one
   request each. BERIL verifies every byte against the manifest. The record is
   what `beril context submissions` lists and what `read` serves byte-exact,
   so it is the wiki's feed. It is idempotent on (owner, project, revision),
   where revision is the sha256 of `REPORT.md`. `/submit` reports it as
   `wiki_submission` (`ok`, `skipped` or `failed`, with the record `id`,
   `revision` and any `missing` paths) and copies that into the `beril.yaml`
   `submissions[]` entry.
2. **The context mirror** (`POST /api/context/ingest_files`), which indexes the
   curated files for `find`, `grep`, `pitfalls` and `discoveries`. It is
   skipped when BERIL is unreachable or you aren't logged in, and it can fail,
   without affecting the archive or the record. `/submit` reports it as
   `context_submission` (`ok`, `skipped` or `failed`).

A skipped or failed mirror never skips the record, and vice versa. To retry
either one (as the project's approver):

```bash
uv run knowledge/scripts/ingest_context.py --record --project <project_id>   # the record
uv run knowledge/scripts/ingest_context.py --project <project_id> --json     # the mirror
```

Both are safe to re-run: the record is idempotent, and the mirror sends files
that already landed nothing new. The record describes the archive, not your
checkout: the upload tool archives a staged snapshot of the project and builds
the record from that snapshot, then keeps it under `knowledge/state/` until
BERIL reports it complete. `--record` re-sends what was kept, so edits made
after archiving (including `/submit`'s own updates to `beril.yaml` and
`SUBMITTED.md`) are never sent. With nothing kept on this machine, `--record`
fails and asks you to re-run `/submit`. Editing files in your checkout changes
nothing in the context layer until the project is submitted again.

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
