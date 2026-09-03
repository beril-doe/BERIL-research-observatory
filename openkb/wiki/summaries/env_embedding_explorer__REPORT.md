---
type: "Summary"
description: "Characterizes AlphaEarth geographic signals, environmental structure, and sampling bias in BERDL."
doc_type: short
full_text: "sources/env_embedding_explorer__REPORT.md"
---

# AlphaEarth Embeddings, Geography & Environment Explorer

## Overview

This report characterizes 64-dimensional [[entities/alphaearth-environmental-embeddings]] derived from satellite imagery for 83,287 genomes in the BERDL pangenome database, examining their geographic, environmental, taxonomic, and metadata structure. It finds that embeddings capture meaningful spatially varying environmental context, but interpretation is strongly affected by clinical sampling bias, questionable coordinates, incomplete environmental metadata, and coverage limited to 28.4% of genomes, illustrating [[concepts/coverage-limited-inference]].

## Key findings

- **Environmental samples show a stronger geographic signal than human-associated samples.** For environmental samples, mean cosine distance increases from 0.27 at distances below 100 km to 0.90 above 10,000 km, a 3.4x ratio. Human-associated samples increase from 0.37 to 0.75, a 2.0x ratio. This suggests that natural landscapes create more differentiated embedding contexts than globally similar hospital and urban settings. This result contributes to [[concepts/geographic-distance-decay]].
- **Embedding distance increases monotonically with geographic distance.** Across 50,000 sampled genome pairs with good coordinates, mean cosine distance rises from 0.41 below 100 km to 0.82 at 10,000–20,000 km. The relationship is strongest below 2,000 km and plateaus beyond approximately 5,000 km, consistent with spatially autocorrelated environmental conditions rather than geographic distance alone.
- **The AlphaEarth subset is strongly human-associated.** Human clinical, gut, and other human-associated genomes comprise 31,525 genomes, or 38% of the 83,287-genome subset. Soil, marine, and freshwater categories each contain about 7%. Another 17% is classified as “Other,” including site-specific labels, generic terms, and uncaptured clinical sites. This bias may dilute environment–gene-content relationships and is relevant to [[concepts/coverage-limited-inference]] and [[concepts/microbiome-ecotype-portability]].
- **Coordinate quality is a major concern.** Of 83,286 genomes with coordinates, 50,109 (60.2%) were classified as good, 30,469 (36.6%) as suspicious clusters, and 2,708 (3.3%) as low-precision integer coordinates. Shared coordinates can represent institutional addresses, but the heuristic also flags legitimate field sites such as Rifle, Colorado, and Saanich Inlet. Coordinate quality should therefore be treated as an uncertainty layer in geographic analyses.
- **UMAP reveals environment-correlated structure.** [[entities/umap]] of valid embeddings identified substantial fine-scale structure, with [[entities/dbscan]] at eps=0.5 producing 320 clusters. Rare categories such as Air, Extreme, and Plant concentrate in a few clusters, whereas Human gut and Human clinical samples span many clusters, potentially reflecting geographic substructure.
- **Embedding space also contains taxonomic structure.** Phylum-level UMAP patterns show clustering, although this is confounded with environment; for example, Campylobacterota are predominantly gut-associated. Embeddings should not be interpreted as purely environmental representations without controlling for taxonomy, consistent with [[concepts/phylogenetic-confounding]] and [[concepts/organism-specificity]].

## Data coverage and harmonization

The AlphaEarth table covers 83,287 of 293,059 genomes. Of these, 79,449 have valid values in all 64 embedding dimensions, while 3,838 contain at least one NaN. Nearly all genomes have cleaned latitude/longitude and `geo_loc_name`; isolation source is available for 91.6%, host for 63.7%, and structured `env_broad_scale` for 41.8%.

A keyword-based mapping converted 5,774 distinct `isolation_source` values into 12 broad environmental categories. It captured 71% of genomes with an isolation-source label, while 17% remained “Other” and 12.5% were “Unknown.” The ENVO-based `env_broad_scale` field is more standardized but has lower coverage and often contains bare ontology identifiers or generic values. These results motivate a reusable [[concepts/environmental-metadata-harmonization]] workflow combining free-text classification with [[entities/envo]] fallback.

## Interpretation

The report supports the interpretation that AlphaEarth embeddings encode geographic and environmental context derived from satellite imagery, including likely climate, vegetation, land use, and urban/rural character. The stronger distance-decay pattern among environmental samples suggests that embeddings are most informative for environmental microbiology and least informative for clinical isolates. However, the findings are observational: geographic distance, environment, taxonomy, sampling intensity, and coordinate quality are not fully separated.

The report connects directly to the prior ecotype analysis result that AlphaEarth-based environment similarity was a weak predictor of gene content, with a median partial correlation of 0.0025. The authors hypothesize that the high proportion of human-associated genomes may partly explain this weak association. This hypothesis should be tested by repeating the analysis on environmental-only samples and controlling for [[concepts/phylogenetic-confounding]] and coordinate reliability.

## Limitations

- AlphaEarth coverage is limited to 28.4% of the pangenome and is likely non-random.
- Thirty-eight percent of the subset is human-associated, potentially distorting global environment comparisons.
- The coordinate-clustering heuristic cannot reliably distinguish institutional addresses from dense field sites.
- Keyword harmonization leaves a substantial “Other” category and may miss non-English or site-specific terms.
- UMAP and DBSCAN structure depends on projection and clustering parameters.
- The cause of NaN values in 4.6% of embeddings is unknown and may involve missing satellite imagery.
- Geographic distance is only a proxy for environmental difference; the plateau at intercontinental distances indicates that raw distance does not fully explain embedding variation.

## Open directions

1. Refine coordinate QC using isolation-source homogeneity and source diversity at each location.
2. Reclassify “Other” samples using clinical body-site terms, underground-laboratory labels, generic water terms, and ENVO metadata.
3. Repeat ecotype and gene-content analyses using environmental-only samples, with phylogenetic and coordinate-quality controls.
4. Correlate individual dimensions A00–A63 with latitude, temperature, precipitation, NDVI, and land-cover variables.
5. Compare keyword-derived environment categories with ENVO classifications on the overlapping 42% of genomes.
6. Test whether environmental genomes with similar AlphaEarth embeddings share more accessory genes after controlling for phylogeny.

## Supporting outputs

Generated resources include the merged `alphaearth_with_env.csv` table, coverage and raw isolation-source count tables, precomputed UMAP coordinates, interactive notebooks, geographic-distance curves, coordinate-quality maps, environment-category plots, and cluster composition visualizations.

## Related Concepts
- [[concepts/genome-ecology-validation]]
- [[concepts/cultivation-bias]]
- [[concepts/annotation-gap]]
- [[concepts/evidence-triangulation]]

## Entities
- [[entities/gtdb]]
- [[entities/fitness-browser]]
- [[entities/average-nucleotide-identity]]
