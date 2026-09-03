---
type: "Summary"
description: "ADP1 deletion phenotypes reveal a continuous, condition-specific metabolic landscape"
doc_type: short
full_text: "sources/adp1_deletion_phenotypes__REPORT.md"
---

# ADP1 Deletion Collection Phenotype Analysis

## Overview

This analysis examines growth phenotypes for the *Acinetobacter baylyi* ADP1 single-gene deletion collection across eight carbon sources. It integrates growth ratios, TnSeq essentiality classifications, functional annotations, and pangenome conservation to characterize condition-dependent gene requirements, phenotype structure, and deletion-collection coverage. [src: adp1_deletion_phenotypes]

## Key Findings

### Carbon sources form a three-tier essentiality landscape

The eight conditions separate into demanding, moderate, and robust growth environments based on the fraction of genes with growth defects. Urea is the most demanding condition: 97.9% of genes show severe defects at a growth-ratio threshold below 0.5. Quinate is the most robust, with only 1.6% defective at that threshold. At the broader ratio < 0.8 threshold, demanding conditions include urea, acetate, and butanediol (95–100% defective), moderate conditions include asparagine and lactate (37–45%), and robust conditions include glucarate, glucose, and quinate (0.5–2.4%). Mean growth ratios range from 0.41 for urea to 1.36 for quinate. [src: adp1_deletion_phenotypes]

### Conditions provide largely independent phenotypic information

The complete growth matrix contains 2,034 genes measured across all eight conditions. Pairwise condition correlations are moderate at best: the highest is acetate–butanediol at Pearson *r* = 0.58, while the median across 28 pairs is *r* = 0.25. PCA requires five components to explain 82% of the variance. PC1 explains 36.7% and represents general growth sensitivity, whereas PC2 explains 12.7% and primarily separates urea responses from carbon-metabolism responses. These results indicate that the panel provides approximately five independent dimensions of phenotypic information rather than only a demanding-versus-robust distinction. [src: adp1_deletion_phenotypes]

### The phenotype landscape is primarily a continuum

Hierarchical clustering of eight-condition growth profiles produces an optimal *K* = 3 but a low silhouette score of 0.24. The two major groups contain 1,160 and 850 genes and broadly represent generally sensitive versus generally tolerant profiles; no functional enrichments survive FDR correction. This supports the [[concepts/condition-dependent-essentiality]] view that gene importance varies continuously across environments rather than separating into discrete functional modules. [src: adp1_deletion_phenotypes]

A notable exception is a 24-gene module with extreme quinate-specific defects: its mean quinate z-score is -7.28 while responses in other conditions are near zero. These genes belong to aromatic degradation pathways and form the only clearly discrete phenotypic module detected in the dataset. [src: adp1_deletion_phenotypes]

### Condition-specific genes map to expected metabolic pathways

A total of 625 genes (31% of the complete matrix) have a condition-specificity score of at least 1.0, indicating that their growth importance is concentrated on one carbon source. The strongest condition-specific signals correspond to expected pathways:

- **Quinate:** protocatechuate/quinate degradation and [[entities/pqq-biosynthesis]], including *pcaC*, *pcaG*, *pcaH*, *pcaB*, *quiA*, *quiB*, *pqqC*, and *pqqD*.
- **Urea:** the complete seven-subunit/accessory [[entities/urease-complex]] (*ureA*–*ureG*).
- **Asparagine:** asparagine catabolism, including aspartate ammonia-lyase and L-asparaginase.
- **Acetate:** fatty-acid beta-oxidation and the glyoxylate shunt, including *fadB*, malate synthase G, and *citB*.
- **Glucarate:** glucarate degradation, including *gudD*, a D-glucarate transporter, and 2,5-dioxovalerate dehydrogenase.
- **Glucose:** the Entner–Doudoroff pathway and PQQ-dependent glucose oxidation, including *eda*, *gntT*, gluconokinase, and glucose dehydrogenase.
- **Butanediol:** butanediol catabolism and the acetoin pathway.
- **Lactate:** lactate regulation and cytochrome oxidase components, including *lldR*, *cyoC*, and *cyoD*.

The quinate-specific set includes 51 genes with specificity > 0.5 and z-score < -1. In addition to aromatic degradation genes, it contains NADH–ubiquinone oxidoreductase subunits, suggesting the hypothesis that aromatic catabolism creates distinctive electron-transport-chain demands. PQQ biosynthesis genes are condition-specific for both quinate and glucose, consistent with PQQ-dependent dehydrogenases contributing to both pathways. [src: adp1_deletion_phenotypes]

### Missing dispensable genes are shorter and less conserved

Of 2,593 TnSeq-dispensable genes, 272 (10.5%) lack growth data in the deletion collection. Compared with the 2,321 present dispensable genes, the missing group has a shorter mean length (813 bp versus 981 bp), lower RAST annotation coverage (91% versus 100%), lower KO annotation coverage (49% versus 59%), and lower pangenome-core representation (76.5% versus 93.3%; *p* = 1.4×10⁻²⁰). [src: adp1_deletion_phenotypes]

Hypothetical proteins are strongly enriched among missing genes: 25 are completely unannotated (*q* = 2.4×10⁻²⁵), and 48 are annotated as hypothetical proteins (*q* = 3.0×10⁻⁴). The 313 uncertain-class genes are even shorter and less conserved, with a mean length of 361 bp, 42% annotation coverage, and 31% pangenome-core status. These properties are consistent with the interpretation that many may be gene fragments or pseudogenes rather than true essential genes, although this remains an interpretation rather than a direct validation. [src: adp1_deletion_phenotypes]

## Interpretation

The results support a [[concepts/phenotypic-landscape]] in which ADP1 gene requirements are shaped by metabolic entry points and distributed along gradients of condition sensitivity. The 625 condition-specific genes provide direct evidence that single-condition assays substantially underrepresent functional dependencies. The quinate pathway is a strong discrete exception to the otherwise continuous landscape. [src: adp1_deletion_phenotypes]

The findings are consistent with the adaptive-flexibility framework of Guzman et al. (2018), while differing from the discrete phenotypic modules reported for *E. coli* chemical-genetic profiles by Nichols et al. (2011). The contrast may reflect organismal metabolic architecture or the difference between single-gene deletions and chemical perturbations. The condition-specificity result also agrees with the broader use of [[entities/random-barcode-transposon-sequencing]] for discovering context-dependent gene functions, despite the different experimental strategy. [src: adp1_deletion_phenotypes]

The association between deletion-collection gaps and reduced pangenome conservation connects [[concepts/pangenome-integration]] with experimental coverage: less-conserved genes are disproportionately likely to be missing from the collection. This is an observed association, not evidence that pangenome status directly causes missingness. [src: adp1_deletion_phenotypes]

## Limitations

- Growth ratios are single-timepoint measurements with unknown technical noise, so some specificity could reflect measurement variation.
- The complete matrix excludes 499 essential genes and 316 genes with incomplete data, biasing the analysis toward dispensable genes with successful deletion mutants.
- Only eight carbon sources were tested; additional conditions may reveal further independent dimensions.
- The pangenome core/accessory assignments are species-level *A. baylyi* data and may not resolve population-level variation.

## Future Directions

1. Apply independent component analysis to test whether latent condition-specific signals are obscured by the gradient structure.
2. Compare ADP1 specificity profiles with overlapping RB-TnSeq conditions in the [[entities/fitness-browser]] and other datasets.
3. Infer regulatory relationships from genes that are jointly specific to individual carbon sources.
4. Expand the panel with additional carbon sources, nitrogen sources, and stress conditions to increase phenotypic resolution.

## Source Artifacts

The analysis generated complete and partial growth matrices, gene-module assignments, condition-specificity scores, and a TnSeq gap-analysis table. Supporting notebooks cover data extraction, condition structure, gene modules, condition specificity, and TnSeq-gap characterization. [src: adp1_deletion_phenotypes]

## Related Concepts
- [[concepts/multi-omics-integration]]

## Entities
- [[entities/quinate-aromatic-degradation]]
- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/berdl]]
