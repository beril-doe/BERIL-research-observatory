---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-10-06
project: annotation_coordinate_atlas
---

# Review: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Summary

This is an eighth-round review of a project that has already absorbed seven prior cycles, each
finding and closing a real (if monotonically shrinking) defect. I independently re-verified
`REVIEW_7.md`'s one substantive finding — that `REPORT.md`/`SCOREBOARD.md`/`claims.json` quoted
lenient precision as `56/59 = 94.9%` when the notebook, data, and figure all said `55/59 = 93.2%`
— and the fix holds: `REPORT.md` now says "lenient 93.2%" everywhere it appears (Finding 4 prose,
the H2 hypothesis table, the Claims section), `SCOREBOARD.md`'s H2 row reads `55/59 = 93.2%`, and
`claims.json`'s `report_hash` (`f237c169...`) matches a fresh `sha256sum` of `REPORT.md` exactly,
confirming the ledger was rebuilt against the corrected text. I additionally re-derived the figure
from first principles directly against `data/audit_precision.csv` rather than trusting any prose:
the 100-row precision stratum tallies `correct=51, wrong_cardinality=4, wrong_label=4,
sentinel_only=2, vacuous=17, no_pattern=15, no_data=7`, giving judgeable `n = 51+4+4 = 59`, strict
`51/59 = 86.44%`, and lenient `(51+4)/59 = 93.22%` — both match the report to the decimal, with no
remaining trace of `56/59` or `94.9%` in any of `README.md`, `REPORT.md`, `SCOREBOARD.md`, or
`claims.json` (the string still appears, correctly, in three `WORKLOG.md` entries that record the
project's own history of getting it wrong and then right, which is the appropriate place for it to
live). `data/nb03_summary.json` and `data/nb04_summary.json` agree with every headline figure in
`REPORT.md` and `SCOREBOARD.md` to the decimal (recall 32.3%/30.0%, census `found_by_specific_label
37` / `generic_only 13` / `missed 1`, multidomain `6167/6530` protein-level vs `6578/6963`
pair-level, `395` repeat-carrying proteins, gap median −392 / IQR [−412,−371], BGC contig overlap
`28,494/28,494`, `13.9` genes/BGC inside vs `754,313` pairs at the ±5kb flank, collocation
`5 direct / 5 protein-only / 3 blocked-or-impossible` of 18). The 28 chain-produced artifacts
(`notebooks/*.ipynb`, `data/*.csv`, `data/*.json`, `figures/*.png`) still cluster in the single
2026-10-06 21:33–21:43 execution window with no stragglers. The README's Reproducibility section
has also been sharpened since `REVIEW_7.md`: it now states precisely, with measured numbers, that
the seed fixes which *columns* are audited but not which *values* within them, and quotes the
observed ±1.7-point run-to-run range on lenient precision (93.2%–94.9% across five full-chain
re-runs) rather than overclaiming reproducibility. **I found no new substantive defect this
round.** Eight rounds in, this project's self-correction loop has converged: the project is ready
for `submit`.

## Methodology

Unchanged from all seven prior rounds' assessment, which remains accurate. Q1 (the census) is
correctly treated as enumeration rather than hypothesis; Q2 (SemCat as a discovery instrument)
carries four falsifiable, pre-registered, competing hypotheses (H0/H1/H2/H3) with explicit
decision thresholds fixed before the audit ran. The NB01→NB02 ordering is genuinely non-circular:
`data/semcat_candidates.csv` is written and frozen before `02_ground_truth_sweep.ipynb` ever
executes, so the SemCat-only answer cannot be contaminated by hindsight — I confirmed this again
by checking that NB01's own cell outputs make no reference to any NB02 artifact. `beril.yaml`
records `plan_approval.via: agent-relayed` — the agent recorded an in-conversation approval rather
than the CLI witnessing a terminal `beril approve`; as in all seven prior reviews, this is
disclosed provenance for a reader weighing the pre-registration claim, not itself a fault. No
`plan_deviations.jsonl` is present in the project directory. The one disclosed plan revision
(`RESEARCH_PLAN.md` Revision History v2: the 12→60 value re-sample and the two-way→four-way
adjudication taxonomy change) remains candidly argued as non-material, and is consistent with what
`data/audit_precision.csv`'s seven-category tally actually shows.

Someone could reproduce this: the README gives exact run order, timeout, environment
prerequisites, and the on-cluster-only tooling constraint (`q.py` vs. the off-cluster `run_sql.py`,
recorded in `memories/pitfalls.md`). The one honest gap — value-level non-determinism in the audit
sample — is now disclosed quantitatively rather than glossed over.

## Code Quality

The `src/` split (`semcat.py`, `census.py`, `validators.py`) continues to do real work, and I spot
checked `04_bgc_region_joinability.ipynb` cell 15/20 directly: the protein-level, one-vote
domain-order statistic (`REVIEW_6.md`'s fix) is implemented as described, and `nb04_summary.json`'s
`multidomain_protein_b_then_a: 6167` / `multidomain_proteins_with_repeats: 395` match the report
exactly. No pitfall from `docs/pitfalls.md` or the project's own `memories/pitfalls.md` appears
unaddressed — the project's pitfalls file has itself grown to document four SemCat traps, two
tooling/Python traps, and two of its own reproducibility bugs (mixed-snapshot desync; SemCat's
rapid regeneration), each with a cheap detection command. I checked the newest of the eight
pitfalls entries (`float('nan')` defeating an `is not None` guard, from SemCat 0.24.2's bounds
format change) against `src/validators.py` informally and found the NaN-normalization pattern it
describes present at the coercion boundary, consistent with the pitfall being fixed rather than
merely logged.

## Evaluation Integrity

This remains descriptive/instrument-evaluation work with no fitted model, so train/test leakage
and baseline selection (`EVALUATION_INTEGRITY.md` items 3–4) are correctly not forced into the
write-up, as in all seven prior reviews. The two checks worth naming:

- **Selection bias / scope (item 1 analogue) — the "Scope of the SemCat verdict" and "Scope of the
  Claim" sections remain careful.** They state plainly that only 5 of SemCat's 25 tables and no
  CLI retrieval path were tested, that the grade covers 636 of its 2,509 indexed tables (readable
  tenants only), and that the census itself is a 34% slice (826 of ~2,509+ tables). Both headings
  stay scoped in their own text — "Only 5 of 17 coordinate-bearing region tables can be joined...",
  "SemCat is high-precision and low-recall (H2), on the subset tested" — rather than generalizing
  to "SemCat" or "BERDL" unqualified, which is the exact failure mode item 6 warns about and which
  six of the seven prior reviews already checked for without finding it.
- **Metric-reporting integrity — re-verified independently, not just re-read.** I rebuilt the
  precision/recall arithmetic from `data/audit_precision.csv` row-by-row (tally above) rather than
  trusting any document's restatement of it, and it reproduces `REPORT.md`'s 86.4%/93.2% to five
  significant figures. This is the exact check that caught the `56/59` error in `REVIEW_7.md`; this
  round it confirms the fix rather than finding a new instance.
- **Pseudo-replication:** both corrections the plan pre-registered (per-`schema_sig` dedup for the
  SemCat audit; the `REVIEW_6`-added per-protein dedup for the domain-order statistic) remain
  implemented and both are confirmed immaterial by the numbers (30.0%→32.3% recall; 94.5%→94.4%
  domain order) — consistent with every prior round's reading.

No train/test leakage, baseline-selection, or biology-specific failure mode (items 3–10) applies
beyond the above — this is a catalog/instrument audit, and the one biological plausibility check
(13.9 genes/BGC; the ABC-transporter N/C-terminal architecture) continues to be used correctly, as
corroboration of a join rather than as the headline claim itself.

## Findings Assessment

Conclusions are supported by the numbers in the cell outputs, not just the prose — I checked this
directly rather than assuming it, tracing `nb03_summary.json` and `nb04_summary.json` against
`REPORT.md`/`SCOREBOARD.md` line by line and finding full agreement (see Summary). Limitations are
unusually well acknowledged: the report states that recall may be a lower bound (the ground-truth
regex itself missed `kbase.content.c_<genome>_features`), that the confusion-matrix cross-check is
biased against SemCat and should not be quoted as a precision estimate, that the audit's judgeable
sample (59 columns) carries a binomial CI whose lower bound sits near the 0.80 decision threshold,
and that the value sample is not bit-reproducible with the observed effect size stated. `### What
Would Have Changed Our Mind` gives the pre-registered refutation routes for both the headline
use-case finding (an empty contig-id intersection, which did not occur) and H1 (either refutation
route would have sufficed; both failed), plus a result that argues against the census's own
completeness (the packed-JSON table found by accident). Nothing is left as "to be filled" — both
figures exist, are referenced by notebook and cell, and match their described content.

Discoveries and Performance Notes are each tied to a specific notebook/figure/data file rather than
floated as free-standing claims, and none reads as speculative or redundant with another project's
`memories/pitfalls.md` (checked: `euk_in_prok_correlates` and `pathway_based_hygiene` are the only
other projects with a non-empty pitfalls file in this repository, and neither overlaps SemCat,
BERDL coordinate systems, or this project's tooling notes).

## Suggestions

1. **(Optional, carried over from `REVIEW_5`/`REVIEW_6`/`REVIEW_7`, still open, lowest priority)**
   `REPORT.md`'s "Five corrections made during analysis" section has not been extended to a sixth,
   seventh, and eighth entry for the `REVIEW_6` (pseudo-replication) and `REVIEW_7` (lenient
   precision + its root cause) fixes, even though both are substantial enough to match the existing
   five in kind. They are currently recoverable only from `WORKLOG.md` and the Limitations bullet
   on value-sample non-determinism. This is purely a presentation nit — the content is not missing,
   only its placement — and has now been raised by three consecutive reviews without action,
   which suggests it is a deliberate choice rather than an oversight; if so, it would be worth a
   one-line note in `REPORT.md` saying so, so a ninth reviewer does not raise it a fourth time.
2. **(Optional, carried over from `REVIEW_3`/`REVIEW_7`, still open)** `beril.yaml`'s
   `artifacts.review` remains `false` despite eight `REVIEW_N.md` files now existing. Almost
   certainly intentional (set by the `submit` skill on approval, not by review), but worth a final
   confirmation before this project leaves the review stage, since it is the one field in
   `beril.yaml` that visibly disagrees with the state of the project directory.
3. **(Not a project defect, a process observation)** Eight review rounds against a project whose
   last four rounds found, respectively, one denominator error, three prose/number drifts, one
   immaterial statistical refinement, and one real-but-non-verdict-moving numeric error, suggest
   this specific chain has reached the point of diminishing returns for *this kind* of review. The
   remaining open items above are cosmetic. If another round is wanted, it would likely be more
   productive aimed at a dimension not yet exercised by rounds 1–8 — e.g., actually attempting the
   `semcat resolve`/`semcat joins` CLI paths that Future Direction 2 names as untested, or
   independently re-deriving the `kescience.fitnessbrowser` cross-frame claim from raw values —
   rather than a ninth pass over the same reconciliation checks this review and `REVIEW_1`–`7`
   have now run to convergence.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-10-06
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, WORKLOG.md, SCOREBOARD.md, REVIEW_1.md–REVIEW_7.md, claims.json, beril.yaml, runtime.json, requirements.txt, references.md, q.py, 4 notebooks (cell source for 01–04 and direct cell-output inspection for 03 cell 8/10/17–18 and 04 cell 15/20), 3 `src/` modules, all data files including direct row-level recomputation of `data/audit_precision.csv`'s precision/recall arithmetic, both figures (existence and naming checked), project `memories/pitfalls.md`, repository `docs/pitfalls.md`, other projects' `memories/pitfalls.md` (`euk_in_prok_correlates`, `pathway_based_hygiene` — no cross-project overlap found), file mtimes and `sha256sum REPORT.md` vs. `claims.json`'s `report_hash` cross-check
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive assessment.

<!-- report_hash: sha256:f237c16905377953b5aef479ea0c7a0fd23d6331f724d41ec5a83d8f15917084 -->
