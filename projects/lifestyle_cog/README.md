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

Analysis — report drafted, awaiting `/berdl-review` and `/submit`.

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

## Related Projects

- `projects/cog_analysis/` — COG functional category analysis (core vs accessory)
- `projects/pangenome_pathway_geography/` — Pangenome openness and biogeography

## Reproduction

1. Upload notebooks to BERDL JupyterHub
2. Run notebooks 01-03 in order
3. Outputs saved to `data/` and `figures/`

## Authors

- Justin Reese, Lawrence Berkeley National Laboratory, ORCID 0000-0002-2170-2250

## Future Directions

See [REPORT.md § Future Directions](REPORT.md#future-directions) for the full list. Highlights:

1. Decompose the V signal by defense-system class (CRISPR-Cas, R-M, T-A) using `defense-finder` / `padloc`.
2. Re-annotate host-associated accessory S-class genes with bakta v1.12.0 to separate annotation-lag from genuine novelty.
3. Phylogenetically-controlled GLM at genus/family resolution to formalize H1/H2/H3 effect sizes.
4. Three-way classification (free-living / commensal / pathogen) to separate phage-pressure from pathogen-specific selection.
