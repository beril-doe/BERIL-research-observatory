---
type: "Concept"
sources: ["summaries/genotype_to_phenotype_enigma__REPORT.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/discoveries.md", "summaries/conservation_vs_fitness__REPORT.md", "summaries/cofitness_coinheritance__REPORT.md"]
description: "Near-universal genes limit detectable pangenome associations through low presence variance."
---

# Prevalence Ceiling in Pangenome Association Analysis

## Definition

The prevalence ceiling is a statistical limitation in pangenome association analysis: when genes or clusters occur in nearly every genome, their binary presence vectors have little variance, causing the phi coefficient and related association measures to approach zero or become undefined. [src: cofitness_coinheritance]

This ceiling can make genuinely coupled genes appear weakly associated because both genes are already present across almost all sampled genomes. [src: cofitness_coinheritance]

## Evidence from Co-inheritance Analysis

In the [[summaries/cofitness_coinheritance__REPORT]] analysis, most Fitness Browser genes mapped to core pangenome clusters with prevalence above 95%, limiting the ability to detect co-inheritance from presence/absence patterns. [src: cofitness_coinheritance]

Pairwise co-fitness showed only a small aggregate association with co-occurrence: mean phi was 0.092 for cofit pairs and 0.089 for prevalence-matched random pairs, yielding delta phi = +0.003 despite a Mann–Whitney p-value of 1.66e-29. [src: cofitness_coinheritance]

The report interprets this small effect as partly attributable to the prevalence ceiling, because near-universal clusters leave little variation for distinguishing cofit pairs from random pairs. [src: cofitness_coinheritance]

The negative relationship between co-fitness strength and co-occurrence supports this interpretation: across 1.04 million pairs, co-fitness strength weakly anti-correlated with phi (Spearman rho = -0.109, p < 1e-300). [src: cofitness_coinheritance]

## Missing and Undefined Associations

When both genes are present in every genome, their presence vectors have zero variance and phi cannot be computed. [src: cofitness_coinheritance]

This issue was especially pronounced for Korea, where 95.2% of cofit pairs had NaN phi because both genes had 100% prevalence across 72 genomes. [src: cofitness_coinheritance]

Only approximately 8,000 of 166,601 Korea cofit pairs were computationally usable, so the observed delta of -0.042 was interpreted as statistical noise from the reduced effective sample rather than as evidence of biological anti-association. [src: cofitness_coinheritance]

## Consequences for Interpretation

A weak pairwise association does not necessarily imply weak functional coupling when the genes are highly prevalent; it may instead reflect insufficient presence/absence variation. [src: cofitness_coinheritance]

Comparisons across organisms are also sensitive to genome-content diversity. Ddia6719 and pseudo3_N2E3 showed the largest positive pairwise effects, with delta phi values of +0.093 and +0.026 respectively, and the report attributes their detectable signals to accessory variation despite their near-clonal genomic backgrounds. [src: cofitness_coinheritance]

The ceiling can therefore obscure [[concepts/gene-co-inheritance]] and complicate comparisons of [[concepts/cofitness-networks]] across organisms with different core-to-accessory genome ratios. [src: cofitness_coinheritance]

Prevalence matching is necessary to control for this problem, but it does not restore information that is absent from nearly invariant presence vectors. [src: cofitness_coinheritance]

## Mitigation Strategies

The report proposes restricting association tests to auxiliary-only pairs, specifically pairs in which both clusters have prevalence below 95%, to maximize presence/absence variance. [src: cofitness_coinheritance]

Module-level analysis provides another strategy: ICA modules showed a stronger co-inheritance signal than individual cofit pairs, with delta phi = +0.053 across 195 modules, while accessory modules had mean delta phi = +0.108. [src: cofitness_coinheritance]

These results suggest that multi-gene units can retain detectable structure even when many individual genes are too prevalent for informative pairwise testing. [src: cofitness_coinheritance]

Analyses should also report the fraction of undefined coefficients, effective sample sizes, and the prevalence distribution rather than relying only on nominal association statistics. [src: cofitness_coinheritance]

## Relationship to Phylogenetic Confounding

Prevalence ceilings and [[concepts/phylogenetic-confounding]] are distinct but interacting limitations: shared ancestry can elevate co-occurrence among related genomes, while high prevalence can suppress or invalidate the statistic used to measure it. [src: cofitness_coinheritance]

In the report, cofit-pair phi was higher among near genomes (mean = 0.102) than medium-distance genomes (mean = 0.067), but sparse representation of far genomes limited separation of functional coupling from phylogenetic signal. [src: cofitness_coinheritance]

## Open Directions

- Recompute pairwise co-inheritance using only auxiliary clusters below 95% prevalence and test whether the co-fitness effect increases. [src: cofitness_coinheritance]
- Compare effect sizes after matching organisms on auxiliary-genome fraction and the number of genomes, testing how much variation is explained by the prevalence distribution. [src: cofitness_coinheritance]
- Use raw Fitness Browser fitness data to add organisms currently lacking co-fitness measurements, especially the two Ralstonia datasets, and determine whether broader phylogenetic sampling changes the ceiling-limited result. [src: cofitness_coinheritance]
- Compare pairwise and module-level statistics while explicitly modeling undefined phi values and prevalence strata. [src: cofitness_coinheritance]

See also: [[summaries/conservation_vs_fitness__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/gene_function_ecological_agora__REPORT]]

See also: [[summaries/genotype_to_phenotype_enigma__REPORT]]