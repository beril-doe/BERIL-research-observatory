---
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/pitfalls.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/env_embedding_explorer__REPORT.md", "summaries/discoveries.md", "summaries/clay_confined_subsurface__REPORT.md", "summaries/cf_formulation_design__REPORT.md", "summaries/amr_strain_variation__REPORT.md"]
type: "Method"
description: "Genomic similarity method used to measure strain relatedness"
---

# Average Nucleotide Identity

## Overview

**Average Nucleotide Identity (ANI)** is a genome-comparison method used in this study to quantify genomic distances among strains within the same species. [src: amr_strain_variation]

**Aliases:** ANI; ANI distance

## Use in the AMR strain-variation study

The report extracted pairwise ANI distance matrices for eligible species and compared them with strain-level AMR Jaccard distance matrices using Mantel tests. [src: amr_strain_variation]

ANI-based phylogenetic analyses covered 1,261 species; species with more than 500 genomes were limited or excluded because of the computational cost of ANI extraction, including *Escherichia coli* and *Klebsiella pneumoniae*. [src: amr_strain_variation]

AMR profiles showed significant phylogenetic signal in 701 of 1,261 species (55.6%) after FDR correction, with a median Mantel correlation of 0.247. [src: amr_strain_variation] This result indicates that strains with greater genomic relatedness tended to have more similar AMR repertoires in the analyzed collection. [src: amr_strain_variation]

The ANI-based analysis also found stronger phylogenetic signal for non-core AMR genes than for core AMR genes: median Mantel r values were 0.222 and 0.117, respectively, with a paired-test p-value of 7.0e-16 across 489 species. [src: amr_strain_variation] The report interprets this pattern as consistent with lineage-restricted maintenance and vertical transmission of acquired resistance, while noting that near-universal core genes have limited Jaccard-distance variation that can suppress distance-based correlations. [src: amr_strain_variation]

## Related analyses

ANI provides the genomic-relatedness component of the study's [[concepts/phylogenetic-amr-structure]] analysis. [src: amr_strain_variation] The method was paired with AMR presence/absence matrices generated using [[entities/amrfinderplus]] and with AMR Jaccard distances to test whether resistance profiles track strain phylogeny. [src: amr_strain_variation]

The report identifies subsampling strategies for species with more than 500 genomes as a future direction for extending ANI-based Mantel tests. [src: amr_strain_variation]

## Source

- [[summaries/amr_strain_variation__REPORT]]

See also: [[summaries/cf_formulation_design__REPORT]]

See also: [[summaries/clay_confined_subsurface__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/env_embedding_explorer__REPORT]]

See also: [[summaries/gene_function_ecological_agora__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]