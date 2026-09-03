---
type: "Concept"
sources: ["summaries/truly_dark_genes__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/pathway_capability_dependency__REPORT.md", "summaries/module_conservation__REPORT.md", "summaries/metal_cross_resistance__REPORT.md", "summaries/lab_field_ecology__REPORT.md", "summaries/genotype_to_phenotype_enigma__REPORT.md", "summaries/essential_metabolome__REPORT.md", "summaries/core_gene_tradeoffs__REPORT.md", "summaries/conservation_fitness_synthesis__REPORT.md", "summaries/cf_formulation_design__REPORT.md", "summaries/berdl_data_atlas__REPORT.md", "summaries/bacillota_b_subsurface_accessory__REPORT.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md"]
description: "Environmental context makes gene and pathway essentiality conditional, graded, and measurable."
---

# Condition-Dependent Essentiality

## Definition

Condition-dependent essentiality is the principle that a gene’s contribution to growth depends on environmental context, including available nutrients, carbon sources, antibiotics, respiratory demands, and experimental medium. Essentiality is therefore a graded phenotype rather than a fixed binary property: the same gene can be strongly required in one condition, moderately important in another, and largely dispensable elsewhere. [src: adp1_deletion_phenotypes, adp1_triple_essentiality, essential_metabolome]

This concept is closely related to the [[concepts/phenotypic-landscape]] and explains why [[concepts/method-concordance]] depends on whether an assay measures lethality, metabolic necessity, fitness cost, or condition-specific growth optimization. It also connects gene-level phenotypes with [[concepts/pathway-completeness]], [[concepts/metabolic-model-gapfilling]], and [[concepts/metabolic-support-networks]]. [src: adp1_deletion_phenotypes, adp1_triple_essentiality, essential_metabolome]

The pathway capability–dependency analysis extends the principle from genes to complete metabolic pathways. Across 161 organism–pathway combinations from seven model bacteria, 35.4% were Active Dependencies, 41.0% were Latent Capabilities, 14.9% were Incomplete but Important, and 8.7% were Missing. Thus, pathway completeness alone did not predict dependency under aggregate laboratory conditions. [src: pathway_capability_dependency]

The 66 Latent Capability pathways were complete by GapMind but not important under the aggregate fitness score; all 66 became fitness-important under at least one tested condition type, especially nitrogen limitation, stress, or carbon limitation. This supports the interpretation that “latent” pathways are conditionally active rather than genomic baggage, although the result is qualified by the median-based importance threshold used in the analysis. [src: pathway_capability_dependency]

The conservation–fitness synthesis extends this principle from individual conditions to the evolutionary scale. Across 194,216 protein-coding genes from 43 diverse bacteria, essential genes were 82% core, while genes neutral in every experiment were still 66% core. The modest gradient indicates that laboratory fitness importance predicts conservation, but does not determine it. [src: conservation_fitness_synthesis]

Core genes were often more conditionally active and burdensome than accessory genes: 24.4% of core genes had positive fitness when deleted, compared with 19.9% of accessory genes; genes with strong condition-specific effects were 1.78 times more likely to be core; and genes that were both important and burdensome in different conditions were 1.29 times more likely to be core. [src: conservation_fitness_synthesis]

The core-gene trade-off analysis identified 25,271 genes, or 17.8% of the analyzed set, as true trade-off genes: they were important in some conditions, with fitness below -1, but burdensome in others, with fitness above 1. Trade-off genes were 1.29 times more likely to be core, with OR = 1.29 and p = 1.2e-44. This supports the view that conservation is compatible with extensive condition-dependent costs and benefits rather than implying uniformly positive fitness effects. [src: core_gene_tradeoffs]

The burden paradox is function-specific rather than universal. Core genes had a burden excess in Protein Metabolism (+6.2 percentage points), Motility (+7.8 percentage points), and RNA Metabolism (+12.9 percentage points), whereas Cell Wall showed the reverse pattern, with non-core cell-wall genes more burdensome (-14.1 percentage points). [src: core_gene_tradeoffs]

These results suggest the hypothesis that laboratory conditions capture the cost of maintaining some genes, whereas natural environments impose selective benefits that maintain them. The selection-signature matrix contained 28,017 costly-and-conserved genes, 5,526 costly-and-dispensable genes, 86,761 neutral-and-conserved genes, and 21,886 neutral-and-dispensable genes. [src: core_gene_tradeoffs]

## Pathway capability versus dependency

The pathway capability–dependency report classified seven organisms using GapMind completeness and Fitness Browser RB-TnSeq data. The organisms were *Desulfovibrio vulgaris* Hildenborough, *Shewanella oneidensis* MR-1, *Pseudomonas putida* KT2440, *Pseudomonas stutzeri* RCH2, *Caulobacter crescentus*, *Sinorhizobium meliloti*, and *Azospirillum brasilense*. Only seven of the 48 Fitness Browser organisms had matching GapMind data, and 23 GapMind pathways had sufficient gene-level annotation, yielding 161 organism–pathway pairs. [src: pathway_capability_dependency]

The composite importance score used 40% essentiality, 30% fitness breadth, and 30% fitness magnitude. The gene-to-pathway mapping used Fitness Browser-native KEGG annotations through besthitkegg, keggmember, EC, KEGG-map, and GapMind relationships rather than the pangenome link-table approach. [src: pathway_capability_dependency]

The four categories were defined as follows: Active Dependency means that a complete pathway contained fitness-important genes; Latent Capability means that a complete pathway was not important under the aggregate conditions; Incomplete but Important means that fitness data indicated importance despite incomplete GapMind predictions; and Missing means that the pathway was neither complete nor important. [src: pathway_capability_dependency]

The condition-stratified result is important but not definitive. All 66 Latent Capability pairs crossed the importance threshold under at least one condition type, but applying a median threshold across multiple subsets can cause some reclassification by construction. Independent calibration against known essentials or direct growth experiments is needed before treating every reclassification as biological pathway activation. [src: pathway_capability_dependency]

Active Dependencies had mean core-gene completeness of 0.986, compared with 0.975 for Latent Capabilities. The small difference is consistent with the near-complete core genomes of the seven model organisms and with the enrichment of metal-fitness genes in core genomes (OR = 2.08). [src: pathway_capability_dependency, metal_fitness_atlas]

At the pan-bacterial scale, pathway variation was associated with pangenome openness. Among 2,810 species with at least 10 genomes, the raw Spearman correlation between variable-pathway count and accessory-gene fraction was rho = 0.327, p = 7.2e-71; the partial correlation controlling for genome count was rho = 0.530, p = 2.83e-203. The positive direction occurred in 13 of 18 genera, with significant results in five genera. [src: pathway_capability_dependency]

The core-versus-all analysis found the largest pathway-completeness gaps for leucine (0.146), valine (0.146), arginine (0.141), lysine (0.140), and threonine (0.140) biosynthesis. The all-gene versus core-only completeness values were 0.614 versus 0.468 for leucine and valine, 0.613 versus 0.472 for arginine, 0.804 versus 0.664 for lysine, and 0.803 versus 0.663 for threonine. [src: pathway_capability_dependency]

These results show that accessory genes can contribute materially to species-level pathway completeness. They support a hypothesis that biosynthetic functions may be distributed among strains and could participate in community-level metabolic exchange, but they do not directly demonstrate metabolite sharing or Black Queen dynamics in any particular community. [src: pathway_capability_dependency]

Among 225 species with at least 50 genomes and at least three variable pathways, pathway-profile clustering produced a median of four metabolic ecotypes per species and a maximum of eight. *Alistipes onderdonkii* and *Barnesiella intestinihominis* each had eight ecotypes. Ecotype count correlated with openness before genome-count control (rho = 0.262, p = 6.8e-05) and afterward (partial rho = 0.322, p = 8.0e-07). [src: pathway_capability_dependency]

The pathway results complement the broader [[concepts/black-queen-dynamics]] framework: pathway loss and retention should be evaluated against environmental breadth and condition-specific demand, not against a single estimate of mean fitness. The report’s evidence is strongest for an association between pathway variability and pangenome openness; the evolutionary mechanism remains a hypothesis requiring longitudinal and ecological validation. [src: pathway_capability_dependency]

## Evidence from the ADP1 deletion collection

The [[summaries/adp1_deletion_phenotypes__REPORT]] analyzed growth ratios for 2,034 *Acinetobacter baylyi* ADP1 genes measured across eight carbon sources. Growth ratios were calculated as mutant/wild-type ratios, with values below 1.0 indicating growth defects. [src: adp1_deletion_phenotypes]

The eight carbon sources formed three broad tiers of overall difficulty:

- **Demanding:** urea, acetate, and butanediol, with mean growth ratios of 0.41–0.65 and 95–100% of genes defective below 0.8.
- **Moderate:** asparagine and lactate, with mean growth ratios of 0.80–0.82 and 37–45% of genes defective below 0.8.
- **Robust:** glucarate, glucose, and quinate, with mean growth ratios of 1.25–1.36 and 0.5–2.4% of genes defective below 0.8. [src: adp1_deletion_phenotypes]

Urea was the most demanding condition: 97.9% of genes showed severe defects below 0.5. Quinate was the most robust, with only 1.6% defective at that threshold. [src: adp1_deletion_phenotypes]

Overall condition difficulty did not mean that the conditions measured the same underlying requirement. Pairwise Pearson correlations were moderate at best, with a maximum of *r* = 0.58 for acetate–butanediol and a median of *r* = 0.25 across all 28 condition pairs. PCA required five components to capture 82% of the variance; PC1 explained 36.7% and represented general growth sensitivity, while PC2 explained 12.7% and primarily separated urea responses from carbon-metabolism responses. [src: adp1_deletion_phenotypes]

These results support approximately five independent dimensions of phenotypic information. Condition-dependent essentiality therefore reflects both a general sensitivity gradient and condition-specific metabolic requirements. [src: adp1_deletion_phenotypes]

A complementary analysis used growth data on eight carbon sources for 478 genes that also had FBA and TnSeq data. Because all genes in this triple-covered set were TnSeq-dispensable, the analysis tested variation within the dispensable space rather than lethality. At a per-condition Q25 defect threshold, 333 genes (70%) showed a defect on some but not all conditions, 10 genes (2%) showed defects across all eight conditions, and 135 genes (28%) showed no defect on any condition. Mean pairwise defect correlation was 0.38. [src: adp1_triple_essentiality]

The deletion-collection and triple-essentiality percentages are not directly contradictory: the first used a fixed ratio threshold across a complete 2,034-gene matrix, whereas the second used Q25 thresholds within an overlapping 478-gene subset. Together they support substantial, definition-dependent condition specificity. [src: adp1_deletion_phenotypes, adp1_triple_essentiality]

## Condition-specific metabolic requirements

Of the 2,034 genes in the complete matrix, 625 genes (31%) had a condition-specificity score of at least 1.0, indicating that their growth importance was concentrated on one carbon source. [src: adp1_deletion_phenotypes]

The strongest signals matched expected pathways. Quinate-specific genes included *pcaC*, *pcaG*, *pcaH*, *pcaB*, *quiA*, *quiB*, *pqqC*, and *pqqD*; urea-specific genes included *ureA* through *ureG*; asparagine-specific genes included aspartate ammonia-lyase and L-asparaginase; acetate-specific genes included *fadB*, malate synthase G, and *citB*; and lactate-specific genes included *lldR*, *cyoC*, and *cyoD*. [src: adp1_deletion_phenotypes]

The quinate-specific set contained 51 genes with specificity greater than 0.5 and z-score below -1. It extended beyond aromatic degradation to include NADH–ubiquinone oxidoreductase subunits, suggesting that aromatic catabolism places distinctive demands on the electron transport chain. [src: adp1_deletion_phenotypes]

The aromatic-catabolism network analysis assigned 44 of the 51 quinate-specific genes (86%) to four functional subsystems: eight aromatic-pathway genes, 21 Complex I genes, seven iron-acquisition genes, and two [[entities/pqq-biosynthesis]] genes. Six transcriptional regulators and seven unassigned genes made up the remainder. [src: aromatic_catabolism_network]

Quinate dehydrogenase (*quiA*) requires PQQ, protocatechuate 3,4-dioxygenase (*pcaGH*) requires non-heme Fe²⁺, and conversion of β-ketoadipate to succinyl-CoA and acetyl-CoA increases TCA-cycle NADH production. These dependencies link cofactor supply and respiratory capacity to growth on quinate. [src: aromatic_catabolism_network]

FBA captured 1.76× higher Complex I flux on aromatic substrates (0.55 versus 0.31) but predicted 0% essentiality for Complex I genes. Thirty of the 51 quinate-specific genes had no FBA reaction mappings. This demonstrates that a model can register increased flux demand while missing a condition-dependent bottleneck created by a multi-subunit respiratory complex or by unmapped cofactor, transport, and regulatory functions. [src: aromatic_catabolism_network]

The support subsystems were genomically independent but metabolically coupled. The Complex I operon occurred at 714–729 kb, the pca/qui pathway at 1,709–1,724 kb, PQQ biosynthesis at 2,461 kb, and iron-acquisition genes across four loci. The Complex I operon contained 13 nuo subunits on the same strand with intergenic distances below 100 bp; 10 of 13 subunits independently produced quinate-specific growth defects. These observations support [[concepts/metabolic-support-networks]] as a framework for requirements emerging from biochemical coupling rather than genomic co-localization. [src: aromatic_catabolism_network]

Cofitness analysis assigned 16 of 23 initially Other/Unknown genes to support subsystems with medium or high confidence. ACIAD3137 and ACIAD2176 each had *r* > 0.98 correlations with Complex I genes and are candidate accessory factors, but these assignments remain hypotheses because they are based on phenotypic correlation rather than direct physical-interaction evidence. [src: aromatic_catabolism_network]

Cross-species data refined the interpretation of the quinate phenotype. In 12,241 ortholog-transferred Fitness Browser entries covering 2,005 genes and 13 conditions, Complex I orthologs had mean fitness of -1.35 on aromatic conditions versus -0.77 on other conditions (*p* < 0.0001, Mann–Whitney). The largest Complex I defects relative to background occurred on acetate (-1.55) and succinate (-1.39), suggesting that the dependency may track high NADH flux rather than aromatic chemistry alone. The presence of [[entities/ndh-2]] could explain why Complex I is dispensable on lower-NADH substrates such as glucose and lactate, but this remains to be tested directly in ADP1. [src: aromatic_catabolism_network]

The triple-essentiality analysis found weak and inconsistent agreement between FBA flux and measured growth across six matched carbon sources: Spearman ρ ranged from -0.257 for asparagine to +0.246 for glucarate. FBA class also failed to distinguish growth-defect rates among TnSeq-dispensable genes: rates were 73.1% for FBA-essential, 73.5% for FBA-variable, and 69.4% for FBA-blocked genes (chi-squared = 0.93, *p* = 0.63). [src: adp1_triple_essentiality]

Aromatic degradation was the main functional category enriched among FBA-discordant genes: nine of 11 genes were discordant (OR = 9.70, *q* = 0.012), and directional analysis gave OR = 12.0 with *q* = 0.004 for FBA under-prediction. [src: adp1_triple_essentiality]

The annotation-gap analysis found 42.5% overall baseline FBA accuracy across 574 organism–carbon-source combinations, with recall of 86.5% (244 of 282 growth-positive conditions) and precision of 42.5%. Conditional gapfilling of 38 false-negative cases added 219 reactions, including 201 enzymatic reactions; 96 of 201 enzymatic reaction–organism pairs (47.8%) received candidate genes through integrated evidence. [src: annotation_gap_discovery]

The pipeline combined EC matching, alternative Bakta annotations, pangenome fitness profiling, and BLAST homology. BLAST alone resolved 70 pairs (34.8%), while the full pipeline resolved 96, supporting [[concepts/evidence-triangulation]] for linking condition-specific fitness evidence with metabolic model gapgapfilling and [[concepts/annotation-gap]]. [src: annotation_gap_discovery]

## Pathway completeness is not gene essentiality

The essential-metabolome analysis provides a pathway-level comparator but not a direct essentiality test. GapMind classified 17 of 18 amino-acid biosynthesis pathways as complete or likely complete in all seven organisms examined, while serine biosynthesis was complete in only six of seven (85.7%). The apparent gap occurred in *Desulfovibrio vulgaris*, which had 17/18 pathways complete (94.4%); the other six organisms had 18/18 (100%). [src: essential_metabolome]

The apparent *D. vulgaris* serine auxotrophy is a hypothesis rather than an established phenotype. GapMind may have missed a divergent or non-canonical pathway, or relevant genes may be unannotated. Environmental serine availability could make loss of biosynthesis tolerable in anaerobic, organic-rich habitats, but experimental growth on serine-free minimal medium is required for confirmation. [src: essential_metabolome]

The same analysis found conserved carbon-source capacity for fumarate, succinate, acetate, propionate, L-lactate, amino acids, deoxyribose, deoxyribonate, and putrescine in all seven organisms, while ethanol and deoxyinosine were present in six of seven. These results suggest broadly shared central catabolism, but the limited sample does not support a universal claim. [src: essential_metabolome]

The capability–dependency analysis reinforces this distinction. GapMind pathway completeness was evaluated against fitness importance, and 14.9% of the pairs were Incomplete but Important. Conversely, 41.0% were complete but not important under the aggregate score. Both outcomes show why pathway presence, pathway activity, and growth necessity must be treated as separate variables. [src: pathway_capability_dependency]

## Antibiotic-dependent fitness and AMR genes

The AMR fitness-cost study identified 1,352 AMR genes across 43 organisms and evaluated non-antibiotic fitness in 25 organisms with sufficient data. Under non-antibiotic conditions, AMR-gene knockouts had systematically higher fitness than non-AMR knockouts. A DerSimonian–Laird random-effects meta-analysis estimated a pooled relative shift of +0.086 [95% CI: +0.074, +0.098], with *z* = 14.3 and *p* approximately 0; all 25 of 25 organisms showed a positive shift. [src: amr_fitness_cost]

This is a relative dispensability effect, not evidence that AMR knockouts grow faster than wild type. AMR knockout fitness averaged -0.024, while the non-AMR knockout background averaged approximately -0.11. [src: amr_fitness_cost]

Across 797 gene–antibiotic observations, 57.0% showed a fitness flip toward greater importance under antibiotics; the mean flip was +0.045 and the Wilcoxon signed-rank test gave *p* = 0.0001. This supports condition-dependent essentiality at the level of resistance function. [src: amr_fitness_cost]

The antibiotic response was mechanism-dependent even though baseline cost was not. Efflux genes showed a mean flip of +0.094 under any antibiotic, whereas enzymatic-inactivation genes showed -0.001; the difference was significant by Mann–Whitney U test (*p* = 0.007). Chloramphenicol-resistance genes showed the expected flip in 6/6 pairs, whereas beta-lactam genes showed a 50% flip rate across 105 pairs. [src: amr_fitness_cost]

Baseline AMR cost did not vary significantly by mechanism: efflux, enzymatic inactivation, metal resistance, and unknown groups gave Kruskal–Wallis H = 0.65, *p* = 0.89. Core and accessory AMR genes also had indistinguishable costs, with mean fitness -0.024 in both groups, Cohen’s *d* = 0.002, and Mann–Whitney *p* = 0.33. [src: amr_fitness_cost]

These findings separate two dimensions of environmental response: baseline burden appears small and relatively uniform, while resistance benefit depends strongly on antibiotic exposure and mechanism. This suggests the hypothesis that [[concepts/compensatory-evolution]] has reduced the observable cost of many AMR genes. [src: amr_fitness_cost]

## Cofitness and shared dispensability under laboratory conditions

The AMR cofitness study analyzed 801 AMR genes across 28 organisms. Of these genes, 769 (96%) had at least one extra-operon cofitness partner at |*r*| > 0.3, producing 180,370 total partners and a mean support-network size of 233 genes at that threshold. [src: amr_cofitness_networks]

AMR support networks were enriched for flagellum-dependent motility, flagellum assembly, bacterial-type flagella, flagellum-dependent swarming, histidine biosynthesis, and tryptophan biosynthesis. The top terms were enriched in three to five organisms, with mean odds ratios from 4.7 to 5.3. [src: amr_cofitness_networks]

These associations may represent genuine condition-specific co-regulation, but they may also reflect [[concepts/shared-dispensability]]. Fitness Browser experiments generally use shaken liquid culture, where flagella and chemotaxis may have limited utility, and often use rich or supplemented media, where amino-acid biosynthesis can be redundant. Similar fitness profiles can therefore arise without direct regulatory relationships. [src: amr_cofitness_networks]

Support-network size did not predict baseline AMR fitness cost (Spearman rho = -0.006, *p* = 0.87, N = 769). A gene may therefore have many correlated fitness partners without imposing a larger relative cost when deleted. [src: amr_fitness_cost, amr_cofitness_networks]

The aromatic-catabolism analysis provides a contrasting use of cofitness. Within-category correlations were very high for Complex I (*r* = 0.992) and aromatic-pathway genes (*r* = 0.961), enabling 16 unknown genes to be assigned to candidate subsystems. However, the analysis used only eight conditions, and correlations beyond core operons may reflect indirect metabolic coupling rather than physical association. [src: aromatic_catabolism_network]

## Conservation, gradients, and functional architecture

Hierarchical clustering of ADP1 genes by their eight-condition profiles produced an optimal *K* = 3 but a low silhouette score of 0.24. The two large groups broadly represented generally sensitive versus generally tolerant profiles, and no functional enrichment survived FDR correction. [src: adp1_deletion_phenotypes]

This weak clustering supports a continuous model in which most genes vary gradually in condition sensitivity rather than belonging to sharply separated functional classes. The principal exception was a 24-gene module with extreme quinate-specific defects and near-zero defects in the other conditions, corresponding to aromatic degradation pathways. [src: adp1_deletion_phenotypes]

The 51-gene aromatic-catabolism network qualifies this apparent module boundary: its members span distinct, genomically separated subsystems, so a condition-specific module can represent a biochemical dependency network rather than a physically linked or transcriptionally unified cluster. [src: aromatic_catabolism_network]

The conservation–fitness synthesis found 1,116 co-regulated fitness modules across 32 organisms. These modules were enriched in core genes, with 86% core versus an 81.5% baseline (OR = 1.46, *p* = 1.6e-87), and 59% of modules contained more than 90% core genes. [src: conservation_fitness_synthesis]

The conservation synthesis found no relationship between module family breadth and core fraction (rho = -0.01, *p* = 0.91). Family breadth therefore did not provide evidence that modules spanning more organisms are more conserved. [src: conservation_fitness_synthesis]

The result contrasts with reports of discrete phenotypic modules in *E. coli* chemical-genetic experiments. The difference may reflect organism, perturbation type, experimental design, or module-construction method. [src: adp1_deletion_phenotypes]

The pathway analysis supplies a different scale of organization: species with more variable pathways had more open pangenomes, and species with more pathway-profile ecotypes also had more open pangenomes after genome-count control. This supports metabolic pathway variation as a potentially informative correlate of genome fluidity, while not establishing that pathway gain and loss is the sole driver of openness. [src: pathway_capability_dependency]

## Relationship to essentiality measurement

Condition-dependent essentiality means that conclusions from one growth condition should not automatically be generalized to other environments. The ADP1 deletion analysis found that nearly one-third of genes in the complete matrix had concentrated importance in one condition, while the triple-essentiality analysis found widespread variation in defect status across eight carbon sources. [src: adp1_deletion_phenotypes, adp1_triple_essentiality]

The conservation–fitness analysis adds that condition dependence is not restricted to accessory genes or genes with low evolutionary retention. Genes with strong condition-specific phenotypes were more likely to be core, and core genes were more likely to show burden when deleted. The core-gene trade-off analysis found the same direction for true trade-off genes. [src: conservation_fitness_synthesis, core_gene_tradeoffs]

The essential-metabolome study demonstrates why pathway presence and essentiality must be separated. GapMind found nearly complete amino-acid biosynthesis in seven organisms, but the data were computational pathway predictions rather than experimental viability measurements. RB-TnSeq experiments conducted in rich media can also make biosynthetic genes appear non-essential because metabolites are supplied externally. [src: essential_metabolome]

The pathway capability–dependency analysis adds a direct comparison between computational completeness and fitness importance. Its Active Dependency and Latent Capability categories show that complete pathways can differ in measured necessity, while its Incomplete but Important category shows that fitness evidence can reveal dependence missed by pathway annotation. [src: pathway_capability_dependency]

The finding also clarifies the relationship between deletion collections and [[entities/random-barcode-transposon-sequencing]]. Both approaches can reveal condition-specific gene functions, but the ADP1 deletion study used single-gene deletions, whereas RB-TnSeq measures pooled mutant fitness. [src: adp1_deletion_phenotypes]

At an essentiality-fraction cutoff of 0.05, only 18 genes were both knockout-essential and TnSeq-essential, while 211 were knockout-essential but TnSeq-dispensable and 293 were knockout-dispensable but TnSeq-essential. [src: adp1_triple_essentiality]

Continuous TnSeq fitness was more informative than essentiality fraction for knockout essentiality, with AUC = 0.700 in rich medium and AUC = 0.725 in minimal medium; essentiality-fraction AUC values were 0.344 and 0.403. [src: adp1_triple_essentiality]

FBA had moderate agreement with knockout lethality (κ = 0.486 in rich medium and κ = 0.493 in minimal medium), but it did not predict growth defects among TnSeq-dispensable genes. Thus, FBA can provide information near the lethal/viable boundary without resolving the continuous landscape of nonlethal, condition-specific growth costs. [src: adp1_triple_essentiality]

The annotation-gap results qualify FBA-based inference. Knockout simulation was inconclusive because models could not grow on the tested minimal media without the gapfilled reactions; the reactions being validated were required to enable growth, making the analysis circular. [src: annotation_gap_discovery]

Coverage gaps complicate essentiality interpretation. Of 2,593 TnSeq-dispensable genes, 272 (10.5%) lacked deletion-collection growth data. Missing genes had a mean length of 813 bp versus 981 bp for 2,321 present dispensable genes, were less frequently RAST-annotated (91% versus 100%), less frequently KO-annotated (49% versus 59%), and less often pangenome-core genes (76.5% versus 93.3%; *p* = 1.4e-20). [src: adp1_deletion_phenotypes]

The essential-metabolome study had an analogous coverage limitation: *Escherichia coli* K-12 had zero GapMind predictions because it was excluded from the GTDB pangenome collection, and only seven organisms were mapped successfully. The pathway estimates may therefore be affected by organism-selection and database-coverage bias. [src: essential_metabolome]

## Tensions

The ADP1 deletion data support a mostly continuous phenotype landscape, whereas prior *E. coli* chemical-genetic work described discrete phenotypic modules. [src: adp1_deletion_phenotypes] This is a methodological and biological tension rather than a direct contradiction; resolving it requires matched single-gene and chemical perturbation experiments across overlapping conditions.

A second tension concerns the scope of condition dependence. The complete deletion matrix identified 625 of 2,034 genes (31%) with a condition-specificity score of at least 1.0, whereas the triple-essentiality subset found 333 of 478 genes (70%) with at least one Q25-defined defect across eight conditions. Applying both definitions to the same genes and measurements would separate threshold effects from gene-set coverage. [src: adp1_deletion_phenotypes, adp1_triple_essentiality]

A third tension concerns pathway completeness and condition-specific importance. All 66 Latent Capability pathway pairs became important under at least one condition type, but the importance threshold was median-based and therefore susceptible to reclassification by construction. Independent thresholds and validation experiments are needed to distinguish genuine conditional activation from statistical threshold behavior. [src: pathway_capability_dependency]

A fourth tension concerns whether conditionally important genes should be accessory. The conservation–fitness synthesis found that genes with strong condition-specific effects were 1.78 times more likely to be core and that core genes had a higher burden rate than accessory genes (24.4% versus 19.9%). The core-gene trade-off analysis found the same direction for true trade-off genes. [src: conservation_fitness_synthesis, core_gene_tradeoffs]

A fifth tension concerns the function-specificity of the burden paradox. Core genes were more burdensome in Protein Metabolism, Motility, and RNA Metabolism, but Cell Wall showed the reverse pattern. The data do not support a universal rule that core genes are more costly. [src: core_gene_tradeoffs]

A sixth tension concerns FBA’s predictive scope. FBA showed moderate concordance with knockout lethality but no association with growth defects among TnSeq-dispensable genes; the annotation-gap study could not independently validate inserted GPRs; and the aromatic-catabolism study found increased flux without predicted Complex I essentiality. These findings indicate that FBA can identify model-level metabolic requirements without necessarily predicting quantitative fitness or validating gene assignments. [src: adp1_triple_essentiality, annotation_gap_discovery, aromatic_catabolism_network]

A seventh tension concerns interpretation of cofitness enrichment. InterProScan GO analysis detected flagellar and amino-acid biosynthesis enrichment in AMR support networks, but the result may reflect shared dispensability under standard laboratory conditions rather than AMR-specific co-regulation. [src: amr_cofitness_networks]

An eighth tension concerns whether Complex I dependence is aromatic-specific. ADP1 deletion data associate Complex I genes with quinate-specific defects, but cross-species ortholog fitness shows the strongest relative defects on acetate and succinate. The high-NADH-flux explanation remains unresolved because a direct ADP1 [[entities/ndh-2]] test has not been reported. [src: aromatic_catabolism_network]

A ninth tension concerns whether the *D. vulgaris* serine gap is biological or methodological. GapMind identifies serine biosynthesis as incomplete in one of seven organisms, but divergent enzymes, non-canonical pathways, or missing annotations could produce the same result. Environmental serine availability makes auxotrophy plausible, but no experimental growth test is reported. [src: essential_metabolome]

A tenth tension concerns the interpretation of accessory-dependent pathway completeness. The core-versus-all gaps for amino-acid pathways demonstrate accessory contributions, but they do not show that strains exchange the corresponding metabolites or that pathway loss is selectively maintained by community cooperation. [src: pathway_capability_dependency]

## Open Directions

- Apply the deletion-study condition-specificity score and the triple-study Q25 defect definition to the same ADP1 gene-by-condition matrix. [src: adp1_deletion_phenotypes, adp1_triple_essentiality]
- Compare ADP1 condition-specificity profiles with overlapping carbon-source experiments in [[entities/fitness-browser]] using condition-matched gene-level and pathway-level concordance tests. [src: adp1_deletion_phenotypes]
- Add carbon, nitrogen, and stress conditions to the ADP1 deletion panel and test whether the number of independent PCA dimensions increases beyond five. [src: adp1_deletion_phenotypes]
- Experimentally validate the 51-gene quinate-specific set, especially NADH–ubiquinone oxidoreductase subunits, to test the respiratory-demand hypothesis. [src: adp1_deletion_phenotypes, aromatic_catabolism_network]
- Identify the alternative NADH dehydrogenase in ADP1 and compare [[entities/ndh-2]] and Complex I deletion phenotypes on quinate, glucose, acetate, and succinate. [src: aromatic_catabolism_network]
- Re-run FBA with experimentally measured media compositions and compare predicted flux with knockout growth defects for aromatic pathways. [src: adp1_triple_essentiality, aromatic_catabolism_network]
- Add PQQ biosynthesis, iron homeostasis, and respiratory-capacity constraints to the ADP1 FBA model and test whether condition-dependent essentiality predictions improve. [src: aromatic_catabolism_network]
- Generate condition-matched RB-TnSeq and knockout measurements to separate environmental effects from differences between pooled insertion fitness and complete deletion. [src: adp1_triple_essentiality]
- Test whether the 28,017 costly-yet-conserved genes are enriched for environmental, host-associated, biofilm, or stress functions using pangenome and environmental data. [src: core_gene_tradeoffs]
- Characterize the 5,526 costly-and-dispensable genes with mobile-element annotations, gene-neighborhood analysis, age estimates, and longitudinal pangenome data. [src: core_gene_tradeoffs]
- Experimentally test high-confidence annotation-gap assignments, prioritizing rxn02185 and rxn03436 across the nine organisms where each was repeatedly resolved. [src: annotation_gap_discovery]
- Extend annotation-gap analysis from 14 to all 48 Fitness Browser organisms and test whether resolution tracks phylogenetic distance, annotation quality, and fitness coverage. [src: annotation_gap_discovery]
- Apply a fitness-matched permutation of AMR support networks using random non-AMR genes with the same mean-fitness distribution. [src: amr_cofitness_networks]
- Recompute AMR cofitness separately under antibiotic-stress and standard-growth conditions to test whether AMR–motility associations depend on environment. [src: amr_cofitness_networks]
- Check lower-confidence GapMind predictions and literature evidence for *D. vulgaris* serine auxotrophy, then test growth on serine-free minimal medium. [src: essential_metabolome]
- Map the remaining essential-gene organisms to GapMind genomes and quantify whether pathway-completeness estimates change when *E. coli* and additional phylogenetic groups are included. [src: essential_metabolome]
- Use eggNOG EC annotations and [[entities/kegg]] pathways to compare pathway completeness for organisms absent from GapMind. [src: essential_metabolome]
- Test whether pathway completeness predicts condition-specific essentiality after controlling for medium composition and metabolite supplementation. [src: essential_metabolome]
- Replace the median pathway-importance threshold with an independently calibrated threshold based on known essentials, held-out conditions, or direct growth assays. [src: pathway_capability_dependency]
- Repeat the pathway-openness analysis with phylogenetic independent contrasts and sampling-aware null models to distinguish pathway turnover from shared ancestry and database sampling. [src: pathway_capability_dependency]
- Validate predicted metabolic ecotypes with strain-resolved phenotyping and test whether ecotype-specific pathway differences produce measurable metabolite-production or utilization differences. [src: pathway_capability_dependency]
- Test whether accessory-dependent leucine, valine, arginine, lysine, and threonine pathways are exchanged among co-occurring strains rather than merely varying neutrally. [src: pathway_capability_dependency]

## Related Documents

- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/amr_cofitness_networks__REPORT]]
- [[summaries/amr_fitness_cost__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]
- [[summaries/conservation_fitness_synthesis__REPORT]]
- [[summaries/core_gene_tradeoffs__REPORT]]
- [[summaries/essential_metabolome__REPORT]]
- [[summaries/pathway_capability_dependency__REPORT]]
- [[summaries/metal_fitness_atlas__REPORT]]
- [[summaries/ecotype_analysis__REPORT]]
- [[summaries/pangenome_openness__REPORT]]

See also: [[summaries/lab_field_ecology__REPORT]], [[summaries/module_conservation__REPORT]], [[summaries/genotype_to_phenotype_enigma__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]

See also: [[summaries/truly_dark_genes__REPORT]]