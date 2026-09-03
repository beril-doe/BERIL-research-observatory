---
type: "Summary"
description: "BacDive phenotypes predict metal tolerance only through phylogenetic structure"
doc_type: short
full_text: "sources/bacdive_phenotype_metal_tolerance__REPORT.md"
---

# BacDive Phenotype Signatures of Metal Tolerance

## Overview

This report tests whether classical bacterial phenotypes recorded in [[entities/bacdive]] predict genome-based metal tolerance scores from the Metal Fitness Atlas. The analysis bridges 97,334 BacDive strains to pangenome data, yielding 37,368 matched strains and 5,647 unique GTDB species; 3,994 species had at least five phenotype features. Ten phenotype features were evaluated using FDR-corrected univariate tests and phylogenetic-blocked multivariate models. [src: bacdive_phenotype_metal_tolerance]

The central conclusion is that phenotype associations with metal tolerance largely reflect [[concepts/phylogenetic-confounding]] rather than independent predictive biology. Taxonomy alone explained 35.4% of variance, while phenotype features alone explained 16.3%; combining taxonomy and phenotypes yielded R² = 0.345, slightly below taxonomy alone. Adding the number of metal resistance gene clusters increased the full-model R² to 0.633. [src: bacdive_phenotype_metal_tolerance]

## Key Findings

### Phenotype associations

Seven of ten phenotype features were significant after FDR correction:

- Gram-negative status: Cohen’s d = -0.610, p = 4.0e-61, q = 4.0e-60, n = 3,272.
- Oxidase positivity: d = +0.530, q = 1.3e-24, n = 1,799.
- Motility: d = +0.345, q = 7.2e-23, n = 3,138.
- Urease positivity: d = -0.175, q = 9.1e-06, n = 3,035.
- Enzyme breadth: rho = -0.058, q = 8.2e-04, n = 3,746.
- Nitrate reduction: d = +0.100, q = 7.4e-03, n = 3,088.
- Catalase positivity: d = +0.104, q = 0.041, n = 2,930.

Metabolite breadth, acetate utilization, and H₂S production did not pass FDR correction. The H₂S estimate was especially unreliable: d = -0.867 but based on only eight negative controls, making small-sample inflation likely. [src: bacdive_phenotype_metal_tolerance]

### Taxonomy dominates phenotype prediction

Taxonomy-only prediction achieved R² = 0.354 and RMSE = 0.038 under five-fold phylogenetic-blocked cross-validation. Phenotype-only prediction achieved R² = 0.163, while taxonomy plus phenotype achieved R² = 0.345, a delta R² of -0.009 relative to taxonomy alone. Gene count alone achieved R² = 0.063, but the full model combining taxonomy, phenotypes, and metal resistance gene-cluster count achieved R² = 0.633 and RMSE = 0.028. [src: bacdive_phenotype_metal_tolerance]

SHAP analysis likewise identified taxonomic class/order codes and `n_metal_clusters` as the dominant predictors. The report interprets classical phenotypes as noisy phylogenetic proxies rather than independent predictors, illustrating the broader [[concepts/phylogenetic-confounding]] problem in microbial trait analysis. [src: bacdive_phenotype_metal_tolerance]

### Gram-negative association

Gram-negative species had substantially higher metal tolerance scores than Gram-positive species (d = -0.61, p < 1e-60, n = 3,272), the largest univariate effect. The association is mechanistically plausible because the Gram-negative outer membrane can restrict metal-cation uptake, but the effect could not be tested within taxonomic classes and was almost entirely a between-lineage comparison, particularly between Gram-positive Actinomycetes and Gram-negative Proteobacteria. [src: bacdive_phenotype_metal_tolerance]

### Urease result reverses the prediction

The predicted positive relationship between urease and nickel tolerance was reversed: urease-positive species had lower overall metal tolerance scores (d = -0.18, p < 1e-5). Class-stratified analysis attributed this pattern primarily to Actinomycetes (d = -0.59, p < 1e-16); the association disappeared in Gammaproteobacteria (d = +0.08, not significant) and Bacilli (d = +0.06, not significant). This suggests a urease–nickel paradox in which nickel handling required for urease does not confer broad metal tolerance and is confounded by lineage composition. [src: bacdive_phenotype_metal_tolerance]

### Catalase shows Simpson’s paradox

Although catalase-positive species had a small positive overall association with metal tolerance (d = +0.10), the direction reversed within major classes. Catalase-negative species scored higher within Actinomycetes (d = -0.62, p < 1e-5), Gammaproteobacteria (d = -0.49, p = 0.004), and Betaproteobacteria (d = -0.51, p = 0.006). The report treats the overall positive association as a between-class composition artifact, a microbial example of Simpson’s paradox. [src: bacdive_phenotype_metal_tolerance]

### Oxygen tolerance and metabolic breadth

The anaerobe–aerobe difference was negligible (d = -0.016, p = 0.55). Facultative anaerobes had a mean score of 0.221, compared with 0.216 for aerobes and 0.215 for anaerobes; although the three-group Kruskal–Wallis test was marginally significant (H = 8.53, p = 0.014), the effect was considered biologically trivial. [src: bacdive_phenotype_metal_tolerance]

Metabolite breadth was not associated with metal tolerance (rho = -0.013, p = 0.42, q = 0.47), providing no support for the hypothesis that broader metabolic versatility predicts a larger metal-resistance repertoire. [src: bacdive_phenotype_metal_tolerance]

## Direct Fitness Browser–BacDive Validation

Only 12 organisms matched directly between the [[entities/fitness-browser]] and [[entities/bacdive]], representing six unique species: *Cupriavidus basilensis*, *Methanococcus maripaludis*, *Ralstonia solanacearum*, *Pseudomonas simiae*, [[entities/azospirillum-brasilense]], and *Pseudomonas fluorescens*. All Gram-typed organisms were Gram-negative, preventing a within-set test of the Gram-stain hypothesis. All urease-typed organisms were urease-negative despite routine nickel testing, consistent with the broader finding that urease status does not predict general metal tolerance. The single anaerobic organism had only one metal tested and was not interpretable. [src: bacdive_phenotype_metal_tolerance]

## Interpretation

The report distinguishes between biologically plausible phenotype mechanisms and statistically independent predictors. Gram-negative envelope structure, catalase activity, oxygen tolerance, and urease-associated nickel handling may influence specific metal responses, but composite metal tolerance scores are dominated by taxonomic structure and genome-encoded resistance capacity. The strongest predictive signal comes from `n_metal_clusters`, supporting a genotype–phenotype concordance perspective in which resistance-gene repertoire is more informative than broad physiological phenotype. [src: bacdive_phenotype_metal_tolerance]

The result is also limited by the nature of the response variable: [[entities/metal-fitness-atlas]] scores are genome-based predictions rather than direct tolerance measurements. Consequently, the study primarily evaluates phenotype-to-genome correlations, even though partial control for `n_metal_clusters` reduces some circularity. Species-name matching recovered 38.4% of the 27,702 GTDB species, and BacDive coverage is biased toward well-studied organisms. [src: bacdive_phenotype_metal_tolerance]

## Open Directions

- Analyze per-metal scores to test specific hypotheses such as catalase–copper or urease–nickel associations rather than general metal tolerance.
- Add GCA accession matching to improve beyond the current 38.4% bridge coverage.
- Apply PGLS or phylogenetic PCA to remove shared ancestry formally before testing phenotype associations.
- Evaluate BacDive machine-learning phenotype predictions while quantifying model-dependent bias.
- Experimentally test H₂S-associated tolerance to zinc, copper, or cadmium, where the observed d = -0.87 estimate is underpowered.
- Compare matched urease-positive and urease-negative strains within a single class using [[entities/random-barcode-transposon-sequencing]] under nickel and non-nickel metal stress. [src: bacdive_phenotype_metal_tolerance]

## Related Concepts
- [[concepts/pangenome-integration]]
- [[concepts/evidence-triangulation]]
- [[concepts/annotation-gap]]
- [[concepts/condition-dependent-essentiality]]

## Entities
- [[entities/amrfinderplus]]
- [[entities/kegg]]
- [[entities/berdl]]
- [[entities/salmonella-enterica]]
- [[entities/escherichia-coli]]
