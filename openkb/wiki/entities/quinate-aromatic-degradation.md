---
sources: ["summaries/discoveries.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md"]
type: "Gene_Or_Pathway"
description: "ADP1 pathways for quinate and related aromatic compound catabolism"
---

# Quinate and Aromatic Compound Degradation

## Identity

**Quinate and aromatic compound degradation** refers to the linked metabolic pathways that enable *Acinetobacter baylyi* ADP1 to use quinate and related aromatic compounds. The pathway proceeds through protocatechuate and the β-ketoadipate pathway, producing succinyl-CoA and acetyl-CoA that enter the TCA cycle. [src: adp1_deletion_phenotypes, aromatic_catabolism_network]

**Aliases:** quinate degradation; aromatic degradation pathway; protocatechuate degradation; β-ketoadipate pathway.

The pathway is associated with [[entities/acinetobacter-baylyi-adp1]], [[entities/protocatechuate-3-4-dioxygenase]], and [[entities/pqq-biosynthesis]]. [src: aromatic_catabolism_network]

## Evidence from ADP1 deletion phenotypes

Quinate was the most robust of the eight tested carbon sources, with a mean growth ratio of 1.36 and only 1.6% of genes showing severe defects at a growth-ratio threshold below 0.5. [src: adp1_deletion_phenotypes]

Despite the generally robust growth condition, quinate produced the strongest discrete phenotype module: 24 genes showed extreme quinate-specific defects, with a mean quinate z-score of -7.28 and near-zero effects in the other tested conditions. [src: adp1_deletion_phenotypes]

The principal quinate- and protocatechuate-associated genes identified by condition-specificity analysis were *pcaC*, *pcaG*, *pcaH*, *pcaB*, *quiA*, *quiB*, *pqqC*, and *pqqD*. [src: adp1_deletion_phenotypes]

The broader quinate-specific set contained 51 genes with specificity scores greater than 0.5 and z-scores below -1. [src: adp1_deletion_phenotypes]

The 51-gene set defines a broader [[concepts/metabolic-support-networks|metabolic support network]] rather than only the core pathway. Co-fitness analysis assigned 44 of the 51 genes (86%) to four functional subsystems: 8 aromatic-pathway genes, 21 [[entities/complex-i]] genes, 7 iron-acquisition genes, and 2 PQQ-biosynthesis genes; 6 additional genes were transcriptional regulators and 7 remained unassigned. [src: aromatic_catabolism_network]

## Evidence from triple essentiality concordance

A separate analysis of FBA, RB-TnSeq, and mutant growth measurements identified aromatic degradation as the principal functional category enriched among FBA-discordant genes. Nine of 11 aromatic degradation genes were discordant, corresponding to an odds ratio of 9.70 and a Benjamini-Hochberg-adjusted q-value of 0.012. [src: adp1_triple_essentiality]

Most of these genes were **FBA-under-predicted**: the model classified them as blocked, with zero predicted flux, even though their deletion was associated with growth defects. [src: adp1_triple_essentiality] Directional enrichment for aromatic degradation among FBA-under-predicted genes was OR = 12.0 with q = 0.004. [src: adp1_triple_essentiality]

The discordance is consistent with a mismatch between the FBA environmental definition and the experimental growth environment. The report proposes the hypothesis that trace aromatic compounds, potentially present in experimental media, or functions not represented by the metabolic model contribute to the observed deletion phenotypes; this remains to be tested. [src: adp1_triple_essentiality]

The beta-ketoadipate pathway was specifically represented among the affected functions, including 4-carboxymuconolactone decarboxylase and beta-ketoadipate enol-lactone hydrolase. [src: adp1_triple_essentiality] The findings therefore identify aromatic catabolism as a targeted priority for [[concepts/metabolic-model-gapfilling]], rather than evidence that the pathway is intrinsically nonessential under all conditions. [src: adp1_triple_essentiality]

## Functional interpretation

The quinate-specific genes extend beyond the core aromatic degradation pathway to include subunits of NADH–ubiquinone oxidoreductase, suggesting the hypothesis that aromatic catabolism places distinctive demands on the electron transport chain. [src: adp1_deletion_phenotypes]

The new network analysis identifies [[entities/complex-i]] as the largest support subsystem: 21 of 51 quinate-specific genes (41%) are associated with Complex I. FBA predicts 1.76× higher Complex I flux on aromatic substrates than on the comparison non-aromatic condition (0.55 versus 0.31), but predicts 0% essentiality for these genes. [src: aromatic_catabolism_network]

The FBA limitation is broader than Complex I essentiality. Thirty of the 51 quinate-specific genes have no FBA reaction mappings, including genes involved in PQQ supply, iron acquisition, regulation, and putative Complex I accessory functions. This provides a pathway-specific example of [[concepts/annotation-gap]] and [[concepts/metabolic-model-gapfilling]]. [src: aromatic_catabolism_network]

The three principal biochemical support requirements are: PQQ for the PQQ-dependent quinate dehydrogenase QuiA; Fe²⁺ for the protocatechuate 3,4-dioxygenase PcaGH; and NADH reoxidation through Complex I as β-ketoadipate-derived carbon increases TCA-cycle oxidation. [src: aromatic_catabolism_network]

PQQ biosynthesis genes were condition-specific for both quinate and glucose, consistent with PQQ-dependent dehydrogenases contributing to the first step of both pathways. [src: adp1_deletion_phenotypes] The new analysis likewise assigns 2 PQQ-biosynthesis genes to the quinate support network, so PQQ dependence is not exclusive to aromatic catabolism. [src: aromatic_catabolism_network]

The Complex I dependency also appears to track NADH flux rather than aromatic chemistry alone. In ortholog-transferred Fitness Browser data, Complex I orthologs had mean fitness of -1.35 on aromatic conditions versus -0.77 on other conditions (Mann-Whitney p < 0.0001), while the largest condition-specific defects occurred on acetate (-1.55) and succinate (-1.39). [src: aromatic_catabolism_network] This supports the [[concepts/nadh-flux-respiratory-constraints|NADH-flux respiratory-constraints]] interpretation and suggests the hypothesis that [[entities/ndh-2]] compensates for Complex I on lower-NADH substrates such as glucose and lactate. [src: aromatic_catabolism_network]

The support subsystems are metabolically coupled without being genomically co-localized. The Complex I operon occurs at 714–729 kb, the pca/qui pathway at 1,709–1,724 kb, PQQ biosynthesis at 2,461 kb, and iron-acquisition genes across four loci. [src: aromatic_catabolism_network] The Complex I operon contains 13 nuo subunits on the same strand with intergenic distances below 100 bp, and 10 of these 13 subunits independently produce quinate-specific growth defects. [src: aromatic_catabolism_network]

Co-fitness analysis assigned 16 of 23 initially Other/Unknown genes to support subsystems with medium or high confidence. Complex I genes correlated at r = 0.992, aromatic-pathway genes at r = 0.961, and ACIAD3137 and ACIAD2176 correlated with Complex I genes at r > 0.98. The two DUF proteins are therefore candidates for uncharacterized Complex I accessory factors, although the assignments are based on phenotypic correlation rather than demonstrated physical association. [src: aromatic_catabolism_network] These results connect the pathway to [[concepts/cofitness-networks]].

The quinate pathway is the sole clear exception to the otherwise continuous [[concepts/phenotypic-landscape]] observed across the eight-condition deletion dataset. [src: adp1_deletion_phenotypes]

The combined evidence supports a condition-dependent interpretation: quinate and aromatic degradation genes can produce strong, substrate-specific growth phenotypes while remaining poorly represented by binary FBA essentiality calls under mismatched media assumptions. [src: adp1_deletion_phenotypes, adp1_triple_essentiality] This distinction links the pathway to [[concepts/condition-dependent-essentiality]] and [[concepts/method-concordance]].

## Related pages

- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/complex-i]]
- [[entities/ndh-2]]
- [[entities/pqq-biosynthesis]]
- [[entities/protocatechuate-3-4-dioxygenase]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/cofitness-networks]]
- [[concepts/metabolic-model-gapfilling]]
- [[concepts/metabolic-support-networks]]
- [[concepts/method-concordance]]
- [[concepts/nadh-flux-respiratory-constraints]]
- [[concepts/phenotypic-landscape]]
- [[summaries/adp1_deletion_phenotypes__REPORT]]
- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/discoveries]]