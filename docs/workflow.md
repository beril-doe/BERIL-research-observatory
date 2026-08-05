# Research Workflow

**Purpose**: How to run a research project in the BERIL Research Observatory — from
a question to an archived report. For *why* the workflow is shaped this way and the
scientific ideas behind it, see [scientific-planning.md](scientific-planning.md);
for the data architecture see [overview.md](overview.md) and [schema.md](schema.md).

---

## The arc at a glance

A line of inquiry moves through three stages over one shared substrate. Each stage
is a skill; `beril.yaml.status` records where the project is.

```
/research-plan   ──►   /execute-plan   ──►   /berdl-review   ──►   /submit
   PLAN                  EXECUTE               REVIEW                SUBMIT
exploration→proposed   proposed→active→analysis      →reviewed            →complete
```

- **`/berdl_start`** is onboarding **and a router**: it scaffolds a project and
  sends you to the right stage. For an existing project it resumes at the stage
  matching the current `status`.

Run the whole thing through `/berdl_start`, or invoke any stage directly.

---

## Stage 1 — Plan (`/research-plan`)

Turns a research interest + live BERDL data + literature into a **frozen,
pre-registered** `RESEARCH_PLAN.md`. Owns `exploration → proposed`.

The plan must contain:
- a sharp, answerable **research question** (FINER / PICO framing);
- **competing hypotheses** — H0/H1 plus 2–3 *genuine* rivals, drafted before you
  state a preference (Chamberlin's multiple working hypotheses);
- per hypothesis: a **prediction**, a **falsification test** (the result that would
  reject it), and a **decision criterion**;
- a **discrimination strategy** — the query/figure that tells the rivals apart;
- a **feasibility verdict** (`answerable | partial | not-answerable`) from cheap
  data probes; `not-answerable` stops and reshapes the question;
- a **per-notebook analysis spec** (goal + expected output + the discriminating
  query that runs first).

It ends at the **mandatory plan-review checkpoint** — approve, run an independent
review (`tools/review.sh --type plan` and/or the read-only **hypothesis-critic** via
`/critique-hypotheses`), or iterate. `/execute-plan` will not begin analysis until you
approve — and analysis code written before you do is recorded, not refused.
**The plan is a contract, frozen before any results are seen.**

Approving means getting a `plan_approval` block into `beril.yaml`. Approve in the
conversation and the agent records it for you:

```bash
uv run beril approve <project_id> --relayed
```

or run it yourself in a terminal, without the flag, and answer the prompt:

```bash
uv run beril approve <project_id>
```

Either way the block carries your ORCID, a timestamp, a `plan_hash`, and a `via`
field naming the route (`agent-relayed` or `terminal`). That block is the only thing
that turns "a human read this plan" into a checkable fact; `status` is not it. See
[the plan-approval witness](#the-plan-approval-witness) below.

---

## Stage 2 — Execute (`/execute-plan`)

Reads the *frozen* plan and runs it. Owns `proposed → active → analysis`.

- For each planned notebook, runs the **discriminating/refuting query first**
  (Platt's strong inference — try to break the hypothesis before confirming it),
  then the rest; commits after each milestone.
- **Revision loop:** a minor deviation is logged in the plan's Revision History and
  execution continues; a *material* change (dropping/adding a hypothesis, moving a
  decision threshold, abandoning the discrimination strategy) **demotes
  `active → proposed`** and re-runs the plan-review checkpoint — you can't silently
  rewrite a pre-registered contract after seeing data.
- Ends by running `/synthesize` → `REPORT.md`, then hands off to review.

---

## Stage 3 — Review & Submit

- **`/berdl-review`** — independent review of the report (`analysis → reviewed`).
  **`/berdl-refute`** adds a post-hoc disconfirmation pass, and the claims ledger
  (`beril claims`, `claims.json`) tracks groundedness — both advisory.
- **`/submit`** — ORCID-gated approval and lakehouse archival
  (`reviewed → complete`).

---

## The plan-approval witness

`/submit` at the end is the repo's one hard gate (no ORCID, no submission). The
plan-review checkpoint at the seam between planning and analysis is mandatory as a
matter of process, but it is backed by a **witness** rather than a block:
`/execute-plan` is instructed not to start without an approval on disk — that is
prose discipline the agent follows, not machinery that stops it — and departing
from the plan leaves a record.

**What `beril approve` records.** `uv run beril approve <project_id>` writes a
`plan_approval` block to `beril.yaml`: ORCID, timestamp, a digest of the plan, and
`via` — `terminal` when you answered the prompt yourself, `agent-relayed` when you
approved in conversation and the agent ran it with `--relayed`. Without a TTY and
without `--relayed` it refuses, but treat that check as a speed
bump rather than a barrier — an agent that allocates a pty can drive the prompt, and
the block it writes is byte-indistinguishable from one you wrote. What actually makes
the record trustworthy is that `beril.yaml` is a reviewed file: the approval shows up
in the diff at PR time, next to the plan it claims to approve. `status` is **never**
read — an agent setting `status: active` records nothing, because the point is that a
self-written plan and a human-approved one must not look the same.

**What the hash covers.** `plan_digest` hashes `RESEARCH_PLAN.md` **above the
`## Revision History` heading** (the whole file if that heading is absent). So a
minor deviation logged as a Revision History append leaves the approval valid, while
a material change — a hypothesis, a decision threshold, the discrimination strategy —
invalidates it and sends you back to the checkpoint for a fresh `beril approve`. This
is a different hash from `tools/review.sh`'s whole-file `plan_hash` footer, which
deliberately covers every byte.

**What the hook does.** `.claude/hooks/plan-gate.py` (`PreToolUse`) does **not** stop
you — it always exits 0 and never refuses a tool call. When analysis code (`.ipynb`,
`.py`) is written under a project whose plan has no matching approval, it appends a
record to `projects/<id>/plan_deviations.jsonl`. Two readers surface that record and
both are advisory: `/berdl-review` reports it under Methodology, and `/submit` prints
a `WARN` per record. Neither blocks. Exploration and light analysis are supported and
never blocked.

**Why a witness and not a block.** Pre-registration integrity does not require that
departing from a frozen plan be impossible, only that it be undeniable. A skipped
checkpoint stops being a silent omission indistinguishable from approval and becomes
a dated record in the project and in git history.

---

## Skills & commands

| Entry point | Stage | What it does |
|---|---|---|
| `/berdl_start` | onboarding | Orient, scaffold a project, route to the right stage |
| `/research-plan` | Plan | Frame the question + competing hypotheses → frozen `RESEARCH_PLAN.md` |
| `/critique-hypotheses` | Plan | Run the read-only hypothesis-critic on a draft plan (advisory) |
| `/execute-plan` | Execute | Build/run notebooks from the frozen plan → `REPORT.md` |
| `/synthesize` | Execute | Interpret notebook outputs → `REPORT.md` |
| `/berdl-review` | Review | Independent review of the report |
| `/submit` | Submit | ORCID-gated approval + lakehouse archival |
| `/berdl`, `/berdl-query` | any | Discover and query BERDL data |
| `/literature-review` | Plan | Search the literature → `references.md` |
| `/suggest-research` | — | Propose the next high-impact research topic |

The **hypothesis-critic** subagent (`.claude/agents/hypothesis-critic.md`) is
read-only and writes nothing — the pre-analysis complement to `/berdl-refute`. The
`pitfall-capture` protocol runs automatically when errors or data surprises occur.

---

## Tutorial: your first project

1. **Start.** Run `/berdl_start`, choose "Start a new research project", and
   describe your interest — e.g. *"do species with open pangenomes occupy more
   diverse environments than those with closed pangenomes?"*
2. **Plan.** `/research-plan` explores the data, drafts competing hypotheses with a
   falsification test and decision criterion each, checks feasibility, and writes a
   frozen `RESEARCH_PLAN.md`. Review it at the checkpoint and approve — in the
   conversation (the agent records it with `--relayed`), or by running
   `uv run beril approve <project_id>` yourself in a terminal. The recorded
   `plan_approval` is what makes your approval a fact the rest of the workflow
   can check.
3. **Execute.** `/execute-plan` runs each notebook's discriminating query first,
   iterates, and synthesizes `REPORT.md`. If a result forces a material change to
   the plan, it returns you to the checkpoint.
4. **Review & submit.** `/berdl-review`, then `/submit` to approve and archive.
5. **Resume anytime.** Reopening `/berdl_start` routes you back to the stage
   matching `beril.yaml.status` and picks up from there.

Final project layout:

```
projects/pangenome_openness_environment/
  beril.yaml            <-- lifecycle authority (status, authors, plan_approval, approval)
  README.md             <-- overview, status, reproduction
  RESEARCH_PLAN.md      <-- frozen plan: competing hypotheses, falsification tests
  REPORT.md             <-- findings, interpretation, evidence
  REVIEW.md             <-- approved review
  references.md
  notebooks/  data/  figures/
```

---

## Key references

- [scientific-planning.md](scientific-planning.md) — the design, authority model, and named-idea grounding
- [provenance-and-trust.md](provenance-and-trust.md) — the claims ledger, runtime provenance, and the canonical artifact/authority table
- [overview.md](overview.md) — data architecture and table descriptions
- [pitfalls.md](pitfalls.md) — common query issues and solutions
- [performance.md](performance.md) — query strategies for large tables
- [research_ideas.md](research_ideas.md) — backlog of research questions
