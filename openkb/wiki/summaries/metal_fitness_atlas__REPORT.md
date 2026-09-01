---
type: "Summary"
description: "Cross-species atlas shows metal fitness genes are predominantly core-genome functions"
doc_type: short
full_text: "sources/metal_fitness_atlas__REPORT.md"
---

# Pan-Bacterial Metal Fitness Atlas

## Overview

This report presents a cross-species genome-wide atlas of bacterial fitness under metal stress, integrating [[entities/fitness-browser]] experiments with ortholog and pangenome data. It examines 559 metal-related experiments across 31 organisms and 16 metals, including 383,349 gene × metal fitness records, 1,182 conserved metal gene families, and genome-scale predictions across 27,702 pangenome species.

The central contribution is a revised model of [[concepts/environmental-metal-tolerance]]: genes required for survival under metal stress are predominantly part of the core genome and represent general cellular robustness, whereas specialized metal-resistance mechanisms form a smaller accessory component.

## Key Findings

### Core-genome enrichment

Across 22 organisms and 14 metals, metal-important genes were 87.4% core compared with 76.9% core for baseline genes (OR=2.08, p=4.3e-162). Twenty-one of 22 organisms showed positive core enrichment, and 14 were significant at p<0.05. After removing four duplicate *Pseudomonas fluorescens* FW300 strains, the result remained robust across 18 organisms (OR=2.065, p=5.9e-141), indicating that the finding was not driven by Pseudomonas overrepresentation.

Essential-metal tolerance genes had stronger core enrichment than toxic-metal genes: mean delta +0.148 versus +0.081 (Mann-Whitney U=39, p=0.015, one-sided). Manganese had the largest enrichment (+0.198; all 30 important genes were core), followed by zinc (+0.151), molybdenum (+0.148), tungsten (+0.145), and iron (+0.116). Cadmium and uranium were not individually significant because of limited coverage.

This result reverses the report's initial expectation of accessory enrichment and contrasts with an earlier DvH analysis of condition-specific heavy-metal genes, which found 71.2% core content. The difference is attributed to scope: the present atlas includes all metal fitness defects, most of which affect conserved processes such as the cell envelope, DNA repair, protein quality control, and central metabolism. The proposed [[concepts/core-accessory-resistance]] model therefore has two tiers:

- **Core tier:** General stress and cellular maintenance functions that are broadly conserved.
- **Accessory tier:** Specialized efflux, sequestration, and detoxification systems that provide targeted metal resistance.

### Atlas scale and fitness phenotypes

The Fitness Browser contains 559 metal-related experiments, representing 8.2% of 6,804 total experiments. Six metals have cross-species coverage in at least three organisms: cobalt (27 organisms), nickel (26), copper (23), aluminum (22), zinc (17), and iron (3). DvH is the most extensively profiled organism, with 149 experiments across 13 metals.

Of 383,349 gene × metal records, 12,838 (3.3%) met the broad definition of a metal-important gene (fit < -1 and/or n_sick ≥ 1), while 5,667 (1.5%) met the strict definition. Iron produced the highest fraction of important genes (12.3%), followed by molybdenum/tungsten (11.2%). DvH had 1,366 metal-important genes, or 49.8% of its genome across 13 metals. *Synechococcus elongatus* was also unusually metal-sensitive, with 33.6% of genes important across two metals.

### Conserved gene families and modules

Among 2,891 ortholog groups with metal phenotypes, 1,182 were conserved across at least two organisms and 601 across at least three. The broadest family, OG00128, occurred in 17 organisms and nine metals. Greater organismal breadth was associated with higher pangenome conservation, supporting the interpretation that widely shared metal phenotypes often involve fundamental cellular functions.

The atlas identifies 149 candidate metal-biology families with conserved phenotypes but incomplete functional annotation: 89 truly unknown families, 43 DUF/UPF-domain families, and 17 families with partial functional hints such as transporter or hydrolase annotations. These are function predictions based on cross-species fitness evidence rather than direct biochemical validation.

ICA analysis identified 600 metal-responsive module records out of 19,453 module × metal-experiment records using per-organism z-scored activity profiles and a |z| > 2.0 threshold. The 183 responsive modules with conservation data had a mean core fraction of 0.826 and a median of 0.929. DvH had 47 responsive modules across 12 metals. A raw-score analysis produced no responsive modules because raw module scores were not comparable across experiments; z-normalization resolved this methodological issue. This connects the atlas to [[concepts/dna-rna-functional-response]] and [[concepts/phenotypic-landscape]].

### Pangenome prediction

A metal functional signature containing 1,286 KEGG KO terms was used to score 27,702 pangenome species. Genome-size normalization prevented organisms with large open pangenomes from dominating the ranking. *Leptospirillum* ranked at the 91st percentile, *Acidithiobacillus* at the 77th, *Marinobacter* at the 75th, and *Sulfobacillus* at the 71st.

Bioleaching genera were not significantly enriched as a group after normalization (Mann-Whitney p=0.17), suggesting that metal-associated functions are broadly distributed across bacteria rather than concentrated exclusively in metal specialists. However, the prediction is based on gene repertoire rather than measured tolerance, and simple presence/absence repertoire scores did not adequately predict fitness. This supports the broader principle that [[concepts/condition-dependent-essentiality]] and motivates expression- or regulation-aware models.

## Interpretation and Limitations

The report distinguishes **metal fitness genes**—all genes whose disruption causes a defect under metal stress—from **metal-resistance genes**, such as annotated efflux pumps and detoxification operons. Specialized resistance genes may remain accessory-enriched, but they constitute only part of the genetic basis of survival. The observed core enrichment may also be conservative because putatively essential genes, approximately 14.3% of protein-coding genes and approximately 82% core, lack transposon insertions and are absent from fitness data.

Important limitations include uneven metal coverage, variation in metal concentrations between organisms, phylogenetic non-independence, the broad metal-important definition, and incomplete pangenome mappings. Conservation analysis covered 22 of 48 organisms with relevant data, and the fitness datasets included 24 organisms. Rare-metal results for uranium, chromium, mercury, cadmium, selenium, and manganese are especially dependent on one or two organisms. The report also does not normalize doses relative to organism-specific MIC values.

## Open Directions

1. Reanalyze genes important for metals but not for other stresses to separate general stress functions from metal-specific resistance.
2. Functionally characterize the 149 novel candidates using PaperBLAST, InterPro, and structural prediction.
3. Normalize fitness effects by concentration relative to MIC for cross-species comparisons.
4. Apply phylogenetic independent contrasts to test whether core-enrichment patterns persist after accounting for relatedness.
5. Replace repertoire counts with enrichment-based, regulatory, or expression-aware pangenome models.
6. Expand RB-TnSeq coverage for manganese, chromium, uranium, tungsten, and rare-earth elements.
7. Test high-priority organisms including *Pseudomonas putida*, methanogenic *Methanococcus* strains, *Acidithiobacillus ferrooxidans*, *Geobacter sulfurreducens*, and *Leptospirillum ferrooxidans*.

The suggested experiments would increase cross-species power for critical metals, directly test the 149 candidate families, and connect pangenome predictions to experimentally measured metal tolerance.

## Related Concepts
- [[concepts/fitness-conservation]]
- [[concepts/evidence-triangulation]]
- [[concepts/organism-specificity]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/two-speed-genome]]
- [[concepts/annotation-gap]]
- [[concepts/gene-essentiality]]
- [[concepts/phenotype-resolution-matching]]
- [[concepts/method-concordance]]

## Entities
- [[entities/iron]]
- [[entities/gtdb]]
- [[entities/kegg]]
- [[entities/interproscan]]
- [[entities/alphafold-protein-structure-database]]
- [[entities/oak-ridge]]
- [[entities/marinobacter]]
- [[entities/klebsiella-pneumoniae]]
- [[entities/pseudomonas-aeruginosa]]
