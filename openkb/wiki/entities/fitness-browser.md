---
sources: ["summaries/prophage_ecology__REPORT.md", "summaries/phb_granule_ecology__REPORT.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/nmdc_context_audit__REPORT.md", "summaries/nmdc_community_metabolic_ecology__REPORT.md", "summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/harvard_forest_warming__REPORT.md", "summaries/euk_in_prok_correlates__REPORT.md", "summaries/env_embedding_explorer__REPORT.md", "summaries/costly_dispensable_genes__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
type: "Dataset"
description: "Dataset of bacterial mutant fitness measurements across genes and conditions"
---

# Fitness Browser

## Overview

The Fitness Browser is a dataset of organism-specific mutant growth-fitness measurements, including [[entities/random-barcode-transposon-sequencing|random barcode transposon sequencing (RB-TnSeq)]] essentiality data, used to quantify gene effects across experimental conditions. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality, amr_cofitness_networks, amr_fitness_cost, amr_pangenome_atlas, annotation_gap_discovery, costly_dispensable_genes]

Its data include continuous fitness values and essentiality fractions aggregated across conditions, allowing gene importance to be analyzed as a quantitative phenotype rather than only as a binary essential/dispensable classification. [src: adp1_triple_essentiality]

The resource supports cross-condition cofitness analysis, antibiotic-resistance fitness-cost analysis, comparisons of gene importance across organisms and environments, phenotype-guided resolution of metabolic annotation gaps, evolutionary analysis of costly accessory genes, and cross-species testing of respiratory and metabolic dependencies. [src: amr_cofitness_networks, amr_fitness_cost, amr_pangenome_atlas, annotation_gap_discovery, aromatic_catabolism_network, costly_dispensable_genes]

## Relevance to antimicrobial-resistance fitness

The AMR fitness-cost study combined Fitness Browser `genefitness`, `gene`, and `experiment` tables with AMR annotations and pangenome mappings. [src: amr_fitness_cost]

That study identified 1,352 AMR genes across 43 organisms; 28 organisms had both AMR genes and Fitness Browser fitness matrices, and 25 organisms met the threshold of at least five AMR genes for per-organism testing. [src: amr_fitness_cost]

Across those 25 organisms, AMR-gene knockouts had systematically higher fitness than non-AMR-gene knockouts under non-antibiotic conditions. All 25 organisms showed a positive AMR-versus-background shift, and a DerSimonian–Laird random-effects meta-analysis estimated a pooled effect of +0.086 [95% CI: +0.074, +0.098], with z = 14.3 and p approximately 0. [src: amr_fitness_cost]

The median per-organism Cohen’s d was 0.18, while heterogeneity was I² = 54.3% and Cochran’s Q = 52.54, p = 0.0007. [src: amr_fitness_cost] The result measures a relative difference between AMR and non-AMR knockouts, not an absolute growth benefit of AMR-gene deletion. AMR knockout fitness averaged −0.024, whereas the non-AMR knockout background averaged approximately −0.11. [src: amr_fitness_cost]

The AMR fitness-cost study classified 6,804 experiments, including 2,868 carbon/nitrogen experiments, 1,862 stress experiments, 727 standard experiments, 447 metal experiments, and 443 antibiotic experiments. [src: amr_fitness_cost]

Under antibiotic conditions, 57.0% of AMR genes showed a fitness flip toward greater importance across 797 gene–antibiotic observations; the mean flip was +0.045 and the Wilcoxon signed-rank p-value was 0.0001. [src: amr_fitness_cost] Broad-spectrum efflux genes showed a stronger mean flip (+0.094) than enzymatic-inactivation genes (−0.001), with Mann–Whitney U p = 0.007. [src: amr_fitness_cost]

Class-matched antibiotic validation covered 157 gene–antibiotic pairs and produced a mean flip of +0.113, but the Wilcoxon test was not significant (p = 0.14). [src: amr_fitness_cost] This contrast makes the Fitness Browser useful for testing [[concepts/condition-dependent-essentiality]] and [[concepts/environmental-resistome]] questions, while showing that antibiotic coverage and mechanism matching affect statistical power and interpretation. [src: amr_fitness_cost]

Baseline AMR fitness cost did not differ significantly among efflux, enzymatic-inactivation, metal-resistance, and unknown mechanisms. [src: amr_fitness_cost] The Kruskal–Wallis test gave H = 0.65, p = 0.89, and the predicted mechanism ordering was unsupported by the Jonckheere–Terpstra test (z = 0.23, p = 0.41). [src: amr_fitness_cost]

Core and accessory AMR genes also showed virtually identical fitness distributions: both groups had mean fitness of −0.024, Cohen’s d = 0.002, and Mann–Whitney p = 0.33. [src: amr_fitness_cost] Mechanism was nevertheless strongly associated with conservation status: metal-resistance genes were 44% accessory, compared with 13% of efflux genes and 16% of enzymatic-inactivation genes. [src: amr_fitness_cost] These results connect Fitness Browser phenotypes with [[concepts/core-accessory-resistance]] and [[concepts/pangenome-integration]].

Only 4.6% of AMR genes were absent from the fitness matrices and were treated as putatively essential, compared with an estimated background essential rate of approximately 14% from a prior analysis using a different organism set. [src: amr_fitness_cost] The report interprets this lower AMR essential fraction as consistent with greater AMR-gene dispensability, while noting that absent genes may introduce censoring if the most costly genes are missing from the matrices. [src: amr_fitness_cost]

### Pan-bacterial AMR cross-reference

A separate pan-bacterial analysis used a conservative DIAMOND link requiring 100% sequence identity between Fitness Browser genes and pangenome sequences. It identified 178 AMR genes across 37 Fitness Browser organisms and yielded 29,386 fitness measurements. [src: amr_pangenome_atlas]

In this cross-reference, AMR genes had slightly less negative fitness effects than the non-AMR baseline: median fitness was −0.007 for AMR genes versus −0.012 for non-AMR genes (Mann–Whitney p = 3.7e-6). Beta-lactamases were nearly neutral, with median fitness of −0.001, whereas singleton AMR genes were costliest, with median fitness of −0.019. [src: amr_pangenome_atlas]

The result suggests that AMR genes represented in these predominantly environmental Fitness Browser organisms are well-integrated intrinsic-resistance genes rather than recently acquired mobile elements. This is a qualified interpretation: the dataset does not directly measure the fitness cost of recently acquired mobile resistance in clinical pathogens. [src: amr_pangenome_atlas]

The 100% identity requirement avoids paralog confusion but may miss closely related allelic variants, including variants differing by a single synonymous substitution, and can therefore undercount fitness effects. [src: amr_pangenome_atlas] The report’s generated-data table separately describes `amr_fitness.csv` as containing 29,386 measurements for 162 AMR genes in 36 Fitness Browser organisms; this coverage difference from the headline count of 178 genes across 37 organisms should be reconciled with the notebook outputs before reuse. [src: amr_pangenome_atlas]

Together, the two AMR studies provide complementary estimates rather than a single universal fitness effect: the broader AMR fitness-cost analysis compares AMR and non-AMR knockouts across 25 organisms, while the pan-bacterial atlas uses stricter sequence matching and emphasizes intrinsic AMR represented in predominantly environmental organisms. [src: amr_fitness_cost, amr_pangenome_atlas]

## Relevance to costly and dispensable genes

The costly+dispensable gene analysis used Fitness Browser fitness statistics together with pangenome conservation, ortholog groups, and functional annotations to classify 142,190 genes across 43 bacteria. It identified 5,526 genes that were both costly, defined as `max_fit > 1` in at least one experiment, and dispensable in the analyzed pangenome. [src: costly_dispensable_genes]

These genes were 7.45 times more likely than costly+conserved genes to contain mobile-element keywords such as transposase, integrase, phage, IS element, recombinase, or prophage (OR=7.45, p=4.6e-71). The SEED category “Phages, Prophages, Transposable elements, Plasmids” was 11.7x enriched (FDR=1.3e-17), while “Virulence” was 26.7x enriched (FDR=5.6e-14), based on small counts of 21 versus 4 genes. [src: costly_dispensable_genes]

The same genes were more poorly annotated and evolutionarily restricted than costly+conserved genes: SEED annotation covered 50.8% versus 74.9%, KEGG annotation covered 20.0% versus 42.7%, and 44.5% versus 13.1% were orphan genes without an ortholog group. Median ortholog breadth was 15 versus 31 organisms (Mann–Whitney p=4.0e-99; rank-biserial r=0.233). [src: costly_dispensable_genes]

Costly+dispensable genes had a 24.2% singleton fraction, whereas no costly+conserved genes were singletons; within the dispensable category, costly genes were only slightly more likely to be singletons than neutral genes (OR=1.09, p=0.02). Their median length was 615 bp versus 765 bp for costly+conserved genes (p=4.2e-75; rank-biserial r=0.170). [src: costly_dispensable_genes]

Fourteen SEED top-level categories, including Protein Metabolism, Respiration, Carbohydrates, Amino Acids, Cofactors/Vitamins, Motility, Stress Response, and RNA Metabolism, were significantly depleted in costly+dispensable genes at FDR < 0.05. This links Fitness Browser burden measurements to [[concepts/mobile-genetic-elements]], [[concepts/horizontal-gene-transfer]], and [[concepts/two-speed-genome]], while suggesting that costly conserved genes and costly accessory genes have different evolutionary interpretations. [src: costly_dispensable_genes]

The analysis found that 14.1% of costly+dispensable genes had condition-specific phenotypes, compared with 16.7% of costly+conserved genes and 2.7% of neutral+dispensable genes. This indicates that some costly, non-conserved genes remain phenotypically active under particular laboratory conditions rather than being uniformly inert. [src: costly_dispensable_genes]

*Pseudomonas stutzeri* RCH2 was an outlier, with 21.5% of its genes classified as costly+dispensable, compared with 14.0% in the next organism, *Bacteroides thetaiotaomicron*. The report suggests a recent mobile-element invasion or genomic expansion specific to this strain, but genomic context analysis is required to distinguish these possibilities. [src: costly_dispensable_genes]

The burden classification is sensitive to the use of `max_fit > 1` in any single experiment, and the report notes that the pangenome classification is binary, Fitness Browser coverage is condition-biased, and ortholog assignment was limited to BBH relationships across 48 organisms. [src: costly_dispensable_genes]

## Relevance to metabolic annotation-gap discovery

The annotation-gap discovery study selected 14 Fitness Browser organisms with rich carbon-source RB-TnSeq coverage and combined their fitness measurements with [[entities/modelseed|ModelSEED]] gapfilling, pangenome data, [[entities/gapmind|GapMind]], [[entities/bakta|Bakta]] annotations, and BLAST homology. [src: annotation_gap_discovery]

Across 574 organism–carbon-source combinations, baseline [[entities/flux-balance-analysis|flux-balance analysis (FBA)]] achieved 42.5% overall accuracy, with recall of 86.5% (244 of 282 growth-positive conditions) and precision of 42.5% (244 of 574 growth predictions). The low precision reflected 330 false-positive growth predictions from permissive draft models. [src: annotation_gap_discovery]

Conditional gapfilling for 38 false-negative cases added 219 reactions, including 201 enzymatic, 14 transport, and 12 exchange reactions. Of the 201 gapfilled enzymatic reaction–organism pairs, 96 (47.8%) received candidate genes with confidence scoring: 44 high-confidence, 19 medium-confidence, and 33 low-confidence assignments; 105 pairs remained unresolved. [src: annotation_gap_discovery]

Fitness Browser evidence contributed through EC-based gene matching, pangenome fitness profiling, and evidence triangulation. EC matching alone resolved 51 of 201 pairs (25.4%), while the full pipeline resolved 96 pairs (47.8%); BLAST alone resolved 70 pairs (34.8%), and removing BLAST, Bakta, or EC matching left 73, 80, or 86 resolved pairs, respectively. [src: annotation_gap_discovery] These results support [[concepts/evidence-triangulation]] as a framework for integrating quantitative fitness phenotypes with sequence and pathway evidence.

Resolution was organism-specific, ranging from 20% in [[entities/bacteroides-thetaiotaomicron|Bacteroides thetaiotaomicron]] to 71.4% in [[entities/klebsiella-michiganensis|Klebsiella michiganensis]]. The lower rate for the sole Bacteroidetes organism was interpreted as consistent with phylogenetic divergence from the predominantly proteobacterial study set, but the result is not a general estimate for all Bacteroidetes. [src: annotation_gap_discovery]

Of 50 gapfilled reactions without ModelSEED EC numbers, only 8 (16%) were resolved, compared with 88 of 151 reactions with known EC numbers (58.3%). This identifies EC-less “dark reactions” as especially difficult annotation gaps and connects Fitness Browser phenotypes to [[concepts/annotation-gap]] and [[concepts/metabolic-model-gapfilling]]. [src: annotation_gap_discovery]

The Fitness Browser measurements also enabled cross-organism EC presence/absence and fitness-specificity analyses. The study constructed a 57-EC by 14-organism matrix, calculated fitness-specificity z-scores, identified 11 strong co-occurrence cases, and found four carbon-source-specific fitness defects. [src: annotation_gap_discovery]

GapMind pathway predictions partially corroborated the carbon-source conditions requiring gapfilling, but exact concordance was limited because GapMind reports pathway-level completeness and step counts rather than individual step identities in the available data. [src: annotation_gap_discovery]

The 44 high-confidence assignments are proposed as targets for experimental validation, with rxn02185 and rxn03436 prioritized because each was resolved with high confidence in 9 of 14 organisms. [src: annotation_gap_discovery]

## Relevance to ADP1

The *Acinetobacter baylyi* ADP1 genome is absent from the Fitness Browser, so the ADP1 database’s mutant growth measurements on eight carbon sources provide a fitness resource not otherwise available for ADP1 in BERDL. [src: acinetobacter_adp1_explorer]

The ADP1 triple-essentiality analysis nevertheless used Fitness Browser-derived RB-TnSeq measurements, including essentiality fractions and continuous fitness values, to compare transposon sequencing with experimental knockout data, FBA, growth assays, proteomics, and [[concepts/multi-omics-integration|multi-omics]] evidence. [src: adp1_triple_essentiality]

Binary RB-TnSeq essentiality classifications showed systematic disagreement with knockout essentiality across tested thresholds: at the 0.05 threshold, recall was 7.9%, precision was 5.8%, F1 was 0.067, and Cohen’s kappa was −0.081. [src: adp1_triple_essentiality]

Continuous fitness values were more informative than essentiality fractions for predicting knockout essentiality, with ROC AUC values of 0.700 in rich medium and 0.725 in minimal medium, compared with essentiality-fraction AUC values of 0.344 and 0.403. [src: adp1_triple_essentiality]

These results support interpreting RB-TnSeq primarily as a measure of relative [[concepts/method-concordance|fitness cost]] rather than complete-gene-deletion lethality. [src: adp1_triple_essentiality] The reported discordance is attributed partly to differences between transposon insertion and gene deletion, condition aggregation, and the distinction between fitness impairment and viability. [src: adp1_triple_essentiality]

### Aromatic catabolism support network

A separate ADP1 study used Fitness Browser ortholog-transferred fitness data to examine whether the [[entities/complex-i|Complex I]] requirement associated with quinate catabolism was specific to aromatic substrates or instead reflected high NADH production. The cross-species dataset contained 12,241 entries, 2,005 genes, and 13 conditions. [src: aromatic_catabolism_network]

Complex I orthologs had significantly worse fitness on aromatic conditions than on non-aromatic conditions, with mean fitness of −1.35 versus −0.77 and Mann–Whitney p < 0.0001. [src: aromatic_catabolism_network] Per-condition analysis, however, found the largest Complex I defects relative to background on acetate (−1.55) and succinate (−1.39), which are non-aromatic substrates that also generate high NADH flux through the TCA cycle. [src: aromatic_catabolism_network]

These data support the hypothesis that Complex I dependence tracks [[concepts/nadh-flux-respiratory-constraints|high-NADH-flux respiratory constraints]] rather than aromatic chemistry alone. The apparent quinate-specificity in ADP1 may reflect compensation by [[entities/ndh-2|NDH-2]] on simpler substrates; this remains to be tested directly in ADP1. [src: aromatic_catabolism_network]

Fitness Browser ortholog data therefore provide a way to distinguish substrate-specific requirements from conserved physiological constraints, while requiring caution because the measurements combine organisms with different respiratory-chain architectures. [src: aromatic_catabolism_network]

## Cofitness and network analysis

The AMR cofitness analysis used Fitness Browser fitness matrices from 28 organisms with AMR genes to identify correlated fitness profiles among AMR genes and other genes. [src: amr_cofitness_networks]

Among 801 AMR genes with fitness data, 769 (96%) had at least one extra-operon cofitness partner at |r| > 0.3, yielding 180,370 total partners and 179,375 extra-operon partners. [src: amr_cofitness_networks]

At the |r| > 0.3 threshold, AMR support networks had a mean size of 233 genes; the means were 110 genes at |r| > 0.4 and 71 genes at |r| > 0.5. [src: amr_cofitness_networks]

Support networks were more organism-specific than mechanism-specific: within-organism cross-mechanism GO-term similarity had mean Jaccard 0.375, compared with 0.207 for the same mechanism across organisms (MWU p = 4.3×10⁻¹³). [src: amr_cofitness_networks] This finding supports [[concepts/organism-specificity]] as an important qualification when comparing Fitness Browser profiles across species.

Fitness Browser cofitness results require cautious biological interpretation. Enrichment for flagellar motility and amino-acid biosynthesis may reflect genuine co-regulation, but it may also arise from [[concepts/shared-dispensability]] under standard shaken-liquid-culture and supplemented-media conditions. [src: amr_cofitness_networks]

Pearson correlation removes each gene’s mean fitness before correlation, but genes can still show similar condition-responsive patterns because they are jointly dispensable under particular laboratory conditions without being directly co-regulated. [src: amr_cofitness_networks]

The ADP1 aromatic-catabolism analysis illustrates a complementary use of cofitness. Among 51 quinate-specific genes, within-category correlations were high for Complex I (mean r = 0.992) and the aromatic pathway (mean r = 0.961), enabling 16 of 23 initially Other/Unknown genes to be assigned to support subsystems. [src: aromatic_catabolism_network] The assignments of ACIAD3137 and ACIAD2176 to probable Complex I accessory functions were based on r > 0.98 correlations and require experimental validation. [src: aromatic_catabolism_network]

## Annotation and integration relevance

The AMR studies combined Fitness Browser matrices with AMR gene catalogs, independent-component-analysis module assignments, pangenome cluster mappings, and functional annotations. [src: amr_cofitness_networks, amr_fitness_cost]

InterProScan GO annotations produced 35 significant enrichment results among 3,193 tests, whereas older SEED annotations produced 0 among 280 tests. [src: amr_cofitness_networks] This difference illustrates how annotation coverage and consistency affect functional interpretation of Fitness Browser cofitness data and relates to [[concepts/annotation-gap]].

The workflow used cached Fitness Browser matrices together with InterProScan GO, Pfam, and Bakta annotations for gene-cluster-level functional analysis. [src: amr_cofitness_networks] The AMR fitness-cost workflow additionally linked Fitness Browser genes to pangenome clusters to evaluate mechanism, conservation, and fitness jointly. [src: amr_fitness_cost]

The pan-bacterial AMR atlas likewise linked Fitness Browser genes to pangenome sequences using DIAMOND at 100% sequence identity, integrating [[entities/amrfinderplus|AMRFinderPlus]] calls with gene-cluster conservation and fitness measurements. [src: amr_pangenome_atlas] These workflows connect Fitness Browser phenotypes to [[concepts/pangenome-integration]] and [[entities/interproscan|InterProScan]] functional annotation.

The aromatic-catabolism study adds a model-integration example. In ADP1, 21 of 51 quinate-specific genes were associated with Complex I, but the FBA model predicted 0% essentiality for this subsystem despite predicting 1.76× higher Complex I flux on aromatic substrates (0.55 versus 0.31). [src: aromatic_catabolism_network] Thirty of the 51 genes had no FBA reaction mappings, including PQQ, iron-acquisition, regulatory, and putative Complex I accessory genes. [src: aromatic_catabolism_network] This quantifies a model gap in which cofactor supply chains, respiratory-complex capacity, and regulatory infrastructure are not represented even when their physiological consequences are measurable.

## Potential comparative use

The ADP1 reports propose using pangenome cluster mappings to compare ADP1 mutant-growth patterns with related organisms represented in the Fitness Browser, despite ADP1 itself not being present. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality]

Such comparisons could connect ADP1’s condition-specific growth phenotypes with pangenome context and help distinguish organism-specific effects from broader fitness patterns. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality]

The annotation-gap study provides a complementary comparative use: Fitness Browser carbon-source fitness profiles can be combined with metabolic-model predictions and pangenome conservation to prioritize candidate genes for unresolved reactions across organisms. [src: annotation_gap_discovery]

The aromatic-catabolism study shows that ortholog-transferred Fitness Browser data can test whether a phenotype attributed to one substrate class generalizes to a physiological load. Complex I defects were strongest on acetate and succinate as well as aromatic conditions, supporting a high-NADH-flux interpretation while leaving organism-specific respiratory compensation unresolved. [src: aromatic_catabolism_network]

The costly+dispensable analysis adds a comparative framework for testing whether laboratory-measured burden predicts evolutionary retention. Its 5,526 costly+dispensable genes were predominantly associated with mobile elements and narrow taxonomic distributions, while 14.1% still showed condition-specific phenotypes. This makes Fitness Browser data useful for connecting [[concepts/condition-dependent-essentiality]], [[concepts/mobile-genetic-elements]], and [[concepts/pangenome-integration]], but the single-experiment burden definition and binary conservation classes limit causal evolutionary conclusions. [src: costly_dispensable_genes]

The AMR studies provide additional comparative frameworks: cofitness analysis evaluates shared fitness-profile structure across organisms and mechanisms, the AMR cost analysis compares relative knockout fitness across 25 bacterial species, and the pan-bacterial atlas links 178 AMR genes across 37 Fitness Browser organisms using exact-sequence matches. [src: amr_cofitness_networks, amr_fitness_cost, amr_pangenome_atlas]

The observed organism-specificity of cofitness networks, moderate meta-analysis heterogeneity, environmental bias of the pan-bacterial cross-reference, variable annotation-gap resolution, mixed respiratory architectures, and the strong mobile-element signal among costly+dispensable genes caution against assuming that a resistance mechanism, metabolic gene function, respiratory dependency, or evolutionary burden has the same relationship in every species. [src: amr_cofitness_networks, amr_fitness_cost, amr_pangenome_atlas, annotation_gap_discovery, aromatic_catabolism_network, costly_dispensable_genes]

## Related resources

- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/amrfinderplus]]
- [[entities/bacteroides-thetaiotaomicron]]
- [[entities/berdl]]
- [[entities/complex-i]]
- [[entities/fitness-browser]]
- [[entities/flux-balance-analysis]]
- [[entities/interproscan]]
- [[entities/kbase-ke-pangenome]]
- [[entities/ndh-2]]
- [[entities/pqq]]
- [[entities/pqq-biosynthesis]]
- [[entities/random-barcode-transposon-sequencing]]
- [[concepts/annotation-gap]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/cofitness-networks]]
- [[concepts/evidence-triangulation]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/metabolic-model-gapfilling]]
- [[concepts/metabolic-support-networks]]
- [[concepts/mobile-genetic-elements]]
- [[concepts/nadh-flux-respiratory-constraints]]
- [[concepts/organism-specificity]]
- [[concepts/pangenome-integration]]
- [[concepts/shared-dispensability]]
- [[concepts/two-speed-genome]]
- [[summaries/acinetobacter_adp1_explorer__REPORT]]
- [[summaries/adp1_deletion_phenotypes__REPORT]]
- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/amr_cofitness_networks__REPORT]]
- [[summaries/amr_environmental_resistome__REPORT]]
- [[summaries/amr_fitness_cost__REPORT]]
- [[summaries/amr_pangenome_atlas__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]
- [[summaries/costly_dispensable_genes__REPORT]]

See also: [[summaries/alphafold_msa_annotation__REPORT]]

See also: [[summaries/env_embedding_explorer__REPORT]]

See also: [[summaries/euk_in_prok_correlates__REPORT]]

See also: [[summaries/harvard_forest_warming__REPORT]]

See also: [[summaries/lanthanide_methylotrophy_atlas__REPORT]]

See also: [[summaries/microbeatlas_metal_ecology__REPORT]]

See also: [[summaries/nmdc_community_metabolic_ecology__REPORT]]

See also: [[summaries/nmdc_context_audit__REPORT]]

See also: [[summaries/pgp_pangenome_ecology__REPORT]]

See also: [[summaries/phb_granule_ecology__REPORT]]

See also: [[summaries/prophage_ecology__REPORT]]