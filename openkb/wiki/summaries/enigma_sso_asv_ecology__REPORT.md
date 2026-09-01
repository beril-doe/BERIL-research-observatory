---
type: "Summary"
description: "Maps SSO microbial ecology to plume flow, depth, redox gradients, and stable spatial structure."
doc_type: short
full_text: "sources/enigma_sso_asv_ecology__REPORT.md"
---

# SSO Subsurface Community Ecology

## Overview

This report analyzes 16S ASV communities from the SSO 3×3 well grid to determine how microbial composition varies across meter-scale space, hydrogeological depth zones, functional gradients, groundwater versus sediment, and a 9-day groundwater time series. Its central interpretation is that a contamination plume entering from the northeast and moving southwest structures community composition through the saturated zone. This provides a testable model of [[concepts/contamination-plume-microbiology]] and subsurface microbial specialization, but direct geochemical confirmation is still absent.

## Key findings

- Sediment communities exhibit significant distance-decay across the approximately 6 m grid (Mantel Spearman ρ = 0.323, p = 0.029; mean Bray-Curtis dissimilarity = 0.747). Turnover is more aligned with the east-west axis than with the uphill-downhill direction, suggesting lateral hydrogeological or plume-related structure rather than simple topographic control.
- U3, M6, and L7 form an unusually similar northeast-to-southwest corridor. Their pairwise Bray-Curtis dissimilarities are 0.558, 0.615, and 0.646, respectively, supporting the hypothesis that they share exposure to a plume flow path.
- Hydrogeological zone explains 27.5% of sample-level community variance (PERMANOVA F = 4.05, p = 0.0001), whereas well identity explains 19.2% and is not significant (F = 0.80, p = 0.979). Samples from different depths within a well are more dissimilar than samples from the same zone across wells, indicating that vertical position—especially intersection with the saturated zone—dominates horizontal location.
- Ten of 12 dominant phyla have significant depth associations. Chloroflexi, Patescibacteria, Myxococcota, and Spirochaetota are shallow-enriched, while Firmicutes, WPS-2, Bacteroidota, and Proteobacteria are deep-enriched. These patterns support hydrogeological depth zonation.
- Taxonomy-based functional inference places putative redox processes across the grid. U3 is associated with iron oxidation and nitrification, M5 has the highest inferred denitrification abundance (7.7%, associated with [[entities/rhodanobacter]]), U1 has an iron-reduction hotspot, M4 has sulfur oxidation and methanotrophy, and L9 has the highest fermentation signal (5.3%). M6 has the lowest oxidative-process signals and is interpreted as an anaerobic plume-core or “dead-zone” site.
- Groundwater and sediment communities differ substantially within wells (median Bray-Curtis dissimilarity = 0.424; within-well range = 0.364–0.450). Groundwater is enriched in putative plume-associated taxa including [[entities/rhodanobacter]] (2.9×), [[entities/gallionella]] (8.9×), and [[entities/sideroxydans]] (7.0×), whereas sediment is enriched in attached anaerobes including [[entities/anaeromyxobacter]], [[entities/arcobacter]], and [[entities/ca-methanoperedens]]. This supports [[concepts/attached-versus-planktonic-microbial-communities]].
- Guild co-occurrence patterns are consistent with redox separation and anaerobic food-web coupling: nitrifiers and iron oxidizers correlate strongly (ρ = +0.95), syntrophs and fermenters correlate positively (ρ = +0.55), fermenters and *Bdellovibrio*-associated predation correlate at ρ = +0.85, and denitrifiers are negatively associated with syntrophs (ρ = −0.67). These are inferred ecological associations, not demonstrated interactions.
- Groundwater community structure is stable over the 9-day interval from September 9 to September 18, 2024. Well identity explains 49.9% of variance (p = 0.001), date explains 0.8% (p = 0.998), and the date-to-date Mantel correlation is ρ = 0.867 (p = 0.001). The result strengthens the interpretation that observed spatial patterns reflect persistent environmental structure at this timescale; it does not establish long-term sediment stability.

## Plume model

The report proposes a northeast-to-southwest contamination plume originating near [[entities/oak-ridge-reservation-area-3]]. The plume model explains the corridor of similar communities, the stronger lateral than hillslope pattern, the dominance of depth over well identity, and the inferred progression from oxidative processes near U3 through denitrification near M5 toward fermentation near L9. The model is explicitly provisional because SSO geochemistry has not been loaded from the 221 registered CORAL samples.

The highest-priority predictions are that nitrate, acidity, and metal concentrations should reveal a northeast-to-southwest gradient; nearby EU/ED wells should show an approaching plume; pump-test groundwater should show a *Rhodanobacter* maximum at M5; and M6 isolate genomes should encode anaerobic metabolisms. These predictions connect the report to [[concepts/redox-zonation]], environmental metal tolerance, and contamination-plume microbiology.

## Data and analytical scope

The analysis used SSO sediment and groundwater ASV data from the `enigma_coral` collection, including community, sample, location, and brick data. Sediment analysis included 9 wells, 23,458 ASVs, and 37 sediment core samples aggregated at the well level. Functional inference covered 22 class-level trait categories with 78% coverage and 65 annotated genera across 12 process categories, but genus-level annotations covered only 21% of total reads.

Analyses included Bray-Curtis dissimilarity, Mantel tests, NMDS, Procrustes analysis, PERMANOVA, depth–phylum correlations, spatial trait mapping, guild co-occurrence analysis, and groundwater–sediment comparisons. The report recommends weighted UniFrac using the available ASV sequences and shotgun metagenomics to test whether inferred functions are supported by phylogenetic and genomic evidence.

## Limitations

- No direct measurements of SSO nitrate, pH, metals, carbon, or isotopes were integrated, so plume and redox interpretations remain hypotheses based primarily on community patterns.
- Sediment was sampled once in February–March 2023, while groundwater was sampled in September 2024; the 18-month offset confounds material type and time.
- Groundwater ASV data cover only five of nine wells and omit the key proposed plume-entry site U3 and denitrification hotspot M5.
- Species-level classification is approximately 0%, and genus-level classification covers only 44% of sediment reads; trait assignments are literature-based rather than direct functional measurements.
- Guild correlations across nine wells cannot by themselves demonstrate metabolic interactions or causality.

## Follow-up work

1. Load the 221 SSO geochemistry samples into CORAL and test community associations with nitrate, pH, metals, carbon, and isotopes.
2. Extract pump-test ASV data from bricks 460–462 to evaluate the M5 denitrification prediction and add a March 2024 temporal point.
3. Use weighted UniFrac to test whether phylogenetic community turnover strengthens the Bray-Curtis plume pattern.
4. Generate metagenomes at matched spatial locations to validate redox and nitrogen-cycle functions, especially in the currently unclassified reads.
5. Sample sediment and groundwater repeatedly across seasons to distinguish persistent plume structure from temporal dynamics.

## Source

[[summaries/enigma_sso_asv_ecology__REPORT]]

## Related Concepts
- [[concepts/subsurface-microbial-specialization]]
- [[concepts/annotation-gap]]
- [[concepts/functional-redundancy]]
- [[concepts/organism-specificity]]
- [[concepts/multi-omics-integration]]

## Entities
- [[entities/berdl]]
- [[entities/gtdb]]
- [[entities/random-barcode-transposon-sequencing]]
