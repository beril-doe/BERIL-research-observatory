---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-10-23
project: annotation_coordinate_atlas
---

# Review: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Summary

This is the sixteenth review of this project, and it follows a substantive post-approval
correction, not a cosmetic one. The project was approved and archived on 2026-10-16
(`beril.yaml`'s `previous_approvals` entry), then demoted back to `analysis` on 2026-10-23 after
a pre-publication audit and a Copilot code review found that NB04's headline joinability
verdicts ("6 of 17 joinable") were a hand-typed list with only one join actually executed. The
author reran the full chain with joinability now derived from queried checks for all 23
coordinate-bearing tables, fixed three validators flagged by the second-opinion review, corrected
a misreading of SemCat's join layer (`verified_joins` vs `edges`), and re-executed all four
notebooks in order against a fresh SemCat snapshot. I independently re-derived the headline
numbers from the raw notebook cell outputs rather than trusting the prose: NB04 cell 23 does
produce a 23-row verdict table from query evidence (13 of 23 joinable, 9 of those verdicts
resting on judgement rather than a query, all marked as such), NB03 cells 10/17/18 reproduce the
quoted strict precision (45/56 = 80.4%, Wilson 0.682–0.887), lenient precision, and recall
(30/95 = 31.6%) exactly, and NB01 cells 2/5/21/22 reproduce the coordinate-conflation and
edges/verified-joins figures exactly. `sha256sum REPORT.md` matches `claims.json`'s
`report_hash`, and every file the chain writes carries the same 2026-10-22 run timestamp with no
stale intermediate — the project's own documented staleness check passes. This is careful,
well-instrumented work, and the self-caught correction (demoting a submitted project rather than
letting a hand-typed result stand) is itself a point in the project's favor. I found no new
critical or important issues; one previously-known gap (memory files not yet refreshed to match
the revision) is noted below but is expected housekeeping, not a defect in the current artifacts.

## Methodology

The two coupled questions (Q1 census, Q2 instrument grade) remain clearly stated, and the
ordering discipline that makes Q2 non-circular (NB01 freezes the SemCat-only answer before NB02
builds ground truth) is unchanged and still followed — NB01 and NB02 file mtimes both sit at
2026-10-22, in the documented order. `beril.yaml`'s `plan_approval.via: agent-relayed` — the
2026-10-02 approval was a conversational grant the agent recorded, not one a human typed at a
terminal; disclosed provenance, not a fault. No `plan_deviations.jsonl` is present. The
Reproduction section in README.md is specific and testable (exact wall times per notebook, the
deterministic value-sampling query, the "run all four, in order" rule with its own rationale),
and the project's self-authored chain-desync detection command (`ls -l` across notebooks/data/
figures) is itself documented as a pre-review habit — I ran it and it confirms a single clean run.

## Code Quality

`src/semcat.py`, `src/census.py`, and `src/validators.py` carry the three fixes recorded in
`WORKLOG.md`'s 2026-10-22 entries (anchored sibling-pattern matching, removal of four
unconstrained `r"."` validators, content-type-specific placeholder filtering). I did not re-audit
every regex, but the downstream effect (precision moving from the earlier 85.0% to 80.4%, in the
direction away from the more favorable prior figure) is consistent with a genuine fix rather than
a tuning-toward-a-preferred-verdict pass, and the Limitations section says plainly that the
validators were fixed *before* the run and not touched after seeing the two marginal failures
(`pdb_uniprot_mapping.pdb_end` = `'66A'`, `annotation_hierarchies_unified.term_id` = `'5.3.-.-'`).
That is the right order of operations and it is stated, not merely true by luck. The joinability
logic in NB04 §5 is now a stated rule (three query-backed routes — direct, self, bridged — plus
two non-query verdicts, protein-space-only and no-gene-table) applied uniformly and the verdict
table is written from `checks[r.fq]` dictionaries populated by the query cells above it, not typed
in; this directly closes the gap the pitfalls file now records ("a hand-typed verdict list is not
a result"). Known pitfalls specific to this project (string-typed coordinate columns, cluster
IDs being pangenome-scoped, SemCat's `coordinate` label conflating systems, `run_sql.py` being
off-cluster-only) are all reflected in the notebooks and in `src/`.

## Evaluation Integrity

No model or threshold is fit here — this is catalog census plus an instrument audit against a
hand-built ground truth, so train/test leakage and baseline-selection concerns
(`EVALUATION_INTEGRITY.md` items 3–4) do not apply, as every prior round also found.

- **Metric misuse / confidence calibration (item 2).** The stratified 200-column audit computes
  strict and lenient precision and recall with 95% Wilson intervals, and the report does not
  collapse a borderline interval into a confident headline: strict precision's interval
  (0.682–0.887) straddles the 0.80 H2/H3 boundary, and the report says exactly that ("the audit
  therefore does not separate H2 from H3 at 95% confidence") rather than reporting only the point
  estimate as a win for H2. The `strand` precision facet (n=1, 100%) and `strand` recall facet
  (n=14, the full in-frame population) are both flagged in Limitations as too small for a stable
  rate rather than quoted as settled. This is the correct response to small-n metric instability.
- **Selection bias / scope (item 6, database-ascertainment analogue).** `### Scope of the Claim`
  states the realized cohort precisely (840 of 864 listed tables read; 655 of those both read and
  indexed feed the SemCat grade; the BGC demonstration is 100% `soil`-biome because all 35,354
  `gene_bgc` rows are) and the Key Finding headings stay scoped ("4 of 14 region-annotation
  tables... all in kescience.mgnify") rather than generalizing to unqualified "BERDL" or
  "annotation tables." This is the item 6 failure mode caught on the author's side, as the
  reviewer brief asks to check for.
- **Audit sampling design.** The 100-precision/100-recall stratified sample draws from SemCat
  labels and from ground truth independently (NB03 cells 10/17), and the per-`schema_sig`
  deduplication (collapsing cloned staging-table columns to one observation) is implemented and
  quoted as the plan requires — this was itself a prior review finding (Correction 4) and remains
  correctly applied in this run (56 precision groups from 58 columns, 95 recall groups from 100
  columns).
- **claims.json.** 6 claims, 5 of resolved-artifact-support `multiple-streams`, 1 `single-stream`
  (the `pfam_annotation_gff` coordinate-system claim, which is a single exact-arithmetic identity
  test on 26,779 rows rather than a statistical inference — flagged by the project itself as
  single-stream, appropriately). One `confidence_mismatch` is flagged, on the SemCat
  precision/recall claim, because its `refutes` entry (the embeddings-retrieval scope caveat) is a
  prose scope note rather than a locally computed artifact and so resolves as `not-checked`
  rather than `resolved` — this is a tooling artifact of the claims checker, not a substantive gap;
  the claim's own confidence is already set to `medium`, which is the right level given the
  straddling interval.
- No biology-specific failure mode (`EVALUATION_INTEGRITY.md` items 5, 7–11) applies — this is a
  catalog/instrument audit, not a comparative-genomics claim.

## Findings Assessment

The headline joinability finding (13 of 23, 4 of 14 region tables) is now traceable end to end:
NB04 cell 23's printed crosstab and per-table table match REPORT.md's Finding 1 table exactly,
including which 9 verdicts rest on judgement rather than a query. Finding 2's named-query
demonstration (28,494/28,494 contig match, 13.9 genes/BGC inside, 754,313 pairs at ±5 kb) and
Finding 4's precision/recall figures both reproduce from notebook cell outputs I inspected
directly (NB03 cells 10, 17, 18; NB01 cells 2, 5, 21, 22), not just from the prose summary. The
report's `### What Would Have Changed the Conclusions` section gives the pre-registered
refutation (an empty contig intersection, which did not occur) and states plainly that one more
mislabelled `schema_sig` group in 56 would flip the point-estimate verdict from H2 to H3 — a
genuine pre-registered fragility disclosure, not a post-hoc hedge. Limitations are specific and
numerous (ground truth itself is a lower bound because of `kbase.content.c_<genome>_features`;
the full-frame confusion matrix is acknowledged as biased against SemCat and superseded by the
value-adjudicated audit; joinability has three stated limits). Nothing is left as "to be filled."
The Discoveries section's claims are each tied to a specific notebook result I was able to
locate (e.g., the `KEGG_Reaction`/`EC_Number`/`pfam` delimited-list examples appear verbatim in
NB03's `MULTI-VALUED` adjudication output), and the Performance Notes are concrete, reproducible
operational figures (wall times, sampling strategy, hash-bucket partitioning) rather than vague
claims.

One thing worth flagging for the record rather than as a defect: `memories/discoveries.md` and
`memories/performance.md` are extraction artifacts from the 2026-10-16 approval and still say
"only 6 of 17... satisfy the second" — the pre-correction joinability figure. This is expected:
those files are regenerated at approval time, and the project was demoted before a new approval
could refresh them. A reviewer or downstream project consulting `memories/discoveries.md` today
would get the superseded 6-of-17 figure rather than the corrected 13-of-23 one; this will resolve
itself automatically if/when this revision is approved, but is worth noting since it is exactly
the kind of staleness this project's own pitfalls file warns about in other contexts.

## Suggestions

1. **(Low priority, informational only)** When this revision is approved, confirm
   `memories/discoveries.md` and `memories/performance.md` are regenerated from the current
   REPORT.md rather than left as the 2026-10-16 extraction — they currently quote the superseded
   "6 of 17" joinability figure that this revision corrected to "13 of 23."
2. **(Unchanged, genuine, low priority)** Future Direction 2 — grading SemCat's
   `column_embeddings`/`edges`/CLI retrieval paths rather than literal `content_type` lookup —
   remains the single most consequential open question about whether the H2 verdict generalizes
   beyond literal label lookup. Correctly scoped as future work in the report, not a gap in the
   current analysis.
3. **(Trivial, optional)** Two figures cover four notebooks and five Key Findings; the census
   itself (Finding 3, 51 tables across coordinate systems) and the SemCat table-level
   found/missed/wrong breakdown (Finding 4's table-level paragraph) are reported only as prose
   and tables. A simple bar chart of the 51-table census by category, or of table-level
   found/missed/generic-only counts, would make Findings 3–4 as visually scannable as Findings 1
   and 2 already are. Not a reproducibility gap — the underlying CSVs exist — just an easy
   addition if another figure pass happens.

Given the scale of independent re-verification I was able to do against raw cell outputs (not
just prose) across all four notebooks, and that the one substantive issue this cycle addressed
(the hand-typed joinability list) was caught and fixed by the author's own process before I saw
it, I see no remaining technical obstacle to re-approval.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-10-23
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, WORKLOG.md, SCOREBOARD.md, claims.json,
  beril.yaml, runtime.json, memories/pitfalls.md, memories/discoveries.md, memories/performance.md,
  docs/pitfalls.md, requirements.txt, references.md, `src/semcat.py`, `src/census.py`,
  `src/validators.py`, all four notebooks (independently re-derived the headline figures for
  joinability, precision/recall, and coordinate-system conflation directly from raw cell
  `outputs`, not from REPORT.md's prose), all 26 files in `data/`, both files in `figures/`
  (existence and timestamp check), an independently recomputed `sha256sum REPORT.md` cross-checked
  against `claims.json`'s recorded `report_hash` (match), and a file-mtime staleness check across
  the full notebook/data/figures chain confirming a single consistent 2026-10-22 run.
  REVIEW_1.md through REVIEW_15.md were read for prior-finding context but their conclusions were
  independently re-verified against the current (post-2026-10-22-revision) artifacts rather than
  taken on trust.
- **Note**: This review was generated by an AI system. It should be treated as advisory input,
  not a definitive assessment.

<!-- report_hash: sha256:a4cfbd343cb232e2be8a4975ee6fc59f8bda6f3ccc2360c6605e5e1ba0403d13 -->
