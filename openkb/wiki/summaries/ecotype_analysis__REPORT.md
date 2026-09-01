---
type: "Summary"
description: "Tests whether environment or phylogeny better explains bacterial gene content."
doc_type: short
full_text: "sources/ecotype_analysis__REPORT.md"
---

# Ecotype Correlation Analysis

## Overview

This report evaluates whether environmental similarity or phylogenetic relatedness better predicts gene-content similarity across bacterial species. The analysis used environmental embeddings, genome metadata, geographic and isolation-source information, pangenome composition, and gene-cluster profiles from the `kbase_ke_pangenome` database. It analyzed 172 species with sufficient environmental and phylogenetic data, drawn from 13,381 genomes across 224 initially targeted species.

## Key Findings

- Phylogeny generally had the stronger association with gene-content similarity. The median partial correlation was **0.0143 for phylogeny** versus **0.0025 for environment**.
- Phylogeny dominated in **60.5%** of species, while environment dominated in **39.5%**.
- Only **12 species (7.0%)** showed a significant positive environmental effect, and **4 species (2.3%)** showed a significant negative effect; **156 species (90.7%)** showed no significant environmental effect.
- Environmental and host-associated bacteria did not differ significantly in environmental effects (**p=0.66**).

These results support the [[concepts/phylogenetic-confounding]] hypothesis that vertical inheritance and clonal ancestry often structure genome-wide gene content more strongly than broad environmental similarity. They also suggest that ecological adaptation may affect particular gene subsets rather than whole-genome gene content.

## Interpretation

The predominance of phylogenetic signal is consistent with literature emphasizing the role of clonal ancestry in within-species genomic variation. The weak genome-wide environmental signal is also compatible with the hypothesis that [[concepts/horizontal-gene-transfer]] and ecological selection act disproportionately on specific loci or functional categories rather than uniformly across genomes.

The report cautions that [[entities/alphaearth-environmental-embeddings]] cover only **28.4% of the genome set**, potentially limiting environmental signal detection. Geographic coordinates are frequently missing or imprecise, and coordinates for host-associated organisms may represent collection sites rather than their actual microenvironments. In addition, [[entities/partial-correlation]] between distance matrices assumes linear relationships and may miss nonlinear ecological effects. These constraints mean that weak environmental effects should not be interpreted as evidence that environment has no role in bacterial diversification.

## Data and Methods

The analysis combined:

- `alphaearth_embeddings` for environmental representations associated with geographic coordinates;
- `genome` and `ncbi_env` for genome, taxonomy, environmental, and isolation-source metadata;
- `pangenome` and `gene_cluster` for species-level gene-content profiles;
- [[entities/average-nucleotide-identity]] distance matrices for phylogenetic or genomic relatedness comparisons.

Two notebooks supported the work: `01_data_extraction.ipynb` extracted embeddings, ANI data, and gene clusters, while `02_ecotype_correlation_analysis.ipynb` computed correlations and generated the figures. Outputs included species-level correlation results, ecological category assignments, embedding diversity and coverage statistics, expanded genome metadata, and per-species gene-cluster profiles.

## Future Directions

1. Test environmental effects within specific functional categories, especially COG categories such as V-Defense and L-Mobile, to determine whether environment-sensitive signals are masked at the whole-genome level.
2. Compare alternative embedding distances and direct environmental metadata to assess whether environmental representation contributes to weak associations.
3. Identify ecotype clusters and compare gene content within species and between ecotypes.
4. Use nonlinear association methods or improved microenvironmental metadata to address limitations of geographic and linear-distance proxies.

## Related Concepts
- [[concepts/organism-specificity]]
- [[concepts/microbiome-ecotype-portability]]

- [[concepts/phylogenetic-confounding]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/pangenome-integration]]
- [[concepts/genome-ecology-validation]]