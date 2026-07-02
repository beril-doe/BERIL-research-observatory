# Toxin-Antitoxin Systems Across Bacterial Lifestyles

## Research Question

How does bacterial lifestyle (host-associated vs free-living) shape the carriage, family composition, and pangenome partitioning of Type II toxin-antitoxin (TA) loci across the BERDL pangenome?

## Hypotheses

- **H1**: TA loci are overwhelmingly accessory rather than core (mirroring COG-V and other defense/mobile categories).
- **H2**: Host-associated species carry FEWER TA loci per Mb than free-living species, consistent with reductive evolution and reduced phage predation in stable host environments.
- **H3**: TA-locus family composition differs by lifestyle — free-living species carry a broader diversity of TA families; host-associated species carriage is biased toward specific families (e.g., HipA-like persistence).

## Approach

1. Enumerate Type II TA Pfam signatures from TADB / literature (PF06769 RelE, PF07803 HipA, PF01850 VapC, PF04552 MazF, PF07927 HicA, and ~35 more).
2. Query `eggnog_mapper_annotations` for genes carrying these Pfam accessions.
3. Reuse the `lifestyle_cog` cohort (2,529 species, 1,705 host-associated + 824 free-living, 10 phyla) for one-shot lifestyle labels.
4. Test H1–H3 with pre-registered statistics (rank tests, effect sizes, BH-FDR), phylum-stratified controls, and genome-size normalization.

## Data Sources

- **Database**: `kbase_ke_pangenome` on the BERDL Delta Lakehouse
- **Tables**:
  - `eggnog_mapper_annotations` — Pfam annotations per gene cluster (93M rows)
  - `gene_cluster` — Core/accessory/singleton status per gene cluster (132M rows)
  - `genome` — Genome metadata including size (293K rows)
  - `pangenome` — Per-species gene-cluster counts (27K rows)
  - `gtdb_species_clade` — Taxonomy for phylogenetic controls (27K rows)
- **Lifestyle labels**: Reused from `projects/lifestyle_cog/data/species_lifestyle.tsv` (already computed).

## Status

**Analysis complete.** See [REPORT.md](REPORT.md) for full findings.

- **H1 STRONGLY SUPPORTED** (LARGE effect): TA loci are predominantly accessory. Paired Wilcoxon p = 2 × 10⁻¹⁵⁵; rank-biserial r = +0.625; 10/11 phyla preserve direction.
- **H2 REJECTED — direction OPPOSITE prediction**: host-associated species carry MORE TA per Mb (6.80 vs 5.21), not fewer. 7/9 testable phyla preserve host-higher direction.
- **H3 SUPPORTED**: 10/10 families differ at BH-FDR < 0.05. Two coherent ecological polarities: **RelBE host-enriched** (r = −0.41, LARGE), **VapBC free-enriched** (r = +0.32, LARGE).

## Novelty Check

Verified 2026-07-02: no branch (local, `origin/*`, or `justaddcoffee/*`), no project directory, no research plan on `origin/main`, and no `docs/research_ideas.md` entry targets TA systems as a study focus. `snipe_defense_system` covers a single defense system (SNIPE); `functional_dark_matter` and `costly_dispensable_genes` mention "antitoxin" only as one keyword in broader mobile/defense filters.

## Related Work in the Observatory

- **`lifestyle_cog`** — Establishes the host/free-living cohort and observed a defense (V) accessory-enrichment gradient this project drills into mechanistically.
- **`snipe_defense_system`** — Complementary defense-system perspective (single system, cross-pangenome).
- **`costly_dispensable_genes`** — Overlaps in mobile-element ecology framing.

## Reproduction

**Prerequisites**: Python 3.10+, pandas, numpy, scipy, matplotlib, seaborn, statsmodels. BERDL Spark Connect for data extraction.

```bash
cd projects/toxin_antitoxin_lifestyle
pip install -r requirements.txt
# Step 1: Extract TA-Pfam hits (BERDL required)
jupyter nbconvert --to notebook --execute --inplace notebooks/NB01_ta_pfam_extraction.ipynb
# Step 2: Lifestyle stratification and hypothesis tests (local)
jupyter nbconvert --to notebook --execute --inplace notebooks/NB02_lifestyle_partition.ipynb
# Step 3: Family-composition and phylum-stratified controls
jupyter nbconvert --to notebook --execute --inplace notebooks/NB03_family_composition.ipynb
```

## Author

Justin Reese ([0000-0002-2170-2250](https://orcid.org/0000-0002-2170-2250)), LBNL.
