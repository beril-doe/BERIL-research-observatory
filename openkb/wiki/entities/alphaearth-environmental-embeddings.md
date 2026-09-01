---
sources: ["summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md"]
type: "Dataset"
description: "Environmental embeddings linking ecological context to bacterial AMR patterns"
---

# AlphaEarth Environmental Embeddings

## What it is

AlphaEarth Environmental Embeddings is a dataset of continuous environmental feature vectors used to represent ecological conditions associated with bacterial species. [src: amr_environmental_resistome, amr_pangenome_atlas]

The embeddings provide a supplementary alternative to discrete environment categories such as clinical, soil, aquatic, and host-associated. [src: amr_environmental_resistome, amr_pangenome_atlas] Their opaque dimensions provide broad environmental signals but limited direct biological interpretability. [src: amr_environmental_resistome]

## Use in environmental resistome analyses

The [[summaries/amr_environmental_resistome__REPORT]] linked species-level AMR profiles to AlphaEarth embeddings for **2,659 species** with both data types available. [src: amr_environmental_resistome] The [[summaries/amr_pangenome_atlas__REPORT]] analyzed **2,684 species** with at least three genomes and embeddings, indicating a difference in analytical inclusion criteria or data snapshot that should be retained rather than silently reconciled. [src: amr_pangenome_atlas]

In the environmental resistome analysis:

- **52 of 64 embedding dimensions** correlated with AMR diversity at FDR < 0.05. [src: amr_environmental_resistome]
- The strongest reported association was for dimension A34, with Spearman rho = **+0.24**. [src: amr_environmental_resistome]
- A Mantel test found that environmental distance, calculated as cosine distance between embeddings, predicted AMR mechanism-profile distance, calculated using Bray–Curtis dissimilarity; the association was **r = 0.098, p = 0.001**. [src: amr_environmental_resistome]
- Stratified Mantel correlations were **0.177** for clinical species, **0.129** for soil species, and **0.061** for aquatic species. [src: amr_environmental_resistome]

The pan-bacterial AMR analysis reported that environmental diversity strongly predicted AMR count, with Spearman rho = **0.466** and p = **1.6e-144**, and that environmental diversity was associated with a lower AMR core fraction, with rho = **-0.173** and p = **1.8e-19**. [src: amr_pangenome_atlas] These findings extend the earlier mechanism-composition analysis from environmental similarity to species-level AMR abundance and conservation. [src: amr_pangenome_atlas]

Together, the results support the [[concepts/environmental-resistome]] view that ecological context is associated with AMR gene content, mechanism composition, and the balance between core and accessory resistance. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Coverage and limitations

Only 28% of genomes had usable AlphaEarth environmental embeddings in the environmental resistome analysis, restricting the supplementary sample to 2,659 species. [src: amr_environmental_resistome] The pan-bacterial AMR analysis included 2,684 species with at least three genomes and embeddings, but did not establish that this difference represents the same filtering universe. [src: amr_pangenome_atlas]

The embedding dimensions are not directly interpretable as named environmental variables, limiting conclusions about which specific ecological conditions drive the observed associations. [src: amr_environmental_resistome] The pan-bacterial analysis also notes that AlphaEarth coverage is biased toward genomes with geographic metadata. [src: amr_pangenome_atlas]

The embedding analyses demonstrate correlation rather than causation and do not by themselves establish that environmental conditions select for particular AMR mechanisms or directly cause resistance-gene acquisition. [src: amr_environmental_resistome, amr_pangenome_atlas] The reported association between environmental diversity and AMR accumulation is therefore best treated as support for the hypothesis that broader or more heterogeneous niches create greater opportunities for resistance acquisition, rather than as an established causal mechanism. [src: amr_pangenome_atlas]

The dataset's main value is as a continuous validation and extension of environment–AMR structure identified through categorical comparisons. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Related concepts

- [[concepts/environmental-resistome]]
- [[concepts/core-accessory-resistance]]
- [[entities/berdl]]
