---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-10-06
project: annotation_coordinate_atlas
---

# Review: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Summary

This is a seventh-round review of a project that has already absorbed six prior review cycles,
each finding and fixing a real (if progressively smaller) defect — mostly instances of the same
"a cached or re-run value silently drifted from the prose" bug class the project itself names and
tracks in `memories/pitfalls.md`. I re-derived every headline figure in `REPORT.md` independently
from the four `data/nb0{1,2,3,4}_summary.json` files, the raw audit CSVs, the notebooks' own saved
cell outputs, and both figures, rather than trusting the prose, and found **one new instance of
that exact bug class, missed by all six prior rounds**: `REPORT.md` (three places), `SCOREBOARD.md`
(one place), and `claims.json` (one place, inside a field that is supposed to be a verbatim quote)
all state SemCat's **lenient** precision as **56/59 = 94.9%**. The string `56/59` and `94.9` do not
appear anywhere in `notebooks/03_semcat_grade.ipynb`; the notebook's own printed output, the raw
`data/audit_precision.csv` (`wrong_cardinality: 4`, not 5), `data/nb03_summary.json`
(`audited_precision_lenient: 0.9322033898305084`), and the rendered figure's own title
(`figures/semcat_precision_recall.png`, right panel: "lenient 93%") all independently agree on
**55/59 = 93.2%**. `WORKLOG.md` shows this is not a typo but a genuine drift: its `REVIEW_2` entry
records "lenient 94.9%" as the figure current at that point in the project's six-round history, and
nothing in the five subsequent re-runs (each of which re-executed the whole live-data chain,
including the un-ordered `LIMIT` value sample that feeds this exact figure) updated the prose to
match the number the final run actually produced. This does not change the H2 verdict — the
decision rule is keyed to **strict** precision (86.4%, correctly reported everywhere), not
lenient — but it is a real, multiply-corroborated numeric error in the primary deliverable, and I
traced a plausible root cause below that is itself worth fixing. Apart from this, the project
remains in excellent shape: the census (51 tables), the joinability assessment (5 of 17 direct),
the BGC demonstration (100% contig overlap, 13.9 genes/BGC), the multi-domain protein-level
dedup fix from `REVIEW_6`, and the coverage/row-count figures all reproduce to the decimal against
their source artifacts.

## Methodology

Unchanged from prior rounds' assessment, which remains accurate: Q1 (the census) is correctly
treated as enumeration, and Q2 (SemCat as a discovery instrument) carries four falsifiable,
pre-registered, competing hypotheses with a non-circular NB01→NB02 ordering (`semcat_candidates.csv`
is written before `02_ground_truth_sweep.ipynb` ever runs, so the SemCat-only answer cannot be
contaminated by hindsight). `beril.yaml` records `plan_approval.via: agent-relayed` — the agent
recorded an in-conversation approval rather than the CLI witnessing a terminal `beril approve`; as
in all six prior reviews, this is disclosed provenance for a reader weighing the pre-registration
claim, not itself a fault. No `plan_deviations.jsonl` is present in the project directory. The one
disclosed plan revision (`RESEARCH_PLAN.md` v2: the 12→60 value re-sample and the
two-way→four-way adjudication taxonomy change) is candidly argued as non-material in both the plan
and `REPORT.md`'s "Five corrections" section.

The README's reproduction section states the audit sample is "seeded (`SEED = 20261002`) and
reproducible." That is accurate for **which 200 columns** are drawn into the audit (a stratified
sample over a seeded random state), but it does not extend to **which values within each column**
get adjudicated — see Code Quality below, where I trace this to the probable cause of the
precision drift documented in Summary.

## Code Quality

The `src/` split (`semcat.py`, `census.py`, `validators.py`) continues to do real work, and the
four-way adjudication taxonomy (`correct` / `wrong_cardinality` / `wrong_label` / `sentinel_only`)
is implemented consistently between `validators.py` and the figure.

**New this round: the value-sampling query that drives the precision audit has no `ORDER BY`, so
repeated full-chain re-runs are not guaranteed to adjudicate the same values.**
`03_semcat_grade.ipynb` cell 8:

```python
def sample_values(fq, col, n=60):
    rs = spark.sql(f'SELECT `{col}` AS v FROM {fq} WHERE `{col}` IS NOT NULL LIMIT {n}').collect()
    return [r["v"] for r in rs]
```

`Performance Notes` in `REPORT.md` recommends exactly this pattern ("`SELECT col ... WHERE col IS
NOT NULL LIMIT n` — limit pushdown, no shuffle") for cost reasons, correctly. But an unordered
`LIMIT` over a Spark/Iceberg table has no row-order guarantee across separate query executions —
task completion order and file-read order can vary run to run, especially on a multi-file Iceberg
table. For a column whose values are a genuine mix of correctly- and incorrectly-shaped entries —
exactly the borderline case the audit exists to catch, e.g.
`refdata.tcdb.acc_to_tcid.uniprot_accession` ("41/60 values are not a UniProt accession", implying
19/60 *are*) — a different 60-row sample on a different run can plausibly cross whatever threshold
`validators.py` uses to call the column `correct` vs `wrong_cardinality` vs `wrong_label`. This is
a credible mechanism for exactly the drift documented in Summary (`wrong_cardinality` 5→4,
`wrong_label` 3→4 between the run `WORKLOG.md`'s `REVIEW_2` entry describes and the final saved
run), and it means the audit's **value-level** reproducibility claim is narrower than the README's
"seeded and reproducible" line implies — the column *selection* is seeded; the per-column value
*sample* is not.

## Evaluation Integrity

This remains descriptive/instrument-evaluation work with no fitted model, so train/test leakage
and baseline selection (`EVALUATION_INTEGRITY.md` items 3–4) are correctly not forced into the
write-up, consistent with all six prior reviews.

- **Metric-reporting integrity (item 2 analogue): a reported sub-metric does not match the
  artifact it cites.** `REPORT.md` line 140 ("lenient 94.9%"), line 146 (the H2 hypothesis-table
  row, "94.9% lenient"), and line 234 (the Claims section, "lenient 56/59 = 94.9%") all disagree
  with `03_semcat_grade.ipynb`'s own printed output ("PRECISION, lenient : 55/59 = 93.2%", cell 10
  and again in cell 17's `schema_sig` dedup pass), `data/nb03_summary.json`
  (`audited_precision_lenient: 0.9322033898305084`), `data/audit_precision.csv`
  (`wrong_cardinality` Counter = 4, not 5), and the rendered
  `figures/semcat_precision_recall.png` (right-panel title literally reads "lenient 93%"). I
  confirmed by direct grep that the strings `56/59` and `94.9` appear **nowhere** in the notebook
  file, while `55/59` (×3) and `93.2` (×7) do. `SCOREBOARD.md` line 12 and `claims.json` line 149
  carry the same stale figure — the latter inside the claim's `supports[].exact` field, which by
  the convention used for every other claim in this ledger (I spot-checked several and they are
  verbatim notebook-output substrings) is supposed to be a literal, independently-verifiable quote
  from the source. Here it is not findable in the source at all. **Non-material to the verdict**:
  the pre-registered decision rule (`03_semcat_grade.ipynb` cell 18, `h2_s = (recall < 0.50) and
  (precision_strict >= 0.80)`) is keyed to **strict** precision, which is correctly 86.4%
  everywhere it appears. But "holds under both adjudication policies," stated in `REPORT.md`'s
  Finding 4 table, is evaluated against the wrong lenient number, and a reader who re-derives the
  binomial interval on "56/59" rather than the real "55/59" is working from a figure that is not
  reproducible from the repository as shipped.
- **Pseudo-replication / dedup (item 5 analogue):** `REVIEW_6`'s fix (protein-level, one-vote
  dedup for the domain-order statistic, `395 proteins (6%) carry repeat copies`) is present,
  correct, and matches `nb04_summary.json` (`multidomain_protein_b_then_a: 6167`,
  `multidomain_proteins_with_repeats: 395`) exactly. The `schema_sig` dedup for the SemCat audit
  remains correctly implemented (`recall_sig` 32.3% vs per-column 30.0%; precision unaffected,
  0 clones in that sample).
- **Selection bias / scope (item 1):** unchanged from prior rounds' correct assessment — "Scope of
  the SemCat verdict" and "Scope of the Claim" remain careful and are not generalized past the
  tested slice.
- No train/test leakage, baseline-selection, or biology-specific failure mode (items 3–10) applies
  here beyond the points above — this is a catalog/instrument audit, and the one place a biological
  check is invoked (13.9 genes/BGC; the ABC-transporter N/C-terminal architecture) is used
  correctly, as corroboration rather than as the primary claim.

## Findings Assessment

Every other headline number I independently re-derived from the four summary JSONs, the raw CSVs,
and the notebooks' own printed outputs agrees with `REPORT.md`/`SCOREBOARD.md` to the decimal:
census 51 entries (24 coordinate-bearing: 15 nucleotide / 5 amino-acid / 4 multiple-frame);
collocation 5 direct / 5 protein-space-only / 2 blocked / 1 impossible of 18 tables assessed, 17
coordinate-bearing; BGC contig overlap 28,494/28,494 = 100%; 754,313 gene–BGC pairs at a ±5,000 bp
flank (21.3/BGC) vs 13.9 genes/BGC strictly inside; multi-domain order 6,167/6,530 proteins = 94.4%
(395 repeat-carrying proteins, 6%); SemCat **strict** precision 51/59 = 86.4%; recall 32.3%/30.0%;
`row_count` 59/60 = 98.3%; table coverage 80.3% (5 stale, 163 missing); 493 candidate tables in
unreadable tenants. The only figure that does not reproduce from the shipped artifacts is the
lenient precision figure documented above. The "Scope of the SemCat verdict," "Scope of the
Claim," "What Would Have Changed Our Mind," and "Five corrections" sections remain the strongest
parts of the write-up and are unaffected by this finding. Row counts, file counts, and timestamps
across the repository (`sha256sum REPORT.md` matches `claims.json`'s `report_hash`; all 28
chain-produced files cluster in the single 21:33–21:44 window on 2026-10-06; `RESEARCH_PLAN.md` and
`beril.yaml` predate the run, as a frozen plan should) show no other desynchronization of the kind
`REVIEW_1`–`REVIEW_3` previously caught.

## Suggestions

1. **(Should-fix, low effort)** Correct the lenient-precision figure from `56/59 = 94.9%` to
   `55/59 = 93.2%` in `REPORT.md` (Finding 4 prose, the H2 table row, and the Claims section's
   `exact` quote), `SCOREBOARD.md`'s H2 row, and `claims.json`'s corresponding `supports[].exact`
   field, then rebuild the claims ledger so `report_hash` is re-pinned. This is the figure the
   repository's own notebook, data, and figure already agree on — no re-computation needed, only
   the prose needs to catch up to the artifact, as in five of the six prior review rounds.
2. **(Worth considering)** Add an explicit, deterministic ordering to the value-sampling query in
   `03_semcat_grade.ipynb` cell 8 (e.g. `ORDER BY hash(<some stable row key>)` with the existing
   seed, or any deterministic tie-break) so that re-running the full chain samples the same 60
   values per audited column every time, not just the same 200 columns. As written, an unordered
   `LIMIT` on a multi-file Iceberg table is not guaranteed stable across executions, which is a
   plausible mechanism for the precision drift this review found and is a gap in the "seeded and
   reproducible" claim in the README's Reproduction section — worth a line there, or a new entry in
   `memories/pitfalls.md` alongside the project's other hard-won reproducibility lessons (this is
   the same family as the "re-running one notebook silently desynchronises the rest" pitfall
   already recorded there, one level deeper: even re-running the *same* notebook does not
   guarantee the *same* adjudicated sample).
3. **(Optional, carried over from `REVIEW_5`/`REVIEW_6`, still open)** `REPORT.md`'s "Five
   corrections" section has not been extended to include the `REVIEW_4`–`REVIEW_6` fixes as
   sixth/seventh/eighth entries, for consistency with how the first several review-driven fixes
   were each logged there. This review's finding would be a natural ninth entry if that pattern is
   resumed.
4. **(Optional, carried over from `REVIEW_3`, still open)** `beril.yaml`'s `artifacts.review` is
   still `false` despite seven `REVIEW_N.md` files now existing; confirm this is intentionally set
   by the `submit` skill rather than something review itself should update.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-10-06
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, WORKLOG.md, SCOREBOARD.md, REVIEW_1.md–REVIEW_6.md, claims.json, beril.yaml, runtime.json, requirements.txt, references.md, q.py, 4 notebooks (cell source and saved outputs inspected directly, including raw grep verification against claimed figures), 3 `src/` modules, all 25 data files (including direct inspection of `data/audit_precision.csv` and all four `data/nb0{1,2,3,4}_summary.json`), 2 figures (opened and visually inspected), project `memories/pitfalls.md`, repository `docs/pitfalls.md`, other projects' `memories/pitfalls.md` (no cross-project overlap found), `.claude/reviewer/EVALUATION_INTEGRITY.md`, file mtimes and `sha256sum`/`report_hash` cross-check
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive assessment.

<!-- report_hash: sha256:40ddffe5dfa4ccfbf20dddede4359707e9995e8d4bc868ff5033a0b7a1262c9f -->
