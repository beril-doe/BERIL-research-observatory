---
type: "Summary"
description: "Validates genome-based metal tolerance predictions against BacDive isolation environments."
doc_type: short
full_text: "sources/bacdive_metal_validation__REPORT.md"
---

# BacDive Isolation Environment × Metal Tolerance Prediction

## Overview

This report validates the [[entities/metal-fitness-atlas]] score from the Metal Fitness Atlas against real-world bacterial isolation environments recorded in [[entities/bacdive]]. BacDive strains were linked to GTDB pangenome species, allowing predicted metal tolerance to be compared across contamination categories, phyla, and metal-utilization phenotypes.

## Key Findings

- Bacteria isolated from heavy-metal contamination sites had substantially higher normalized metal tolerance scores than the environmental baseline: Cohen’s d = +1.00, Mann–Whitney p = 0.006, n = 10. The environmental baseline had median 0.187 and mean 0.195.
- The association followed a contamination-intensity pattern: heavy metal (+1.00) > waste/sludge (+0.57) > all contamination (+0.43) > industrial (+0.20). All reported comparisons were statistically significant.
- The signal persisted after phylum stratification in Pseudomonadota (delta = +0.040, p < 0.001) and Actinomycetota (delta = +0.035, p < 0.001), but not in Bacillota (delta = -0.012, p = 0.285) or Bacteroidota (delta = -0.008, p = 0.456).
- Host-associated isolates also had slightly higher scores than the baseline (Cohen’s d = +0.14, p < 0.0001), contrary to the original expectation that host niches would select for lower metal tolerance. The report attributes this cautiously to possible genome-size and taxonomic composition confounding.

## BacDive–Pangenome Bridge

Species-name matching linked 42,227 of 97,334 BacDive strains (43.4%) to metal scores across 6,426 GTDB species. Exact species matches accounted for 33,535 strains (34.5%), while removal of GTDB suffixes recovered an additional 8,692 strains (8.9%). Of the linked strains, 25,089 had isolation-source metadata and 24 had matched metal-utilization records. A total of 55,107 strains (56.6%) remained unmatched. This demonstrates the utility and coverage limitations of [[concepts/pangenome-integration]] for connecting strain metadata to species-level genome resources.

## Metal Utilization Validation

The phenotype comparison was inconclusive because only 24 records matched strains with metal scores: 8 positive and 16 negative results. Positive utilizers had lower scores, but the difference was not significant (Mann–Whitney p = 0.14, Cohen’s d = -0.57). This result is underpowered and should not be interpreted as evidence against the genome-based score.

## Interpretation and Cross-Project Connections

The report treats the contamination association as validation that genome content captures ecological metal adaptation. The dose-response pattern supports the hypothesis that more metal-intensive environments select for bacteria with greater predicted metal-tolerance gene content. However, the heavy-metal result is at the power threshold: with n = 10, the minimum detectable effect at 80% power was approximately d = 0.93, compared with an observed d = 1.00. This is an example of [[concepts/genome-ecology-validation]] in which genome-derived predictions are tested against environmental metadata.

The findings refine the [[concepts/environmental-metal-tolerance]] result that 88% of metal-tolerance genes are core within species. Within-species core conservation does not eliminate between-species differences in the number of encoded metal-tolerance functions, which can still produce an environmental signal.

They also strengthen, at larger scale, the hypothesis raised by the lab-field ecology project: lab-derived metal tolerance may relate to field or isolation-environment distributions. The BacDive analysis provides stronger evidence than the Oak Ridge comparison, where the relationship between lab tolerance and field abundance was suggestive but non-significant (rho = 0.50, p = 0.095, n = 11 genera). The comparison illustrates the value of [[concepts/evidence-triangulation]] across laboratory fitness measurements, field abundance, and isolation-environment data.

The phylum-specific results indicate that [[concepts/phylogenetic-amr-structure]] is only partly analogous to the phylogenetic-confounding question examined here. The signal within Pseudomonadota and Actinomycetota argues against a purely phylum-compositional explanation, while the null results in Bacillota and Bacteroidota may reflect either biology or limited contamination-isolate sample sizes.

## Limitations

- The heavy-metal group contained only 10 matched isolates, making the effect-size estimate imprecise.
- BacDive is biased toward culturable and described strains and may underrepresent environmental diversity and metal-tolerant extremophiles.
- Species-level matching is lossy because BacDive and GTDB use different species definitions.
- Genome-size normalization reduces, but may not eliminate, confounding between metal scores, genome complexity, and taxonomy.
- The metal-utilization dataset is too small for reliable validation.

## Future Directions

1. Match BacDive GCA accessions directly to pangenome genome IDs to recover strains missed by species-name matching.
2. Integrate ENIGMA CORAL data from the Oak Ridge metal-contaminated site for complementary field validation.
3. Test whether specific metal-tolerance gene families predict environments contaminated by particular metals.
4. Expand BacDive phenotype extraction to include MIC, growth-inhibition, and other metal-tolerance measurements.

## Source Notebooks

- `01_bacdive_pangenome_bridge.ipynb` — BacDive-to-pangenome matching.
- `02_environment_metal_scores.ipynb` — environment comparisons, power analysis, and phylum-stratified tests.
- `03_metal_utilization.ipynb` — exploratory phenotype validation.

## Related Concepts
- [[concepts/organism-specificity]]
- [[concepts/environmental-resistome]]
- [[concepts/annotation-gap]]

## Entities
- [[entities/kegg]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/berdl]]
