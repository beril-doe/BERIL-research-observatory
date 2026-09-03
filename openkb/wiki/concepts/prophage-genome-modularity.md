---
type: "Concept"
sources: ["summaries/prophage_ecology__REPORT.md"]
description: "Prophages combine linked core functions with scattered, mobile accessory modules."
---

# Prophage Genome Modularity

## Definition

Prophage genome modularity is the organization of prophage-associated functions into partially independent functional units that differ in conservation, genomic co-localization, and ecological responsiveness. The [[summaries/prophage_ecology__REPORT]] supports a two-tier model: a physically linked core backbone of packaging, lysis, and lysogenic regulation, alongside accessory functions such as structural diversification, integration, and anti-defense that are more variable or genomically dispersed. [src: prophage_ecology]

This organization places prophages within the broader biology of [[concepts/mobile-genetic-elements]], where functions can be retained, exchanged, lost, or redeployed independently rather than inherited only as complete elements. [src: prophage_ecology]

## Evidence for a Core Backbone

Across 27,702 bacterial species, packaging (module A), lysis (D), and lysogenic regulation (F) were detected in 100.0%, 99.9%, and 100.0% of species, respectively. These modules also showed strong within-module co-occurrence and high contig co-localization. [src: prophage_ecology]

In tests spanning 15 phylogenetically stratified species, packaging genes showed significant co-occurrence in 11/15 species with mean contig co-localization of 0.986; lysis genes were significant in 13/15 with mean co-localization of 0.901; and lysogenic-regulation genes were significant in 10/15 with mean co-localization of 1.000. [src: prophage_ecology]

The strong physical association of these functions supports the interpretation that packaging, lysis, and lysogenic regulation commonly form a linked prophage backbone rather than representing independently distributed annotations. [src: prophage_ecology]

## Variable and Accessory Functions

Head morphogenesis (B), tail (C), and anti-defense (G) modules were substantially less prevalent than the core modules, occurring in 56.1%, 55.6%, and 64.3% of species, respectively. Only 34.9% of species carried all seven defined modules. [src: prophage_ecology]

Structural modules also showed strong environmental variation: head morphogenesis ranged from 10.2% in Thermoplasmatota to 81% in human-associated species, while tail ranged from 6.5% in Thermoplasmatota to 82% in food-associated species. Anti-defense prevalence ranged from 3.1% in Patescibacteria to 97.8% in Campylobacterota. [src: prophage_ecology]

Anti-defense genes had especially weak physical association with one another, showing significant co-occurrence in only 3/11 tests and mean contig co-localization of 0.281. This pattern is consistent with anti-defense functions occurring in defense islands that are distinct from the core prophage backbone. [src: prophage_ecology]

Integration genes were also weakly co-localized, with significant co-occurrence in only 1/15 tests and mean co-localization of 0.420. Their dispersed distribution is compatible with insertion at different genomic sites and with the persistence of prophage-derived remnants that retain integrases without a complete prophage architecture. [src: prophage_ecology]

## Modularity and Ecological Response

The report found that environment explained more variation in prophage module composition than host-family phylogeny after accounting for the strong effect of genome size: PERMANOVA F-statistics were 30.04 for environment and 6.17 for phylogeny, with p=0.01 for both predictors. [src: prophage_ecology]

Human-associated environments were enriched for tail, head-morphogenesis, and anti-defense modules after constrained permutations preserved host-family and genome-size strata. Tail had log2(OR)=2.21 and Z=10.86, head morphogenesis had log2(OR)=1.98 and Z=10.00, and anti-defense had log2(OR)=1.70 and Z=8.76. [src: prophage_ecology]

The concentration of environmental signal in structurally variable and anti-defense modules suggests that modular exchange, retention, or loss may allow prophage-associated functions to respond to ecological conditions without requiring adaptation of an entire prophage lineage. This is an evidence-supported interpretation of the module-level results, not a direct demonstration of gene transfer or causal selection. [src: prophage_ecology]

NMDC metagenomic analysis independently detected significant environmental associations for modules including head morphogenesis, tail, and anti-defense, which were also significant in the pangenome enrichment analysis. Near-universal modules were significant in some NMDC abiotic analyses but showed little pangenome enrichment, consistent with a prevalence ceiling limiting presence/absence variation. [src: prophage_ecology]

## Modularity Versus Lineage Ecology

TerL clustering produced 10,991 lineages from 38,085 sequences at 70% amino acid identity, including 6,921 singleton lineages and a largest lineage spanning 1,094 members across 869 species. [src: prophage_ecology]

No individual TerL lineage showed significant environment-specific enrichment after FDR correction across 500 tests, whereas module-level environmental associations were detected. This contrast supports the [[concepts/module-versus-lineage-ecology]] distinction: ecological differentiation can occur at the level of exchanged or independently retained modules even when whole-lineage distributions remain largely explained by host ecology and phylogeny. [src: prophage_ecology]

Among 824 TerL lineages with at least five species, 325 were classified as specialists and 499 as generalists, indicating substantial variation in ecological breadth despite the absence of FDR-significant lineage-specific enrichment. [src: prophage_ecology]

## Interpretation and Boundaries

The modularity model is strongest for the core backbone because co-occurrence and contig-localization evidence directly support physical linkage for packaging, lysis, and lysogenic regulation. [src: prophage_ecology]

The interpretation of modules B, C, E, and G as accessory or independently organized functions is supported by lower prevalence, weaker co-localization, or both, but their classifications were derived from eggNOG annotations rather than dedicated prophage detection tools. Annotation-based inference may therefore include bacterial homologs and domesticated prophage remnants, an instance of the broader [[concepts/annotation-gap]]. [src: prophage_ecology]

The environmental interpretation is also constrained by genome size, incomplete environmental metadata, indirect genus-level inference in NMDC samples, and limited co-occurrence replication across species. These limitations make the ecological role of modularity a strong comparative hypothesis rather than a fully resolved mechanism. [src: prophage_ecology]

## Tensions

The report simultaneously supports strong physical linkage for core modules and substantial independence for integration and anti-defense functions. This is not necessarily a contradiction: it indicates that “prophage modularity” describes heterogeneous organization rather than a uniform property shared equally by every module. [src: prophage_ecology]

A second tension is that module-level ecology shows environmental associations while TerL lineages do not show individually significant environmental enrichment. The available evidence favors modular exchange or differential module retention as an explanation, but dedicated gene-history analyses would be required to distinguish these mechanisms from annotation and sampling effects. [src: prophage_ecology]

## Open Directions

- Apply geNomad or VIBRANT to representative genomes and test whether core-versus-accessory co-localization patterns persist after dedicated prophage identification, addressing the annotation gap. [src: prophage_ecology]
- Compare module gene trees with TerL phylogenies to test whether environmentally enriched modules have histories of horizontal transfer or reassortment independent of whole-prophage lineages. [src: prophage_ecology]
- Map anti-defense genes together with host defense systems and test defense-island co-localization across the same genomes, directly evaluating the proposed separation from the core backbone. [src: prophage_ecology]
- Expand co-occurrence tests within phyla and across multiple genomes per species to determine whether the observed core-backbone pattern generalizes beyond the 15-species sample. [src: prophage_ecology]
- Use partial PERMANOVA while simultaneously controlling for genome size and phylogeny to quantify the unique environmental component of module composition. [src: prophage_ecology]