---
type: "Concept"
sources: ["summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/microbeatlas_metal_ecology__REPORT.md"]
description: "Broader metal resistance repertoires are linked to broader microbial niches."
---

# Ecological Generalism and Resistance Breadth

## Core idea

Ecological generalism is the tendency of a taxon to occur across a broad range of environments, while resistance breadth is the number of distinct metal types for which it carries inferred resistance determinants. The central result of the [[summaries/microbeatlas_metal_ecology__REPORT]] is that these traits are positively associated in bacteria: genera with broader metal-resistance repertoires tend to have broader inferred ecological niches after phylogenetic correction. [src: microbeatlas_metal_ecology]

This relationship concerns resistance breadth rather than resistance burden. The number of metal types resisted predicted niche breadth, whereas total AMR cluster count and core AMR fraction did not survive the primary multiple-testing correction. [src: microbeatlas_metal_ecology] This distinction connects [[concepts/metal-resistance-breadth]] with [[concepts/ecological-generalism]], [[concepts/environmental-metal-tolerance]], and [[concepts/environmental-resistome]].

## Evidence from the global comparison

The analysis linked AMRFinderPlus annotations from 6,789 GTDB species to niche estimates from 98,919 MicrobeAtlas OTUs across 463,972 samples. [src: microbeatlas_metal_ecology] At the genus level, the primary phylogenetically corrected analysis included 606 bacterial genera with at least three OTUs, GTDB tree representation, and metal-AMR data. [src: microbeatlas_metal_ecology]

Bacterial niche breadth showed substantial phylogenetic conservation, with Pagel’s λ = 0.787 for standardized Levins’ niche breadth and λ = 0.909 for the number of detected environment categories across 1,264 genera. [src: microbeatlas_metal_ecology] After accounting for phylogeny, standardized metal type diversity had a positive coefficient of β = +0.021, SE = 0.0056, and p = 1.5×10⁻⁴, passing the Bonferroni threshold of p < 0.0083 for six primary models. [src: microbeatlas_metal_ecology]

The multi-predictor model retained the metal-type effect at β = +0.023 and p = 5.5×10⁻⁴, while total AMR cluster count and core AMR fraction remained non-significant. [src: microbeatlas_metal_ecology] These results provide strong comparative evidence for an association, but they do not demonstrate that resistance breadth causes ecological generalism. [src: microbeatlas_metal_ecology]

## Breadth versus depth

A genus can possess many resistance genes concentrated on a small number of metals, or it can possess determinants spanning several metal types. The study found that the second property, not simply the total number of AMR clusters, was associated with broader niche estimates. [src: microbeatlas_metal_ecology]

This breadth-over-depth pattern suggests that resistance repertoires may capture the ability to tolerate chemically diverse stressors, whereas gene-count burden alone may be a less informative indicator of ecological range. [src: microbeatlas_metal_ecology] This interpretation is consistent with [[concepts/core-accessory-resistance]] and [[concepts/two-speed-genome]], because core and accessory resistance components can have different evolutionary and ecological distributions. [src: microbeatlas_metal_ecology]

## Evolutionary basis

Metal AMR traits had intermediate phylogenetic signal: λ = 0.260 for total AMR clusters, λ = 0.441 for core AMR fraction, and λ = 0.335 for metal type diversity. [src: microbeatlas_metal_ecology] Niche breadth was therefore more phylogenetically conserved than the measured metal-resistance traits in bacteria. [src: microbeatlas_metal_ecology]

The report interprets this contrast as consistent with a mixed inheritance model in which core resistance is more vertically conserved, while accessory resistance and expansion across metal types are more labile and potentially influenced by [[concepts/horizontal-gene-transfer]] and [[concepts/mobile-genetic-elements]]. [src: microbeatlas_metal_ecology] This is an evolutionary interpretation supported by signal structure, not a direct measurement of transfer events or resistance acquisition histories. [src: microbeatlas_metal_ecology]

The comparison with nitrification provides an internal contrast: nitrification had λ = 0.939 in bacteria and λ = 1.000 in archaea, whereas metal-resistance traits had intermediate values. [src: microbeatlas_metal_ecology] The study uses this contrast to distinguish deeply conserved metabolic functions from more labile resistance traits. [src: microbeatlas_metal_ecology]

## Robustness and boundary conditions

The positive metal-type association remained significant after adding pangenome species count, genome size, or both genome size and species count as covariates. [src: microbeatlas_metal_ecology] In the three-covariate model, metal types had β = +0.0218, p = 3.5×10⁻⁴, and genome size also had an independent positive association, while log species count was not significant. [src: microbeatlas_metal_ecology]

Rarefaction to one species per genus across 200 iterations produced a median metal-type coefficient of +0.0147, with 89.5% of iterations nominally significant and 57.5% passing the Bonferroni threshold. [src: microbeatlas_metal_ecology] This supports the conclusion that uneven pangenome coverage does not fully explain the association, although the rarefied effect was smaller than the full-data estimate. [src: microbeatlas_metal_ecology]

The association remained positive after excluding each of the seven primary metal categories, but no individual leave-one-metal-out model remained significant. [src: microbeatlas_metal_ecology] This pattern is compatible with a distributed signal across metal types, although it could also partly reflect reduced predictor variance when one of seven categories is removed. [src: microbeatlas_metal_ecology]

Excluding each of the 13 broad environment categories also preserved a positive coefficient, with the weakest result after excluding aquatic samples: β = +0.0085 and p = 0.031. [src: microbeatlas_metal_ecology] A strict within-environment prevalence threshold of 5% reduced the sample to 379 genera and yielded β = +0.0166 and p = 0.092, indicating that the direction persisted but power decreased substantially. [src: microbeatlas_metal_ecology]

These sensitivity results support [[concepts/evidence-triangulation]], while also illustrating [[concepts/coverage-limited-inference]]: inferred niche breadth depends on detection, sampling intensity, environment definitions, and taxonomic aggregation. [src: microbeatlas_metal_ecology]

## Independent environmental checks

In 1,624 groundwater samples, metal type diversity was positively associated with genus prevalence across 767 genera, with Spearman ρ = +0.112 and p = 0.0019. [src: microbeatlas_metal_ecology] Top-quartile metal-diversity genera had median groundwater prevalence of 0.81%, compared with 0.62% for bottom-quartile genera, and the group comparison gave p = 0.007. [src: microbeatlas_metal_ecology]

Groundwater fold enrichment relative to non-groundwater samples was not significantly associated with metal type diversity, with ρ = +0.042 and p = 0.242. [src: microbeatlas_metal_ecology] Thus, the groundwater analysis supports a prevalence association but does not establish groundwater-specific selection or prove a metal-contamination mechanism. [src: microbeatlas_metal_ecology]

A separate analysis of 133 ENIGMA ORFRC samples found that community-weighted mean metal-type diversity differed across eight wells, with Kruskal–Wallis p = 0.0001, and increased over time after carbon amendment, with Spearman ρ = +0.383 and p < 0.0001. [src: microbeatlas_metal_ecology] The contaminated-plume wells FW215 and FW216 had the highest median community-weighted values, but only 16.8% of reads were joinable to genus-level AMR data, so this result remains coverage-limited. [src: microbeatlas_metal_ecology]

The decline of *Sulfurimonas* over time despite its high prevalence demonstrates that ecological success in groundwater can also be controlled by electron-acceptor availability rather than metal resistance breadth. [src: microbeatlas_metal_ecology] This counterexample supports separating [[concepts/environmental-occupancy-vs-activity]] and general environmental prevalence from resistance-mediated fitness under a specific stress. [src: microbeatlas_metal_ecology]

## Causal alternatives

The observed association is compatible with at least three causal models. [src: microbeatlas_metal_ecology]

1. Resistance breadth may enable colonization of chemically diverse environments.
2. Broad-niche taxa may encounter more habitats, metal exposures, and potential HGT donors, thereby acquiring more diverse resistance determinants.
3. A shared factor, such as genome size, metabolic versatility, or biofilm capacity, may promote both ecological generalism and resistance breadth.

Genome-size adjustment reduced the plausibility that genome complexity alone explains the result, but the cross-sectional design cannot establish directionality. [src: microbeatlas_metal_ecology] The appropriate conclusion is therefore that bacterial genera with diverse inferred metal-resistance repertoires are, on average, broader inferred ecological generalists, not that resistance breadth causes range expansion. [src: microbeatlas_metal_ecology]

## Tensions

The global PGLS association is statistically robust in bacteria, but the strict 5% prevalence analysis was non-significant at p = 0.092 and the groundwater fold-enrichment test was non-significant at p = 0.242. [src: microbeatlas_metal_ecology] These results do not reverse the main finding, but they limit claims that the association is specifically driven by rare-detection artifacts or preferential groundwater enrichment. [src: microbeatlas_metal_ecology]

The archaeal analysis also remains unresolved: metal type diversity had a positive coefficient of β = +0.0145 but was non-significant at p = 0.467 in only 48 genera. [src: microbeatlas_metal_ecology] Formal power analysis estimated that at least 702 genera would be needed for 80% power at α = 0.05 under the observed effect and model assumptions. [src: microbeatlas_metal_ecology]

## Open Directions

- Use finer MicrobeAtlas environmental categories, especially marine, freshwater, and estuarine subdivisions of “aquatic,” to test whether ecological generalism depends on category granularity. [src: microbeatlas_metal_ecology]
- Combine genus-level metal breadth with site metadata for contaminated and uncontaminated locations to test whether the global association is specifically coupled to metal exposure. [src: microbeatlas_metal_ecology]
- Estimate pangenome openness and HGT burden alongside metal type diversity to test whether accessory-genome dynamics explain the breadth-generalism relationship. [src: microbeatlas_metal_ecology]
- Perform longitudinal metal-enrichment experiments with the shortlisted OTUs or defined communities to distinguish resistance-mediated expansion from general stress tolerance and ecological filtering. [src: microbeatlas_metal_ecology]
- Expand archaeal AMR sampling and repeat the PGLS when substantially more environmentally representative archaeal genera are available. [src: microbeatlas_metal_ecology]
- Test metal co-resistance combinations and validate AMRFinderPlus classifications experimentally or by manual sequence review before assigning mechanistic meaning to resistance breadth. [src: microbeatlas_metal_ecology]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]