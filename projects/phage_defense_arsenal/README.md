# Pan-Bacterial Anti-Phage Defense Arsenal

## Research Question
Across the 293K-genome BERDL pangenome, how are seven of the major anti-phage defense system families (CRISPR-Cas, restriction-modification, CBASS, Gabija, Retron, BREX, DISARM) distributed; does species-level defense-system count scale with prophage burden (the coevolutionary arms-race prediction); and which system combinations co-occur beyond phylogenetic expectation, defining "defense syndromes" that may represent mobile defense islands?

## Status
Completed — 27 of 28 defense-system pairs form significant positive syndromes (H1b); species-level defense count scales with prophage burden after controlling for genome size and phylum, universal across 9 major phyla (H1a partial ρ = 0.30, p = 1.6e-153); 6 of 7 systems are enriched in the accessory pangenome (H1c).

## Overview
Surveys seven of the major anti-phage defense system families (CRISPR-Cas, restriction-modification, CBASS, Gabija, Retron, BREX, DISARM) across the BERDL pangenome (293K genomes, 27,690 species). Tests three linked hypotheses: (1) species-level defense-system count scales with prophage burden after controlling for genome size and phylum (the coevolutionary arms race), (2) specific system combinations co-occur beyond phylogenetic expectation, defining "defense syndromes" consistent with mobile-defense-island transfer, and (3) defense systems are enriched in the accessory pangenome. Detection uses `kbase_ke_pangenome.interproscan_domains` (primary, Pfam accession-based) with `eggnog_mapper_annotations` for R-M and CRISPR description-based confirmation. Prophage burden is re-derived using the eggNOG-description classifier from `projects/prophage_ecology/src/prophage_utils.py`.

**Headline results**: H1a supported (partial ρ = 0.30, p = 1.6e-153; universal across 9 major phyla), H1b supported massively (27 of 28 defense-system pairs are positive syndromes at BH-FDR q<0.05, with R-M Type II × Gabija OR = 24 as the strongest and novel finding), H1c supported for 6 of 7 systems (DISARM detection artefact flagged).

## Quick Links
- [Research Plan](RESEARCH_PLAN.md) — hypotheses, detection rules, query strategy, analysis plan
- [Report](REPORT.md) — findings, interpretation, supporting evidence

## Reproduction

### Prerequisites

- BERDL JupyterHub access with the standard on-cluster Python 3.13 image (provides `berdl_notebook_utils` and `pyspark` via Spark Connect). Off-cluster runs are possible via the local `.venv-berdl` + SSH tunnels; see `.claude/skills/berdl-query/references/off-cluster-mechanics.md`.
- A valid `KBASE_AUTH_TOKEN` in the environment (or `.env`) with read access to the `kbase_ke_pangenome` collection.
- Python packages listed in `requirements.txt` (pandas, numpy, scipy, scikit-learn, statsmodels, matplotlib, jupytext) — pre-installed in the JupyterHub image.

### Steps

Run the numbered notebooks in order from `projects/phage_defense_arsenal/notebooks/`:

1. `00_exploration.ipynb` — Phase-A feasibility check (reads `data/detection_feasibility.csv`; runs a handful of small Spark queries).
2. `01_extract_defense_clusters.ipynb` — Extract 930K defense marker hits from `interproscan_domains` + `eggnog_mapper_annotations`. Writes `data/defense_gene_clusters.tsv.gz` (~15 MB). Runtime: ~2 min.
3. `02_species_system_matrix.ipynb` — Build the species × system matrix, apply broad-Pfam co-occurrence filtering, attach covariates (phylum via regex-extract from `genome.gtdb_taxonomy_id`, `median_genome_size` cast from STRING to DOUBLE in `gtdb_metadata`), plot phylum heatmap. Writes `data/species_defense_matrix.tsv.gz`, `figures/system_prevalence_by_phylum.png`. Runtime: ~30 s.
4. `03_prophage_burden.ipynb` — Import `projects/prophage_ecology/src/prophage_utils.py` via `sys.path`, run the 5,377-char prophage OR-chain query against `eggnog_mapper_annotations`, classify hits into 7 modules in Python. Writes `data/species_prophage_burden.tsv.gz`. Runtime: ~35 min (Python `apply` over ~4M hits is the bottleneck).
5. `04_arms_race.ipynb` — H1a test: marginal + partial Spearman, negative-binomial GLM (`statsmodels`), per-phylum consistency. Writes `data/arms_race_*.tsv`, `figures/arms_race_scatter.png`, `figures/partial_correlation_barplot.png`. Runtime: <30 s.
6. `05_defense_syndromes.ipynb` — H1b test: 28 pairs × 1,000 phylum-stratified column-permutation null; Fisher exact, BH-FDR. Writes `data/syndrome_pairs.tsv`, `figures/syndrome_heatmap.png`, `figures/syndrome_network.png`. Runtime: ~2 min (dominated by the permutation loop).
7. `06_accessory_enrichment.ipynb` — H1c test: per-system χ² vs pangenome-wide core/aux/singleton background. Writes `data/accessory_enrichment.tsv`, `figures/core_vs_accessory_by_system.png`. Runtime: <30 s.

Every artifact under `data/` and `figures/` is deterministic given the same BERDL snapshot and the fixed random seed `20260715` used in NB05.

### Version pinning notes

- BERDL collection: `kbase_ke_pangenome` was queried as of 2026-07-15/16. Row counts (`gene_cluster` 132,531,501; `interproscan_domains` 833M) are recorded in `data/detection_feasibility.csv` and NB00 outputs for future comparison.
- Prophage classifier: `projects/prophage_ecology/src/prophage_utils.py` at HEAD of the `main` branch as of 2026-07-15.

## Authors
- Justin Reese ([0000-0002-2170-2250](https://orcid.org/0000-0002-2170-2250)), LBL
