---
type: "Summary"
description: "Tests whether bacterial co-fitness predicts pangenome co-inheritance."
doc_type: short
full_text: "sources/cofitness_coinheritance__REPORT.md"
---

# Co-fitness and Co-inheritance in Bacterial Pangenomes

## Overview

This report tests whether laboratory-measured gene co-fitness predicts gene co-occurrence across bacterial pangenomes. It compares Fitness Browser co-fit pairs with prevalence-matched random pairs across 9 organisms, and evaluates whether multi-gene ICA fitness modules show stronger co-inheritance than individual gene pairs. The analysis connects [[concepts/cofitness-networks]] with [[concepts/gene-co-inheritance]] and [[concepts/pangenome-integration]].

## Key Findings

- Pairwise co-fitness was a weak but generally positive predictor of co-occurrence. Across 2,253,491 cofit pairs and 22,534,910 random pairs, the aggregate mean phi was 0.092 for cofit pairs versus 0.089 for random pairs, giving delta phi = +0.003 (Mann–Whitney p = 1.66e-29).
- Seven of nine organisms had positive cofit-versus-random effects, and eight of nine were individually significant at p < 0.05. However, the Wilcoxon signed-rank test across organisms was not significant (W = 9, p = 0.13), reflecting substantial inter-organism variation.
- The strongest pairwise signal occurred in Ddia6719 (delta = +0.093), followed by pseudo3_N2E3 (+0.026). Korea showed a negative effect (-0.042), attributed to 95.2% of cofit pairs having undefined phi because both genes were universally prevalent.
- Genomic adjacency was unlikely to explain the result: only 0.7% of cofit pairs were within five genes, and excluding adjacent pairs did not change the overall pattern.
- ICA modules showed substantially stronger co-inheritance than pairwise cofit relationships. Across 195 modules in 6 organisms, mean phi was 0.229 versus 0.177 for prevalence-matched null sets (delta = +0.053); 51/195 modules were significant at p < 0.05 and 21/195 remained significant after FDR correction.
- Accessory modules had the strongest signal, with mean delta phi = +0.108, 8/11 significant at p < 0.05, and 4/11 significant at q < 0.05. Core modules had delta = +0.059, while mixed modules had delta = +0.031. This supports [[concepts/core-accessory-resistance]] and coordinated multi-gene functional modules as important units of co-inheritance.
- Co-fitness strength itself weakly anti-correlated with phi (Spearman rho = -0.109, p < 1e-300), likely because strong cofitness pairs are enriched for core genes near universal prevalence. This is described as a [[concepts/prevalence-ceiling]] rather than evidence against functional coupling.
- Phylogenetic structure remained important: cofit-pair phi averaged 0.102 among near genomes and 0.067 among medium-distance genomes. Limited representation of far genomes prevented complete separation of functional coupling from shared ancestry, motivating [[concepts/phylogenetic-confounding]].

## Interpretation

The report concludes that pairwise laboratory co-fitness explains only a small portion of natural pangenome co-inheritance patterns. The stronger module-level signal suggests that coordinated multi-gene regulation, rather than isolated pairwise functional similarity, may better represent the selective or mobile units that travel together through bacterial populations. This interpretation is consistent with the report's connection to gene mobility, co-regulation, and [[concepts/pangenome-integration]].

The result is strongest in organisms with enough accessory variation to provide presence/absence variance. Near-clonal organisms can still reveal co-inheritance when accessory variation exists, but their high baseline phi values make absolute co-occurrence values harder to interpret.

## Scope and Limitations

- Most Fitness Browser genes map to core clusters with prevalence above 95%, limiting phi-based detection because near-universal genes have little variance.
- Ralstonia UW163 and Ralstonia GMI1000 were excluded from the primary analysis because they had no available Fitness Browser co-fitness data, despite having pangenome and phylogenetic data.
- Phylogenetic stratification was incomplete because most organisms lacked genomes in the far-distance stratum.
- Pairwise co-fitness and ICA modules measure different biological structures; the stronger module result may reflect the relevance of coordinated regulation or multi-gene units.
- Korea's negative pairwise effect is considered statistical noise from its small effective sample after excluding undefined phi values, not a biological anti-association signal.

## Future Directions

1. Restrict pairwise analyses to auxiliary gene clusters below 95% prevalence.
2. Calculate co-fitness directly from raw `genefitness` data for Ralstonia and other organisms lacking precomputed cofit values.
3. Repair reference-genome mapping to improve phylogenetic distance control.
4. Build module co-transfer networks and test cross-module inheritance relationships.
5. Expand analysis to organisms with more than 30% auxiliary gene content and available co-fitness measurements.

## Data and Reproducibility

The analysis used Fitness Browser co-fitness pairs, KBase pangenome presence matrices, phylogenetic distances, the Fitness Browser–pangenome gene-link table, ICA fitness modules, module-conservation statistics, and SEED annotations. The workflow comprises Spark extraction, local phi and prevalence-matching analyses, module-level permutation tests, and cross-organism meta-analysis in notebooks `01_data_extraction.ipynb` through `04_cross_organism.ipynb`.

## Related Concepts
- [[concepts/evidence-triangulation]]
- [[concepts/method-concordance]]
- [[concepts/organism-specificity]]
- [[concepts/shared-dispensability]]
- [[concepts/resistance-islands]]

## Entities
- [[entities/random-barcode-transposon-sequencing]]
