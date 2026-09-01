---
sources: ["summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/metal_resistance_global_biogeography__REPORT.md", "summaries/bacdive_metal_validation__REPORT.md"]
type: "Dataset"
description: "Genome-based dataset predicting bacterial metal tolerance across pangenome species."
---

# Metal Fitness Atlas

## Overview

The Metal Fitness Atlas is a genome-based dataset and prediction resource for bacterial metal tolerance. It derives metal-tolerance scores from cross-species fitness evidence generated with [[entities/random-barcode-transposon-sequencing]] and projects those scores onto pangenome species using [[entities/kegg]] functional annotations. [src: bacdive_metal_validation]

## Key Facts

- The Atlas projected metal-tolerance predictions onto 27,702 pangenome species. [src: bacdive_metal_validation]
- Its normalized metal score represents metal-tolerance gene content relative to annotated gene clusters, helping control for genome-size differences. [src: bacdive_metal_validation]
- In the BacDive validation study, 42,227 of 97,334 BacDive strains were linked to Atlas scores through GTDB pangenome species matching, covering 6,426 unique GTDB species. [src: bacdive_metal_validation]
- Bacteria isolated from heavy-metal contamination sites had scores one standard deviation above the environmental baseline (Cohen’s d = +1.00, Mann–Whitney p = 0.006, n = 10). [src: bacdive_metal_validation]
- The environmental association was also observed for all contamination sites (Cohen’s d = +0.43), waste/sludge sites (+0.57), and industrial sites (+0.20), with p < 0.0001 for each comparison. [src: bacdive_metal_validation]
- The contamination signal remained significant within Pseudomonadota (delta = +0.040, p < 0.001) and Actinomycetota (delta = +0.035, p < 0.001), but not within Bacillota or Bacteroidota. [src: bacdive_metal_validation]

## Interpretation

The BacDive comparison provides direct ecological validation for the Atlas: predicted metal-tolerance gene content is associated with the environments from which bacteria were isolated. This supports the broader [[concepts/environmental-metal-tolerance]] and [[concepts/genome-ecology-validation]] themes, while the species-level projection illustrates [[concepts/pangenome-integration]]. [src: bacdive_metal_validation]

The validation is strongest for the direction of the environmental association rather than for a precise effect-size estimate. The heavy-metal group contained only 10 matched isolates, and the power analysis estimated a minimum detectable effect of approximately d = 0.93 at 80% power; the observed d = 1.00 therefore barely exceeded the detection threshold. [src: bacdive_metal_validation]

The report also discusses a tension between environmental variation in Atlas scores and the finding from the Metal Specificity project that metal-tolerance genes are 88% core within species. Core conservation within species does not preclude differences between species in the total number of metal-tolerance functions represented in their genomes. [src: bacdive_metal_validation]

## Related Resources

- [[entities/bacdive]] — source of bacterial isolation-environment and phenotype metadata used for validation. [src: bacdive_metal_validation]
- [[entities/fitness-browser]] — related fitness-evidence resource underlying the Atlas’s broader lab-to-environment interpretation. [src: bacdive_metal_validation]
- [[entities/gtdb]] — pangenome taxonomy used to link BacDive strains to predicted scores. [src: bacdive_metal_validation]
- [[summaries/bacdive_metal_validation__REPORT]] — summary of the BacDive isolation-environment validation report. [src: bacdive_metal_validation]

## Limitations and Next Steps

Species-name matching left 55,107 BacDive strains unmatched, so direct GCA-accession matching to pangenome genomes could improve coverage. The report also recommends testing metal-specific environmental associations and expanding phenotype validation with MIC and growth-inhibition data. [src: bacdive_metal_validation]

See also: [[summaries/metal_resistance_global_biogeography__REPORT]]

See also: [[summaries/microbeatlas_metal_ecology__REPORT]]