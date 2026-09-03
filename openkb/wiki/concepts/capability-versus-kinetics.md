---
type: "Concept"
sources: ["summaries/metabolic_capability_dependency__REPORT.md", "summaries/genotype_to_phenotype_enigma__REPORT.md"]
description: "Genome content predicts metabolic capability better than growth kinetics."
---

# Genetic Capability versus Physiological Kinetics

## Core distinction

Genome-based prediction must distinguish **genetic capability** from **physiological kinetics**. KO presence/absence can indicate whether an organism has transporters, enzymes, or pathways required to use a substrate, but it does not by itself determine how rapidly that organism grows, how long it waits before growing, or how much biomass it produces. [src: genotype_to_phenotype_enigma]

This distinction is central to [[concepts/phenotype-resolution-matching]] and [[concepts/capability-versus-kinetics]]: the resolution of the genomic features must match the resolution of the phenotype being predicted. [src: genotype_to_phenotype_enigma]

## Evidence from ENIGMA growth-curve modeling

The ENIGMA study trained LightGBM models on 46,389 genome-by-condition pairs from 727 genomes using named KEGG ortholog presence/absence features and genus-blocked holdouts across 106 genera. [src: genotype_to_phenotype_enigma]

Binary growth was predictably related to genome content for some substrate classes. AUC was 0.775 for amino acids, 0.780 for nucleosides, and 0.695 for carbon sources; performance was poor for antibiotics (0.619), metals (0.605), and nitrogen sources (0.435). [src: genotype_to_phenotype_enigma]

At the individual-condition level, 95 of 343 testable conditions achieved AUC greater than 0.75. Tryptophan, phenylalanine, valine, mannose, and galactose were among the best-predicted substrates, with tryptophan reaching AUC 0.933. [src: genotype_to_phenotype_enigma]

The most informative full-corpus features included substrate-relevant functions such as K10440, annotated as the ribose transporter rbsC; K03762, the proline/betaine transporter proP; K01857, protocatechuate cycloisomerase pcaB; K13633, an AraC-family carbon-catabolism regulator; and K01214, treX isoamylase. Their emergence supports the interpretation that gene content can predict metabolic capability when the relevant pathway is represented in sufficiently broad training data. [src: genotype_to_phenotype_enigma]

By contrast, maximum growth rate, lag time, and yield had negative cross-genus R² in both KO-based models and models using bulk genomic features. Weak associations between KO count or tRNA count and maximum growth rate were phylogenetically confounded and did not provide predictive power under cross-genus holdout. [src: genotype_to_phenotype_enigma]

The report attributes kinetic variation to factors not represented by binary KO calls, including enzyme catalytic parameters, expression level, regulatory state, ribosome efficiency, and codon usage bias. Nucleotide sequences for computing codon usage features and expression data were not available in the modeling environment. [src: genotype_to_phenotype_enigma]

## Why the distinction matters

A capability model answers a question such as “does this genome contain functions compatible with growth on ribose?” A kinetic model must answer a different question: “under this condition, how quickly and efficiently will this organism grow?” The second question depends on pathway deployment, flux, regulation, and cellular resource allocation, not merely pathway presence. [src: genotype_to_phenotype_enigma]

This distinction also separates gene presence across genera from gene essentiality within a strain. Fitness Browser concordance for SHAP-selected features was 18.7%, compared with a 16.3% random baseline, corresponding to 1.19× enrichment. The weak enrichment does not invalidate capability features because Fitness Browser measures disruption effects within individual strains, whereas the ENIGMA model predicts growth differences across genomes. [src: genotype_to_phenotype_enigma]

Functional redundancy and correlated inheritance can further weaken correspondence between predictive features and individual fitness effects. A gene may distinguish genomes that can grow on a substrate while its disruption has little effect in a strain with alternative pathways; correlated gene blocks may also distribute SHAP credit across several features. [src: genotype_to_phenotype_enigma]

## Dependence on training scale and method

With seven anchor strains, the model was dominated by condition class and a 63-feature genome-scale axis containing genome size, gene counts, operons, rRNA/tRNA features, and co-inherited KOs. It effectively learned a broad relationship in which larger genomes were more likely to grow on amino acids. [src: genotype_to_phenotype_enigma]

With the expanded 46,000-plus-pair corpus, condition-specific transporters and catabolic genes became prominent. This shift indicates that mechanistic capability prediction depends on broad genome-by-condition coverage and is consistent with [[concepts/sample-size-aware-modeling]] and [[concepts/phylogenetic-confounding]]. [src: genotype_to_phenotype_enigma]

The same principle appeared in exometabolomic analysis. Multivariate GBDT failed with six strains and 105 metabolites (AUC 0.500), whereas univariate per-metabolite correlations identified 940 strong KO-metabolite associations across all 62 variable metabolites: 454 production associations and 486 consumption associations. [src: genotype_to_phenotype_enigma]

Growth-predictive KOs and metabolite-associated KOs were largely distinct, with Spearman rho = 0.043, showing that substrate-use capability, metabolite production or consumption, and physiological kinetics represent related but non-equivalent prediction targets. [src: genotype_to_phenotype_enigma]

## Implications for experimental design

Binary growth prediction is most actionable when interpreted as a hypothesis about metabolic capability rather than a guarantee of physiological performance. For continuous growth phenotypes, future models should incorporate sequence-derived codon usage, expression or regulatory measurements, enzyme kinetics, and other variables linked to resource allocation and flux. [src: genotype_to_phenotype_enigma]

Active learning should therefore prioritize experiments that expose missing capability features and condition-specific failures, while separately measuring kinetic responses if the goal is physiological prediction. In the ENIGMA study, an error-by-uncertainty-by-field-relevance ranking selected 50 experiments emphasizing organic acids, nitrate, and low-pH-relevant substrates, with Prescottella and Microbacterium prioritized as informative genera. [src: genotype_to_phenotype_enigma]

This strategy connects [[concepts/experimental-functional-prioritization]] with [[concepts/pathway-completeness]]: experiments can test whether a predicted pathway is sufficient for growth, whether an apparently present pathway is actually deployed, and which additional measurements are needed to explain rate variation. [src: genotype_to_phenotype_enigma]

## Tensions

The study reports mechanistically coherent KO predictors but only weak concordance with Fitness Browser fitness effects. This is a measurement-level tension rather than a direct contradiction: capability across genomes and essentiality within a strain are distinct biological properties, and the appropriate resolution of evidence differs between them. [src: genotype_to_phenotype_enigma]

A second tension is that gene content explains binary growth for some conditions but fails for nitrogen, metals, antibiotics, and continuous kinetics. This pattern suggests that environmental chemistry, regulation, stress response, transport activity, and physiological state become more important when pathway presence alone does not define the phenotype. [src: genotype_to_phenotype_enigma]

## Open Directions

- Add codon usage bias from accessible GenBank nucleotide sequences and test whether it improves genus-blocked prediction of maximum growth rate. [src: genotype_to_phenotype_enigma]
- Combine KO presence with expression or proteomics measurements to test whether pathway deployment explains residual variation in growth rate, lag, and yield. [src: genotype_to_phenotype_enigma]
- Compare capability predictions with Fitness Browser effects after KEGG-module expansion to determine whether weak single-gene concordance reflects pathway-level agreement. [src: genotype_to_phenotype_enigma]
- Use the proposed 50-condition experiment set and retrospective ranked-versus-random subsampling to test whether active learning improves capability-model calibration. [src: genotype_to_phenotype_enigma]
- Link Oak Ridge well geochemistry to strain locations and test whether pH, nitrate, metals, and organic acids explain prediction failures beyond genomic capability features. [src: genotype_to_phenotype_enigma]

## Related Documents
- [[summaries/genotype_to_phenotype_enigma__REPORT]]


See also: [[summaries/metabolic_capability_dependency__REPORT]]