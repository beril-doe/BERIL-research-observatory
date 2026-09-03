---
type: "Summary"
description: "Integrates FBA, knockout, RB-TnSeq, growth, and proteomics evidence for ADP1 essentiality."
doc_type: short
full_text: "sources/adp1_triple_essentiality__REPORT.md"
---

# Triple Essentiality Concordance Analysis for *Acinetobacter baylyi* ADP1

## Summary

This report integrates computational flux balance analysis (FBA), experimental knockout phenotypes, RB-TnSeq, mutant growth assays, and proteomics to examine [[concepts/gene-essentiality]] in *Acinetobacter baylyi* ADP1. It combines an original analysis of 478 TnSeq-dispensable genes with a refined, genome-wide comparison of 5,852 genes.

The central conclusion is that the methods measure different forms of gene importance rather than a single universal essentiality state. Knockouts measure lethality, FBA measures predicted metabolic necessity, TnSeq and growth assays measure fitness costs, and proteomics reflects expression requirements. Consequently, method concordance depends strongly on the biological endpoint being evaluated.

## Major Findings

- FBA did not predict growth defects among TnSeq-dispensable genes. Across 478 triple-covered genes, growth-defect rates were 73.1% for FBA-essential genes, 73.5% for FBA-variable genes, and 69.4% for FBA-blocked genes; the association was not significant (chi-squared = 0.93, p = 0.63). The result remained nonsignificant from Q10 through Q35 growth-defect thresholds.
- FBA showed moderate agreement with experimental knockout essentiality when evaluated across all available genes: F1 = 0.624 and κ = 0.486 in rich medium, versus F1 = 0.673 and κ = 0.493 in minimal medium. Recall was 60.8% in rich medium and 65.6% in minimal medium.
- RB-TnSeq binary classifications disagreed systematically with knockout results. At the 0.05 essentiality-fraction threshold, recall was 7.9%, precision was 5.8%, F1 was 0.067, and Cohen's κ was -0.081. All tested thresholds from 0.01 to 0.20 produced negative κ values.
- Continuous fitness was substantially more informative than binary essentiality fraction for predicting knockout essentiality. Fitness produced AUC values of 0.700 in rich medium and 0.725 in minimal medium, whereas essentiality fraction produced AUC values of 0.344 and 0.403, respectively.
- Proteomics was the strongest reported continuous predictor in minimal medium. Essential genes had mean log2 expression of 28.43 versus 25.73 for dispensable genes, corresponding to a 6.5-fold expression difference; AUC = 0.743, Pearson r = 0.345, and Mann-Whitney p = 9.91×10⁻⁵⁹.
- Growth effects were condition-dependent: 333 of 478 genes (70%) showed defects on some but not all of eight carbon sources, while only 10 genes (2%) were defective across all eight. Mean pairwise defect correlation was 0.38.

## Model and Method Discordance

The report frames [[concepts/method-concordance]] as a distinction between lethality, metabolic necessity, fitness cost, expression requirement, and condition-specific optimization. Complete deletion can eliminate all gene function, whereas a transposon insertion may permit truncated protein production, transcriptional read-through, or residual domain activity. This may explain why 211 knockout-essential genes were TnSeq-dispensable, while 293 knockout-dispensable genes were TnSeq-essential and therefore fitness-important without being lethal.

FBA was useful near the lethal/dispensable boundary but did not explain quantitative growth variation among dispensable genes. The report suggests that binary FBA essentiality is not an adequate proxy for continuous growth effects and recommends condition-matched simulations using continuous flux values.

## Aromatic Catabolism as a Model Gap

Aromatic degradation genes were strongly enriched among FBA-discordant genes: 9 of 11 were discordant (OR = 9.70, q = 0.012), with directional enrichment for FBA under-prediction (OR = 12.0, q = 0.004). Genes in the beta-ketoadipate pathway, including 4-carboxymuconolactone decarboxylase and beta-ketoadipate enol-lactone hydrolase, were generally predicted to be blocked despite deletion-associated growth defects.

This pattern is presented as evidence for [[concepts/metabolic-model-gapfilling]], particularly a mismatch between FBA media assumptions and experimental environments that may contain trace aromatic compounds. In contrast, lipid-metabolism genes were depleted among discordant genes (OR = 0.34, q = 0.042), suggesting better representation of those pathways in the model.

## Implications

The report recommends using knockout data as the reference for lethality, FBA as a first-pass metabolic screen, continuous TnSeq fitness rather than essentiality fraction, and proteomics as supporting evidence. For dispensable genes, specific growth assays are needed because FBA class does not predict growth-rate variation. A combined predictor integrating FBA, fitness, and proteomics is proposed as a potential direction for [[concepts/multi-omics-integration]].

Priority follow-up work includes analyzing transposon insertion position in the 211 knockout-essential/TnSeq-dispensable genes, matching TnSeq and knockout conditions, adding trace aromatic substrates to FBA media definitions, testing condition-specific FBA, and extending the comparison to other *Acinetobacter* species.

## Data and Provenance

The refined analysis used essentiality vectors covering 5,852 genes, knockout data from rich and minimal media, FBA classifications for 866 genes per medium, RB-TnSeq fitness and essentiality fractions, and proteomics measurements for 2,383 genes across seven *Acinetobacter* strains. The original study used mutant growth rates on glucose, acetate, asparagine, butanediol, glucarate, lactate, pyruvate, and succinate. Analysis outputs include concordance summaries, ROC summaries, proteomics statistics, and lists of 211 and 293 discordant genes.

[source: adp1_triple_essentiality]

## Related Concepts
- [[concepts/condition-dependent-essentiality]]
- [[concepts/phenotypic-landscape]]
- [[concepts/pangenome-integration]]

## Entities
- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/berdl]]
- [[entities/fitness-browser]]
- [[entities/flux-balance-analysis]]
- [[entities/modelseed]]
- [[entities/proteomics]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/quinate-aromatic-degradation]]
- [[entities/pqq-biosynthesis]]
- [[entities/urease-complex]]
