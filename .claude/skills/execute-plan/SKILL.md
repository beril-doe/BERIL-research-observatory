---
name: execute-plan
description: Read a frozen RESEARCH_PLAN.md and build, run, and write up the analysis — running each notebook's discriminating query first, then synthesizing a REPORT.md. Use when `projects/<id>/beril.yaml` carries a `plan_approval` block whose `plan_hash` matches the current RESEARCH_PLAN.md, and analysis should begin or resume. Without that block the plan-review checkpoint has not happened — `status` alone is not approval.
allowed-tools: Bash, Read, Write, Edit, WebSearch, AskUserQuestion
user-invocable: true
---

# Execute Plan Skill

This is the **EXECUTE** workflow — the middle of the research arc. It reads the *frozen* `RESEARCH_PLAN.md` (the contract), then builds and runs the planned notebooks and hands off to synthesis and review.

It owns the lifecycle transitions `proposed → active → analysis`. The plan pins the science and the decision rules; execution owns the exact code and may revise the plan — but a *material* change demotes the project and re-runs the plan-review checkpoint (see the Revision Loop). `beril.yaml` remains the sole lifecycle authority.

## Usage

```
/execute-plan <project_id>
```

If no `<project_id>` argument is provided, detect from the current working directory (if inside `projects/{id}/`). This skill is normally reached from `/berdl_start` (it delegates Phase C/D here), but it is independently invocable.

## Precondition: the plan must be frozen and approved

1. Read the **frozen** `projects/<id>/RESEARCH_PLAN.md` — the contract: competing hypotheses, falsification tests, decision criteria, per-notebook analysis plan.
2. Confirm the approval **on disk**. `status` is not evidence — a plan you just wrote and a plan a human approved are both `proposed`. The only witness is the `plan_approval` block in `beril.yaml`:
   ```bash
   grep -A3 '^plan_approval:' projects/<id>/beril.yaml
   ```
   If it is absent, or its `plan_hash` no longer matches the current plan, **do not start analysis**: return to the `/research-plan` checkpoint and ask the user to approve. If they approve in the conversation, record it with `uv run beril approve <id> --relayed` (`via: agent-relayed`) and commit `beril.yaml`; they can also run `uv run beril approve <id>` in a terminal themselves (`via: terminal`). Never relay an approval the user did not give. Nothing stops you mechanically; `.claude/hooks/plan-gate.py` always lets the write through and appends a record to `projects/<id>/plan_deviations.jsonl`, which surfaces (advisory, never blocking) at review and submit time. Not being blocked is not permission.
   The digest covers the plan **above `## Revision History`**, so a minor Revision-History append leaves the approval valid while a material edit (hypotheses, thresholds, discrimination strategy) invalidates it — the Revision Loop rule below.
3. If `status` is already `active`, the analysis is being resumed — pick up at the next unfinished notebook.

## Phase C: Analysis (Notebooks)

Status transition: `proposed` → `active`.

- Update `beril.yaml`: `status: active`, `last_session_at` to now.
- Append a worklog entry (`analysis started → active`) — see `.claude/skills/worklog-capture/SKILL.md`.
- For **each notebook in the Analysis Plan**, in order:
  1. Create the numbered analysis notebook (`01_data_exploration.ipynb`, `02_analysis.ipynb`, …) following the per-notebook spec in `RESEARCH_PLAN.md`.
  2. **Run the discriminating/refuting query FIRST** (Platt's strong inference): the crucial test the plan named for this step goes *before* any confirmatory cells. Lead with the result that could refute the hypothesis, not the one that would confirm a favorite. This is the forward complement of post-hoc refutation.
  3. Produce the **expected output** named in the plan (the CSV(s) / figure(s)), then execute the remaining cells, inspect outputs, iterate.
  4. **Update `projects/<id>/SCOREBOARD.md`** — one row per *hypothesis* (a notebook often moves several), using this shape exactly:

     ```markdown
     # Scoreboard — {project title}
     <!-- plan_hash: sha256:… -->  **2 of 5 notebooks run**

     | Hypothesis | Standing | Criterion | Observed (unit, n) | Where |
     |---|---|---|---|---|
     | H1 | open | rho > 0.3, n ≥ 50 genera | — | NB04 (not run) |
     | H2 | refuted | ≥ 40% supports, < 20% refutes | 12% vs 11% base rate; gene cluster, n = 3,104 | `notebooks/03_mge.ipynb` cell 9 |
     | H3 | needs-evidence | < 10% refutes, > 50% supports | 31%: criterion adjudicates neither | `notebooks/02_floor.ipynb` cell 14 |
     ```

     `Standing` is one of `open | supported | refuted | needs-replication | blocked | needs-evidence` (`beril_cli/science.py` `CLAIM_STATUSES`), so rows carry into `REPORT.md` `## Claims` unchanged. Applying a pre-registered criterion to a number is arithmetic, not interpretation — what stays out is *why*: no mechanism, no literature, no "suggests that". No locator → the row stays `open`. New plans only; an in-flight project starts at its next un-run notebook and says so in the header.
  5. **Commit** after the notebook is complete (and after any data extraction or key result reproduced).
  6. **Append a worklog entry** for that milestone — the notebook run, the figures saved, the data exported, or a correction (a bug found, a re-run, an approach abandoned). Corrections matter most: they are the only record of why the project was not a straight line. See `.claude/skills/worklog-capture/SKILL.md`.
- Notebooks are the primary audit trail — do as much work as possible in notebooks so humans can inspect intermediate results. When parallel execution or complex pipelines are needed, write scripts in `projects/<id>/src/` but call them from notebooks.
- **Capture pitfalls** as you go via `.claude/skills/pitfall-capture/SKILL.md` (appends to `projects/<id>/memories/pitfalls.md`). Re-read `docs/pitfalls.md` and `docs/performance.md` when something doesn't behave as expected.

### Revision Loop

The plan is a contract; revisions are explicit, not silent. As analysis proceeds:

- **Minor deviation** (a tweaked filter, a renamed output, an extra exploratory cell that doesn't change the science): append to `RESEARCH_PLAN.md` Revision History as `- **v{n}** ({date}): {change}` and **continue**.
- **MATERIAL change** to the pre-registered contract — dropping or adding a hypothesis, moving a decision threshold, abandoning the discrimination strategy, or changing what result would refute H1: this is no longer the plan that was approved. **Demote `active → proposed`** in `beril.yaml`, record the reason in Revision History, and **re-run the plan-review checkpoint** (return to `/research-plan` step 8). Do not continue analysis on a materially-changed plan without re-approval.
- **Which cutoffs are material**: a changed cutoff is material only when that value **appears in a decision criterion**; log the rest and continue. Same when the realized cohort puts a criterion out of reach — mark that row `blocked`.

### Checkpoint: Results Review

After notebooks are executed and committed, pause and present key results before synthesis.

- Summarize the key results: main statistics, notable patterns, anything unexpected. Render computed signals as words, not fabricated numbers — the only numbers shown are real counts and statistics actually produced by the notebooks.
- Ask: "Look at the notebooks/figures before I write up findings, or proceed with `/synthesize`?"
- If the user wants to explore first, wait. If they want changes, iterate on the notebooks before proceeding.

## Phase D: Synthesis & Writeup

Status transition: `active` → `analysis` (handled by `/synthesize` itself).

- Run `/synthesize` to create `REPORT.md`. The skill compares results against the **pre-registered decision rule** and confidence prior in `RESEARCH_PLAN.md`, updates `beril.yaml` automatically (`status: analysis`, `artifacts.report: true`, `last_session_at`), and updates `README.md` Status to "Analysis — report drafted, awaiting `/berdl-review` and `/submit`."
- Commit the report and updated `beril.yaml`.
- Discuss the report with the user — revise if needed.

## Hand-off to Review & Submit

Execution ends at synthesis. Hand the project to the existing back of the arc:

- **`/berdl-review {project_id}`** — produces a numbered `REVIEW_N.md` with a report-hash footer; flips `status: analysis → reviewed`. Iterate freely (different models, multiple opinions).
- **`/submit {project_id}`** — verifies the latest review covers the current `REPORT.md`, checks the configured ORCID, asks for explicit approval, uploads to the lakehouse, and writes the `SUBMITTED.md` marker; flips `status: reviewed → complete`.

When the provenance/trust layer is present, `/berdl-refute` and the claims ledger (`claims.json`) complement this back-of-arc handoff — `/berdl-refute` is the post-analysis counterpart to the discriminating-query-first discipline above. These are referenced as complementary **when present**; everything here works unchanged on a repo without them, and the canonical handoff is `/berdl-review` + `/submit`.

## Integration

- **Reads from**: `projects/<id>/RESEARCH_PLAN.md` (frozen contract), `projects/<id>/beril.yaml` (`plan_approval`), `docs/pitfalls.md`, `docs/performance.md`, `projects/*/memories/pitfalls.md`.
- **Writes**: numbered notebooks under `projects/<id>/notebooks/`, data under `data/`, figures under `figures/`, `SCOREBOARD.md`, `RESEARCH_PLAN.md` Revision History, `beril.yaml` (`status: active`; demote to `proposed` on a material change).
- **Calls**: `/berdl` or `/berdl-query` (running queries), `/pitfall-capture` (logging gotchas), `/synthesize` (Phase D → `REPORT.md`).
- **Hands off to**: `/berdl-review` + `/submit` (and `/berdl-refute` + the claims ledger when present).

## Pitfall Detection

When you encounter errors, unexpected results, retry cycles, performance issues, or data surprises during this task, follow the pitfall-capture protocol. Read `.claude/skills/pitfall-capture/SKILL.md` and follow its instructions to determine whether the issue should be added to the active project's `projects/<id>/memories/pitfalls.md`.
