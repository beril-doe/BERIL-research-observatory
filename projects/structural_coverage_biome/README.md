# Structural Coverage Gap by Biome

## Research Question

Where does experimental (PDB) and high-confidence predicted (AlphaFold) structural coverage of the environmental microbiome fall short, once we account for biome, taxonomy, and function — and which biome × functional-category cells are the largest gaps?

## Status

**Analysis complete** — extraction, biome stratification, statistics, figures, and REPORT all done 2026-07-24. NB04 (per-Pfam curated priority list) is deferred.

## Headline Finding

H1 (environmental > host coverage gap) is **rejected on marginal rates** but **confirmed within core clusters**: freshwater 18.0% no-Pfam > host_urogenital 11.3% (monotonic environmental > host gradient among is_core=True). The marginal-rate confound is pangenome depth — host biomes are 10–100× larger and skew accessory. See REPORT.md for full findings.

## Overview

**As-executed pipeline (revised from v0 scaffold — see RESEARCH_PLAN.md v1):**

The pangenome is joined to the PDB via **Pfam family**, not UniRef100 identity: `kescience_pdb.pdb_pfam` (990K rows: PDB × chain × UniProt × Pfam) supplies "which Pfams have PDB structure"; `kbase_ke_pangenome.interproscan_domains` filtered to `analysis='Pfam'` (preferred over `bakta_pfam_domains`, which silently drops half of pangenome Pfams) supplies each cluster's Pfam set. Per-cluster tier is `no_pfam_annotation` / `pfam_no_covered` / `pfam_partial_covered` / `pfam_all_covered`.

Biome comes from `gtdb_metadata.ncbi_isolation_source` via a 17-label keyword classifier (host_gut, soil, marine, freshwater, subsurface_extreme, etc.), rolled up to species via majority vote. This rebuild was necessary because the `genome_environment.csv` referenced in v0 lives in another user's home directory not accessible here.

## Key databases (as-executed)

- `kescience_pdb.pdb_pfam` — 990K rows: PDB × chain × UniProt × Pfam (the canonical "PDB has structure of this family" source)
- `kbase_ke_pangenome.interproscan_domains` — 833M rows; filter `analysis='Pfam'` for pangenome Pfam annotations
- `kbase_ke_pangenome.gene_cluster` — 132.4M rows: cluster → species + is_core/is_auxiliary/is_singleton
- `kbase_ke_pangenome.genome` — 226K rows: genome → gtdb species
- `kbase_ke_pangenome.gtdb_metadata` — 293K rows: genome → `ncbi_isolation_source` (biome source)

## Quick Links

- [Research Plan](RESEARCH_PLAN.md) — hypotheses, join strategy, phases
- [References](references.md) — literature and prior BERIL projects

## Relationship to prior work

- **Distinct from `alphafold_msa_annotation`**: that project asked whether AF confidence is lower for accessory genes (yes, produced 415K "paradox proteins"). It never touched PDB and never stratified by biome. This project uses PDB as the coverage denominator and biome as the primary stratifier.
- **Distinct from `truly_dark_genes`**: that project ranks proteins by annotation depth (hypothetical vs. characterized). This project ranks by *structural evidence tier*, independent of textual annotation.
- **Complementary to `functional_dark_matter`**: which has biogeographic profiles but no PDB/AF cross-link.

## Reproduction

Prerequisites: on-cluster Spark (any BERDL JupyterHub node) for step 1; local Python 3.10+ for step 2. See `requirements.txt`.

```bash
python scripts/01_extract_and_stratify.py   # Spark, ~10 min → writes data/*.csv
python scripts/02_analysis_and_figures.py   # local, ~30 s   → writes data/*.csv + figures/*.png
```

Notebooks in `notebooks/` mirror the pipeline for interactive exploration. Interpretation lives in `REPORT.md`.

## Authors

- Justin Reese | ORCID: 0000-0002-2170-2250 | Lawrence Berkeley National Laboratory
