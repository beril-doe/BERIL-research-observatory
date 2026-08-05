# Eukaryotic Contamination Correlates in Prokaryote-Targeted Metagenomes

## Research Question
What sample collection, processing, and sequencing factors correlate most strongly with
eukaryotic contamination of samples collected for prokaryotic metagenome analysis?

## Status
Completed — eukaryotic contamination of NMDC prokaryote-targeted metagenomes is common (77% of runs) and photosynthetic-dominated; its association with environment is confounded with study/batch and only recoverable under batch control (within-study R²=+0.17). (Submission pending — tenant write access needed; see SUBMISSION_FAILED.md.)

## Overview
Samples collected and sequenced for prokaryotic (bacterial/archaeal) metagenome analysis
frequently carry eukaryotic sequence — host DNA, plant/fungal material, protists, or reagent
contaminants. This project asks which upstream metadata factors best predict the eukaryotic
fraction of a prokaryote-targeted metagenome, using NMDC read-based taxonomy (collections
`nmdc_results`, `nmdc_metadata`, `kbase_nmdc_arkin`). Main result: eukaryotic contamination is
common (77% of runs) and overwhelmingly photosynthetic (plant/algal plastid); it associates
strongly with environment univariately, but that association is **confounded with study/batch**
and does not generalize across studies (out-of-study R²=−0.30). Only under batch control (within
one NEON soil study) do local vegetation and geography genuinely predict eukaryotic content
(within-study R²=+0.17; Arctic tundra ≫ temperate forest).

## Quick Links
- [Research Plan](RESEARCH_PLAN.md) — hypothesis, approach, query strategy
- [Report](REPORT.md) — findings, interpretation, supporting evidence

## Reproduction
1. On-cluster (BERDL JupyterHub), from the repo root: `python scripts/berdl_env.py --check`.
2. Build the analysis table (heavy Spark aggregation over `nmdc.results`):
   `python projects/euk_in_prok_correlates/src/build_analysis_table.py` → writes `data/analysis_table.csv`.
3. Execute the notebooks in order (they load the frozen CSVs and save figures):
   `jupyter nbconvert --to notebook --execute --inplace projects/euk_in_prok_correlates/notebooks/0{1,2,3,4}_*.ipynb`.
   **Note:** on this JupyterHub, `--inplace` can silently drop saved outputs (see `docs/pitfalls.md`
   "`jupyter nbconvert --inplace` Silently Drops Cell Outputs"). After executing, confirm each notebook has
   non-empty code-cell outputs; if any are empty, re-run with `--output <name>_executed.ipynb`.
4. Outputs: `figures/fig0{1..4}_*.png`, `data/*.csv`. See `data/00_feasibility_findings.md` and
   `data/01_data_landscape.md` for data-provenance and study-breadth context.

## Authors
Mark Andrew Miller (LBL), ORCID [0000-0001-9076-6066](https://orcid.org/0000-0001-9076-6066)
