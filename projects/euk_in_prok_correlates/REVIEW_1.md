---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-07-10
project: euk_in_prok_correlates
---

# Review: Eukaryotic Contamination Correlates in Prokaryote-Targeted Metagenomes

## Summary
This is a methodologically careful project that asks which sample-collection metadata correlate with eukaryotic
contamination in NMDC prokaryote-targeted metagenomes, and its strongest contribution is not the headline
correlation but the demonstration that the naive cross-study version of that correlation is confounded with
study/batch (out-of-study R² = −0.34) — a genuine, well-supported, and honestly reported negative result. The
project explicitly revised its own plan mid-stream (v1 → v2, documented in `RESEARCH_PLAN.md`'s revision history)
after discovering this confound, switched response-variable sources, and added a within-study batch-controlled
test (NB04) that recovers a real, interpretable signal (vegetation/geography → soil eukaryotic fraction, R²=+0.17).
All four notebooks execute end-to-end with saved outputs, all four have a matching figure, the two project-level
pitfalls are documented in `memories/pitfalls.md` and consistently applied in code, and the REPORT's literature
context and limitations sections are unusually thorough. The main gaps are (1) a Kruskal-Wallis test in NB02 that
folds an "Unknown"/missing-metadata category into a formal hypothesis test without caveat, (2) a vestigial dead
line of code in NB03, and (3) the pooled-run representative-biosample choice (MIN(biosample_id)) that isn't fully
caveated as a source of metadata noise. None of these undermine the headline findings, but the first is worth
fixing before treating the "ecosystem_type" p-value as clean evidence.

## Methodology
The research question is clearly stated and testable, and the hypothesis structure (H0/H1a/H1b/H1c) maps cleanly
onto the notebook sequence. Data sources are explicitly identified per-table in `RESEARCH_PLAN.md`'s Query
Strategy table and in `REPORT.md`'s Data/Sources table, including which BERDL collection each table lives in.

A real strength is the project's own mid-course correction: `data/00_feasibility_findings.md` (Phase A) documents
which literature-ranked predictors NMDC actually captures (environment/matrix 94%, but DNA extraction ~1%, size
fractionation 0%, library prep 0%) — an honest feasibility scan rather than a hand-wave. `data/01_data_landscape.md`
then goes further and interrogates whether a broader on-system source could break the ~9-study confound before
concluding it cannot, which is exactly the kind of check that should precede a confounded correlate claim.

Reproducibility is good: the README's `## Reproduction` section gives an ordered, concrete command sequence
(feasibility check → `build_analysis_table.py` heavy Spark step → `jupyter nbconvert --execute --inplace` over
NB01-04), states what's heavy/on-cluster vs what runs from frozen CSVs, and lists expected outputs. Someone with
BERDL access could reproduce this end-to-end. One gap: no explicit runtime estimate is given for the Spark
aggregation step (the README says "heavy Spark aggregation" but not roughly how long), which the Reproduction
guidance in the review checklist calls out as useful to include.

## Code Quality
The four notebooks (`01_data_assembly`, `02_univariate_tests`, `03_model_variance`, `04_within_study`) are
well-organized: each opens with a markdown cell stating its goal relative to the hypothesis it's testing, uses a
consistent `DATA`/`FIG` path convention, and ends with a "takeaways" cell. All are backed by real commit history
(`git log --oneline -- projects/euk_in_prok_correlates/notebooks/` shows NB01-04 built across dedicated commits,
not reconstructed post hoc — the project avoids the "notebook alongside artifacts" pitfall documented in
`docs/pitfalls.md`).

Statistical methods are appropriate for the zero-inflated, non-normal response: Kruskal-Wallis/Mann-Whitney with
BH-FDR correction for group comparisons (NB02), a logit transform of the response for the regression models
(NB01/NB03), and `GroupKFold(groups=study_id)` to get an honest out-of-study R² instead of a leakage-prone random
split (NB03) — this is the single most important methodological choice in the project and it's done correctly.

Two project-specific pitfalls are documented in `memories/pitfalls.md` (Kraken DB is prokaryote-restricted; NMDC
child tables join on `parent_id` not `id`; the `omics_files_table`/`biosample_to_workflow_run` bridge) and both
are correctly reflected in `src/build_analysis_table.py` — e.g. `kraken2_classification_report` is queried and
kept only as a robustness control (its near-zero fraction is explained, not silently dropped), and the
`data_generation_set_has_input` → `*_instrument_used` join uses `parent_id` as documented.

Three specific issues, in order of importance:

1. **`notebooks/02_univariate_tests.ipynb`, cell 7** — the "ecosystem_type" Kruskal-Wallis test
   (`top=df['ecosystem_type'].value_counts().head(8).index.tolist()`) takes the top-8 most frequent values by
   count, and the single most frequent value is `"Unknown"` (1,002/2,760 runs, from `.fillna('Unknown')` in NB01
   cell 5) — the fill-value for missing `ecosystem_type`. The output table shows `Unknown` has the **highest**
   median eukaryotic fraction (0.0866) of any group in the test, higher than `Roots` (0.0549), and it is included
   in the reported `H=231.1, p=7.9×10⁻⁵⁰` statistic that REPORT.md's Finding 2 and Results table cite as evidence
   ecosystem type predicts euk fraction. This is inconsistent with the matrix-level test two cells earlier (cell 5),
   which deliberately restricts `groups` to `['Terrestrial','Aquatic','Plants','Artificial ecosystem']` and excludes
   `Unknown`. Folding a missing-data bucket into a formal significance test — and one that happens to carry the
   highest response value — risks the significance being partly an artifact of whatever mechanism causes
   `ecosystem_type` to be missing (e.g. it may cluster in a specific study or workflow), not a genuine ecosystem
   effect. This should either be excluded (matching the matrix-level test's convention) or explicitly flagged as
   a missingness-driven result if kept.
2. **`notebooks/03_model_variance.ipynb`, cell 5** — `res['study_only_group']=r2_cv(None if False else ENV,gkf,groups)  # placeholder replaced below`
   builds a `res` dict entry that is never read again (the actual reported values are assembled into the separate
   `part` Series a few lines later). This is dead/vestigial code left over from development — harmless to the
   result (it doesn't feed `part`), but it's worth removing so a future reader doesn't mistake `res` for a live
   variable feeding the analysis.
3. **`src/build_analysis_table.py`, lines 41-48** — for pooled `workflow_run_id`s (1,067/2,760 runs, per NB01),
   the biosample-level metadata (environment, ecosystem, geography, etc.) is taken from `MIN(biosample_id)` — an
   arbitrary representative biosample among however many were pooled into that sequencing run. The eukaryotic
   read fraction itself reflects the combined pooled material, but the environment label attached to it reflects
   only one constituent sample. This is a plausible source of noise (not necessarily bias) in the univariate and
   modeling results that isn't mentioned in REPORT.md's Limitations section (which does note pooling as a
   pseudo-replication concern but not this specific metadata-representativeness angle).

No SQL correctness issues were found in `src/build_analysis_table.py` — the GOTTCHA/Kraken/Centrifuge aggregation
correctly divides by the per-run total (with `NULLIF` guarding the Centrifuge denominator), and the bridge joins
match the documented pitfalls.

## Findings Assessment
The four numbered findings in REPORT.md are each backed by a specific notebook, table, and figure, and the
headline claim (Finding 3: apparent environment effect is confounded with batch) is the strongest-supported result
in the project — it's shown three independent ways (random-CV vs GroupKFold R² gap, `study_id`-only R² matching
the environment-only random-CV R², and near-chance out-of-study AUC). Finding 4's within-study test is a
legitimate, if narrower, control — the Limitations section correctly caveats that it's demonstrated for one soil
study only and that even within-study, sub-batches (sampling campaigns) aren't fully ruled out.

Limitations are unusually candid for an automated project: the "Few independent studies" and "Wet-lab factors not
testable" limitations are backed by the Phase A feasibility scan rather than asserted, and the Interpretation
section correctly frames the whole project's headline as a "cautionary result" about confounding rather than
over-claiming a causal metadata correlate. Nothing in the report is left as "to be filled." The Discoveries and
Performance Notes sections are appropriately scoped:
- The "cross-collection contamination-QC correlates are a confounding trap" discovery is directly tied to the
  NB03 GroupKFold result and is phrased as tentative ("This likely also qualifies...") rather than overclaimed.
- The "within-batch, environmental drivers are real and large" discovery is scoped correctly to "in a NEON soil
  study" rather than generalized.
- The classifier-database discovery (GOTTCHA vs Kraken/Centrifuge) duplicates the project's own
  `memories/pitfalls.md` entry almost verbatim — reasonable for a REPORT.md Discoveries section since that's
  exactly the kind of claim meant to surface to future projects, but note it is not a novel finding of this
  project so much as a documented gotcha; scope ("Applies to": NMDC classifiers specifically) is accurate.
- Performance Notes are concrete and actionable (aggregate before joining `kraken2_classification_report`'s ~29M
  rows; analyze at `workflow_run_id` not biosample level; the bridge chain). All are consistent with what
  `src/build_analysis_table.py` actually does.

One figure/finding mismatch to note: Figure 1 (`fig01_euk_distributions.png`) is cited as supporting Finding 1,
but its third panel (source prevalence bar chart) is really evidence for Finding 2 (source-tracks-environment);
this is a minor labeling nit, not a substantive issue.

## Suggestions
1. **(Correctness, moderate priority)** Exclude the `"Unknown"` ecosystem_type bucket from the NB02 cell-7
   Kruskal-Wallis test (or re-run and report both with/without it), matching the exclusion convention already
   used for the matrix-level test in cell 5. Update REPORT.md's Finding 2 / Results table if the statistic
   changes materially.
2. **(Cleanliness, low priority)** Remove the dead `res['study_only_group']=...` line in
   `notebooks/03_model_variance.ipynb` cell 5, or wire it into `part` if it was intended to be used.
3. **(Documentation, low priority)** Add a sentence to REPORT.md's Limitations noting that pooled-run predictors
   are drawn from one representative biosample (`MIN(biosample_id)`) rather than all pooled biosamples, alongside
   the existing pooling/pseudo-replication caveat.
4. **(Nice-to-have)** Add an approximate runtime for `src/build_analysis_table.py`'s Spark aggregation step to the
   README's Reproduction section, so a reproducer knows what to expect before kicking it off.
5. **(Future work, already flagged by the authors)** The project's own Future Directions #1 (bringing in a
   many-study resource like SPF to break the batch confound) is the right next step if this line of work
   continues — worth prioritizing over #3/#4 given it's the one that would let the central claim generalize
   beyond NMDC's ~9 studies.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-07-10
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, references.md, beril.yaml, 4 notebooks, 12 data files (2 markdown provenance docs + 10 CSVs), 4 figures, `src/build_analysis_table.py`, `docs/pitfalls.md`, `memories/pitfalls.md`
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive assessment.

<!-- report_hash: sha256:89906b656be4c42af3515e7746a43e90a2d14849b93a2ff9bc8fe432cb02ac2d -->
