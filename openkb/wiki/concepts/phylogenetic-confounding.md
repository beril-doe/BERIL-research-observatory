---
type: "Concept"
sources: ["summaries/t4ss_cazy_environmental_hgt__REPORT.md", "summaries/soil_metal_functional_genomics__REPORT.md", "summaries/snipe_defense_system__REPORT.md", "summaries/pitfalls.md", "summaries/pathway_capability_dependency__REPORT.md", "summaries/pangenome_openness__REPORT.md", "summaries/metal_resistance_global_biogeography__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/lab_field_ecology__REPORT.md", "summaries/ibd_phage_targeting__REPORT.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/euk_in_prok_correlates__REPORT.md", "summaries/enigma_contamination_functional_potential__REPORT.md", "summaries/ecotype_env_reanalysis__REPORT.md", "summaries/ecotype_analysis__REPORT.md", "summaries/cf_formulation_design__REPORT.md", "summaries/caulobacter_fur_lipida_loss__REPORT.md", "summaries/berdl_data_atlas__REPORT.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md"]
description: "Shared ancestry can make microbial trait and environment associations appear causal."
---

# Phylogenetic Confounding

## Definition

**Phylogenetic confounding** occurs when an apparent association between a microbial trait and an outcome is produced, or substantially amplified, by shared evolutionary history rather than by an independent causal relationship. In this setting, phenotypes can function as proxies for taxonomic membership, making a biologically plausible association difficult to distinguish from a lineage-composition effect. [src: bacdive_phenotype_metal_tolerance]

This issue connects microbial trait prediction with [[concepts/phylogenetic-amr-structure]], [[concepts/organism-specificity]], [[concepts/phenotypic-landscape]], and analyses of whether phylogeny or environment better explains genome-wide gene-content variation. [src: bacdive_phenotype_metal_tolerance, ecotype_analysis, ecotype_env_reanalysis]

## Evidence from BacDive Metal-Tolerance Analysis

The BacDive analysis compared ten phenotype features with genome-based metal-tolerance scores across 5,647 GTDB species, including 3,994 species with at least five phenotype features. [src: bacdive_phenotype_metal_tolerance]

Gram-negative species had higher metal-tolerance scores than Gram-positive species, with Cohen’s d = -0.61, p < 1e-60, and n = 3,272. However, the association could not be tested within taxonomic classes and was largely a between-lineage comparison involving Gram-positive Actinomycetes and Gram-negative Proteobacteria. [src: bacdive_phenotype_metal_tolerance]

Seven of ten phenotype features were individually significant after FDR correction, including Gram stain, oxidase, motility, urease, enzyme breadth, nitrate reduction, and catalase. These univariate associations do not establish that the phenotypes independently predict metal tolerance because their distributions are themselves structured by taxonomy. [src: bacdive_phenotype_metal_tolerance]

Taxonomy alone explained 35.4% of metal-tolerance variance in five-fold phylogenetic-blocked cross-validation, whereas phenotype features alone explained 16.3%. Adding phenotype features to taxonomy reduced the model’s R² to 0.345, compared with 0.354 for taxonomy alone, producing delta R² = -0.009. [src: bacdive_phenotype_metal_tolerance]

The full model, which also included the number of metal-resistance gene clusters, achieved R² = 0.633. SHAP analysis identified taxonomic class/order codes and `n_metal_clusters` as the dominant predictors, while phenotype features contributed minimally after taxonomy was included. [src: bacdive_phenotype_metal_tolerance]

## Evidence from Ecotype Correlation Analysis

The original ecotype analysis tested environmental similarity and phylogenetic relatedness as predictors of gene-content similarity across 172 bacterial species with sufficient environmental and phylogenetic data. It used [[entities/alphaearth-environmental-embeddings]], genome metadata, geographic coordinates, pangenome composition, and gene-cluster profiles from [[entities/kbase-ke-pangenome]]. [src: ecotype_analysis]

Phylogeny had the larger median partial correlation with gene-content similarity: 0.0143 for phylogeny versus 0.0025 for environment. Phylogeny dominated in 60.5% of species, while environment dominated in 39.5%. [src: ecotype_analysis]

Only 12 species (7.0%) showed a significant positive environment effect, 4 species (2.3%) showed a significant negative environment effect, and 156 species (90.7%) showed no significant environmental effect. These results provide cross-project support for the possibility that broad environmental associations with genome-wide gene content can be weaker than lineage-associated signals. [src: ecotype_analysis]

The comparison between environmental and host-associated bacteria found no significant difference in environmental effects (p=0.66). Thus, the original analysis did not support the expectation that free-living bacteria would show stronger environment effects simply because geographic coordinates are more interpretable for them. [src: ecotype_analysis]

### Genome-level environmental reanalysis

A follow-up reanalysis tested whether the original weak environment signal was explained by clinical sampling bias. Of 224 species selected for the AlphaEarth ecotype analysis, 106 (47%) were majority human-associated, 47 (21%) were majority environmental, and 71 (32%) were mixed/other, using genome-level harmonized environment categories and majority-vote classification. [src: ecotype_env_reanalysis]

The reanalysis did not find stronger environment–gene content correlations in environmental species. Environmental species had a median partial correlation of 0.051, compared with 0.084 for human-associated species; the one-sided Mann–Whitney test gave U=1536 and p=0.83. The result was opposite to the predicted direction. [src: ecotype_env_reanalysis]

The continuous analysis likewise found no relationship between the fraction of environmental genomes and partial-correlation strength (Spearman rho=-0.085, p=0.25), or between the fraction of human-associated genomes and partial-correlation strength (rho=0.030, p=0.69). [src: ecotype_env_reanalysis]

Species with missing partial correlations were disproportionately environmental rather than human-associated: 10/47 environmental species (21%), 13/66 mixed/other species (20%), and 7/100 human-associated species (7%) had NaN values. Because environmental species were filtered more heavily, correcting this issue would not plausibly turn the observed comparison into evidence for a stronger environmental effect; the reanalysis argues that it would, if anything, strengthen the null interpretation. [src: ecotype_env_reanalysis]

The reanalysis produced a median partial correlation of 0.081 across 183 species, compared with 0.003 in the original analysis. The 27-fold difference was attributed to using all genomes with embeddings, up to 3,505 per species, rather than diversity-maximizing downsampling to a maximum of 250 genomes, as well as to differences in genome sets and distance distributions. The within-method group comparison remains the relevant test, but absolute correlation magnitudes are not directly comparable across analyses. [src: ecotype_env_reanalysis]

## Examples of Confounding

### Urease

Urease-positive species had lower overall metal-tolerance scores than urease-negative species (d = -0.175, q = 9.1e-06), reversing the prediction that nickel-dependent urease physiology would confer greater nickel tolerance. [src: bacdive_phenotype_metal_tolerance]

The effect was concentrated in Actinomycetes, where urease-positive species had d = -0.59, p < 1e-16; it disappeared in Gammaproteobacteria (d = +0.08, not significant) and Bacilli (d = +0.06, not significant). This pattern indicates that lineage composition, rather than urease itself, explains the aggregate association. [src: bacdive_phenotype_metal_tolerance]

### Catalase

Catalase positivity showed a small positive overall association with metal tolerance (d = +0.104, q = 0.041), but the direction reversed within major classes. Catalase-negative species scored higher within Actinomycetes (d = -0.62, p < 1e-5), Gammaproteobacteria (d = -0.49, p = 0.004), and Betaproteobacteria (d = -0.51, p = 0.006). [src: bacdive_phenotype_metal_tolerance]

This is a Simpson’s-paradox-like pattern: the aggregate association is produced by differences in class composition, while within-class comparisons show the opposite direction. [src: bacdive_phenotype_metal_tolerance]

### Oxygen tolerance and metabolic breadth

The anaerobe–aerobe comparison showed a negligible difference in metal tolerance (d = -0.016, p = 0.55), despite a marginally significant three-group Kruskal–Wallis test (H = 8.53, p = 0.014). [src: bacdive_phenotype_metal_tolerance]

Metabolite breadth was not associated with metal tolerance (rho = -0.013, q = 0.47), indicating that broad substrate utilization did not provide an independent proxy for the composite metal-tolerance score in this analysis. [src: bacdive_phenotype_metal_tolerance]

### Environmental similarity and gene content

The ecotype analyses illustrate a related form of confounding at the genome-comparison level: phylogenetic relatedness was more often and more strongly associated with gene-content similarity than environmental similarity in the original analysis, and a genome-level reanalysis found no stronger signal among environmental species. [src: ecotype_analysis, ecotype_env_reanalysis]

These are cross-species correlation results, not proof that environmental adaptation is absent. They suggest the hypothesis that environmental effects may be heterogeneous across species or concentrated in particular gene subsets rather than in whole-genome gene content. [src: ecotype_analysis, ecotype_env_reanalysis]

## Interpretation

The findings support a distinction between a phenotype being biologically meaningful and a phenotype providing independent predictive information. Gram-negative envelope structure, urease-associated nickel handling, catalase activity, and oxygen physiology may affect particular metal responses, but their aggregate associations with composite metal tolerance were inseparable from taxonomic structure in this dataset. [src: bacdive_phenotype_metal_tolerance]

Similarly, phylogeny’s stronger association with genome-wide gene-content similarity does not establish that environment is irrelevant. It suggests that vertical inheritance can dominate broad genomic similarity while environmental selection acts on specific functions, mobile loci, or accessory genes. This interpretation is consistent with [[concepts/horizontal-gene-transfer]] and [[concepts/pangenome-integration]]. [src: ecotype_analysis, ecotype_env_reanalysis]

The environmental reanalysis weakens the specific explanation that clinical sampling bias accounts for the ecotype null result. Although 47% of the analyzed species were human-associated and only 21% environmental, environmental species did not show stronger correlations under either binary or continuous classification. [src: ecotype_env_reanalysis]

The absence of a lifestyle difference also does not imply that AlphaEarth geography is irrelevant. Environmental embeddings may capture geographic differentiation without capturing ecological variables that determine gene content, while human-associated species may carry real regional epidemiological structure. These explanations remain hypotheses rather than established mechanisms. [src: ecotype_env_reanalysis]

Genome-encoded resistance repertoire was more informative than broad phenotype metadata: adding `n_metal_clusters` to taxonomy and phenotype features increased R² from the taxonomy-only value of 0.354 to 0.633. This supports integrating phenotype observations with genomic resistance data through [[concepts/pangenome-integration]] rather than treating phenotype labels as standalone predictors. [src: bacdive_phenotype_metal_tolerance]

The result also highlights the importance of [[concepts/method-concordance]]: univariate tests, class-stratified analyses, blocked cross-validation, and SHAP interpretation all pointed toward strong taxonomic structure, whereas raw phenotype associations alone could have been overinterpreted. [src: bacdive_phenotype_metal_tolerance]

The ecotype analyses used partial correlations between environmental, phylogenetic, and gene-content distance relationships. Interpretation is limited by 28.4% AlphaEarth coverage in the original analysis, incomplete or imprecise geographic coordinates, potentially uninformative coordinates for host-associated organisms, the assumption of linear relationships between distance matrices, and the reanalysis’s use of no downsampling. [src: ecotype_analysis, ecotype_env_reanalysis]

## Scope and Limitations

The response variable in the BacDive analysis was a genome-based Metal Fitness Atlas prediction rather than a direct experimental measurement of metal tolerance, so the reported relationships are ultimately phenotype-to-genome correlations. [src: bacdive_phenotype_metal_tolerance]

Species-name matching linked 37,368 BacDive strains to pangenome and metal-score data, corresponding to 38.4% of the bridge and 5,647 unique GTDB species; GCA accession matching was not implemented. [src: bacdive_phenotype_metal_tolerance]

The direct Fitness Browser–BacDive validation included only 12 organisms, all Gram-typed organisms were Gram-negative, and the single anaerobe had only one metal tested. These data could not independently test the strongest phenotype associations. [src: bacdive_phenotype_metal_tolerance]

The original ecotype analysis included 172 species selected from 224 target species and used 13,381 genomes in its expanded metadata set. Its environmental proxy had only 28.4% genome coverage, geographic metadata were often missing or imprecise, and host-associated coordinates may represent collection locations rather than organismal microenvironments. [src: ecotype_analysis]

The reanalysis classified 224 species using majority environment labels and analyzed partial correlations for 213 species, with 30 species-level correlations reported as NaN. *Klebsiella pneumoniae* was excluded because gene-cluster extraction exceeded Spark’s `maxResultSize` and no correlation data were available for it. [src: ecotype_env_reanalysis]

The reanalysis used all genomes with embeddings rather than the original diversity-maximizing downsampling, yielding correlation magnitudes that are not directly comparable with the original values. Genome count may also affect statistical power, and majority-vote labels can obscure species containing heterogeneous environments. [src: ecotype_env_reanalysis]

## Tensions

The Gram-negative association is mechanistically plausible because the Gram-negative outer membrane can restrict metal-cation uptake, yet the available class-stratified analysis cannot separate that mechanism from broad Proteobacteria-versus-Actinomycetes lineage differences. [src: bacdive_phenotype_metal_tolerance]

Similarly, urease requires nickel handling, but the observed association was negative at the aggregate level and absent within the tested non-Actinomycete classes. Resolving whether urease contributes to nickel-specific tolerance therefore requires per-metal measurements within matched taxonomic lineages rather than composite scores across diverse species. [src: bacdive_phenotype_metal_tolerance]

The ecotype result creates a complementary interpretive tension: phylogeny dominated in most species in the original analysis, but environment dominated in 39.5% of species, and neither the original comparison (p=0.66) nor the genome-level reanalysis (p=0.83) found a significant lifestyle difference. [src: ecotype_analysis, ecotype_env_reanalysis]

The reanalysis also changes the interpretation of clinical sampling bias. The AlphaEarth subset is clinically skewed, but the environmental group did not show the predicted stronger signal even after harmonized genome-level classification. Thus, sampling bias remains a limitation and a possible source of power imbalance, but it is not supported as the principal explanation for the weak environment effect. [src: ecotype_env_reanalysis]

## Open Directions

- Apply phylogenetic generalized least squares or phylogenetic PCA to the species-level phenotype matrix and test whether any phenotype retains an association with metal tolerance after shared ancestry is removed. [src: bacdive_phenotype_metal_tolerance]
- Reanalyze per-metal fitness scores to determine whether urease predicts nickel tolerance specifically even though it does not predict composite metal tolerance. [src: bacdive_phenotype_metal_tolerance]
- Compare urease-positive and urease-negative organisms within the same taxonomic class using matched strains and direct nickel challenge experiments. [src: bacdive_phenotype_metal_tolerance]
- Add GCA accession matching to test whether increased species coverage changes the strength or taxonomic distribution of phenotype associations. [src: bacdive_phenotype_metal_tolerance]
- Compare downsampled and full-genome ecotype extraction to identify why the median partial correlation changes from 0.003 to 0.081 and whether the discrepancy is driven by sample size, genome composition, or distance distributions. [src: ecotype_analysis, ecotype_env_reanalysis]
- Reanalyze the ecotype data by gene function, including COG categories such as V-Defense and L-Mobile, to test whether environmental effects become detectable after whole-genome averaging is removed. [src: ecotype_analysis]
- Add genome count as a covariate and repeat the binary and continuous environment analyses to test whether unequal statistical power obscures a group effect. [src: ecotype_env_reanalysis]
- Compare AlphaEarth distances with direct environmental metadata and nonlinear distance-association methods to test whether environmental representation or linearity is suppressing ecological signal. [src: ecotype_analysis, ecotype_env_reanalysis]
- Repeat the analysis with structured ENVO terms from `env_broad_scale` to test whether more precise environmental classification changes the null result. [src: ecotype_env_reanalysis]
- Identify ecotype clusters within species and compare gene content between clusters while controlling for phylogenetic relatedness. [src: ecotype_analysis]

## Related Sources

See [[summaries/bacdive_phenotype_metal_tolerance__REPORT]] for the complete BacDive study summary. [src: bacdive_phenotype_metal_tolerance]

See [[summaries/ecotype_analysis__REPORT]] for the complete original ecotype correlation analysis summary. [src: ecotype_analysis]

See [[summaries/ecotype_env_reanalysis__REPORT]] for the genome-level environmental reanalysis. [src: ecotype_env_reanalysis]

See also [[summaries/berdl_data_atlas__REPORT]]. [src: berdl_data_atlas]

See also [[summaries/caulobacter_fur_lipida_loss__REPORT]]. [src: caulobacter_fur_lipida_loss]

See also [[summaries/cf_formulation_design__REPORT]]. [src: cf_formulation_design]

See also: [[summaries/enigma_contamination_functional_potential__REPORT]]

See also: [[summaries/euk_in_prok_correlates__REPORT]]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/gene_function_ecological_agora__REPORT]]

See also: [[summaries/ibd_phage_targeting__REPORT]]

See also: [[summaries/lab_field_ecology__REPORT]]

See also: [[summaries/metal_fitness_atlas__REPORT]]

See also: [[summaries/metal_resistance_global_biogeography__REPORT]]

See also: [[summaries/pangenome_openness__REPORT]]

See also: [[summaries/pathway_capability_dependency__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/snipe_defense_system__REPORT]]

See also: [[summaries/soil_metal_functional_genomics__REPORT]]

See also: [[summaries/t4ss_cazy_environmental_hgt__REPORT]]