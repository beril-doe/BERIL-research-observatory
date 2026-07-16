# Pan-Bacterial Anti-Phage Defense Arsenal

## Research Question
How are the major anti-phage defense systems (CRISPR-Cas, restriction-modification, abortive infection, CBASS, Gabija, Retron, Thoeris, DISARM, Wadjet, and others) distributed across the 293K-genome BERDL pangenome, and does defense-system repertoire size scale with prophage burden — as the bacterial-phage arms race hypothesis predicts?

## Status
Reviewed — REVIEW_1.md drafted; awaiting /submit.

## Overview
Surveys seven of the major anti-phage defense system families (CRISPR-Cas, restriction-modification, CBASS, Gabija, Retron, BREX, DISARM) across the BERDL pangenome (293K genomes, 27,690 species). Tests three linked hypotheses: (1) species-level defense-system count scales with prophage burden after controlling for genome size and phylum (the coevolutionary arms race), (2) specific system combinations co-occur beyond phylogenetic expectation, defining "defense syndromes" consistent with mobile-defense-island transfer, and (3) defense systems are enriched in the accessory pangenome. Detection uses `kbase_ke_pangenome.interproscan_domains` (primary, Pfam accession-based) with `eggnog_mapper_annotations` for R-M and CRISPR description-based confirmation. Prophage burden is re-derived using the eggNOG-description classifier from `projects/prophage_ecology/src/prophage_utils.py`.

**Headline results**: H1a supported (partial ρ = 0.30, p = 1.6e-153; universal across 9 major phyla), H1b supported massively (27 of 28 defense-system pairs are positive syndromes at BH-FDR q<0.05, with R-M Type II × Gabija OR = 24 as the strongest and novel finding), H1c supported for 6 of 7 systems (DISARM detection artefact flagged).

## Quick Links
- [Research Plan](RESEARCH_PLAN.md) — hypotheses, detection rules, query strategy, analysis plan
- [Report](REPORT.md) — findings, interpretation, supporting evidence

## Reproduction
*TBD — add prerequisites and step-by-step instructions after analysis is complete.*

## Authors
- Justin Reese ([0000-0002-2170-2250](https://orcid.org/0000-0002-2170-2250)), LBL
