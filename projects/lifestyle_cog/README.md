# Lifestyle-Based COG Stratification

## Research Question

How does bacterial lifestyle (free-living vs host-associated) affect pangenome functional composition at the COG category level?

## Hypothesis

- **H0**: COG enrichment patterns in core vs accessory genes are independent of bacterial lifestyle
- **H1**: Host-associated bacteria show higher defense (V) enrichment in accessory genes; free-living bacteria show greater metabolic (E, G, C, P, I) diversity in accessory genes; host-associated bacteria have smaller core genome fractions

## Approach

1. Classify genomes by lifestyle using NCBI BioSample environmental metadata (`ncbi_env` table)
2. Aggregate to species-level lifestyle assignments
3. Compare COG functional enrichment patterns (core vs accessory) between lifestyle groups
4. Control for phylogeny by stratifying within phyla
5. Statistical testing with multiple comparison correction

## Data Sources

- **Database**: `kbase_ke_pangenome` on BERDL Delta Lakehouse
- **Tables**:
  - `ncbi_env` — Environmental metadata (EAV format, 4.1M rows)
  - `genome` — Genome metadata (293K rows)
  - `gene_cluster` — Core/accessory classification (132M rows)
  - `eggnog_mapper_annotations` — COG functional annotations (93M rows)
  - `pangenome` — Per-species pangenome statistics (27K rows)
  - `gtdb_species_clade` — Taxonomy (27K rows)

## Status

Completed — all three pre-registered hypotheses (defense V accessory-enrichment in host-associated, metabolism E/G/C/P/I accessory-enrichment in free-living, host smaller core fraction) supported across 2,529 species in 10 phyla; S (function unknown) is the most lifestyle-discriminating category (LARGE effect, r=−0.57).

## Key Findings

All three pre-registered hypotheses supported across 2,529 species (1,705 host-associated, 824 free-living) in 10 phyla.

- **H1 SUPPORTED**: Defense (V) more accessory-enriched in host-associated species (median 1.09 vs 0.77, p_adj = 2.3 × 10⁻²¹; 8/10 phyla agree).
- **H2 SUPPORTED**: Metabolic categories (E, G, C, P, I) more accessory-enriched in free-living species (all p_adj < 3 × 10⁻²⁴; 9/10 phyla agree for most).
- **H3 SUPPORTED**: Host-associated species have smaller median core fraction (0.255 vs 0.320, p = 1.3 × 10⁻²³; 6/8 phyla agree).
- **Striking unexpected finding**: S (function unknown) is the single most lifestyle-discriminating category (p_adj = 7.8 × 10⁻¹¹⁷). Host accessory genomes carry ~23% uncharacterized vs ~17% in free-living.

See [REPORT.md](REPORT.md) for full results, interpretation, and literature context.

## Notebooks

| Notebook | Purpose |
|----------|---------|
| [`01_data_exploration.ipynb`](notebooks/01_data_exploration.ipynb) | Assess ncbi_env coverage, build lifestyle classifier, identify target species |
| [`02_cog_enrichment.ipynb`](notebooks/02_cog_enrichment.ipynb) | COG enrichment analysis (core vs accessory) by lifestyle group, hypothesis tests |
| [`03_phylogenetic_controls.ipynb`](notebooks/03_phylogenetic_controls.ipynb) | Phylum-stratified controls, confounder analysis, publication figures |

## Visualizations

| Figure | Description |
|--------|-------------|
| `figures/lifestyle_cog_heatmap.png` | Side-by-side heatmap of median COG enrichment by lifestyle with significance markers |
| `figures/enrichment_heatmap.png` | Per-species enrichment matrix clustered by lifestyle |
| `figures/phylum_stratified.png` | Within-phylum host-vs-free comparisons across the 10 testable phyla |
| `figures/core_fraction_comparison.png` | Distribution of core fraction by lifestyle |

## Data Files

| File | Description |
|------|-------------|
| `data/species_lifestyle_classification.csv` | Species-level lifestyle assignments |
| `data/cog_enrichment_by_lifestyle.csv` | COG enrichment scores by lifestyle group |
| `data/cog_lifestyle_stats.csv` | Per-COG Mann-Whitney + BH-FDR (24 categories) |
| `data/phylum_within_stats.csv` | Per-phylum × COG within-phylum tests with BH correction |
| `data/review_addenda/effect_sizes.csv` | Rank-biserial / Cliff's δ effect sizes |
| `data/review_addenda/log_ratio_sensitivity.csv` | Pseudocount sensitivity (log₂ ratio formulation) |
| `data/review_addenda/phylum_within_bh.csv` | Same as `phylum_within_stats.csv` (computed by `src/review_addenda.py` for self-contained reproduction) |
| `data/review_addenda/annotation_coverage_*.csv` | Per-species COG-annotation rate by lifestyle |

## Related Projects

- `projects/cog_analysis/` — COG functional category analysis (core vs accessory)
- `projects/pangenome_pathway_geography/` — Pangenome openness and biogeography

## Reproduction

### Prerequisites
- Access to BERDL JupyterHub (`hub.berdl.kbase.us`) with read access to the `kbase_ke_pangenome` database
- Python environment with packages in `requirements.txt`. On JupyterHub the kernel already includes pyspark/scipy/pandas/numpy/matplotlib/seaborn; locally `pip install -r requirements.txt` after activating `.venv-berdl`.
- For the off-cluster path: working SSH tunnels (1337/1338) and pproxy (8123) per `scripts/berdl_env.py --check`.

### Steps and runtime

| Step | Where | Approx. runtime |
|---|---|---|
| **NB01 `01_data_exploration.ipynb`** — full notebook is Spark-bound (queries `ncbi_env`, `genome`, joins; writes `data/species_lifestyle_classification.csv`) | BERDL JupyterHub | ~5-10 min |
| **NB02 `02_cog_enrichment.ipynb` cells 1-4** — Spark per-species batched query (`gene_cluster` ⨝ `eggnog_mapper_annotations`, BATCH_SIZE=20, ~127 batches over 2,529 species; writes `data/cog_raw_counts.csv` internally) | BERDL JupyterHub | ~30-60 min (heaviest step) |
| **NB02 cells 5+** — pandas/scipy stats and figure generation; runs on cached CSVs | Local or JupyterHub | <2 min |
| **NB03 `03_phylogenetic_controls.ipynb`** — entirely pandas/scipy on cached CSVs from NB01 and NB02 | Local or JupyterHub | <2 min |
| **`src/review_addenda.py`** — post-hoc rank-biserial / phylum-BH / log-ratio sensitivity, all on cached CSVs | Local or JupyterHub | <30 s |
| **`src/annotation_coverage.py`** — Spark-bound; per-species annotation rate against `gene_cluster` ⨝ `eggnog_mapper_annotations` | BERDL JupyterHub | ~30-60 min |

### Quick-start (full reproduction)
1. Upload `notebooks/` and `src/` to BERDL JupyterHub
2. Run NB01 → NB02 → NB03 in order on JupyterHub
3. Run `python src/review_addenda.py` and `python src/annotation_coverage.py` for the post-review addenda
4. All outputs land under `data/` (CSVs) and `figures/` (PNGs)

### Working with cached results
If you only want to reproduce statistics or figures from existing CSVs without re-running the Spark steps, NB03 and `src/review_addenda.py` can run locally on the committed CSVs.

## Authors

- Justin Reese, Lawrence Berkeley National Laboratory, ORCID 0000-0002-2170-2250

## Future Directions

See [REPORT.md § Future Directions](REPORT.md#future-directions) for the full list. Highlights:

1. Decompose the V signal by defense-system class (CRISPR-Cas, R-M, T-A) using `defense-finder` / `padloc`.
2. Re-annotate host-associated accessory S-class genes with bakta v1.12.0 to separate annotation-lag from genuine novelty.
3. Phylogenetically-controlled GLM at genus/family resolution to formalize H1/H2/H3 effect sizes.
4. Three-way classification (free-living / commensal / pathogen) to separate phage-pressure from pathogen-specific selection.
