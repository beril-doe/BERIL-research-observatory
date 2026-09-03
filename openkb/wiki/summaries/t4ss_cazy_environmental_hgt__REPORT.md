---
type: "Summary"
description: "Environmental T4SS links GT2 transfer, CAZy diversity, and metal resistance"
doc_type: short
full_text: "sources/t4ss_cazy_environmental_hgt__REPORT.md"
---

# T4SS-CAZy Environmental HGT

## Overview

This preliminary report investigates whether [[entities/type-iv-secretion-system]] (T4SS) machinery is associated with horizontal transfer of [[entities/cazy]] genes in environmental metagenome-assembled genomes (MAGs). Core analyses are complete; threshold validation and manuscript figures remain pending. [src: t4ss_cazy_environmental_hgt]

The findings contribute to the cross-document themes of [[concepts/horizontal-gene-transfer]], [[concepts/gene-neighborhood-inference]], [[concepts/mobile-genetic-elements]], and [[concepts/metal-resistance-breadth]].

## Key Findings

- T4SS or conjugative machinery was detected in 6,652 of 30,497 high-quality environmental MAGs (21.8%), using a multi-marker definition including VirB4/6/8/9/10/11, VirD4, TraI/D, TrwB, and TraG. [src: t4ss_cazy_environmental_hgt]
- Ninety-two CAZy families showed elevated co-occurrence with T4SS loci within 10 kb, although the distance threshold still requires validation. [[entities/gt2-glycosyltransferases]] were the strongest hit, occurring in 767 genomes with an average locus distance of 5,041 bp. [src: t4ss_cazy_environmental_hgt]
- T4SS–CAZy associations were enriched in marine sediment (OR=5.5, q<10⁻⁹⁸), barley rhizosphere (OR=10.4), and maize rhizosphere (OR=4.1). [src: t4ss_cazy_environmental_hgt]
- A GT2 gene-tree analysis detected 77 HGT events, including 32 high-confidence normalized cross-phylum events. Node_4915 was the strongest case, spanning eight phyla with a maximum divergence of 4.843. [src: t4ss_cazy_environmental_hgt]
- [[entities/icefinder]] found no evidence that the CAZy genes were plasmid-borne; only 12 integrative mobilizable elements (IMEs) appeared among the top 100 accumulators. T4SS-positive genomes nevertheless had 10× higher mobile genetic element density than other genomes (p<0.001), supporting chromosomal or integrative transfer through IMEs or ICEs rather than plasmid carriage. [src: t4ss_cazy_environmental_hgt]
- A 70/30 discovery/validation split reproduced the enrichment patterns, supporting their robustness. [src: t4ss_cazy_environmental_hgt]

## HGT Characterisation

Among the 77 detected events, 65 spanned two phyla and 12 spanned at least three phyla (15.6%). Node_4915 contained 35 genes, 82.9% synteny, and representatives from WOR-3, Desulfobacterota, Patescibacteria, Bacteroidota, Firmicutes_A, Methanobacteriota, Bdellovibrionota, and Acidobacteriota. [src: t4ss_cazy_environmental_hgt]

Divergence and synteny were negatively correlated (Spearman ρ = −0.615, p<0.001): more phylogenetically distant events had lower syntenic percentages, which is consistent with sequence divergence after transfer. The phyla most frequently involved across all events were Firmicutes_A (27), Pseudomonadota (22), Bacillota_A (19), and Actinomycetota (10). [src: t4ss_cazy_environmental_hgt]

## GT2 Neighbourhoods and Metal Resistance

In 376 GT2-associated genomes, list-format neighbourhood parsing identified T4SS in 503 neighbourhood entries and GT2 in 495, confirming contig-level co-localisation. [[entities/gh23-murein-lytic-transglycosylases]], a murein lytic transglycosylase, was the second most common CAZy family in GT2 neighbourhoods, with 106 occurrences, suggesting clustering of cell-wall-remodelling functions with GT2–T4SS loci. [src: t4ss_cazy_environmental_hgt]

GT2-neighbourhood MAGs had a mean of 0.045 metal-resistance types, compared with 0.004 in 260,276 non-GT2 MAGs (Mann–Whitney p=8.6e-27). The report characterises this as an 11× enrichment of metal-resistance genes in genomes carrying GT2 within T4SS-proximal neighbourhoods. This independently supports a possible connection between CAZy–T4SS transfer hubs and the metal-resistance niche-breadth hypothesis, but the association remains observational. [src: t4ss_cazy_environmental_hgt]

## Interpretation and Evidence Limits

The co-localisation of T4SS machinery with GT2 glycosyltransferase cassettes, together with GT2 phylogenetic incongruence, provides positive evidence for 32 cross-phylum HGT events. The absence of plasmid-borne CAZy genes and elevated MGE density in T4SS-positive genomes is consistent with chromosomal or integrative transfer mechanisms. [src: t4ss_cazy_environmental_hgt]

The results support—but do not establish—the hypothesis that T4SS machinery mediates environmental dissemination of CAZy diversity across distant bacterial lineages. All associations are observational, and mechanistic confirmation requires experimental validation. [src: t4ss_cazy_environmental_hgt]

## Pending Validation

1. Run a synteny-threshold permutation test using unfiltered Spark data.
2. Validate Node_4915 with BLAST against NCBI nr.
3. Establish a housekeeping-gene null baseline.
4. Factorise biome enrichment using θ = OR(T4SS-CAZy) / [OR(T4SS) × OR(CAZy)].

## Figures

- `figures/fig_nb05_hgt_scatter.png`
- `figures/fig_nb05_neighbourhood_functions.png`

## Related Concepts
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/organism-specificity]]
- [[concepts/spatial-sampling-effort]]
