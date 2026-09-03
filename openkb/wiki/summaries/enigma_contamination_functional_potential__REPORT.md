---
type: "Summary"
description: "ENIGMA analysis tests contamination effects on inferred microbial functional potential"
doc_type: short
full_text: "sources/enigma_contamination_functional_potential__REPORT.md"
---

# Contamination Gradient vs Functional Potential in ENIGMA Communities

## Overview

This report presents a reproducible workflow for testing whether metal contamination gradients predict community-level functional potential in 108 ENIGMA samples. It links ENIGMA genus abundances to GTDB pangenome clades and eggNOG-derived COG features, then compares strict, relaxed, and species-proxy mapping modes. It focuses on environmental metal tolerance, [[concepts/functional-redundancy]], [[concepts/coverage-limited-inference]], and [[concepts/pangenome-integration]].

## Data and workflow

- ENIGMA overlap data included 108 samples with both geochemistry and community composition, 41,711 community taxon rows, 212 distinct communities, and 1,392 observed genera.
- The contamination index combined eight metals—arsenic, cadmium, chromium, copper, lead, nickel, uranium, and zinc—using per-metal `log1p` z-scores averaged by sample. Values ranged from -0.448 to 3.836, with median -0.271 and IQR [-0.363, 0.053].
- The taxonomy bridge parsed 27,690 GTDB species rows, mapping 530 of 1,392 observed genera and leaving 862 unmapped.
- Strict mapping produced 530 clades, relaxed mapping produced 7,380 clades, and the unique-genus species-proxy mode retained 150 clades.
- The bridge contained 8,242 rows and substantial ambiguity: some genera mapped to hundreds of clades, including *Pseudomonas* (433), *Streptomyces* (378), and *Prevotella* (358).
- Functional features were computed across three mapping modes, producing 3,630 feature rows and 324 site-level functional-score rows.

## Main findings

### Confirmatory tests were null

Predeclared genus-level Spearman tests found no robust monotonic relationship between contamination and `site_defense_score`:

- Relaxed mapping: rho = 0.0587, 95% bootstrap CI [-0.128, 0.250], p = 0.546, FDR q = 0.862.
- Strict mapping: rho = 0.0682, 95% bootstrap CI [-0.111, 0.253], p = 0.483, FDR q = 0.849.

The confirmatory endpoint remained non-significant across four contamination-index definitions: composite all-metals, uranium-only, top-three variance metals, and the first PCA component. All eight variant tests had q = 0.546.

### Exploratory defense associations depended on adjustment and coverage

Coverage-aware exploratory OLS models showed positive defense coefficients, but these were less consistently supported after global multiple-testing correction. For relaxed mapping, the coverage-adjusted coefficient was 0.000751 with 95% CI [0.000224, 0.001779], p = 0.000398, and q = 0.0462. The corresponding strict-mapping coefficient was 0.000640 with CI [0.000169, 0.001538], p = 0.00354, and q = 0.130.

Fraction-aware models also produced positive estimates, but q-values were 0.0838 for relaxed mapping and 0.130 for strict mapping. High-coverage subsets yielded defense p-values of 0.0207 and 0.00980 for relaxed and strict mapping, respectively, but q-values of 0.301 and 0.189. Most other functional outcomes were non-significant; the only reported exploratory exception was a strict-mapping high-coverage association between contamination and `site_stress_score` (rho = 0.2489, p = 0.0407).

### Fraction stratification weakened the apparent signal

Fraction-aware models used 212 sample-fraction rows: 106 from the `0.2_micron_filter` fraction and 106 from the `10_micron_filter` fraction. Within-fraction defense correlations were non-significant in both mapping modes and both fractions, with p-values from 0.767 to 0.898. Thus, the strongest apparent defense association was not robustly reproducible within individual community-fraction strata, highlighting [[concepts/coverage-limited-inference]] and the importance of multiple-testing correction.

### Higher taxonomic resolution was coverage-limited

The species-proxy mode restricted analysis to genera mapping to exactly one GTDB species clade. It retained only 150 unique-clade genera, compared with 530 mapped genera overall, and reduced mean mapped abundance fraction from 0.343 in strict/relaxed modes to 0.031. The defense trend was positive but non-significant (rho = 0.169, p = 0.081), and no high-coverage test was feasible at the threshold `mapped_abundance_fraction >= 0.25`.

This result suggests the hypothesis that higher-resolution functional inference could reveal finer-scale adaptation, but the current ENIGMA taxonomy and bridge do not provide sufficient mapped coverage to test it strongly. The finding motivates [[concepts/coverage-limited-inference]], [[concepts/annotation-gap]], and [[concepts/pangenome-integration]].

## Interpretation

Within this ENIGMA subset, contamination did not produce a robust community-wide shift in broad, genus-aggregated functional scores. The result is compatible with contamination-driven taxonomic turnover that is functionally redundant, pathway-specific, or expressed mainly at species or strain resolution. Broad COG-fraction proxies may dilute metal-resistance and metal-stress responses that would be detectable using curated gene sets or pathway-level summaries.

The report's evidence is strongest for a null confirmatory result: the null persisted across mapping modes and contamination-index definitions. Positive defense associations in adjusted models are exploratory and sensitive to coverage, fraction handling, covariates, and global FDR correction. They should not be treated as an established general contamination-response effect.

## Limitations

- ENIGMA taxonomy in the analyzed table reaches genus but not species or strain.
- A substantial fraction of observed genera was unmapped to the current pangenome bridge.
- Many-to-many genus-to-clade expansion creates ambiguity, with a long right tail in clade counts.
- COG-fraction features are coarse functional proxies rather than curated metal-response pathways.
- Site structure was represented by coarse `location_prefix` effects rather than hierarchical or random-effects models.
- Species-proxy analyses were severely constrained by low mapped abundance coverage.

## Future directions

1. Replace COG fractions with curated metal-stress, resistance, transport, and detoxification gene sets.
2. Obtain species- or strain-resolved ENIGMA taxonomy and compare functional inference gains against genus and species-proxy modes.
3. Model depth, location, sampling date, and compositional structure explicitly.
4. Investigate whether unmapped genera drive contamination gradients and expand the taxonomy bridge.
5. Use mixed-effects or hierarchical well/location models to test whether exploratory defense associations persist after richer site-structure control.

## Source

`enigma_contamination_functional_potential__REPORT`

## Related Concepts
- [[concepts/phylogenetic-confounding]]
- [[concepts/organism-specificity]]
- [[concepts/subsurface-microbial-specialization]]
- [[concepts/resource-darkness]]

## Entities
- [[entities/bacdive]]
- [[entities/kegg]]
