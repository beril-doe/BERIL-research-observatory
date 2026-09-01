---
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/essential_metabolome__REPORT.md", "summaries/enigma_carbon_census_1__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
type: "Method"
description: "Constraint-based method for predicting metabolic flux, growth, and gene necessity"
---

# Flux Balance Analysis

Also known as **FBA**.

## What it is

Flux Balance Analysis is a constraint-based method for estimating metabolic flux patterns and predicting growth from a metabolic model. In the ADP1 database, FBA generates metabolic flux classes and growth-phenotype predictions using ModelSEED-based metabolic models. [src: acinetobacter_adp1_explorer] [src: adp1_triple_essentiality]

FBA primarily evaluates whether a modeled metabolic network requires a gene or reaction for growth under specified environmental constraints. Its essentiality predictions therefore represent **metabolic necessity in silico**, rather than the full range of quantitative growth costs or experimental lethality. [src: adp1_triple_essentiality]

In the annotation-gap discovery study, FBA was used to evaluate draft RAST/ModelSEED metabolic models across 574 organism–carbon-source combinations and to identify false-negative growth predictions for conditional gapfilling. Baseline FBA achieved 42.5% overall accuracy, with recall of 86.5% (244 of 282 growth-positive conditions) and precision of 42.5% (244 of 574 predicted growth conditions). The low precision reflected 330 false-positive growth predictions from permissive draft models. [src: annotation_gap_discovery]

## Key facts from the ADP1 exploration

- FBA flux data covers 15% of the 5,852 genes in the database, making it the sparsest of the six integrated data modalities. [src: acinetobacter_adp1_explorer]
- FBA predictions and TnSeq essentiality calls were available for 866 genes; the two approaches were concordant for 639 genes (73.8%) and discordant for 227 genes. [src: acinetobacter_adp1_explorer]
- The 227 discordant genes are candidates for metabolic-model refinement and may reflect regulatory effects not captured by FBA. [src: acinetobacter_adp1_explorer]
- Of the 866 genes compared, 177 (20%) changed FBA flux class between rich and minimal media, indicating condition-dependent metabolic changes. [src: acinetobacter_adp1_explorer]
- Across 14 genomes, the database contains 1,330 unique metabolic reactions; 1,248 (94%) are shared across all genomes, 62 are variable, and 20 are genome-unique. [src: acinetobacter_adp1_explorer]
- Of 121,519 growth-phenotype predictions, 105,376 (87%) require at least one gapfilled reaction. Consequently, prediction accuracy is tightly coupled to [[concepts/metabolic-model-gapfilling|gapfilling]] quality. [src: acinetobacter_adp1_explorer]

## Findings from the ADP1 triple-essentiality analysis

- In experimental knockout comparisons, FBA showed moderate concordance with knockout essentiality: in rich medium, F1 = 0.624 and Cohen's κ = 0.486 across 724 genes; in minimal medium, F1 = 0.673 and κ = 0.493 across 833 genes. [src: adp1_triple_essentiality]
- FBA recall was 60.8% in rich medium and 65.6% in minimal medium, while precision was 64.0% and 69.2%, respectively. [src: adp1_triple_essentiality]
- FBA performed better against knockout essentiality in minimal medium than in rich medium, with F1 scores of 0.673 and 0.624, respectively. The report suggests that tighter metabolic constraints may make minimal-medium assumptions more compatible with FBA. [src: adp1_triple_essentiality]
- FBA class did not predict growth defects among 478 genes that were TnSeq-dispensable but also had mutant growth measurements. At the Q25 threshold, defect rates were 73.1% for FBA-essential genes, 73.5% for FBA-variable genes, and 69.4% for FBA-blocked genes (chi-squared = 0.93, p = 0.63). [src: adp1_triple_essentiality]
- The null association between FBA class and growth defects remained across Q10–Q35 thresholds; only Q40 produced a marginal association (p = 0.048). A threshold-independent Kruskal-Wallis test on continuous mean growth rates was also nonsignificant (H = 1.67, p = 0.43). [src: adp1_triple_essentiality]
- Condition-specific FBA flux showed weak and mixed correlations with mutant growth rates across six matched carbon sources. Spearman correlations ranged from -0.257 on asparagine (p < 0.001) to +0.246 on glucarate (p = 0.005), with the positive glucarate association running opposite to the expected direction. [src: adp1_triple_essentiality]
- These results distinguish FBA's ability to classify genes near the lethal/dispensable boundary from its inability to explain quantitative growth variation among genes that remain dispensable. [src: adp1_triple_essentiality]

## Model limitations and pathway-specific discordance

- Aromatic degradation genes were strongly enriched among FBA-discordant genes: 9 of 11 were discordant (odds ratio = 9.70, q = 0.012), and directional analysis found enrichment for FBA under-prediction (odds ratio = 12.0, q = 0.004). [src: adp1_triple_essentiality]
- Several discordant genes belong to the beta-ketoadipate pathway, including 4-carboxymuconolactone decarboxylase and beta-ketoadipate enol-lactone hydrolase. These genes were generally predicted as blocked even though their deletion was associated with growth defects. [src: adp1_triple_essentiality]
- The report hypothesizes that missing or unmodeled aromatic substrates in the FBA environmental definition may contribute to this under-prediction, potentially because experimental media contain trace aromatic compounds. This hypothesis requires testing with measured media composition and revised constraints. [src: adp1_triple_essentiality]
- Lipid-metabolism genes were depleted among discordant genes (odds ratio = 0.34, q = 0.042), suggesting that this portion of the model may be more accurately represented than aromatic catabolism. [src: adp1_triple_essentiality]
- Pangenome status did not explain the original discordance pattern: 93–100% of genes across concordance classes were core, with no significant enrichment among discordant genes (Fisher's exact test, odds ratio = 0.89, p = 0.80). [src: adp1_triple_essentiality]
- In the annotation-gap discovery study, conditional gapfilling for 38 false-negative cases added 219 reactions: 201 enzymatic, 14 transport, and 12 exchange reactions. [src: annotation_gap_discovery]
- Multiple valid gapfill solutions may exist for a given false-negative case. The study used default ModelSEED gapfilling, which minimizes the number of added reactions but does not guarantee biological optimality. [src: annotation_gap_discovery]
- Carbon-source mappings between Fitness Browser experiment names and ModelSEED exchange reactions were manually curated for 109 carbon sources, so mapping errors could generate spurious false negatives. [src: annotation_gap_discovery]
- Gene-knockout validation of 23 inserted GPR rules was inconclusive because the models required the gapfilled reactions themselves to enable growth on the tested carbon sources, making knockout analysis circular. [src: annotation_gap_discovery]
- The annotation-gap study's FBA analysis was based on 14 organisms, 12 of which were Proteobacteria; this phylogenetic bias limits generalization to divergent lineages. [src: annotation_gap_discovery]

### Aromatic-catabolism support-network blind spots

- In ADP1, FBA captured 1.76× higher predicted Complex I flux on aromatic substrates than on the comparison condition (0.55 versus 0.31), but predicted 0% essentiality for Complex I genes. This indicates that FBA can represent increased respiratory demand without capturing the bottleneck created by loss of a multi-subunit [[entities/complex-i|Complex I]]. [src: aromatic_catabolism_network]
- Thirty of 51 quinate-specific genes had no FBA reaction mappings. The unmapped functions included [[entities/pqq-biosynthesis|PQQ biosynthesis]], iron acquisition, transcriptional regulation, and putative Complex I accessory factors, demonstrating that cofactor supply chains and regulatory infrastructure can remain outside the model scope. [src: aromatic_catabolism_network]
- The 51-gene quinate-specific support network included 8 aromatic-pathway genes, 21 Complex I genes, 7 iron-acquisition genes, 2 PQQ-biosynthesis genes, 6 regulators, and 7 unassigned genes. [src: aromatic_catabolism_network]
- The model's failure to identify Complex I essentiality is consistent with a limitation of growth-optimization models: they can redistribute flux through alternatives, whereas disruption of one subunit can eliminate the function of the entire respiratory complex. [src: aromatic_catabolism_network]
- Cross-species ortholog-transferred data found worse Complex I fitness on aromatic conditions than on non-aromatic conditions (mean = -1.35 versus -0.77, Mann–Whitney p < 0.0001), but the largest relative defects occurred on acetate (-1.55) and succinate (-1.39). This supports the hypothesis that the dependency tracks high NADH flux rather than aromaticity specifically. [src: aromatic_catabolism_network]
- The ADP1 report proposes that [[entities/ndh-2|NDH-2]] may compensate for Complex I on simpler, lower-NADH substrates; this remains to be tested experimentally. [src: aromatic_catabolism_network]

## Relationships

This method is central to the metabolic-model analyses in [[summaries/acinetobacter_adp1_explorer__REPORT]]. Its predictions were compared with [[entities/random-barcode-transposon-sequencing|TnSeq]] essentiality data and connected to [[entities/modelseed|ModelSEED]] biochemical reaction identifiers. FBA is also part of the database's [[concepts/multi-omics-integration|multi-omics integration]] alongside [[entities/proteomics|proteomics]] and pangenome data. [src: acinetobacter_adp1_explorer]

The triple-essentiality analysis compared FBA with experimental knockout data, TnSeq fitness, and condition-specific mutant growth measurements in [[entities/acinetobacter-baylyi-adp1|*Acinetobacter baylyi* ADP1]]. It found moderate FBA–knockout agreement but no FBA association with growth defects within the TnSeq-dispensable subset, illustrating a broader [[concepts/method-concordance|method-concordance]] distinction between metabolic necessity, lethality, and fitness cost. [src: adp1_triple_essentiality]

The annotation-gap discovery study used FBA as the upstream model-based screen for integrating gapfilling with [[concepts/evidence-triangulation|evidence triangulation]], [[concepts/pangenome-integration|pangenome integration]], fitness data, GapMind, Bakta, and BLAST. The resulting pipeline resolved 96 of 201 gapfilled enzymatic reaction–organism pairs (47.8%), showing that FBA-derived gapfill requirements can provide targets for downstream gene annotation rather than serving only as growth predictions. [src: annotation_gap_discovery]

The aromatic-catabolism network study used FBA alongside [[concepts/cofitness-networks|co-fitness networks]] to compare modeled flux demand with gene-level growth phenotypes. Its results connect FBA to [[concepts/metabolic-support-networks|metabolic support networks]] and [[concepts/nadh-flux-respiratory-constraints|NADH-flux respiratory constraints]], while showing that the model omits important non-reaction-level dependencies. [src: aromatic_catabolism_network]

## Open analytical questions

- Test whether adding trace aromatic compounds to the minimal-medium definition reduces the under-prediction of beta-ketoadipate pathway genes. [src: adp1_triple_essentiality]
- Run condition-specific FBA matched to the eight experimental carbon sources and test whether continuous flux values predict mutant growth rates better than binary FBA classes. [src: adp1_triple_essentiality]
- Determine whether the 227 FBA–TnSeq discordances identified in the broader ADP1 exploration overlap with the aromatic-degradation discordance identified in the triple-essentiality study. [src: acinetobacter_adp1_explorer] [src: adp1_triple_essentiality]
- Evaluate whether combining FBA with continuous TnSeq fitness and proteomics improves essentiality prediction beyond any single data type. [src: adp1_triple_essentiality]
- Assess whether pangenome conservation can improve confidence in gapfilled reactions and distinguish network gaps from condition-specific or regulatory effects. [src: acinetobacter_adp1_explorer]
- Compare RAST/ModelSEED reconstructions with gapseq-based reconstructions to test whether improved initial model quality reduces false-positive growth predictions and produces more biologically targeted gapfill cases. [src: annotation_gap_discovery]
- Experimentally test high-confidence gene–reaction assignments generated from FBA gapfill cases, prioritizing reactions rxn02185 and rxn03436, which were each resolved with high confidence in 9 of 14 organisms. [src: annotation_gap_discovery]
- Re-run FBA and gapfilling across all 48 Fitness Browser organisms to test whether broader phylogenetic coverage improves pangenome-supported annotation and resolution of model gaps. [src: annotation_gap_discovery]
- Add PQQ biosynthesis, iron acquisition, and respiratory-chain capacity constraints to the ADP1 model and test whether the revised model predicts quinate-specific essentiality more accurately. [src: aromatic_catabolism_network]
- Search ADP1 for [[entities/ndh-2|NDH-2]] and compare its deletion phenotype on quinate, glucose, acetate, and succinate to test the high-NADH-flux hypothesis. [src: aromatic_catabolism_network]
- Test whether adding the 30 currently unmapped quinate-specific genes, or appropriate capacity constraints for their functions, improves prediction of condition-dependent essentiality. [src: aromatic_catabolism_network]

## Related Documents

- [[summaries/acinetobacter_adp1_explorer__REPORT]]
- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/enigma_carbon_census_1__REPORT]]

See also: [[summaries/essential_metabolome__REPORT]]

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]