# Structural Coverage Gap by Biome

## Research Question

Where does experimental (PDB) and high-confidence predicted (AlphaFold) structural coverage of the environmental microbiome fall short, once we account for biome, taxonomy, and function — and which biome × functional-category cells are the largest gaps?

## Status

In progress — scaffolding created 2026-07-24.

## Overview

The BERDL pangenome links 132.5M gene clusters to UniProt via `bakta_annotations.uniref100`. That same UniProt key joins into (a) `kescience_pdb.pdb_uniprot_mapping` (967K SIFTS chain-to-UniProt rows across 250K experimental structures) and (b) `kescience_alphafold.alphafold_entries` + `alphafold_msa_depths` (241M predicted structures with confidence proxies). Meanwhile `genome_environment.csv` (293K genomes) carries `compartment` and `env_broad_scale` labels for each genome.

This project intersects those layers to produce a **biome × functional-category coverage matrix** — for each cell, what fraction of clusters have a direct PDB match (≥95% identity), a PDB homolog (30–95%), an AF-confident model (MSA depth ≥ 300), an AF-low-confidence model, or nothing? The output is a prioritized gap list of biome-relevant, functionally-annotated clusters with no structural evidence — a crystallography wishlist grounded in environmental relevance.

## Key databases

- `kbase_ke_pangenome` — `gene_cluster`, `bakta_annotations`, `interproscan_domains`, `marker_gene_clusters`
- `kescience_pdb` — `pdb_entries`, `pdb_uniprot_mapping`, `pdb_validation`
- `kescience_alphafold` — `alphafold_entries`, `alphafold_msa_depths`
- Local CSVs from `plant_microbiome_ecotypes` — `genome_environment.csv`, `ncbi_env_pivot.csv`, `bacdive_isolation.csv`

## Quick Links

- [Research Plan](RESEARCH_PLAN.md) — hypotheses, join strategy, phases
- [References](references.md) — literature and prior BERIL projects

## Relationship to prior work

- **Distinct from `alphafold_msa_annotation`**: that project asked whether AF confidence is lower for accessory genes (yes, produced 415K "paradox proteins"). It never touched PDB and never stratified by biome. This project uses PDB as the coverage denominator and biome as the primary stratifier.
- **Distinct from `truly_dark_genes`**: that project ranks proteins by annotation depth (hypothetical vs. characterized). This project ranks by *structural evidence tier*, independent of textual annotation.
- **Complementary to `functional_dark_matter`**: which has biogeographic profiles but no PDB/AF cross-link.

## Reproduction

Prerequisites: BERDL JupyterHub (Spark) for NB01–NB02; local Python 3.10+ for NB03–NB04. See `requirements.txt`.

Notebooks in order:
1. `NB01_coverage_extraction.ipynb` — Spark; extract per-cluster PDB + AF tier assignment
2. `NB02_biome_stratification.ipynb` — Spark; join to genome_environment, aggregate by biome × function
3. `NB03_coverage_model.ipynb` — local; logistic regression, plots, biome gap rankings
4. `NB04_priority_gap_list.ipynb` — local; top-100 per biome with per-candidate functional annotation

## Authors

- Justin Reese | ORCID: 0000-0002-2170-2250 | Lawrence Berkeley National Laboratory
