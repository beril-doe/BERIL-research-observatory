---
type: "Concept"
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/nmdc_community_metabolic_ecology__REPORT.md", "summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/lignin_community_enrichment__REPORT.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/genotype_to_phenotype_enigma__REPORT.md"]
description: "Genomic features should match the biological resolution of the phenotype being predicted."
---

# Matching Feature Resolution to Phenotype Resolution

## Definition

[[concepts/phenotype-resolution-matching]] is the principle that predictive features must represent the biological processes operating at the resolution of the target phenotype. In the ENIGMA analysis, gene presence/absence was informative for binary growth capability, but insufficient for continuous growth kinetics. [src: genotype_to_phenotype_enigma]

## Evidence from the ENIGMA model

The strongest evidence comes from genus-blocked modeling of 46,389 genome-by-condition pairs across 727 genomes. Binary growth was most predictable for amino acids (AUC 0.775) and nucleosides (AUC 0.780), moderately predictable for carbon sources (AUC 0.695), and poorly predictable for metals, antibiotics, and nitrogen sources. [src: genotype_to_phenotype_enigma]

The full-corpus model identified condition-specific functions as important predictors, including K10440, a ribose transporter; K03762, a proline/betaine transporter; K01857, protocatechuate cycloisomerase; K13633, an AraC-family regulator; and K01214, an isoamylase. These features match the capability question being asked: whether a genome contains functions that can enable use of a tested substrate. [src: genotype_to_phenotype_enigma]

By contrast, maximum growth rate, lag time, and yield had negative cross-genus R² values when predicted from KO presence/absence or bulk genomic features. The report interprets this as a biological limitation rather than simply a shortage of training data: binary gene content indicates potential metabolic capability, whereas kinetic performance depends on enzyme kinetics, expression and regulation, ribosome efficiency, and other quantitative cellular properties. [src: genotype_to_phenotype_enigma]

## Resolution mismatch across training scales

A seven-strain anchor model mainly learned condition class and a genome-scale axis. The genome-scale feature group accounted for 25.3% of total SHAP importance, while condition class accounted for 45.9%; the resulting behavior was characterized as learning that larger genomes tend to grow on amino acids. [src: genotype_to_phenotype_enigma]

When the training corpus expanded to 46,389 pairs, condition-specific catabolic genes emerged as interpretable predictors. This comparison indicates that both feature resolution and data scale constrain mechanistic interpretation: a small, phylogenetically narrow dataset encourages broad genome-level proxies, while broad genome-by-condition coverage can support substrate-specific feature attribution. [src: genotype_to_phenotype_enigma]

## Different phenotypes require different analytical resolutions

The same principle appeared in the Web of Microbes exometabolomic analysis. Multivariate gradient-boosted decision trees failed with six strains (AUC 0.500), but univariate per-metabolite correlations identified 940 strong KO-metabolite associations across all 62 variable metabolites. These included 454 production associations and 486 consumption associations. [src: genotype_to_phenotype_enigma]

The KOs associated with metabolite production or consumption differed from the KOs that predicted cross-genus growth, with Spearman rho = 0.043 between the feature sets. This result supports [[concepts/metabolite-production-utilization-decoupling]]: the ability to grow, the metabolites an organism produces, and the metabolites it consumes are related but distinct phenotypes requiring different feature-target mappings. [src: genotype_to_phenotype_enigma]

The choice of [[concepts/sample-size-aware-modeling]] is therefore part of resolution matching. The ENIGMA study used multivariate GBDT for large-scale cross-genus binary prediction, but switched to per-metabolite univariate association analysis for the six-strain exometabolomics problem. [src: genotype_to_phenotype_enigma]

## Implications for model design

For binary substrate utilization, named KO features and pathway-level interaction features are appropriate because they represent transport and catabolic capability. Adding KO-by-condition interactions increased mean AUC from 0.620 to 0.653, with improvement in 80 of 106 held-out genera. [src: genotype_to_phenotype_enigma]

For continuous growth prediction, the report proposes adding nucleotide-sequence-derived codon usage bias and, where possible, expression measurements. These features would represent translational optimization and regulatory state more directly than binary KO presence/absence. [src: genotype_to_phenotype_enigma]

For mechanistic interpretation, SHAP values should be interpreted with caution when features are correlated. Correlation grouping at |r| > 0.8 identified a 63-feature genome-scale block, showing that individual feature attribution can split credit across co-inherited genes. This connects the concept to [[concepts/gene-co-inheritance]] and [[concepts/functional-redundancy]]. [src: genotype_to_phenotype_enigma]

Fitness Browser validation also illustrates a resolution mismatch. SHAP-selected genes showed 18.7% significant fitness effects versus a 16.3% random baseline, a 1.19× enrichment. The report explains that cross-genus gene presence asks whether a function is available for growth, whereas RB-TnSeq measures the effect of disrupting a gene within one strain; redundancy and condition differences can make these signals diverge. [src: genotype_to_phenotype_enigma]

## Boundary of the principle

The principle does not imply that high-resolution features always improve prediction. The report found that condition-specific features became useful only with sufficient genome-by-condition coverage, while small datasets were dominated by broad genomic and condition-class effects. [src: genotype_to_phenotype_enigma]

Nor does it imply that a mechanistically plausible feature is necessarily causal. The weak Fitness Browser concordance, correlated SHAP blocks, and unmeasured expression and kinetic variables all limit causal interpretation of feature importance. [src: genotype_to_phenotype_enigma]

## Open Directions

- Compute codon usage bias from the available GenBank sequences and test whether it improves genus-blocked prediction of maximum growth rate, lag, or yield. [src: genotype_to_phenotype_enigma]
- Add expression or regulatory-state measurements to determine whether they explain kinetic variation that KO presence/absence misses. [src: genotype_to_phenotype_enigma]
- Expand Fitness Browser concordance from correlated KO blocks to KEGG-module-level neighborhoods and test whether pathway-level agreement exceeds the observed 1.19× enrichment. [src: genotype_to_phenotype_enigma]
- Compare multivariate and per-metabolite models across progressively larger strain panels to identify the sample size at which metabolite prediction can move from association-level analysis to validated multivariate prediction. [src: genotype_to_phenotype_enigma]

## Source

- [[summaries/genotype_to_phenotype_enigma__REPORT]]

See also: [[summaries/lanthanide_methylotrophy_atlas__REPORT]]

See also: [[summaries/lignin_community_enrichment__REPORT]]

See also: [[summaries/metal_fitness_atlas__REPORT]]

See also: [[summaries/microbeatlas_metal_ecology__REPORT]]

See also: [[summaries/nmdc_community_metabolic_ecology__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]