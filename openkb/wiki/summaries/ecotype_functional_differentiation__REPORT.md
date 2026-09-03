---
type: "Summary"
description: "Multi-species analysis shows ecotypes differ systematically in bacterial gene functions."
doc_type: short
full_text: "sources/ecotype_functional_differentiation__REPORT.md"
---

# Ecotype Functional Differentiation

## Overview

This study tests whether within-species gene-content ecotypes differ functionally rather than representing random pangenome variation. PCA and [[entities/kmeans-clustering]] clustering were applied to auxiliary gene presence/absence matrices for a stratified sample of bacterial species in the [[entities/berdl]] pangenome database, followed by COG-category enrichment tests. The results support widespread, functionally structured ecotype differentiation and connect within-species ecotype structure with [[concepts/pangenome-integration]].

## Study Design and Coverage

- Of 27,702 species in the BERDL pangenome database, 457 had at least 50 genomes and 456 remained eligible after COG annotation filtering.
- Fifteen species were sampled across genome-count bins; 12 produced valid ecotype clusters.
- The 12 species contained 1,820 assigned genomes and represented an average of 3.7 ecotypes per species, ranging from 2 to 6.
- Clustering used [[entities/principal-component-analysis]] with up to 50 components followed by [[entities/kmeans-clustering]] over k = 2–6. Valid clusters required at least two ecotypes with at least 10 genomes each and at least 20 assigned genomes overall.
- Silhouette scores were moderate overall (mean 0.215; median 0.174), indicating overlapping statistical populations rather than sharply discrete lineages.
- The clearest separation occurred in *Erwinia amylovora* (silhouette 0.468; 2 ecotypes) and *Bacteroides xylanisolvens* (0.366; 6 ecotypes). The weakest signals occurred in *Staphylococcus simulans* (0.118) and *Streptococcus pseudopneumoniae* (0.131).

## Main Findings

### Gene-content ecotypes are widespread

Valid gene-content ecotypes were identified in 12 of 15 sampled species (80%), supporting the view that within-species gene-content subpopulations are a general feature of bacterial pangenomes. The ecotypes should be interpreted as statistical tendencies in auxiliary gene content, not necessarily as discrete ecological or evolutionary lineages.

### COG functions differentiate between ecotypes

Across 257 species-by-COG tests, 170 (66.1%) were significant after BH-FDR correction at q < 0.05. Every one of the 12 species showed at least one significantly differentiated COG category, rejecting the hypothesis that ecotype gene-content differences are functionally random.

The most recurrent categories were:

- **E — Amino acid metabolism:** significant in 11/12 species (91.7%); mean effect 0.0120.
- **S — Unknown function:** significant in 11/12 species (91.7%); mean effect 0.0392.
- **V — Defense:** significant in 11/12 species (91.7%); mean effect 0.0078.
- **G — Carbohydrate metabolism:** significant in 10/12 species (83.3%); mean effect 0.0176.

Categories with weaker differentiation included **A** (RNA processing, 1/9), **B** (chromatin, 1/8), and **Z** (cytoskeleton, 2/6).

### Adaptive functions have larger effects than housekeeping functions

The results partially support the adaptive-function hypothesis. Adaptive categories V, P, G, E, Q, M, and K had a significance rate of 79.8% (67/84), compared with 68.8% (33/48) for housekeeping categories J, F, H, and C. However, the stronger result concerned magnitude: mean effect size was 0.0136 for adaptive categories and 0.0064 for housekeeping categories, a 2.13-fold difference. This difference was highly significant by one-sided Mann–Whitney U test (p = 2.53 x 10^-6).

Thus, both adaptive and housekeeping functions can differentiate between ecotypes, but adaptive categories—including defense, transport, secondary metabolism, and cell-wall functions—show larger proportional shifts. This pattern is consistent with selection acting on top of a baseline contribution from drift and demographic structure.

### Unknown-function and mobile-element-associated categories dominate effect size

Category **S** (unknown function) had the largest mean effect size (0.0392) and was significant in 11/12 species. Category **L** (replication, recombination, and repair) had the second-largest mean effect size (0.0337) and was significant in 9/12 species. Category L includes transposases, integrases, and other [[concepts/mobile-genetic-elements]] machinery, linking ecotype differentiation to [[concepts/horizontal-gene-transfer]] and the [[concepts/two-speed-genome]] pattern. The prominence of category S also indicates that many ecotype-associated genes remain poorly characterized, reinforcing the importance of the [[concepts/annotation-gap]].

## Biological Interpretation

The strongest recurrent differences involve environmental interaction: amino acid and carbohydrate metabolism, defense, cell-wall biosynthesis, and inorganic-ion transport. These functions are plausible targets of niche-specific selection, including differences in nutrient availability, phage exposure, and physicochemical conditions.

The study’s interpretation is deliberately moderate. Silhouette scores indicate that ecotypes overlap, and gene-content acquisition and loss are ongoing. The findings demonstrate functional structure in the observed clusters, but they do not by themselves establish that the clusters are ecologically adapted populations. Literature comparisons support links among defense islands, mobile elements, accessory genes, and niche differentiation, while the results extend single-species observations to 12 diverse species.

## Limitations and Tensions

- Only 12 species were analyzed successfully, out of 456 eligible species; the sample may not represent the full phylogenetic or ecological breadth of the database.
- KMeans was used because HDBSCAN was unavailable, and its spherical-cluster assumptions may affect ecotype definitions.
- Approximately 38% of gene clusters had COG annotations. The unannotated 62% may contain ecotype-specific adaptive genes, potentially biasing functional results toward annotated functions.
- Within-species phylogenetic structure was not controlled. Some ecotypes may reflect demographic or lineage structure rather than ecological specialization, a central [[concepts/phylogenetic-confounding]] issue.
- The largest mean effects were small: 0.0392 for S and 0.0337 for L, corresponding to roughly 3–4 percentage-point differences in COG proportions as described in the report.
- Two species were lost because of transient Spark S3 read errors, and query times ranged from 94 to 1642 seconds under cluster load.

The principal unresolved tension is whether gene-content ecotypes represent ecological adaptation, phylogenetic substructure, or a mixture of both. Core-genome phylogenies and environmental metadata are needed to separate these explanations.

## Data and Reproducibility

Generated datasets include 456 eligible species records, 1,820 genome-to-ecotype assignments, 12 clustering-statistics records, 894 ecotype COG profiles, and 257 differential-enrichment test results. The analysis was supported by notebooks for species selection, clustering and COG profiling, and differential enrichment, plus the standalone `src/run_clustering.py` script.

## Open Directions

1. Scale the analysis to all 456 eligible species to test how broadly the observed functional pattern holds.
2. Overlay core-genome phylogenetic trees on ecotype assignments to distinguish ecological adaptation from demographic structure.
3. Analyze the category S genes using protein-structure prediction and domain annotation to identify hidden defense, transport, or regulatory functions.
4. Integrate habitat metadata to test whether ecotype-associated categories track soil, host-associated, aquatic, or other environments.
5. Re-run clustering with HDBSCAN and compare assignments and functional enrichment with the KMeans results.

## Related Concepts
- [[concepts/organism-specificity]]
- [[concepts/genome-ecology-validation]]
- [[concepts/evidence-triangulation]]
- [[concepts/method-concordance]]

## Entities
- [[entities/gtdb]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/diamond]]
- [[entities/interproscan]]
