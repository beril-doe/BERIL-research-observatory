# `ls` on a file address returns HTTP 502 — including addresses `ls -r` itself just emitted

**Severity:** Medium — breaks the documented "feed any address back" round-trip
**Area:** context layer / OpenViking integration
**Labels:** bug, context, backend

## Environment

| | |
|---|---|
| Repo | `/home/wjriehl/beril-context`, branch `cm-issues`, HEAD `2ba38cc5` |
| CLI | `.venv/bin/beril`, `beril-cli` `0.1.2.dev221+g9f7c612bb` (editable install) |
| Server | `https://beril.kbase.us` (fronted by Cloudflare) |
| Host | BERDL JupyterHub pod (on-cluster) |
| Observed | 2026-10-29, after the ISSUE-01…05 fixes |

## Summary

`beril context ls <address>` succeeds when the address names a directory and fails with
HTTP 502 when it names a file. The failing addresses are ones `ls -r` produces, so the
round-trip the skill promises — take an address from a result, pass it back to `ls` —
breaks on every leaf.

**Not known to be a regression:** I did not exercise this shape before the ISSUE-02 depth
fix, so I cannot say whether it is new. It is reachable far more often now that `ls -r`
returns file addresses at all.

## Reproduction

```bash
# Take any file address that `ls -r` emits, then list it.
f=$(.venv/bin/beril context ls --docs -r --simple | grep '\.md$' | head -1)
echo "$f"
.venv/bin/beril context ls "$f"            # -> 502
.venv/bin/beril context ls "$(dirname "$f")"   # -> OK, lists the file
```

### Actual

```
beril/docs/discoveries/discoveries/Discoveries_Log/2026-02/ecotype_env_rean_11more_f6839a69_1.md
error: failed to list (HTTP 502): the gateway returned an error page instead of BERIL's
response (HTTP 502); if it persists, run `beril context doctor` or tell a BERIL admin
```

Systematic across both corpora — central docs and project files:

| Address | Result |
|---|---|
| `beril/docs/discoveries/discoveries/Discoveries_Log/2026-02/` | ✅ 200, lists its files |
| `beril/docs/.../2026-02/ecotype_env_rean_11more_f6839a69_1.md` | ❌ 502 |
| `beril/docs/.../2026-02/fitness_effects__15more_….md` | ❌ 502 |
| `0000-0001-5810-2497/metal_cross_resistance/beril.yaml/beril.md` | ❌ 502 |

### Expected

Either the single entry for that file (it already comes back with `name`, `size`,
`mode`, `modTime`, `isDir`, `address` when listed via its parent), or a clean 404 if
listing a file is considered meaningless. Not a gateway error.

## The 502 is Cloudflare's, not BERIL's

Same signature as the pre-fix ISSUE-01/04 failures. Captured by hitting the route
directly, directory versus file, one run:

```
  dir : 200  0.25s  application/json  server=cloudflare
        body: [{'name': 'ecotype_env_rean_11more_f6839a69_1.md', 'size': 7599, ...
  file: 502  0.10s  text/html         server=cloudflare
```

BERIL's own backend-failure path returns JSON (`{"detail": "The context manager is
currently unavailable."}`, `ui/app/routes/context.py`), so this is not that path — the
origin is failing to produce a response at all. At 0.10s it fails *faster* than the
directory succeeds (0.25s), which rules out a timeout and points at an immediate
origin-side error.

The CLI's rendering is correct here — the `_detail()` fix from ISSUE-04 is doing its job,
reporting a gateway error page rather than dumping markup.

## Where to look

- Route: `ui/app/routes/context.py:380-402` (`GET /api/context/ls`) — takes
  `project` / `path` / `owner` / `all_owners` / `recursive` / `simple` / `node_limit` /
  `depth`, with no file-versus-directory branch.
- Manager: `ui/app/context_manager/openviking.py:list_files()` — forwards the resolved
  URI to the SDK and already handles `SdkNotFoundError` by returning an empty list
  ("A listing of a path the backend does not know is an empty list, not an error"). A
  file path is evidently raising something else, which escapes that guard.

Reproducing against the SDK directly with a file URI would confirm whether OpenViking
raises a distinct error type for a non-directory target; if so, catching it next to
`SdkNotFoundError` and returning the single entry (or an empty list) is likely the whole
fix.

## Why it matters

`.claude/skills/knowledge-context/SKILL.md:40` states the contract plainly:

> Any address can be passed back to scope a read: `--address A`, or as `ls`'s argument.

and SKILL.md's `ls` section documents `-r` as the way to enumerate a project's files.
Since the ISSUE-02 fix, `ls -r` emits file addresses as a matter of course — so the
natural next step on any of them now errors. An agent following the skill's own
drill-down loop ("a promising hit → read its source") hits this immediately.

## Acceptance criteria

- [ ] `beril context ls <file address>` returns that file's entry, or a clean 404 with a
      message saying a file cannot be listed — never a 502.
- [ ] Every address emitted by `ls -r` can be passed back to `ls` without error.
- [ ] Test covers `ls` on a file address for both a project file and a central-docs file.
