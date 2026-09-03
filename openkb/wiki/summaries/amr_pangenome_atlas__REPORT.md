---
type: "Summary"
description: "Pan-bacterial analysis maps AMR conservation, ecology, function, and fitness."
doc_type: short
full_text: "sources/amr_pangenome_atlas__REPORT.md"
---

# Pan-Bacterial AMR Gene Landscape

## Overview

This report analyzes antimicrobial-resistance (AMR) genes across 27,690 bacterial pangenome species using uniform [[entities/bakta]] and [[entities/amrfinderplus]] annotations, taxonomic data, environmental metadata, [[entities/alphaearth-environmental-embeddings]], and [[entities/fitness-browser]] measurements. It characterizes [[concepts/core-accessory-resistance]], taxonomic hotspots, functional enrichment, environmental distributions, and laboratory fitness effects.

## Key Findings

### AMR is predominantly accessory

AMR genes are substantially depleted from core genomes: 30.3% are core compared with 46.8% for the pangenome baseline (OR=0.49, chi-squared=23,117, p≈0), while the auxiliary genome is enriched 2.2-fold for AMR (33.6% versus 15.3%). In a paired analysis of 4,252 species, 63.7% had a lower AMR core fraction than their species baseline (Wilcoxon p=1.1e-130; mean difference -0.102). [src: amr_pangenome_atlas]

The report interprets this pattern as a broad [[concepts/core-accessory-resistance]] dichotomy. Intrinsic genes, including beta-lactamases such as ampC and efflux systems such as emhABC, tend to be chromosomal and highly conserved. Acquired genes, including blaTEM, tet(C), and ant(2'')-Ia, are accessory or singleton genes; the named examples are 0% core. [src: amr_pangenome_atlas]

### Clinical pathogens are AMR hotspots

Human/Clinical species carry an average of 10.6 AMR clusters per species, compared with 4.6 in Soil/Terrestrial species, 3.9 in Aquatic species, and 3.0 in Animal species. The difference is significant (Kruskal-Wallis H=440, p=7.0e-93). Clinical AMR is also less conserved than environmental AMR: 30.8% core in clinical species versus 58.1% in soil and 63.1% in plant species. The environmental comparison is restricted to 7,838 species with non-unknown classifications. [src: amr_pangenome_atlas]

AMR density is strongly phylogenetically structured. Klebsiella averages 206 AMR clusters per species, followed by Salmonella (198), Citrobacter (134), and Enterobacter (93). Gammaproteobacteria contain 45% of all AMR clusters (37,752/83,008). Pangenome openness correlates positively with AMR count in 8 of 10 tested phyla, although the overall correlation is near zero (rho=0.006), indicating that phylogeny dominates the aggregate signal. [src: amr_pangenome_atlas]

### Environmental diversity predicts AMR accumulation

Among 2,684 species with sufficient genomes and [[entities/alphaearth-environmental-embeddings]], environmental diversity is positively associated with AMR count (Spearman rho=0.466, p=1.6e-144). Environmental diversity is also associated with a lower AMR core fraction (rho=-0.173, p=1.8e-19). The report presents this as evidence supporting an [[concepts/environmental-resistome]] hypothesis, while noting that the relationship may reflect sampling and niche breadth effects. [src: amr_pangenome_atlas]

### AMR genes are enriched in defense and ion transport

Among 77K AMR clusters with [[entities/eggnog]] annotations compared with an 86M-cluster baseline, COG V (Defense mechanisms) is enriched 7.05-fold (14.9% versus 2.1%), COG P (Inorganic ion transport) 1.93-fold (10.7% versus 5.6%), and COG J (Translation) 1.50-fold. Replication, lipid metabolism, and cell motility categories are depleted. The ion-transport signal reflects the prominence of mercury and arsenic resistance genes. [src: amr_pangenome_atlas]

Heavy-metal resistance is a major component of the catalog: merA, merP, and related mercury-resistance genes contribute approximately 15,000 hits, while arsenic-resistance genes contribute another approximately 6,000. Because the [[entities/amrfinderplus]] Reference Gene Catalog includes stress-response genes, the dataset is broader than antibiotic resistance alone. [src: amr_pangenome_atlas]

### Intrinsic AMR shows little laboratory fitness cost

A [[entities/diamond]]-based [[entities/fitness-browser]] cross-reference using 100% sequence identity identified 178 AMR genes across 37 Fitness Browser organisms and produced 29,386 fitness measurements. AMR genes had slightly less negative fitness effects than the non-AMR baseline (median -0.007 versus -0.012; Mann-Whitney p=3.7e-6), and beta-lactamases were nearly neutral (median -0.001). Singleton AMR genes were more costly (median -0.019). [src: amr_pangenome_atlas]

This result is limited primarily to predominantly environmental Fitness Browser organisms and therefore does not establish that recently acquired mobile resistance is cost-free in clinical pathogens. The report's generated-data table separately lists 29,386 measurements for 162 AMR genes in 36 organisms, creating a coverage discrepancy that should be checked against the notebook outputs. [src: amr_pangenome_atlas]

## Dataset and Methods

The AMR census contains 83,008 [[entities/amrfinderplus]] hits on gene-cluster representatives, covering 82,908 distinct clusters, 1,939 AMR gene families, and 2,079 AMR products across 14,723 species. These species represent 53.2% of the 27,690 pangenome species. Detection methods were HMM (51.5%), BLASTP (22.7%), EXACTP (13.0%), PARTIALP (9.7%), and ALLELEP (3.0%). [src: amr_pangenome_atlas]

Keyword matching of AMRFinderPlus product descriptions classified the hits into eight mechanisms. Beta-lactamases had the highest core fraction among major categories (54.9%), whereas regulatory genes had the lowest (6.5%). The 22.2% Other/Unclassified category reflects limitations of keyword matching rather than a definitive biological class. [src: amr_pangenome_atlas]

The five most abundant gene-family labels are bla (6,115 hits), merA (4,506), arsD (2,611), merP (2,222), and vanR (1,929). Annotation depth is high by Bakta and [[entities/eggnog]]: 93.0% of AMR clusters have both annotation sources. No AMR clusters have Pfam hits in the reported Pfam table, suggesting non-overlapping sequence space or an annotation-coverage issue. [src: amr_pangenome_atlas]

## Interpretation and Limitations

The report's central interpretation is that bacterial AMR comprises at least two evolutionary populations: vertically inherited intrinsic defenses that are conserved and relatively fitness-neutral, and horizontally acquired resistance elements that are accessory, environmentally structured, and especially prominent in clinical settings. The evidence is strongest for the genome-conservation and environment comparisons; the niche-breadth interpretation and generalization of fitness results remain hypotheses because of sampling and database coverage constraints. [src: amr_pangenome_atlas]

Important limitations include clinical and database sampling bias, the broad inclusion of heavy-metal and stress-response genes, sparse and inconsistent isolation-source metadata, limited AlphaEarth coverage, predominantly environmental Fitness Browser organisms, singleton annotation artifacts, keyword-based mechanism classification, lack of formal multiple-testing correction, and the conservative 100% identity threshold for fitness linking. [src: amr_pangenome_atlas]

## Open Directions

- Map Bakta cross-references to the CARD Antibiotic Resistance Ontology to replace keyword mechanism classes and reduce the 22.2% unclassified fraction.
- Combine pangenome AMR calls with NMDC or MGnify metagenomes to test whether accessory isolate genes are prevalent in environmental communities.
- Use phylogenetic distances to estimate AMR gene gain and loss rates and compare acquired versus intrinsic dynamics.
- Test AMR co-localization with genomic islands, insertion sequences, and integrons.
- Expand fitness analyses to antibiotic-stress conditions and mobile resistance elements in clinical pathogens.

## Related Concepts
- [[concepts/annotation-gap]]
- [[concepts/organism-specificity]]
- [[concepts/pangenome-integration]]
- [[concepts/condition-dependent-essentiality]]

## Entities
- [[entities/gtdb]]
- [[entities/berdl]]
- [[entities/klebsiella-pneumoniae]]
- [[entities/salmonella-enterica]]
