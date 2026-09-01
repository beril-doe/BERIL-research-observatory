---
type: "Summary"
description: "Pan-bacterial analysis finds AMR costs are universal, modest, and mechanism-independent"
doc_type: short
full_text: "sources/amr_fitness_cost__REPORT.md"
---

# Fitness Cost of Antimicrobial Resistance Genes

## Overview

This report presents a pan-bacterial analysis of antimicrobial-resistance (AMR) gene fitness costs using genome-wide [[entities/random-barcode-transposon-sequencing]] data from the [[entities/fitness-browser]] and pangenome annotations. It evaluates whether AMR genes impose a cost without antibiotics, whether they become beneficial under antibiotic exposure, and whether cost varies with resistance mechanism or core/accessory status. The study identifies 1,352 AMR genes across 43 organisms and analyzes non-antibiotic fitness data from 25 organisms. [src: amr_fitness_cost]

The central conclusion is that AMR genes impose a **small but highly consistent relative fitness burden**: AMR-gene knockouts are fitter than non-AMR knockouts under non-antibiotic conditions in all 25 tested organisms. This supports a framework in which resistance is costly but commonly retained because the cost is modest and may be reduced by [[concepts/compensatory-evolution]].

## Key Findings

### Universal relative fitness cost

A [[entities/der-simonian-laird-random-effects-meta-analysis]] found a pooled AMR-versus-background fitness shift of **+0.086 [95% CI: +0.074, +0.098]**, with z = 14.3 and p approximately 0. All 25 organisms showed a positive shift; the median per-organism Cohen’s d was 0.18. Heterogeneity was moderate, with I² = 54.3% and Cochran’s Q = 52.54, p = 0.0007. [src: amr_fitness_cost]

The effect is relative rather than an absolute growth benefit. AMR knockouts averaged −0.024 fitness, while the non-AMR knockout background averaged approximately −0.11. Thus, AMR genes are more dispensable than typical genes, but deleting them does not generally make cells grow faster than the wild type. [src: amr_fitness_cost]

Only 4.6% of AMR genes were absent from fitness matrices and therefore putatively essential, compared with an estimated background essential rate of approximately 14% from a different organism set. This lower essential fraction is consistent with AMR genes being relatively dispensable and argues against strong right-censoring bias. [src: amr_fitness_cost]

Tier 1 manually identified genes and the larger Tier 2 keyword-annotated set had indistinguishable fitness distributions, indicating that the Tier 2 expansion did not substantially dilute the signal. [src: amr_fitness_cost]

### Antibiotic-dependent importance

Under antibiotic exposure, 57.0% of AMR genes showed a fitness flip toward greater importance, with a mean flip of +0.045 and Wilcoxon signed-rank p = 0.0001 across 797 gene–antibiotic observations. This supports the broader idea of condition-dependent fitness and connects to [[concepts/condition-dependent-essentiality]]. [src: amr_fitness_cost]

The response depended on resistance mechanism. Broad-spectrum efflux genes showed a mean flip of +0.094, whereas enzymatic-inactivation genes showed −0.001; the difference was significant by Mann–Whitney U test, p = 0.007. The report interprets this as evidence that broad-spectrum efflux systems can become important under many antibiotics, while narrow-spectrum enzymes generally require exposure to a matching antibiotic. [src: amr_fitness_cost]

Class-matched validation produced a larger mean flip of +0.113 across 157 gene–antibiotic pairs, but it was not statistically significant by the Wilcoxon test (p = 0.14). Chloramphenicol-resistance genes showed the strongest validation, with 6/6 expected flips; beta-lactam genes showed a 50% flip rate across 105 pairs. [src: amr_fitness_cost]

### Baseline cost does not vary by mechanism

Fitness cost did not differ significantly among efflux, enzymatic inactivation, metal resistance, and unknown mechanisms. The Kruskal–Wallis test gave H = 0.65, p = 0.89, and the predicted ordering of efflux > enzymatic > metal > unknown was unsupported by the Jonckheere–Terpstra test (z = 0.23, p = 0.41). [src: amr_fitness_cost]

The report treats this uniformity as a meaningful result rather than evidence that resistance mechanisms are interchangeable. It suggests the hypothesis that the analyzed strains disproportionately retain AMR genes whose costs have already been reduced by [[concepts/compensatory-evolution]], leaving a similar residual overhead across mechanisms. This interpretation is limited by the use of lab-adapted strains. [src: amr_fitness_cost]

### Core and accessory genes have similar costs

Core/intrinsic AMR genes and accessory/acquired AMR genes had virtually identical fitness distributions: mean knockout fitness −0.024 in both groups, Cohen’s d = 0.002, and Mann–Whitney p = 0.33. This does not support the prediction that recently acquired accessory genes are systematically more costly. [src: amr_fitness_cost]

The result is qualified by uncertainty in core/accessory labels. Most species had few GTDB genomes available, with a median of 9 and a range of 2–399, so the ≥95% prevalence threshold is imprecise in poorly sampled species. The null result is considered more credible in well-sampled species such as *Klebsiella michiganensis*, *Bacteroides thetaiotaomicron*, and *Sinorhizobium meliloti*. [src: amr_fitness_cost]

This finding connects directly to [[concepts/core-accessory-resistance]] and illustrates the value and limitations of [[concepts/pangenome-integration]] for interpreting resistance-gene conservation. [src: amr_fitness_cost]

### Mechanism predicts genomic location, not cost

Resistance mechanism was strongly associated with conservation status (χ² = 69.3, p = 1.4×10⁻¹³). Metal-resistance genes were 44% accessory, compared with 13% for efflux genes and 16% for enzymatic-inactivation genes. The report therefore distinguishes the evolutionary processes determining **where** AMR genes occur in the pangenome from those determining their residual metabolic cost. This connects to [[concepts/core-accessory-resistance]] and [[concepts/pangenome-integration]]. [src: amr_fitness_cost]

## Data and Methods

The analysis combined:

- `kbase_ke_pangenome` tables for AMR identification and annotations.
- `kescience_fitnessbrowser` gene, experiment, and fitness tables.
- A cross-project Fitness Browser–pangenome bridge file.
- Cached fitness matrices from the fitness-modules project.

The assembled data included 6,804 classified experiments, 801 per-gene non-antibiotic fitness summaries, 954 antibiotic-validation measurements, 25 organism-level effect sizes, and stratification summaries. The main analytical methods were [[entities/random-barcode-transposon-sequencing]] fitness comparisons, Mann–Whitney tests, Kruskal–Wallis tests, Jonckheere–Terpstra tests, Wilcoxon signed-rank tests, chi-square tests, and [[entities/der-simonian-laird-random-effects-meta-analysis]]. These methods relate to [[concepts/method-concordance]] and the use of cross-condition fitness measurements. [src: amr_fitness_cost]

## Interpretation and Limitations

The results reconcile two observations: resistance costs are real enough to support resistance decline under antibiotic stewardship, but modest enough to permit persistence after antibiotic withdrawal. The report’s comparison with prior literature is supportive but not a direct equivalence because published studies often measure absolute fitness differences between isogenic resistant and susceptible strains, whereas this analysis measures relative differences between transposon knockouts.

Important limitations include lab-adaptation and compensatory-evolution bias, Tier 2 annotation noise, incomplete antibiotic-class matching, possible essential-gene censoring, relative rather than absolute fitness measurement, polar effects of transposon insertions, unclassified fosfomycin and tellurite resistance genes, and imprecise core/accessory labels in sparsely sampled species. The positive pooled effect may therefore underestimate costs in natural populations, while ecological contexts could make some resistance genes beneficial even without therapeutic antibiotics. These limitations also concern [[concepts/gene-essentiality]], [[concepts/organism-specificity]], and [[concepts/condition-dependent-essentiality]]. [src: amr_fitness_cost]

## Future Directions

1. Test mechanism effects within individual organisms with many AMR genes to reduce phylogenetic confounding.
2. Subclassify efflux systems into broad-spectrum RND pumps and narrower drug-specific pumps.
3. Measure costs separately across metal, osmotic, carbon-limitation, and other stress conditions.
4. Compare the 144 metal-resistance genes with the metal fitness atlas.
5. Extend the analysis from the 25 Fitness Browser organisms to the broader BERDL pangenome.

These analyses would test whether the apparent universal residual cost persists within genetic backgrounds, environments, and more representative natural populations. [src: amr_fitness_cost]

## Related Concepts
- [[concepts/annotation-gap]]
- [[concepts/environmental-resistome]]

## Entities
- [[entities/bakta]]
- [[entities/gtdb]]
- [[entities/berdl]]
- [[entities/amrfinderplus]]
- [[entities/kegg]]
- [[entities/modelseed]]
