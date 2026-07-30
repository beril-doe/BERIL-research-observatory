---
name: worklog-capture
description: Append a narrative entry to a project's WORKLOG.md as work happens. Invoked by other BERIL skills at lifecycle transitions and after each unit of analysis work.
allowed-tools: Read, Write, Edit, Bash
---

# Worklog Capture Protocol

This skill is not user-invocable. It is referenced by BERIL skills (`berdl_start`, `synthesize`, `berdl-review`, `submit`) and should be followed whenever a project advances.

The worklog answers **"what did the agent do, and why?"** for a human scanning a finished project. It is the narrative counterpart to `REPORT.md` (which answers "what did we find?").

## Where the worklog lives

`projects/<id>/WORKLOG.md` — append-only, one file per project, alongside `RESEARCH_PLAN.md` and `REPORT.md`.

Not in `memories/`. That directory is for cross-project knowledge destined for OpenViking ingestion (pitfalls, discoveries, performance). The worklog is project-local narrative and is not ingested.

## Entry format

```markdown
## {YYYY-MM-DD} · {what happened}{ → new_status}
## {YYYY-MM-DD} · ! {a correction}
{One to three sentences: what was done and *why*. The decision, not the mechanics.}
→ [{label}]({project-relative-path})
→ [{label}]({project-relative-path}) ×{n}
```

The `→ new_status` suffix appears **only** on the six lifecycle transitions. Work-unit entries omit it.

A **leading `!`** marks a correction — a bug found, a re-run, an approach abandoned. Use it whenever the entry records the project changing direction. These are the highest-value entries in the file, and the dashboard gives them an amber marker so a reader scanning the timeline finds the turning points without reading every entry. Without the `!` a correction is indistinguishable from "ran notebook 3". The marker is optional and unmarked worklogs parse exactly as before.

Worked example:

```markdown
## 2026-02-18 · plan written → proposed
Framed the question as three-way concordance (TnSeq / FBA / proteomics).
Rejected a pure TnSeq cutoff — no orthogonal check on a single-assay call.
→ [RESEARCH_PLAN.md](RESEARCH_PLAN.md)

## 2026-02-18 · essentiality vectors built
Per-gene vectors across the three sources. Dropped 412 genes absent from the
FBA model rather than imputing them — imputation would manufacture concordance.
→ [nb 01](notebooks/01_data_assembly.ipynb)
→ [fig](figures/data_assembly_overview.png) ×2

## 2026-02-18 · ! COG parsing bug
COG letters split on the wrong delimiter, inflating category counts. Re-ran 02
and added a threshold sensitivity pass to check the result wasn't cutoff-driven.
→ [nb 02](notebooks/02_concordance_analysis.ipynb)
→ [fig](figures/threshold_sensitivity.png)
```

## When to write an entry

### Lifecycle transitions — mandatory, one entry each

| Transition | Written by | Heading |
|---|---|---|
| project scaffolded (`exploration`) | `/berdl_start` Phase 0 | `project scaffolded → exploration` |
| `exploration` → `proposed` | `/berdl_start` Phase B | `plan written → proposed` |
| `proposed` → `active` | `/berdl_start` Phase C | `analysis started → active` |
| `active` → `analysis` | `/synthesize` | `findings synthesized → analysis` |
| `analysis` → `reviewed` | `/berdl-review` | `review completed → reviewed` |
| `reviewed` → `complete` | `/submit` | `approved by {ORCID} → complete` |

Demotions are transitions too: a `/synthesize` re-open of a `complete` project, or a `/berdl-review` hash-mismatch demote, gets its own entry saying what went stale and why.

### Work units — write one whenever any of these completes

- A notebook is written **and executed** (not on every cell run).
- A batch of figures is saved.
- A data export lands in `data/`.
- A correction: a bug found, a re-run, an approach abandoned. **These are the highest-value entries** — they are the only record of why the project isn't a straight line. Mark them with a leading `!` so they stand out on the dashboard.
- The plan changes mid-flight (pair it with the `RESEARCH_PLAN.md` Revision History bump).

## Rules

- **Append-only.** Never edit or delete a prior entry. If something turns out wrong, write a new entry saying so. The worklog is a record of what was believed when.
- **Never block.** No user approval, no confirmation prompt. Write the entry and continue the task. If the worklog write fails for any reason, carry on with the real work — a missing entry must never derail an analysis.
- **Log the why.** "Ran notebook 02" is worthless; the reader can see the notebook. "Dropped 412 genes rather than imputing — imputation would manufacture concordance" is the entry worth having.
- **Every link must resolve.** Paths are project-relative (`notebooks/02_x.ipynb`, not `projects/<id>/notebooks/02_x.ipynb`). Only link artifacts that exist on disk at write time.
- **One entry per event, not per file.** Six figures from one notebook are one entry with `×6`, not six entries.
- **Don't log noise.** File reads, individual queries, cell executions, `git add`. If it wouldn't appear in a lab notebook, it doesn't belong here.
- **Don't duplicate the pitfalls file.** A pitfall gets its full write-up in `memories/pitfalls.md` via `pitfall-capture`; the worklog gets one line noting the correction happened and what it changed.

## Creating the file

If `projects/<id>/WORKLOG.md` doesn't exist, the first entry creates it with a one-line header:

```markdown
# Worklog — {project_id}

{first entry}
```

Use `Write` to create, `Edit` to append. Entries go in chronological order, newest at the bottom.
