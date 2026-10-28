# `grep` reports matched files as "file(s) scanned", inverting the meaning of a zero result

**Severity:** Medium — causes a confident wrong diagnosis on no-match searches
**Area:** CLI output, context manager field naming
**Labels:** bug, context, ux, good-first-issue

## Environment

| | |
|---|---|
| Repo | `/home/wjriehl/beril-context`, branch `cm-beril-context-cli`, HEAD `2237c9aa` |
| CLI | `.venv/bin/beril`, `beril-cli` `0.1.2.dev221+g9f7c612bb` (editable install) |
| Server | `https://beril.kbase.us` |
| Observed | 2026-10-28 |

## Summary

`beril context grep` ends its output with `N match(es) in M file(s) scanned`. `M` is not
the number of files scanned — it is the number of files that **contained a match**. On a
search with no hits it prints `0 match(es) in 0 file(s) scanned`, which reads as "your
scope is empty / nothing is indexed" when the truth is "files were searched and none
matched". That is the opposite diagnosis.

## Reproduction

Hold the scope fixed and vary only the pattern. A real scan count would be constant:

```bash
for p in pangenome ModelSEED zzzznosuchtoken; do
  printf '%-18s ' "$p"
  .venv/bin/beril context grep "$p" --docs --json \
    | .venv/bin/python -c "import sys,json;d=json.load(sys.stdin);print(f\"count={d['count']:<5} files_scanned={d['files_scanned']}\")"
done
```

Actual:

```
pangenome          count=183   files_scanned=50
ModelSEED          count=6     files_scanned=3
zzzznosuchtoken    count=0     files_scanned=0
```

The value tracks the pattern, so it is a matched-file count.

## The misleading case

```bash
.venv/bin/beril context grep "ModelSEED"
# 0 match(es) in 0 file(s) scanned
```

This was my own first read of it during testing, and it was wrong: the default scope is
the caller's own projects, which are indexed and non-empty —
`grep "pangenome"` in that same default scope returns `52 match(es) in 11 file(s)`. So
nothing was wrong with the scope; "ModelSEED" simply does not occur there. The output
invited the opposite conclusion.

## Root cause

The field is named `files_scanned` end to end and is summed, not computed, by BERIL:

- `ui/app/context_manager/openviking.py:1050` —
  `"files_scanned": sum(int(p.get("files_scanned") or 0) for p in payloads)`
- `ui/app/context_manager/openviking.py:105` — `_EMPTY_GREP` uses the same key

So the semantics originate in the OpenViking payload; BERIL faithfully passes along a
badly named field. The user-visible wording is added here:

`beril_cli/context_cmd.py:352-364`, specifically line 362:

```python
f"{count} match(es)" + (f" in {scanned} file(s) scanned" if scanned is not None else "")
```

## Suggested fix

Smallest honest change, in the CLI — drop the unsupportable word and suppress the clause
when there is nothing to qualify:

```python
def format_grep(result: dict) -> str:
    matches = result.get("matches") or []
    lines = [
        f"{m.get('address') or ''}:{m.get('line')}: {(m.get('content') or '').strip()}"
        for m in matches
    ]
    count = result.get("count", len(matches))
    files = result.get("files_scanned")
    # ``files_scanned`` is the backend's name for the number of files that
    # matched, not the number searched; say neither rather than say it wrong.
    lines.append(
        f"{count} match(es)" + (f" in {files} file(s)" if count and files is not None else "")
    )
    return "\n".join(lines)
```

This yields `183 match(es) in 50 file(s)` and a bare `0 match(es)` — no implied claim
about coverage either way.

Optionally, also rename the field to `files_matched` in
`ui/app/context_manager/openviking.py` (mapping from the backend's key) so the `--json`
payload is self-describing. That is a breaking change for any consumer reading
`files_scanned`, so it may be worth doing only alongside an OpenViking-side rename.

If a genuine scanned-file count is wanted, it has to come from the backend; it is not
derivable from what is returned today.

## Acceptance criteria

- [ ] A zero-match `grep` no longer implies that nothing was searched.
- [ ] A non-zero `grep` no longer claims a scan count it does not have.
- [ ] `tests/beril_cli/test_cli_context.py::test_grep_prints_address_line_text_and_a_count`
      updated to the new wording, plus a case asserting the zero-match output.
