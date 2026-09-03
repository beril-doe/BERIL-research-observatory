---
type: "Summary"
description: "Links metabolic pathway capability, context-dependent fitness, and pangenome openness."
doc_type: short
full_text: "sources/pathway_capability_dependency__REPORT.md"
---

# Metabolic Capability vs Dependency

## Overview

This report distinguishes genomic metabolic capability from metabolic dependency by integrating GapMind pathway-completeness predictions with RB-TnSeq fitness data from the Fitness Browser. It analyzes 161 organism–pathway combinations across seven model bacteria, then extends the analysis to 2,810 GTDB species and 293,000 genomes. The central implication is that pathway presence alone is insufficient to predict whether a bacterium requires that pathway under a given environment; dependency is context-dependent. This motivates a [[concepts/latent-metabolic-capabilities]] framework linked to [[concepts/condition-dependent-essentiality]] and [[concepts/black-queen-dynamics]].

## Tier 1: Capability–Dependency Classification

Pathways were classified using two dimensions: GapMind completeness and a composite fitness-importance score combining essentiality (40%), fitness breadth (30%), and fitness magnitude (30%). Among 161 organism–pathway pairs:

- **Active Dependency:** 57/161 (35.4%); complete pathways containing fitness-important genes.
- **Latent Capability:** 66/161 (41.0%); complete pathways without fitness importance under aggregate laboratory conditions.
- **Incomplete but Important:** 24/161 (14.9%); GapMind-incomplete pathways whose mapped genes are fitness-important, potentially reflecting annotation gaps or salvage routes.
- **Missing:** 14/161 (8.7%); pathways that were neither complete nor important.

The seven organisms were *Desulfovibrio vulgaris* Hildenborough, *Shewanella oneidensis* MR-1, *Pseudomonas putida* KT2440, *Pseudomonas stutzeri* RCH2, *Caulobacter crescentus*, *Sinorhizobium meliloti*, and *Azospirillum brasilense*.

## Condition-Dependent Importance

All 66 pathways classified as Latent Capability became fitness-important under at least one condition type when fitness effects were stratified by nitrogen limitation, carbon limitation, stress, and other conditions. Nitrogen limitation and stress were among the most frequent triggers. The result supports interpreting latent pathways as conditionally active rather than permanently dispensable, although the report cautions that the median-based importance threshold makes this result partly threshold-dependent.

This finding connects pathway-level metabolism to broader evidence that laboratory fitness can differ from fitness in nature. It also suggests that maintenance of pathways may reflect the range of environmental conditions encountered by a species rather than fitness under a single standard laboratory condition.

## Tier 2: Pathway Variation and Pangenome Openness

Across 2,810 species with at least 10 genomes, the number of variable pathways—present in 10–90% of genomes—was positively associated with pangenome openness:

- Raw Spearman correlation: rho=0.327, p=7.2e-71.
- Partial Spearman correlation controlling for genome count: rho=0.530, p=2.83e-203.

The positive direction was observed in 13 of 18 genera, with significant results in five genera: Clostridium, Eubacterium, Mesorhizobium, Pseudomonas, and Streptomyces. The report interprets this as evidence that pathway gain and loss is associated with genome fluidity, extending [[concepts/pangenome-integration]] with a mechanistically interpretable pathway-variation metric.

## Accessory Contributions to Metabolic Pathways

Comparing GapMind completeness calculated from core genes versus all genes identified amino acid biosynthesis as the most accessory-dependent pathway class. The largest completeness gaps were:

| Pathway | All-genes completeness | Core-only completeness | Gap |
|---|---:|---:|---:|
| Leucine biosynthesis | 0.614 | 0.468 | 0.146 |
| Valine biosynthesis | 0.614 | 0.468 | 0.146 |
| Arginine biosynthesis | 0.613 | 0.472 | 0.141 |
| Lysine biosynthesis | 0.804 | 0.664 | 0.140 |
| Threonine biosynthesis | 0.803 | 0.663 | 0.140 |

These results indicate that pathway completeness can depend on accessory genes within a species. The report proposes that variable biosynthetic capacity could provide a substrate for community-level metabolic sharing and [[concepts/black-queen-dynamics]] dynamics, but does not directly demonstrate metabolite exchange.

## Metabolic Ecotypes

For 225 species with at least 50 genomes and three or more variable pathways, binary profiles across 80 pathways were clustered with hierarchical clustering and Jaccard distance. Species contained a median of four metabolic ecotypes, with a maximum of eight. The maximum was observed in *Alistipes onderdonkii* and *Barnesiella intestinihominis*.

Ecotype count correlated with pangenome openness:

- Raw Spearman correlation: rho=0.262, p=6.8e-05.
- Partial Spearman correlation controlling for genome count: rho=0.322, p=8.0e-07.

The ecotype-openness correlation survives the genome-count control, indicating that species with genuinely more metabolic diversity—not just more sampled genomes—tend to have more open pangenomes. This supports a [[concepts/metabolic-ecotypes]] concept, while noting that ecotype counts depend on the fixed 50% dendrogram-distance threshold and may partly reflect phylogenetic structure.

## Main Synthesis

The report proposes three connected principles:

1. **Capability is not dependency:** a complete pathway does not imply fitness dependence under every condition.
2. **Dependency is environmentally conditional:** pathways that appear dispensable in standard assays can become important under nutrient limitation or stress.
3. **Accessory genomes distribute conditional functions:** pathway variation and ecotype diversity are associated with pangenome openness, especially for amino acid biosynthesis.

Together, these findings refine [[concepts/black-queen-dynamics]] by replacing a simple needed-versus-baggage distinction with a continuum of context-dependent metabolic dependency. They also complement the broader observation that fitness-important genes are enriched in core genomes, while conditionally useful functions may be distributed across accessory genomes.

## Limitations

The Tier 1 analysis includes only seven of 48 Fitness Browser organisms with matching GapMind data and covers only 80 GapMind pathways. Fitness measurements are laboratory-based and do not represent the full range of natural selection. KEGG-based gene-to-pathway mapping can miss genes lacking accurate annotations. The median importance threshold is partly circular for condition-specific reclassification. Ecotype counts depend on clustering choices, and genome-count controls do not remove all sampling bias. Full phylogenetic independent contrasts were not performed. The proposed analysis relating metabolic ecotypes to AlphaEarth environmental niche breadth was not executed because AlphaEarth embeddings covered only 83K of 293K genomes.

## Related Concepts
- [[concepts/fitness-conservation]]
- [[concepts/gene-essentiality]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/annotation-gap]]
- [[concepts/evidence-triangulation]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/metabolic-support-networks]]
- [[concepts/organism-specificity]]
