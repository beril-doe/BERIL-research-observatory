# `find` silently truncates at a 200-node budget, with no flag to raise it and no warning

**Severity:** Medium-High — the one remaining command that can quietly under-report, and the one agents reach for first
**Area:** CLI, context layer
**Labels:** bug, context, silent-truncation

## Environment

| | |
|---|---|
| Repo | `/home/wjriehl/beril-context`, branch `cm-issues`, HEAD `2ba38cc5` |
| CLI | `.venv/bin/beril`, `beril-cli` `0.1.2.dev221+g9f7c612bb` (editable install) |
| Server | `https://beril.kbase.us` |
| Host | BERDL JupyterHub pod (on-cluster) |
| Observed | 2026-10-29, after the ISSUE-01…05 fixes |

## Summary

`beril context find` is bounded by a backend node budget that defaults to **200**. With
that default it returns ~6.6% of the matching corpus. Unlike `grep` and `ls` — both of
which now expose `--node-limit` *and* warn on truncation — `find` exposes no such flag and
emits no warning, so a caller cannot tell the result set is partial, nor widen it.

## Reproduction

```bash
.venv/bin/python -c "
from beril_cli import auth_store
from beril_cli.context_client import ContextClient, Scope
r=auth_store.load()
with ContextClient(r.base_url,r.token,timeout=120) as c:
    base=len(c.find('metal resistance',Scope(all_owners=True),limit=200).get('results') or [])
    print(f'  default            -> {base} results')
    for nl in [100,200,256,300,500,1000,10000]:
        n=len(c.find('metal resistance',Scope(all_owners=True),limit=200,node_limit=nl).get('results') or [])
        print(f'  node_limit={nl:<5}   -> {n} results')
"
```

### Actual

```
  default            -> 156 results
  node_limit=100     -> 84 results
  node_limit=200     -> 156 results     <== identical to the default
  node_limit=256     -> 202 results
  node_limit=300     -> 240 results
  node_limit=500     -> 411 results
  node_limit=1000    -> 856 results
  node_limit=10000   -> 2351 results
```

`node_limit=200` reproduces the default exactly, pinning the implicit budget at 200.
The full matching set is **2351**; the default surfaces **156** of them.

Note `--limit 200` was in force throughout and is *not* the limiter — 156 < 200. The two
bounds are independent, and the one that actually binds is the one the CLI does not
expose.

## Why this is the inconsistent case

All three search commands are bounded, but they treat the caller differently:

| Command | Default budget | `--node-limit` flag? | Warns on truncation? |
|---|---:|---|---|
| `grep` | 256 (`_DEFAULT_GREP_LIMIT`, `context_cmd.py:34`) | yes (`context_cmd.py:93`) | yes (`context_cmd.py:264-270`) |
| `ls` | 1000 (`DEFAULT_LS_NODE_LIMIT`, `base.py:28`) | yes (`context_cmd.py:78`) | yes (`context_cmd.py:231-242`) |
| **`find`** | **200** (backend's own) | **no** | **no** |

`find` has the smallest budget of the three and is the only one that is both unraisable
and silent. The server-side field already exists — `ContextQuery.node_limit`
(`ui/app/context_manager/base.py:218`, capped by `MAX_FIND_NODE_LIMIT = 10_000` at
`base.py:14`) — and `ContextClient.find()` already forwards it. **Only the CLI parser is
missing the flag** (`beril_cli/context_cmd.py:52-67`).

## Why it matters

`.claude/skills/knowledge-context/SKILL.md` makes `find` the default entry point — the
first row of "Picking the right command", and the seed query in "For other skills". The
skill's retrieval loop tells agents to stop "when two refinements surface nothing new",
which is exactly the wrong stopping rule against a silently truncated result set: an
agent concludes "no prior work exists" having seen 6% of it.

This is the same false-negative class as ISSUE-02 (`ls -r` depth) and ISSUE-03
(`files_scanned`), both of which were fixed by making the bound visible and raisable.
`find` is the remaining instance.

## Suggested fix

1. **Add `--node-limit` to the `find` parser**, mirroring `grep`'s wording
   (`context_cmd.py:91-95`):

   ```python
   find.add_argument(
       "--node-limit", type=int,
       help="Maximum nodes searched (default 200, up to 10000); a warning says when it is reached",
   )
   ```

   Nothing else needs plumbing — `_find()` can pass it straight through, and both
   `ContextClient.find()` and `ContextQuery` already accept it.

2. **Warn on truncation**, as `grep` and `ls` do. One wrinkle to design around: the
   existing warnings compare the returned count against the budget, which works because
   a grep match and an ls entry are each one node. For `find` they are not — a 200-node
   budget yielded 156 results, because nodes are document fragments that collapse into
   fewer hits. So `len(results) >= node_limit` will never fire.

   Either have the route report whether the budget was exhausted (cleanest — the backend
   knows), or, failing that, warn whenever `--node-limit` is omitted and the result count
   is within some margin of the default. The first is worth asking OpenViking for.

3. **Give the default a named constant** alongside `_DEFAULT_GREP_LIMIT` and
   `_DEFAULT_LS_LIMIT` (`context_cmd.py:34-38`) so the three budgets are documented in one
   place, and consider raising find's 200 toward ls's 1000 — it is the lowest of the three
   while being the most used.

4. **Document the bound** in SKILL.md's `find` section, which currently describes
   `--limit` only. The grep section's "Results are capped … Treat those results as
   incomplete" paragraph (SKILL.md:146) is the model to copy.

## Acceptance criteria

- [ ] `beril context find --node-limit N` exists and changes the result set.
- [ ] A truncated `find` prints a stderr warning, parseable output unaffected (`--json`
      stays clean).
- [ ] SKILL.md documents find's budget and tells agents not to conclude absence from a
      truncated result.
- [ ] Tests cover the flag reaching the request and the warning firing.
