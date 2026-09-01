---
type: "Concept"
sources: ["summaries/microbeatlas_metal_ecology__REPORT.md"]
description: "Metal-type diversity links bacterial ecological breadth beyond phylogeny."
---

# Metal-Resistance Breadth as an Ecological Trait

## Overview

Metal-resistance breadth is the diversity of metal types represented in a bacterial lineage’s resistance repertoire, rather than the total number of resistance genes or clusters. In the [[summaries/microbeatlas_metal_ecology__REPORT]] study, it was measured as the number of distinct metal categories resisted per genus from AMRFinderPlus pangenome annotations, covering mercury, arsenic, copper, zinc, cadmium, chromium, and nickel. [src: microbeatlas_metal_ecology]

The concept treats resistance breadth as a potentially informative ecological trait: genera with resistance mechanisms spanning more metal types were associated with broader inferred ecological niches in a global microbiome atlas. This association is relevant to [[concepts/environmental-metal-tolerance]], [[concepts/ecological-generalism]], and [[concepts/metal-resistance-breadth]]. [src: microbeatlas_metal_ecology]

## Core evidence

Across 606 bacterial genera with MicrobeAtlas niche data, GTDB r214 phylogenetic representation, and metal AMR data, metal-type diversity positively predicted standardized Levins’ niche breadth after phylogenetic correction. The simple PGLS coefficient was β = +0.021 per standard-deviation increase in metal-type diversity, with SE = 0.0056 and p = 1.5×10⁻⁴; this passed the Bonferroni threshold of p < 0.0083 for six confirmatory models. [src: microbeatlas_metal_ecology]

Metal-type diversity remained significant in a multi-predictor PGLS containing total AMR cluster count and core AMR fraction, with β = +0.023 and p = 5.5×10⁻⁴. The two measures of resistance burden were not significant in that model. This distinguishes resistance breadth from resistance depth: many resistance genes directed toward relatively few metals were not sufficient to predict broader niche breadth in this analysis. [src: microbeatlas_metal_ecology]

The raw association was modest, with an OLS correlation of approximately r = 0.21, because both ecological breadth and resistance traits contain substantial lineage structure. The PGLS result therefore represents residual covariation after accounting for phylogenetic relationships, not a simple uncorrected correlation. [src: microbeatlas_metal_ecology]

## Relationship to phylogeny and gene mobility

Bacterial niche breadth showed strong phylogenetic conservation, with Pagel’s λ = 0.787 for Levins’ B_std across 1,264 genera and λ = 0.909 for the number of detected environment categories. [src: microbeatlas_metal_ecology]

Metal AMR traits showed weaker but significant phylogenetic structure: λ = 0.260 for total AMR cluster count, λ = 0.441 for core AMR fraction, and λ = 0.335 for metal-type diversity. The ordering of these values is consistent with a mixed model in which core resistance is more vertically conserved, while accessory resistance and expansion across metal types are more evolutionarily labile. [src: microbeatlas_metal_ecology]

This pattern is compatible with the role of [[concepts/horizontal-gene-transfer]] and [[concepts/mobile-genetic-elements]] in distributing accessory resistance among distantly related taxa, but the study did not directly reconstruct transfer events. The PGLS association should therefore be interpreted as evidence that metal-resistance breadth covaries with ecological breadth beyond shared ancestry, not as proof that HGT caused ecological expansion. [src: microbeatlas_metal_ecology]

## Robustness of the trait association

The metal-type effect remained positive and significant after adding pangenome species count as a PGLS covariate, with β = +0.0204 and p = 3.4×10⁻⁴. In 200 one-species-per-genus rarefaction iterations, the median coefficient was +0.0147, 89.5% of iterations had p < 0.05, and 57.5% passed the Bonferroni threshold. [src: microbeatlas_metal_ecology]

The effect also remained significant after controlling for genome size. In a 527-genus analysis, metal-type diversity had β = +0.0218, SE = 0.0061, and p = 3.6×10⁻⁴, while adding it to a genome-size model improved AIC by 10.8. A three-covariate model controlling for metal types, log species count, and log genome size retained the metal-type effect at β = +0.0218 and p = 3.5×10⁻⁴. [src: microbeatlas_metal_ecology]

Within-genus heterogeneity did not explain the result: adding the within-genus standard deviation of metal-type counts yielded a metal-type coefficient of β = +0.0189, p = 0.0016, while the standard-deviation covariate was non-significant at p = 0.181. [src: microbeatlas_metal_ecology]

The direction remained positive after excluding each of the seven primary metals, although every leave-one-metal-out model lost significance. This pattern is consistent with a distributed contribution across the diversity spectrum, but it could also partly reflect the reduced variance caused by shrinking the maximum score from seven to six metal types. [src: microbeatlas_metal_ecology]

## Environmental validation

An independent groundwater analysis found that metal-type diversity was positively associated with genus prevalence across 1,624 groundwater samples and 767 genera: Spearman ρ = +0.112, p = 0.0019. Top-quartile genera had median groundwater prevalence of 0.81%, compared with 0.62% for bottom-quartile genera, and the quartile comparison gave p = 0.007. [src: microbeatlas_metal_ecology]

However, metal-type diversity was not significantly associated with groundwater fold enrichment relative to non-groundwater samples, with ρ = +0.042 and p = 0.242. Thus, the validation supports a prevalence association but does not establish that metal-diverse genera are specifically enriched in groundwater beyond their general global prevalence. [src: microbeatlas_metal_ecology]

In the PRJNA1084851 ENIGMA subsurface dataset, community-weighted mean metal-type diversity differed across eight wells, with Kruskal–Wallis H = 29.10 and p = 0.0001. It also increased over time after carbon amendment across 133 samples, with Spearman ρ = +0.383 and p < 0.0001; the strongest within-well association occurred in FW216, with ρ = +0.576 and p = 0.0001. These observations are compatible with environmental selection, but the study notes that only 16.8% of reads were joinable to genus-level AMR data and that the analysis was observational. [src: microbeatlas_metal_ecology]

## Interpretation and boundaries

The ecological-generalism interpretation is that resistance to multiple metals may help lineages tolerate chemically heterogeneous environments, including settings with polymetallic exposure and variation in redox state, salinity, and organic carbon. Alternatively, broad-niche genera may encounter more metal exposures and more potential HGT donors, thereby acquiring broader resistance repertoires. A shared factor such as genome size, metabolic versatility, or biofilm capacity could also influence both traits. [src: microbeatlas_metal_ecology]

Genome-size and sampling-depth controls reduce support for a simple genome-complexity explanation, but they do not resolve directionality. The cross-sectional PGLS design cannot determine whether resistance breadth enables niche expansion, broad ecology promotes resistance acquisition, or both result from another ecological or genomic property. [src: microbeatlas_metal_ecology]

The trait is also proxy-dependent. Niche breadth was inferred from 16S detection across 13 broad environment categories, so it can reflect sequencing effort, primer bias, uneven geographic sampling, and differences among species within a genus rather than the realized range of a single organism. A strict 5% within-environment prevalence filter retained the positive direction, β = +0.0166, but reduced the sample to 379 genera and produced p = 0.092. [src: microbeatlas_metal_ecology]

## Relation to broader concepts

Metal-resistance breadth connects [[concepts/environmental-resistome]] to [[concepts/ecological-generalism]] by proposing that the diversity of resistance functions can be an ecological correlate rather than merely a clinical or genomic inventory. Its distinction between core and accessory resistance also relates to [[concepts/core-accessory-resistance]] and [[concepts/two-speed-genome]]. [src: microbeatlas_metal_ecology]

The evidence illustrates [[concepts/phylogenetic-confounding]]: both niche breadth and resistance traits vary among lineages, so phylogenetic correction is necessary to assess their association. It also exemplifies [[concepts/evidence-triangulation]], because the main global PGLS result was complemented by groundwater prevalence analysis and an independent subsurface time series, each with different limitations. [src: microbeatlas_metal_ecology]

## Open Directions

- Recompute niche breadth after splitting the heterogeneous aquatic category into marine, freshwater, estuarine, and related subclasses, then test whether the metal-type coefficient changes. [src: microbeatlas_metal_ecology]
- Estimate pangenome openness and accessory-gene burden alongside metal-type diversity to test whether a general HGT-associated genome architecture explains the association. [src: microbeatlas_metal_ecology]
- Cluster metal types by gene co-occurrence, such as Cu–Zn or Hg–As combinations, and compare specific co-resistance signatures with the raw count of metal types. [src: microbeatlas_metal_ecology]
- Validate 100 AMRFinderPlus metal-resistance clusters by manual sequence comparison to quantify annotation error and test whether any metal category disproportionately affects breadth estimates. [src: microbeatlas_metal_ecology]
- Use longitudinal metal-enrichment experiments with targeted OTU or qPCR tracking to test whether inferred metal-resistance breadth predicts competitive persistence and ecological expansion. [src: microbeatlas_metal_ecology]
