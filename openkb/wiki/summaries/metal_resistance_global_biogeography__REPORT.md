---
type: "Summary"
description: "Global map of environmental MAG metal resistance and its spatial data gaps"
doc_type: short
full_text: "sources/metal_resistance_global_biogeography__REPORT.md"
---

# Global Biogeography of Environmental Bacterial Metal Resistance

## Status

Preliminary analysis is complete through NB02; production figures and several robustness checks remain pending. The study extracts environmental metagenome-assembled genomes (MAGs), links them to geospatial coordinates, and evaluates global patterns of bacterial metal resistance. It contributes to the cross-document topics [[concepts/environmental-metal-tolerance]], [[concepts/geospatial-coverage-gaps]], and [[concepts/spatial-sampling-effort]].

## Dataset and Coordinate Coverage

- 260,652 environmental MAGs were extracted from [[entities/mgnify]]; filtering to host-associated biomes reduced the set to 30,497 MAGs. [src: metal_resistance_global_biogeography]
- 22,356 MAGs had usable geospatial coordinates, representing 73.3% coordinate coverage of the environmental MAG set. [src: metal_resistance_global_biogeography]
- ENA batch retrieval returned 24,511 sample records, of which 16,964 (69.2%) had valid latitude/longitude pairs; thus, 30.8% of records lacked usable coordinates. [src: metal_resistance_global_biogeography]
- The coordinate deficit is a per-sample data-quality gap rather than a geographic gap: all 532 MAG grid cells were covered by the [[entities/european-nucleotide-archive]] coordinate file. [src: metal_resistance_global_biogeography]

The missing-coordinate rate creates substantial geographic blind spots for global analyses based on public metagenomic archives. Which biomes are most underrepresented remains unresolved. [src: metal_resistance_global_biogeography]

## Global Metal-Resistance Prevalence

Among the 22,356 MAGs with coordinates, 2.8% carried at least one metal-resistance type. This is substantially lower than the prevalence implied by the broader 30,497-MAG filtered set and indicates that metal resistance is rare in the globally georeferenced environmental MAG pool. [src: metal_resistance_global_biogeography]

The result also distinguishes metal-resistance genes identified by [[entities/amrfinderplus]] from type IV secretion system (T4SS) machinery: the report notes that the 2.8% metal-resistance prevalence is much lower than the previously reported 21.8% T4SS prevalence, supporting the interpretation that these are distinct features that are not uniformly co-distributed. [src: metal_resistance_global_biogeography]

## Spatial Hotspots and Coldspots

A 5° grid analysis included 289 cells with at least five MAGs. Fisher’s exact tests with Benjamini–Hochberg false-discovery-rate correction identified 11 significant hotspots with odds ratios above 2 and 3 significant coldspots with odds ratios below 0.5. [src: metal_resistance_global_biogeography]

- The strongest hotspot was in the [[entities/atacama-desert]]/Andean region of Chile (latitude −25°, longitude −70°), where prevalence was 21.8%, OR=9.83, q=7.6e-12, across 101 MAGs. [src: metal_resistance_global_biogeography]
- Eastern and central USA clusters at approximately longitude −80° and −90° had OR values of 7.9 and 6.3. [src: metal_resistance_global_biogeography]
- An East/Southeast Asia cluster spanning approximately 25–30°N and 105–120°E had OR values from 4.4 to 5.9. [src: metal_resistance_global_biogeography]

These regional signals are preliminary because expedition-level clustering and sampling-effort correction have not yet been completed. The report therefore treats hotspot locations as candidates for validation rather than definitive global biogeographic patterns. [src: metal_resistance_global_biogeography]

## Biome Differences

Prevalence differed strongly among georeferenced biomes, using Fisher’s exact tests against the global baseline with BH correction: [src: metal_resistance_global_biogeography]

| Biome | MAGs | Prevalence | OR | q |
|---|---:|---:|---:|---:|
| Soil | 7,939 | 5.8% | 5.05 | 1.8e-82 |
| Rhizosphere | 422 | 1.9% | 0.66 | 0.30 (NS) |
| Marine | 13,995 | 1.2% | 0.20 | 9.2e-80 |

Soil is significantly enriched for metal resistance, while marine samples are significantly depleted relative to the global baseline. The rhizosphere estimate is not statistically distinguishable from the baseline in this analysis. [src: metal_resistance_global_biogeography]

## Limitations and Pending Work

1. Test whether the Atacama and USA hotspots are driven by single expeditions or studies by examining distinct `sample_accession` prefixes within each hotspot. [src: metal_resistance_global_biogeography]
2. Normalize hotspot analyses by `log(n_MAGs)` to determine whether the regional signals persist after accounting for sampling effort. [src: metal_resistance_global_biogeography]
3. Fix the missing `import matplotlib.pyplot as plt` statement in the NB01 map cell before producing the final global figure. [src: metal_resistance_global_biogeography]
4. Complete NB03 production figures, including `fig_nb02_global_hotspot_map.png` and `fig_nb02_biome_prevalence.png`. [src: metal_resistance_global_biogeography]

## Main Contribution

This report establishes a globally georeferenced environmental MAG framework for testing bacterial metal-resistance biogeography. Its strongest results are the quantified 30.8% per-sample coordinate gap, the low overall prevalence of metal resistance (2.8%), significant soil enrichment and marine depletion, and a set of geographically localized candidate hotspots. The findings support further analysis but do not yet establish that the hotspots reflect geographically general biological patterns rather than study clustering or uneven sampling. [src: metal_resistance_global_biogeography]

## Related Concepts
- [[concepts/geographic-distance-decay]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/cultivation-bias]]
- [[concepts/evidence-triangulation]]
- [[concepts/organism-specificity]]

## Entities
- [[entities/metal-fitness-atlas]]
- [[entities/berdl]]
- [[entities/gtdb]]
- [[entities/kegg]]
