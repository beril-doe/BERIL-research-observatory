---
type: "Summary"
description: "Gene-level analysis reveals universal, conserved metal cross-resistance and tiered gene architecture."
doc_type: short
full_text: "sources/metal_cross_resistance__REPORT.md"
---

# Gene-Resolution Metal Cross-Resistance Across Diverse Bacteria

## Overview

This report analyzes gene-level fitness data from the [[entities/fitness-browser]] to characterize metal cross-resistance across diverse bacteria. It evaluates 452 metal experiments across 37 organisms and 14 metals, with detailed cross-resistance analysis for 28 organisms having measurements for at least three metals. The study connects cross-resistance magnitude, phylogenetic conservation, gene-function tiers, pangenome conservation, and [[entities/bacdive]] environmental metadata. [src: metal_cross_resistance]

## Key Findings

### Universal positive cross-resistance

Across 317 organism–metal-pair observations covering 85 unique metal pairs, 311 of 317 gene-level fitness correlations were positive (98.1%), and 99.1% were statistically significant at p < 0.05. Every one of the 15 metal pairs tested in at least five organisms showed greater than 90% sign consistency, and no pair displayed systematic negative cross-resistance. This establishes a strong directional, universal layer of cross-resistance. [src: metal_cross_resistance]

The strongest consensus associations were:

- **Fe–Zn:** mean r = 0.61 across 6 organisms
- **Co–Ni:** mean r = 0.56 across 28 organisms
- **Co–Zn:** mean r = 0.52 across 18 organisms
- **Ni–Zn:** mean r = 0.51 across 18 organisms
- **Cu–Zn:** mean r = 0.48 across 16 organisms

Aluminum was comparatively independent, with a mean association of r = 0.34; Al–Co was the weakest listed pair at r = 0.30 across 20 organisms. [src: metal_cross_resistance]

### Conservation across organisms

Cross-resistance architectures were qualitatively similar across Proteobacteria, Bacteroidetes, Firmicutes, and Actinobacteria. Co–Ni was the strongest recurring pair, with a median r of approximately 0.58 across 28 organisms, while Al–Co and Al–Ni were weaker, with median r values of approximately 0.30. Inter-organism ranking agreement was mostly positive across 12 organisms with at least five metals. [src: metal_cross_resistance]

Conservation was supported by 351 pairwise [[entities/mantel-test]] tests, which produced a mean r of 0.23 with 62% of values positive. Leave-one-out consensus prediction produced a mean r of 0.41, indicating that a universal cross-resistance map predicts average organism-level patterns, although only 2 of 28 organisms reached individual significance. The metal-label permutation test was nonsignificant (p = 0.42), which the report interprets as a consequence of uniformly positive correlations rather than absence of a directional signal. [src: metal_cross_resistance]

These results contribute to the broader [[concepts/shared-stress-biology]] and [[concepts/fitness-conservation]] themes, while leaving phylogenetic non-independence as an unresolved issue.

### Three-tier gene architecture

The 8,162 metal-important genes were classified into three tiers:

| Tier | Genes | Share | Mean core percentage | Fully core (≥95%) |
|---|---:|---:|---:|---:|
| General stress | 1,484 | 18.2% | 92.0% | 57.2% |
| Metal-shared | 2,306 | 28.3% | 91.0% | 50.4% |
| Metal-specific | 4,372 | 53.6% | 89.8% | 45.7% |

The gradient supports the model that broadly pleiotropic stress defenses are most conserved, shared metal defenses are intermediate, and specialized resistance mechanisms are more accessory and evolutionarily dynamic. The fully core fraction declines by 11.5 percentage points from general-stress to metal-specific genes. [src: metal_cross_resistance]

Functional keyword analysis associated general-stress genes with energy, respiration, and cell-envelope functions, whereas metal-specific genes were enriched for transporters, efflux, and iron/metal-related functions. This provides evidence for layered [[concepts/environmental-metal-tolerance]] and [[concepts/core-accessory-resistance]].

### Conserved cross-resistance gene families

The analysis identified 318 ortholog groups that were metal-shared—important for at least two metals—in at least two organisms. The most broadly conserved families occurred in up to 14 organisms and included functions related to cell envelope biology, energy metabolism, DNA repair, and ion homeostasis. These families are candidate components of the conserved machinery underlying multi-metal tolerance. [src: metal_cross_resistance]

### BacDive validation was underpowered

Multi-metal tolerance scores did not correlate with [[entities/bacdive]] isolation from metal environments at the Fitness Browser species scale (Spearman rho approximately -0.02, p > 0.8). After excluding two organisms lacking tier data and collapsing multiple strains to species-level entries, the effective validation set contained 20 independent species. Genus-plus-species substring matching was imprecise for incompletely identified organisms, so fuzzy matches require caution. [src: metal_cross_resistance]

The report treats this null result as inconclusive rather than evidence against the prediction. It argues that meaningful validation requires pangenome-scale analysis, drawing on a prior result in which 42K strains produced Cohen’s d = +1.0. The proposed next step is to apply KEGG/PFAM mapping to cross-resistance signatures across approximately 27K species and test them against [[entities/bacdive]] polymetallic isolation metadata. [src: metal_cross_resistance]

## Interpretation

The report proposes two layers of metal cross-resistance:

1. **Universal directional layer:** all metals share genetic dependencies because they disrupt fundamental processes such as protein stability, DNA integrity, membrane function, and cofactor insertion.
2. **Chemistry-specific magnitude layer:** the strength of association varies with chemical similarity and shared toxicity mechanisms. Co, Ni, and Zn show strong relationships, while Al and possibly Mo are more independent.

The study extends classical Co–Ni–Zn efflux-based models by showing that the association is visible across whole-genome gene-fitness profiles, not only in dedicated efflux genes. It also extends the Metal Fitness Atlas finding that metal-associated genes are 87.4% core by resolving a finer gradient within metal-important genes: 92.0% core for general-stress genes, 91.0% for metal-shared genes, and 89.8% for metal-specific genes. [src: metal_cross_resistance]

## Limitations

- Metal concentrations differed among experiments, allowing dose-response effects to influence correlations.
- Organism coverage was uneven, ranging from 3 to 112 metal experiments.
- The 28 organisms are phylogenetically non-independent; PGLS or independent contrasts are needed to strengthen conservation claims.
- The [[entities/bacdive]] validation was too small and relied partly on imprecise organism matching.
- No non-metal stress controls were included, so universal positivity may partly reflect a shared general-stress response rather than metal-specific cross-resistance.

## Future Directions

- Apply cross-resistance gene signatures to pangenome-scale prediction across approximately 27K species and validate against [[entities/bacdive]] metadata.
- Use PGLS, phylogenetic PCA, or independent contrasts to separate organismal conservation from shared ancestry.
- Normalize fitness effects by metal concentration relative to MIC.
- Apply ICA to metal conditions to identify regulatory modules underlying shared and metal-specific responses.
- Use structural biology to test whether conserved metal-shared proteins possess common metal-binding or membrane-interface features.

## Related Concepts
- [[concepts/condition-dependent-essentiality]]
- [[concepts/organism-specificity]]
- [[concepts/evidence-triangulation]]
- [[concepts/coverage-limited-inference]]
- [[concepts/method-concordance]]

- [[concepts/environmental-metal-tolerance]]
- [[concepts/shared-stress-biology]]
- [[concepts/core-accessory-resistance]]
- [[concepts/fitness-conservation]]
- [[concepts/pangenome-integration]]

## Entities
- [[entities/kegg]]
- [[entities/gtdb]]
- [[entities/berdl]]
- [[entities/independent-component-analysis]]
