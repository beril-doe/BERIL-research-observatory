---
type: "Summary"
description: "Tests whether lab metal tolerance predicts Oak Ridge groundwater ecology"
doc_type: short
full_text: "sources/lab_field_ecology__REPORT.md"
---

# Lab Fitness Predicts Field Ecology at Oak Ridge

## Overview

This report compares laboratory fitness measurements from the [[entities/fitness-browser]] with field microbial community composition and geochemistry from 108 Oak Ridge groundwater sites in the [[entities/enigma-coral]] dataset. It tests whether aggregate lab [[concepts/environmental-metal-tolerance]] predicts genus-level abundance across uranium contamination gradients and finds that field ecology is shaped by broader ecological and geochemical factors.

## Key Findings

- Of 26 genera represented in the Fitness Browser, 14 were detected in Oak Ridge groundwater communities using 16S amplicon sequencing.
- The most prevalent detected genera were *Sphingomonas* (93% of 108 sites), *Pseudomonas* (91%), and *Caulobacter* (82%). *Desulfovibrio*, an ENIGMA model organism, occurred at 34% of sites and reached a maximum relative abundance of only 0.09%.
- Five of 11 sufficiently prevalent Fitness Browser genera showed significant uranium-abundance correlations after Benjamini–Hochberg false-discovery-rate correction:
  - *Herbaspirillum* increased with uranium (Spearman rho = +0.336, q = 0.001).
  - *Bacteroides* increased with uranium (rho = +0.264, q = 0.013).
  - *Caulobacter* decreased with uranium (rho = −0.411, q = 1.1e-4).
  - *Sphingomonas* decreased with uranium (rho = −0.382, q = 2.5e-4).
  - *Pedobacter* decreased with uranium (rho = −0.266, q = 0.013).
- *Desulfovibrio* and *Pseudomonas* showed no significant uranium correlation, while *Azospirillum* was only marginal after correction. *Shewanella*, *Dechlorosoma*, and *Marinobacter* were excluded because they occurred at fewer than 10 sites.
- The aggregate lab metal-tolerance score had a positive but non-significant association with the high-uranium/low-uranium abundance ratio (Spearman rho = 0.503, p = 0.095, n = 12 genera). Thus, H1 was not supported, although the trend was directionally consistent with the prediction.
- Community composition differed between sites above and below the median uranium concentration. The shift was not simply an enrichment of metal-tolerant organisms; it also involved rare taxa, subsurface specialists, redox conditions, and carbon or energy sources.

## Interpretation

The report supports the hypothesis that laboratory fitness can translate to field ecology only partially. Genus-level abundance responds to uranium in both positive and negative directions, supporting ecological sorting along a contamination gradient, but a simple aggregate measure of laboratory metal tolerance does not explain field success. The proposed disconnect reflects several limitations of translating single-organism fitness to natural communities, including [[concepts/phenotype-resolution-matching]] and [[concepts/environmental-occupancy-vs-activity]]:

1. Field sites vary in pH, redox potential, carbon sources, sulfate, nitrate, and other variables in addition to uranium.
2. Competition, cross-feeding, and syntrophy can alter performance relative to isolated laboratory cultures.
3. 16S data provide genus-level resolution, whereas Fitness Browser measurements concern specific strains and organisms.
4. Point-in-time geochemistry may not represent the historical conditions that shaped community assembly.
5. The low abundance of *Desulfovibrio* makes field correlation estimates for this model organism unreliable.

The results are consistent with prior Oak Ridge studies linking contamination and low pH to selective microbial pressures, heavy-metal resistance acquired through [[concepts/horizontal-gene-transfer]], deterministic community succession after carbon amendment, and the limited predictability of coculture interactions from single-organism fitness data.

## Contribution and Limitations

The report presents a direct comparison between Fitness Browser laboratory fitness data and ENIGMA CORAL field communities across a geochemical gradient. It identifies *Caulobacter* and *Sphingomonas* as candidate indicators of uranium contamination and *Herbaspirillum* and *Bacteroides* as possible tolerant colonizers, but these ecological interpretations remain genus-level associations rather than strain-resolved mechanisms.

Important limitations include the inability of 16S data to match species or strains to Fitness Browser organisms, limited coverage of Oak Ridge geochemistry, temporal mismatch between measurements and community history, aggregation of multiple communities per sample, the crude aggregate tolerance metric, low statistical power for the 12-genus tolerance analysis, and uncontrolled confounding by other environmental variables. These limitations exemplify [[concepts/coverage-limited-inference]] and [[concepts/organism-specificity]].

## Data and Methods

The analysis used ENIGMA CORAL geochemistry, ASV counts, ASV taxonomy, and sample metadata extracted through Spark, together with Fitness Browser fitness statistics, organism mappings, and core/accessory genome links. Three notebooks extracted the data, constructed genus-by-site abundance matrices, and tested relationships between laboratory fitness, uranium concentration, and field abundance. The report generated site geochemistry, ASV, taxonomy, metadata, genus abundance, genus count, and Fitness Browser genus-mapping tables.

## Future Directions

- Use ENIGMA CORAL metagenomic, genome, or assembly data for species- and strain-level matching.
- Apply CCA or RDA to model community composition against uranium and multiple geochemical variables simultaneously.
- Replace aggregate tolerance with metal-specific fitness scores, including uranium-specific measurements.
- Test whether temporal changes in geochemistry track community changes across sampling dates.
- Add *Rhodanobacter*, a dominant contaminated-aquifer genus absent from the Fitness Browser, as a priority target for future laboratory fitness profiling.

## Related Concepts
- [[concepts/genome-ecology-validation]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/evidence-triangulation]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/redox-zonation]]
- [[concepts/pangenome-integration]]

- [[concepts/environmental-metal-tolerance]]
- [[concepts/coverage-limited-inference]]
- [[concepts/organism-specificity]]
- [[concepts/phenotype-resolution-matching]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/subsurface-microbial-specialization]]
- [[entities/enigma-coral]]
- [[entities/fitness-browser]]
- [[entities/oak-ridge]]
- [[entities/uranium]]

## Entities
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/gtdb]]
- [[entities/bacdive]]
