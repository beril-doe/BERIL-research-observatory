# Pan-Bacterial Anti-Phage Defense Arsenal

## Research Question
How are the major anti-phage defense systems (CRISPR-Cas, restriction-modification, abortive infection, CBASS, Gabija, Retron, Thoeris, DISARM, Wadjet, and others) distributed across the 293K-genome BERDL pangenome, and does defense-system repertoire size scale with prophage burden — as the bacterial-phage arms race hypothesis predicts?

## Status
Proposed — research plan written, awaiting analysis.

## Overview
This project surveys seven of the major anti-phage defense system families (CRISPR-Cas, restriction-modification, CBASS, Gabija, Retron, BREX, DISARM) across the BERDL pangenome (293K genomes, 27,690 species). We test three linked hypotheses: (1) species-level defense-system count scales with prophage burden after controlling for genome size and phylum (the coevolutionary arms race), (2) specific system combinations co-occur beyond phylogenetic expectation, defining "defense syndromes" consistent with mobile-defense-island transfer, and (3) defense systems are enriched in the accessory pangenome (`is_auxiliary`/`is_singleton`). Detection uses `interproscan_domains` (primary, Pfam accession-based; validated to detect all 7 systems in Phase A) with `eggnog_mapper_annotations` for R-M and CRISPR description-based confirmation. Prophage burden is re-derived using the eggNOG-description classifier from `projects/prophage_ecology/src/prophage_utils.py`.

## Quick Links
- [Research Plan](RESEARCH_PLAN.md) — hypotheses, detection rules, query strategy, analysis plan
- [Report](REPORT.md) — TBD

## Reproduction
*TBD — add prerequisites and step-by-step instructions after analysis is complete.*

## Authors
- Justin Reese ([0000-0002-2170-2250](https://orcid.org/0000-0002-2170-2250)), LBL
