---
sources: ["summaries/discoveries.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md"]
type: "Organism"
description: "Salmonella enterica shows extensive accessory and lineage-structured AMR variation."
---

# Salmonella enterica

## Identity

*Salmonella enterica* is a bacterial species examined in analyses of the [[concepts/environmental-resistome]], pan-bacterial AMR distribution, and within-species AMR variation. The available reports do not provide a stable external identifier or additional taxonomic metadata for this entity. [src: amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation]

## Findings in the environmental resistome analysis

*Salmonella enterica* was one of five deeply sampled case-study species used to examine how AMR varies with the environmental distribution of genomes. The dataset included **10,097 genomes** and **836 AMR gene clusters** for this species. [src: amr_environmental_resistome]

Only **11 AMR clusters were core**, while **825 (99%) were accessory**. [src: amr_environmental_resistome] This profile places *S. enterica* among the examples of species with extensive accessory resistance variation in the pangenome. [src: amr_environmental_resistome]

Its dominant environment was classified as **host-associated**, representing **31% of its genomes**. [src: amr_environmental_resistome] The report uses this species-level classification as part of a broader analysis linking environmental distribution to [[concepts/core-accessory-resistance]] composition and total AMR content. [src: amr_environmental_resistome]

## Findings in the pan-bacterial AMR atlas

In the pan-bacterial AMR atlas, Salmonella was identified as a major AMR hotspot at the genus level, averaging **198 AMR clusters per species**. It ranked second among the listed genera, behind Klebsiella at 206 AMR clusters per species. [src: amr_pangenome_atlas]

The atlas analyzed [[entities/amrfinderplus]] annotations across 14,723 AMR-carrying species and found that AMR genes were generally depleted from core genomes relative to pangenome baselines: 30.3% of AMR genes were core compared with 46.8% for the baseline. [src: amr_pangenome_atlas] The *S. enterica* case-study result is more extreme, with 99% of its reported AMR clusters classified as accessory. [src: amr_environmental_resistome]

The two reports use different datasets and aggregation schemes, so their AMR counts should not be treated as directly interchangeable. The environmental-resistome analysis reports 836 clusters for the *S. enterica* case study, whereas the atlas reports a genus-level mean of 198 clusters per species. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Findings in the within-species AMR variation analysis

The within-species strain-variation report included *S. enterica* among case-study species for AMR ecotype visualization. Its case-study UMAP showed visible environmental structuring of AMR profiles, although the broader environment-ecotype association analysis was underpowered because 52.7% of genomes lacked a classifiable isolation source and only two species met the strict criteria for statistical testing. [src: amr_strain_variation]

The report excluded *Escherichia coli* from its case studies because of a 500-genome computational cap, but it did not report a corresponding exclusion of *S. enterica*. [src: amr_strain_variation]

The broader analysis found that 19.5% of 974 species with sufficient genomes formed at least two distinct AMR ecotypes using UMAP and DBSCAN, with a median silhouette score of 0.620. These cross-species results provide context for interpreting the visible *S. enterica* environmental structuring, but no species-specific ecotype count or significance result was reported for *S. enterica*. [src: amr_strain_variation]

## Interpretation and context

The high accessory fraction is consistent with the broader [[concepts/core-accessory-resistance]] finding that acquired resistance is concentrated in accessory genomes, whereas intrinsic resistance can be more conserved. [src: amr_environmental_resistome, amr_pangenome_atlas] The within-species variation analysis further shows that, across the analyzed species, AMR variation can be organized into phylogenetic lineages and tightly co-inherited resistance islands rather than being randomly distributed. [src: amr_strain_variation]

The atlas reports that clinical species carry **10.6 AMR clusters per species**, compared with **4.6** for Soil/Terrestrial species, and that clinical AMR is less core (**30.8%**) than soil AMR (**58.1%**) or plant AMR (**63.1%**). [src: amr_pangenome_atlas] These comparisons, together with the host-associated classification of the *S. enterica* environmental-resistome dataset, support the hypothesis that host-associated and clinical sampling is associated with greater abundance of acquired-looking, accessory AMR in *S. enterica* and other bacteria. [src: amr_environmental_resistome, amr_pangenome_atlas]

However, species-level pangenome summaries and the *S. enterica* case-study visualization do not establish that host-associated growth, clinical exposure, or environment caused the observed AMR pattern. [src: amr_environmental_resistome, amr_strain_variation] The environmental association result for *S. enterica* should therefore be treated as descriptive rather than as a statistically established ecotype-environment relationship. [src: amr_strain_variation]

The strain-variation report also found, across 1,261 species, that 55.6% had significant AMR phylogenetic signal after FDR correction, with a median Mantel r of 0.247; non-core AMR genes had a higher median signal than core genes (0.222 versus 0.117). [src: amr_strain_variation] These aggregate results are relevant to the hypothesis that accessory AMR in *S. enterica* may be maintained within lineages, but the report does not provide a *S. enterica*-specific Mantel statistic, so this interpretation is not established for this species. [src: amr_strain_variation]

The *S. enterica* case study is documented in [[summaries/amr_environmental_resistome__REPORT]], its genus-level hotspot result is documented in [[summaries/amr_pangenome_atlas__REPORT]], and its strain-level ecotype visualization is documented in [[summaries/amr_strain_variation__REPORT]].

## Related entities

- [[entities/klebsiella-pneumoniae]]
- [[entities/staphylococcus-aureus]]
- [[entities/streptococcus-pneumoniae]]
- [[entities/mycobacterium-tuberculosis]]

## Related concepts

- [[concepts/core-accessory-resistance]]
- [[concepts/environmental-resistome]]
- [[concepts/phylogenetic-amr-structure]]
- [[concepts/resistance-islands]]

See also: [[summaries/bacdive_phenotype_metal_tolerance__REPORT]]

See also: [[summaries/discoveries]]