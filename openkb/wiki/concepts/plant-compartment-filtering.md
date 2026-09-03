---
type: "Concept"
sources: ["summaries/plant_microbiome_ecotypes__REPORT.md"]
description: "Plant compartments impose small, measurable shifts in microbial functional profiles."
---

# Plant Compartments as Functional Filters

Plant compartments act as statistically detectable but weak functional filters on microbial communities. Root, rhizosphere, and phyllosphere communities differ in functional-profile centroids, while also differing in within-compartment dispersion. The evidence supports compartment-specific ecological selection, but not the claim that compartment identity explains most functional variation. [[concepts/plant-compartment-filtering]] [[summaries/plant_microbiome_ecotypes__REPORT]]

## Core Finding

Using the refined 17-marker panel and Jaccard distances across 607 plant-associated species from root, rhizosphere, and phyllosphere compartments, PERMANOVA estimated a total compartment effect of R² = 0.071 (pseudo-F = 23.2, p = 0.001; 999 permutations). db-RDA separated centroid location from dispersion and estimated a location-only R² = 0.060 (p = 0.001), meaning approximately 84% of the PERMANOVA effect reflected genuine shifts in compartment centroids. [src: plant_microbiome_ecotypes]

The effect is therefore biologically and statistically real but small: compartments explain approximately 6% of functional-profile variance after the refined analysis. Root, rhizosphere, and phyllosphere communities are functionally distinct in centroid terms, but compartment identity is only one of several forces shaping their genomic profiles. [src: plant_microbiome_ecotypes]

## Dispersion Is Part of the Ecological Signal

PERMDISP detected significant heterogeneity in within-compartment dispersion (F = 15.6, p = 0.001). Root-associated species were most tightly clustered, with a mean centroid distance of 0.452; phyllosphere species were intermediate at 0.503; and rhizosphere species were most variable at 0.528. [src: plant_microbiome_ecotypes]

This distinction matters because a significant PERMANOVA can reflect both differences in group centroids and differences in group spread. In this dataset, dispersion contributes approximately 16% of the total PERMANOVA R², while the larger share is attributable to centroid displacement. The compartment effect should therefore be interpreted as a combination of ecological filtering and unequal breadth of functional profiles, rather than as a purely location-based separation. [src: plant_microbiome_ecotypes]

## Why the Original Effect Was Overstated

The Phase 1 analysis reported a compartment PERMANOVA R² = 0.527 using a broader 25-marker panel. Sensitivity analysis excluding the three most genome-rich species per compartment reduced the estimate to R² = 0.072, an 86% reduction. The report attributes most of the original magnitude to the marker panel and uneven taxonomic sampling, especially a small number of dominant rhizobial and Pseudomonas clades, rather than to a community-wide compartment effect. [src: plant_microbiome_ecotypes]

The refined Phase 2b analysis reproduced the small effect on the full 607-species dataset, with PERMANOVA R² = 0.071 and db-RDA location-only R² = 0.060. This convergence indicates that the revised conclusion is not simply a consequence of reducing sample size. [src: plant_microbiome_ecotypes]

## Functional Patterns by Compartment

Earlier per-marker tests identified directional compartment associations even though the multivariate effect was small. In the original framework, root species showed strong enrichment for ACC deaminase (OR = 69.3), T3SS (OR = 65.6), nitrogen fixation (OR = 14.5), and quorum sensing (OR = 24.1), and 69 of 96 marker-by-compartment comparisons were significant. These enrichments support the presence of specific functional filters, but their interpretation is limited by taxonomic clustering and incomplete phylogenetic control. [src: plant_microbiome_ecotypes]

The report describes root-associated communities as enriched for rhizobial lineages such as Rhizobium, Mesorhizobium, and Bradyrhizobium, while Sphingomonas and Methylobacterium are prominent in the phyllosphere. Pseudomonas_E was the only genus with significant presence across all major compartments. These distributions are consistent with compartment-linked ecological strategies, including nitrogen fixation and root colonization in roots, and methylotrophic or surface-associated lifestyles in the phyllosphere. [src: plant_microbiome_ecotypes]

However, marker presence is not equivalent to demonstrated activity. The report's refined phylogenetic controls found that only nitrogen fixation, ACC deaminase, and T3SS survived the strictest within-genus label-shuffling test. Other associations, including phenazine, cell-wall-degrading enzymes, phosphate solubilization, and effectors, were supported by cluster-robust models but not by within-genus permutation, suggesting genus-scale or cassette-level enrichment rather than reliable species-level compartment specialization. [src: plant_microbiome_ecotypes]

## Interpretation

The evidence supports a layered model of compartment filtering:

1. **Compartment filtering is genuine but weak.** Centroid shifts are significant, yet account for only about 6% of variance. [src: plant_microbiome_ecotypes]
2. **Compartments differ in functional breadth.** Root communities are more tightly constrained, whereas rhizosphere communities are more heterogeneous. [src: plant_microbiome_ecotypes]
3. **Specific functions can be strongly enriched despite a small global effect.** Large odds ratios for individual markers do not imply that the entire functional profile is determined by compartment. [src: plant_microbiome_ecotypes]
4. **Taxonomic composition is a major confounder.** Many apparent plant-association signals are concentrated at the genus level, and broad marker panels can exaggerate multivariate separation. [src: plant_microbiome_ecotypes]
5. **Functional potential should not be equated with ecological outcome.** Shared systems such as T3SS may contribute to pathogenicity, symbiosis, or other interactions depending on host and environmental context. [src: plant_microbiome_ecotypes]

This interpretation connects compartment filtering to [[concepts/phylogenetic-confounding]], [[concepts/dual-nature-microbial-lifestyles]], and [[concepts/phenotype-resolution-matching]]. It also illustrates [[concepts/evidence-triangulation]]: the strongest conclusion comes from combining PERMANOVA, PERMDISP, db-RDA, marker-level tests, sensitivity analysis, and phylogenetic controls rather than relying on a single effect size. [src: plant_microbiome_ecotypes]

## Tensions

### Large Phase 1 effect versus small Phase 2b effect

The Phase 1 estimate of R² = 0.527 suggested a very strong compartment effect, whereas the corrected Phase 2b analysis estimated total R² = 0.071 and location-only R² = 0.060. The report resolves this as a methodological tension rather than a biological contradiction: the earlier estimate was highly sensitive to the broad marker panel and a few genome-rich species, while the refined analysis retained a smaller, robust signal. [src: plant_microbiome_ecotypes]

### Centroid separation versus dispersion heterogeneity

PERMDISP was significant, so group spread differs among compartments; however, db-RDA showed that approximately 84% of the PERMANOVA effect was location-only. The evidence therefore supports both genuine centroid shifts and unequal dispersion. Neither component should be ignored when comparing plant compartments. [src: plant_microbiome_ecotypes]

### Marker enrichment versus species-level specificity

Several markers are enriched in plant-associated or compartment-associated groups under regression models but fail within-genus label shuffling. This indicates that some apparent functional filters operate through the distribution of genera across compartments rather than through consistent species-level differences within genera. [src: plant_microbiome_ecotypes]

## Open Directions

- Apply a full tree-informed model or sparse phylogenetic approximation to test whether compartment effects remain after accounting for relationships below the genus level, addressing the gap left by genus clustering. [src: plant_microbiome_ecotypes]
- Expand endophyte sampling beyond 29 species so that all four compartments can be compared with adequate power. [src: plant_microbiome_ecotypes]
- Pair marker profiles with transcriptomic or proteomic measurements across matched root, rhizosphere, and phyllosphere isolates to determine which compartment-enriched functions are active. [src: plant_microbiome_ecotypes]
- Reanalyze compartment profiles using reaction-level or substrate-level metabolic features, because coarse marker and pathway categories may miss finer functional differentiation. [src: plant_microbiome_ecotypes]
- Test whether the higher rhizosphere dispersion reflects host species, soil environment, sampling design, or genuinely broader ecological niches using host-stratified and environment-matched comparisons. [src: plant_microbiome_ecotypes]