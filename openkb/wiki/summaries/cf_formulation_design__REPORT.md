---
type: "Summary"
description: "Rational design of safe commensal consortia to suppress P. aeruginosa in CF airways"
doc_type: short
full_text: "sources/cf_formulation_design__REPORT.md"
---

# Rational Design of Protective Microbiome Formulations in CF Airways

## Overview

This report develops a multi-criterion strategy for suppressing chronic *Pseudomonas aeruginosa* infection in cystic fibrosis (CF) airways using rationally selected commensal communities. It integrates PROTECT isolate assays, patient metagenomics and metatranscriptomics, growth kinetics, pangenome pathway predictions, pairwise interaction data, and *P. aeruginosa* virulence and population analyses. The central design principle is [[concepts/metabolic-competitive-exclusion]]: commensals may suppress the pathogen by collectively consuming the amino acid carbon sources on which lung-adapted *P. aeruginosa* depends.

## Data and Study Design

The PROTECT collection contains 4,949 isolates from 175 patient samples, spanning 211 species and 23 structured tables totaling 30.5 million rows. The principal assays measured planktonic inhibition of PA14, utilization of 21 carbon sources, and growth kinetics. The core analysis included 142 isolates from 62 species; kinetic data were available for 32 isolates. Pangenome analyses covered 499 genomes across the five proposed formulation species and 6,760 *P. aeruginosa* genomes. [src: cf_formulation_design]

## Main Findings

### Metabolic overlap is real but incomplete as a suppression mechanism

PA14 preferentially uses amino acids, especially proline, histidine, ornithine, glutamate, aspartate, isoleucine, and arginine, while glucose supports only moderate growth. Metabolic overlap with PA14 significantly predicts inhibition across the 142-isolate cohort (r = 0.384, p = 2.3×10⁻⁶). A multivariate metabolic model explains R² = 0.274 of inhibition variance, but five-fold cross-validation gives CV R² = 0.145 ± 0.142, indicating limited out-of-sample predictive power. Adding genus raises training R² to 0.360, supporting a role for species- or genus-specific direct antagonism in addition to resource competition. [src: cf_formulation_design]

The report therefore supports a multi-mechanism pathogen-suppression model involving:

1. **Metabolic competition**, through depletion of PA14-preferred amino acids.
2. **Direct antagonism**, potentially involving bacteriocins, secreted enzymes, contact-dependent killing, or other taxon-specific mechanisms.
3. **Community-level niche saturation**, in which several organisms collectively cover the pathogen's resource niche even though no individual commensal outgrows PA14 on tested substrates.

Top positive residuals from the metabolic model include *Streptococcus salivarius*, *Gemella sanguinis*, and *Neisseria mucosa*, suggesting that these species combine metabolic overlap with additional inhibitory mechanisms. [src: cf_formulation_design]

### Growth kinetics favor pre-colonization rather than faster growth

Commensals exceed PA14's maximum growth rate on only 13.8% of substrate comparisons, but begin growing earlier than PA14 on 43.1% of comparisons. This suggests that pre-colonization or biomass pre-loading may be more useful than attempting to select organisms with superior intrinsic growth rates. Kinetic features are not redundant with endpoint growth measurements: adding them to the metabolic model increases training R² to 0.311 among the 29 isolates with all relevant assay types. [src: cf_formulation_design]

### Engraftability identifies respiratory anchors

Patient metagenomic and metatranscriptomic data identified *N. mucosa* as the strongest candidate for airway persistence, with an engraftability score of 1.595. *Rothia dentocariosa* (0.422) and *S. salivarius* (0.172) also exceeded the median among inhibition-tested species. However, engraftability is inferred from prevalence and transcriptional activity rather than directly measured following administration. [src: cf_formulation_design]

## Proposed Formulations

A strict safety filter excluded well-known pathogens and additionally removed *Pseudomonas*, Enterobacteriaceae, and *Staphylococcus*. The resulting formulation core consists of:

- *Neisseria mucosa* — strongest engraftability and 88% best inhibition.
- *Streptococcus salivarius* — up to 98% inhibition and a candidate direct-antagonism backbone.
- *Micrococcus luteus* — broad metabolic coverage and the species that completes PA14 niche coverage.
- *Rothia dentocariosa* — strong inhibition, respiratory association, and possible secreted-antagonism activity.
- *Gemella sanguinis* — strong inhibition and positive residuals, but the smallest pangenome and therefore the greatest strain-selection uncertainty.

The strict-safe rankings identify the following candidates:

| Size | Formulation | PA14 niche coverage | Mean inhibition | Engraftability |
|---|---|---:|---:|---:|
| k=1 | *N. mucosa* | 18% | 88% | 1.595 |
| k=2 | *R. dentocariosa* + *N. mucosa* | 18% | 84% | 0.820 |
| k=3 | *M. luteus* + *N. mucosa* + *S. salivarius* | 100% | 75% | 0.140 |
| k=4 | *R. dentocariosa* + *M. luteus* + *N. mucosa* + *S. salivarius* | 100% | 76% | 0.185 |
| k=5 | *R. dentocariosa* + *M. luteus* + *G. sanguinis* + *N. mucosa* + *S. salivarius* | 100% | 78% | 0.188 |

Exhaustive enumeration of 127,598 valid k=3 formulations confirmed the *M. luteus* + *N. mucosa* + *S. salivarius* triple as the global optimum under the scoring scheme. Bootstrap confidence intervals for k=2 through k=5 overlapped, so formulation sizes were not statistically distinguishable on composite score. [src: cf_formulation_design]

The report recommends the lung-adapted k=2 pair as the primary clinical candidate because it combines 84% mean inhibition with much higher inferred engraftability. The k=3 formulation is an aspirational candidate because *M. luteus* raises niche coverage to 100% but has zero patient detection and zero lung genomes, creating an [[concepts/organism-specificity]] tradeoff between metabolic coverage and airway persistence. [src: cf_formulation_design]

## Prebiotic Strategy

No tested amino acid or simple sugar favored commensals over PA14: PA14 outgrew the average commensal on every tested substrate. This rules out a straightforward amino-acid prebiotic strategy and supports [[concepts/selective-prebiotics]].

Genomic pathway comparisons instead identified six candidate substrates that are complete in at least one formulation species but absent or nearly absent in PA14:

- Myoinositol
- Xylitol
- Xylose
- Arabinose
- Fucose
- Rhamnose

Xylitol is predicted to feed *S. salivarius* and *G. sanguinis*, while xylose, arabinose, fucose, and rhamnose are predicted to benefit *N. mucosa* and *G. sanguinis*. The report proposes a multi-prebiotic strategy targeting different consortium members rather than a single universal substrate. These predictions require experimental validation because pathway completeness does not establish growth under CF airway conditions. [src: cf_formulation_design]

## Pangenome and Airway Adaptation Evidence

The metabolic traits used for formulation design are generally conserved at the species level. Across 499 genomes, *M. luteus* retained 18/18 amino acid pathways and 39/39 carbon pathways at greater than 95% conservation; *S. salivarius* retained 18/18 and 32/35; *N. mucosa* retained 16/16 and 27/27; *R. dentocariosa* retained 14/18 and 39/41; and *G. sanguinis* retained 7/18 and 37/39. *G. sanguinis* therefore has the greatest amino acid pathway variability and the strongest need for strain-level characterization. These results exemplify [[concepts/pangenome-integration]] for evaluating translational robustness. [src: cf_formulation_design]

Respiratory metadata support *R. dentocariosa* and *N. mucosa* as natural airway-associated anchors: they account for 10 of 29 and 5 of 15 species genomes from respiratory sources, respectively. *M. luteus* has no lung genomes and is primarily skin- or environment-associated, creating a central tension between metabolic coverage and engraftability. [src: cf_formulation_design]

## Interaction Evidence and Limitations

Pairwise competition data show mildly antagonistic interactions overall, with mean synergy of −5.8%. *N. mucosa* combinations were near-additive (+5.3% and −2.2%), whereas some other pairs showed stronger antagonism, including −19.8%. The dataset contains only 8 comparisons across 5 unique pairs, so the additive formulation-scoring assumption remains provisional. The complete 10-pair matrix for the five-species core is the highest-priority validation experiment. [src: cf_formulation_design]

A data-integrity issue prevents interpretation of per-substrate co-culture effects: the `fact_pairwise_interaction` table is identical to the carbon-utilization table, with correlation = 1.0 and mean difference = 0.0. Current interaction conclusions therefore rely on the RFU-based competition assay rather than endpoint OD co-culture data. This is an instance of the broader [[concepts/annotation-gap]] and data-quality limitations affecting interpretation of integrated datasets. [src: cf_formulation_design]

## Relevance of PA14 and Robustness Across *P. aeruginosa* Diversity

PA14 is not representative of most CF *P. aeruginosa*: 94% of CF genomes were ExoS+ and 5% ExoU+, whereas PA14 is ExoU+ and Pel-only. Most genomes (96.4%) carry both Pel and Psl biofilm operons, making the PA14 phenotype uncommon. Nevertheless, amino acid catabolic pathways are effectively invariant between ExoU+ and ExoS+ variants, and are 97.4% conserved across 1,796 lung-associated PA genomes. CF versus non-CF lung PA showed zero amino acid pathway differences. [src: cf_formulation_design]

These results support the hypothesis that the formulation's metabolic targets should apply broadly across PA variants, while emphasizing that inhibition must be confirmed against PAO1 and mucoid clinical isolates. Biofilm structure, virulence, antibiotic resistance, and spatial refuge may still produce strain-specific clinical outcomes. [src: cf_formulation_design]

Lung-associated PA also shows metabolic streamlining, with reduced sorbitol, mannitol, and gluconate pathways relative to non-lung isolates. Acute exacerbation samples show broad pathway downregulation, including amino acid biosynthesis, potentially increasing dependence on host-derived nutrients; this remains a hypothesis about increased susceptibility rather than a demonstrated therapeutic effect. [src: cf_formulation_design]

## Priority Experiments

1. Complete the 10-pair interaction matrix for the five core species.
2. Test xylitol, myoinositol, xylose, arabinose, fucose, and rhamnose experimentally with the formulation species and PA14.
3. Evaluate planktonic-to-biofilm translation in CF bronchial epithelial culture models.
4. Identify genomic determinants of direct antagonism in the strongest inhibitory isolates.
5. Compare k=2, k=3, and k=5 formulations, with and without prebiotics, in a chronic PA14 mouse model.
6. Repeat assays against PAO1 and 3–5 mucoid clinical PA isolates.
7. Expand metabolic testing to mucin components, polyamines, iron limitation, and CF-relevant pH.

## Overall Assessment

The report establishes a quantitative basis for [[concepts/rational-microbiome-formulation-design]] against CF airway pathogens. Its strongest translational conclusion is not that metabolic overlap alone predicts clinical protection, but that effective formulations should combine conserved resource competition, direct antagonism, airway compatibility, and experimentally validated community interactions. The k=2 *R. dentocariosa*–*N. mucosa* pair is the most practical near-term candidate, while the k=3 and k=5 communities offer greater niche coverage subject to resolving the *M. luteus* engraftment problem and confirming interactions in biofilm and animal models. [src: cf_formulation_design]

## Related Concepts
- [[concepts/evidence-triangulation]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/method-concordance]]
- [[concepts/phylogenetic-confounding]]

## Entities
- [[entities/kegg]]
- [[entities/average-nucleotide-identity]]
- [[entities/bakta]]
- [[entities/eggnog]]
- [[entities/random-barcode-transposon-sequencing]]
