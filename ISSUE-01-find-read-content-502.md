# `beril context find --read-content` fails with HTTP 502 for every query

**Severity:** High — breaks the only documented path for reading a file that is not in the local checkout
**Area:** context layer / OpenViking integration
**Labels:** bug, context, backend

## Environment

| | |
|---|---|
| Repo | `/home/wjriehl/beril-context`, branch `cm-beril-context-cli`, HEAD `2237c9aa` |
| CLI | `.venv/bin/beril`, `beril-cli` `0.1.2.dev221+g9f7c612bb` (editable install) |
| Server | `https://beril.kbase.us` |
| Account | ORCID `0000-0002-3405-2744` |
| Host | BERDL JupyterHub pod (on-cluster) |
| Observed | 2026-10-28 |

## Summary

Passing `--read-content` to `beril context find` always returns HTTP 502. The flag is
non-functional against the live server. Every other `find` flag works.

## Reproduction

```bash
.venv/bin/beril context find "cross-resistance" --read-content --limit 1
```

Actual:

```
error: failed to search (HTTP 502): <!DOCTYPE html>
<!--[if lt IE 7]> <html class="no-js ie6 oldie" lang="en-US"> <![endif]-->
...
```

Expected: the hits, each followed by `--- content ---`, its full text, and `--- end ---`
(the shape `format_find` in `beril_cli/context_cmd.py:320` already produces).

## Scope of the failure

Deterministic. Not a payload-size or scope problem — isolated by varying one flag at a time:

| Command | Result |
|---|---|
| `find "cross-resistance" --limit 1` | OK — 1 result |
| `find "cross-resistance" --address <owner>/<project>/README.md` | OK — 2 results |
| `find "cross-resistance" --read-content --limit 1` | **502** |
| `find "cross-resistance" --docs --read-content --limit 1` | **502** |
| `find "cross-resistance" --address <...>/README.md --read-content` | **502** (3/3 tries) |

`--read-content` is the single differentiating variable. `--limit 1` still fails, so this is
not the "a broad query would return every matching document in full" case the field's
docstring anticipates.

## Root cause (probable)

`read_content` **is** a declared field on the request model, so this is not a
client/server schema mismatch:

- `ui/app/context_manager/base.py:199` — `read_content: bool = False` on `ContextQuery`
- `beril_cli/context_client.py:95` — the CLI sends it only when true (`_present()` drops
  `False`), so an omitted flag never reaches the wire

That points at the OpenViking backend rejecting or failing the request once
`read_content` is set. Per `ui/app/routes/context.py:192-195`, a backend that "rejects or
cannot answer the query surfaces as 502 — the store is an implementation detail, so its
error text is logged rather than returned." So **the actual cause is in the BERIL server
logs, not in the HTTP response.** First debugging step is to read the logged backend
error for one of these requests.

Pinned backend versions, in case this is a known OpenViking regression
(`pyproject.toml`): `openviking==0.4.22`, `openviking_sdk==0.1.12`.

## Why this matters beyond one flag

`.claude/skills/knowledge-context/SKILL.md:32-38` makes `--read-content` the **only**
documented way to read a file through the context layer:

> If the project isn't in the checkout (someone else's, or not yet merged), read the file
> through the context layer.
> `beril context find "<query>" --address <owner>/<project>/<source file> --read-content`

With 72 indexed projects across 13 owners and only 78 project directories in this
checkout, any agent asked to read another owner's unmerged work currently has no working
route to the text — it can see abstracts and grep lines, but cannot read a document.

## Note on test coverage

`tests/beril_cli/test_cli_context.py::test_find_read_content_prints_the_full_text`
passes. It mocks the HTTP layer, so it verifies the *formatting* of a `content` field and
cannot catch a backend that never returns one. The gap is integration coverage, not unit
coverage.

## Suggested fix

1. Read the server-side log for a `--read-content` request to get the suppressed backend
   error; fix or work around it (likely an OpenViking SDK call signature or version issue).
2. If the backend genuinely cannot serve full text right now, fail with a 422 and a
   message naming `read_content` rather than an opaque 502, so callers can tell input from
   outage.
3. Add an integration/smoke test that exercises `--read-content` against a real (or
   contract-faked) backend response containing `content`.

## Acceptance criteria

- [ ] `beril context find "<q>" --address <owner>/<project>/README.md --read-content`
      returns the file's text.
- [ ] A regression test covers the request actually reaching and being answered by the
      backend with `read_content=true`, not just the formatting of the reply.
