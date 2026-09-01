---
sources: ["summaries/metabolic_capability_dependency__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
type: "Organism"
description: "ADP1 is a model bacterium for integrated metabolic and genetic analysis."
---

# Acinetobacter baylyi ADP1

## Identity

**Acinetobacter baylyi ADP1** is the focal organism and strain in a database explorer integrating genomic, phenotypic, metabolic, essentiality, and proteomic data. [src: acinetobacter_adp1_explorer] The strain is also the subject of a complete single-gene deletion collection analyzed across eight carbon sources, an integrated comparison of FBA, RB-TnSeq, knockout phenotypes, mutant growth, and proteomics, and a 51-gene analysis of aromatic-catabolism support requirements. [src: adp1_deletion_phenotypes, adp1_triple_essentiality, aromatic_catabolism_network]

**Aliases:** *A. baylyi* ADP1; ADP1. [src: acinetobacter_adp1_explorer]

No stable external identifier was provided in the source reports. [src: acinetobacter_adp1_explorer, adp1_deletion_phenotypes]

## Data resource

The ADP1 database contains 15 interconnected tables, 461,522 total rows, and 135 MB of data for ADP1 and 13 related genomes. [src: acinetobacter_adp1_explorer] Its central `genome_features` table contains 5,852 genes and 51 annotation columns spanning six modalities: [[entities/random-barcode-transposon-sequencing|TnSeq essentiality]], [[entities/flux-balance-analysis|FBA]] flux, mutant growth fitness on eight carbon sources, [[entities/proteomics|proteomics]], pangenome classification, and COG/KO/Pfam/UniRef functional annotations. [src: acinetobacter_adp1_explorer]

The deletion-phenotype analysis identified 2,034 genes with complete growth-ratio measurements across all eight carbon sources, 2,350 genes with measurements on at least one condition, and 5,852 total annotated genes. [src: adp1_deletion_phenotypes] No gene has data across all six modalities simultaneously, and FBA flux is the sparsest modality at 15% gene coverage. [src: acinetobacter_adp1_explorer] The resource therefore exemplifies [[concepts/multi-omics-integration|multi-omics integration]] while illustrating the limitations imposed by incomplete modality overlap. [src: acinetobacter_adp1_explorer]

The refined essentiality analysis used an essentiality vector covering 5,852 genes and compared FBA, knockout data, RB-TnSeq metrics, and proteomics across different subsets of genes. [src: adp1_triple_essentiality] FBA classifications were available for 866 genes in each of rich and minimal media, knockout data covered 2,953 genes in LB and 3,092 genes in minimal-media comparisons, and proteomics covered 2,383 genes across seven *Acinetobacter* strains. [src: adp1_triple_essentiality]

The aromatic-catabolism analysis used ADP1 genome features, gene phenotypes, and gene–reaction mappings from `berdl_tables.db`, ortholog-transferred fitness data from the [[entities/fitness-browser|Fitness Browser]], and pangenome annotations from `kbase_ke_pangenome`. [src: aromatic_catabolism_network] Its generated datasets include 51-gene support-network and operon assignments, 1,275 pairwise co-fitness correlations, 23 unknown-gene assignments, and 13-condition cross-species fitness comparisons. [src: aromatic_catabolism_network]

## BERDL integration

ADP1 connects strongly to [[entities/berdl|BERDL]] collections through genome IDs, reactions, compounds, and pangenome clusters. [src: acinetobacter_adp1_explorer] Genome IDs and compounds matched at 100%, 4,891 pangenome clusters matched at 100% through an indirect mapping, and 1,210 of 1,330 reactions matched ModelSEED biochemistry at 91%. [src: acinetobacter_adp1_explorer]

The 13 BERDL-format genomes associated with this analysis belong to *s__Acinetobacter_baylyi*, whose BERDL pangenome contains 3,207 core and 1,684 accessory gene clusters. [src: acinetobacter_adp1_explorer] ADP1 was absent from the [[entities/fitness-browser|Fitness Browser]] in the database-explorer scan, although the triple-essentiality study used Fitness Browser RB-TnSeq data as an ADP1-related essentiality and fitness resource, and the aromatic-catabolism study used ortholog-transferred Fitness Browser data for cross-species analysis. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality, aromatic_catabolism_network]

## Pangenome identifier mapping

The database uses mmseqs2-style cluster IDs, while BERDL uses centroid gene IDs, producing 0% direct string matching between the identifier systems. [src: acinetobacter_adp1_explorer] A bridge through BERDL's `gene_genecluster_junction` table mapped all 4,891 BERDL clusters to 4,081 unique ADP1 clusters, with 100% gene-level matching across 43,754 genes. [src: acinetobacter_adp1_explorer] The resulting mapping supports [[concepts/pangenome-integration|pangenome integration]] and joining BERDL functional annotations to ADP1 genes. [src: acinetobacter_adp1_explorer]

The deletion-collection analysis found that 272 of 2,593 TnSeq-dispensable genes (10.5%) lacked growth data. [src: adp1_deletion_phenotypes] These missing dispensable genes were less conserved than the 2,321 present dispensable genes: 76.5% were pangenome-core compared with 93.3% of present genes, with *p* = 1.4×10⁻²⁰. [src: adp1_deletion_phenotypes] This association links experimental deletion-collection coverage with pangenome status, although the report does not establish a causal mechanism. [src: adp1_deletion_phenotypes]

## Essentiality and metabolic phenotypes

TnSeq essentiality and FBA predictions agree for 639 of 866 jointly measured genes, corresponding to 73.8% concordance. [src: acinetobacter_adp1_explorer] The remaining 227 discordant genes are candidates for metabolic-model refinement or investigation of regulatory effects not represented by FBA. [src: acinetobacter_adp1_explorer]

A separate comparison found that FBA had moderate agreement with experimental knockout essentiality rather than uniformly reproducing genetic phenotypes. [src: adp1_triple_essentiality] In rich medium, FBA versus knockout data gave recall = 60.8%, precision = 64.0%, F1 = 0.624, and Cohen's κ = 0.486 across 724 genes. [src: adp1_triple_essentiality] In minimal medium, the corresponding values were recall = 65.6%, precision = 69.2%, F1 = 0.673, and κ = 0.493 across 833 genes. [src: adp1_triple_essentiality] These results support FBA as a first-pass metabolic screen, while indicating that experimental validation remains necessary. [src: adp1_triple_essentiality]

Essentiality is condition-dependent: 499 genes were essential on minimal media compared with 346 genes on LB. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality] In the deletion collection, the complete eight-condition growth matrix spans mean growth ratios from 0.41 on urea to 1.36 on quinate. [src: adp1_deletion_phenotypes] Urea, acetate, and butanediol form a demanding tier, asparagine and lactate form a moderate tier, and glucarate, glucose, and quinate form a robust tier based on the fraction of genes with growth defects. [src: adp1_deletion_phenotypes]

Across eight carbon sources, the earlier database analysis reported a mean pairwise fitness correlation of 0.44; urea fitness was weakly correlated with other conditions at *r* = 0.12–0.28 and had *r* = 0.11 with quinate. [src: acinetobacter_adp1_explorer] The deletion-phenotype reanalysis reported a median Pearson correlation of *r* = 0.25 across all 28 condition pairs, with acetate–butanediol the strongest pair at *r* = 0.58. [src: adp1_deletion_phenotypes] PCA showed that five components capture 82% of growth-profile variance; PC1 explains 36.7% and represents general growth sensitivity, while PC2 explains 12.7% and separates urea responses from carbon metabolism. [src: adp1_deletion_phenotypes]

Among 478 genes with TnSeq, FBA, and growth data, all were TnSeq-dispensable, and FBA class was not associated with growth-defect status (chi-squared = 0.93, *p* = 0.63). [src: adp1_triple_essentiality] At the Q25 threshold, defects occurred in 57/78 FBA-essential genes (73.1%), 150/204 FBA-variable genes (73.5%), and 136/196 FBA-blocked genes (69.4%). [src: adp1_triple_essentiality] The null association persisted across Q10–Q35 thresholds, and the continuous-growth Kruskal–Wallis test was also nonsignificant (H = 1.67, *p* = 0.43). [src: adp1_triple_essentiality]

Condition-specific FBA flux showed weak and mixed correlations with growth rates across matched carbon sources: glucose ρ = -0.021, acetate ρ = -0.153, asparagine ρ = -0.257, butanediol ρ = -0.145, glucarate ρ = +0.246, and lactate ρ = -0.160. [src: adp1_triple_essentiality] The positive glucarate correlation and weak overall relationships suggest that FBA flux does not reliably capture quantitative growth effects for dispensable genes under these conditions. [src: adp1_triple_essentiality]

FBA flux classes changed between rich and minimal media for 177 of 866 genes, or 20%. [src: acinetobacter_adp1_explorer] Together with the carbon-source results, this condition dependence makes ADP1 useful for studying model-experiment concordance, metabolic rewiring, and [[concepts/condition-dependent-essentiality|condition-dependent essentiality]]. [src: acinetobacter_adp1_explorer, adp1_deletion_phenotypes, adp1_triple_essentiality]

Hierarchical clustering of the 2,034 complete growth profiles produced an optimal *K* = 3 but a low silhouette score of 0.24, and no functional enrichments survived FDR correction. [src: adp1_deletion_phenotypes] The result supports a largely continuous [[concepts/phenotypic-landscape|phenotypic landscape]] rather than discrete functional modules. [src: adp1_deletion_phenotypes] The main exception is a 24-gene quinate-specific module with mean quinate z-score = -7.28, corresponding to aromatic degradation genes. [src: adp1_deletion_phenotypes]

A total of 625 genes (31% of the complete matrix) had a condition-specificity score of at least 1.0. [src: adp1_deletion_phenotypes] The strongest signals corresponded to expected pathways, including the urease system on urea, asparagine catabolism on asparagine, fatty-acid beta-oxidation and the glyoxylate shunt on acetate, glucarate degradation on glucarate, Entner–Doudoroff and PQQ-dependent glucose oxidation on glucose, butanediol and acetoin metabolism on butanediol, lactate regulation and cytochrome oxidase on lactate, and quinate/protocatechuate degradation plus PQQ biosynthesis on quinate. [src: adp1_deletion_phenotypes]

The quinate-specific set included 51 genes with specificity > 0.5 and z-score < -1, including NADH–ubiquinone oxidoreductase subunits. [src: adp1_deletion_phenotypes] The aromatic-catabolism network analysis assigned these genes across the core aromatic pathway, [[entities/complex-i|Complex I]], iron acquisition, [[entities/pqq-biosynthesis|PQQ biosynthesis]], regulation, and unassigned categories. [src: aromatic_catabolism_network] PQQ biosynthesis genes were condition-specific for both quinate and glucose, consistent with PQQ-dependent dehydrogenases contributing to both pathways. [src: adp1_deletion_phenotypes]

The 51-gene network contained 8 aromatic-pathway genes, 21 Complex I genes, 7 iron-acquisition genes, 2 PQQ-biosynthesis genes, 6 transcriptional regulators, and 7 unassigned genes. [src: aromatic_catabolism_network] Co-fitness assigned 16 of 23 initially Other/Unknown genes to support subsystems, including ACIAD3137 and ACIAD2176, which correlated with Complex I genes at *r* > 0.98 and are candidate uncharacterized Complex I accessory factors. [src: aromatic_catabolism_network] These assignments are hypotheses based on phenotypic correlation rather than direct physical-interaction evidence. [src: aromatic_catabolism_network]

## TnSeq, knockout, and proteomics comparisons

The refined analysis found systematic disagreement between RB-TnSeq binary calls and experimental knockout essentiality across five essentiality-fraction thresholds from 0.01 to 0.20. [src: adp1_triple_essentiality] At the 0.05 threshold, RB-TnSeq versus knockout data produced 18 true positives, 293 false positives, 211 false negatives, and 1,411 true negatives across 1,933 genes; recall = 7.9%, precision = 5.8%, F1 = 0.067, specificity = 82.8%, and κ = -0.081. [src: adp1_triple_essentiality] Every tested threshold had negative Cohen's κ, indicating that threshold selection did not resolve the discordance. [src: adp1_triple_essentiality]

The 211 knockout-essential/TnSeq-dispensable genes had mean essentiality fraction = 0.0034 and mean fitness = -0.79, whereas the 293 knockout-dispensable/TnSeq-essential genes had mean essentiality fraction = 0.1023 and mean fitness = -0.34. [src: adp1_triple_essentiality] These patterns support the interpretation that transposon insertion and complete deletion measure different biological consequences, potentially because insertions can retain partial gene function and because TnSeq data aggregate fitness effects across conditions. [src: adp1_triple_essentiality]

Continuous fitness was a better predictor of knockout essentiality than essentiality fraction. [src: adp1_triple_essentiality] Inverted fitness produced ROC AUC = 0.700 in rich medium and AUC = 0.725 in minimal medium, while essentiality fraction produced AUC = 0.344 and 0.403, respectively. [src: adp1_triple_essentiality] The findings support using continuous [[entities/random-barcode-transposon-sequencing|RB-TnSeq fitness]] values rather than binary essentiality fractions when estimating gene importance. [src: adp1_triple_essentiality]

Proteomics provided an independent essentiality-associated signal. [src: adp1_triple_essentiality] Across 2,288 genes, essential genes had mean log2 expression = 28.43 ± 2.94 and dispensable genes had mean log2 expression = 25.73 ± 2.96, a difference of 2.70 log2 units or 6.5-fold higher expression in essential genes. [src: adp1_triple_essentiality] The association was highly significant (Mann–Whitney *p* = 9.91×10⁻⁵⁹), with Pearson *r* = 0.345, Spearman ρ = 0.338, and ROC AUC = 0.743. [src: adp1_triple_essentiality]

## Aromatic degradation and model limitations

Aromatic degradation genes are a major source of FBA discordance in ADP1. [src: adp1_triple_essentiality] Among 11 aromatic degradation genes, 9 were discordant, yielding OR = 9.70 and q = 0.012; directional enrichment for FBA under-prediction was OR = 12.0 and q = 0.004. [src: adp1_triple_essentiality] The discordant set included beta-ketoadipate pathway enzymes such as 4-carboxymuconolactone decarboxylase and beta-ketoadipate enol-lactone hydrolase. [src: adp1_triple_essentiality]

The affected genes were generally predicted as FBA-blocked despite deletion-associated growth defects, suggesting a mismatch between environmental assumptions in the model and experimental conditions. [src: adp1_triple_essentiality] The report proposes testing whether adding trace aromatic compounds to the minimal-media definition resolves this gap, linking ADP1 to [[concepts/metabolic-model-gapfilling|metabolic-model gapfilling]]. [src: adp1_triple_essentiality]

The aromatic-catabolism report further found that 21 of 51 quinate-specific genes were associated with Complex I, which represented the largest support subsystem. [src: aromatic_catabolism_network] FBA predicted 1.76× higher Complex I flux on aromatic substrates (0.55 versus 0.31) but predicted 0% essentiality for the Complex I genes. [src: aromatic_catabolism_network] Thirty of the 51 quinate-specific genes had no FBA reaction mappings, including genes involved in PQQ supply, iron acquisition, regulation, and putative respiratory support. [src: aromatic_catabolism_network] This result provides a specific example of the [[concepts/metabolic-model-gapfilling|metabolic-model gap]] between represented flux and unrepresented cofactor, regulatory, and respiratory constraints.

Cross-species ortholog fitness data showed significantly worse Complex I fitness on aromatic conditions than on other conditions (mean = -1.35 versus -0.77, Mann–Whitney *p* < 0.0001), but the largest relative defects occurred on acetate (-1.55) and succinate (-1.39). [src: aromatic_catabolism_network] This supports the hypothesis that the ADP1 Complex I phenotype reflects a [[concepts/nadh-flux-respiratory-constraints|high-NADH-flux respiratory constraint]] rather than an aromatic-specific requirement alone. [src: aromatic_catabolism_network]

Lipid-metabolism genes were depleted among discordant genes (OR = 0.34, q = 0.042), suggesting better FBA representation of lipid pathways in this analysis. [src: adp1_triple_essentiality]

## Annotation and conservation

COG assignments were present for 33% of essential genes and 5% of dispensable genes, while KEGG KO assignments were present for 92% and 53%, respectively. [src: acinetobacter_adp1_explorer] Approximately 8% of essential genes lacked KO assignments and were identified in the report as candidates for further investigation of potentially novel essential functions. [src: acinetobacter_adp1_explorer]

Across 14 genomes, 1,248 of 1,330 unique metabolic reactions were shared by all genomes, 62 were variable, and 20 were genome-unique. [src: acinetobacter_adp1_explorer] Average gapfilling represented 7.7% of reactions, with 243 missing functions cataloged. [src: acinetobacter_adp1_explorer] Of 121,519 growth phenotype predictions, 105,376, or 87%, required at least one gapfilled reaction. [src: acinetobacter_adp1_explorer] These results make ADP1 a useful case for [[concepts/metabolic-model-gapfilling|metabolic-model gapfilling]] research.

The 272 missing dispensable deletion-collection genes had a mean length of 813 bp, compared with 981 bp for the 2,321 present dispensable genes; RAST annotation covered 91% versus 100%, and KO annotation covered 49% versus 59%. [src: adp1_deletion_phenotypes] Completely unannotated hypothetical proteins and proteins annotated as hypothetical were enriched among the missing genes, with *q* = 2.4×10⁻²⁵ and *q* = 3.0×10⁻⁴, respectively. [src: adp1_deletion_phenotypes] The report interprets these patterns as consistent with gene fragments or pseudogenes, particularly among 313 uncertain-class genes, which had a mean length of 361 bp, 42% annotation coverage, and 31% core status. [src: adp1_deletion_phenotypes]

## Engineered strains and proteomics

The database documents seven ADP1 strains: wild-type ADP1 and six derivatives with aromatic amino acid pathway modifications, including ΔaroF, ΔaroG, and *dgoA* variants. [src: acinetobacter_adp1_explorer] Proteomics data cover 2,383 genes across all seven strains, and the report describes high cross-strain correlations consistent with targeted rather than globally disruptive engineering effects. [src: acinetobacter_adp1_explorer]

The separate proteomics analysis averaged log2 expression across seven *Acinetobacter* strains and found a strong association between expression and knockout essentiality, although the analysis covered 2,288 genes after essentiality and expression data were intersected. [src: adp1_triple_essentiality] This provides an independent expression-based view of ADP1 gene importance and supports [[concepts/multi-omics-integration|multi-omics integration]] with FBA, knockout, TnSeq, and growth measurements. [src: adp1_triple_essentiality]

## Related resources

- [[entities/berdl]] — lakehouse collections used for comparative genomics, biochemistry, and pangenome validation.
- [[entities/modelseed]] — biochemical reaction and compound reference used in the connection scan.
- [[entities/flux-balance-analysis]] — metabolic modeling approach represented in the ADP1 database.
- [[entities/random-barcode-transposon-sequencing]] — essentiality and continuous fitness modality represented for ADP1.
- [[entities/proteomics]] — cross-strain protein abundance modality represented for ADP1.
- [[entities/fitness-browser]] — resource checked for ADP1 fitness data in the explorer and source of RB-TnSeq measures used in the triple-essentiality and aromatic-catabolism analyses.
- [[entities/complex-i]] — respiratory subsystem comprising 21 of the 51 quinate-specific support-network genes.
- [[entities/ndh-2]] — proposed alternative NADH dehydrogenase that may compensate for Complex I on lower-NADH substrates.
- [[entities/iron]] — required for protocatechuate 3,4-dioxygenase-mediated aromatic ring cleavage.
- [[entities/protocatechuate-3-4-dioxygenase]] — Fe²⁺-dependent enzyme in the quinate-to-β-ketoadipate pathway.
- [[entities/pqq-biosynthesis]] — PQQ pathway associated with quinate- and glucose-specific phenotypes.
- [[entities/urease-complex]] — condition-specific urease system identified on urea.
- [[entities/quinate-aromatic-degradation]] — condition-specific aromatic degradation system identified on quinate and a major source of FBA discordance.
- [[summaries/acinetobacter_adp1_explorer__REPORT]] — source report for the database-explorer characterization.
- [[summaries/adp1_deletion_phenotypes__REPORT]] — source report for the deletion-collection phenotype analysis.
- [[summaries/adp1_triple_essentiality__REPORT]] — source report for the integrated FBA, knockout, RB-TnSeq, growth, and proteomics analysis.
- [[summaries/aromatic_catabolism_network__REPORT]] — source report for the 51-gene aromatic-catabolism support-network analysis.

See also: [[summaries/metabolic_capability_dependency__REPORT]]