---
type: "Concept"
sources: ["summaries/genotype_to_phenotype_enigma__REPORT.md", "summaries/discoveries.md", "summaries/costly_dispensable_genes__REPORT.md", "summaries/cofitness_coinheritance__REPORT.md"]
description: "Functional coupling can weakly predict which genes are inherited together."
---

# Gene Co-inheritance

## Definition

Gene co-inheritance is the tendency of genes or pangenome clusters to occur together across genomes, assessed from correlated presence and absence patterns. In bacterial pangenomes, it can reflect shared functional requirements, coordinated regulation, mobile genetic elements, lineage history, or other processes that constrain accessory-genome composition. [src: cofitness_coinheritance]

## Evidence from Co-fitness Comparisons

The [[summaries/cofitness_coinheritance__REPORT]] tested whether laboratory-measured functional coupling predicts natural gene co-inheritance by comparing Fitness Browser co-fit pairs with prevalence-matched random pairs across 9 organisms. [src: cofitness_coinheritance]

Across 2,253,491 cofit pairs and 22,534,910 random pairs, the overall mean phi coefficient was 0.092 for cofit pairs and 0.089 for random pairs, corresponding to an aggregate delta of +0.003 (Mann–Whitney two-sided p = 1.66e-29). [src: cofitness_coinheritance]

The direction was generally positive but heterogeneous: 7 of 9 organisms had positive delta phi values, 8 of 9 had organism-level p-values below 0.05, and the Wilcoxon signed-rank test across organisms was not significant (W = 9, p = 0.13). Thus, pairwise functional coupling provides a statistically detectable but small and organism-dependent signal of co-inheritance. [src: cofitness_coinheritance]

The strongest pairwise signal occurred in Ddia6719 (delta = +0.093), followed by pseudo3_N2E3 (delta = +0.026). Korea showed a negative delta (-0.042), but 95.2% of its cofit pairs had undefined phi because both genes were present in all 72 genomes; the report attributes the negative estimate to the small effective computable sample rather than to a biological anti-association. [src: cofitness_coinheritance]

## Multi-gene Modules as Co-inheritance Units

Co-inheritance was stronger for multi-gene groups identified by [[entities/independent-component-analysis]] than for individual cofit pairs. Across 195 modules in 6 organisms, within-module mean phi was 0.229 versus 0.177 for prevalence-matched null sets, giving delta = +0.053. Fifty-one modules (26%) were significant at p < 0.05, and 21 modules (11%) remained significant after Benjamini–Hochberg FDR correction. [src: cofitness_coinheritance]

Accessory modules showed the strongest signal: their mean delta phi was +0.108, with 8 of 11 modules significant at p < 0.05 and 4 of 11 significant at q < 0.05. Core modules had delta = +0.059, while mixed modules had delta = +0.031. The accessory-versus-core difference trended toward significance (Mann–Whitney p = 0.051). [src: cofitness_coinheritance]

These results suggest the hypothesis that coordinated multi-gene modules may be more informative selective or transmission units than isolated pairwise functional relationships. This remains an interpretation rather than a demonstrated mechanism because the analysis measured association in genome presence patterns, not the direct transfer or selection of modules. [src: cofitness_coinheritance]

## Factors Affecting Detection

### Prevalence ceiling

The analysis was limited by a [[concepts/prevalence-ceiling]]: most Fitness Browser genes mapped to core clusters with prevalence above 95%, leaving little presence/absence variance and driving phi toward zero for both cofit and random pairs. [src: cofitness_coinheritance]

Co-fitness strength weakly anti-correlated with co-occurrence (Spearman rho = -0.109, p < 1e-300 across 1.04 million pairs). The report interprets this pattern as a prevalence effect because the strongest cofit pairs were likely enriched for near-universal core genes, not as evidence that stronger functional coupling prevents co-inheritance. [src: cofitness_coinheritance]

### Phylogenetic confounding

Shared ancestry can produce apparent co-inheritance independently of direct functional coupling, making [[concepts/phylogenetic-confounding]] a central interpretive issue. Cofit-pair phi averaged 0.102 among near genomes and 0.067 among medium-distance genomes. Most organisms lacked enough genomes in the far-distance stratum, so the analysis could not fully separate functional coupling from phylogenetic signal. [src: cofitness_coinheritance]

### Genomic adjacency

Genomic adjacency was not a major confound in this analysis: only 0.7% of cofit pairs were within five genes of one another, and excluding adjacent pairs did not change the result pattern. [src: cofitness_coinheritance]

## Biological Interpretation

The report supports a cautious connection between [[concepts/cofitness-networks]] and [[concepts/gene-co-inheritance]]: laboratory co-fitness relationships predict a small component of natural co-occurrence, while coordinated module structure predicts a larger component. [src: cofitness_coinheritance]

The aggregate pairwise effect indicates that measured functional coupling explains only a small fraction of pangenome co-inheritance patterns. The stronger accessory-module signal suggests that gene organization, coordinated regulation, and accessory-genome dynamics may constrain inheritance in ways that pairwise co-fitness alone does not capture. [src: cofitness_coinheritance]

The interpretation is also relevant to [[concepts/pangenome-integration]], because the analysis links Fitness Browser measurements to genome-by-cluster presence matrices and phylogenetic distances. [src: cofitness_coinheritance]

## Limitations and Tensions

The evidence is not uniform across organisms. Pairwise cofit effects were positive in most organisms but varied substantially, and the across-organism signed-rank test was not significant. [src: cofitness_coinheritance]

The two Ralstonia organisms in the extraction set had zero available Fitness Browser co-fitness data and were excluded from the primary analysis, preventing assessment in organisms that might have provided stronger phylogenetic contrast. [src: cofitness_coinheritance]

The pairwise and module-level results should not be treated as interchangeable measures: pairwise co-fitness describes relationships between gene pairs, whereas ICA modules represent coordinated multi-gene groups. [src: cofitness_coinheritance]

## Open Directions

- Recalculate co-inheritance using only auxiliary clusters below 95% prevalence to test whether removing the [[concepts/prevalence-ceiling]] increases the pairwise effect. [src: cofitness_coinheritance]
- Derive co-fitness directly from raw gene-fitness data for the Ralstonia organisms and test whether missing measurements explain the limited taxonomic coverage. [src: cofitness_coinheritance]
- Improve reference-genome mapping and compare cofit associations across near, medium, and far phylogenetic strata to quantify residual [[concepts/phylogenetic-confounding]]. [src: cofitness_coinheritance]
- Construct module co-transfer networks and test whether co-fitness predicts inheritance between distinct modules rather than only within-module co-occurrence. [src: cofitness_coinheritance]
- Expand the analysis to organisms with more than 30% auxiliary genes to test whether accessory-genome diversity systematically strengthens gene co-inheritance signals. [src: cofitness_coinheritance]

See also: [[summaries/costly_dispensable_genes__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/genotype_to_phenotype_enigma__REPORT]]