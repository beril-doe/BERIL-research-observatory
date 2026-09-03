---
type: "Concept"
sources: ["summaries/metal_resistance_global_biogeography__REPORT.md", "summaries/field_vs_lab_fitness__REPORT.md", "summaries/discoveries.md", "summaries/bacdive_metal_validation__REPORT.md"]
description: "Genome-based metal scores track bacterial isolation from contaminated environments."
---

# Environmental Metal Tolerance

## Overview

Environmental metal tolerance is the relationship between bacterial genomic metal-tolerance capacity and the environments from which strains are isolated. The BacDive validation study tests this relationship by linking isolation metadata to pangenome-derived scores from the [[entities/metal-fitness-atlas]]. [src: bacdive_metal_validation]

This concept connects [[concepts/genome-ecology-validation]], which concerns validation of genome-derived predictions against ecological observations, with [[concepts/pangenome-integration]], which enables strain metadata to be connected to species-level genomic features. [src: bacdive_metal_validation]

## Evidence from BacDive

Species-name matching linked 42,227 of 97,334 BacDive strains (43.4%) to metal-tolerance scores across 6,426 GTDB species; 25,089 linked strains had isolation-source metadata. [src: bacdive_metal_validation]

Strains isolated from heavy-metal contamination sites had metal scores one standard deviation above the environmental baseline (Cohen’s d = +1.00, Mann–Whitney p = 0.006, n = 10). [src: bacdive_metal_validation] The environmental baseline had median 0.187 and mean 0.195, whereas the heavy-metal group had median 0.240 and mean 0.236. [src: bacdive_metal_validation]

The association followed the reported contamination-intensity ordering: heavy metal (+1.00) > waste/sludge (+0.57) > all contamination (+0.43) > industrial (+0.20), where values are Cohen’s d relative to the environmental baseline. [src: bacdive_metal_validation] Host-associated strains also scored slightly above baseline (Cohen’s d = +0.14, p < 0.0001), contrary to the original expectation that host-associated bacteria would have lower scores. [src: bacdive_metal_validation]

## Phylogenetic Structure

The contamination signal persisted within Pseudomonadota (delta = +0.040, p < 0.001) and Actinomycetota (delta = +0.035, p < 0.001). [src: bacdive_metal_validation] It was not significant within Bacillota (delta = -0.012, p = 0.285) or Bacteroidota (delta = -0.008, p = 0.456), where contamination-isolate sample sizes were smaller. [src: bacdive_metal_validation]

These results indicate that the association is not explained entirely by phylum composition, while leaving open both biological and statistical explanations for the phylum-specific null results. [src: bacdive_metal_validation] This makes environmental metal tolerance relevant to broader questions about [[concepts/organism-specificity]] and phylogenetic structure in phenotype prediction. [src: bacdive_metal_validation]

## Interpretation

The report interprets the heavy-metal association as validation that genome-derived metal scores capture real ecological adaptation: bacteria isolated from contaminated environments carry more predicted metal-tolerance gene content than bacteria from the environmental baseline. [src: bacdive_metal_validation] The ordered effect sizes across contamination categories are consistent with a hypothesis that stronger metal exposure selects for greater genomic metal-tolerance capacity, although the heavy-metal estimate is based on only 10 matched isolates. [src: bacdive_metal_validation]

The result is compatible with the observation that metal-tolerance genes are 88% core within species. [src: bacdive_metal_validation] Core conservation within species can coexist with between-species differences in the total number of encoded metal-tolerance functions, allowing species-level scores to vary across isolation environments. [src: bacdive_metal_validation]

The slightly elevated host-associated score may reflect taxonomic and genome-complexity composition, because the report identifies host-associated BacDive records as being dominated by large-genome Pseudomonadota pathogens. [src: bacdive_metal_validation] Genome-size normalization reduced but did not eliminate this possible confounding because metal-tolerance functions may correlate with total metabolic complexity. [src: bacdive_metal_validation]

## Phenotypic Validation and Limitations

Only 24 metal-utilization records matched strains with metal scores, including 8 positive and 16 negative results. [src: bacdive_metal_validation] The comparison was not significant (Mann–Whitney p = 0.14, Cohen’s d = -0.57), so it provides no reliable confirmation or refutation of the genome-based score. [src: bacdive_metal_validation]

The heavy-metal comparison had approximately 80% power only for effects of about d = 0.93 or larger; the observed d = 1.00 therefore barely exceeded the reported detection threshold. [src: bacdive_metal_validation] Additional limitations include culture-collection bias, loss of coverage from species-level matching, and possible residual confounding by genome size and taxonomy. [src: bacdive_metal_validation]

## Relation to the Environmental Resistome

Environmental metal tolerance provides an ecological validation case for the broader [[concepts/environmental-resistome]] concept: environmental context can be associated with the distribution of resistance-related genomic functions. [src: bacdive_metal_validation] The BacDive analysis supports this connection for predicted metal-tolerance capacity, but its small heavy-metal sample and incomplete phenotype matching limit conclusions about individual metals or directly measured resistance phenotypes. [src: bacdive_metal_validation]

## Open Directions

- Match BacDive GCA accessions directly to pangenome genome IDs to test whether improved linkage changes the environmental effect estimates. [src: bacdive_metal_validation]
- Add ENIGMA CORAL data from the Oak Ridge metal-contaminated site to test whether the BacDive pattern generalizes to an independently sampled field community. [src: bacdive_metal_validation]
- Analyze iron and manganese environments separately where BacDive representation is sufficient, testing whether specific gene families predict specific contamination types. [src: bacdive_metal_validation]
- Expand BacDive phenotype extraction to MIC and growth-inhibition records to compare genome scores with direct metal-tolerance measurements. [src: bacdive_metal_validation]

## Related Source

- [[summaries/bacdive_metal_validation__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/field_vs_lab_fitness__REPORT]]

See also: [[summaries/metal_resistance_global_biogeography__REPORT]]