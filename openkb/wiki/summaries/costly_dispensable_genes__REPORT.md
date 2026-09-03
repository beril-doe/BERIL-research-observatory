---
type: "Summary"
description: "Cross-organism analysis links costly, dispensable genes to mobile genetic element burden."
doc_type: short
full_text: "sources/costly_dispensable_genes__REPORT.md"
---

# The 5,526 Costly + Dispensable Genes

## Overview

This report analyzes 142,190 bacterial genes across 43 organisms to characterize the 5,526 genes that are both **costly** in laboratory fitness experiments and **dispensable** in the pangenome. Cost is defined as `max_fit > 1` in at least one experiment, meaning that deleting the gene improves fitness under at least one tested condition. Dispensability reflects lack of conservation across the analyzed organism set.

The central conclusion is that costly+dispensable genes are predominantly [[concepts/mobile-genetic-elements|mobile genetic elements]] and other recently acquired DNA, rather than degraded versions of core metabolic genes. They are enriched for transposases, integrases, phage genes, insertion sequences, recombinases, prophage remnants, plasmid-associated functions, and defense or virulence systems.

## Key Findings

### Strong enrichment for mobile elements

Costly+dispensable genes are 7.45 times more likely to contain mobile-element keywords than costly+conserved genes (OR=7.45, p=4.6e-71). The SEED category “Phages, Prophages, Transposable elements, Plasmids” is 11.7-fold enriched (FDR=1.3e-17). “Virulence” is 26.7-fold enriched (FDR=5.6e-14), although this estimate is based on small counts: 21 versus 4 genes.

These results support the interpretation that [[concepts/horizontal-gene-transfer|horizontal gene transfer]] and selfish genetic elements are major sources of costly, non-conserved genes.

### Poor annotation and narrow evolutionary distribution

Compared with costly+conserved genes, costly+dispensable genes are more poorly characterized and have narrower taxonomic distributions:

- 50.8% have SEED annotations, compared with 74.9% of costly+conserved genes.
- 20.0% have KEGG annotations, compared with 42.7% of costly+conserved genes.
- 44.5% are orphan genes with no ortholog group, compared with 13.1% of costly+conserved genes.
- The median ortholog breadth is 15 organisms, compared with 31 for costly+conserved genes (Mann–Whitney p=4.0e-99; rank-biserial r=0.233).
- 24.2% are singletons found in only one genome, whereas no costly+conserved genes are singletons. This comparison is partly structural because core genes cannot be singletons.
- Within the dispensable category, costly genes are only slightly more likely than neutral genes to be singletons (OR=1.09, p=0.02).
- Median gene length is 615 bp, compared with 765 bp for costly+conserved genes (p=4.2e-75; rank-biserial r=0.170).

The short length, poor annotation, orphan fraction, and restricted distribution are consistent with recent gene acquisition, insertion-sequence expansion, prophage remnants, and gene fragments. These features support the report’s evolutionary interpretation but do not by themselves establish the age or exact origin of individual genes. They also connect to [[concepts/annotation-gap|annotation gaps]], [[concepts/structural-novelty|structural novelty]], and [[concepts/pangenome-integration|pangenome integration]].

### Depletion of core cellular functions

Fourteen SEED top-level categories are significantly depleted in costly+dispensable genes at FDR < 0.05. Depleted categories include Protein Metabolism, Respiration, Carbohydrates, Amino Acids, Cofactors/Vitamins, Motility, Stress Response, and RNA Metabolism.

By contrast, costly+conserved genes are enriched for core functions such as Protein Metabolism, Respiration, and Motility. The report interprets this contrast as evidence that some energetically expensive genes are maintained by natural selection despite imposing measurable laboratory costs, whereas costly+dispensable genes are less consistently retained. This distinction relates to [[concepts/core-accessory-resistance|core–accessory tradeoffs]], [[concepts/gene-essentiality|gene essentiality]], and [[concepts/condition-dependent-essentiality|condition-dependent essentiality]].

### *Pseudomonas stutzeri* RCH2 is an outlier

[[entities/pseudomonas-stutzeri-rch2|Pseudomonas stutzeri RCH2]] contributes 21.5% of its genes as costly+dispensable, substantially above the next organism, *Bacteroides thetaiotaomicron*, at 14.0%. This pattern suggests a strain-specific genomic expansion or recent invasion by mobile DNA, but the report emphasizes that the cause remains unresolved. Candidate explanations include phage invasion, insertion-sequence expansion, or genomic-island acquisition.

### Some costly+dispensable genes have condition-specific effects

Despite their burden and limited conservation, 14.1% of costly+dispensable genes have condition-specific phenotypes. This is lower than the 16.7% observed for costly+conserved genes but much higher than the 2.7% observed for neutral+dispensable genes.

The result suggests that costly+dispensable genes are not uniformly inert. A subset may provide fitness advantages in particular environments, potentially slowing their loss from genomes. Because the phenotype data are based on laboratory-testable conditions, the result should not be generalized to all natural environments.

## Interpretation

The report proposes that costly+dispensable genes represent genomic debris or transient acquisitions associated with [[concepts/horizontal-gene-transfer|horizontal gene transfer]] and [[concepts/mobile-genetic-elements|mobile genetic elements]]. Their combined profile—mobile-element enrichment, narrow ortholog distribution, high orphan and singleton fractions, short length, poor annotation, and depletion of core metabolism—is consistent with recently acquired selfish elements that impose a host burden.

The genes are therefore candidates for ongoing gene loss. However, their persistence may reflect condition-specific benefits, genome-defense roles, or ecological contexts not represented in the fitness experiments. The report frames the 14.1% condition-specific phenotype fraction as evidence that some apparently costly accessory genes may remain useful under particular conditions.

This interpretation differs from a simple Black Queen Hypothesis explanation. The Black Queen Hypothesis concerns adaptive loss of costly functions when other community members provide them as public goods. The costly+dispensable set in this analysis is dominated by selfish mobile elements rather than metabolic functions, suggesting that many genes may be burdensome acquisitions before any adaptive gene-loss process occurs. Community data could test whether a smaller subset of these genes participates in dependency formation, connecting the question to [[concepts/shared-dispensability|shared dispensability]] and [[concepts/metabolic-support-networks|metabolic support networks]].

## Comparison with Related Work

- Price et al. (2018) supplied the Fitness Browser mutant-phenotype framework used to identify burdensome genes. This report adds pangenome conservation to distinguish potentially stable costly genes from transient, non-conserved ones.
- Morris et al. (2012) established the Black Queen Hypothesis; the report treats costly+dispensable genes as possible candidates for related gene-loss dynamics, while emphasizing their predominantly mobile-element character.
- Rosconi et al. (2022) showed that gene essentiality can be strain-dependent in *Streptococcus pneumoniae*. The condition-specific effects found among costly+dispensable genes similarly indicate that non-conserved genes can still have context-dependent fitness consequences.
- Armitage et al. (2025) documented extensive pseudogenization and gene loss in symbiotic cyanobacteria. The report presents costly+dispensable genes in free-living bacteria as possible earlier-stage indicators of genome degradation, though this extrapolation remains a hypothesis.

## Limitations

- Burden is defined by `max_fit > 1` in any experiment, so a single noisy or atypical experiment can determine classification.
- SEED and KEGG annotations cover only 56–79% of genes, leaving uncertainty about the unannotated fraction.
- Binary core/accessory classification does not capture quantitative conservation or the fraction of genomes carrying a gene.
- The 90% identity DIAMOND threshold used to link Fitness Browser genes to the pangenome may miss recently acquired genes with low sequence similarity.
- The psRCH2 outlier may reflect strain-specific genomic structure rather than a general bacterial pattern.
- Ortholog groups were assigned using bidirectional best hits across 48 organisms; genes with homologs outside this set may be misclassified as orphans.
- Condition-specific phenotypes are biased toward experimentally tested conditions.

## Future Directions

1. Analyze the psRCH2 genome for phage regions, insertion-sequence expansions, plasmids, genomic islands, and other recent acquisitions.
2. Test whether costly+dispensable genes cluster near tRNA genes, genomic-island boundaries, scaffold edges, or other horizontal-transfer signatures.
3. Compare multiple strains within organisms to determine whether these genes are being lost over evolutionary time.
4. Use ENIGMA CORAL community-composition data to test whether accessory gene loss correlates with neighboring organisms that could provide corresponding functions, providing a direct community-dependency test.
5. Replace binary conservation classes with the fraction of species genomes carrying each gene cluster to distinguish nearly core genes from rare accessory genes.
6. Reanalyze burden using replicated and condition-specific fitness measurements to separate robust costs from single-experiment classifications.

## Data and Supporting Materials

The analysis uses the BERDL `kescience_fitnessbrowser` collection (`genefitness`, `gene`, and `exps`) for fitness values and experiment metadata, and the `kbase_ke_pangenome` collection (`gene_cluster`, `gene_genecluster_junction`, and `eggnog_mapper_annotations`) for pangenome structure and functional annotations.

The generated `data/gene_quadrants.tsv` file contains 142,190 genes with fitness statistics, conservation status, and quadrant assignments. Supporting notebooks define the quadrants, perform functional enrichment, and analyze evolutionary context. Figures cover annotation rates, SEED enrichment, organism distributions, ortholog breadth, gene length, and per-organism quadrant proportions.

## Related Concepts
- [[concepts/mobile-genetic-elements]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/core-accessory-resistance]]
- [[concepts/organism-specificity]]
- [[concepts/gene-co-inheritance]]
- [[concepts/genome-ecology-validation]]

## Entities
- [[entities/fitness-browser]]
