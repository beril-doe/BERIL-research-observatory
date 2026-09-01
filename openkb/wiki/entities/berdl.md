---
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/soil_metal_functional_genomics__REPORT.md", "summaries/respiratory_chain_wiring__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/prophage_ecology__REPORT.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/metal_resistance_global_biogeography__REPORT.md", "summaries/metal_cross_resistance__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/enigma_sso_asv_ecology__REPORT.md", "summaries/ecotype_env_reanalysis__REPORT.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/bacdive_metal_validation__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
type: "Dataset"
description: "Integrated BERDL data platform linking pangenomes, phenotypes, models, and ecology"
---

# BERDL

## Overview

BERDL, the KBase BER Data Lakehouse, is an integrated data environment connecting bacterial genome features with pangenome, phenotype, metabolic-model, Fitness Browser, proteomics, domain-annotation, structural, taxonomic, environmental, antimicrobial-resistance, and prophage resources. [src: acinetobacter_adp1_explorer, adp1_deletion_phenotypes, adp1_triple_essentiality, alphafold_msa_annotation, amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation, aromatic_catabolism_network, prophage_ecology]

BERDL supports cross-dataset analyses of [[entities/acinetobacter-baylyi-adp1]], including [[concepts/pangenome-integration]], [[concepts/gene-essentiality]], [[concepts/multi-omics-integration]], [[concepts/annotation-gap]], [[concepts/structural-novelty]], [[concepts/environmental-resistome]], [[concepts/core-accessory-resistance]], [[concepts/resistance-islands]], [[concepts/phylogenetic-amr-structure]], [[concepts/metabolic-support-networks]], [[concepts/prophage-genome-modularity]], and [[concepts/module-versus-lineage-ecology]]. [src: acinetobacter_adp1_explorer, adp1_deletion_phenotypes, adp1_triple_essentiality, alphafold_msa_annotation, amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation, aromatic_catabolism_network, prophage_ecology]

The lakehouse combines large comparative resources with organism-focused datasets. The pan-bacterial AMR analysis examined 83,008 AMRFinderPlus hits across 27,690 pangenome species, while the within-species analysis examined 1,305 species and 180,025 genomes. [src: amr_pangenome_atlas, amr_strain_variation] The annotation-gap study integrated Fitness Browser experiments, pangenome clusters, Bakta and GapMind annotations, and ModelSEED reaction definitions. [src: annotation_gap_discovery] The aromatic-catabolism study additionally used a user-provided SQLite database containing `genome_features`, `gene_phenotypes`, and `gene_reaction_data`, together with Fitness Browser ortholog-transferred fitness and pangenome annotations. [src: aromatic_catabolism_network]

The prophage ecology analysis used BERDL pangenome, taxonomy, genome, environmental, and gene-neighborhood resources to examine prophage-associated modules across bacterial phylogeny and environmental gradients. [src: prophage_ecology] It identified 4,005,537 prophage-associated gene clusters across 27,702 species using 93 million eggNOG annotations and 112 query conditions. [src: prophage_ecology] The analysis also connected BERDL species-level prophage summaries to AlphaEarth environmental embeddings and used genus-level mappings to apply pangenome-derived prophage burden scores to 6,365 NMDC metagenomic samples. [src: prophage_ecology]

## Role in prophage ecology analysis

BERDL provided the primary comparative substrate for a seven-module prophage analysis: packaging (A), head morphogenesis (B), tail (C), lysis (D), integration (E), lysogenic regulation (F), and anti-defense (G). [src: prophage_ecology] All 27,702 analyzed species had at least one prophage-associated gene cluster, but only 34.9% carried all seven modules. [src: prophage_ecology] Packaging and lysogenic regulation were present in 100.0% of species, lysis in 99.9%, integration in 99.1%, head morphogenesis in 56.1%, tail in 55.6%, and anti-defense in 64.3%. [src: prophage_ecology]

The analysis found that genome size was the strongest predictor of prophage module composition, followed by environment and host-family phylogeny. [src: prophage_ecology] PERMANOVA on 1,773 species produced F-statistics of 212.99 for genome-size quartile, 30.04 for environment, and 6.17 for phylogeny, with p=0.01 for each predictor. [src: prophage_ecology] Prophage cluster count correlated with genome size at rho=0.717, but environmental effects remained significant within every genome-size quartile, with all Kruskal-Wallis tests yielding p < 6.5e-78. [src: prophage_ecology] An AlphaEarth analysis likewise found a partial Spearman correlation of 0.468 between environmental niche breadth and prophage module count after controlling for genome size, with p=8.41e-110. [src: prophage_ecology]

Constrained permutation analysis across 18,031 species identified eight significant module–environment associations after FDR correction. [src: prophage_ecology] Human-associated environments were enriched for tail (log2(OR)=2.21, Z=10.86), head morphogenesis (log2(OR)=1.98, Z=10.00), and anti-defense (log2(OR)=1.70, Z=8.76). [src: prophage_ecology] Anti-defense was depleted in freshwater (log2(OR)=-0.74, Z=-4.74) and animal-associated environments (log2(OR)=-0.24, Z=-8.77). [src: prophage_ecology] These findings suggest a possible [[concepts/microbial-arms-race]] signal in human-associated niches, but annotation-based identification and environmental metadata do not establish a causal mechanism. [src: prophage_ecology]

BERDL also supported clustering of 38,085 terminase large-subunit proteins from 11,789 species with [[entities/mmseqs2]] at 70% amino acid identity. [src: prophage_ecology] The resulting 10,991 [[entities/terminase-large-subunit]] lineages included 6,921 singleton lineages (63%) and a largest lineage spanning 1,094 members across 869 species. [src: prophage_ecology] No individual lineage showed significant environment-specific enrichment after FDR correction across 500 tests, although 325 of 824 lineages with at least five species were classified as specialists and 499 as generalists. [src: prophage_ecology] This result supports the [[concepts/module-versus-lineage-ecology]] distinction: module-level environmental signals can exceed phylogenetic expectation even when whole-lineage ecology largely follows host ecology. [src: prophage_ecology]

The NMDC cross-validation used BERDL-derived genus-level prophage burden scores and [[entities/nmdc]] environmental data. [src: prophage_ecology] Across 6,365 samples, 57 module–abiotic-variable correlations were significant at FDR < 0.05. [src: prophage_ecology] The strongest associations were packaging with pH (Spearman rho=0.519), all-module burden with pH (rho=0.474), temperature (rho=0.399), depth (rho=0.361), and total nitrogen (rho=0.333). [src: prophage_ecology] Head morphogenesis, tail, and anti-defense were significant in both the pangenome enrichment and NMDC analyses. [src: prophage_ecology]

Gene-neighborhood analysis across 15 phylogenetically stratified species found strong co-occurrence for packaging, lysis, and lysogenic-regulation genes, while integration and anti-defense genes were more dispersed. [src: prophage_ecology] Packaging was significant in 11 of 15 tests with mean contig co-localization 0.986; lysis was significant in 13 of 15 with mean co-localization 0.901; and lysogenic regulation was significant in 10 of 15 with mean co-localization 1.000. [src: prophage_ecology] Integration was significant in 1 of 15 tests with mean co-localization 0.420, while anti-defense was significant in 3 of 11 with mean co-localization 0.281. [src: prophage_ecology] These results support a two-tier model of prophage organization consisting of a linked core backbone and more scattered accessory functions. [src: prophage_ecology]

The prophage study's interpretation is limited by its use of eggNOG annotations as proxies rather than dedicated prophage detection tools, the strong genome-size relationship, sparse environmental metadata, indirect genus-level NMDC inference, limited co-occurrence replication, and biased AlphaEarth coverage. [src: prophage_ecology] These limitations make the dataset valuable for comparative hypothesis generation and [[concepts/evidence-triangulation]], but not sufficient by itself to establish intact prophage prevalence or prophage induction mechanisms. [src: prophage_ecology]

## Role in the ADP1 exploration

The exploration queried BERDL collections for pangenome, biochemical, and Fitness Browser connectivity, linking the ADP1 resource to [[entities/modelseed]], [[entities/fitness-browser]], and [[concepts/pangenome-integration]]. [src: acinetobacter_adp1_explorer]

Four of five tested connection types produced strong matches: genome IDs to the pangenome matched 13 of 13 genomes (100%); reactions to biochemical records matched 1,210 of 1,330 reactions (91%); compounds to biochemical records matched 230 of 230 compounds (100%); and pangenome cluster IDs matched 4,891 of 4,891 clusters (100%) through an indirect mapping. [src: acinetobacter_adp1_explorer]

The BERDL pangenome contains 13 genomes assigned to *s__Acinetobacter_baylyi* and includes 3,207 core and 1,684 accessory gene clusters. [src: acinetobacter_adp1_explorer]

The deletion-collection phenotype analysis used BERDL pangenome cluster IDs and core/accessory status cross-referenced through the `pangenome_cluster_id` column in the ADP1 `genome_features` table. [src: adp1_deletion_phenotypes] Among 2,593 TnSeq-dispensable ADP1 genes, 272 genes (10.5%) lacked deletion-collection growth data. [src: adp1_deletion_phenotypes] Missing genes had 76.5% pangenome-core representation compared with 93.3% among 2,321 genes with measurements, a difference reported as significant at *p* = 1.4×10⁻²⁰. [src: adp1_deletion_phenotypes] This is an association between pangenome status and phenotype-data coverage, not evidence that pangenome status causes missingness. [src: adp1_deletion_phenotypes]

The triple-essentiality analysis used BERDL genome features and proteomics data to compare knockout essentiality with FBA, RB-TnSeq, mutant growth, and protein expression. [src: adp1_triple_essentiality] BERDL supplied average log2 proteomics expression across seven *Acinetobacter* strains for 2,383 genes. [src: adp1_triple_essentiality] In the matched analysis of 2,288 genes, essential genes had mean log2 expression of 28.43 ± 2.94, compared with 25.73 ± 2.96 for dispensable genes; the analysis reported a 6.5-fold expression difference, Pearson *r* = 0.345, Spearman ρ = 0.338, and ROC AUC = 0.743. [src: adp1_triple_essentiality]

These results make BERDL a source for [[concepts/multi-omics-integration]]: expression data provide an independent continuous signal related to knockout essentiality, while pangenome data provide conservation context for phenotype coverage and discordance analyses. [src: adp1_triple_essentiality, adp1_deletion_phenotypes]

## Role in aromatic-catabolism network analysis

The aromatic-catabolism analysis used a user-provided SQLite database with `genome_features`, `gene_phenotypes`, and `gene_reaction_data` tables for ADP1 growth ratios, FBA predictions across 230 conditions, and gene–reaction mappings. [src: aromatic_catabolism_network] It also used the `kescience_fitnessbrowser` collection for ortholog-transferred fitness and `kbase_ke_pangenome` annotations for conservation context. [src: aromatic_catabolism_network]

The analysis identified 51 quinate-specific ADP1 genes organized into a support network around [[entities/quinate-aromatic-degradation]]. [src: aromatic_catabolism_network] Co-fitness analysis assigned 44 of 51 genes (86%) to the aromatic pathway, Complex I, iron acquisition, PQQ biosynthesis, or regulation; the assignments included 8 aromatic-pathway genes, 21 Complex I genes, 7 iron-acquisition genes, 2 PQQ-biosynthesis genes, and 6 regulators, with 7 genes unassigned. [src: aromatic_catabolism_network]

BERDL-linked FBA and phenotype data showed 1.76× higher predicted Complex I flux on aromatic substrates than on the comparison substrates (0.55 versus 0.31), while the model predicted 0% essentiality for Complex I genes. [src: aromatic_catabolism_network] Thirty of the 51 quinate-specific genes lacked FBA reaction mappings, demonstrating a [[concepts/metabolic-model-gapfilling|metabolic-model gap]] involving cofactor supply, iron acquisition, respiratory capacity, and regulation. [src: aromatic_catabolism_network]

The cross-species Fitness Browser analysis contained 12,241 ortholog-transferred fitness entries covering 2,005 genes and 13 conditions. [src: aromatic_catabolism_network] Complex I orthologs had mean fitness of −1.35 on aromatic conditions versus −0.77 on non-aromatic conditions, with Mann–Whitney *p* < 0.0001. [src: aromatic_catabolism_network] The largest Complex I defects relative to background occurred on acetate (−1.55) and succinate (−1.39), supporting the hypothesis that the dependency tracks high NADH flux rather than aromatic chemistry specifically. [src: aromatic_catabolism_network]

The study generated a 51-gene support-network table, operon assignments, 1,275 pairwise co-fitness measurements, 23 unknown-gene assignments, and a 13-condition cross-species fitness comparison. [src: aromatic_catabolism_network] These results extend BERDL's use from pathway and reaction integration to analysis of distributed [[concepts/metabolic-support-networks]] and [[concepts/nadh-flux-respiratory-constraints]]. [src: aromatic_catabolism_network]

## Role in annotation-gap discovery

The annotation-gap discovery study selected 14 Fitness Browser organisms with rich carbon-source RB-TnSeq coverage and used BERDL to connect draft metabolic models, gene annotations, pangenomes, pathway completeness, and sequence evidence. [src: annotation_gap_discovery] The relevant collections were `kescience_fitnessbrowser` (`organism`, `experiment`, `genefitness`, and `gene`), `kbase_ke_pangenome` (`genome`, `gene_cluster`, `gene_genecluster_junction`, `eggnog_mapper_annotations`, `bakta_annotations`, and `gapmind_pathways`), and `kbase_msd_biochemistry` (`reaction` and `reagent`). [src: annotation_gap_discovery]

Baseline FBA across 574 organism–carbon-source combinations achieved 42.5% overall accuracy, with recall of 86.5% (244 of 282 growth-positive conditions) and precision of 42.5% (244 of 574 growth predictions). [src: annotation_gap_discovery] Conditional gapfilling for 38 false-negative cases added 219 reactions: 201 enzymatic, 14 transport, and 12 exchange reactions. [src: annotation_gap_discovery] Evidence integration assigned candidate genes to 96 of 201 gapfilled enzymatic reaction–organism pairs (47.8%), exceeding the prespecified 30% resolution threshold. [src: annotation_gap_discovery]

The full pipeline resolved 96 pairs (47.8%), compared with 70 (34.8%) for BLAST alone, 51 (25.4%) for EC matching alone, and 22 (10.9%) for Bakta alone. [src: annotation_gap_discovery] The analysis therefore used BERDL as a substrate for [[concepts/evidence-triangulation]] across metabolic models, annotations, homology, pangenome conservation, and phenotype. [src: annotation_gap_discovery]

The study resolved only 8 of 50 EC-less “dark reactions” (16%), leaving 105 of 201 enzymatic reaction–organism pairs unresolved. [src: annotation_gap_discovery] GapMind pathway predictions partially corroborated ModelSEED gapfilling for 104 pathway pairings, but exact concordance was limited because GapMind reports pathway-level completeness and step counts rather than individual reaction identities. [src: annotation_gap_discovery] This illustrates both the value and limitations of [[concepts/method-concordance]].

## Role in AMR fitness-cost analysis

The AMR fitness-cost analysis used BERDL's `kbase_ke_pangenome.bakta_amr` and `bakta_annotations` collections to identify resistance genes and connected them to `kescience_fitnessbrowser` gene, experiment, and `genefitness` tables. [src: amr_fitness_cost]

The assembled dataset identified 1,352 AMR genes across 43 organisms, including 178 Tier 1 genes and 1,174 Tier 2 keyword-annotated genes. [src: amr_fitness_cost] Across 25 organisms, AMR-gene knockouts had higher fitness than non-AMR knockouts under non-antibiotic conditions, with a pooled DerSimonian–Laird random-effects effect of +0.086 [95% CI: +0.074, +0.098], *z* = 14.3, and *p* approximately 0; all 25 organisms showed a positive shift. [src: amr_fitness_cost]

The result is a relative dispensability signal rather than evidence that AMR knockouts grow faster than wild type: AMR knockout fitness averaged −0.024, while the non-AMR background averaged approximately −0.11. [src: amr_fitness_cost] BERDL-linked Fitness Browser data also showed that 57.0% of 797 AMR genes exhibited a fitness flip toward greater importance under antibiotic exposure. [src: amr_fitness_cost]

Mechanism was associated with AMR conservation status (χ² = 69.3, *p* = 1.4×10⁻¹³): metal-resistance genes were 44% accessory, compared with 13% of efflux genes and 16% of enzymatic-inactivation genes. [src: amr_fitness_cost] This links BERDL's pangenome and fitness resources to [[concepts/core-accessory-resistance]] and [[concepts/compensatory-evolution]]. [src: amr_fitness_cost]

A complementary pan-bacterial analysis used a conservative 100% sequence-identity bridge to identify 178 AMR genes across 37 Fitness Browser organisms and 29,386 fitness measurements. [src: amr_pangenome_atlas] AMR genes had a slightly less negative median fitness than the non-AMR baseline (−0.007 versus −0.012; Mann–Whitney *p* = 3.7e-6). [src: amr_pangenome_atlas] The two fitness analyses differ in organism sets, AMR inclusion criteria, and data assembly, so their numerical estimates are not a single reconciled effect. [src: amr_fitness_cost, amr_pangenome_atlas]

## Role in environmental-resistome analysis

The environmental-resistome analysis used BERDL collections including `bakta_amr`, `gene_cluster`, `pangenome`, `ncbi_env`, `genome`, `gtdb_taxonomy_r214v1`, and `alphaearth_embeddings_all_years` to relate AMR gene clusters and pangenome structure to environmental metadata, taxonomy, and continuous environmental embeddings. [src: amr_environmental_resistome]

The assembled dataset contained 82,908 AMR gene clusters across 14,723 species, with 280,337 genomes carrying `ncbi_env` metadata; 93.5% of these genomes received a per-genome environment classification. [src: amr_environmental_resistome] Clinical-source species had a median of 5 AMR gene clusters, compared with 2 for soil, aquatic, and host-associated species; the environment association was significant (Kruskal–Wallis *H* = 781.9, *p* = 9.4×10⁻¹⁶⁷, η² = 0.056). [src: amr_environmental_resistome]

BERDL-derived pangenome and AMR data showed an environment-dependent core/accessory gradient: clinical species averaged 32.4% core and 67.6% accessory AMR, soil species averaged 57.1% core and 42.9% accessory AMR, and human-gut species averaged 19.7% core and 80.3% accessory AMR. [src: amr_environmental_resistome] Among 2,659 species with AMR data and AlphaEarth embeddings, 52 of 64 embedding dimensions correlated with AMR diversity at FDR < 0.05, while a Mantel test found that environmental distance predicted AMR mechanism-profile distance (r = 0.098, *p* = 0.001). [src: amr_environmental_resistome]

The pan-bacterial atlas independently assembled 83,008 AMRFinderPlus hits across 82,908 clusters and 14,723 species. [src: amr_pangenome_atlas] Human/Clinical species averaged 10.6 AMR clusters per species, compared with 4.6 for Soil/Terrestrial, 3.9 for Aquatic, and 3.0 for Animal species. [src: amr_pangenome_atlas] These results position BERDL as a platform for integrating pangenome conservation, environmental metadata, AMR mechanisms, and taxonomy, while the reported associations do not establish causality. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Role in within-species AMR strain-variation analysis

The strain-variation analysis used BERDL's `kbase_ke_pangenome` `gene`, `gene_genecluster_junction`, `genome`, `genome_ani`, and `ncbi_env` tables to examine AMR prevalence, co-occurrence, phylogenetic structure, ecotypes, temporal patterns, and environmental burden across bacterial strains. [src: amr_strain_variation]

AMR variation was extensive at strain resolution: 51.3% of AMR gene-species occurrences were rare (≤5% prevalence), 41.3% were variable (5–95%), and 7.5% were fixed (≥95%). [src: amr_strain_variation] The study detected 1,517 resistance islands across 705 species, with mean island size 6.2 genes, median size 4, maximum size 43, and mean phi coefficient 0.827. [src: amr_strain_variation] These findings support a BERDL-enabled [[concepts/resistance-islands]] view of tightly co-inherited AMR modules, although co-occurrence does not prove co-selection.

ANI-based Mantel tests showed significant AMR phylogenetic signal in 701 of 1,261 species (55.6%; FDR < 0.05), with median Mantel r = 0.247. [src: amr_strain_variation] Non-core AMR genes had stronger signal than core genes (median r = 0.222 versus 0.117; paired *t*-test *t* = -8.35, *p* = 7.0e-16, *n* = 489). [src: amr_strain_variation] This contributes to [[concepts/phylogenetic-amr-structure]], while the report notes that prevalence structure and transmission direction cannot be inferred from this result alone. [src: amr_strain_variation]

## Role in pan-bacterial AMR pangenome analysis

The pan-bacterial AMR atlas used `kbase_ke_pangenome` tables including `bakta_amr`, `gene_cluster`, `bakta_annotations`, `eggnog_mapper_annotations`, `bakta_pfam_domains`, `pangenome`, `genome`, `gtdb_taxonomy_r214v1`, `ncbi_env`, and `alphaearth_embeddings_all_years`. [src: amr_pangenome_atlas]

The census contained 83,008 AMRFinderPlus hits on gene-cluster representatives, covering 82,908 distinct clusters across 14,723 species, or 53.2% of 27,690 pangenome species. [src: amr_pangenome_atlas] AMR genes were 30.3% core versus 46.8% for the pangenome baseline (OR = 0.49, chi-squared = 23,117, *p* approximately 0), and the auxiliary genome was 2.2× enriched for AMR (33.6% versus 15.3%). [src: amr_pangenome_atlas]

Gammaproteobacteria contained 45% of all AMR clusters (37,752/83,008). [src: amr_pangenome_atlas] Functional analysis of 77K AMR clusters with eggNOG annotations found 7.05× enrichment of COG V (Defense mechanisms), 1.93× enrichment of COG P (Inorganic ion transport), and 1.50× enrichment of COG J (Translation). [src: amr_pangenome_atlas] Mechanism classification used keyword matching against AMRFinderPlus product descriptions rather than a CARD ontology mapping; consequently, 22.2% of hits were Other/Unclassified. [src: amr_pangenome_atlas]

## Role in AlphaFold annotation-gap analysis

The AlphaFold analysis used `kbase_ke_pangenome.gene_cluster`, `bakta_annotations`, `interproscan_domains`, and `kescience_alphafold.alphafold_msa_depths` to connect pangenome class, UniRef100 linkage, hypothetical status, domain annotations, and MSA depth. [src: alphafold_msa_annotation]

Of 132,531,501 total gene clusters, 38,804,903 (29.3%) had a real UniProt accession through `bakta_annotations.uniref100`, and 38,051,842 (28.7%) bridged successfully to AlphaFold MSA-depth records. [src: alphafold_msa_annotation] The bridged dataset had a strong pangenome-class gradient: core clusters had median MSA depth of 15,308, compared with 5,527 for auxiliary non-singletons and 5,299 for auxiliary-plus-singleton clusters. [src: alphafold_msa_annotation]

Across 38,051,842 gene-cluster–UniProt pairs, MSA depth correlated with InterProScan domain-hit count (Spearman ρ = 0.7563). [src: alphafold_msa_annotation] The analysis identified 415,603 core clusters with MSA depth below 10, including 286,439 hypothetical proteins (68.9%), 137 EC-annotated proteins (0.033%), and 346 KEGG-mapped proteins (0.083%). [src: alphafold_msa_annotation] These low-depth core proteins form a prioritized hypothesis set for structural and functional characterization, not a confirmed set of essential or biochemically characterized proteins. [src: alphafold_msa_annotation]

## Pangenome identifier mapping

ADP1 and BERDL use different pangenome cluster naming systems: ADP1 uses mmseqs2-style identifiers, while BERDL uses centroid gene identifiers. [src: acinetobacter_adp1_explorer]

The bridge uses BERDL's `gene_genecluster_junction` table to connect BERDL cluster IDs to member gene IDs, which match `feature_id` values in the ADP1 `pan_genome_features` table. [src: acinetobacter_adp1_explorer] This mapping connected all 4,891 BERDL clusters to 4,081 unique ADP1 clusters, with 100% gene-level matching across 43,754 genes. [src: acinetobacter_adp1_explorer]

The same cross-reference enabled phenotype analyses to assign pangenome conservation status to ADP1 genes and compare genes with and without deletion-collection growth measurements. [src: adp1_deletion_phenotypes] In the triple-essentiality analysis, the BERDL-linked `genome_features` table contained 5,852 genes and 51 columns, while the shared `gene_phenotypes` table contained 239,584 rows. [src: adp1_triple_essentiality]

## Limitations and data gaps

The 120 reactions without BERDL biochemical matches, representing 9% of the ADP1 reaction set, may be custom or draft reactions not yet represented in [[entities/modelseed]]. [src: acinetobacter_adp1_explorer] ADP1 was absent from the BERDL [[entities/fitness-browser]] collection, so its database's mutant growth measurements on eight carbon sources provide a resource not otherwise available for this organism in BERDL. [src: acinetobacter_adp1_explorer]

ADP1 pangenome core/accessory assignments came from a species-level *A. baylyi* pangenome and may have limited population-level resolution. [src: adp1_deletion_phenotypes] The proteomics signal used for ADP1 essentiality was averaged across seven *Acinetobacter* strains rather than measured exclusively in ADP1. [src: adp1_triple_essentiality]

The aromatic-catabolism study's FBA blind-spot conclusions are limited by incomplete reaction mappings, and its Complex I-associated assignments beyond the core nuo operon rely on phenotypic correlation rather than demonstrated physical association. [src: aromatic_catabolism_network] Its cross-species fitness data mix organisms with different respiratory-chain architectures, and the co-fitness analysis used only 8 conditions. [src: aromatic_catabolism_network]

The annotation-gap study was limited by draft-model errors, non-unique gapfill solutions, manual carbon-source mapping, fitness-threshold sensitivity, incomplete GapMind scope, and phylogenetic bias. [src: annotation_gap_discovery] Twelve of its 14 organisms were Proteobacteria, and its knockout validation was inconclusive because gapfilled reactions were required for model growth, making the test circular. [src: annotation_gap_discovery]

The AMR analyses are affected by clinical sampling bias, incomplete AMR annotation, metadata sparsity, uneven genome coverage, approximate environmental labels, and limited matched antibiotic experiments. [src: amr_fitness_cost, amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation] The within-species study excluded species with more than 500 genomes from relevant Mantel analyses, and 52.7% of genomes lacked a classifiable isolation source. [src: amr_strain_variation] Resistance-island results establish co-occurrence rather than mobility, co-selection, or functional synergy. [src: amr_strain_variation]

The AlphaFold MSA-depth analysis covered only 29.3% of all gene clusters and used representative sequences, so within-cluster diversity was not measured. [src: alphafold_msa_annotation] Its analyzed genomes were taxonomically imbalanced, and the MSA-depth/domain-richness relationship was not subgroup-stratified. [src: alphafold_msa_annotation]

The prophage ecology analysis is additionally limited by annotation-based prophage identification, which may include domesticated remnants and bacterial homologs; genome-size confounding; coarse environment categories; indirect genus-level NMDC inference; limited replication in module co-occurrence tests; and biased AlphaEarth embedding coverage. [src: prophage_ecology] Dedicated prophage detection with geNomad or VIBRANT, formal partial PERMANOVA, and genomic analysis of anti-defense islands were identified as needed follow-up work. [src: prophage_ecology]

## Related pages

- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/alphaearth-environmental-embeddings]]
- [[entities/alphafold-protein-structure-database]]
- [[entities/amrfinderplus]]
- [[entities/bakta]]
- [[entities/diamond]]
- [[entities/eggnog]]
- [[entities/fitness-browser]]
- [[entities/gtdb]]
- [[entities/interproscan]]
- [[entities/modelseed]]
- [[entities/flux-balance-analysis]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/proteomics]]
- [[entities/uniprot]]
- [[entities/esmfold]]
- [[entities/gapmind]]
- [[entities/complex-i]]
- [[entities/ndh-2]]
- [[entities/pqq]]
- [[entities/pqq-biosynthesis]]
- [[entities/iron]]
- [[entities/protocatechuate-3-4-dioxygenase]]
- [[entities/quinate-aromatic-degradation]]
- [[entities/mmseqs2]]
- [[entities/terminase-large-subunit]]
- [[concepts/msa-depth]]
- [[concepts/structural-novelty]]
- [[concepts/annotation-gap]]
- [[concepts/evidence-triangulation]]
- [[concepts/multi-omics-integration]]
- [[concepts/pangenome-integration]]
- [[concepts/metabolic-model-gapfilling]]
- [[concepts/metabolic-support-networks]]
- [[concepts/nadh-flux-respiratory-constraints]]
- [[concepts/method-concordance]]
- [[concepts/environmental-resistome]]
- [[concepts/core-accessory-resistance]]
- [[concepts/resistance-islands]]
- [[concepts/phylogenetic-amr-structure]]
- [[concepts/compensatory-evolution]]
- [[concepts/prophage-genome-modularity]]
- [[concepts/module-versus-lineage-ecology]]
- [[concepts/microbial-arms-race]]
- [[summaries/acinetobacter_adp1_explorer__REPORT]]
- [[summaries/adp1_deletion_phenotypes__REPORT]]
- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/alphafold_msa_annotation__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]
- [[summaries/amr_environmental_resistome__REPORT]]
- [[summaries/amr_fitness_cost__REPORT]]
- [[summaries/amr_pangenome_atlas__REPORT]]
- [[summaries/amr_strain_variation__REPORT]]
- [[summaries/prophage_ecology__REPORT]]

See also: [[summaries/amr_cofitness_networks__REPORT]]

See also: [[summaries/bacdive_metal_validation__REPORT]]

See also: [[summaries/bacdive_phenotype_metal_tolerance__REPORT]]

See also: [[summaries/ecotype_env_reanalysis__REPORT]]

See also: [[summaries/enigma_sso_asv_ecology__REPORT]]

See also: [[summaries/fitness_modules__REPORT]]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/metal_cross_resistance__REPORT]]

See also: [[summaries/metal_resistance_global_biogeography__REPORT]]

See also: [[summaries/pgp_pangenome_ecology__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]

See also: [[summaries/soil_metal_functional_genomics__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]