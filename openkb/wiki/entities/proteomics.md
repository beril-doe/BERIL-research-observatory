---
sources: ["summaries/discoveries.md", "summaries/clay_confined_subsurface__REPORT.md", "summaries/berdl_data_atlas__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
type: "Method"
description: "Protein-abundance measurements that predict ADP1 gene essentiality"
---

# Proteomics

## Overview

Proteomics is a method for measuring protein abundance across biological samples. In the ADP1 data explorer, it forms one of six integrated data modalities alongside essentiality, metabolic flux, mutant fitness, pangenome classification, and functional annotation. [src: acinetobacter_adp1_explorer]

Proteomics is connected to [[concepts/multi-omics-integration]] and is represented as a core component of the ADP1 database summarized in [[summaries/acinetobacter_adp1_explorer__REPORT]]. [src: acinetobacter_adp1_explorer]

In the triple-essentiality analysis, proteomics provided an independent continuous measurement of expression requirement for comparison with experimental knockout essentiality, [[entities/random-barcode-transposon-sequencing]] fitness, and [[entities/flux-balance-analysis]] predictions. [src: adp1_triple_essentiality]

## ADP1 application

Protein abundance was measured across seven *Acinetobacter* strains, providing data for 2,383 genes in the ADP1 analysis. [src: adp1_triple_essentiality] The earlier ADP1 database report describes the strain set as including wild-type ADP1 and six engineered derivatives with aromatic amino acid pathway modifications, including ΔaroF, ΔaroG, and dgoA variants. [src: acinetobacter_adp1_explorer]

Cross-strain protein-abundance correlations were high, indicating that the engineered modifications had targeted rather than globally disruptive effects on the proteome. [src: acinetobacter_adp1_explorer] This result is based on cross-strain analysis and does not establish that all engineered changes had no broader physiological effects. [src: acinetobacter_adp1_explorer]

For the refined essentiality analysis, 2,288 genes had both proteomics and knockout-essentiality data: 464 were classified as essential and 1,824 as dispensable. [src: adp1_triple_essentiality] Essential genes had mean log2 expression of 28.43 ± 2.94, compared with 25.73 ± 2.96 for dispensable genes. [src: adp1_triple_essentiality] The 2.70-log2-unit difference corresponded to 6.5-fold higher expression in essential genes. [src: adp1_triple_essentiality]

The expression difference was highly significant by a Mann–Whitney U test (p = 9.91×10⁻⁵⁹). [src: adp1_triple_essentiality] Protein abundance correlated positively with essentiality, with Pearson r = 0.345 (p = 5.32×10⁻⁶⁵) and Spearman ρ = 0.338 (p = 3.28×10⁻⁶²). [src: adp1_triple_essentiality] Proteomics predicted knockout essentiality with ROC AUC = 0.743 in the analyzed minimal-medium gene set. [src: adp1_triple_essentiality]

These results support the interpretation that essential genes tend to require robust expression, while also showing that protein abundance is a continuous predictor rather than a direct substitute for a knockout phenotype. [src: adp1_triple_essentiality] The predictive result is an association from cross-gene analysis and does not demonstrate that high protein abundance causes essentiality. [src: adp1_triple_essentiality]

## Data coverage

Proteomics data cover 41% of the 5,852 genes represented in the central `genome_features` table. [src: acinetobacter_adp1_explorer] The refined analysis used 2,383 genes with expression measurements and 2,288 genes after matching proteomics data to knockout essentiality calls. [src: adp1_triple_essentiality] No single gene has measurements across all six database modalities, so proteomics must be interpreted alongside the other available evidence rather than as a complete multi-omics profile for every gene. [src: acinetobacter_adp1_explorer]

The refined study averaged log2 protein expression across seven *Acinetobacter* strains. [src: adp1_triple_essentiality] Proteomics therefore supplies cross-strain expression evidence, whereas knockout, fitness, and growth measurements address survival or phenotype under particular experimental conditions. [src: adp1_triple_essentiality]

## Related resources

The proteomics measurements are part of the user-provided ADP1 database and are not identified as a separate BERDL collection in the report. [src: acinetobacter_adp1_explorer] They can be analyzed alongside [[entities/acinetobacter-baylyi-adp1]], [[entities/random-barcode-transposon-sequencing]], and [[entities/flux-balance-analysis]] data to compare protein abundance with gene essentiality, mutant fitness, and metabolic predictions. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality]

The triple-essentiality report recommends using proteomics as supporting evidence for essentiality and combining it with FBA and continuous fitness measurements in integrated predictors. [src: adp1_triple_essentiality] This positions proteomics as a complementary modality in [[concepts/multi-omics-integration]] rather than as a standalone ground-truth assay. [src: adp1_triple_essentiality]

## Related Documents
- [[summaries/adp1_triple_essentiality__REPORT]]


See also: [[summaries/berdl_data_atlas__REPORT]]

See also: [[summaries/clay_confined_subsurface__REPORT]]

See also: [[summaries/discoveries]]