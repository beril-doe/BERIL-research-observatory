---
type: "Summary"
description: "Quantifies how bacterial gene fitness effects correlate with pangenome conservation"
doc_type: short
full_text: "sources/fitness_effects_conservation__REPORT.md"
---

# Fitness Effects vs Conservation

## Overview

This report analyzes approximately 194,000 genes across 43 diverse bacteria to test how mutant fitness effects relate to pangenome conservation. It integrates [[entities/fitness-browser]] RB-TnSeq measurements with gene-to-cluster conservation mappings, essentiality classifications, and condition-specific phenotype annotations. The central result is a positive but modest relationship between [[concepts/fitness-conservation]] and pangenome conservation: genes with stronger or broader fitness effects are more likely to be core genes.

## Key Findings

### Fitness importance and conservation

The proportion of core genes declines across the fitness spectrum:

| Fitness category | Genes | Core |
|---|---:|---:|
| Essential (no viable mutants) | 27,693 | 82% |
| Often sick (>10% experiments) | 15,989 | 78% |
| Mixed (sick + beneficial) | 20,739 | 70% |
| Sometimes sick | 25,201 | 72% |
| Always neutral | 94,889 | 66% |
| Sometimes beneficial | 9,705 | 70% |

The same pattern appears when genes are binned by their strongest fitness effect: essential genes are 82.2% core, genes with `min_fit < -3` are 77.7% core, and genes with `min_fit -1 to 0` are 66.4% core. Thus, the report identifies a 16-percentage-point difference between essential and always-neutral genes, although conservation remains only weakly predicted by fitness importance.

### Breadth of fitness effects

Genes affecting fitness in more experimental conditions are more likely to be core. The association is statistically significant but small (Spearman rho = 0.086, p = 8.1e-230):

| Fitness breadth | Core |
|---|---:|
| Essential | 82% |
| 20+ experiments | 79% |
| 6–20 experiments | 73% |
| 1–5 experiments | 71% |
| 0 experiments | 66% |

This supports [[concepts/condition-dependent-essentiality]] as a contributor to conservation, while indicating that breadth alone is not a strong predictor.

### Core genes show stronger effects in both directions

The report rejects the expectation that accessory genes are more burdensome to carry. Core genes are more likely than auxiliary genes to show positive fitness effects when deleted: 24.4% were ever beneficial compared with 19.9% of auxiliary genes, with an odds ratio of 0.77 for auxiliary versus core genes. Core genes also have heavier fitness-distribution tails in both the negative direction, reflecting importance, and the positive direction, reflecting burden or trade-off effects.

This suggests that core genes are functionally active components of critical pathways rather than uniformly neutral or beneficial genes. Their deletion can be strongly harmful in some conditions and beneficial in others.

### Condition-specific effects

Genes tagged with strong condition-specific effects in the `specificphenotype` annotation are 77.3% core, compared with 70.3% for genes without such phenotypes (OR = 1.78, p = 1.8e-97). This contradicts the simple expectation that condition-specific genes should mainly be accessory. Instead, condition-specific effects may be especially detectable among core genes because they participate in well-characterized and environmentally responsive pathways.

A related pattern appears for “ephemeral niche genes”—genes neutral overall but critical in one condition. Of 4,450 such genes (2.7%), 3.0% of core genes fit this pattern, compared with 1.7% of auxiliary genes and 1.6% of singleton genes.

### Novel and singleton genes

Novel singleton genes have near-zero mean fitness in the tested assays, suggesting that they are largely invisible under laboratory conditions rather than systematically detrimental or beneficial. This interpretation is uncertain because singleton genes may have poor transposon coverage, and the available experiments emphasize rich media and standard stresses.

## Interpretation

The findings support a model in which gene conservation reflects functional importance across conditions: essential, broadly influential, and strongly condition-responsive genes are more often maintained across genomes. However, the relationship is not deterministic. Accessory genes can be important in particular environments, while core genes can produce positive deletion effects under trade-off conditions.

The report therefore favors a model of core genes as highly integrated and functionally active, with larger fitness effects in both directions, and accessory genes as comparatively quieter under the laboratory conditions represented in the [[entities/fitness-browser]]. The results are consistent with stronger purifying selection on core genes and with pangenome frequency distributions being shaped by selection, drift, and horizontal gene transfer.

## Data and Methods

- Fitness measurements: [[entities/fitness-browser]] RB-TnSeq mutant fitness data for approximately 194,000 genes.
- Taxonomic scope: 43 bacteria, primarily Proteobacteria.
- Conservation: KBase pangenome gene-to-cluster mappings.
- Additional classifications: essential genes and Fitness Browser `specificphenotype` annotations.
- Supporting analyses: `02_fitness_vs_conservation.ipynb` and `03_breadth_vs_conservation.ipynb`.
- Generated tables: `fitness_stats.tsv`, `fitness_stats_by_condition.tsv`, and `specific_phenotypes.tsv`.

## Limitations

- Laboratory conditions are biased toward rich media and standard stresses and may omit ecologically important niches.
- Single-gene knockout assays do not capture epistatic interactions.
- The dataset covers 43 bacteria and is primarily Proteobacterial, limiting generalization.
- Apparent neutrality among singleton genes may result from insufficient transposon coverage.
- The observed conservation gradient is statistically robust but explains only a limited portion of conservation variation.

## Related Concepts
- [[concepts/phenotypic-landscape]]
- [[concepts/method-concordance]]
- [[concepts/organism-specificity]]

- [[concepts/fitness-conservation]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/gene-essentiality]]
- [[concepts/pangenome-integration]]
- [[concepts/coverage-limited-inference]]