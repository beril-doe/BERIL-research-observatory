---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-07-10
project: euk_in_prok_correlates
---

# Review: Eukaryotic Contamination Correlates in Prokaryote-Targeted Metagenomes

## Summary
This is a well-executed, self-critical project: it asks which sample-collection metadata correlate with
eukaryotic contamination in NMDC prokaryote-targeted metagenomes, and its central contribution — showing that
the naive cross-study version of that correlation is confounded with study/batch (out-of-study R² = −0.34) while
a batch-controlled within-study test recovers a genuine signal (R² = +0.17) — is honest, well-supported, and
methodologically the right way to have framed this analysis. I confirmed via `git log` that the three issues
raised in `REVIEW_1.md` (the `Unknown`-bucket Kruskal-Wallis test in NB02, a dead line in NB03, and an
undocumented pooled-run metadata caveat) were fixed in commit `ddaeb255`, and I independently verified all three
fixes are correctly applied in the current notebooks and REPORT.md — this is a project that responds to review
rather than just filing it. My own independent pass over the current state found one new issue worth fixing
before further use: REPORT.md's Finding 4 ("When batch is held constant... environment is genuinely predictive")
presents a depth–eukaryote correlation (ρ=−0.29) inline with the batch-controlled vegetation/geography results,
but that correlation is computed on the whole cross-study table, and the dominant NEON soil study used for the
rest of Finding 4 has **zero** non-null depth values — so this one statistic is not batch-controlled at all,
despite its placement implying it is. I also found two minor, non-blocking data-hygiene nits. None of these
undermine the project's headline confounding result, which remains the strongest and best-evidenced claim in the
report.

## Methodology
The research question (which metadata factors correlate with eukaryotic fraction in prokaryote-targeted
metagenomes) is clearly stated, testable, and the H0/H1a/H1b/H1c structure maps directly onto the four
notebooks. `RESEARCH_PLAN.md`'s revision history (v1 → v2) transparently documents two real mid-course
corrections: switching the response-variable source after discovering the Kraken2 reference DB is
prokaryote-restricted, and adding the within-study contrast (NB04) after `data/01_data_landscape.md` established
that no on-system source can break the ~9-study confound. This kind of documented pivot, backed by
`data/00_feasibility_findings.md` (a genuine feasibility scan showing which literature-ranked predictors NMDC
actually captures: extraction kit ~1%, size fractionation 0%, library prep 0%) is a real strength — the project
does not hand-wave its way past a data-availability gap, it investigates and reports it.

Data sources are identified precisely, down to which BERDL collection and table each predictor/response variable
comes from (`RESEARCH_PLAN.md`'s Query Strategy table, `REPORT.md`'s Data/Sources table). Reproducibility is
good: README's `## Reproduction` section gives an ordered command sequence from the heavy Spark build step
through notebook execution, and states what output files to expect. One reproducibility gap: the README's step 3
recommends `jupyter nbconvert --to notebook --execute --inplace ...`, which `docs/pitfalls.md` documents (under
"`jupyter nbconvert --inplace` Silently Drops Cell Outputs") as a known failure mode on this JupyterHub — it can
exit 0 while writing zero cell outputs back to disk. The README doesn't flag this risk or suggest the documented
workaround (`--output` to a separate file), so a reproducer following the README verbatim could silently lose
the very outputs the Reproducibility checklist cares about.

## Code Quality
The four notebooks are consistently organized (goal statement → setup → analysis → takeaways), use a shared
`DATA`/`FIG` path convention, and are backed by real, incremental commit history
(`73fdeadd`, `bcf1e473`, `ddaeb255` each touch the notebooks directly) — not reconstructed after the fact, which
avoids the "Commit Notebooks Alongside Their Artifacts" pitfall in `docs/pitfalls.md`.

Statistical methods are appropriate for a zero-inflated, non-normal, batch-structured response: Kruskal-Wallis /
Mann-Whitney with BH-FDR correction (NB02), a logit-transformed response for regression (NB01/NB03), and —
the single most important methodological choice in the project —
`GroupKFold(groups=study_id)` to get an honest out-of-study R² instead of a leakage-prone random split (NB03).
The `study_id`-only "batch ceiling" model is correctly reported as in-sample only, with an explicit comment
explaining why it can't be evaluated out-of-study (a one-hot of `study_id` can't generalize to unseen studies).

**Verified fixes from REVIEW_1** (commit `ddaeb255`, "fix(euk_in_prok_correlates): address REVIEW_1"):
1. NB02 cell 7 now explicitly excludes the `Unknown`/missing-metadata bucket
   (`top=[t for t in df['ecosystem_type'].value_counts().index if t!='Unknown'][:8]`), and the resulting
   `ecosystem_type` statistic (H=77.8, p=1.3×10⁻¹⁷) is now identical to the matrix-level test — REPORT.md
   correctly notes this is not an independent confirmation, and the old inflated p≈10⁻⁵⁰ statistic has been
   removed from the Results table.
2. The dead `res['study_only_group']=...` placeholder line is gone from NB03 cell 5.
3. REPORT.md's Limitations now includes a "Pooled-run metadata" entry describing the `MIN(biosample_id)`
   representative-biosample choice for pooled runs and its conservative-bias direction.

All three are correctly and specifically applied — this is not just a status-field edit.

**New issue found in this pass:**

1. **`REPORT.md`, Finding 4 (lines ~65–80)** — the paragraph "A depth association also emerges (Spearman
   ρ = −0.29, p=5.2×10⁻⁷, n=292): shallower samples carry more eukaryotic DNA, consistent with surface
   plant/algal input" is placed immediately after, and reads as part of, the batch-controlled within-study
   analysis of the dominant NEON soil study (`nmdc:sty-11-34xj1150`, 1,186 runs). I checked
   `data/analysis_clean.csv` directly: the dominant study has **0 of 1,186 runs with a non-null `depth_m`**, so
   this correlation cannot have been computed within that study. It is in fact the NB02 cell-13 cross-collection
   statistic (`dd2=df[df['depth_m'].notna()&(df['depth_m']>0)]`, run on the full 2,760-row table before any
   study restriction), drawn almost entirely from three other studies (`nmdc:sty-11-hht5sb92` n=141,
   `nmdc:sty-11-r2h77870` n=103, `nmdc:sty-11-5bgrvr62` n=46). The Results table technically labels this row
   "Euk ~ depth (**within-collection**)" (accurate), but the Finding 4 narrative text and its placement directly
   under "When batch is held constant... environment is genuinely predictive" strongly implies it was computed
   under the same batch control as the vegetation/geography results two bullets above it. Given the project's own
   central thesis — that cross-study associations without batch control are potentially spurious (Finding 3) —
   citing an un-batch-controlled 3-4-study correlation as supporting evidence for a batch-controlled finding is
   an internal inconsistency that a careful reader could mistake for another controlled result. This should be
   moved out of Finding 4 (e.g., into Finding 3 or its own caveated sentence) and explicitly labeled as
   cross-study/not batch-controlled, or dropped if it isn't going to be re-run within a depth-populated study.

**Minor, non-blocking nits:**

2. **`src/build_analysis_table.py`, gottcha CTE (lines 20-26)** — one row in `data/analysis_table.csv` has a
   null `workflow_run_id` (`sample_id`), which propagates through as a phantom "run" with `gott_euk_frac=0.0`
   and null everything else, inflating the reported run/study counts by one (2,760 vs. 2,759 valid; NB03's
   "10 studies" vs. NB01's "9 studies" — the 10th is this orphan's `fillna('NA')` bucket). Adding
   `WHERE workflow_run_id IS NOT NULL` to the gottcha query would remove it. Impact is negligible (1/2,760 rows)
   but it's a one-line fix and the current 9-vs-10-studies inconsistency between NB01 and NB03 output is a minor
   point of confusion.
3. **`data/euk_fraction_per_file.csv`** is a leftover v1 (`kbase.nmdc_arkin` snapshot) artifact — it is not
   referenced anywhere in `REPORT.md`'s Generated Data table, `README.md`, or any current `src/*.py` script
   (confirmed via `grep`). It's harmless clutter left over from before the v2 pivot to `nmdc.results`, but worth
   removing or noting as superseded so a future reader doesn't mistake it for a currently-used data product.

No SQL correctness issues otherwise: the GOTTCHA/Kraken/Centrifuge aggregation queries correctly divide by the
per-run total (with `NULLIF` guarding the Centrifuge denominator), and the `parent_id`-based bridge joins match
the pitfalls documented in `memories/pitfalls.md`.

## Findings Assessment
The four numbered findings are each backed by a specific notebook, table, and figure. Finding 3 (the apparent
environment effect is confounded with batch) is the strongest-supported result in the project, shown three
independent ways (random-CV vs. GroupKFold R² gap, `study_id`-only R² matching the environment-only random-CV
R², and near-chance out-of-study AUC = 0.56). Finding 4's vegetation/geography result is legitimately
batch-controlled — I independently confirmed `env_local` (11 levels) and `geo_loc` (47 sites) are both real,
substantially populated fields within the dominant study — only the depth sub-claim within Finding 4 is not (see
Code Quality #1 above).

Limitations are candid and specific rather than boilerplate: "Few independent studies" and "Wet-lab factors not
testable" are each backed by the Phase A feasibility scan, and the newly-added "Pooled-run metadata" limitation
correctly scopes the `MIN(biosample_id)` representative-sample noise as conservative (can only weaken, not
manufacture, associations). Nothing in the report is left as "to be filled." The Discoveries section is
appropriately scoped:
- The "confounding trap" discovery is tied directly to the NB03 GroupKFold result and hedges appropriately
  ("This likely also qualifies...").
- The "within-batch, environmental drivers are real and large" discovery is correctly scoped to "in a NEON soil
  study" rather than generalized to all environments.
- The classifier-database discovery duplicates `memories/pitfalls.md` almost verbatim, which is appropriate for
  a Discoveries section meant to surface reusable gotchas, though it is a documented pitfall rather than a novel
  finding of this project — the scope ("NMDC classifiers specifically") is accurate.

Performance Notes are concrete and match what `src/build_analysis_table.py` actually does (aggregate the ~29M-row
`kraken2_classification_report` before joining; analyze at `workflow_run_id`, not biosample level, to avoid
pseudo-replication from pooled runs).

## Suggestions
1. **(Correctness, moderate priority)** Move or re-caveat the depth correlation in REPORT.md's Finding 4 — it is
   a cross-collection (3-4 study), not batch-controlled, statistic and should not sit inside the "batch held
   constant" narrative without an explicit flag. Either relocate it near Finding 3/2's cross-study discussion, or
   add a parenthetical noting it was not computed within the dominant study (depth is unmeasured there).
2. **(Reproducibility, low priority)** Add a note or workaround to README's Reproduction section for the
   documented `jupyter nbconvert --inplace` output-loss risk (`docs/pitfalls.md`), e.g. recommend `--output` to a
   separate file or point reproducers at the workaround already documented in that pitfall entry.
3. **(Cleanliness, low priority)** Filter the null `workflow_run_id` row out of `analysis_table.csv`
   (`WHERE workflow_run_id IS NOT NULL` in the gottcha query in `src/build_analysis_table.py`) to resolve the
   9-vs-10-studies discrepancy between NB01 and NB03 output.
4. **(Cleanliness, nice-to-have)** Remove or annotate `data/euk_fraction_per_file.csv` as a superseded v1
   artifact, since it is not used by any current notebook or script.
5. **(Future work, already flagged by the authors)** Future Directions #1 (bringing in a many-study resource
   like SPF to break the batch confound) remains the right next step if this line of work continues, since it's
   the one improvement that would let the central claim generalize beyond NMDC's ~9 studies.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-07-10
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, REVIEW_1.md, references.md, beril.yaml, `memories/pitfalls.md`,
  `docs/pitfalls.md`, 4 notebooks (`01_data_assembly`–`04_within_study`), `src/build_analysis_table.py` and
  `src/build_nb0{1..4}.py`, 12 data files (2 markdown provenance docs + 10 CSVs, including a direct check of
  `analysis_clean.csv` and `analysis_table.csv` contents), 4 figures, and `git log`/`git show` of the project's
  commit history including the REVIEW_1 fix commit (`ddaeb255`).
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive
  assessment.

<!-- report_hash: sha256:2a09f5593925ba32f531e37f10b41e42e8ba61f4f6648cb8a426574eaa544825 -->
