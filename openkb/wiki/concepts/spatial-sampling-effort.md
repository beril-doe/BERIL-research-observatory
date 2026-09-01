---
type: "Concept"
sources: ["summaries/t4ss_cazy_environmental_hgt__REPORT.md", "summaries/pitfalls.md", "summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/metal_resistance_global_biogeography__REPORT.md"]
description: "How uneven sampling effort shapes spatial inference from environmental MAGs"
---

# Spatial Sampling Effort

Spatial sampling effort is the uneven distribution of observations across locations, biomes, and studies that can bias geographic comparisons of microbial traits. In environmental metagenomic analyses, it must be distinguished from the availability of geographic coordinates: a location may have coordinate coverage while still being represented by very different numbers of MAGs or samples. This concept connects to [[concepts/geospatial-coverage-gaps]], [[concepts/coverage-limited-inference]], and [[concepts/environmental-resistome]].

## Evidence from Global Metal-Resistance Mapping

The global metal-resistance analysis began with 260,652 environmental MAGs extracted from MGnify and retained 30,497 MAGs after filtering host-associated biomes. Of these, 22,356 had usable geospatial coordinates. [src: metal_resistance_global_biogeography]

The associated ENA retrieval contained 24,511 sample records, but only 16,964 (69.2%) had valid latitude/longitude pairs, leaving a 30.8% per-sample spatial data gap. [src: metal_resistance_global_biogeography] This gap is a data-quality limitation on global mapping, but it did not correspond to unsampled geographic grid cells: all 532 MAG grid cells had ENA coordinate coverage. [src: metal_resistance_global_biogeography]

The distinction matters because coordinate completeness does not establish equal sampling effort. A grid cell can be represented in the archive while having few MAGs, while another cell may be strongly represented by one or several studies. Consequently, apparent regional enrichment may reflect where sampling occurred, how intensively locations were sampled, or study-level clustering rather than a general geographic pattern. This is an inferential warning supported by the report's pending validation requirements, not a demonstrated explanation for any specific hotspot. [src: metal_resistance_global_biogeography]

## Sampling Effort and Hotspot Interpretation

Among the 22,356 MAGs with coordinates, 2.8% carried at least one metal-resistance type. [src: metal_resistance_global_biogeography] A 5° grid analysis included 289 cells with at least five MAGs and identified 11 significant hotspots and 3 significant coldspots using Fisher's exact tests with Benjamini–Hochberg correction. [src: metal_resistance_global_biogeography]

The strongest candidate hotspot was the Atacama/Andean region of Chile, at approximately latitude −25° and longitude −70°, with 21.8% prevalence, OR=9.83, q=7.6e-12, and 101 MAGs. [src: metal_resistance_global_biogeography] Additional clusters occurred in the eastern and central USA, with OR values of 7.9 and 6.3, and in East/Southeast Asia, with OR values from 4.4 to 5.9. [src: metal_resistance_global_biogeography]

These results are statistically supported candidate spatial patterns, but they are not yet sampling-effort-corrected biological generalizations. [src: metal_resistance_global_biogeography] The planned correction is to test whether hotspots persist after normalization by log(n_MAGs), directly addressing the possibility that observation intensity contributes to the signal. [src: metal_resistance_global_biogeography] A separate expedition-level clustering analysis will examine whether the Atacama and USA patterns are driven by single studies, using distinct sample-accession prefixes within each hotspot. [src: metal_resistance_global_biogeography]

## Biome-Level Sampling Considerations

Metal-resistance prevalence differed among the sampled biomes: soil contained 7,939 MAGs with 5.8% prevalence, OR=5.05, and q=1.8e-82; rhizosphere contained 422 MAGs with 1.9% prevalence, OR=0.66, and q=0.30; and marine samples contained 13,995 MAGs with 1.2% prevalence, OR=0.20, and q=9.2e-80. [src: metal_resistance_global_biogeography]

The strong soil enrichment and marine depletion are evidence of differences in the observed dataset, but interpreting them as unbiased biome-wide prevalence requires consideration of sampling intensity and archive composition. The report establishes the statistical contrasts but leaves the extent of biome-specific sampling bias as an open question. [src: metal_resistance_global_biogeography]

## Analytical Implications

- Require minimum observation thresholds for spatial comparisons; the reported grid analysis used cells with at least five MAGs. [src: metal_resistance_global_biogeography]
- Separate coordinate availability from sampling intensity, because all represented grid cells had ENA coverage despite the 30.8% per-sample coordinate gap. [src: metal_resistance_global_biogeography]
- Test study or expedition clustering before assigning biological meaning to regional hotspots. [src: metal_resistance_global_biogeography]
- Normalize or model sampling effort, including a planned log(n_MAGs) correction, before treating geographic enrichment as robust. [src: metal_resistance_global_biogeography]
- Report archive blind spots explicitly, especially because the report does not yet identify which biomes are most underrepresented among samples lacking coordinates. [src: metal_resistance_global_biogeography]

## Related Source

The complete analysis, including coordinate retrieval, hotspot statistics, biome comparisons, and pending sampling-effort checks, is summarized in [[summaries/metal_resistance_global_biogeography__REPORT]].

## Open Directions

- Apply the planned log(n_MAGs) sampling-effort correction and test whether the 11 hotspots and 3 coldspots remain significant. [src: metal_resistance_global_biogeography]
- Compare sample-accession prefixes within the Atacama and USA hotspot cells to determine whether signals are expedition-level artefacts. [src: metal_resistance_global_biogeography]
- Quantify coordinate-missingness by biome and archive source to identify which environments contribute most to the 30.8% per-sample gap. [src: metal_resistance_global_biogeography]

See also: [[summaries/microbeatlas_metal_ecology__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/t4ss_cazy_environmental_hgt__REPORT]]