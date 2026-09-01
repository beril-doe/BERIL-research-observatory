---
type: "Concept"
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/respiratory_chain_wiring__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md"]
description: "Ecological divergence expressed through differences in resource-use pathways."
---

# Metabolic Niche Partitioning

## Definition

**Metabolic niche partitioning** is the differentiation of ecological roles through systematic differences in the carbon sources and metabolic pathways available to organisms occupying distinct environments. In the [[summaries/pseudomonas_carbon_ecology__REPORT]], this concept is evaluated by comparing pathway-completeness profiles across [[entities/pseudomonas]] species and ecological categories. [src: pseudomonas_carbon_ecology]

Metabolic profiles can therefore serve as indicators of ecological specialization, but pathway presence measures **capability**, not necessarily pathway activity or growth kinetics in situ. The report’s environmental predictions should consequently be interpreted as evidence of ecological association rather than direct proof that a pathway is active in a particular environment. [src: pseudomonas_carbon_ecology]

## Evidence from *Pseudomonas*

The report analyzed 62 [[entities/gapmind]] carbon pathways across 12,732 genomes and 433 *Pseudomonas* species clades. [src: pseudomonas_carbon_ecology] Species-level pathway profiles were significantly associated with environment among 54 free-living and plant-associated species: a 999-permutation PERMANOVA-like test produced **p = 0.006**, with between-group mean distance of **2.054** and within-group mean distance of **1.890**. [src: pseudomonas_carbon_ecology]

A Random Forest classifier distinguishing soil, freshwater, plant-surface, and rhizosphere species achieved balanced accuracy of **0.408 +/- 0.169**, compared with a **0.250** chance baseline. [src: pseudomonas_carbon_ecology] The result provides moderate evidence that carbon pathway composition contains ecological information, while the limited accuracy shows that the profiles do not fully resolve fine-grained environmental niches. [src: pseudomonas_carbon_ecology]

The pathways with the greatest classifier importance were D-serine, arabinose, rhamnose, fucose, and xylose, with importances of **0.132**, **0.094**, **0.086**, **0.085**, and **0.070**, respectively. [src: pseudomonas_carbon_ecology] Several of these compounds are associated with plant-derived carbohydrates or plant and animal glycans, providing a mechanistic basis for testing whether plant-associated environments select for broader access to these substrates. [src: pseudomonas_carbon_ecology]

## Phylogenetic structure versus ecological differentiation

The strongest source of pathway variation was not lifestyle alone, but the deep division between *Pseudomonas* sensu stricto, including the *P. aeruginosa* group, and *Pseudomonas_E*, including the *P. fluorescens/putida* group. [src: pseudomonas_carbon_ecology] PCA of all species primarily separated these two subgenera, while free-living, host-associated, and plant-associated categories substantially overlapped within *Pseudomonas_E*. [src: pseudomonas_carbon_ecology]

This creates a central [[concepts/phylogenetic-confounding]] problem: an apparent ecological association can arise because environments are unevenly represented across lineages. [src: pseudomonas_carbon_ecology] The report therefore supports metabolic niche partitioning most strongly as a combination of lineage-level metabolic divergence and weaker within-subgenus ecological differentiation, rather than as a clean lifestyle-specific effect independent of phylogeny. [src: pseudomonas_carbon_ecology]

## Host-associated streamlining as niche differentiation

The *P. aeruginosa* group showed marked loss of pathways for plant-derived sugars and sugar alcohols relative to *Pseudomonas_E*. [src: pseudomonas_carbon_ecology] Among the largest differences, xylose completeness was **0.0%** versus **74.4%**, arabinose was **0.0%** versus **62.6%**, galacturonate was **28.6%** versus **88.4%**, and myo-inositol was **0.0%** versus **58.8%** in the two groups, respectively. [src: pseudomonas_carbon_ecology]

Ribose, mannitol, and sorbitol also differed by **64.2**, **51.6**, and **51.5 percentage points**, respectively. [src: pseudomonas_carbon_ecology] In contrast, amino-acid pathways and core organic-acid pathways remained near-universal (>99%) in both groups. [src: pseudomonas_carbon_ecology]

This pattern is consistent with [[concepts/metabolic-streamlining]]: a host-associated lineage may retain pathways relevant to host nutrients while losing capabilities associated with plant or soil carbon sources. [src: pseudomonas_carbon_ecology] Because the analysis is based on genome-derived pathway predictions rather than direct environmental flux measurements, the nutritional interpretation is supported but should not be treated as a direct demonstration of substrate use in host environments. [src: pseudomonas_carbon_ecology]

Free-living and plant-associated species also showed greater pathway richness than host-associated species, with median richness of **57** versus **55** pathways complete in more than half of genomes. [src: pseudomonas_carbon_ecology] Within *Pseudomonas_E*, mean richness was **56.7** in plant-associated species, **56.1** in free-living species, and **55.2** in host-associated species. [src: pseudomonas_carbon_ecology]

## What the evidence establishes

- Carbon pathway profiles are non-randomly associated with environment among the analyzed free-living and plant-associated species. [src: pseudomonas_carbon_ecology]
- The ecological signal is statistically detectable but has modest predictive strength when using only 62 GapMind pathways. [src: pseudomonas_carbon_ecology]
- The dominant variation reflects subgenus-level divergence, especially the loss of plant-associated sugar pathways in the *P. aeruginosa* group. [src: pseudomonas_carbon_ecology]
- Within *Pseudomonas_E*, lifestyle-associated differences are comparatively subtle and overlapping. [src: pseudomonas_carbon_ecology]
- Species-level pathway presence does not establish strain-level activity, realized resource use, or competitive outcomes in a specific environment. [src: pseudomonas_carbon_ecology]

These boundaries connect metabolic niche partitioning to [[concepts/capability-versus-kinetics]], [[concepts/pathway-completeness]], [[concepts/metabolic-ecotypes]], and [[concepts/phenotype-resolution-matching]].

## Tensions

### Ecological signal versus phylogenetic dominance

One result supports ecological partitioning: pathway profiles differed significantly among environment categories, with **p = 0.006**. [src: pseudomonas_carbon_ecology] A second result limits the interpretation: PCA was dominated by the *Pseudomonas* sensu stricto–*Pseudomonas_E* split, and lifestyle categories overlapped within *Pseudomonas_E*. [src: pseudomonas_carbon_ecology] The unresolved question is whether environment-associated pathway differences remain after explicitly controlling for phylogenetic relatedness. [src: pseudomonas_carbon_ecology]

### Broad pathway profiles versus fine-scale ecological prediction

The Random Forest result exceeded chance but achieved only **0.408 +/- 0.169** balanced accuracy. [src: pseudomonas_carbon_ecology] The report attributes the modest performance to small class sizes, overlap among environments, coarse pathway resolution, metadata uncertainty, and likely strain-level variation. [src: pseudomonas_carbon_ecology] Thus, broad carbon capability may identify ecological tendencies without providing sufficiently detailed resolution for reliable habitat assignment. [src: pseudomonas_carbon_ecology]

## Open Directions

1. Apply PGLS or phylogenetic logistic regression to the species pathway profiles and GTDB species tree to test whether environment associations persist after phylogenetic correction. [src: pseudomonas_carbon_ecology]
2. Add aromatic degradation modules, including toluene, benzoate, and naphthalene pathways, to test whether compounds central to *Pseudomonas putida* ecology improve environmental classification beyond the 62 GapMind pathways. [src: pseudomonas_carbon_ecology]
3. Analyze within-species pathway variation in *Pseudomonas fluorescens* and *Pseudomonas putida* to test for metabolic ecotypes associated with different isolation environments. [src: pseudomonas_carbon_ecology]
4. Combine genome-level pathway predictions with the full isolation-source dataset to determine whether strain-level profiles outperform species-level profiles for predicting environment. [src: pseudomonas_carbon_ecology]
5. Compare predicted carbon capabilities with experimental fitness measurements from [[entities/random-barcode-transposon-sequencing]] and the [[entities/fitness-browser]] to distinguish genomic capability from condition-specific functional use. [src: pseudomonas_carbon_ecology]

See also: [[summaries/respiratory_chain_wiring__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]