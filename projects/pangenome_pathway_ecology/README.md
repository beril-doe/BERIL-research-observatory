# Pangenome Openness, Metabolic Pathways, and Phylogenetic Distances

## Research Question

How do pangenome characteristics (open vs. closed) correlate with metabolic pathway completeness, phylogenetic distances, and species ecology?

## Status

Completed — Open pangenomes are associated with fewer complete metabolic pathways in the sequenced GTDB cohort; the pattern is phylogenetically structured and attenuates in host-associated genera.

## Overview

This project investigates whether pangenome openness correlates with GapMind metabolic pathway completeness and phylogenetic/structural distances from AlphaEarth embeddings. It tests whether open pangenomes indicate generalist species with broader niche adaptation and greater metabolic pathway diversity, while closed pangenomes indicate specialists with conserved core pathways. The analysis controls for phylogenetic signal using independent contrasts or PGLS.

## Quick Links

- [Research Plan](RESEARCH_PLAN.md) — Detailed hypothesis, approach, query strategy
- [Report](REPORT.md) — Findings, interpretation, supporting evidence

## Data Collections

This project uses data from `kbase_ke_pangenome` (pangenome metrics, GapMind pathways, AlphaEarth embeddings, genome metadata, NCBI environment annotations).

## Reproduction

### Requirements
- **NB01–NB03**: BERDL JupyterHub with Spark access (`kbase_ke_pangenome` collection)
- **NB04**: Local Python 3.9+ with pandas, numpy, scipy, matplotlib, seaborn

### Runtime estimates

The current pipeline is NB03 → NB04. NB01/NB02 are historical (v1 exploration, superseded).

| Notebook | Environment | Approximate runtime |
|----------|------------|-------------------|
| 03_data_integration | Spark (JupyterHub) | ~15 min (joins across 5 tables) |
| 04_statistical_analysis | Local (pandas) | ~1 min (from cached CSVs) |

### Quick start (from cached data)
If `data/species_integrated.csv` already exists, NB04 can run locally without Spark:
```
cd notebooks/
jupyter notebook 04_statistical_analysis.ipynb
# or: python 04_run_analysis.py
```

## Authors
- **William J. Riehl** | ORCID: 0000-0002-3405-2744 | Author
