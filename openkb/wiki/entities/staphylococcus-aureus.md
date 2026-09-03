---
sources: ["summaries/functional_dark_matter__REPORT.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md"]
type: "Organism"
description: "A clinically sampled species with highly accessory AMR and structured strain variation"
---

# Staphylococcus aureus

## Identity

*Staphylococcus aureus* is a bacterial organism analyzed as a deeply sampled species in the environmental resistome study and as an AMR strain-variation case study. [src: amr_environmental_resistome, amr_strain_variation]

**Alias:** *S. aureus*. [src: amr_environmental_resistome]

## Evidence from the environmental resistome study

The dataset included **13,274 genomes** of *S. aureus* and identified **642 AMR gene clusters**. [src: amr_environmental_resistome]

Only **9 AMR clusters were core**, while **633 (99%) were accessory**. [src: amr_environmental_resistome] This profile places *S. aureus* among the examples of a [[concepts/core-accessory-resistance]] pattern dominated by acquired rather than broadly conserved resistance. [src: amr_environmental_resistome]

Clinical genomes represented **85%** of the sampled *S. aureus* genomes, making clinical sources the dominant environment in this case study. [src: amr_environmental_resistome]

The report uses *S. aureus*, alongside [[entities/klebsiella-pneumoniae]], [[entities/salmonella-enterica]], [[entities/streptococcus-pneumoniae]], and [[entities/mycobacterium-tuberculosis]], to illustrate substantial AMR variation in deeply sampled species associated with clinical environments. [src: amr_environmental_resistome]

## Evidence from the within-species AMR variation study

*S. aureus* was one of the case-study species examined with UMAP visualizations of AMR profiles and clinical or environmental metadata. [src: amr_strain_variation] The visualization showed visible environmental structuring of AMR profiles, although the study did not establish a statistically supported environment-ecotype association for *S. aureus*. [src: amr_strain_variation]

Across the broader analysis, 190 of 974 species with sufficient genome sampling formed at least two distinct AMR ecotypes, but environmental testing was strongly limited by metadata sparsity; 52.7% of genomes lacked a classifiable isolation source, and only two species met the strict criteria for association testing. [src: amr_strain_variation] Therefore, the apparent environmental structure in *S. aureus* should be treated as suggestive rather than as evidence of a confirmed ecological partition. [src: amr_strain_variation]

The broader study found that host-associated species carried more AMR genes per genome than terrestrial or aquatic species, with human-clinical isolates showing the highest AMR burden in both environmental-classification approaches. [src: amr_strain_variation] This result is consistent with the clinical predominance and accessory-AMR profile observed for *S. aureus*, but it is a cross-species association rather than a separate organism-specific test. [src: amr_environmental_resistome, amr_strain_variation]

## Interpretation and limitations

The near-total accessory fraction in the sampled *S. aureus* AMR profile is consistent with extensive within-species AMR variation and possible horizontal gene transfer in clinical settings, but the report does not establish causality or directly test transfer events for this organism. [src: amr_environmental_resistome]

The strain-variation study further suggests that AMR profiles in *S. aureus* may be structured by ecological niche, but the environmental interpretation remains underpowered because of incomplete isolation-source metadata. [src: amr_strain_variation]

Interpretation is limited by clinical sampling bias, uneven genome representation, and the study's use of species-level environment summaries rather than a true per-genome within-species comparison. [src: amr_environmental_resistome]

The broader strain-variation analysis also relied on AMRFinderPlus for AMR detection, used approximate environment classifiers, and cautioned that genome-collection bias limits generalization to environmental populations. [src: amr_strain_variation]

## Related pages

- [[concepts/environmental-resistome]]
- [[concepts/core-accessory-resistance]]
- [[concepts/phylogenetic-amr-structure]]
- [[concepts/resistance-islands]]
- [[summaries/amr_environmental_resistome__REPORT]]
- [[summaries/amr_strain_variation__REPORT]]

See also: [[summaries/functional_dark_matter__REPORT]]