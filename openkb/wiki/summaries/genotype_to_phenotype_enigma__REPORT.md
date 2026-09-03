---
type: "Summary"
description: "ENIGMA study defines what genome content can predict about bacterial phenotypes"
doc_type: short
full_text: "sources/genotype_to_phenotype_enigma__REPORT.md"
---

# Genotype-to-phenotype prediction from ENIGMA growth curves

## Overview

This project integrates ENIGMA growth curves, genome annotations, Fitness Browser fitness data, Web of Microbes exometabolomics, Carbon Source Phenotypes, and global environmental datasets to test how well bacterial phenotypes can be predicted from genome content and growth condition. The central result is that [[concepts/phenotype-resolution-matching]] works substantially better for binary substrate utilization than for continuous growth kinetics. [src: genotype_to_phenotype_enigma]

The study combines 46,389 genome-by-condition training pairs from 727 genomes and evaluates models with genus-blocked holdouts across 106 genera. It also connects model interpretation to ecological niche structure, fitness data, metabolite associations, and active experimental design. [src: genotype_to_phenotype_enigma]

## Main findings

### Binary growth is condition-dependent and partly predictable

Binary growth prediction from KO presence/absence performs best for amino acids (AUC 0.775) and nucleosides (AUC 0.780), is moderate for carbon sources (AUC 0.695), and is weak for antibiotics (0.619), metals (0.605), and nitrogen sources (0.435). Across 343 individually tested conditions, 95 achieve AUC greater than 0.75; tryptophan is the best-predicted substrate with AUC 0.933. [src: genotype_to_phenotype_enigma]

KO-by-condition interaction features improve overall AUC from 0.620 to 0.653, indicating that explicitly representing whether a genome contains functions relevant to a tested substrate adds predictive value. [src: genotype_to_phenotype_enigma]

The strongest full-corpus features are condition-specific functions, including the proline/betaine transporter K03762, ribose transporter K10440, protocatechuate cycloisomerase K01857, AraC-family regulator K13633, and isoamylase K01214. Their importance is consistent with a [[concepts/pathway-completeness]] interpretation: transport and catabolic functions help predict whether an organism can use a substrate. [src: genotype_to_phenotype_enigma]

### Continuous kinetics remain poorly predictable

Maximum growth rate, lag time, and yield show negative cross-genus R² in both KO-based and bulk-genomic regression models. Weak correlations between genome size or KO count and growth rate disappear under cross-genus holdout, suggesting that gene presence primarily encodes metabolic capability rather than kinetic performance. [src: genotype_to_phenotype_enigma]

The report attributes this limitation to unmeasured enzyme kinetics, expression and regulatory state, ribosome efficiency, and codon usage bias. Codon usage features and expression data are proposed as necessary additions for future continuous-rate prediction. [src: genotype_to_phenotype_enigma]

### Training scale determines interpretability

With only seven anchor strains, the model is dominated by condition class and a 63-feature genome-scale axis, effectively learning that larger genomes tend to grow on more substrates. With 46,000-plus training pairs, condition-specific catabolic genes emerge as predictors. This supports the [[concepts/sample-size-aware-modeling]] hypothesis that mechanistic resolution requires broad genome-by-condition coverage, not merely more features on a small strain set. [src: genotype_to_phenotype_enigma]

### Model features are mechanistically coherent but weakly concordant with fitness data

The top SHAP features include biologically plausible transporters, catabolic enzymes, and regulators. However, condition-matched comparison with [[entities/fitness-browser]] identifies only 18.7% significant fitness effects among SHAP-selected loci versus a 16.3% random baseline, or 1.19× enrichment. [src: genotype_to_phenotype_enigma]

This weak concordance reflects different biological questions: cross-genus gene presence asks whether a genome can support growth, whereas RB-TnSeq asks whether disrupting a gene affects fitness within one strain. Functional redundancy, condition differences, and correlated gene blocks can separate these signals. [src: genotype_to_phenotype_enigma]

### Small-sample exometabolomics requires a different method

For six [[entities/web-of-microbes]] strains and 105 metabolites, multivariate GBDT prediction fails at AUC 0.500. Univariate point-biserial correlations instead identify 940 strong KO-metabolite associations across all 62 variable metabolites: 454 production associations and 486 consumption associations. [src: genotype_to_phenotype_enigma]

The analysis used 156 Fitness Browser-cognate KOs as a focused feature set. Examples include PAPS synthase associated with taurine production, thymidine phosphorylase with thymine production, lactate permease with lactate consumption, and xanthine oxidase with hypoxanthine consumption. Growth-predictive KOs and metabolite-associated KOs have very different feature profiles (Spearman rho = 0.043), reinforcing the [[concepts/sample-size-aware-modeling]] principle. [src: genotype_to_phenotype_enigma]

### Ecological niches show a global pH gradient

Oak Ridge co-occurrence data reveal two opposing genus clusters. A Brevundimonas-Caulobacter-Sphingomonas cluster is associated with more neutral, cooler environments, while a Rhodanobacter-Ralstonia-Dyella cluster occupies environments averaging pH 5.43 and 22.6°C, compared with pH 6.78 and 15.7°C for the first cluster. [src: genotype_to_phenotype_enigma]

The 1.35-unit pH difference across 464,000 global 16S samples suggests that the local Oak Ridge contamination-gradient pattern reflects a broader [[concepts/subsurface-microbial-specialization]] axis rather than a site-specific interaction. The result is correlational and does not establish direct microbial interaction or causation. [src: genotype_to_phenotype_enigma]

## Data integration and quality lessons

The project established a 486-pair anchor set linking growth curves, genome annotations, and Fitness Browser data across seven strains and 72 conditions. Five conditions occur in all four major phenotype datasets: cytidine, glycine, inosine, thymidine, and uridine. [src: genotype_to_phenotype_enigma]

Growth-curve analysis covered 27,632 wells. Of these, 15,227 (55.1%) showed no detectable growth and 9,861 (35.7%) produced fit-ok curves with median Gompertz R² of 0.98. Among fit-ok curves, the median maximum growth rate was 0.028 h⁻¹, lag was 11.4 h, and asymptotic OD increase was 0.315. [src: genotype_to_phenotype_enigma]

KO profiling identified eight metabolic guilds among 123 strains and 7,167 unique KOs. Guilds broadly align with taxonomy but are defined by functional gene content. [src: genotype_to_phenotype_enigma]

A major integration pitfall involved short strain-name collisions: matching ENIGMA strains to pangenome records by identifier produced 12 of 32 genus-level mismatches and introduced 1,751 spurious clinical genomes into environmental profiles. Authoritative GTDB-Tk taxonomy reduced verified linkages from 32 to 20 and eliminated the false matches. This is a reusable [[concepts/pangenome-integration]] and [[concepts/evidence-triangulation]] lesson for environmental microbiology data integration. [src: genotype_to_phenotype_enigma]

## Active learning and experimental priorities

An active-learning score combining prediction error, uncertainty, and Oak Ridge field relevance identified 50 proposed experiments. The highest-priority conditions include fumaric acid, melibionic acid, fumarate, itaconic acid, lactic acid, nitrate, and pyruvic acid. These choices emphasize organic acids, nitrogen cycling, low-pH-compatible substrates, and aromatic metabolism, where current prediction is weakest or field relevance is highest. [src: genotype_to_phenotype_enigma]

Prescottella and Microbacterium are prioritized as test genera because their current growth predictions are relatively unreliable, with observed growth rates of 16% and 23% across tested conditions, respectively. The proposal is actionable but has not yet been formally validated against random experimental selection; retrospective subsampling is the next test. [src: genotype_to_phenotype_enigma]

## Limitations and next steps

Key limitations include string-based condition matching, incomplete growth-curve fitting, genus-level rather than species-level biogeography, unresolved geochemistry-to-location links, and the inability to compute codon usage bias from nucleotide sequences in the current environment. [src: genotype_to_phenotype_enigma]

Priority follow-up work includes ChEBI-based condition canonicalization, codon-usage analysis for continuous growth prediction, linkage of Oak Ridge wells to uranium/nitrate/metal measurements, SparCC analysis of compositional co-occurrence, retrospective validation of active-learning rankings, and pathway-level expansion of Fitness Browser concordance tests. [src: genotype_to_phenotype_enigma]

## Overall contribution

The report establishes a practical boundary for [[concepts/capability-versus-kinetics]]: genome content can predict many binary metabolic capabilities when sufficient cross-genus training data are available, but it does not by itself predict growth kinetics. It also demonstrates that interpretation, validation, and experimental design must be matched to biological resolution, sample size, and the distinction between capability, fitness, and metabolite production. [src: genotype_to_phenotype_enigma]

## Related Concepts
- [[concepts/condition-dependent-essentiality]]
- [[concepts/cultivation-bias]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/gene-co-inheritance]]
- [[concepts/prevalence-ceiling]]
- [[concepts/shared-dispensability]]
- [[concepts/redox-zonation]]
