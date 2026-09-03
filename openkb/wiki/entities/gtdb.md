---
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/soil_metal_functional_genomics__REPORT.md", "summaries/paperblast_explorer__REPORT.md", "summaries/nmdc_context_audit__REPORT.md", "summaries/module_conservation__REPORT.md", "summaries/metal_resistance_global_biogeography__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/metal_cross_resistance__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/lab_field_ecology__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/euk_in_prok_correlates__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/env_embedding_explorer__REPORT.md", "summaries/enigma_sso_asv_ecology__REPORT.md", "summaries/ecotype_functional_differentiation__REPORT.md", "summaries/ecotype_env_reanalysis__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md"]
type: "Dataset"
description: "Taxonomic and phylogenetic database supporting genome and pangenome analysis"
---

# Genome Taxonomy Database

Also known as **GTDB**, the Genome Taxonomy Database is a taxonomic and phylogenetic resource used to organize bacterial species and evaluate whether observed genomic patterns persist across taxonomic lineages. [src: alphafold_msa_annotation, amr_environmental_resistome, amr_pangenome_atlas]

## Relevance to the reports

The AlphaFold MSA annotation report references GTDB as a framework for analysing conserved-yet-novel bacterial proteins. It identifies 415,603 core gene clusters with AlphaFold MSA depth below 10, including 68.9% classified as hypothetical, distributed across 14,768 species clades. [src: alphafold_msa_annotation] These [[concepts/structural-novelty]] candidates motivate mapping conserved proteins onto GTDB phylogeny to identify lineages with unusually high densities of proteins with limited sequence representation and to refine [[concepts/annotation-gap]] priorities within bacterial [[concepts/pangenome-integration]]. [src: alphafold_msa_annotation]

In the environmental resistome analysis, the `gtdb_taxonomy_r214v1` collection was used alongside genome, pangenome, AMR, and environment tables to provide taxonomy and phylogenetic grouping for 14,723 bacterial species. [src: amr_environmental_resistome] GTDB-based phylum and family groupings enabled tests of whether environment-associated AMR differences persisted after controlling for phylogenetic structure. [src: amr_environmental_resistome]

Five of six tested major phyla—Pseudomonadota, Bacillota_A, Actinomycetota, Bacteroidota, and Bacillota—showed significant within-phylum environment effects on AMR, while Chloroflexota was non-significant; Bacteroidota had the largest within-phylum effect (η² = 0.130). [src: amr_environmental_resistome] At the family level, 20 of 141 testable families showed significant within-family environment effects after FDR correction, including Enterobacteriaceae, Bacteroidaceae, Lachnospiraceae, and Pseudomonadaceae. [src: amr_environmental_resistome]

The pan-bacterial AMR atlas likewise used `gtdb_taxonomy_r214v1` with genome, pangenome, AMR, and environmental tables to analyze 83,008 AMRFinderPlus hits across 14,723 species. [src: amr_pangenome_atlas] GTDB taxonomic groupings showed that AMR density is strongly phylogenetically structured: Gammaproteobacteria contained 45% of all AMR clusters (37,752/83,008), while Klebsiella, Salmonella, Citrobacter, and Enterobacter were among the highest-density genera. [src: amr_pangenome_atlas] Within phyla, pangenome openness was positively correlated with AMR count in 8 of 10 tested phyla, but the overall correlation was near zero (rho=0.006), indicating that phylogeny dominates the aggregate signal. [src: amr_pangenome_atlas]

These analyses support the conclusion that environmental structuring of the resistome is not solely a consequence of differences in taxonomic composition, while the reports note that environment and phylogeny remain deeply entangled and that many families do not span enough environments for testing. [src: amr_environmental_resistome] GTDB classifications therefore provide the framework for separating broad phylogenetic structure from within-lineage ecological and pangenomic effects, rather than eliminating confounding between these factors. [src: amr_environmental_resistome, amr_pangenome_atlas]

### Fitness-module conservation and GTDB sampling

The fitness-module conservation analysis used a KBase pangenome gene-to-cluster link table, with GTDB providing the genome context for pangenome construction and conservation assessment. [src: module_conservation] Pangenome links were available for 29 of the 32 module organisms; Cola, Kang, and SB2B lacked links because their species had too few genomes in GTDB for pangenome construction. [src: module_conservation]

Among 974 ICA modules with at least three mapped genes, 577 (59%) were classified as core modules (>90% core genes), 349 (36%) as mixed modules (50–90% core), and 48 (5%) as accessory modules (<50% core); the median module was 93.4% core. [src: module_conservation] Module genes were 86.0% core compared with 81.5% for all genes, an enrichment of +4.5 percentage points (OR=1.46, p=1.6e-87). [src: module_conservation] The analysis found no relationship between module-family breadth across organisms and conservation (Spearman rho=-0.01, p=0.914). [src: module_conservation]

These results connect GTDB-supported pangenome sampling to [[concepts/fitness-conservation]] and [[concepts/pangenome-integration]]: co-regulated fitness-response units were modestly enriched in the conserved genome, but the high 81.5% baseline core rate produced a ceiling effect. [src: module_conservation] The three organisms without GTDB pangenome links and the uneven sampling underlying pangenome construction limit how broadly these module-conservation results can be generalized. [src: module_conservation]

### Within-species AMR strain variation

The within-species AMR strain-variation analysis examined 1,305 species and 180,025 genomes, using taxonomic groupings to compare AMR variability across bacterial lineages. [src: amr_strain_variation] Median AMR variability differed among reported phyla, ranging from 0.487 in Bacillota to 0.600 in Bacillota_A; Pseudomonadota, which included 591 species, had a median variability index of 0.533. [src: amr_strain_variation]

GTDB-associated lineage context is also relevant to the report's finding that AMR profiles track phylogeny within species. Among 1,261 species tested with ANI-based Mantel analyses, 701 (55.6%) showed significant AMR phylogenetic signal after FDR correction, with a median Mantel r of 0.247 and 87.8% of species showing positive correlations. [src: amr_strain_variation] Non-core, putatively acquired AMR genes had a higher median Mantel r than core genes (0.222 versus 0.117; paired t-test t = -8.35, p = 7.0e-16, n = 489), suggesting lineage-restricted maintenance after acquisition, although the report notes that near-universal core-gene prevalence suppresses distance-based variation. [src: amr_strain_variation] This result extends the existing [[concepts/phylogenetic-amr-structure]] view from cross-species taxonomic structure to strain-level patterns within species.

The same analysis identified 1,517 resistance islands across 705 species, with a mean island size of 6.2 genes and a mean phi coefficient of 0.827. [src: amr_strain_variation] Because 88% of these islands contained genes from multiple resistance mechanisms, GTDB-defined lineages provide a useful framework for asking whether tightly co-inherited AMR modules are concentrated in particular taxonomic groups. [src: amr_strain_variation] These findings connect GTDB-based phylogenetic organization with [[concepts/resistance-islands]], while the report cautions that co-occurrence does not prove co-selection. [src: amr_strain_variation]

### Pangenome integration in AMR fitness analysis

GTDB genome sampling was used to classify AMR genes as core or accessory in the AMR fitness-cost analysis, with genes present in at least 95% of sampled genomes treated as core. [src: amr_fitness_cost] Across Fitness Browser species, GTDB sampling was uneven: the median number of genomes was 9, with a range of 2–399. [src: amr_fitness_cost] Consequently, core/accessory assignments are imprecise for sparsely sampled species; for example, presence in all 9 sampled genomes can meet the core threshold without establishing core status at greater sampling depth. [src: amr_fitness_cost]

The AMR fitness analysis found no meaningful fitness-cost difference between core and accessory AMR genes: both groups had mean knockout fitness of −0.024, Cohen’s d = 0.002, and Mann–Whitney p = 0.33. [src: amr_fitness_cost] The report considers this null result more informative for well-sampled species, including *Klebsiella michiganensis* with 399 genomes, *Bacteroides thetaiotaomicron* with 287 genomes, and *Sinorhizobium meliloti* with 241 genomes. [src: amr_fitness_cost]

The pan-bacterial AMR atlas used GTDB-associated pangenome conservation measures to compare AMR genes with species-wide core/accessory baselines across 14,723 species. [src: amr_pangenome_atlas] AMR genes were 30.3% core versus 46.8% for the pangenome baseline, and 63.7% of 4,252 species in a paired analysis had a lower AMR core fraction than their species baseline. [src: amr_pangenome_atlas] The strain-variation analysis provides strain-resolution support for this distinction: 77.3% of atlas-defined Core AMR gene-species occurrences were fixed, while 78.7% of Singleton occurrences were rare. [src: amr_strain_variation] Together, these results illustrate how taxonomic representation and sampling depth affect [[concepts/core-accessory-resistance]] inference and the interpretation of [[concepts/pangenome-integration]] results. [src: amr_fitness_cost, amr_pangenome_atlas, amr_strain_variation]

## Related resources

- [[summaries/alphafold_msa_annotation__REPORT]] [src: alphafold_msa_annotation]
- [[summaries/amr_environmental_resistome__REPORT]] [src: amr_environmental_resistome]
- [[summaries/amr_fitness_cost__REPORT]] [src: amr_fitness_cost]
- [[summaries/amr_pangenome_atlas__REPORT]] [src: amr_pangenome_atlas]
- [[summaries/amr_strain_variation__REPORT]] [src: amr_strain_variation]
- [[entities/alphafold-protein-structure-database]]
- [[concepts/msa-depth]]
- [[concepts/structural-novelty]]
- [[concepts/annotation-gap]]
- [[concepts/environmental-resistome]]
- [[concepts/phylogenetic-amr-structure]]
- [[concepts/resistance-islands]]
- [[concepts/core-accessory-resistance]]
- [[concepts/pangenome-integration]]
- [[concepts/fitness-conservation]]

See also: [[summaries/annotation_gap_discovery__REPORT]]

See also: [[summaries/ecotype_env_reanalysis__REPORT]]

See also: [[summaries/ecotype_functional_differentiation__REPORT]]

See also: [[summaries/enigma_sso_asv_ecology__REPORT]]

See also: [[summaries/env_embedding_explorer__REPORT]]

See also: [[summaries/essential_genome__REPORT]]

See also: [[summaries/euk_in_prok_correlates__REPORT]]

See also: [[summaries/fitness_modules__REPORT]]

See also: [[summaries/lab_field_ecology__REPORT]]

See also: [[summaries/metabolic_capability_dependency__REPORT]]

See also: [[summaries/metal_cross_resistance__REPORT]]

See also: [[summaries/metal_fitness_atlas__REPORT]]

See also: [[summaries/metal_resistance_global_biogeography__REPORT]]

## Related Documents
- [[summaries/module_conservation__REPORT]]


See also: [[summaries/nmdc_context_audit__REPORT]]

See also: [[summaries/paperblast_explorer__REPORT]]

See also: [[summaries/soil_metal_functional_genomics__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]