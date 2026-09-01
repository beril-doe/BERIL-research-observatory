---
type: "Summary"
description: "Metal concentrations are linked to soil microbial functional gene shifts, pending validation."
doc_type: short
full_text: "sources/soil_metal_functional_genomics__REPORT.md"
---

# Soil Metal Functional Genomics

## Overview

This preliminary report tests whether environmental metal concentrations are associated with shifts in microbial functional gene content across soil and other environments. It combines [[entities/spearman-correlation]], [[entities/db-rda]], and biome-stratified [[entities/phylogenetic-generalized-least-squares]] (PGLS). [[concepts/environmental-metal-tolerance]]

## Key Findings

- Across 51,748 soil samples, 2,355 significant COG–metal associations were identified at FDR < 0.05 across Cu, Co, Cr, Ni, Zn, Pb, As, Cd, and Hg. Chromium and lead produced the strongest signals, while ABC/RND transporters and biosynthesis genes dominated top associations. [src: soil_metal_functional_genomics]
- In a copper-specific analysis of 7,566 samples with nearby KBase genomes within 10 km, 116 COGs were significant at FDR < 0.05. Positive associations included cell-division and nucleotide-transport COGs; negative associations included energy-production COGs, suggesting an energetic trade-off under copper stress. [src: soil_metal_functional_genomics]
- db-RDA reported R² = 0.799 and p = 0.005 using 999 permutations, with metal concentrations explaining 80% of the variance in community COG profiles after conditioning on batch/project effects. [src: soil_metal_functional_genomics]
- Biome-stratified PGLS found distinct metal–COG relationships in soil, marine, and wastewater environments, supporting environment-specific responses rather than a universal resistance program. [src: soil_metal_functional_genomics]

## Interpretation

The observed association between soil metal concentrations and co-located microbial functional gene content is strong after conditioning on project accession, and the copper-associated enrichment of membrane transport functions together with depletion of energy-production functions is consistent with known mechanisms of copper toxicity. These results are observational and do not establish that individual metals caused the functional shifts. [src: soil_metal_functional_genomics]

A central unresolved issue is [[concepts/metal-co-contamination-confounding]]: chromium, copper, lead, and zinc frequently covary in industrial soils. Consequently, apparent single-metal associations may reflect a general response to multi-metal stress rather than metal-specific effects. The report also notes that effect sizes have not been systematically audited, so statistical significance may not correspond to biologically meaningful association strength. [src: soil_metal_functional_genomics]

## Critical Assessment and Limitations

- The conditional db-RDA R² = 0.799 describes variance explained by metals in the residual community variation after project effects were removed. The unconditional metals-only R² is not reported and could be substantially lower. [src: soil_metal_functional_genomics]
- The 2,355 discoveries among 3,915 nominal metal-by-COG tests represent a high discovery rate. Because metals co-vary, test dependence may make the reported Benjamini–Hochberg FDR anti-conservative; the true FDR may be higher. [src: soil_metal_functional_genomics]
- The copper analysis uses a 10 km soil-to-genome proximity threshold. Some matched genomes may not be genuinely co-located with the measured soil sites, so associations require sensitivity testing at 5 km and 20 km. [[concepts/geospatial-coverage-gaps]] [src: soil_metal_functional_genomics]
- Required validation analyses depend on the `kescience_mgnify` and [[entities/kbase-ke-pangenome]] Spark tables. Local CSV files containing Spearman effect sizes or model residuals are unavailable. [src: soil_metal_functional_genomics]

## Pending Validation

1. Audit the Spearman ρ distribution for all 2,355 associations and flag associations with ρ < 0.05.
2. Test residual spatial autocorrelation using Moran’s I, followed by SEVM if spatial dependence is significant.
3. Fit partial correlation models such as `COG ~ Cr | Cu + Zn + Pb` to separate metal-specific effects from general multi-metal stress.
4. Classify significant COGs into resistance, stress, membrane, energy, and unknown functional categories.
5. Report the unconditional db-RDA R² for metals without project-accession conditioning alongside the conditional value.
6. Repeat copper analyses using 5 km and 20 km proximity thresholds.

## Open Questions

The report’s main testable hypothesis is that some COG–metal relationships are metal-specific, while others are shared responses to co-contamination. Resolving this requires partial-correlation models, effect-size distributions, spatial validation, and proximity-threshold sensitivity analyses run against the source Spark tables. [[concepts/evidence-triangulation]] [src: soil_metal_functional_genomics]

## Related Concepts
- [[concepts/shared-stress-biology]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/geographic-distance-decay]]
- [[concepts/genome-ecology-validation]]
- [[concepts/scalable-spark-data-analysis]]
- [[concepts/method-concordance]]

## Entities
- [[entities/berdl]]
- [[entities/gtdb]]
- [[entities/random-barcode-transposon-sequencing]]
