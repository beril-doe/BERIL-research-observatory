---
type: "Concept"
sources: ["summaries/prophage_amr_comobilization__REPORT.md", "summaries/discoveries.md", "summaries/bacdive_metal_validation__REPORT.md", "summaries/amr_strain_variation__REPORT.md"]
description: "AMR profiles often follow bacterial lineage structure within species."
---

# Phylogenetic Structure of AMR

## Overview

[[concepts/phylogenetic-amr-structure]] describes the tendency for antimicrobial-resistance (AMR) gene repertoires to track evolutionary relatedness among strains of the same species. In the within-species survey, AMR profiles were generally structured rather than randomly distributed: closely related strains tended to share more AMR genes. [[summaries/amr_strain_variation__REPORT]] [src: amr_strain_variation]

This pattern connects AMR variation to [[concepts/core-accessory-resistance]] and [[concepts/resistance-islands]]. Core and non-core genes differ in prevalence and statistical behavior, while tightly co-inherited resistance islands can create lineage-specific AMR signatures. [src: amr_strain_variation]

## Evidence from the strain-variation survey

ANI distance matrices and AMR Jaccard distance matrices were compared for 1,261 species. Significant phylogenetic signal was detected in 701 species (55.6%) after FDR correction, the median Mantel correlation across all AMR profiles was 0.247, and 87.8% of species showed positive correlations. [src: amr_strain_variation]

The results indicate that AMR repertoires are frequently organized along phylogenetic lineages: strains that are more closely related tend to have more similar resistance profiles. This is a broad comparative result across more than 1,000 species, rather than an inference from a single pathogen. [src: amr_strain_variation]

## Acquired versus intrinsic resistance

Putatively acquired, non-core AMR genes showed a stronger phylogenetic signal than core or intrinsic AMR genes. The median Mantel r was 0.222 for non-core genes and 0.117 for core genes; the paired comparison gave t = -8.35, p = 7.0e-16, with n = 489 species. [src: amr_strain_variation]

The finding is consistent with a model in which a lineage acquires a resistance element and subsequently maintains and vertically transmits it within that lineage. It also suggests that horizontal acquisition is not necessarily followed by random distribution across the species. However, this interpretation remains a hypothesis because the analysis measured similarity and phylogenetic association, not transfer events or genomic inheritance histories. [src: amr_strain_variation]

The lower signal for core genes should not be interpreted straightforwardly as weaker evolutionary constraint. Core genes are nearly universal by definition, so their AMR presence/absence profiles have limited Jaccard variation; this can suppress distance-based correlations such as Mantel r. [src: amr_strain_variation]

## Relationship to resistance islands

The survey identified 1,517 resistance islands across 705 species, with a mean within-island phi coefficient of 0.827. Most islands, 1,343 of 1,517 (88%), contained genes associated with multiple resistance mechanisms. [src: amr_strain_variation]

These tightly co-occurring modules provide a plausible genetic basis for lineage-specific AMR profiles: once a linked resistance element enters a lineage, multiple genes may be inherited together. The island analysis does not prove that the genes are co-selected or that their combined mechanisms provide functional synergy; physical linkage on a mobile element could produce the same co-occurrence pattern. [src: amr_strain_variation]

## Interpretation and significance

Phylogenetic structure changes how AMR surveillance can be interpreted. Monitoring individual resistance genes alone may miss the importance of clonal background, linked resistance modules, and lineage-restricted accumulation. The report therefore proposes that tracking resistant lineages and resistance islands may complement gene-centered surveillance. This is a strategic implication of the observed associations, not a directly tested surveillance outcome. [src: amr_strain_variation]

The result also refines a simple contrast between intrinsic resistance, which is expected to follow phylogeny, and acquired resistance, which is often assumed to be phylogenetically random. In this dataset, non-core AMR showed stronger signal, but the result is partly shaped by prevalence-dependent distance metrics and cannot by itself distinguish vertical inheritance from repeated horizontal transfer among close relatives. [src: amr_strain_variation]

## Limitations and Tensions

- ANI extraction was limited to species with no more than 500 genomes, excluding large datasets such as *Escherichia coli* and *Klebsiella pneumoniae* from the phylogenetic-signal analysis. [src: amr_strain_variation]
- AMR detection relied on AMRFinderPlus, so resistance mechanisms absent from that database could not contribute to the observed profiles. [src: amr_strain_variation]
- A positive AMR–phylogeny association is compatible with stable vertical inheritance, lineage-restricted horizontal transfer, or both; the reported analysis does not resolve these alternatives. [src: amr_strain_variation]
- The core-versus-non-core comparison has a metric-related tension: near-universal core genes have little presence/absence variance, which can reduce Mantel correlations independently of biological evolutionary history. [src: amr_strain_variation]

## Open Directions

1. Add plasmid, chromosome, integron, and insertion-sequence context to the 1,517 detected resistance islands to test whether phylogenetic signal is concentrated in particular mobile-element classes. [src: amr_strain_variation]
2. Apply ANI-based Mantel tests or lineage-aware models to mega-species, including *E. coli* and *K. pneumoniae*, using computationally controlled subsampling to determine whether the reported pattern generalizes to the largest populations. [src: amr_strain_variation]
3. Compare phylogenetic signal with explicit gene-transfer histories to distinguish vertical maintenance from repeated transfer among closely related strains. [src: amr_strain_variation]
4. Integrate AMR lineage structure with virulence and metabolic variation to test whether resistant clades also form broader ecological or phenotypic syndromes. [src: amr_strain_variation]

See also: [[summaries/bacdive_metal_validation__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/prophage_amr_comobilization__REPORT]]