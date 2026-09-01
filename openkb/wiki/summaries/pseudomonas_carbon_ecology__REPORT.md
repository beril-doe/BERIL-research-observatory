---
type: "Summary"
description: "Genus-scale analysis links Pseudomonas carbon pathways to ecology and host adaptation."
doc_type: short
full_text: "sources/pseudomonas_carbon_ecology__REPORT.md"
---

# Pseudomonas Carbon Ecology

## Overview

This report analyzes carbon-source utilization across **12,732 genomes**, **433 *Pseudomonas* species clades**, and **62 GapMind carbon pathways** from GTDB r214. It tests whether pathway profiles distinguish ecological environments and whether host-associated lineages show metabolic streamlining. The central result is that deep phylogenetic divergence—especially the split between *Pseudomonas* sensu stricto and *Pseudomonas_E*—dominates pathway variation, while carbon profiles also retain a weaker but significant ecological signal.

The report contributes to the cross-document themes of [[concepts/metabolic-streamlining]], carbon-source utilization, ecological prediction from microbial traits, [[concepts/phylogenetic-confounding]], and pangenome–ecology relationships.

## Dataset and classification

- The analysis used the BERDL `kbase_ke_pangenome` collection, including pangenome, GapMind, genome, isolation-source, sample, GTDB metadata, and taxonomy tables.
- The dataset contained 6,905 genomes from 19 *Pseudomonas* sensu stricto species and 5,687 genomes from 398 *Pseudomonas_E* species.
- Isolation metadata were classifiable for 8,171 of 12,732 genomes (64.2%). Keyword-based classification identified clinical, human, freshwater, soil, plant-surface, rhizosphere, food/dairy, animal, industrial, and marine environments.
- Of 433 species, 387 had at least one classifiable genome. Majority assignments yielded 204 free-living, 109 host-associated, 59 plant-associated, and 15 food-associated species.
- Species-level pathway completeness was defined as the fraction of genomes scored “complete” or “likely_complete” for each GapMind pathway. Mean completeness across species was 0.882, while pathway richness ranged from 27 to 61 pathways and averaged 54.6.

## Key findings

### 1. Host-associated *Pseudomonas* lost plant-derived sugar pathways

The *Pseudomonas aeruginosa* group showed substantially lower completeness for plant-derived sugars and sugar alcohols than the *P. fluorescens/putida* group. Among seven *Pseudomonas* sensu stricto species and 189 *Pseudomonas_E* species with at least five genomes, **43 of 62 pathways** differed significantly by Mann–Whitney U tests with Benjamini–Hochberg correction.

Largest differences included:

| Pathway | *P. aeruginosa* group | *P. fluorescens* group | Difference |
|---|---:|---:|---:|
| Xylose | 0.0% | 74.4% | +74.4 percentage points |
| Ribose | 27.9% | 92.0% | +64.2 percentage points |
| Arabinose | 0.0% | 62.6% | +62.6 percentage points |
| Galacturonate | 28.6% | 88.4% | +59.8 percentage points |
| Myo-inositol | 0.0% | 58.8% | +58.8 percentage points |
| Mannitol | 25.9% | 77.5% | +51.6 percentage points |
| Sorbitol | 25.9% | 77.4% | +51.5 percentage points |

By contrast, amino-acid catabolism—including arginine, histidine, serine, and glutamate—and core organic-acid pathways such as citrate, succinate, and pyruvate remained near-universal (>99%) in both groups. This pattern is consistent with host-associated *P. aeruginosa* retaining pathways useful in amino-acid-rich host environments while losing plant-carbon pathways that are less relevant to that lifestyle. The report rates this hypothesis, H1b, as **strongly supported**.

Rhamnose and fucose were more complete in *P. aeruginosa* (66.8%) than in the *P. fluorescens* group (41.3% and 45.1%, respectively), although these differences were not significant after FDR correction. The report suggests that rhamnose utilization may relate to *P. aeruginosa* rhamnolipid biology, but this remains an interpretation rather than an established causal explanation.

### 2. Carbon profiles contain ecological information

Among 54 free-living and plant-associated species meeting filtering criteria, pathway profiles were significantly associated with isolation environment. A 999-permutation PERMANOVA-like test gave **p = 0.006**, with between-group mean distance of **2.054** versus within-group mean distance of **1.890**. The first five principal components explained **74.9%** of variance; PC1 explained **31.2%**.

A Random Forest classifier trained on soil, freshwater, plant-surface, and rhizosphere classes achieved balanced accuracy of **0.408 +/- 0.169**, above the **0.250** chance baseline. The strongest features were:

1. D-serine — importance 0.132, associated with rhizosphere samples
2. Arabinose — 0.094
3. Rhamnose — 0.086
4. Fucose — 0.085
5. Xylose — 0.070

Thus, H1a is **partially supported**: pathway profiles carry a statistically significant ecological signal, but their predictive performance is modest and insufficient for reliable fine-grained environment classification alone.

### 3. Free-living species have greater pathway richness

Across species with at least five genomes, free-living and plant-associated species had higher carbon pathway richness than host-associated species, with median richness of **57** versus **55** pathways complete in more than half of genomes. Within *Pseudomonas_E*, where deep subgenus divergence was controlled more directly, mean richness was **56.7** for plant-associated species, **56.1** for free-living species, and **55.2** for host-associated species.

The effect is smaller within *Pseudomonas_E* than between subgenera, indicating that lifestyle-associated variation exists but is secondary to the major phylogenetic split.

### 4. The aeruginosa–fluorescens division dominates pathway variation

PCA across all species primarily separated *Pseudomonas* sensu stricto from *Pseudomonas_E*, driven by the loss of plant-sugar pathways in the former. Within *Pseudomonas_E*, free-living, host-associated, and plant-associated species overlapped substantially. This demonstrates a key [[concepts/phylogenetic-confounding]] issue: apparent lifestyle effects may partly reflect lineage composition rather than independent ecological adaptation.

## Interpretation

The report presents genus-scale evidence for [[concepts/metabolic-streamlining]] in host-associated *Pseudomonas*. The missing pathways are concentrated in xylose, arabinose, myo-inositol, galacturonate, mannitol, and sorbitol metabolism—substrates associated with plants, plant cell walls, or plant-associated environments. Retention of amino-acid and organic-acid pathways is compatible with nutrition in host environments such as cystic-fibrosis sputum.

The findings extend prior observations of metabolic specialization in *P. aeruginosa* from individual strains or infection settings to a species-level pattern across thousands of genomes. They also support the idea of [[concepts/metabolic-niche-partitioning]] within environmentally diverse *Pseudomonas*, while showing that the ecological signal is weaker than the subgenus-level signal.

The modest classifier accuracy suggests that 62 GapMind pathways are too coarse to capture all niche-relevant metabolism. In particular, aromatic compound degradation—important in *P. putida* ecology—is underrepresented. Strain-level accessory-genome variation may therefore be more informative for environmental prediction than species-level pathway profiles.

## Limitations

- *P. aeruginosa* was overrepresented, comprising 53% of the genomes (6,760/12,732), while many environmental species had fewer than 10 genomes.
- Isolation sources were assigned using keywords from free-text metadata; approximately 6.7% were unknown and 29.1% were classified as other.
- GapMind’s 62 pathways omit important genus-specific and aromatic degradation capabilities.
- PCA was dominated by subgenus divergence, and the analyses did not explicitly model phylogenetic non-independence.
- Majority-vote environment assignments obscure species that occupy multiple environments.
- Species-level aggregation may conceal strain-level metabolic ecotypes and environment-specific subpopulations.

## Future analyses

1. Add KEGG or equivalent modules for toluene, benzoate, naphthalene, and other aromatic compounds.
2. Use GTDB phylogenies with PGLS or phylogenetic logistic regression to test whether lifestyle associations persist after phylogenetic correction.
3. Analyze within-species variation in broadly distributed species such as *P. fluorescens* and *P. putida* to identify [[concepts/metabolic-ecotypes]].
4. Compare predicted pathways with experimental RB-TnSeq data from the [[entities/fitness-browser]] to test pathway importance under defined carbon sources.
5. Model the full 789,012-row genome-by-pathway matrix with genome-level isolation sources to assess strain-level environmental prediction.

## Source notebooks and outputs

- `01_data_extraction.ipynb`: BERDL extraction of species, pathways, and isolation sources.
- `02_environment_harmonization.ipynb`: Environment classification and species-level lifestyle aggregation.
- `03_pathway_lifestyle_analysis.ipynb`: Subgenus and lifestyle pathway comparisons.
- `04_ecology_prediction.ipynb`: PCA, permutation testing, and Random Forest prediction.
- Generated data include species statistics, 789,012 genome-level pathway scores, isolation sources, environment assignments, species lifestyle profiles, and 62 pathway comparison results.

## Related Concepts
- [[concepts/condition-dependent-essentiality]]
- [[concepts/coverage-limited-inference]]
- [[concepts/ecological-generalism]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/evidence-triangulation]]
- [[concepts/latent-metabolic-capabilities]]
- [[concepts/organism-specificity]]
- [[concepts/scalable-spark-data-analysis]]

## Entities
- [[entities/bakta]]
- [[entities/berdl]]
- [[entities/flux-balance-analysis]]
- [[entities/modelseed]]
- [[entities/average-nucleotide-identity]]
