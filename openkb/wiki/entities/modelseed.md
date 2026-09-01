---
sources: ["summaries/respiratory_chain_wiring__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/pitfalls.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/nmdc_community_metabolic_ecology__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/harvard_forest_warming__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/essential_metabolome__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/clay_confined_subsurface__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
type: "Dataset"
description: "Biochemical reference collection used for metabolic modeling and gapfilling"
---

# ModelSEED

## Overview

ModelSEED is a biochemical reference collection used for reaction and compound name resolution, metabolic-model reconstruction, flux-balance analysis, and gapfilling. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality, annotation_gap_discovery] The annotation-gap discovery study used ModelSEED biochemistry reaction and reagent tables to interpret gapfilled reaction definitions and stoichiometry across multiple organisms. [src: annotation_gap_discovery]

## Relevance to the ADP1 database

The ADP1 database contains 1,330 unique metabolic reactions, of which 1,210 (91%) matched entries in the ModelSEED biochemistry collection. [src: acinetobacter_adp1_explorer] The database also contains 230 compounds, all of which matched ModelSEED biochemistry entries. [src: acinetobacter_adp1_explorer]

The 120 unmatched reactions may represent custom or draft reactions that are not yet included in ModelSEED. [src: acinetobacter_adp1_explorer] This incomplete reaction correspondence is relevant to [[concepts/metabolic-model-gapfilling]], because ADP1 growth predictions depend heavily on reactions added through gapfilling. [src: acinetobacter_adp1_explorer]

ModelSEED-derived FBA classifications were available for 866 genes in rich medium and 866 genes in minimal medium. [src: adp1_triple_essentiality] Compared with experimental knockout essentiality, these predictions showed moderate concordance: in rich medium, recall was 60.8%, precision was 64.0%, F1 was 0.624, and Cohen's kappa was 0.486; in minimal medium, recall was 65.6%, precision was 69.2%, F1 was 0.673, and Cohen's kappa was 0.493. [src: adp1_triple_essentiality] FBA performance was therefore better in minimal medium than in rich medium, although the report characterizes it as a screening method requiring experimental validation. [src: adp1_triple_essentiality]

Within 478 genes classified as TnSeq-dispensable, ModelSEED FBA class was not associated with measured growth defects (chi-squared = 0.93, p = 0.63; Kruskal-Wallis H = 1.67, p = 0.43). [src: adp1_triple_essentiality] Thus, ModelSEED-based binary FBA predictions distinguish some knockout-essential genes from dispensable genes but do not predict quantitative growth variation among TnSeq-dispensable genes. [src: adp1_triple_essentiality]

Aromatic degradation genes were a major source of FBA discordance: 9 of 11 such genes were discordant, with odds ratio = 9.70 and BH-adjusted q = 0.012. [src: adp1_triple_essentiality] Most were FBA-under-predicted, being assigned zero flux despite deletion-associated growth defects; directional enrichment had odds ratio = 12.0 and q = 0.004. [src: adp1_triple_essentiality] The report identifies the beta-ketoadipate pathway, including 4-carboxymuconolactone decarboxylase and beta-ketoadipate enol-lactone hydrolase, as an example of this limitation. [src: adp1_triple_essentiality] These results connect ModelSEED-based modeling to [[concepts/metabolic-model-gapfilling]] and [[entities/quinate-aromatic-degradation]], because environmental assumptions about aromatic substrates may not match the experimental media. [src: adp1_triple_essentiality]

## Relevance to annotation-gap discovery

The annotation-gap discovery study selected 14 organisms and used draft models built from ModelSEED/RAST annotations for baseline FBA and conditional gapfilling across 574 organism–carbon-source combinations. [src: annotation_gap_discovery] Baseline FBA achieved 42.5% overall accuracy, with recall of 86.5% (244 of 282 growth-positive conditions correctly predicted) and precision of 42.5% (244 of 574 growth predictions correct); the low precision reflected 330 false-positive growth predictions from permissive draft models. [src: annotation_gap_discovery]

Conditional gapfilling of 38 false-negative cases added 219 reactions: 201 enzymatic, 14 transport, and 12 exchange reactions, averaging 5.8 reactions per case. [src: annotation_gap_discovery] Of the 201 gapfilled enzymatic reaction–organism pairs, 50 (24.9%) were dark reactions with no EC number assigned by ModelSEED. [src: annotation_gap_discovery]

Only 8 of the 50 dark reactions (16%) were resolved to candidate genes, compared with 88 of 151 reactions with known EC numbers (58.3%). [src: annotation_gap_discovery] This result indicates that ModelSEED reactions lacking EC classifications are especially difficult inputs for downstream sequence-homology and functional-annotation searches, and links ModelSEED to [[concepts/annotation-gap]] and [[concepts/evidence-triangulation]]. [src: annotation_gap_discovery]

Across all evidence streams, 96 of 201 gapfilled enzymatic pairs (47.8%) received candidate genes with confidence scoring: 44 high-confidence pairs (21.9%), 19 medium-confidence pairs (9.5%), and 33 low-confidence pairs (16.4%); 105 pairs (52.2%) remained unresolved. [src: annotation_gap_discovery] The pipeline combined ModelSEED gapfilling with Fitness Browser fitness data, pangenome conservation, GapMind pathway evidence, Bakta annotations, and DIAMOND BLAST homology. [src: annotation_gap_discovery]

The study found that no single evidence stream exceeded 35% resolution: BLAST alone resolved 70 pairs (34.8%), EC matching alone resolved 51 (25.4%), and Bakta alone resolved 22 (10.9%), whereas the full pipeline resolved 96 (47.8%). [src: annotation_gap_discovery] Removing individual streams left 73–86 resolved pairs, supporting the complementarity of the integrated approach. [src: annotation_gap_discovery]

## Related resources

- [[entities/berdl]] — the data lakehouse queried for biochemical and comparative-genomics connections. [src: acinetobacter_adp1_explorer]
- [[entities/flux-balance-analysis]] — the modeling approach used for ModelSEED-based ADP1 metabolic flux predictions and for evaluating draft models in the annotation-gap study. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality, annotation_gap_discovery]
- [[entities/acinetobacter-baylyi-adp1]] — the organism whose metabolic reactions, gene essentiality, and growth phenotypes were analyzed. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality]
- [[entities/fitness-browser]] — the source of carbon-source fitness experiments used alongside ModelSEED gapfilling in the annotation-gap study. [src: annotation_gap_discovery]
- [[entities/gapmind]] — the pathway-level annotation resource used to assess concordance with ModelSEED gapfilling. [src: annotation_gap_discovery]
- [[entities/bakta]] — the alternative annotation source used to supplement ModelSEED EC assignments, especially for dark reactions. [src: annotation_gap_discovery]
- [[entities/diamond]] — the sequence-homology method used to triangulate candidate genes for ModelSEED gapfilled reactions. [src: annotation_gap_discovery]
- [[concepts/metabolic-model-gapfilling]] — the cross-document topic concerning missing reactions and model-completion assumptions. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality, annotation_gap_discovery]
- [[concepts/annotation-gap]] — the topic concerning unresolved links between metabolic reactions and candidate genes. [src: annotation_gap_discovery]
- [[concepts/evidence-triangulation]] — the topic concerning integration of independent evidence streams for annotation. [src: annotation_gap_discovery]
- [[summaries/acinetobacter_adp1_explorer__REPORT]] — source report describing the ModelSEED connection scan. [src: acinetobacter_adp1_explorer]
- [[summaries/adp1_triple_essentiality__REPORT]] — source report evaluating ModelSEED-based FBA predictions against knockout and growth measurements. [src: adp1_triple_essentiality]
- [[summaries/annotation_gap_discovery__REPORT]] — source report integrating ModelSEED gapfilling with fitness, pangenome, pathway, annotation, and homology evidence. [src: annotation_gap_discovery]

## Open integration question

Resolving the 120 unmatched ADP1 reactions and determining whether they are custom, draft, or genuinely absent biochemical functions could improve interpretation of the ADP1 metabolic model and its gapfilled growth predictions. [src: acinetobacter_adp1_explorer] A specific follow-up is to add trace aromatic compounds or otherwise match FBA environmental constraints to the experimental media, then test whether discordance of beta-ketoadipate pathway genes decreases. [src: adp1_triple_essentiality]

For the broader ModelSEED-based annotation workflow, the 105 unresolved reaction–organism pairs and 50 EC-less dark reactions are concrete targets for improved reaction classification, alternative enzyme-prediction methods, and experimental enzyme characterization. [src: annotation_gap_discovery] Comparing ModelSEED/RAST draft models with models reconstructed using gapseq could also test whether improved initial model quality reduces false-positive FBA predictions and changes the set of reactions selected by gapfilling. [src: annotation_gap_discovery]

See also: [[summaries/amr_fitness_cost__REPORT]]

See also: [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/clay_confined_subsurface__REPORT]]

See also: [[summaries/essential_genome__REPORT]]

See also: [[summaries/essential_metabolome__REPORT]]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/harvard_forest_warming__REPORT]]

See also: [[summaries/lanthanide_methylotrophy_atlas__REPORT]]

See also: [[summaries/metabolic_capability_dependency__REPORT]]

See also: [[summaries/nmdc_community_metabolic_ecology__REPORT]]

See also: [[summaries/pgp_pangenome_ecology__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]