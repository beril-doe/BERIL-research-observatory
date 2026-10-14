---
name: knowledge-context
description: Use when searching what the observatory already knows — submitted projects and the central docs — before research, synthesis, or pitfall work. Covers `beril context` find/grep/ls/pitfalls/discoveries and how to follow a hit to its source.
allowed-tools: Bash, Read
user-invocable: true
---

# Knowledge Context Skill

BERIL keeps an indexed context layer over every submitted project and the central docs. Query it with `beril context`, which uses the user's `beril login`. Use it for fast recall, then read the underlying file before editing or citing: search results are a map, not the source of truth.

## Addresses

Every result names a resource by **address**: `<owner>/<project>/<path>`.

- **Projects:** `<owner ORCiD>/<project_id>/...`, for example `0009-0001-2345-6789/fitness_effects_conservation/REPORT.md/...`. Each submitted project carries its curated files (`README.md`, `RESEARCH_PLAN.md`, `REPORT.md`, `REVIEW.md`, `references.md`, `FINDINGS.md`, `EXECUTIVE_SUMMARY.md`, `FAILURE_ANALYSIS.md`, `DESIGN_NOTES.md`, `CORRECTIONS.md`, `beril.yaml`), plus:
  - `memories/*.md`;
  - `REFUTATION_<n>.md`;
  - `PROJECT_METADATA.md`, a generated table of project_id, title, status, authors, dates and branch. Use it for "by author" or "by status" lookups.
- **Central docs:** `beril/docs/<doc>/...` for `pitfalls`, `discoveries`, `performance` and `research_ideas`.

Documents are indexed in fragments, so a hit's address usually continues past the file name. In `0009-…/alpha/REPORT.md/REPORT.md` or `beril/docs/pitfalls/pitfalls/Foreign_Key_Gotchas.md`, **the third segment is the source file**:

| Address starts with | Read this file |
|---|---|
| `<owner>/<project>/<file>/…` | `projects/<project>/<file>` in this checkout |
| `beril/docs/<doc>/…` | `docs/<doc>.md` |

If the project isn't in the checkout (someone else's, not yet merged), read it through the context layer: `beril context find "<topic>" --address <owner>/<project>/<file> --read-content`.

Any address can be passed back to scope a read: `--address A`, or as `ls`'s argument.

## Picking the right command

| Question | Use | Why |
|---|---|---|
| Free-text / fuzzy ("anything about phage timing?") | `find` | Semantic top-K across everything |
| Time-bounded ("changed in the last 7 days") | `find --since 7d --time-field updated_at` | Server-side time filter |
| Exact name / ID / ORCiD / table ("every mention of Ada Lovelace") | `grep` | Literal matches, not a ranked top-K (capped by `--node-limit`; see `grep` below) |
| Has this gotcha been hit before? | `pitfalls` | Project memories plus the central archive, as documents |
| What has been found about X? | `discoveries` | Findings, with stale central duplicates already suppressed |
| What exists ("list every project") | `ls` | A listing question; embeddings can't enumerate |
| The full text of a hit | `find --address <hit> --read-content` | Or read the local file (see § Addresses) |

This is a toolkit, not a single command. Use it like bash: pick a command, look at what comes back, and **follow up**. § Using the toolkit with judgment covers when `find` is the wrong tool and how to refine. The command reference is further down.

### Scope

- With no scope, `find` searches **everything**: every owner's projects and the central docs.
- `ls` and `grep` with no scope look only at the user's own projects.

To narrow or widen:

- `--project <id>` means **the user's own** project of that name. For a project whoever owns it, add `--all-owners`: `--project <id> --all-owners`.
- `--owner <ORCiD>` narrows to one person; `--all-owners` spans everyone.
- `--path <p>` narrows to a path within `--project`.
- `--docs` means the central docs (`beril/docs`).
- `--address <owner/project/path>` takes an address from an earlier result.

Contradictory flags (an address plus `--project`, or `--owner` plus `--all-owners`) are refused before anything is sent. So are misspelled flags.

## Using the toolkit with judgment

### When `find` is *not* the right tool

`find` is semantic top-K, best for exploring an unfamiliar concept. Reach for something else when:

- You need **every literal hit** rather than a ranked top-K: use `grep`, with a `--node-limit` large enough (see the cap under `grep`).
- You know the **exact token** (a gene ID, ORCiD, error string or table name): use `grep`, because semantic ranking can bury an exact string.
- The question is a **known gotcha** or a **prior finding**: use `pitfalls` / `discoveries`. They return whole documents and apply the project-memory precedence rules for you.
- You need to **enumerate**: use `ls`.

### The retrieval loop

A first query is a starting point, not the answer. Read the result, then move:

- **Too many or vague hits:** tighten the terms, add `--score-threshold 0.5`, or scope with `--project <id> --all-owners` / `--docs`.
- **Too few or zero hits:** broaden the terms, drop the threshold, widen the scope, or switch from `find` to `grep` on a single defining token.
- **A promising hit:** read its source file (see § Addresses). To find related work, `find` on the theme the hit turned out to be about.
- **Stop** when you can name the source files that answer the question, or when two refinements surface nothing new. Don't keep querying past sufficiency.

Once a hit looks right, **read the underlying file** before editing or citing it.

### Drill-down chains (worked examples)

```bash
# "What's known about X?"  broad find -> read the strongest hit -> find related work
beril context find "metal resistance biogeography" --limit 5
#   top hit 0009-…/metal_atlas/REPORT.md/… -> read projects/metal_atlas/REPORT.md
beril context find "<the hit's specific organism or method>" --limit 5

# "Has anyone already done Y?"  find -> if vague, grep a defining term
beril context find "carbon formulation scoring"
beril context grep "CF formulation" --all-owners -i

# "Pitfalls for database Z?"  purpose-built, exact-token match
beril context pitfalls "kbase_ke_pangenome" --exact
```

### When BERIL is unreachable

There is **no offline fallback**: when BERIL can't be reached, `beril context` fails and says so. Run the diagnostic to see why:

```bash
beril context doctor     # OK | NOT_LOGGED_IN | UNREACHABLE | AUTH_FAILED | UNAVAILABLE (exit 0/1)
```

- `NOT_LOGGED_IN` / `AUTH_FAILED`: the user runs `beril login`.
- `UNREACHABLE`: a network or server problem.
- `UNAVAILABLE`: BERIL is up but its context layer isn't answering.

In every failure case, tell the user, and fall back to reading this checkout's own files with your normal tools: `projects/*/` and `docs/{pitfalls,discoveries,performance}.md`. That covers only what's in this checkout, with no semantic search and nothing submitted elsewhere, so say that recall is partial.

## Command reference

Every command takes `--json` to print the raw response (addresses included), for filtering with `jq`.

### `find`: semantic search

```bash
beril context find "query terms"                                  # everything
beril context find "query terms" --project <id> --all-owners      # one project, any owner
beril context find "query terms" --project <id>                   # one of the user's own projects
beril context find "query terms" --docs                           # central docs only
beril context find "query terms" --address <owner>/<project>/REPORT.md
beril context find "query terms" --since 7d --time-field updated_at
beril context find "query terms" --score-threshold 0.5 --limit 25
beril context find "query terms" --read-content                   # full text, not just abstracts
```

Output is `N result(s)`, then for each hit: its address, `score: 0.xxx`, and its abstract (plus `--- content ---` with `--read-content`).

### `grep`: exact-pattern search

Literal matches across all indexed file content in scope. Matches include incidental mentions, not just structured fields (see § Common workflows for the by-author caveat).

**Results are capped.** At most `--node-limit` matches come back: 256 by default, 10,000 at most. When a search reaches the cap, `beril context grep` prints a `warning: results stopped at the N-match limit` on stderr. **Treat those results as incomplete**: raise `--node-limit` or narrow the scope before concluding that something is absent or that a list is complete.

```bash
beril context grep "Ada Lovelace" --all-owners
beril context grep "0000-0002" --all-owners -i
beril context grep "TODO" --project <id> --all-owners --node-limit 50
beril context grep "deprecated" --all-owners --exclude beril/docs
beril context grep "kbase_ke_pangenome" --docs
```

Output is `address:line: text` per match, then a count. Flags: `-i/--case-insensitive`, `--node-limit N`, `--exclude <address>`.

### `pitfalls` / `discoveries`: purpose-built document searches

```bash
beril context pitfalls "spark OOM"                       # semantic
beril context pitfalls "kbase_ke_pangenome" --exact      # literal token match
beril context pitfalls --project <id>                    # one of the user's own projects (+ central)
beril context pitfalls --owner <ORCiD>                   # one owner's projects (+ central)
beril context discoveries "core genome"                  # findings, stale duplicates suppressed
beril context discoveries                                # list every discovery document
```

Each result is a **document**: its address, its origin, its score and the matching excerpts.
- `pitfalls` origins: `project_memory` (with the project) or `central`.
- `discoveries` origins: `project_memory`, `central_legacy` or `central_background`.

The header reports how many stale central duplicates were suppressed in favor of a project's own copy.

### `ls`: listing

```bash
beril context ls                                  # the user's own projects
beril context ls --all-owners --simple            # every owner
beril context ls <owner>                          # one owner's projects
beril context ls <owner>/<project> -r             # a project's files, recursively
beril context ls beril/docs                       # the central docs
```

Directories end in `/`. With `--json`, each entry carries `name`, `isDir`, `size` and `modTime`.

## Common workflows

**"Find all projects by an author":** `grep` matches **all** file content, not just author rows, so expect false positives from incidental mentions. Use a generous `--node-limit` (e.g. 2000) and check for the truncation warning. For an authoritative list, keep only matches in the generated metadata file:

```bash
beril context grep "Ada Lovelace" --all-owners --node-limit 2000 --json \
  | jq -r '[.matches[] | select(.address | contains("/PROJECT_METADATA.md")) | .address | split("/")[1]] | unique | .[]'
```

**"What changed in the last week?":** `find` needs a non-empty query, so use a topic word or a broad term:

```bash
beril context find "BERIL" --since 7d --time-field updated_at --limit 50
```

**"List every project":**

```bash
for owner in $(beril context ls --all-owners --simple); do beril context ls "$owner" --simple; done
# beril/docs in that list is the central docs, not a project.
```

**"What does this project relate to?":** read its `REPORT.md`, then `find` on its theme, organism or method.

## How content gets in

A project enters the context layer when `/submit` approves and archives it: after the lakehouse archive succeeds, `/submit` mirrors the approved files into the context layer. See the `submit` skill. Editing files in the checkout changes nothing in the index until the project is submitted again. Central docs are maintained by BERIL admins.

**The mirror is best-effort.** The archive can succeed while the mirror is skipped (BERIL unreachable, not logged in) or fails. `/submit` reports which in its `context_submission` verdict (`ok`, `skipped` or `failed`). After a `/submit`, check that verdict before telling the user the project is searchable. If it's `skipped` or `failed`, the project's approver can retry the same mirror. It goes through BERIL with their login, and files that already landed are skipped:

```bash
uv run knowledge/scripts/ingest_context.py --project <project_id> --json
```

So **absence from results is not proof of absence**: a submitted project whose mirror never landed won't appear. When "no prior work" matters, also check this checkout's `projects/` before concluding.

## For other skills

Any skill that answers a **cross-project** question ("what's known", "what's been done", "is this already documented", "what relates to X") should consult the knowledge layer first instead of scanning `projects/*` by hand. The convention:

1. Run a query from § Using the toolkit with judgment with a topic-specific seed (each calling skill supplies its own starter query).
2. Treat results as a **map**: read the underlying file before citing.
3. Iterate per the retrieval loop, and stop at sufficiency.
4. If `beril context` fails, run `beril context doctor`, tell the user, and fall back to this checkout's files. Recall is partial.

Skills should reference this skill rather than embedding the loop, so the guidance stays in one place.
