---
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/soil_metal_functional_genomics__REPORT.md", "summaries/prophage_ecology__REPORT.md", "summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/pitfalls.md", "summaries/phb_granule_ecology__REPORT.md", "summaries/paperblast_explorer__REPORT.md", "summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/lab_field_ecology__REPORT.md", "summaries/ibd_phage_targeting__REPORT.md", "summaries/harvard_forest_warming__REPORT.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/enigma_sso_asv_ecology__REPORT.md", "summaries/ecotype_functional_differentiation__REPORT.md", "summaries/cofitness_coinheritance__REPORT.md", "summaries/clay_confined_subsurface__REPORT.md", "summaries/cf_formulation_design__REPORT.md", "summaries/berdl_data_atlas__REPORT.md", "summaries/bacillota_b_subsurface_accessory__REPORT.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/bacdive_metal_validation__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
type: "Method"
description: "Pooled transposon method for measuring condition-specific bacterial gene fitness"
---

# Random-Barcode Transposon Sequencing

## Overview

Random-Barcode Transposon Sequencing (RB-TnSeq; also called random-barcode transposon sequencing) is a pooled transposon-mutagenesis method for measuring the fitness consequences of transposon-disrupted alleles across bacterial strains and experimental conditions. [src: acinetobacter_adp1_explorer, adp1_deletion_phenotypes, adp1_triple_essentiality, amr_fitness_cost]

RB-TnSeq primarily captures relative fitness costs and condition-dependent growth impairment in pooled libraries. Its outputs should not be treated as interchangeable with complete-gene-deletion phenotypes: knockout experiments measure lethality or growth defects in deletion strains, whereas RB-TnSeq measures competitive or relative fitness effects of insertion mutants. [src: adp1_triple_essentiality, amr_fitness_cost]

The [[entities/fitness-browser|Fitness Browser]] provides a major source of RB-TnSeq-derived fitness matrices in this corpus. These matrices support gene-importance comparisons, antibiotic validation, cofitness analysis, cross-organism functional inference, and integration with metabolic-model gapfilling. [src: amr_cofitness_networks, amr_fitness_cost, annotation_gap_discovery]

RB-TnSeq-derived fitness data also underlie the Metal Fitness Atlas, whose cross-species measurements were projected onto pangenome species using KEGG functional annotations. [src: bacdive_metal_validation] This enabled an ecological validation in which BacDive strains linked to pangenome species were tested for associations between predicted metal tolerance and isolation environment. [src: bacdive_metal_validation] The environmental-resistome study provides a complementary pangenome-scale view of AMR gene content across environments, but it does not use RB-TnSeq measurements as an analysis input. [src: amr_environmental_resistome]

## Evidence in the ADP1 explorer

The ADP1 database contains TnSeq essentiality calls for genes grown on minimal media and LB media, covering 58% of the 5,852 genes in the database. [src: acinetobacter_adp1_explorer] Essentiality is condition-dependent: 499 genes are classified as essential on minimal media, compared with 346 genes on LB. [src: acinetobacter_adp1_explorer]

The report compares these experimental calls with [[entities/flux-balance-analysis|flux-balance analysis]] predictions for 866 genes; the two approaches are concordant for 639 genes (73.8%) and discordant for 227 genes. [src: acinetobacter_adp1_explorer]

The ADP1 deletion-phenotype analysis classified 2,593 genes as TnSeq-dispensable. Of these, 2,321 had corresponding deletion-collection growth data, while 272 (10.5%) lacked growth data. [src: adp1_deletion_phenotypes] The missing dispensable genes had a lower mean length (813 bp versus 981 bp), lower RAST annotation coverage (91% versus 100%), lower KO annotation coverage (49% versus 59%), and lower pangenome-core representation (76.5% versus 93.3%) than dispensable genes with growth data; the core-status difference was significant (*p* = 1.4×10⁻²⁰). [src: adp1_deletion_phenotypes]

The triple-essentiality analysis evaluated 478 genes with TnSeq, FBA, and mutant-growth data; all 478 were TnSeq-dispensable because viable deletion mutants are required for growth-rate measurements. [src: adp1_triple_essentiality] Within this restricted set, FBA class was not associated with growth-defect status (chi-squared = 0.93, *p* = 0.63), and growth-defect rates were 73.1% for FBA-essential genes, 73.5% for FBA-variable genes, and 69.4% for FBA-blocked genes. [src: adp1_triple_essentiality]

## AMR fitness-cost application

The AMR fitness-cost study used RB-TnSeq-derived fitness matrices to compare 801 AMR genes with non-AMR knockout backgrounds under non-antibiotic conditions and to evaluate fitness changes under antibiotic exposure. [src: amr_fitness_cost] AMR genes were identified across 43 organisms, and 25 organisms had sufficient AMR-gene data for per-organism tests. [src: amr_fitness_cost]

AMR-gene knockouts showed systematically higher relative fitness than non-AMR knockouts in all 25 organisms. A DerSimonian–Laird random-effects meta-analysis estimated a pooled shift of **+0.086 [95% CI: +0.074, +0.098]**, with z = 14.3 and p approximately 0; the median per-organism Cohen’s d was 0.18. [src: amr_fitness_cost] This indicates a small relative burden associated with retaining AMR genes, rather than a claim that AMR-gene knockouts generally grow faster than wild type. [src: amr_fitness_cost]

The analysis found no significant baseline fitness-cost difference among efflux, enzymatic-inactivation, metal-resistance, and unknown mechanisms (Kruskal–Wallis H = 0.65, *p* = 0.89). [src: amr_fitness_cost] Core and accessory AMR genes also had virtually identical fitness distributions, with mean knockout fitness −0.024 in both groups, Cohen’s *d* = 0.002, and Mann–Whitney *p* = 0.33. [src: amr_fitness_cost]

Under antibiotic exposure, 57.0% of AMR genes showed a fitness flip toward greater importance across 797 gene–antibiotic observations; the mean flip was +0.045 and the Wilcoxon signed-rank test gave *p* = 0.0001. [src: amr_fitness_cost] Efflux genes showed a stronger mean flip (+0.094) than enzymatic-inactivation genes (−0.001; Mann–Whitney *p* = 0.007), supporting condition-dependent importance that is more mechanism-specific under antibiotic exposure than under baseline conditions. [src: amr_fitness_cost]

Class-matched antibiotic validation included 157 gene–antibiotic pairs and produced a mean flip of +0.113, but the Wilcoxon test was not significant (*p* = 0.14). [src: amr_fitness_cost] Chloramphenicol-resistance genes showed the strongest class-matched result, with 6/6 showing the expected flip, whereas beta-lactam genes showed a 50% flip rate across 105 pairs. [src: amr_fitness_cost]

These results extend RB-TnSeq from general gene-importance measurement to [[concepts/condition-dependent-essentiality|condition-dependent essentiality]] and AMR cost–benefit analysis. [src: amr_fitness_cost] The interpretation that a uniform residual cost reflects [[concepts/compensatory-evolution|compensatory evolution]] is a hypothesis rather than a directly established mechanism because the study used lab-adapted strains and did not directly measure the underlying evolutionary changes. [src: amr_fitness_cost]

## RB-TnSeq and genome–ecology validation

The BacDive isolation-environment study used RB-TnSeq-derived Metal Fitness Atlas scores as a genome-based predictor and tested whether scores differed among bacterial isolation environments. [src: bacdive_metal_validation] Species-name matching linked 42,227 of 97,334 BacDive strains (43.4%) to scores across 6,426 GTDB species; 25,089 linked strains had isolation-source metadata. [src: bacdive_metal_validation]

Strains isolated from heavy-metal contamination sites had metal tolerance scores one standard deviation above the environmental baseline (Cohen’s *d* = +1.00, Mann–Whitney *p* = 0.006, *n* = 10). [src: bacdive_metal_validation] The association was also significant for waste/sludge (Cohen’s *d* = +0.57), all contamination (+0.43), and industrial environments (+0.20), with reported *p* < 0.0001 for each comparison. [src: bacdive_metal_validation] The ordering of effect sizes—heavy metal > waste/sludge > all contamination > industrial—supports, but does not by itself prove, a contamination-intensity relationship. [src: bacdive_metal_validation]

The signal remained significant within Pseudomonadota (contamination–environment delta = +0.040, *p* < 0.001) and Actinomycetota (delta = +0.035, *p* < 0.001), but not within Bacillota (delta = −0.012, *p* = 0.285) or Bacteroidota (delta = −0.008, *p* = 0.456). [src: bacdive_metal_validation] These results provide evidence against a purely phylum-compositional explanation in the two best-sampled phyla, while the null results may reflect either biology or limited sample sizes. [src: bacdive_metal_validation]

The heavy-metal estimate is weakly powered: with *n* = 10 matched isolates, the minimum detectable effect at 80% power was approximately *d* = 0.93, compared with the observed *d* = 1.00. [src: bacdive_metal_validation] The study therefore supports [[concepts/genome-ecology-validation|genome–ecology validation]] of RB-TnSeq-derived predictions, but a larger matched dataset is needed to estimate the effect precisely. [src: bacdive_metal_validation]

Only 24 BacDive metal-utilization records matched strains with metal scores, including 8 positive and 16 negative results. [src: bacdive_metal_validation] The comparison was not significant (Mann–Whitney *p* = 0.14, Cohen’s *d* = −0.57), so it provides no reliable phenotype-level validation or refutation of the score. [src: bacdive_metal_validation]

## RB-TnSeq in annotation-gap resolution

The annotation-gap discovery study used RB-TnSeq fitness data as one component of a five-stream pipeline integrating metabolic-model gapfilling, fitness evidence, pangenome conservation, GapMind pathway predictions, alternative Bakta annotations, and BLAST homology. [src: annotation_gap_discovery] The study selected 14 organisms from the Fitness Browser with rich carbon-source RB-TnSeq coverage and evaluated 201 gapfilled enzymatic reaction–organism pairs across 18 carbon sources. [src: annotation_gap_discovery]

Evidence triangulation assigned candidate genes to 96 of 201 pairs (47.8%), exceeding the prespecified 30% resolution threshold. [src: annotation_gap_discovery] Forty-four pairs (21.9%) were high confidence, 19 (9.5%) were medium confidence, and 33 (16.4%) were low confidence; 105 pairs (52.2%) remained unresolved. [src: annotation_gap_discovery] This provides a direct application of [[concepts/evidence-triangulation|evidence triangulation]] to the [[concepts/annotation-gap|annotation gap]] problem.

No individual evidence stream exceeded 35% resolution: BLAST alone resolved 70 pairs (34.8%), EC-based matching alone resolved 51 (25.4%), and Bakta alone resolved 22 (10.9%). [src: annotation_gap_discovery] The full pipeline resolved 96 pairs, while configurations omitting NB03, NB04, or NB06 resolved 86 (42.8%), 80 (39.8%), and 73 (36.3%) pairs, respectively. [src: annotation_gap_discovery] RB-TnSeq fitness evidence therefore contributed to a complementary annotation workflow rather than serving as a sufficient standalone predictor. [src: annotation_gap_discovery]

Resolution varied from 20% in Bacteroides thetaiotaomicron to 71.4% in Klebsiella michiganensis. [src: annotation_gap_discovery] Of 201 gapfilled reactions, 50 (24.9%) were dark reactions without ModelSEED EC numbers; only 8 of these 50 (16%) were resolved, compared with 88 of 151 (58.3%) reactions with known EC numbers. [src: annotation_gap_discovery]

## Interpretation and methodological cautions

The refined ADP1 comparison found disagreement between binary RB-TnSeq classifications and experimental knockout essentiality. At an essentiality-fraction threshold of 0.05, the comparison included 1,933 genes and produced recall of 7.9%, precision of 5.8%, F1 = 0.067, specificity of 82.8%, and Cohen’s κ = −0.081; all tested thresholds from 0.01 through 0.20 yielded negative κ values. [src: adp1_triple_essentiality]

At the same threshold, 18 genes were essential by both methods, 1,411 were dispensable by both, 211 were knockout-essential but TnSeq-dispensable, and 293 were knockout-dispensable but TnSeq-essential. [src: adp1_triple_essentiality] Possible explanations include residual function from truncated proteins, transcriptional read-through, insertion-position effects, growth-condition differences, and the distinction between relative fitness and lethality; these mechanisms were not individually established. [src: adp1_triple_essentiality]

Continuous fitness was more informative for predicting knockout essentiality than binary essentiality fraction: inverted fitness produced ROC AUC values of 0.700 in rich medium and 0.725 in minimal medium, compared with 0.344 and 0.403 for essentiality fraction. [src: adp1_triple_essentiality] Continuous RB-TnSeq fitness values should therefore be prioritized over thresholded or aggregated essentiality fractions when estimating gene importance in this corpus. [src: adp1_triple_essentiality]

TnSeq-based classifications support the [[concepts/condition-dependent-essentiality|condition-dependent essentiality]] and [[concepts/phenotypic-landscape|phenotypic landscape]] frameworks. In the ADP1 deletion collection, 625 genes (31% of 2,034 genes measured across eight carbon sources) showed condition-specific growth importance. [src: adp1_deletion_phenotypes] In the triple-essentiality analysis, 333 of 478 genes (70%) showed growth defects on some but not all eight carbon sources, while 10 genes (2%) showed defects across all eight; mean pairwise defect correlation was 0.38. [src: adp1_triple_essentiality]

## RB-TnSeq cofitness applications

RB-TnSeq-derived fitness profiles support genome-wide cofitness analysis. The AMR cofitness study analyzed matrices from the [[entities/fitness-browser|Fitness Browser]] for 28 organisms containing AMR genes, yielding 801 AMR genes with fitness data and 180,370 total cofitness partners at |r| > 0.3. [src: amr_cofitness_networks]

Of 801 AMR genes, 769 (96%) had at least one extra-operon cofitness partner at |r| > 0.3; mean support-network sizes were 233 genes at |r| > 0.3, 110 at |r| > 0.4, and 71 at |r| > 0.5. [src: amr_cofitness_networks] These profiles supported analyses of cofitness neighborhoods, independent-component-analysis modules, functional enrichment, and cross-organism network conservation. [src: amr_cofitness_networks]

The strongest cross-organism signals involved flagellar motility, flagellum assembly, bacterial-type flagella, flagellum-dependent swarming, histidine biosynthesis, and tryptophan biosynthesis. [src: amr_cofitness_networks] These are provisional as evidence of co-regulation because shared dispensability under shaken liquid-culture and supplemented-media conditions can produce similar fitness patterns without direct regulatory linkage. [src: amr_cofitness_networks] This illustrates the [[concepts/shared-dispensability|shared-dispensability]] problem in interpreting [[concepts/cofitness-networks|cofitness networks]].

Support networks were more organism-specific than mechanism-specific: mean GO-term Jaccard similarity was 0.375 for different mechanisms within the same organism and 0.207 for the same mechanism across organisms (MWU *p* = 4.3×10⁻¹³). [src: amr_cofitness_networks] Annotation quality also affected inference: InterProScan GO annotations produced 35 significant enrichment results among 3,193 tests, compared with 0 of 280 tests using old SEED annotations. [src: amr_cofitness_networks]

## Relationship to models and environmental resistomes

The 227 FBA–TnSeq disagreements in ADP1 are candidates for metabolic-model refinement or investigation of regulatory effects absent from FBA models. [src: acinetobacter_adp1_explorer] Aromatic-degradation genes were enriched among FBA-discordant genes: 9 of 11 were discordant (OR = 9.70, *q* = 0.012), with directional enrichment for FBA under-prediction (OR = 12.0, *q* = 0.004). [src: adp1_triple_essentiality]

The [[concepts/environmental-resistome|environmental resistome]] report analyzed 82,908 AMR gene clusters across 14,723 species and found a median of 5 AMR clusters in clinical species versus 2 in soil and aquatic species. [src: amr_environmental_resistome] This analysis did not use RB-TnSeq measurements; combining environmental AMR profiles with RB-TnSeq fitness costs remains a proposed analysis. [src: amr_environmental_resistome]

## Related resources

The method and its ADP1 measurements are documented in [[summaries/acinetobacter_adp1_explorer__REPORT|the Acinetobacter ADP1 Data Explorer report]], [[summaries/adp1_deletion_phenotypes__REPORT|the ADP1 deletion collection phenotype analysis]], and [[summaries/adp1_triple_essentiality__REPORT|the ADP1 triple essentiality concordance analysis]]. [src: acinetobacter_adp1_explorer, adp1_deletion_phenotypes, adp1_triple_essentiality]

The BacDive validation is documented in [[summaries/bacdive_metal_validation__REPORT|the BacDive isolation-environment and metal-tolerance validation report]]. [src: bacdive_metal_validation]

The corpus contains differing statements about ADP1 availability in the [[entities/fitness-browser|Fitness Browser]]: one report states that ADP1 is absent, while another uses Fitness Browser-derived RB-TnSeq data as a comparative source. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality]

RB-TnSeq measurements can be integrated with [[entities/flux-balance-analysis|flux-balance analysis]], [[concepts/multi-omics-integration|multi-omics integration]], experimental growth phenotypes, [[concepts/method-concordance|method concordance]], [[concepts/cofitness-networks|cofitness networks]], [[concepts/pangenome-integration|pangenome integration]], and [[concepts/metabolic-model-gapfilling|metabolic-model gapfilling]]. [src: adp1_triple_essentiality, amr_cofitness_networks, annotation_gap_discovery, bacdive_metal_validation]

## Related Documents

- [[summaries/acinetobacter_adp1_explorer__REPORT]]
- [[summaries/adp1_deletion_phenotypes__REPORT]]
- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/amr_cofitness_networks__REPORT]]
- [[summaries/amr_environmental_resistome__REPORT]]
- [[summaries/amr_fitness_cost__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/bacdive_metal_validation__REPORT]]
- [[summaries/alphafold_msa_annotation__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/bacdive_phenotype_metal_tolerance__REPORT]]

See also: [[summaries/bacillota_b_subsurface_accessory__REPORT]]

See also: [[summaries/berdl_data_atlas__REPORT]]

See also: [[summaries/cf_formulation_design__REPORT]]

See also: [[summaries/clay_confined_subsurface__REPORT]]

See also: [[summaries/cofitness_coinheritance__REPORT]]

See also: [[summaries/ecotype_functional_differentiation__REPORT]]

See also: [[summaries/enigma_sso_asv_ecology__REPORT]]

See also: [[summaries/gene_function_ecological_agora__REPORT]]

See also: [[summaries/harvard_forest_warming__REPORT]]

See also: [[summaries/ibd_phage_targeting__REPORT]]

See also: [[summaries/lab_field_ecology__REPORT]]

See also: [[summaries/metabolic_capability_dependency__REPORT]]

See also: [[summaries/microbeatlas_metal_ecology__REPORT]]

See also: [[summaries/paperblast_explorer__REPORT]]

See also: [[summaries/phb_granule_ecology__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]

See also: [[summaries/prophage_ecology__REPORT]]

See also: [[summaries/soil_metal_functional_genomics__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]