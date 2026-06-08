---
reviewer: BERIL Automated Review
date: 2026-06-08
project: lifestyle_cog
---

# Review: Lifestyle-Based COG Stratification (re-review)

## Summary

This is a substantially improved second-round version of a well-scoped pangenome study comparing COG functional composition between free-living and host-associated bacteria across 2,529 species in 10 phyla. The author has addressed all twelve issues from the previous round: the placeholder "Findings" cells now point to REPORT.md, the enrichment-score pseudocount distortion is documented and a log-ratio sensitivity check confirms sign-preservation for all 24 COGs, multi-character COG splitting is explicitly described in a methods note (with the 6.5% inflation quantified), the README has a real Reproduction section with per-step Spark/local separation and runtimes, `requirements.txt` exists, rank-biserial effect sizes are reported throughout (with the striking finding that only S is "large" by Cohen-style cutoffs), the annotation-coverage confounder check (`src/annotation_coverage.py`) ran on the full cohort and shows only a 1.3 pp difference in COG-annotation rate by lifestyle, within-phylum tests are now BH-corrected (`src/review_addenda.py` → 42 of 110 tests survive q<0.05), `scipy.stats.false_discovery_control` replaces the manual BH calculation, the lifestyle classifier uses substring sentinel matching that catches `"not known"` and `"not applicable [GAZ:none]"`, numeric columns are defensively cast with `pd.to_numeric`, and RESEARCH_PLAN.md author metadata is synchronized. The remaining gaps are minor: one referenced data file (`data/phylum_within_stats.csv`) is missing because NB03 cell 5's added BH block didn't fully re-execute when the notebook was last saved, the four figures still show the original 1e-4-pseudocount enrichment values (so the heatmap label "A: −2.40" looks alarming even though the more conservative log-ratio rescales it to −0.31), and the single-letter-only sensitivity check and a phylogenetically-controlled GLM are correctly listed as future work rather than performed.

## Methodology

The research design has not changed since the first round, and it remains sound. The pre-registered H1/H2/H3 hypotheses, the EAV pivot of `ncbi_env`, the `gene_cluster_id = query_name` join, the per-species batching (BATCH_SIZE = 20) over 2,529 species, the species-level ≥70% majority vote at ≥10 genomes, and the per-phylum consistency analysis are all unchanged and all defensible. The methodology improvements that landed in this round are mostly *post-hoc* robustness work rather than new primary analyses:

- The lifestyle classifier was tightened: NB01 cell 17 now uses `na_substrings = ['not applicable', 'not collected', 'missing', 'n/a', 'none', 'unknown', 'not known', 'restricted access', 'not provided', 'not reported', 'na ', 'not available']` checked via substring containment, rather than exact `isin()`. This closes the previously-flagged hole where `"not known"` and `"not applicable [GAZ:none]"` slipped through as valid hosts. Good fix.
- An annotation-coverage confounder check (`src/annotation_coverage.py`) runs a single Spark join via `createOrReplaceTempView("lifestyle_species")` rather than a Python loop — a clean efficient pattern.
- The within-phylum tests are BH-corrected in both NB03 cell 5 and `src/review_addenda.py`, and the more conservative number (42/110 surviving at q<0.05) is what REPORT.md now cites.
- A log-ratio re-formulation `log2((prop_acc + 1e-3) / (prop_core + 1e-3))` is included as sensitivity check; the `log_ratio_sensitivity.csv` shows sign preserved for all 24 COG categories.

Reproducibility is much improved:

- **Reproduction section is now substantive**: README.md now has Prerequisites (BERDL JupyterHub, requirements.txt, off-cluster tunnels), a per-step runtime table (NB01 ~5–10 min Spark, NB02 cells 1–4 ~30–60 min Spark, NB02 cells 5+ <2 min local/pandas, NB03 <2 min local, `src/review_addenda.py` <30 s, `src/annotation_coverage.py` ~30–60 min Spark), and a Quick-start that explicitly tells the reader which steps need Spark and which can run on the cached CSVs. This was the largest documentation gap before, and it is fixed.
- **`requirements.txt` is present** with pinned minimum versions for pyspark, scipy, pandas, numpy, matplotlib, seaborn.
- **Notebook outputs are still saved** (NB01 16/17, NB02 11/13 of the code cells, NB03 8/9), which preserves the audit trail.
- **All four figures are referenced and exist on disk** — though see Code Quality #2 below for the figure-staleness caveat.

The classification framework remains binary (host_associated vs free_living) with ambiguous cases excluded; the three-way classification (free-living / commensal / pathogen) is correctly listed under Future Directions.

## Code Quality

**Strengths (this round):**

- `scipy.stats.false_discovery_control(... , method='bh')` is now used in NB02 cell 13, NB03 cell 5, and `src/review_addenda.py` — no more manual reverse-cummin step, no dead import.
- Rank-biserial correlation is computed in-line in NB02 cell 13 (`rb = 1.0 - 2.0 * float(stat) / (len(host) * len(free))`), classified into Cohen-style bins via `pd.cut`, and saved into `cog_lifestyle_stats.csv` so downstream consumers get effect sizes for free.
- NB02 cell 16 (H3 core fraction) and NB03 cell 7 (confounder plots) both now `pd.to_numeric(..., errors='coerce')` the `no_core` and `no_gene_clusters` columns — defensive against the documented string-typed-numeric pitfall.
- The new `src/annotation_coverage.py` correctly uses `createDataFrame` + `createOrReplaceTempView` to join the lifestyle CSV inside Spark, avoiding the per-species IN-clause batching that the original NB02 cell 4 uses for the heavier query. This is the right pattern when the join key is a small set.
- The multi-character COG splitting convention is now explicitly documented in NB02 cell 7 (markdown) and in REPORT.md §"Methods note: multi-character COG categories", and the 6.5% inflation figure is computed in NB02 cell 6 with a printed output (`Multi-char fraction: 6.5%`) that the reader can verify directly.

**Remaining issues:**

1. **`data/phylum_within_stats.csv` is referenced but missing.** README.md lists this file under Data Files, and NB03 cell 5 ends with `phylum_df.to_csv('../data/phylum_within_stats.csv', index=False)`. But the file is not present in `data/` (only `data/review_addenda/phylum_within_bh.csv` is). Inspecting NB03 cell 5's saved outputs shows the prints from the BH block (`Phylum x COG tests: ... significant after BH`) are absent — only the earlier "Within-Phylum Consistency" prints and the `phylum_stats.head(20)` display are saved. This strongly suggests the BH-correction code at the bottom of cell 5 was added after the last full re-run, so the CSV was never actually written. The equivalent (correct) data IS available in `data/review_addenda/phylum_within_bh.csv`, so the analytical claim in REPORT.md is supported; this is just a documentation/file-presence mismatch. Either delete the README row, point it at `phylum_within_bh.csv`, or re-run NB03.

2. **The four committed figures are pre-revision** (all dated Jun 8 13:59, before the round-2 changes that went in at 14:33–15:22). They use the original `(prop_acc − prop_core) / (prop_core + 1e-4)` enrichment score. For most categories this is fine — magnitudes change but signs and qualitative ordering do not — but `enrichment_heatmap.png` and `lifestyle_cog_heatmap.png` will display the A-category at roughly −2.40 (the small-denominator artifact) even though REPORT.md text now explicitly tells the reader the conservative number is −0.31. A reader looking only at the figures will see the inflated value and may be misled. Either (a) re-render the heatmaps with the log-ratio column, or (b) add a small caption note in the figure (or alt-text in REPORT.md) flagging that the A magnitude is artifactual.

3. **The single-letter-only sensitivity check is still future work.** The methods note quantifies the 6.5% inflation but defers the actual re-analysis. Given how cheap this would be (`cog_raw[cog_raw['cog_len'] == 1]` then re-aggregate, no Spark needed), it would be straightforward to add as a one-cell appendix to NB02 and a one-line confirmation in REPORT.md. Not a blocker; just low-hanging fruit.

4. **The primary enrichment score in `data/cog_enrichment_by_lifestyle.csv` is still the 1e-4 formulation.** The log-ratio sensitivity check in `src/review_addenda.py` writes a separate `log_ratio_sensitivity.csv` rather than augmenting the main per-species file with an `enrichment_log2` column. A reader who pulls `cog_enrichment_by_lifestyle.csv` for downstream work will get the original score. Adding `enrichment_log2` as a second column in NB02 cell 10 (cheap — five lines) would let downstream users pick the more conservative score directly.

5. **Genome-count confounder is addressed verbally, not quantitatively.** REPORT.md correctly argues that "uniform amplification cannot explain the differential COG composition" because the V/L/K/U/S vs E/G/C/P/I directions go opposite ways. That argument is sound, but a subsample-matched comparison (e.g., for each host species, draw a free species in the same phylum and ±20% genome count) or a residual analysis (regress enrichment on log10(no_genomes) within lifestyle then test residuals between lifestyles) would convert this from rhetorical to quantitative. Listed already in Future Directions as the GLM step.

6. **NB02 cell 4 still does `.toPandas()` per batch.** Reasonable here because each batch returns a small aggregate, but the 127-batch loop accumulates ~14M output rows. This is fine for current scale but if the cohort grows (e.g., re-running on the next BERDL release) it would benefit from Spark-side concatenation or writing batches to disk and reading at the end.

Otherwise the SQL and aggregation logic looks correct, the COG dictionary handling is safe (the multi-char split happens before the description dict lookup, so no NaN-handling pitfall), and the pangenome `no_core` / `no_gene_clusters` arithmetic is correctly defended against string-typed columns.

## Findings Assessment

The findings section is the strongest part of the revised project. REPORT.md now contains:

- **Effect sizes throughout.** Each H1/H2 result table carries the rank-biserial `r` and Cohen-style effect-size class (small / medium / large). The headline that "S is the *only* LARGE-effect category and E/I/J/P/C/F/K are MEDIUM while V/L/U/W are SMALL" is more informative than the original p-value-only framing, and explicitly tempers the V finding (which is biologically central to the H1 narrative but only "small" in magnitude).
- **A log-ratio sensitivity result.** The `log_ratio_sensitivity.csv` shows sign preserved for 24/24 categories vs. the original formula, 21/24 still BH-significant, and the A-category Δ rescales from −2.40 to −0.31 (with r = +0.25, small). This directly addresses the previous round's #2 issue and the analysis cleanly confirms top-line conclusions.
- **Quantitative annotation-coverage confounder result.** The host vs free median COG-annotation rate is 56.5% vs 57.9% (Δ = −1.3 pp, p = 8.9 × 10⁻³, rank-biserial r = +0.06, "negligible"). REPORT.md correctly notes this is statistically present but biologically tiny, and uses it to bound the contribution of annotation lag to the S-category finding (6.4 pp shift in S accessory share vs 1.3 pp coverage gap → most of the S finding is real compositional shift). This is exactly the right interpretive move.
- **BH-corrected within-phylum tests.** The 42/110 surviving at q<0.05 number replaces the heuristic-only direction-consistency claim from the previous round. The narrative now uses the BH numbers as the conservative complement to the consistency heuristic, which is a more defensible argumentative structure.

Specific strengths:

- The Cyanobacteriota H3 outlier discussion is unchanged but still excellent — host-associated Cyanobacteria include reduced endosymbionts that violate the facultative-host assumption, and this is explicitly called out as a classifier limitation.
- The H3-vs-classical-streamlining discussion is correct: the ≥10-genome filter excludes obligate endosymbionts, so the "host has smaller core fraction" finding lives in a different regime from McCutcheon/Moran/Klasson.
- The "S inflation = annotation-lag" interpretation is appropriately hedged ("partly reflect under-study rather than novel biology") and supported by both the annotation-coverage check and the cross-reference to `functional_dark_matter` NB12.
- Wang et al. (2024) on Bacillus subtilis and Awad et al. (2025) on Enterobacteriaceae are cited in the right places to corroborate V/L accessory-enrichment from independent published cohorts.

Remaining weaknesses:

- **The four published figures are still the v1-formula figures** (see Code Quality #2). For a reader who only looks at figures plus the bullet points, the inflated A-category magnitude is what they will see.
- **The genome-count confound (median 20 vs 14)** is addressed by argument, not by a matched subsample. The argument is correct but a quantitative check would close the loop.
- **The novelty claim "first pan-bacterial, lifestyle-stratified test of COG functional composition at the core/accessory level"** is plausible but worth flagging — Dewar et al. (2024) at 126 species, Wang et al. (2024) at the Bacillus subtilis group, and Awad et al. (2025) at Enterobacteriaceae are the named comparators, and the 2,529-species 10-phylum scope is genuinely the largest, so the claim seems supportable. A literature search restricted to the last 18 months would harden it.

## Suggestions

In priority order:

1. **(Medium) Re-run NB03 (or just cell 5) to write `data/phylum_within_stats.csv`.** The README references this file and the cell is set up to write it; only the saved outputs from the BH-correction print block are missing. Alternatively, delete the row from the README table and point downstream consumers at `data/review_addenda/phylum_within_bh.csv` (which has identical content). Pick one.

2. **(Medium) Regenerate the two heatmap figures (`enrichment_heatmap.png`, `lifestyle_cog_heatmap.png`) from the log-ratio column.** Or add a caption note clarifying that the A magnitude shown is the original `(prop_acc - prop_core) / (prop_core + 1e-4)` value and that the conservative log₂ ratio rescales it to −0.31. The current figures contradict the §Limitations text for any reader who skims figures first.

3. **(Medium) Add an `enrichment_log2` column to `cog_enrichment_by_lifestyle.csv`** alongside the original `enrichment_score`. Five lines in NB02 cell 10. This lets downstream consumers (and future projects that build on this CSV) pick the conservative formulation without re-running `src/review_addenda.py`.

4. **(Low) Run the single-letter-only sensitivity check.** `cog_raw[cog_raw['COG_category'].str.len() == 1]`, re-aggregate, repeat the Mann-Whitney panel, and report whether the V / E / G / C / P / I / S directions all hold. This converts the 6.5% inflation caveat from "left to future work" to a closed loop.

5. **(Low) Add a genome-count-matched subsample analysis** for the H1/H2/H3 panels. For each host species, sample a free species in the same phylum and within ±25% on `log10(no_genomes)`; re-run Mann-Whitney on the matched pairs. If the V/L/K/U vs E/G/C/P/I directions all hold, the genome-count argument becomes empirical rather than rhetorical.

6. **(Low) Verify the "first pan-bacterial lifestyle-stratified COG analysis" claim** with a focused PubMed/Europe PMC search in the 2024–2026 window for terms like `"pangenome" + "COG" + "host-associated" + "free-living"`. The current literature context is good but doesn't explicitly bound the claim.

7. **(Low) Consider committing a short `Makefile` or `run.sh`** that calls `python src/review_addenda.py` and `python src/annotation_coverage.py` in sequence after the notebooks. The Reproduction section explains the order in prose; codifying it would prevent reproducers from running the heavy `annotation_coverage.py` before `review_addenda.py` (or vice versa) if the dependency between them ever becomes relevant.

## Review Metadata

- **Reviewer**: BERIL Automated Review
- **Date**: 2026-06-08
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, references.md, beril.yaml, requirements.txt, 3 notebooks (`01_data_exploration.ipynb`, `02_cog_enrichment.ipynb`, `03_phylogenetic_controls.ipynb`), 3 primary CSVs in `data/`, 5 addenda CSVs in `data/review_addenda/`, 4 figures in `figures/`, 2 Python scripts in `src/` (`annotation_coverage.py`, `review_addenda.py`), plus `docs/pitfalls.md` for context. This is a re-review following the author's response to a previous 12-item review; the previous REVIEW.md was read first and used to frame the assessment.
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive assessment.
