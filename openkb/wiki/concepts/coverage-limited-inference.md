---
type: "Concept"
sources: ["summaries/soil_frontier_genomics__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/prophage_ecology__REPORT.md", "summaries/phb_granule_ecology__REPORT.md", "summaries/phage_defense_arsenal__REPORT.md", "summaries/nmdc_context_audit__REPORT.md", "summaries/nmdc_community_metabolic_ecology__REPORT.md", "summaries/metal_cross_resistance__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/lab_field_ecology__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/fitness_effects_conservation__REPORT.md", "summaries/field_vs_lab_fitness__REPORT.md", "summaries/euk_in_prok_correlates__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/enigma_contamination_functional_potential__REPORT.md"]
description: "Inference constrained by incomplete reference, sample, and study coverage"
---

# Coverage-Limited Inference

## Definition

Coverage-limited inference occurs when functional or ecological conclusions are constrained by the fraction of observations that can be mapped to usable reference taxa, genomes, clades, annotations, spatial locations, or independently represented studies. Low mapped coverage can reduce statistical power, distort community-level summaries, and make apparent associations sensitive to model specification. [src: enigma_contamination_functional_potential] [src: euk_in_prok_correlates] [src: soil_frontier_genomics]

This limitation is distinct from biological absence: an unmapped taxon, unsequenced environment, or poorly represented biome may still contribute substantially to the community, while its functional potential remains absent from the inferred feature set. [src: enigma_contamination_functional_potential] [src: soil_frontier_genomics] A related problem occurs when an ecological correlate is represented by too few independent studies or spatially representative samples: strong associations within a collection may reflect study, batch, or sampling-effort structure rather than a portable environmental effect. [src: euk_in_prok_correlates] [src: soil_frontier_genomics] Coverage-limited inference therefore connects [[concepts/annotation-gap]], [[concepts/resource-darkness]], [[concepts/pangenome-integration]], [[concepts/functional-redundancy]], [[concepts/batch-confounding]], [[concepts/geospatial-coverage-gaps]], [[concepts/spatial-sampling-effort]], and [[concepts/negative-out-of-sample-prediction]].

## Evidence from ENIGMA contamination analysis

The ENIGMA workflow retained 108 samples with both geochemistry and community composition, including 1,392 observed genera. [src: enigma_contamination_functional_potential] Only 530 genera mapped to the current GTDB-to-pangenome bridge, while 862 remained unmapped. [src: enigma_contamination_functional_potential]

Mapped coverage varied substantially across samples in strict and relaxed mapping modes: the mean mapped abundance fraction was 0.343, with a range from 0.031 to 0.854. [src: enigma_contamination_functional_potential] Coverage-aware analyses consequently used mapped abundance fraction as a covariate or restricted tests to samples with mapped abundance fraction at least 0.25. [src: enigma_contamination_functional_potential]

The species-proxy mode illustrates the severity of the problem at higher taxonomic resolution. It retained only genera mapping to exactly one GTDB species clade: 150 unique-clade genera out of 530 mapped genera. [src: enigma_contamination_functional_potential] Mean mapped abundance fraction fell to 0.031 in this mode, compared with 0.343 in strict and relaxed modes, and no high-coverage test was feasible at the threshold of 0.25. [src: enigma_contamination_functional_potential]

## Evidence from NMDC eukaryotic-fraction analysis

The NMDC analysis adds a second form of coverage limitation: ecological, study, and classifier-reference coverage. It examined 2,759 ReadbasedAnalysis runs from nine studies, but one NEON soil study contributed 1,186 runs, approximately 43% of the total. [src: euk_in_prok_correlates] Because each biome was approximately 80–100% nested within a single study, the apparent cross-study environmental effect could not be separated cleanly from study or batch coverage. [src: euk_in_prok_correlates]

Univariate matrix associations were strong (Kruskal–Wallis **H=77.8, p=1.3×10⁻¹⁷**), but environment prediction failed when entire studies were held out: out-of-study **R²=−0.30**, with detection AUC **0.56**, approximately chance. [src: euk_in_prok_correlates] The environment model therefore generalized worse than predicting the mean and performed no better than the study-only batch ceiling in the reported comparison. [src: euk_in_prok_correlates] Within the single NEON study, where environmental metadata varied within a common collection, local vegetation and geography were strongly associated with eukaryotic fraction, and a combined model achieved **5-fold R²=+0.17 ± 0.06**. [src: euk_in_prok_correlates]

This contrast shows that sufficient sample count does not guarantee sufficient independent coverage. A large number of runs can still provide weak evidence for a general environmental relationship when studies are unevenly represented or environmental categories are study-specific. [src: euk_in_prok_correlates]

Classifier reference coverage creates an additional constraint. In the NMDC collection, Kraken2 and Centrifuge produced approximately zero domain-level Eukaryota signal because their reference databases were prokaryote-restricted; GOTTCHA2 was the only usable estimator of eukaryotic fraction. [src: euk_in_prok_correlates] GOTTCHA2 measured detectable eukaryotic reads in **77%** of runs, with a median eukaryotic fraction of **2.7%** and a mean of **13.3%**, but these values are database-dependent relative estimates rather than calibrated absolute contamination. [src: euk_in_prok_correlates] An apparent absence in a classifier output may therefore indicate inadequate reference coverage rather than biological absence. [src: euk_in_prok_correlates]

## Evidence from global soil genomic-frontier analysis

The soil-frontier analysis extends coverage limitation from taxonomic and study mapping to spatial genomic representation. It analyzed **5,441 soil samples** containing clay content, mine proximity, nighttime lights, uranium, and functional-gene counts. [src: soil_frontier_genomics] A provisional Genomic Discovery Index (GDI), defined as **OTU Richness / (Mean Genome Completeness + 1)** and calculated in 1° spatial bins, identified forest (**902.36**) and cropland (**890.82**) as jointly highest-GDI biomes, while grassland (**503.42**) and wetland (**525.13**) had lower values. [src: soil_frontier_genomics]

The GDI results suggest a genomic representation gap in forest and cropland soils, but the scalar index is not yet validated. The formula combines richness and genome completeness, has no published precedent, and yields a GDI of 902 even when zero genomes are present if completeness is 0. [src: soil_frontier_genomics] Forest and cropland should not yet be treated as meaningfully rank-ordered: their GDI difference is 1.3%, and bootstrap confidence intervals have not been calculated. [src: soil_frontier_genomics]

The analysis also found a pH-associated discovery gap. Frontier areas with GDI > 1000 had mean pH = 6.74, compared with 5.94 in mapped areas, a **+0.8 pH-unit gap**. [src: soil_frontier_genomics] This supports the hypothesis that alkaline soil microbiomes are under-sampled in public genomic databases, but it does not distinguish a true assembly or annotation gap from fewer sequencing efforts at those pH values. [src: soil_frontier_genomics]

The reverse-causality concern is central: controlling for the number of 16S samples in each pH bin is required before interpreting the pH pattern as a genomic discoverability effect rather than [[concepts/spatial-sampling-effort]]. [src: soil_frontier_genomics]

## Clay shield analysis and negative predictive performance

The soil analysis tested whether clay content improves prediction of functional potential under environmental and industrial stressors. All three predictive model families had negative out-of-sample R²: Soil & Climate, **−0.205 ± 0.197**; Geochemical, **−0.331 ± 0.071**; and Industrial, **−0.221 ± 0.042**. [src: soil_frontier_genomics]

The shield-efficiency comparison found low-clay CV R² = **−0.268** and high-clay CV R² = **−0.292**, for a difference of **0.024** with 95% CI **[−0.423, 0.161]**. [src: soil_frontier_genomics] Clay appeared consistently as a feature with importance approximately **0.14**, but did not improve predictive accuracy in high-clay soils. [src: soil_frontier_genomics]

These results do not support the clay shield hypothesis at global scale, but they do not yet establish genuine biological unpredictability. The negative R² values may arise from train/test distributional shift caused by spatial autocorrelation within GroupKFold folds, high-leverage outliers dominating test-fold mean squared error, or true failure of the measured predictors to explain functional-gene counts at global scale. [src: soil_frontier_genomics] Only the third explanation supports a strong biological null interpretation; the first two would indicate a modelling or validation failure. [src: soil_frontier_genomics]

## Consequences for statistical inference

The predeclared confirmatory relationship between contamination and the site defense score was null in both relaxed and strict genus-level modes. Relaxed mapping gave rho = 0.0587, 95% bootstrap CI [-0.128, 0.250], p = 0.546, and FDR q = 0.862; strict mapping gave rho = 0.0682, 95% bootstrap CI [-0.111, 0.253], p = 0.483, and FDR q = 0.849. [src: enigma_contamination_functional_potential]

Coverage-adjusted exploratory models produced positive defense coefficients, but their strength depended on mapping mode, coverage adjustment, fraction handling, and multiple-testing correction. [src: enigma_contamination_functional_potential] In coverage-adjusted OLS models, the relaxed estimate was beta = 0.000751 with 95% bootstrap CI [0.000224, 0.001779], p = 0.000398, and q = 0.0462, whereas the strict estimate was beta = 0.000640 with CI [0.000169, 0.001538], p = 0.00354, and q = 0.130. [src: enigma_contamination_functional_potential]

Fraction-aware models used 212 sample-fraction rows, split evenly between the `0.2_micron_filter` and `10_micron_filter` fractions. [src: enigma_contamination_functional_potential] Within-fraction Spearman tests for defense were non-significant in both mapping modes, with p-values ranging from 0.767 to 0.898. [src: enigma_contamination_functional_potential] This weakens the interpretation that the positive adjusted association represents a robust within-fraction monotonic response. [src: enigma_contamination_functional_potential]

The NMDC results provide a parallel warning against unvalidated cross-collection regression. The cross-study association between sequencing depth and eukaryotic fraction was Spearman **rho = −0.29, p=5.2×10⁻⁷, n=292**, but measured-depth runs came from a handful of non-soil studies and the dominant NEON soil study had no depth values. [src: euk_in_prok_correlates] The association is therefore suggestive rather than evidence of a general depth effect. [src: euk_in_prok_correlates]

The combined evidence supports a calibrated conclusion: the ENIGMA confirmatory contamination-to-functional relationship remained null, positive exploratory defense associations persisted in some coverage-aware specifications, and the soil clay-shield comparison failed to improve out-of-sample prediction. [src: enigma_contamination_functional_potential] [src: soil_frontier_genomics] None of these results alone distinguishes biological redundancy or unpredictability from incomplete mapping, spatial sampling gaps, batch structure, or model failure. [src: enigma_contamination_functional_potential] [src: euk_in_prok_correlates] [src: soil_frontier_genomics]

## Mapping ambiguity as a second coverage problem

Coverage is not determined only by whether a genus maps; the quality and specificity of the mapping also matter. The ENIGMA bridge contained 8,242 genus-to-clade rows and had a long right tail in the number of clades per genus, with a maximum of 433 clades per genus. [src: enigma_contamination_functional_potential] The most ambiguous genera included *Pseudomonas* with 433 clades, *Streptomyces* with 378, *Prevotella* with 358, *Streptococcus* with 214, and *Mycobacterium* with 186. [src: enigma_contamination_functional_potential]

This many-to-many expansion can increase apparent functional representation while reducing taxonomic specificity. [src: enigma_contamination_functional_potential] Strict and relaxed modes therefore represent different compromises between coverage and mapping ambiguity rather than interchangeable estimates of the same underlying quantity. [src: enigma_contamination_functional_potential]

The NMDC classifier comparison shows the same tradeoff at the database level: a classifier with a prokaryote-restricted reference database cannot provide a reliable eukaryotic-fraction estimate, while GOTTCHA2 supplies a usable but database-dependent relative signal. [src: euk_in_prok_correlates] Reference choice must therefore be treated as part of the measurement model, not as a neutral implementation detail. [src: euk_in_prok_correlates]

## Relationship to functional redundancy

The absence of a robust broad functional response does not establish that contamination has no biological effect. [src: enigma_contamination_functional_potential] The ENIGMA report proposes that contamination-driven taxonomic turnover may be functionally redundant at genus-aggregated resolution, or that relevant adaptation may occur at species, strain, or pathway level rather than in broad COG-fraction summaries. [src: enigma_contamination_functional_potential] This is a hypothesis motivated by the null confirmatory result and coarse functional representation, not a directly demonstrated mechanism. [src: enigma_contamination_functional_potential]

The soil results provide a similar caution: clay showed correlational associations with microbial functional potential and some interaction with industrial stressors, but did not improve high-clay predictive accuracy. [src: soil_frontier_genomics] The report attributes the global-scale negative predictions potentially to spatial autocorrelation, batch effects, and unmeasured confounders, so functional redundancy remains only one possible explanation. [src: soil_frontier_genomics]

The NMDC findings reinforce the need to distinguish biological redundancy from incomplete observation. Environmental eukaryotic signal differed by matrix—freshwater samples were dominated by algal plastid, terrestrial samples showed mixed plant plastid and soil fungi or protists, and plant-root samples were dominated by non-plastid fungi or protists—but classifier and study coverage limited how broadly those patterns could be generalized. [src: euk_in_prok_correlates] A stable community-level summary may therefore reflect functional redundancy, missing taxa or annotations, inadequate spatial or reference coverage, or insufficient independent study coverage. [src: enigma_contamination_functional_potential] [src: euk_in_prok_correlates] [src: soil_frontier_genomics]

## Tensions

### Apparent adjusted defense signal versus null confirmatory association

Coverage-adjusted exploratory models yielded positive defense estimates, including an FDR-significant relaxed-mode coefficient with q = 0.0462. [src: enigma_contamination_functional_potential] However, the predeclared Spearman tests were non-significant in both mapping modes, and fraction-stratified tests did not show a strong within-fraction monotonic signal. [src: enigma_contamination_functional_potential] Resolving this tension requires determining whether adjustment removes coverage confounding, introduces sensitivity to covariate structure, or detects a conditional association that the marginal confirmatory test cannot capture. [src: enigma_contamination_functional_potential]

### Higher resolution versus usable coverage

Species-proxy mapping was intended to improve taxonomic specificity, but it reduced mean mapped abundance fraction to 0.031 and produced a non-significant defense trend of rho = 0.169 with p = 0.081. [src: enigma_contamination_functional_potential] Higher resolution currently comes at the cost of substantial information loss, preventing a strong test of whether species-level inference improves functional-response detection. [src: enigma_contamination_functional_potential]

### Strong pooled environmental association versus poor cross-study portability

In NMDC, matrix was strongly associated with eukaryotic fraction in the pooled collection, but environment failed to generalize under whole-study holdout (**R²=−0.30**, AUC **0.56**). [src: euk_in_prok_correlates] Within the NEON study, vegetation and geography were predictive, with within-study **R²=+0.17 ± 0.06**. [src: euk_in_prok_correlates] The tension is whether the pooled environmental pattern reflects a portable ecological relationship or study-specific coverage and batch structure; resolving it requires more independently sampled studies and batch-controlled replication across biomes. [src: euk_in_prok_correlates]

### Negative global prediction versus biological null interpretation

All three soil model families had negative out-of-sample R², but the report identifies distributional shift, test-fold outlier leverage, and genuine unpredictability as unresolved alternatives. [src: soil_frontier_genomics] Spatially blocked validation, influence diagnostics, and predictor-response analyses are required before the clay-shield result can be treated as a biological null rather than a coverage or modelling limitation. [src: soil_frontier_genomics]

### Genomic frontier signal versus sampling-effort bias

Frontier areas had mean pH = 6.74 versus 5.94 in mapped areas, but the GDI analysis did not yet control for the number of 16S samples per pH bin. [src: soil_frontier_genomics] The observed alkaline-soil gap could therefore represent under-sequencing effort rather than a specific difficulty in assembling or annotating alkaline-soil genomes. [src: soil_frontier_genomics]

## Open Directions

- Replace broad COG-fraction proxies with curated metal-stress and resistance gene sets, then test whether associations persist after mapped abundance fraction adjustment. [src: enigma_contamination_functional_potential]
- Expand the genus-to-clade bridge for the 862 unmapped observed genera and quantify how much contamination-associated abundance is recovered. [src: enigma_contamination_functional_potential]
- Obtain species- or strain-resolved ENIGMA taxonomy and compare functional coverage and effect estimates against strict, relaxed, and species-proxy modes. [src: enigma_contamination_functional_potential]
- Fit hierarchical well- or location-level models with depth, sampling date, and community fraction to test whether the exploratory defense association survives richer structure control. [src: enigma_contamination_functional_potential]
- Analyze coverage deciles and fraction-specific results jointly to identify whether the defense signal is concentrated in particular coverage regimes. [src: enigma_contamination_functional_potential]
- Extend the NMDC eukaryotic-fraction pipeline to aquatic and plant-associated studies, using within-study contrasts and study-held-out validation to test whether matrix-specific source patterns generalize beyond the NEON soil cohort. [src: euk_in_prok_correlates]
- Expand the number of independently represented studies, then compare random cross-validation with study-held-out validation to quantify how much environmental prediction is lost to study coverage and batch confounding. [src: euk_in_prok_correlates]
- Acquire extraction-kit, host-depletion, size-fractionation, and library-preparation metadata and test whether these unmeasured factors explain residual classifier or contamination differences. [src: euk_in_prok_correlates]
- Calibrate GOTTCHA2 eukaryotic fractions against spike-ins or an independent benchmark, and compare estimates across classifier databases to separate biological signal from reference-coverage effects. [src: euk_in_prok_correlates]
- Decompose the soil models’ negative R² into spatial distributional shift, outlier leverage, and residual unpredictability using spatial blocking and influence diagnostics. [src: soil_frontier_genomics]
- Recalculate GDI after rarefaction-correcting 16S richness, report richness and genome completeness separately, and add bootstrap 95% CIs before comparing biomes. [src: soil_frontier_genomics]
- Control GDI–pH analyses for the number of 16S samples per pH bin to distinguish alkaline-soil sampling gaps from assembly or annotation gaps. [src: soil_frontier_genomics]
- Re-run NB05 validations from the BERIL Observatory 16S tables and `kbase_ke_pangenome` completeness data; no local CSV output is available for these validations. [src: soil_frontier_genomics]

## Source

[[summaries/enigma_contamination_functional_potential__REPORT]]

[[summaries/euk_in_prok_correlates__REPORT]]

[[summaries/soil_frontier_genomics__REPORT]]

See also: [[summaries/essential_genome__REPORT]]

See also: [[summaries/field_vs_lab_fitness__REPORT]]

See also: [[summaries/fitness_effects_conservation__REPORT]]

See also: [[summaries/fitness_modules__REPORT]]

See also: [[summaries/lab_field_ecology__REPORT]]

See also: [[summaries/metabolic_capability_dependency__REPORT]]

See also: [[summaries/metal_cross_resistance__REPORT]]

See also: [[summaries/nmdc_community_metabolic_ecology__REPORT]]

See also: [[summaries/nmdc_context_audit__REPORT]]

See also: [[summaries/phage_defense_arsenal__REPORT]]

See also: [[summaries/phb_granule_ecology__REPORT]]

See also: [[summaries/prophage_ecology__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]