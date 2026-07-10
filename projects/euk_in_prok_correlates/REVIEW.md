---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-07-10
project: euk_in_prok_correlates
---

# Review: Eukaryotic Contamination Correlates in Prokaryote-Targeted Metagenomes

## Summary
This project remains a well-executed, self-critical piece of work: it asks which sample-collection metadata
correlate with eukaryotic contamination in NMDC prokaryote-targeted metagenomes, and its central, honestly-framed
contribution — the apparent environment↔eukaryote association is confounded with study/batch (out-of-study
R²≈−0.30) but re-emerges as a genuine signal once batch is held constant within one study (within-study
R²=+0.17) — is unchanged and remains well supported. I confirmed via `git log`/`git show` that every issue raised
in `REVIEW_1.md` and `REVIEW_2.md` was fixed in commits `ddaeb255` and `12d46cdd`, and independently verified each
fix against the current notebooks, `REPORT.md`, and the regenerated `data/analysis_table.csv` (2,759 rows, 9
studies, matching the report throughout). This is a project that consistently responds to review rather than just
filing it. My own pass over the current state found one new, verifiable numeric inconsistency introduced as a
side effect of the REVIEW_2 fix (the null-`workflow_run_id` filter shifted the out-of-study R² from −0.34 to
−0.30, but two other locations still quote the old −0.34 figure) plus a couple of small stale/leftover items.
None of these undermine the project's headline confounding result or its within-study finding, which remain the
strongest and best-evidenced claims in the report.

## Methodology
The research question (which metadata factors correlate with eukaryotic fraction in prokaryote-targeted
metagenomes) is clearly stated and testable, and the H0/H1a/H1b/H1c structure maps directly onto the four
notebooks. `RESEARCH_PLAN.md`'s revision history documents two genuine mid-course corrections — switching the
response-variable source after discovering the Kraken2 reference DB is prokaryote-restricted, and adding the
within-study contrast (NB04) after `data/01_data_landscape.md` established that no on-system source can break the
~9-study confound — both backed by real feasibility/landscape scans (`data/00_feasibility_findings.md`,
`data/01_data_landscape.md`) rather than assertion.

Data sources are identified precisely down to table and BERDL collection (`RESEARCH_PLAN.md`'s Query Strategy
table, `REPORT.md`'s Data/Sources table). Reproducibility is good: the README's `## Reproduction` section gives an
ordered command sequence from the heavy Spark build step through notebook execution, states what's heavy/on-cluster
vs. frozen-CSV, lists expected outputs, and — since REVIEW_2 — now explicitly flags the documented
`jupyter nbconvert --inplace` output-loss pitfall and the workaround (`--output <name>_executed.ipynb`). This
closes the reproducibility gap raised in REVIEW_2.

## Code Quality
The four notebooks remain consistently organized (goal statement → setup → analysis → takeaways), use a shared
`DATA`/`FIG` path convention, and are backed by real, incremental commit history including the two review-fix
commits — not reconstructed after the fact.

**Verified fixes from REVIEW_1 (commit `ddaeb255`) — still correctly in place:**
1. NB02 cell 7 excludes the `Unknown`/missing-metadata bucket from the `ecosystem_type` Kruskal-Wallis test
   (`top=[t for t in df['ecosystem_type'].value_counts().index if t!='Unknown'][:8]`); the resulting statistic
   (H=77.8, p=1.3×10⁻¹⁷) is correctly reported in REPORT.md as identical to, not an independent confirmation of,
   the matrix-level test.
2. The dead `res['study_only_group']=...` placeholder line is gone from NB03 cell 5.
3. REPORT.md's Limitations retains the "Pooled-run metadata" entry on the `MIN(biosample_id)` representative-
   biosample choice.

**Verified fixes from REVIEW_2 (commit `12d46cdd`) — still correctly in place:**
1. The depth correlation (Spearman ρ=−0.29) is now inside Finding 3 (the confounded cross-study section), with
   explicit language that it is "not batch-controlled" and "read as suggestive only" — no longer implied to be
   part of the batch-controlled Finding 4 narrative.
2. README's Reproduction section now names the `--inplace`-drops-outputs pitfall and its workaround.
3. `src/build_analysis_table.py`'s gottcha/kraken/centrifuge CTEs now all filter `workflow_run_id IS NOT NULL`;
   I confirmed `data/analysis_table.csv` has exactly 2,759 rows across 9 distinct `study_id` values, matching
   REPORT.md and NB01/NB03/NB04 output throughout — the previous 2,760-vs-2,759 / 9-vs-10-studies discrepancy is
   resolved in the data and in REPORT.md's prose.
4. `data/euk_fraction_per_file.csv` (the superseded v1 artifact) is **still present and still unreferenced** by
   any current script or document — this nice-to-have cleanup was not applied (low priority, unchanged from
   REVIEW_2 suggestion 4; not re-raised as a new numbered suggestion below since it is unaltered from prior review).

**New issue found in this pass:**

1. **Stale out-of-study R² figure in two locations, inconsistent with the current data and REPORT.md.**
   `README.md` line 18 ("...does not generalize across studies (out-of-study R²=−0.34)...") and
   `notebooks/04_within_study.ipynb` cell 9's print string ("`Contrast with cross-study out-of-study R^2 = -0.34
   (NB03).`") both quote **−0.34**. The actual, current NB03 output (verified in the notebook's own saved cell-5
   output and in `data/variance_partition.csv`) is `environment (GroupKFold, out-of-study) = -0.296` (≈ **−0.30**),
   which is exactly the number `REPORT.md`'s Finding 3 table and Results table correctly cite. The −0.34 figure
   appears to be a holdover from before the REVIEW_2 fix filtered the null-`workflow_run_id` row out of
   `analysis_table.csv` (2,760→2,759 rows), which slightly perturbed the GroupKFold model's cross-validated R².
   `REPORT.md` was updated to the new value; the README overview and the NB04 hardcoded print string were not.
   This is a minor but concrete, user-facing inconsistency: a reader who checks the headline overview number in
   README.md against REPORT.md's own Finding 3 table will see two different R² values (−0.34 vs −0.30) for the
   same claim.
2. **Stale run-count in NB01's markdown takeaways.** `notebooks/01_data_assembly.ipynb` cell 12 ("NB01 takeaways")
   still reads "2,760 ReadbasedAnalysis runs (9 studies)", while cell 1's own executed output — two cells earlier
   in the same notebook — prints "runs: 2759 | studies: 9". This is the same underlying stale-count issue as #1
   (a markdown cell not updated after the REVIEW_2 data fix was applied and the notebook re-run), isolated to
   NB01 and not propagated elsewhere; REPORT.md and README.md's own body text correctly say "2,759" throughout.

Both issues are textual/reporting inconsistencies, not analysis errors — the underlying computation, data, and
REPORT.md numbers are correct; only two leftover prose strings (one in README, one in a notebook markdown/print
cell) were not refreshed after the last data fix.

No SQL correctness issues found: the GOTTCHA/Kraken/Centrifuge aggregation queries in
`src/build_analysis_table.py` correctly divide by the per-run total (with `NULLIF` guarding the Centrifuge
denominator), all three now filter `workflow_run_id IS NOT NULL`, and the `parent_id`-based bridge joins match
the pitfalls documented in `memories/pitfalls.md`.

## Findings Assessment
The four numbered findings in REPORT.md are each backed by a specific notebook, table, and figure. Finding 3 (the
apparent environment effect is confounded with batch) remains the strongest-supported result, shown three
independent ways (random-CV vs. GroupKFold R² gap, `study_id`-only R² matching the environment-only random-CV R²,
and near-chance out-of-study AUC = 0.56). Finding 4's vegetation/geography result is legitimately batch-controlled
(`env_local`, 11 levels, and `geo_loc`, 47 sites, are both genuinely-varying fields within the dominant NEON soil
study), and — since the REVIEW_2 fix — is no longer conflated with the non-batch-controlled depth statistic.

Limitations remain candid and specific: "Few independent studies" and "Wet-lab factors not testable" are backed by
the Phase A feasibility scan; the "Pooled-run metadata" limitation correctly scopes the representative-sample
noise as conservative. Nothing in the report is left as "to be filled." The Discoveries section is appropriately
scoped — the confounding-trap discovery is hedged ("This likely also qualifies..."), the within-batch discovery is
scoped to "in a NEON soil study" rather than generalized, and the classifier-database discovery accurately mirrors
`memories/pitfalls.md` (a documented gotcha, not claimed as a novel finding). Performance Notes remain concrete and
match what `src/build_analysis_table.py` actually does.

## Suggestions
1. **(Correctness, low-moderate priority)** Update `README.md` line 18's out-of-study R² from −0.34 to −0.30 (or
   the exact −0.296) to match `REPORT.md`'s Finding 3 table and the current `data/variance_partition.csv`, and
   update the same hardcoded string in `notebooks/04_within_study.ipynb` cell 9. This is the one place a careless
   reader could see two different numbers for the same headline claim.
2. **(Cleanliness, low priority)** Update `notebooks/01_data_assembly.ipynb` cell 12's takeaways text from
   "2,760 ReadbasedAnalysis runs" to "2,759", matching cell 1's own printed output and the rest of the project.
3. **(Cleanliness, nice-to-have, carried over from REVIEW_2)** `data/euk_fraction_per_file.csv` remains an
   unreferenced superseded v1 artifact; remove or annotate it as superseded.
4. **(Future work, already flagged by the authors)** Future Directions #1 (bringing in a many-study resource like
   SPF to break the batch confound) remains the right next step if this line of work continues, since it is the
   one improvement that would let the central claim generalize beyond NMDC's ~9 studies.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-07-10
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, REVIEW_1.md, REVIEW_2.md, references.md, beril.yaml,
  `memories/pitfalls.md`, `docs/pitfalls.md`, 4 notebooks (`01_data_assembly`–`04_within_study`, including saved
  cell outputs), `src/build_analysis_table.py`, 12 data files (2 markdown provenance docs + 10 CSVs, including a
  direct row/study count check of `analysis_table.csv` and a value check of `variance_partition.csv`), 4 figures,
  and `git log`/`git show` of the project's commit history including both prior review-fix commits (`ddaeb255`,
  `12d46cdd`).
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive
  assessment.

<!-- report_hash: sha256:345875dfe9abb66eeb33126277f33a3a655e7e7feed29ff12ebd79787207c86a -->
