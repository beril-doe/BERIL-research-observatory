---
sources: ["summaries/metabolic_capability_dependency__REPORT.md", "summaries/discoveries.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_strain_variation__REPORT.md"]
type: "Organism"
description: "Model organism included in AMR variation and metabolic annotation-gap studies"
---

# Escherichia coli

## Identity

- **Canonical name:** *Escherichia coli* [src: amr_strain_variation__REPORT, annotation_gap_discovery]
- **Alias:** *E. coli* [src: amr_strain_variation__REPORT, annotation_gap_discovery]
- **Entity type:** Organism [src: annotation_gap_discovery]

## Relevance to the AMR strain-variation study

*Escherichia coli* was identified as a major case-study species for within-species antimicrobial-resistance (AMR) variation. [src: amr_strain_variation__REPORT] The planned case-study set also includes [[entities/klebsiella-pneumoniae]], [[entities/staphylococcus-aureus]], [[entities/pseudomonas-aeruginosa]], [[entities/salmonella-enterica]], and [[entities/acinetobacter-baumannii]]. [src: amr_strain_variation__REPORT]

The species was excluded from the report's case-study UMAP plots because it exceeded the 500-genome computational cap. [src: amr_strain_variation__REPORT] It was likewise excluded from the ANI-based Mantel phylogenetic-signal analysis because the species contained 15,388 genomes, exceeding the analysis limit. [src: amr_strain_variation__REPORT]

These exclusions mean that the report's broad conclusions about [[concepts/phylogenetic-amr-structure]] were not directly evaluated for *E. coli* in the capped Mantel analysis. [src: amr_strain_variation__REPORT] They also leave *E. coli* as a priority target for future large-species AMR analysis using a justified subsampling strategy. [src: amr_strain_variation__REPORT]

## AMR and ecological context

The report states that the genome collection is strongly biased toward clinical and human-associated isolates, particularly for *E. coli*, [[entities/klebsiella-pneumoniae]], and [[entities/staphylococcus-aureus]]. [src: amr_strain_variation__REPORT] This sampling bias should be considered when interpreting *E. coli* AMR burden, ecological distributions, and potential [[concepts/core-accessory-resistance]] patterns from the collection. [src: amr_strain_variation__REPORT]

## Metabolic annotation-gap study

*E. coli* Keio was one of 14 organisms selected from the [[entities/fitness-browser]] for integrated metabolic annotation-gap analysis. [src: annotation_gap_discovery__REPORT] The study combined [[entities/flux-balance-analysis]]-based gapfilling with fitness evidence, pangenome conservation, GapMind, Bakta annotations, and DIAMOND sequence homology to identify genes associated with unresolved metabolic reactions. [src: annotation_gap_discovery__REPORT]

For the *E. coli* Keio strain, 7 gapfilled reaction–organism pairs were evaluated and 4 were resolved, giving a resolution rate of 57.1%. [src: annotation_gap_discovery__REPORT] This organism-level result was part of a broader analysis that resolved 96 of 201 pairs (47.8%) across the 14 organisms. [src: annotation_gap_discovery__REPORT]

The analysis used draft models built from ModelSEED/RAST annotations and evaluated growth across organism–carbon-source conditions before conditional gapfilling. [src: annotation_gap_discovery__REPORT] The resulting assignments should be interpreted in light of the study's limitations, including non-unique gapfill solutions, possible carbon-source mapping errors, automated-model errors, and phylogenetic bias toward Proteobacteria. [src: annotation_gap_discovery__REPORT]

## Open analytical work

The report recommends a detailed *E. coli* AMR case study with UMAP, heatmap, and clinical-metadata overlays. [src: amr_strain_variation__REPORT] It also recommends developing subsampling strategies to extend ANI-based Mantel tests to species with more than 500 genomes, which would make direct assessment of *E. coli*'s [[concepts/phylogenetic-amr-structure]] possible. [src: amr_strain_variation__REPORT]

The four resolved metabolic annotation-gap pairs in *E. coli* Keio are candidates for follow-up validation, although the report's knockout simulations were inconclusive because the tested gapfilled reactions were themselves required for growth on the relevant minimal carbon-source media. [src: annotation_gap_discovery__REPORT] Applying targeted genetic validation after improving model formulation could test whether the proposed assignments explain the observed phenotypes. [src: annotation_gap_discovery__REPORT]

## Sources

- [[summaries/amr_strain_variation__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]

See also: [[summaries/bacdive_phenotype_metal_tolerance__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/metabolic_capability_dependency__REPORT]]