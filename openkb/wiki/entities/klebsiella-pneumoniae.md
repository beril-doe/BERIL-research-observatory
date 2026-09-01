---
sources: ["summaries/metal_fitness_atlas__REPORT.md", "summaries/discoveries.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md"]
type: "Organism"
description: "Clinical-associated species with a large, highly accessory AMR resistome."
---

# *Klebsiella pneumoniae*

## Identity

*Klebsiella pneumoniae* is a bacterial species analyzed as a deeply sampled example of environment-associated antimicrobial-resistance variation. Known abbreviation: *K. pneumoniae*. [src: amr_environmental_resistome]

## Resistome profile

- One analysis included **13,637 genomes** of *K. pneumoniae*. [src: amr_environmental_resistome]
- These genomes contained **1,115 AMR gene clusters**, including **7 core clusters** and **1,108 accessory clusters (99%)**. [src: amr_environmental_resistome]
- Clinical sources were the dominant environment, accounting for **80% of its genomes**. [src: amr_environmental_resistome]

The extreme accessory fraction makes *K. pneumoniae* a prominent example of the [[concepts/core-accessory-resistance]] pattern identified in the report: clinical-dominated species tend to carry large, predominantly accessory resistomes. [src: amr_environmental_resistome]

The pan-bacterial AMR atlas additionally reports that the **Klebsiella genus** had the highest genus-level AMR density, with **206 AMR clusters per species**. This is a genus-level result and should not be treated as a measurement specific to the 13,637 *K. pneumoniae* genomes above. [src: amr_pangenome_atlas]

A separate within-species AMR-variation analysis used a collection containing **14,240 *K. pneumoniae* genomes**; this count differs from the 13,637-genome analysis because the projects used different source collections or selection criteria. [src: amr_strain_variation]

## Within-species AMR variation

The strain-variation study included *K. pneumoniae* among its case-study species for UMAP visualization of AMR profiles. The case-study plots showed visible environmental structuring of AMR profiles, but formal environment–ecotype testing was severely limited across the study: only **2 species** met the required metadata and expected-frequency criteria, so no adequately powered species-specific statistical conclusion is reported here for *K. pneumoniae*. [src: amr_strain_variation]

The same study excluded *K. pneumoniae* from ANI-based Mantel testing because the analysis imposed a **500-genome computational cap**; consequently, the report does not provide a *K. pneumoniae*-specific estimate of AMR phylogenetic signal. [src: amr_strain_variation]

These observations make *K. pneumoniae* a useful case for investigating [[concepts/phylogenetic-amr-structure]] and AMR ecotype formation, but the visible environmental pattern remains hypothesis-generating rather than a statistically established species-level association. [src: amr_strain_variation]

## Interpretation

The large accessory resistome of *K. pneumoniae* is interpreted as evidence of substantial within-species AMR variation associated with clinical sampling and horizontal gene transfer in clinical settings. This is an interpretation of an observational species-level analysis rather than a direct per-genome demonstration of transfer or causality. [src: amr_environmental_resistome]

The broader atlas found that human/clinical species carried **10.6 AMR clusters per species**, compared with **4.6** in Soil/Terrestrial species, **3.9** in Aquatic species, and **3.0** in Animal species. Clinical AMR was also less core (**30.8%**) than soil AMR (**58.1%**) or plant AMR (**63.1%**). These cross-environment results support interpreting *K. pneumoniae* as a clinical-associated example of the broader [[concepts/environmental-resistome]] pattern, while the atlas values are not species-specific estimates for *K. pneumoniae*. [src: amr_pangenome_atlas]

The within-species study's environmental UMAP pattern is consistent with ecological structuring of AMR profiles, but metadata sparsity prevents treating that pattern as a confirmed environment-associated ecotype result for this species. [src: amr_strain_variation]

The pan-bacterial analysis further found that AMR genes overall were depleted from bacterial core genomes: **30.3%** were core versus **46.8%** for the pangenome baseline (OR=0.49, chi-squared=23,117, p≈0), with the auxiliary genome **2.2x enriched** for AMR. These aggregate results provide context for, but do not replace, the *K. pneumoniae*-specific measurements. [src: amr_pangenome_atlas]

## Related entities

- [[entities/amrfinderplus]] — AMR annotation resource used in the source projects' data assembly. [src: amr_environmental_resistome, amr_pangenome_atlas]
- [[entities/staphylococcus-aureus]] — another deeply sampled clinical-dominated species used for comparison and an AMR-ecotype case study. [src: amr_environmental_resistome, amr_strain_variation]
- [[entities/salmonella-enterica]] — a deeply sampled comparison species with a host-associated dominant environment and an AMR-ecotype case study. [src: amr_environmental_resistome, amr_strain_variation]
- [[entities/escherichia-coli]] — a deeply sampled case-study species that, like *K. pneumoniae*, exceeded the 500-genome cap for the strain-variation study's phylogenetic analysis. [src: amr_strain_variation]
- [[entities/mycobacterium-tuberculosis]] — another clinical-dominated case study in the environmental-resistome analysis. [src: amr_environmental_resistome]

## Related Documents

- [[summaries/amr_pangenome_atlas__REPORT]]
- [[summaries/amr_strain_variation__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/metal_fitness_atlas__REPORT]]