---
sources: ["summaries/discoveries.md", "summaries/amr_fitness_cost__REPORT.md"]
type: "Method"
description: "A random-effects method used to pool AMR fitness effects across organisms"
---

## DerSimonian–Laird Random-Effects Meta-Analysis

The DerSimonian–Laird random-effects meta-analysis is a statistical method used in the [[summaries/amr_fitness_cost__REPORT]] to combine organism-specific estimates of the relative fitness cost associated with antimicrobial-resistance genes. [src: amr_fitness_cost]

## Use in the AMR Fitness-Cost Report

The analysis pooled effect sizes from 25 bacterial organisms with at least five AMR genes represented in Fitness Browser fitness matrices. [src: amr_fitness_cost] The pooled effect was **+0.086 [95% CI: +0.074, +0.098]**, with z = 14.3 and p approximately 0. [src: amr_fitness_cost] All 25 organisms showed a positive AMR-versus-background fitness shift, while the median organism-level Cohen’s d was 0.18. [src: amr_fitness_cost]

The meta-analysis also quantified between-organism variation: I² was 54.3%, and Cochran’s Q was 52.54 with p = 0.0007. [src: amr_fitness_cost] This heterogeneity indicates that the otherwise consistent AMR fitness-cost signal varies across organisms, connecting the method to [[concepts/organism-specificity]]. [src: amr_fitness_cost]

## Interpretation

The pooled estimate supports a small but consistent relative burden of AMR genes across the tested organisms. [src: amr_fitness_cost] In this analysis, the effect represents the difference between AMR-gene knockout fitness and the non-AMR knockout background, rather than an absolute selection coefficient measured in an isogenic resistant-versus-sensitive competition. [src: amr_fitness_cost] The report interprets this residual cost as potentially consistent with [[concepts/compensatory-evolution]], while noting that the organisms are lab-adapted and may have undergone prior compensation. [src: amr_fitness_cost]

## Related Methods and Data

The organism-level effect sizes were derived from genome-wide [[entities/random-barcode-transposon-sequencing]] measurements in the [[entities/fitness-browser]] compendium. [src: amr_fitness_cost] The use of a pooled estimate alongside organism-specific tests provides a basis for assessing cross-organism [[concepts/method-concordance]] while retaining evidence of organism-level heterogeneity. [src: amr_fitness_cost]

See also: [[summaries/discoveries]]