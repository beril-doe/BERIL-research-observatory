# `knowledge-context` skill: the "find all projects by an author" workflow is both unrunnable and incomplete

**Severity:** Medium — the skill's one "authoritative" recipe fails on the hub, and would under-report by ~75% if it ran
**Area:** skills, environment image
**Labels:** bug, docs, environment

## Environment

| | |
|---|---|
| Repo | `/home/wjriehl/beril-context`, branch `cm-beril-context-cli`, HEAD `2237c9aa` |
| CLI | `.venv/bin/beril`, `beril-cli` `0.1.2.dev221+g9f7c612bb` (editable install) |
| Host | BERDL JupyterHub pod (on-cluster) |
| Observed | 2026-10-28 |

Three separable problems in `.claude/skills/knowledge-context/SKILL.md`, ordered by
severity.

---

## 1. The by-author result set covers only 17 of 72 indexed projects

SKILL.md:189-193 presents filtering to `PROJECT_METADATA.md` as the way to get an
**authoritative** author list, as against raw `grep`'s incidental mentions. But most
projects have no indexed `PROJECT_METADATA.md`, so the "authoritative" filter is in fact
the least complete option available.

```bash
.venv/bin/beril context grep "0000-" --all-owners --node-limit 10000 --json \
  | python3 -c '
import sys,json
d=json.load(sys.stdin)
md={m["address"] for m in d["matches"] if "/PROJECT_METADATA.md" in m["address"]}
print("total matches:",d["count"])
print("distinct projects with PROJECT_METADATA.md:",len({a.split("/")[1] for a in md}))'
```

```
total matches: 178
distinct projects with PROJECT_METADATA.md: 17
```

No truncation warning was emitted (178 ≪ the 10000 cap), so this is a complete count, not
a capped one. Against 72 indexed projects across 13 owners, coverage is ~24%.

Concretely: Paramvir S. Dehal (`0000-0001-5810-2497`) owns **39** indexed projects, but
the documented recipe returns **one**:

```bash
.venv/bin/beril context grep "Paramvir S. Dehal" --all-owners --node-limit 2000 --json \
  | python3 -c 'import sys,json; print(*sorted({m["address"].split("/")[1] for m in json.load(sys.stdin)["matches"] if "/PROJECT_METADATA.md" in m["address"]}), sep="\n")'
# metal_cross_resistance
```

**Probable cause:** SKILL.md:30 notes `PROJECT_METADATA.md` is generated at submit time,
so projects submitted before that generator existed have none. Worth confirming against
`/submit`, since if so the gap will close only for newly submitted work and the skill
needs to say so today.

**Suggested fix:** either stop calling this authoritative and state the coverage caveat,
or replace it with something that actually enumerates — e.g. `ls` per owner (which is
complete, see SKILL.md:205) combined with a per-project author lookup, falling back to
`PROJECT_METADATA.md` only where it exists. An agent asked "what has this person worked
on?" currently gets a confident, badly wrong answer.

---

## 2. The recipe depends on `jq`, which is absent from the hub image

```bash
command -v jq
# (nothing)
ls /usr/bin/jq /opt/conda/bin/jq
# ls: cannot access '/usr/bin/jq': No such file or directory
# ls: cannot access '/opt/conda/bin/jq': No such file or directory
```

Running SKILL.md:192-193 verbatim:

```
/bin/bash: line 19: jq: command not found      (exit 127)
```

The `beril context` half works; only the filter fails. Also affects SKILL.md:125, which
tells agents `--json` output is "for filtering with `jq`".

**Suggested fix** — either:

1. Add `jq` to the hub image (it is a reasonable baseline and the skill assumes it), or
2. Use stdlib Python, guaranteed present wherever the CLI runs:

   ```bash
   beril context grep "Ada Lovelace" --all-owners --node-limit 2000 --json \
     | python3 -c 'import sys,json; print(*sorted({m["address"].split("/")[1] for m in json.load(sys.stdin)["matches"] if "/PROJECT_METADATA.md" in m["address"]}), sep="\n")'
   ```

   Tested on this pod: exit 0, and on a real author it returns the same single row the
   `jq` form would. (It inherits problem 1 — this fixes runnability, not coverage.)

   If you take route 2, soften SKILL.md:125 to "for filtering with `jq` or `python3 -c`".

---

## 3. One address example in the table is wrong

SKILL.md:28, in the "Hit address → Read this file" table:

| Hit address | Read this file |
|---|---|
| `beril/docs/pitfalls/pitfalls/Foreign_Key_Gotchas.md` | `docs/pitfalls.md` |

Real addresses carry a category segment between the doc name and the leaf:

```
beril/docs/pitfalls/pitfalls/BERDL_Database_Common_Pitfalls_Gotchas/Foreign_Key_Gotchas.md
```

The rule stated at line 22 ("For a central doc, the doc's name is the segment after
`beril/docs/`") is correct and still yields `docs/pitfalls.md`; only the illustration is
off. Worth fixing so the example matches what an agent actually sees.

---

## Acceptance criteria

- [ ] The by-author workflow either enumerates completely, or states its coverage limit
      where an agent will read it before trusting the result.
- [ ] The documented command runs to completion on the BERDL hub pod.
- [ ] SKILL.md:125 does not assume a tool that may be absent.
- [ ] SKILL.md:28's example address matches a real one.
