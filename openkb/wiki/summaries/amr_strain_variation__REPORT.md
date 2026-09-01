---
type: "Summary"
description: "Large-scale analysis shows structured AMR variation within bacterial species."
doc_type: short
full_text: "sources/amr_strain_variation__REPORT.md"
---

# Within-Species AMR Strain Variation

## Overview

This report analyzes within-species antimicrobial resistance (AMR) diversity across 1,305 bacterial species and 180,025 genomes using genome, AMR, ANI, environmental, and collection-date data from the KBase/BER Data Lakehouse. It shows that AMR repertoires vary extensively among strains, but the variation is structured by gene conservation class, co-inherited resistance islands, phylogeny, and—in some species—distinct AMR ecotypes.

## Key Findings

### Extensive but structured within-species variation

Of 37,444 AMR gene-species records, 51.3% were rare, 41.3% variable, and only 7.5% fixed within species. The median variability index was 0.526, and the median pairwise strain-level AMR Jaccard distance was 0.435. Atlas conservation classes aligned strongly with strain-level prevalence: 77.3% of Core AMR genes were fixed, whereas 78.7% of Singleton genes were rare and 57.3% of Auxiliary genes were variable. AMR variability was weakly negatively correlated with pangenome openness (Spearman rho = -0.193, p = 2.2e-12), potentially because open pangenomes accumulate genes below the rare-gene threshold. These findings extend the [[concepts/core-accessory-resistance]] framework to strain-level AMR variation.

### Resistance islands and co-inheritance

The analysis detected 1,517 resistance islands across 705 species, or 54% of analyzed species. Islands contained a mean of 6.2 genes, a median of 4, and a maximum of 43; their mean phi coefficient was 0.827, indicating tight co-occurrence. Most islands (1,343/1,517; 88%) combined genes from multiple resistance mechanisms. Efflux components occurred in 954 islands, enzymatic-inactivation genes in 698, oxidoreductases in 694, and regulatory genes in 502. The results support [[concepts/resistance-islands]] as an important organizing principle for AMR repertoires, while the report cautions that co-occurrence does not establish co-selection or functional synergy.

### Phylogenetic structure of AMR profiles

Among 1,261 species tested with [[entities/average-nucleotide-identity]]-based Mantel analyses, 701 (55.6%) showed significant AMR phylogenetic signal after FDR correction. The median Mantel r for all AMR genes was 0.247, and 87.8% of species had positive correlations, indicating that closely related strains tend to share more AMR genes. Putatively acquired, non-core genes showed stronger signal than core genes (median r = 0.222 versus 0.117; paired t-test t = -8.35, p = 7.0e-16, n = 489). This may indicate stable clonal maintenance and vertical transmission after acquisition, although the comparison is partly affected by the near-universal prevalence of core genes, which suppresses distance-based variation. This finding connects to [[concepts/phylogenetic-amr-structure]].

### AMR ecotypes

Of 974 species with at least 15 genomes, 190 (19.5%) formed at least two AMR ecotypes using UMAP and DBSCAN clustering, with a median silhouette score of 0.620. Environmental association testing was severely underpowered: only two species met strict expected-frequency criteria because 52.7% of genomes lacked a classifiable isolation source. Case studies of [[entities/klebsiella-pneumoniae]], [[entities/staphylococcus-aureus]], and [[entities/salmonella-enterica]] nevertheless showed visible environmental structuring. The report treats environment-linked ecotypes as a promising but incompletely tested form of AMR organization.

### Temporal trends were unresolved

None of 513 species with at least 20 genomes spanning at least three post-1990 years showed a significant AMR gene-count trend after Benjamini-Hochberg correction. Positive and negative slopes were nearly balanced (251 versus 262). The report interprets this null result cautiously because only 70% of genomes had parseable dates and collection metadata were sparse; it should not be taken as evidence that AMR accumulation lacks temporal dynamics.

### Environment and AMR burden

Host-associated species carried more AMR genes per genome than terrestrial or aquatic species in both environmental classification approaches (Kruskal-Wallis, p < 0.05). The NCBI keyword classifier assigned environments to 1,190 of 1,307 species (91%), while the BacDive approximation classified 459 (35%). Both methods identified human-clinical isolates as having the highest AMR burden, but both classifications were approximate and affected by collection bias. These results contribute to the [[concepts/environmental-resistome]] perspective.

## Interpretation

The report's central conclusion is that within-species AMR variation is extensive but non-random. Resistance genes are organized into tightly co-inherited multi-mechanism modules, are often distributed along phylogenetic lineages, and can form strain clusters that may correspond to ecological niches. The stronger phylogenetic signal of non-core genes challenges a simple model in which horizontally acquired resistance is randomly distributed across a species. A more plausible hypothesis is that acquisition is followed by lineage-restricted maintenance and vertical transmission, although genomic-context data and explicit transfer analyses are needed to distinguish clonal inheritance from repeated transfer among close relatives.

The scale of the analysis extends observations previously made in individual pathogen species to a broad bacterial survey. It also suggests that AMR surveillance may benefit from tracking clonal lineages and resistance modules, rather than monitoring individual genes alone.

## Limitations and Tensions

- The GTDB/NCBI collection is biased toward clinical and human-associated isolates, especially for [[entities/klebsiella-pneumoniae]], [[entities/staphylococcus-aureus]], and [[entities/escherichia-coli]].
- AMR detection depends on [[entities/amrfinderplus]] and may miss novel resistance mechanisms.
- Species with more than 500 genomes were excluded from some Mantel analyses, including [[entities/escherichia-coli]] and [[entities/klebsiella-pneumoniae]].
- Environmental labels from NCBI keywords and BacDive approximations are incomplete and inconsistently curated.
- Sparse collection dates limit temporal inference.
- Resistance-island co-occurrence may reflect physical linkage without proving co-selection or functional complementarity.
- The core/non-core phylogenetic comparison contains a metric-related tension: core genes have lower observed signal partly because near-universal prevalence leaves little Jaccard variation, not necessarily because core resistance is less biologically constrained.

## Data and Analyses

The report generated genome-by-AMR matrices for 1,305 species, prevalence and variability metrics for 37,444 AMR gene-species records, 1,517 resistance-island records, 1,261 Mantel results, 974 ecotype summaries, 513 temporal regressions, and an integrated per-species summary. Analyses included prevalence classification, Jaccard and entropy metrics, phi-based co-occurrence clustering, ANI-AMR Mantel tests, UMAP/DBSCAN ecotype detection, temporal regression, and environment-AMR comparisons.

## Future Directions

1. Run ANI-based Mantel tests on mega-species using principled subsampling strategies.
2. Curate collection dates and isolation-source metadata to improve temporal and ecotype tests.
3. Map resistance islands to plasmids, chromosomes, integrons, and insertion sequences.
4. Compare AMR ecotypes with virulence-factor and metabolic-pathway variation.
5. Use island co-occurrence structure to predict likely future co-acquisition of resistance genes.
6. Produce detailed AMR and clinical-metadata case studies for [[entities/klebsiella-pneumoniae]], [[entities/escherichia-coli]], [[entities/staphylococcus-aureus]], [[entities/pseudomonas-aeruginosa]], [[entities/salmonella-enterica]], and [[entities/acinetobacter-baumannii]].

## Related Concepts
- [[concepts/organism-specificity]]
- [[concepts/pangenome-integration]]
- [[concepts/annotation-gap]]

## Entities
- [[entities/berdl]]
- [[entities/gtdb]]
- [[entities/streptococcus-pneumoniae]]
- [[entities/mycobacterium-tuberculosis]]
