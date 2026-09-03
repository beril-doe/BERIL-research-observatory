---
type: "Concept"
sources: ["summaries/soil_frontier_genomics__REPORT.md", "summaries/pitfalls.md", "summaries/metal_resistance_global_biogeography__REPORT.md"]
description: "Missing sample coordinates create geographic blind spots in global microbial analyses."
---

# Geospatial Coverage Gaps

## Definition

Geospatial coverage gaps are missing or unusable geographic coordinates in environmental microbiology datasets, limiting the ability to infer spatial distributions, compare regions, and distinguish biological patterns from uneven sampling. [src: metal_resistance_global_biogeography]

## Evidence from the Global Metal-Resistance Dataset

The global metal-resistance analysis extracted 260,652 environmental MAGs from MGnify and retained 30,497 MAGs after filtering host-associated biomes. [src: metal_resistance_global_biogeography] Of these, 22,356 MAGs had usable geospatial coordinates, corresponding to 73.3% coordinate coverage of the environmental MAG set. [src: metal_resistance_global_biogeography]

An independent ENA batch retrieval returned 24,511 sample records, but only 16,964 records (69.2%) contained valid latitude/longitude pairs. [src: metal_resistance_global_biogeography] The resulting 30.8% per-sample spatial data gap means that a substantial fraction of publicly archived metagenomic samples cannot be placed reliably on a global map. [src: metal_resistance_global_biogeography]

The gap is not equivalent to unrepresented geographic regions. The ENA coordinate file covered all 532 grid cells represented in the MAG coordinate dataset; therefore, the observed deficit reflects samples without coordinates rather than grid cells with no samples. [src: metal_resistance_global_biogeography] This distinction is important for [[concepts/spatial-sampling-effort]] and [[concepts/coverage-limited-inference]]: apparent geographic coverage can coexist with substantial record-level missingness.

## Analytical Consequences

Missing coordinates can produce geographic blind spots and make regional prevalence estimates sensitive to which samples happen to include location metadata. [src: metal_resistance_global_biogeography] The report therefore treats global maps of environmental metal resistance as subject to substantial spatial-data limitations rather than as unbiased representations of worldwide biology. [src: metal_resistance_global_biogeography]

In the georeferenced MAG set, 2.8% of 22,356 MAGs carried at least one metal-resistance type. [src: metal_resistance_global_biogeography] This prevalence estimate applies specifically to the coordinate-resolved dataset and should not automatically be generalized to all environmental MAGs. [src: metal_resistance_global_biogeography]

The analysis identified 11 significant 5° grid hotspots and 3 coldspots among 289 cells containing at least five MAGs. [src: metal_resistance_global_biogeography] The strongest candidate hotspot was the Atacama/Andean region of Chile, with 21.8% prevalence, OR=9.83, q=7.6e-12, and 101 MAGs. [src: metal_resistance_global_biogeography] Eastern and central USA clusters had OR values of 7.9 and 6.3, while an East/Southeast Asia cluster had OR values ranging from 4.4 to 5.9. [src: metal_resistance_global_biogeography]

These hotspots are not yet established as geographically general biological patterns because expedition-level clustering and sampling-effort correction remain pending. [src: metal_resistance_global_biogeography] This is an instance of [[concepts/phylogenetic-confounding]]-like inferential risk in which structured data collection, rather than the target biological feature itself, may explain an apparent pattern; here, the relevant structure is study and sampling geography rather than phylogeny. [src: metal_resistance_global_biogeography]

## Relationship to Biome Representation

The report found 5.8% metal-resistance prevalence in 7,939 soil MAGs (OR=5.05, q=1.8e-82), 1.9% in 422 rhizosphere MAGs (OR=0.66, q=0.30), and 1.2% in 13,995 marine MAGs (OR=0.20, q=9.2e-80). [src: metal_resistance_global_biogeography] These differences show why missing-coordinate patterns should be assessed by biome: if coordinate availability is associated with biome, geographic analyses may also inherit biome-specific representation bias. [src: metal_resistance_global_biogeography]

The source report does not determine which biomes are most underrepresented among samples lacking coordinates. [src: metal_resistance_global_biogeography] Consequently, biome-level prevalence contrasts should be interpreted alongside [[concepts/cultivation-bias]] and [[concepts/environmental-occupancy-vs-activity]], which address other ways that available environmental datasets can misrepresent ecological distributions or biological activity.

## Evidence Strength and Scope

The coordinate-gap measurements are direct data-quality results from record retrieval and coordinate filtering. [src: metal_resistance_global_biogeography] The conclusion that missing coordinates create global geographic blind spots is a strong methodological inference from those measurements. [src: metal_resistance_global_biogeography] In contrast, biological interpretations of regional hotspots are provisional because the report has not yet completed expedition clustering checks or sampling-effort normalization. [src: metal_resistance_global_biogeography]

## Open Directions

- Compare coordinate availability by biome, expedition, study, and sample-accession prefix to identify which sources contribute most to the 30.8% missing-coordinate rate. [src: metal_resistance_global_biogeography]
- Recalculate hotspot prevalence after normalizing by log(n_MAGs), testing whether the Atacama, USA, and East/Southeast Asia signals persist after accounting for sampling effort. [src: metal_resistance_global_biogeography]
- Test whether hotspot MAGs come from multiple independent expeditions and accession-prefix groups rather than single-study clusters. [src: metal_resistance_global_biogeography]
- Compare coordinate-resolved and coordinate-missing samples by biome and resistance status to assess whether missingness could bias the 2.8% global prevalence estimate. [src: metal_resistance_global_biogeography]
- Complete the production mapping workflow after fixing the missing `matplotlib.pyplot` import, then report uncertainty and sample counts alongside geographic prevalence. [src: metal_resistance_global_biogeography]

## Related Source

[[summaries/metal_resistance_global_biogeography__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/soil_frontier_genomics__REPORT]]