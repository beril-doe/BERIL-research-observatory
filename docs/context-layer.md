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
GET /api/context/read?address=<owner>/<project>/<path>[&revision=<sha256>]
```

`address` is the `<owner>/<project>/<path>` form every other read route
names a resource by. The response is JSON — `content`, `encoding` (`utf-8`,
or `base64` for a figure), `sha256`, `size`, `content_type`, `source`,
`modified_at`, `revision` — or, with `Accept: application/octet-stream`, the
raw bytes with `X-Content-SHA256`, `X-Content-Source`, `X-Content-Revision`
and (when known) `X-Content-Modified-At` headers. Every submission is of an
approved project, so reads are global; a file that does not exist is a 404.

**Readable files.** Only `REPORT.md`, `README.md`, `beril.yaml`,
`CORRECTIONS.md`, `REFUTATION_<n>.md` and anything under `figures/` can be
read whole (plus the central digests under `beril/docs/`); anything else is
a 403. This is deliberately narrower than what is ingested: it is the
contract the wiki builds from. Reviews, plans and memories stay reachable
through `find`, `grep` and `ls`.

**Byte-exactness.** The bytes are the ones the project submitted, always.
`source` says where they came from:

- `submission` — the submission store: the bytes `/submit` handed BERIL
  (below), byte-exact by construction. The newest complete submission
  answers, or the one `revision` names.
- `context` — the context store's copy, served only for a legacy project
  with no submission record, and only when it hashes to the `content_sha256`
  BERIL recorded at ingest (the store decomposes documents and reassembles
  them on read; that is not promised to round-trip).
- `archive` — the lakehouse copy (`BERIL_ARCHIVE_*`), for a legacy project
  whose store copy differs or was never ingested (figures). 502 if the
  archive is needed and unreachable.

A client that checks `sha256` can trust the bytes from any source.

## Submission records

`/submit` records every submission with BERIL after the lakehouse upload
succeeds — independently of the context-store mirror, which is best-effort
and may never run:

```
POST /api/context/submissions                       manifest.json + bundle.zip (multipart)
PUT  /api/context/submissions/{id}/files/{path}     one figure per request (body = bytes)
GET  /api/context/submissions/{id}                  status, stored flags, what is still missing
```

`manifest.json` is `{project, owner_orcid, revision, submitted_at,
archive_path, approval: {by, at, report_hash}, files: [{path, sha256,
size}]}` and lists **every** archived file, figures and data included.
`bundle.zip` carries the wiki's text files (`REPORT.md`, `README.md`,
`beril.yaml`, `CORRECTIONS.md`, `REFUTATION_<n>.md`). BERIL checks each
bundled file against its manifest sha256, that `revision` and
`approval.report_hash` are the sha256 of `REPORT.md`, and that `approval.by`
and `owner_orcid` are the caller (403 otherwise). The post is idempotent on
`(owner, project, revision)`: re-posting returns the existing record
(`created: false`) and stores whatever it still lacked. Figures the report
embeds (`![](figures/…)`, `<img src="figures/…">`) are PUT one per request,
hash-checked, owner only; the response's `missing` lists what is still
needed. A submission is `pending` until every readable text file and every
embedded figure is stored, then `complete`. Proxy body limits: 40 MiB on the
post, 64 MiB per figure (`nginx.conf`; the SPIN ingress needs the same
annotations). Bytes live in the submission store: a filesystem volume at
`BERIL_SUBMISSIONS_DIR` by default, or S3 when `BERIL_SUBMISSIONS_S3_*` is
set, laid out as `<owner>/<project>/<revision>/<path>`.

## The submissions feed

What was submitted, and when — the "changed since" feed the wiki curator
polls:

```
GET /api/context/submissions?since=<iso8601>&kind=approved,seeded&limit=100
```

```json
{
  "submissions": [
    {
      "id": "…",
      "project": "alpha",
      "owner_orcid": "0000-0001-2345-6789",
      "address": "0000-0001-2345-6789/alpha",
      "revision": "<sha256 of REPORT.md>",
      "submitted_at": "2026-11-10T12:00:00+00:00",
      "kind": "approved",
      "archive_path": "s3a://cdm-lake/…/projects/alpha",
      "approval_by": "0000-0001-2345-6789",
      "approval_at": "2026-11-10T11:00:00+00:00",
      "files": [{"path": "REPORT.md", "sha256": "…", "size": 1234}]
    }
  ],
  "next_since": "2026-11-10T12:00:00+00:00"
}
```

One entry per **complete** submission, oldest by `submitted_at` first; each
stored file's `sha256` and `size` are what `read` serves byte-exact. `since`
is exclusive — pass back the `next_since` you were given (an empty page
echoes your own cursor). `limit` is 100 by default, 1000 at most.

**`kind`.** `approved` is a `/submit`: it passed the approval gate and the
record's own checks. `seeded` is an admin import
(`POST /api/admin/context/import_files`) of a repo project that predates
`/submit` — never gated, so a consumer that wants only reviewed work asks
for `kind=approved`. A seeded project's address is under its **repo
owner** (the ORCiD the repo importer assigned from `beril.yaml` or the
README's authors), where that owner's own later `/submit` also writes, so a
project never has two addresses; imports carry no figures, so a seeded
submission is complete at once and its figures come from the archive.
`docs` is the central digests (`discoveries.md`, `pitfalls.md`, …) recorded
by `POST /api/admin/context/import_docs` under owner `beril`, project `docs`;
it is off the default `kind` and must be asked for.

## The wiki as a second backend

`find`, `read` and `ls` take `source=context` (default) or `source=wiki`.
With `wiki`, BERIL answers from the wiki container's internal API (in-cluster
only, `BERIL_WIKI_INTERNAL_URL` / `_TOKEN`), never from OpenViking:

- `POST /api/context/find` `{"query": …, "source": "wiki", "path": "<collection>"}`
  → hits with `address` (`wiki/<collection>/<slug>`), `title`, `text`,
  `match_reason` (the heading) and `link` (the public page URL with the
  heading's anchor: `BERIL_WIKI_PUBLIC_URL` + `/<collection>/<slug>#<anchor>`),
  plus the site `artifact` the answer came from.
- `GET /api/context/read?address=wiki/<collection>/<slug>[#section]&source=wiki`
  → the page as a `ContextFile` (`source: wiki`) plus `artifact`, `title`,
  `link`, `sources`.
- `GET /api/context/ls?source=wiki&path=wiki/<collection>` → the entries.

Collections are `concepts`, `topics`, `conflicts`, `entities`, `summaries`,
`sources`, `findings`, `directions`, `data`; `authors` is never served. When
the wiki is unreachable the answer is a 503 with `detail: "wiki unavailable"`.

**Ask (chat wiki mode).** `POST /api/chat {"mode": "wiki"}` opens a session
on the admin-held `BERIL_WIKI_ASK_*` provider, model and key; turns need no
credentials. The agent has exactly two tools, `find` and `read` with
`source=wiki`, and the Ask rules as its system prompt (cite `[n]`, numbers
verbatim, `NO_ANSWER`, no confidence labels, open questions are untested,
under 220 words). Any `[n]` the reply cites that the turn never retrieved is
dropped on the server before the reply is stored or streamed; the retrieved
`sources` come back with the answer. Before each turn BERIL reserves
`BERIL_WIKI_ASK_RESERVE_TOKENS_PER_TURN` (and its USD at the model's rates
in `chat_providers.yaml`) against the per-user daily token and USD caps, the
global monthly ones, and the per-conversation turn limit; the reservation is
settled to actual usage afterwards (`ask_spend`). A refused turn is a 429
whose `error` names the cap and when it resets.

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
