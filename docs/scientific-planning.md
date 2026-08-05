# Scientific Planning & Execution

**Purpose**: Companion guide to the planning ⇄ execution workflow — what each
construct is for, how authority is divided, and the scientific ideas the design
is grounded in. For step-by-step usage see [workflow.md](workflow.md).

This layer adds the **front of the research arc** — a way to *form, rank, and
sustain a line of inquiry* — to complement the existing retrospective trust and
review tooling at the back.

---

## The three-stage arc

A line of inquiry moves through three composable workflows over one shared
substrate:

```
/research-plan  ──►  /execute-plan  ──►  /berdl-review · /submit
   PLAN                 EXECUTE             REVIEW / SUBMIT (existing)
```

| Stage | Skill | Owns lifecycle | What it produces |
|---|---|---|---|
| **Plan** | `/research-plan` | `exploration → proposed` | A frozen, pre-registered `RESEARCH_PLAN.md`: a sharp question, competing hypotheses, a falsification test and decision criterion per hypothesis, a discrimination strategy, a feasibility verdict, and a per-notebook analysis spec. |
| **Execute** | `/execute-plan` | `proposed → active → analysis` | Reads the *frozen* plan, builds and runs the notebooks (the discriminating query first), then `/synthesize` → `REPORT.md`. |
| **Review / Submit** | `/berdl-review`, `/submit` | `analysis → reviewed → complete` | The existing back of the arc — independent review, then ORCID-gated approval and archival. |

`/berdl_start` keeps onboarding and the 3-door menu and now acts as a **router**:
it delegates planning to `/research-plan` and execution to `/execute-plan`, and
routes a resumed project to the right stage by `beril.yaml.status`.

**The plan is a contract, frozen before results are seen.** This is
pre-registration: predictions and disconfirming checks are committed *before* the
analysis runs. Execution may revise the plan, but a *material* change (dropping or
adding a hypothesis, moving a decision threshold, abandoning the discrimination
strategy) demotes `active → proposed` and re-triggers the plan-review checkpoint.
Minor deviations are logged inline and execution continues.

---

## Authority: what gates, and what never does

Three files carry state, with strictly separated roles. The canonical artifact
table lives in
[provenance-and-trust.md](provenance-and-trust.md#where-each-artifact-lives); this
section states the rules it encodes.

- **`beril.yaml` is the sole authority.** The ORCID `/submit` approval is the one
  hard gate that rides on it; the plan-approval block below is a witness on the
  same file.
- **`claims.json` is generated and advisory.** It never blocks — `/submit` only
  ever `WARN`s on a flagged claim.
- **`runtime.json` is non-authoritative** passive session history; nothing reads
  it to make a decision.

**Computed signals render as words, never fabricated numbers.** Progress is
described qualitatively; the only numbers ever displayed are real ones — counts
and statistics the notebooks actually produced, or a `claims.json` tally when that
file exists.

### The plan-approval witness

The plan-review checkpoint used to leave **no witness**. A plan the agent had just
written and a plan a human had approved were byte-identical on disk, so
`/execute-plan`'s instruction to "verify the user approved" had no referent.

The witness is a **hash, never a status**. `uv run beril approve <id>` records a
`plan_approval` block (ORCID, timestamp, `via`, `plan_hash`) in `beril.yaml`:
`via: terminal` when the human answered the prompt at a terminal, `via: agent-relayed`
when the human approved in conversation and the agent recorded it with `--relayed`.
`status` is never read: an agent writing `status: active` records nothing. Without a
TTY and without `--relayed` the command refuses, but that check was never the
boundary: a pty defeats it and the resulting block is
byte-indistinguishable from a human's. The real control is that `beril.yaml` is
reviewed — the approval lands in the PR diff beside the plan it names, `via`
included. The checkpoint
stays mandatory as process: `/execute-plan` is instructed not to start without an
approval on disk, and nothing enforces that but the agent following the instruction.

`plan_digest` hashes the plan **above the `## Revision History` heading** (the
whole file when that heading is absent). This preserves the minor/material
distinction the workflow already draws: appending a minor-deviation line to
Revision History must not invalidate the approval, but editing a hypothesis, a
decision threshold, or the discrimination strategy — all of which live above that
heading — must. It is deliberately **not** `tools/review.sh`'s whole-file
`plan_hash`, which anchors a review artifact to an exact file and so has to change
on any byte.

**The hook records; it does not block.** The `PreToolUse` hook
`.claude/hooks/plan-gate.py` lets the write through — it always exits 0 and emits no
permission decision — and appends a record to `projects/<id>/plan_deviations.jsonl`
when analysis code is written under a plan with no matching approval. That record
surfaces at review and submit time; both readers are advisory and neither blocks.
Exploration and light analysis must stay supported, and pre-registration integrity
does not require that violating the plan be impossible — only that it be
undeniable. What changes is the *evidence*: a skipped checkpoint is no longer a
silent omission indistinguishable from approval, but a dated record in the project
and in git history.

---

## The constructs and how they fit

| Construct | What it is | Where it lives |
|---|---|---|
| **`/research-plan`** | User-invocable PLAN skill. Frames the question, drafts genuine competing hypotheses *before* asking your preference, attaches a falsification test + decision criterion to each, writes the discrimination strategy, runs a cheap feasibility probe, and freezes `RESEARCH_PLAN.md`. | `.claude/skills/research-plan/` |
| **`/execute-plan`** | User-invocable EXECUTE skill. Reads the frozen plan, runs each notebook's discriminating/refuting query first, and hands off to review. | `.claude/skills/execute-plan/` |
| **Plan-approval witness** | `beril approve` writes the `plan_approval` block, stamping `via: terminal` (prompted at a TTY) or `via: agent-relayed` (`--relayed`, for an approval the user gave in conversation) — provenance, not a gate, since a pty defeats the TTY check anyway (see above); the `PreToolUse` hook records a deviation when analysis code is written under a plan whose digest does not match, and never refuses the write. Stdlib-only and Python 3.9-safe, because the harness runs it with the system interpreter, not the venv. | `beril_cli/approve_cmd.py`, `.claude/hooks/plan-gate.py` |
| **hypothesis-critic** | Read-only subagent invoked at the plan-review checkpoint (also via `/critique-hypotheses`). Asks: are the rivals genuine or strawmen? is there a discrimination strategy? does each hypothesis have a falsification test + decision criterion? is the question answerable given feasibility? It critiques and writes nothing — the **pre-analysis** complement to the post-analysis `/berdl-refute`. | `.claude/agents/hypothesis-critic.md` |
| **Plan reviewer** | `tools/review.sh --type plan` uses `PLAN_REVIEW_PROMPT.md`, which now includes a *Multiple Working Hypotheses & Falsifiability* item that lints single-hypothesis plans and any hypothesis without a stated falsification test or decision criterion. | `.claude/reviewer/PLAN_REVIEW_PROMPT.md` |

---

## Named-idea grounding

The design is a deliberate application of long-standing ideas about how inquiry
should be structured. Each idea lands on a specific construct.

| Idea | What it asks of a plan | Where it lands |
|---|---|---|
| **Chamberlin (1890) — multiple working hypotheses** | Hold several rival explanations at once; don't fall in love with one. | The Competing Hypotheses block; hypothesis-critic; the new PLAN_REVIEW item. |
| **Platt (1964) — strong inference** | Design the *crucial experiment* that excludes alternatives, and run it first. | The discrimination strategy; "discriminating/refuting query first" in `/execute-plan`. |
| **Popper / Lakatos — falsification** | A claim that nothing could refute is not science; state the disconfirming test. | The per-hypothesis falsification test; the PLAN_REVIEW "not yet testable" lint. |
| **Mayo — severe testing** | A hypothesis earns credence only by surviving a test that *could* have caught it failing; *unfalsified ≠ severely tested*. | The pre-registered decision rule; hypothesis-critic's posture. |
| **FINER / PICO — question quality** | Make the question Feasible, Interesting, Novel, Ethical, Relevant; state problem / comparator / outcome. | Research-question framing; the feasibility verdict. |

### Why "survival of a disconfirming check," not persuasion

Recent agentic research systems (e.g. Google's AI co-scientist, Sakana's
approaches) often rank hypotheses by **debate or persuasiveness** — which argument
wins. This design deliberately ranks by a different criterion: **whether a
hypothesis survives a check that was designed to disconfirm it.** A persuasive
hypothesis that no one tried to refute has earned nothing; a hypothesis that
withstood its own falsification test has. That is why the plan must name, *in
advance*, the result that would prove it wrong — and why execution runs the
disconfirming query before the confirmatory cells.
