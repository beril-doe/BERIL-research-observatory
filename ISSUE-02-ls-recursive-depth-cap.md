# `beril context ls -r` silently truncates at 3 levels below its root

**Severity:** High — returns an incomplete listing that looks complete; no warning, no flag to raise it
**Area:** context layer / OpenViking integration, CLI
**Labels:** bug, context, silent-truncation

## Environment

| | |
|---|---|
| Repo | `/home/wjriehl/beril-context`, branch `cm-beril-context-cli`, HEAD `2237c9aa` |
| CLI | `.venv/bin/beril`, `beril-cli` `0.1.2.dev221+g9f7c612bb` (editable install) |
| Server | `https://beril.kbase.us` |
| Host | BERDL JupyterHub pod (on-cluster) |
| Observed | 2026-10-28 |

## Summary

`ls -r` enumerates only ~3 levels below the address it is called on. Deeper entries are
dropped with no warning and no way to ask for them. From a high address such as
`beril/docs`, it reports directories and **zero documents**, even though the documents
exist and `grep` finds them.

## Reproduction

```bash
.venv/bin/beril context ls --docs -r
```

Actual: 13 entries, all directories, 0 files.

```
beril/docs/discoveries/
beril/docs/discoveries/discoveries/
beril/docs/discoveries/discoveries/Discoveries_Log/
beril/docs/performance/
...
```

Expected: the documents under those directories, which demonstrably exist:

```bash
.venv/bin/beril context ls beril/docs/pitfalls/pitfalls/Per-Database_Pitfalls
# beril/docs/pitfalls/pitfalls/Per-Database_Pitfalls/kbase_msd_bioche_13more_b77aefd5_1.md
# beril/docs/pitfalls/pitfalls/Per-Database_Pitfalls/kbase_msd_bioche_13more_b77aefd5_2.md
# beril/docs/pitfalls/pitfalls/Per-Database_Pitfalls/kbase_uniref50_kb_2more_f33c66e2.md
# beril/docs/pitfalls/pitfalls/Per-Database_Pitfalls/Per-Database_Pitf_2more_4696a50c.md
```

## It is a depth cap, not a node budget

`--node-limit` has no effect at any value:

```bash
for nl in "" "--node-limit 50" "--node-limit 500" "--node-limit 10000"; do
  .venv/bin/beril context ls --docs -r $nl --json | .venv/bin/python -c \
    "import sys,json;d=json.load(sys.stdin);print(len(d),'entries',
     sum(1 for e in d if not e.get('isDir')),'files')"
done
# 13 entries 0 files   (all four)
```

Walking the same tree from successively deeper roots shows the cap moving with the root:

| `ls -r` root | dirs | files | Deeper files that exist but are omitted |
|---|---:|---:|---|
| `beril/docs` | 13 | **0** | all of them |
| `beril/docs/pitfalls` | 10 | 10 | 30 |
| `beril/docs/pitfalls/pitfalls` | 9 | 30 | — |
| `beril/docs/pitfalls/pitfalls/Per-Database_Pitfalls` | 0 | 4 | — |

Same on a project address. `ls 0000-0001-5810-2497/metal_cross_resistance -r` returns 12
files and includes depth-3 leaves such as
`REPORT.md/Report_Gene-Resolution_Metal_Cross-Resist_da8b7f8a/Data_4more_2c2f945c.md`,
but omits depth-4 leaves such as
`REPORT.md/Report_Gene-Resolution_Metal_Cross-Resist_da8b7f8a/Key_Findings/1._Metal_cross-re_6more_451dbaf9_1.md`,
which `grep` on the same project finds.

## Root cause

This repo passes `recursive` straight through without depth handling:

- `ui/app/routes/context.py:389,419` — route accepts `recursive` and forwards it
- `ui/app/context_manager/openviking.py:773-818` — `list_files()` forwards
  `recursive=recursive` to the SDK at line 809; `_Budget` governs `node_limit` only

So the cap is inside OpenViking (`openviking==0.4.22` / `openviking_sdk==0.1.12`), not in
BERIL's own code. Confirmed behaviourally by `--node-limit` being inert: BERIL's budget is
not what is trimming the result.

## Why this matters

1. `.claude/skills/knowledge-context/SKILL.md:181` documents
   `beril context ls <owner>/<project> -r` as "a project's files, recursively". For any
   project with nested fragments — which is all of them, since documents are indexed in
   fragments — that listing is incomplete while appearing authoritative.
2. `ls` is the skill's designated tool for enumeration ("What exists (list every
   project)… embeddings can't enumerate", SKILL.md:51). An agent that enumerates to decide
   "no such document exists" gets a false negative.
3. `grep` warns when it truncates (`context_cmd.py:228-234`). `ls -r` does not, so the two
   commands have inconsistent honesty about incomplete results.

## Suggested fix

Pick one, in rough order of preference:

1. **Upstream** — determine whether the depth cap is configurable in the OpenViking SDK
   (a `depth`/`max_depth` argument on `list_files`) and plumb it through
   `openviking.py:807-812`, the `/api/context/ls` route, and a CLI `--depth` flag.
2. **Walk it in the manager** — if the SDK cannot go deeper in one call, make
   `list_files(recursive=True)` iterate: list, re-list each returned directory, repeat
   until no new directories, bounded by the existing `node_limit` budget. Pure addition
   inside `openviking.py:773-818`; the route and CLI are unchanged.
3. **At minimum, stop lying** — if a recursive listing hits the cap, warn on stderr in the
   style `grep` already uses, so callers know the listing is partial.

Option 2 plus the warning from 3 is probably the smallest change that makes the
documented workflow correct.

## Acceptance criteria

- [ ] `beril context ls --docs -r` lists the pitfall/discovery/performance documents, not
      just directories.
- [ ] `beril context ls <owner>/<project> -r` includes `Key_Findings/*`-style depth-4
      fragments.
- [ ] If any recursion limit remains, reaching it prints a stderr warning (matching
      `grep`'s behaviour) and there is a flag to raise it.
- [ ] Test covers a tree deeper than 3 levels. Note the existing unit tests
      (`test_cli_context.py::test_ls_*`) mock the backend and cannot catch this.
