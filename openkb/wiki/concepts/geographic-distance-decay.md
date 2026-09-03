---
type: "Concept"
sources: ["summaries/soil_metal_functional_genomics__REPORT.md", "summaries/metal_resistance_global_biogeography__REPORT.md", "summaries/env_embedding_explorer__REPORT.md"]
description: "Microbial similarity declines with geographic distance through spatially varying environments."
---

# Geographic Distance-Decay in Microbial Ecology

## Definition

Geographic distance-decay is the tendency for microbial communities or genome-derived features to become less similar as the geographic distance between sampling locations increases. In microbial ecology, this pattern can reflect spatially autocorrelated environmental conditions, dispersal limitation, environmental selection, or combinations of these processes. [src: env_embedding_explorer]

Distance-decay should not be treated as evidence that geographic distance itself is the causal driver. Geographic distance can instead serve as a proxy for differences in climate, vegetation, land use, habitat chemistry, or host-associated settings. Separating these explanations requires environmental measurements, phylogenetic controls, and explicit tests of dispersal and spatial structure. [src: env_embedding_explorer]

## Evidence from AlphaEarth embeddings

The [[summaries/env_embedding_explorer__REPORT]] analyzed 50,000 sampled genome pairs with good-quality coordinates and found that mean AlphaEarth embedding cosine distance increased monotonically with geographic distance. [src: env_embedding_explorer]

| Geographic distance | Mean cosine distance | Number of pairs |
|---|---:|---:|
| <100 km | 0.41 | 231 |
| 100–500 km | 0.51 | 1,058 |
| 500–1K km | 0.56 | 2,016 |
| 1K–2K km | 0.66 | 3,779 |
| 2K–5K km | 0.78 | 5,824 |
| 5K–10K km | 0.80 | 20,935 |
| 10K–20K km | 0.82 | 16,107 |

The relationship was strongest at short distances, especially below 2,000 km, and approached a plateau above approximately 5,000 km. [src: env_embedding_explorer] This pattern suggests that the embeddings capture spatially varying environmental context rather than unstructured noise, while the plateau indicates that additional geographic separation produces diminishing changes in the embedding representation. [src: env_embedding_explorer]

The environmental interpretation is plausible because AlphaEarth embeddings are derived from satellite imagery associated with genome sampling locations and may encode features such as climate, vegetation, land use, and urbanization. [src: env_embedding_explorer] However, the report did not directly validate individual embedding dimensions against environmental measurements, so the contribution of each feature remains unresolved. [src: env_embedding_explorer]

## Environmental context changes the strength of decay

Distance-decay was substantially stronger for environmental samples than for human-associated samples. [src: env_embedding_explorer] Among environmental samples, mean cosine distance increased from 0.27 for pairs less than 100 km apart to 0.90 for pairs more than 10,000 km apart, a 3.4-fold ratio. [src: env_embedding_explorer] Among human-associated samples, the corresponding values were 0.37 and 0.75, a 2.0-fold ratio. [src: env_embedding_explorer]

This contrast supports the hypothesis that natural environments produce greater geographic differentiation in satellite-derived context than hospitals and other urban settings, which may appear more similar across regions. [src: env_embedding_explorer] It also shows why pooled distance-decay estimates can conceal important habitat-specific patterns. [src: env_embedding_explorer]

The finding connects geographic distance-decay with [[concepts/environmental-metadata-harmonization]]: reliable environmental categories are needed to stratify samples and distinguish natural habitat effects from clinical, urban, or institutional sampling contexts. [src: env_embedding_explorer]

## Relationship to microbial community ecology

The report places the embedding pattern within the broader biogeographic expectation that community similarity declines with geographic separation. [src: env_embedding_explorer] Its environmental-only result is also consistent with the report's cited literature suggesting that environmental variation can explain microbial community structure more strongly than geographic separation alone in some systems. [src: env_embedding_explorer]

The observed plateau at intercontinental distances suggests that the embedding signal is more closely related to environmental similarity than to a linear effect of distance. [src: env_embedding_explorer] This interpretation is compatible with [[concepts/phylogenetic-confounding]] and [[concepts/microbiome-ecotype-portability]], because geographic patterns may reflect taxonomic composition, host or habitat filtering, and the portability of environment-associated genomic traits rather than geography alone. [src: env_embedding_explorer]

## Implications for gene-content and ecotype analyses

A prior ecotype analysis reported that AlphaEarth-based environment similarity was a weak predictor of gene content, with a median partial correlation of 0.0025. [src: env_embedding_explorer] The embedding explorer report proposes that the 38% human-associated fraction of the AlphaEarth subset may dilute an environment–gene-content relationship because human-associated samples have a flatter geographic embedding gradient. [src: env_embedding_explorer]

This is a hypothesis rather than an established correction. [src: env_embedding_explorer] A stronger test would repeat the analysis using environmental-only genomes, while controlling for phylogeny, sampling density, coordinate quality, and uneven representation of habitats. [src: env_embedding_explorer] Such analyses would connect geographic distance-decay to [[concepts/pangenome-integration]] and [[concepts/phylogenetic-confounding]].

## Confounders and evidence limits

The AlphaEarth embeddings were available for 83,287 of 293,059 genomes, or 28.4% of the pangenome database, so the analyzed sample is coverage-limited and may not represent the full genome collection. [src: env_embedding_explorer] Human-associated genomes comprised 38% of the embedding subset, and 17% of genomes were assigned to an “Other” environment category, limiting ecological stratification. [src: env_embedding_explorer]

Coordinate reliability is another major limitation. Of 83,286 genomes with coordinates, 60.2% were classified as good, 36.6% as suspicious coordinate clusters, and 3.3% as low-precision integer coordinates. [src: env_embedding_explorer] The heuristic incorrectly flags some legitimate field sites, so institutional-coordinate artifacts could either inflate or distort geographic patterns. [src: env_embedding_explorer]

Embedding distance also combines environmental, taxonomic, and potentially sampling-related structure. [src: env_embedding_explorer] UMAP analysis showed both environment-correlated clusters and taxonomic clustering, with the latter partly confounded by habitat—for example, some phyla were predominantly gut-associated. [src: env_embedding_explorer] Therefore, distance-decay in embedding space is evidence for geographic structure in the representation, but not by itself proof of microbial dispersal limitation or environmental selection.

## Tensions

### Geographic separation versus environmental selection

The embedding distance gradient increases with geographic distance, but the report interprets the embeddings as measurements of environmental context rather than raw geographic separation. [src: env_embedding_explorer] The resulting tension is whether geographic distance-decay primarily reflects dispersal limitation and spatial separation, or whether it reflects environmental turnover that happens to increase with distance. [src: env_embedding_explorer]

The stronger gradient in environmental samples and the plateau at intercontinental distances favor an environmental-context interpretation, but the report does not directly measure dispersal, climate, vegetation, or land use at the relevant locations. [src: env_embedding_explorer]

## Open Directions

- Compare pairwise embedding distance with matched climate, precipitation, temperature, NDVI, land-cover, and habitat variables to test whether environmental dissimilarity explains the geographic gradient better than distance alone. [src: env_embedding_explorer]
- Repeat the distance-decay analysis after excluding suspicious and low-precision coordinates, then compare effect sizes with the full dataset to quantify coordinate-artifact sensitivity. [src: env_embedding_explorer]
- Re-estimate decay curves separately for harmonized environmental categories and ENVO-derived categories to test whether the 3.4-fold environmental gradient is robust to classification method. [src: env_embedding_explorer]
- Fit partial Mantel, db-RDA, or comparable spatial models with geographic distance, environmental distance, phylogenetic distance, and sampling density to distinguish competing mechanisms. [src: env_embedding_explorer]
- Test whether accessory-gene similarity shows a stronger environmental distance-decay relationship among environmental-only genomes than in the pooled AlphaEarth subset. [src: env_embedding_explorer]

See also: [[summaries/metal_resistance_global_biogeography__REPORT]]

See also: [[summaries/soil_metal_functional_genomics__REPORT]]