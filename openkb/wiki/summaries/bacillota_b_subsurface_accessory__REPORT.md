---
type: "Summary"
description: "Deep-clay Bacillota_B show gene-content expansion and enriched anaerobic functions."
doc_type: short
full_text: "sources/bacillota_b_subsurface_accessory__REPORT.md"
---

# Subsurface Bacillota_B Specialization

## Overview

This report compares 10 deep-clay Bacillota_B genomes with 62 soil-baseline Bacillota_B genomes to identify accessory-genome features associated with deep subsurface specialization. It finds strong enrichment of anaerobic-respiration and survival functions, substantial genome expansion rather than streamlining, and a methodological correction that removes the apparent shallow-clay iron-reduction advantage. The report informs [[concepts/subsurface-microbial-specialization]], [[concepts/genome-expansion-versus-streamlining]], [[concepts/pangenome-integration]], and [[concepts/multi-heme-cytochrome-detection]].

## Cohort and analytical design

The deep-clay anchor contained 10 Bacillota_B genomes from [[entities/mont-terri]] Opalinus Clay and bentonite, Mont Terri rock-porewater samples, and the Russian Beyelii Yar borehole. The 62-genome baseline comprised phylum-matched soil and sediment Bacillota_B, while the full Bacillota_B universe contained 334 genomes. Analyses used Firmicutes-level eggNOG orthologous groups, with bacterial or root-level fallbacks where necessary, and controlled for genome completeness using CheckM.

## Key findings

### 1. Broad accessory-genome enrichment

A total of 547 eggNOG OGs were significantly enriched in the deep-clay anchor under per-OG Fisher tests with BH-FDR correction, fold-difference of at least 3, and at least 3 anchor genomes carrying each OG. Only 27 OGs were depleted. The enriched set greatly exceeded the preregistered expectation of at least 10 OGs.

The keyword-defined categories included 42 anaerobic-respiration OGs, 24 sporulation or revival OGs, 12 mineral-attachment or extracellular-polymeric-substance OGs, 4 anaerobic-regulator OGs, and 3 osmoadaptation OGs. The remaining 462 OGs were classified as other or unannotated, but manual inspection showed that this category concealed additional anaerobic-niche signals. Examples included molybdopterin-cofactor metabolism, DsrE/DsrF/DsrH-like sulfite-handling proteins, 2-oxoglutarate:ferredoxin oxidoreductase, and a major facilitator superfamily transporter.

The combined result supports a strong association between deep-clay Bacillota_B and expanded capacities for anaerobic electron transfer, respiratory flexibility, sporulation and revival, mineral attachment, regulation, and osmotic adaptation. The functional categorization remains provisional because keyword scanning underestimates domain- and gene-family-level signals.

### 2. Deep-clay genomes are larger, not streamlined

Deep-clay genomes averaged 4,110,038 bp compared with 3,046,124 bp in the soil baseline, with Cohen's *d* = +1.39 and Mann–Whitney *p* = 0.025. CheckM-rescaled sizes were 4,323,230 bp versus 3,233,715 bp, with *d* = +1.37 and *p* = 0.013. Mean eggNOG OG counts were 2,630 versus 2,106, and CheckM-rescaled counts were 2,771 versus 2,233; all comparisons had large effect sizes and significant Mann–Whitney tests.

Mean completeness was nearly identical between groups, 94.7% for the anchor and 94.3% for the baseline, indicating that the size difference is unlikely to be a MAG-quality artefact. The report therefore rejects the preregistered hypothesis that deep-clay Bacillota_B would be more compact. Instead, the data support gene-content expansion and are consistent with a self-sufficiency strategy in free-living subsurface Firmicutes.

This result contrasts with the streamlining reported for Patescibacteria/CPR, but the comparison involves different phyla and lifestyles: Patescibacteria include episymbiotic lineages, whereas the Bacillota_B examined here are cultivable or free-living anaerobic subsurface organisms. The report interprets the contrast as evidence that “subsurface adaptation” is not a single genome-size strategy, consistent with [[concepts/genome-expansion-versus-streamlining]].

### 3. Correction of the clay-project iron-reduction analysis

The earlier `clay_confined_subsurface` analysis used K07811, K17324, and K17323 as iron-reduction markers, although these correspond to TMAO reductase and glycerol transport functions rather than canonical Geobacter or Shewanella multi-heme cytochromes. The report reanalyzed the cohort using PFAM PF02085, PFAM PF22678, and a sequence-based CXXCH motif count of at least four in gene-cluster protein sequences, following the [[concepts/multi-heme-cytochrome-detection]] approach.

Corrected multi-heme-cytochrome-positive rates were 55.6% for deep clay (5/9), 40.0% for shallow clay (12/30), and 40.9% for soil baseline (61/149). No pairwise comparison was significant; corrected Fisher-test *p* values were at least 0.46. Thus, the former shallow-greater-than-deep iron-reduction pattern was an artefact of mismatched markers, and the iron-reduction portion of the clay-project narrative loses statistical support.

The sulfur-reduction side of the earlier H3 result remains supported: 5/9 deep-clay genomes carried the specified sulfur-reduction markers compared with a reported Mitzscherling rock-attached null rate of 0.2%, with binomial *p* = 4×10⁻¹². The report therefore characterizes the original porewater-bias interpretation as half-supported: robust for sulfur reduction, unsupported for the corrected iron-reduction comparison.

## Interpretation and significance

The 547 enriched OGs provide a target list for biochemical characterization, cultivation, and fitness experiments. Their distribution supports the hypothesis that deep-clay Bacillota_B rely on broader anaerobic respiratory repertoires and greater metabolic self-sufficiency rather than extreme genome reduction. The finding is compatible with prior observations of subsurface Firmicutes containing versatile respiratory systems, sporulation capacity, and complete carbon, nitrogen, and amino-acid biosynthesis pathways.

The report also contributes a reusable methodological pattern: when KEGG assignments are unreliable or lack canonical markers for extracellular electron transfer, multi-heme cytochrome detection can combine curated PFAM domains with CXXCH motif scanning. This approach is intended for broader pangenome analyses of iron reduction and extracellular electron transfer.

## Limitations

The anchor cohort is small and taxonomically clumped, so some enriched OGs may be lineage-specific rather than general deep-clay adaptations. The anchor is also dominated by borehole and porewater genomes and cannot test whether rock-attached Bacillota_B differ from porewater lineages. Hierarchical eggNOG assignments and root-level fallbacks reduce functional and phylogenetic resolution. Finally, the keyword-based annotation undercounts anaerobic-respiration and electron-transfer functions, and the corrected iron-reduction analysis represents a Phase 1 marker correction rather than a complete reassessment of the former clay-project narrative.

## Recommended follow-up

1. Apply the corrected multi-heme-cytochrome analysis to the `clay_confined_subsurface` branch and amend its report.
2. Reclassify the 462 “other/unannotated” enriched OGs using domain-aware or LLM-assisted annotation.
3. Decompose the enrichment signal by genus and expand the anchor with additional clay-isolated Bacillota_B.
4. Partition the approximately 1 Mbp of additional anchor DNA among respiration, sporulation, mobile elements, regulation, and other functions.
5. Apply the same within-phylum enrichment workflow to deep-clay Bacteroidota, Pseudomonadota, and Acidobacteriota.

## Source

Primary source: `bacillota_b_subsurface_accessory__REPORT`.

## Related Concepts
- [[concepts/annotation-gap]]
- [[concepts/metabolic-support-networks]]
- [[concepts/condition-dependent-essentiality]]

## Entities
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/uniprot]]
