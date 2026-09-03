---
type: "Summary"
description: "Pangenome-scale analysis links bacterial resistomes to ecology and clinical exposure."
doc_type: short
full_text: "sources/amr_environmental_resistome__REPORT.md"
---

# Environmental Resistome at Pangenome Scale

## Overview

This report analyzes how bacterial antimicrobial-resistance (AMR) gene content varies across ecological environments using 82,908 AMR gene clusters from 14,723 species and 280,337 genomes in the KBase BER Data Lakehouse. It tests environment-level differences in AMR abundance, core/accessory composition, resistance mechanisms, within-species clinical exposure, phylogenetic controls, and continuous environmental embeddings.

The central conclusion is that the [[concepts/environmental-resistome]] is strongly ecology-structured: clinical and human-gut species carry substantially more AMR than soil and aquatic species, and the excess is predominantly accessory, likely acquired resistance. Soil and aquatic species have proportionally more core resistance, especially metal resistance, whereas clinical and gut species are enriched for target modification and other antibiotic-associated mechanisms.

## Data and scope

- **82,908 AMR gene clusters** across **14,723 species**.
- **280,337 genomes** with environmental metadata; 93.5% received a per-genome environment classification.
- Species-level majority-vote environment classifications covered 95% of species, or 13,981 species.
- **823 species** qualified for the within-species proxy analysis using genomes from at least two environments and at least five genomes per environment.
- Mechanism assignments included enzymatic inactivation (26,220 clusters), metal resistance (22,223), target modification (11,067), and efflux (5,224).
- **15,550 clusters (18.7%)** could not be assigned to a resistance mechanism and were excluded from mechanism-composition fractions.

## Key findings

### 1. Clinical species carry more AMR

Clinical-source species had a median of **5 AMR gene clusters**, compared with **2** for soil, aquatic, and host-associated species; human-gut species also had a median of 5. The environment effect was strong and highly significant (Kruskal–Wallis H = 781.9, p = 9.4×10⁻¹⁶⁷, η² = 0.056), with 13 of 15 pairwise environment comparisons significant after FDR correction. The largest contrast was clinical versus aquatic species (rank-biserial r = −0.49).

The result remained significant under majority-vote classification thresholds of 50%, 60%, 75%, and 90% (η² = 0.044–0.056). At this scale, the analysis extends earlier ecology-based resistome studies from approximately 6,000 genomes to 293K genomes and 14,723 species.

### 2. Clinical AMR is predominantly accessory

The [[concepts/core-accessory-resistance]] composition varied substantially by environment. Clinical species averaged **32.4% core and 67.6% accessory AMR**, while soil species averaged **57.1% core and 42.9% accessory AMR**. Human-gut species had the highest accessory fraction, at **80.3%**.

| Environment | Mean core AMR | Mean accessory AMR |
|---|---:|---:|
| Soil | 57.1% | 42.9% |
| Aquatic | 54.4% | 45.6% |
| Host-associated | 49.7% | 50.3% |
| Other environmental | 40.4% | 59.6% |
| Clinical | 32.4% | 67.6% |
| Human gut | 19.7% | 80.3% |

The environment effect on core AMR percentage was significant (Kruskal–Wallis H = 506.0, p = 4×10⁻¹⁰⁷, η² = 0.036). The report interprets core resistance as primarily chromosomal or intrinsic and accessory resistance as more mobile or acquired, while noting that these labels depend on genome sampling and a 95% prevalence threshold.

### 3. Resistance mechanisms differ by environment

All four classified mechanisms showed significant environment-dependent composition after BH-FDR correction. The strongest effects were for metal resistance (η² = 0.107) and target modification (η² = 0.100).

- **Metal resistance** accounted for 45.0% of aquatic AMR and 44.0% of soil AMR, but only 6.1% of human-gut AMR.
- **Target modification** accounted for 43.6% of human-gut AMR and 27.5% of clinical AMR, but only 6.2% of aquatic AMR.
- **Enzymatic inactivation** was broadly distributed, ranging from 24.1% in human gut to 44.1% in host-associated species.
- **Efflux** showed a smaller but significant environment effect, ranging from 1.1% in aquatic species to 7.0% in human-gut species.

These data support the hypothesis that ecological niches select different resistance strategies. Natural environments are associated with metal-resistance-heavy profiles, while clinical and gut environments are associated with target modification and, to a lesser extent, efflux. The report connects this pattern to the AMR fitness-cost project, proposing that mechanism-specific conservation and accessory status may partly reflect ecological use and selection.

### 4. Clinical exposure predicts AMR within species

The within-species analysis is a species-level proxy rather than a true per-genome comparison. Among 823 multi-environment species, the fraction of genomes from clinical sources correlated with total AMR cluster count (Spearman rho = 0.465, p = 2.2×10⁻⁴⁵).

Species dominated by clinical genomes carried a mean of **72.9 AMR clusters**, compared with **16.4** in environmentally dominated species, a 4.4-fold difference (MWU p = 2×10⁻¹⁸). Clinical-dominated species also had a higher grouped accessory fraction (**93.6% vs 81.7%**, MWU p = 0.004), although the continuous correlation between clinical fraction and accessory percentage was borderline (rho = 0.065, p = 0.064).

Deeply sampled examples included:

| Species | Genomes | AMR clusters | Core | Accessory | Dominant environment |
|---|---:|---:|---:|---:|---|
| *Klebsiella pneumoniae* | 13,637 | 1,115 | 7 | 1,108 (99%) | Clinical (80%) |
| *Staphylococcus aureus* | 13,274 | 642 | 9 | 633 (99%) | Clinical (85%) |
| *Salmonella enterica* | 10,097 | 836 | 11 | 825 (99%) | Host-associated (31%) |
| *Streptococcus pneumoniae* | 7,944 | 59 | 1 | 58 (98%) | Clinical (99.6%) |
| *Mycobacterium tuberculosis* | 6,673 | 44 | 4 | 40 (91%) | Clinical (98%) |

*K. pneumoniae* was especially extreme: only 7 of its 1,115 AMR clusters were core, indicating extensive accessory variation consistent with horizontal gene transfer in clinical settings.

### 5. Environment effects persist after phylogenetic control

Environment-AMR associations remained detectable within major taxonomic groups. Five of six tested phyla showed significant within-phylum effects; only Chloroflexota was non-significant. Bacteroidota had the largest within-phylum effect (η² = 0.130).

At the family level, 20 of 141 testable families showed significant environment effects after FDR correction. The strongest results included Enterobacteriaceae (q = 3×10⁻²¹), Bacteroidaceae (q = 1.3×10⁻¹⁷), Lachnospiraceae (q = 2.5×10⁻¹²), and Pseudomonadaceae (q = 3.9×10⁻¹²). These results support ecology as an influence beyond phylogenetic composition, although limited environmental coverage prevents testing in most families.

### 6. Continuous environmental embeddings corroborate discrete patterns

Among 2,659 species with both AMR data and [[entities/alphaearth-environmental-embeddings]], 52 of 64 embedding dimensions correlated significantly with AMR diversity after FDR correction. The strongest was dimension A34 (rho = +0.24). A Mantel test found a relationship between environmental distance and AMR mechanism-profile distance (r = 0.098, p = 0.001).

The association was strongest among clinical species (r = 0.177), intermediate in soil species (r = 0.129), and weakest in aquatic species (r = 0.061). Because the embedding dimensions are opaque and cover only 28% of genomes, this analysis provides confirmation but limited mechanistic interpretation.

## Interpretation

The report argues that clinical and human-gut resistomes are enriched in recently acquired, accessory AMR, while soil and aquatic resistomes retain a larger intrinsic or core component. Mechanism composition provides a possible ecological explanation: metal resistance dominates natural-environment profiles, whereas target modification and efflux are more prominent in antibiotic-exposed host-associated settings.

The findings are consistent with prior work on ecology-structured resistomes, soil-resistome phylogenetic structure, shared soil and clinical resistance genes, and the distinction between core and rare resistomes. However, the report emphasizes that the analyses establish association rather than causality. Clinical sampling bias, phylogenetic-environment entanglement, incomplete AMR annotation, and uneven genome counts may all contribute to the observed gradients.

## Limitations

1. Environment and phylogeny remain deeply confounded; many families lack sufficient representation across environments.
2. NCBI sampling overrepresents clinical isolates and may inflate the apparent clinical AMR burden.
3. Majority-vote species classifications collapse important within-species environmental variation.
4. Bakta/[[entities/amrfinderplus]]-based annotation may detect known clinical resistance more effectively than novel environmental resistance.
5. Core/accessory status is sensitive to genome count and the 95% prevalence threshold.
6. The observational design cannot distinguish antibiotic selection from reverse causality or co-selection with clinical traits.
7. Effect sizes are modest despite extremely small p-values, with η² values of 0.02–0.13.
8. Unclassified mechanisms account for 18.7% of AMR clusters and may be non-randomly distributed.
9. Planned PCoA, PERMANOVA, environment-specific gene identification, MAG/isolate comparisons, and archaeal analyses were not performed.
10. The within-species analysis uses species-level clinical dominance rather than the originally planned per-genome test.

## Future directions

- Identify AMR clusters shared between soil and clinical species as candidates for cross-niche horizontal transfer.
- Analyze temporal genome series from species such as *S. aureus* and *K. pneumoniae* to test changes in accessory AMR.
- Combine environmental profiles with the AMR fitness-cost project to test whether clinically enriched mechanisms are more costly or more evolutionarily optimized.
- Validate species-level predictions against NMDC metagenomes and community-level AMR profiles.
- Add plasmid, transposon, and integrative-element context using future mobile-element data.
- Perform environment-specific gene tests and ordination/PERMANOVA to determine which individual clusters drive ecological separation.

## Supporting materials

Key notebooks are `01_data_extraction.ipynb`, `02_resistome_vs_environment.ipynb`, `03_within_species.ipynb`, and `04_alphaearth_analysis.ipynb`. Generated tables include species AMR profiles, genome and species environment classifications, pairwise environment comparisons, mechanism tests, stratified phylogenetic results, within-species results, and AlphaEarth correlations.

## Related Concepts
- [[concepts/pangenome-integration]]
- [[concepts/annotation-gap]]
- [[concepts/organism-specificity]]
- [[concepts/condition-dependent-essentiality]]

## Entities
- [[entities/klebsiella-pneumoniae]]
- [[entities/staphylococcus-aureus]]
- [[entities/salmonella-enterica]]
- [[entities/streptococcus-pneumoniae]]
- [[entities/mycobacterium-tuberculosis]]
- [[entities/berdl]]
- [[entities/gtdb]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/fitness-browser]]
- [[entities/kegg]]
