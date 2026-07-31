---
name: research-plan
description: Turn a research interest, live BERDL data, and literature into a detailed, pre-registered RESEARCH_PLAN.md with competing hypotheses, falsification tests, and decision criteria. Use when a project is ready to move from exploration to a frozen plan, or to resume an `exploration`/`proposed` project.
allowed-tools: Bash, Read, Write, Edit, WebSearch, AskUserQuestion
user-invocable: true
---

# Research Plan Skill

This is the **PLAN** workflow — the front of the research arc. It turns a researcher's interest, the data you actually found, and the literature into a *detailed, frozen, pre-registered* `RESEARCH_PLAN.md`: competing hypotheses with falsification-first framing, per-hypothesis predictions and decision criteria, a discrimination strategy, a feasibility verdict, and a per-notebook analysis plan.

It owns the lifecycle transition `exploration → proposed` and ends at the **mandatory plan-review checkpoint**. `beril.yaml` remains the sole lifecycle authority.

## Usage

```
/research-plan <project_id>
```

If no `<project_id>` argument is provided, detect from the current working directory (if inside `projects/{id}/`). This skill is normally reached from `/berdl_start` (it delegates Phase A/B here), but it is independently invocable.

## When to run

Run when a project is at `status: exploration` (or `proposed`, to iterate on an existing plan) and the researcher is ready to commit a line of inquiry. Inputs:

- the researcher's **interest** and goals;
- **live data discovery** via `/berdl` (on-cluster) or `/berdl-query` (off-cluster) — what tables actually exist, what they cover;
- **literature** via `/literature-review`, which writes to `projects/<id>/references.md`.

**Do NOT** write or execute analysis notebooks here. That is the EXECUTE workflow (`/execute-plan`), and it must not start until the plan-review checkpoint is approved.

## Phase A: Orientation & Exploration

Status: `exploration`. Read context, explore data, accept user-supplied input, and develop the raw material for hypotheses — all inside the project directory.

**Required reading before designing any queries:**
1. `PROJECT.md` — dual goals (science + knowledge capture), project structure, reproducibility standards, JupyterHub workflow, Spark notebook patterns.
2. `docs/overview.md` — data architecture, key tables, generation workflow, known limitations.
3. `docs/pitfalls.md` and `docs/performance.md` — **critical: read before any query design**. These are the frozen historical archives; per-project pitfalls hit by recent projects also live in `projects/*/memories/pitfalls.md` (worth a scan, especially for projects on the same database family).
4. `docs/research_ideas.md` — check for related ideas; avoid duplicating work.
5. Use `berdl_notebook_utils.get_databases(return_json=False)`, `get_tables(... return_json=False)`, and `get_table_schema(... detailed=True, return_json=False)` for live access-aware discovery. For database-specific gotchas, grep `docs/pitfalls.md` for the database name (e.g., `grep -A 20 "^## kbase\.ke_pangenome$" docs/pitfalls.md`); also check `projects/*/memories/pitfalls.md` for any project-tagged entries on the same database.
6. For "what's already known" on the research topic across projects, query the knowledge layer rather than scanning REPORTs by hand — see `knowledge-context`. Seed: `knowledge_query.py find "<topic>"` for concepts, or `grep "<exact db/term>" --uri viking://resources/` for the database's documented gotchas; then `read` the strongest hits.

**Setup check (Phase 1.5 of `/berdl_start` already verified KBASE_AUTH_TOKEN and proxy):**
6. `gh auth status` — needed for branches/PRs. Prompt `gh auth login` if missing.

**Engagement (status stays `exploration`):**
- Discuss the user's research interest and goals.
- **If the user has input data** (gene lists, phenotype tables, FASTAs, SQLite, etc.): drop it in `projects/<id>/user_data/`. Never leave user-supplied data in `~/` or the repo root.
- Run exploratory queries with `/berdl`. For any query worth keeping, save it as a numbered exploration notebook (`projects/<id>/notebooks/00_exploration.ipynb`, then `00b_*.ipynb` if you need more). Even rough exploration gets a home.
- Search literature with `/literature-review` if relevant. References go to `projects/<id>/references.md`.
- Check related prior work through the knowledge layer (`knowledge_query.py find "<topic>"` / `relations`), not by hand-scanning `projects/`. Read a specific project's files directly only once the knowledge layer points you to it.

When the user has a clear research interest and is ready to commit to a plan, transition to Phase B.

## Phase B: Draft the pre-registered plan

Status transition: `exploration` → `proposed`. Work through these steps in order. Steps 1–6 produce the *content* of the plan; step 7 writes the files; step 8 is the mandatory checkpoint.

### 1. Frame a sharp, answerable research question

Frame the question in **FINER / PICO** terms — the **problem**, the **comparator**, and the **outcome** — so it is sharp and answerable, not a vague theme. A good question already implies the comparison the data must make.

Before drafting, ask up to **3 grounded clarifying questions** — but only ones whose answers would actually change the analysis (the comparator, the population, the outcome metric). If nothing would change the analysis, skip them and proceed.

### 2. Draft competing hypotheses BEFORE asking the user's preference

Draft **H0** (null), **H1**, and **2–3 genuine rival hypotheses** (H2, optionally H3) that the available data could actually distinguish — *not strawmen*. A rival is genuine only if a real result could favor it over H1.

Draft these *before* asking which the user prefers. Anchoring on the user's favorite first produces strawman rivals; multiple working hypotheses (Chamberlin) means the rivals are taken seriously from the start.

### 3. Per-hypothesis prediction, falsification test, and decision criteria

For each hypothesis write:
- a **prediction** — what you would observe in the data if it were true;
- a **falsification test** — the single result that would reject it (Popper/Mayo: a hypothesis you cannot say how to refute is not yet testable);
- a **unit of analysis** — what one row is, and why those rows are independent (or the correction applied); check `.claude/reviewer/EVALUATION_INTEGRITY.md` items 5–11 and name any that apply;
- a **decision criterion** — the concrete threshold or comparison that adjudicates (e.g., "rho > 0.3, p < 0.01, one genome per GTDB genus, n ≥ 50 genera" — not "looks correlated", and not "≥ 50 species": shared ancestry inflates p without adding evidence [Felsenstein 1985]).

### 4. Discrimination strategy and confidence prior

- **Discrimination strategy**: the specific query or figure result that tells H1 / H2 / H3 *apart* (Platt's strong inference — design the crucial test that excludes a rival, not one that merely confirms a favorite).
- **Confidence prior**: HIGH / MEDIUM / LOW with a reason. Cite literature (`references.md`) for a HIGH prior. This is compared against the posterior at synthesis.

### 5. Feasibility check via cheap probes

Run a **feasibility** check using `/berdl-query` (off-cluster) or `/berdl` (on-cluster) **cheap probes only** — `DESCRIBE EXTENDED <db>.<table>`, `SHOW TABLES`, bounded `COUNT(DISTINCT id)` coverage checks. Do not run the full analysis here. Record:
- **Verdict**: `answerable | partial | not-answerable`.
- **Limiting tables / coverage**: what you probed and what you found (e.g., "annotation table covers only ~30% of genomes").

A **`not-answerable`** verdict **stops** the plan: reshape the question (Phase B step 1) before anything is frozen. Do not write a `RESEARCH_PLAN.md` for a question the data cannot answer.

### 6. Per-notebook Analysis Plan

Write the Analysis Plan as a **per-notebook spec**. For each notebook:
- **Goal** — what it establishes;
- **Discriminating/refuting query (run first)** — the crucial test for that step, and which hypotheses it separates; `/execute-plan` runs it *before* any confirmatory cells;
- **Expected output** — the CSV(s) / figure(s) it produces.

### 7. Write the plan

1. Write `projects/<id>/RESEARCH_PLAN.md` using the **Enriched Template** below. Fill every section; do not leave the competing-hypotheses table or the falsification column blank.
2. Update `projects/<id>/README.md` Status block to "Proposed — research plan written, awaiting analysis." Fill in any sections that became clearer (Overview, Research Question).
3. Update `beril.yaml`: `status: proposed`, `last_session_at` to now, `artifacts.research_plan: true`.
4. Commit: `feat(project): research plan for {id}`.

**STOP HERE.** The plan is the contract for what comes next. Do NOT write or execute notebooks. Proceed to the checkpoint.

### 8. Plan-review checkpoint (mandatory pause)

This pause is the key guard against rushing from plan to compute without human or independent review. **Never skip it** — this is the most important rule in the planning workflow and the easiest to violate.

Present the plan to the user concisely:
- Title and refined research question (FINER/PICO).
- Competing hypotheses (H0, H1, and the genuine rivals) and the discrimination strategy.
- Feasibility verdict and limiting tables.
- Query strategy summary (tables touched, filter strategy, estimated complexity).
- Expected outcomes (what supports H1, what supports H0, the unit of analysis each criterion rests on).

Then ask explicitly:

> "Plan ready to start analysis?
> (a) Approve — say so here and I record it with `uv run beril approve {project_id} --relayed`, or run `uv run beril approve {project_id}` yourself in a terminal for a `via: terminal` record; then I start the analysis (`/execute-plan {project_id}`)
> (b) Run an independent review first — `bash tools/review.sh {project_id} --type plan` writes `PLAN_REVIEW_<n>.md` with the exact `RESEARCH_PLAN.md` hash (use `--reviewer codex` for a second opinion), and/or invoke the **hypothesis-critic** agent to stress-test the competing hypotheses (are the rivals genuine or strawmen? does each have a falsification test + decision criterion? is the question answerable given the feasibility verdict?).
> (c) Iterate on the plan"

**Do not advance to `/execute-plan` until the user picks (a) *and* the approval is on disk.**

- If (a): the approval has to reach `beril.yaml` as a `plan_approval` block (ORCID, timestamp, `via`, plan hash) — the only place a human approval becomes a checkable fact. Two routes: the user runs `uv run beril approve {project_id}` in a terminal and answers the prompt (`via: terminal`), or — when the user approved right here in the conversation — you run `uv run beril approve {project_id} --relayed`, which prompts no one and records `via: agent-relayed`. Then **you** commit `beril.yaml`; that is your job, not the user's. **Never relay an approval the user did not actually give.** `--relayed` asserts they said yes; relaying unasked is a fabricated record, and it is visible in the manifest and in the diff next to the plan it names. That hash covers the plan above `## Revision History` — it is not the whole-file hash `tools/review.sh` stamps into a `PLAN_REVIEW_<n>.md`. Verify the block exists before handing off. Setting `status: active` records nothing; and analysis code written while the approval is missing or stale is logged to `projects/<id>/plan_deviations.jsonl` by `.claude/hooks/plan-gate.py`, which surfaces at review and submit time.
- If (b): invoke the plan reviewer and/or the hypothesis-critic agent (read-only, writes nothing), present the critique to the user, then re-ask. Reviewer/critic output is advisory — the user has final say.
- If (c): iterate on `RESEARCH_PLAN.md`. Record changes in Revision History as `- **v2** ({date}): {change description}`, then re-ask.

## Enriched RESEARCH_PLAN.md template (the frozen contract)

This skill owns this template. Fill every section.

```markdown
# Research Plan: {Title}

## Research Question
{FINER/PICO-framed: the problem, the comparison, the outcome — sharp and answerable}

## Competing Hypotheses
- **H0** (null): {…}
- **H1**: {…}
- **H2** (rival): {a genuine alternative the available data could distinguish — not a strawman}
- **H3** (rival, optional): {…}

### Per-hypothesis predictions, falsification & decision criteria
| Hypothesis | Prediction (what we'd observe if true) | Falsification test (result that rejects it) | Unit of analysis (what one row is; why independent) | Decision criterion (threshold/comparison) |
|---|---|---|---|---|
| H1 | {…} | {…} | {…} | {…} |
| H2 | {…} | {…} | {…} | {…} |
| H3 (optional) | {…} | {…} | {…} | {…} |

One row per substantive hypothesis (H1, H2, H3, …); the null H0 has no falsification test of its own — it is adjudicated by rejection (see Pre-registered Decision Rule).

## Discrimination Strategy
{The specific query/figure result that would tell H1 / H2 / H3 apart.}

## Confidence Prior
{HIGH / MEDIUM / LOW + why. Cite literature for HIGH. Compared against the posterior at synthesis.}

## Literature Context
{What's known, key references (references.md), identified gaps.}

## Feasibility
- **Verdict**: {answerable | partial | not-answerable}
- **Limiting tables / coverage**: {what was probed and found}

## Query Strategy
### Tables Required
| Table | Purpose | Estimated Rows | Filter Strategy |
|---|---|---|---|
| {table} | {why} | {count} | {how to filter} |
### Performance Plan
- **Tier**: {local bounded Spark SQL / JupyterHub Spark SQL}
- **Estimated complexity**: {simple / moderate / complex}
- **Known pitfalls**: {from pitfalls.md}

## Analysis Plan
### Notebook 1: {name}
- **Goal**: {what it establishes}
- **Discriminating/refuting query (run first)**: {the crucial test for this step; which hypotheses it separates, e.g. "H1 vs H2"}
- **Expected output**: {CSV/figures}
### Notebook 2: …

## Pre-registered Decision Rule
{How the Discrimination Strategy result selects among the hypotheses at synthesis, each tied to its own decision criterion above:
 H1's criterion met and rivals' not (signal not swamped) → H1 supported, with caveats;
 H2's (or H3's) criterion met instead → that rival supported;
 no hypothesis's strong-support beats its refuting evidence, or signal swamped → H0 not rejected;
 more than one criterion met → mixed evidence (say so plainly).}

## Expected Outcomes
- **If H1 supported**: {interpretation}
- **If H2 supported**: {interpretation}
- **If H3 supported** (when used): {interpretation}
- **If H0 not rejected**: {interpretation}

## Revision History
- **v1** ({date}): Initial plan

## Authors
{name, affiliation, ORCID}
```

## Integration

- **Reads from**: `PROJECT.md`, `docs/overview.md`, `docs/pitfalls.md`, `docs/performance.md`, `docs/research_ideas.md`, `projects/<id>/references.md`, `projects/<id>/user_data/`, related `projects/*/README.md`.
- **Calls**: `/berdl` or `/berdl-query` (data discovery + cheap feasibility probes), `/literature-review` (Phase A literature).
- **Writes**: `projects/<id>/RESEARCH_PLAN.md`, `projects/<id>/README.md` (Status), `projects/<id>/beril.yaml` (`status: proposed`, `artifacts.research_plan: true`).
- **Checkpoint tools** (advisory): `tools/review.sh --type plan` (writes `PLAN_REVIEW_<n>.md`), the **hypothesis-critic** agent (read-only critique of the hypotheses block).
- **Hands off to**: `/execute-plan` once the user approves at the checkpoint.

## Pitfall Detection

When you encounter errors, unexpected results, retry cycles, performance issues, or data surprises during this task, follow the pitfall-capture protocol. Read `.claude/skills/pitfall-capture/SKILL.md` and follow its instructions to determine whether the issue should be added to the active project's `projects/<id>/memories/pitfalls.md`.
