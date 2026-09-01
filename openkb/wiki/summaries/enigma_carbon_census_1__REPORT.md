---
type: "Summary"
description: "Tiered census maps 83 compounds to callable taxa and an actionable organism-dark set."
doc_type: short
full_text: "sources/enigma_carbon_census_1__REPORT.md"
---

# ENIGMA Carbon Census — Summary

## Overview

The ENIGMA Carbon Census integrates compound identity resolution, pathway linkage, organism prediction, phylogenetic placement, field occurrence, and global environmental abundance for 83 enrichment compounds: 59 from SSO groundwater and 24 from necromass. Its principal contribution is an actionable map of [[concepts/resource-darkness]]: compounds not linkable to isolate-level utilization through the queried BERDL and curated resources. [src: enigma_carbon_census_1]

## Key Findings

- All 83 compounds were structure-resolved through PubChem, and 54 linked to KEGG. Only 9 were initially callable: 8 through ENIGMA-isolate predictions and lauric acid through a Tier-1 measured RB-TnSeq carbon-source experiment in a reference bacterium. Consequently, 74/83 compounds (89%) were organism-dark. [src: enigma_carbon_census_1]
- The dark fraction was similar by source—53/59 groundwater compounds (90%) and 21/24 necromass compounds (88%)—indicating that darkness is more closely associated with chemical class and annotation coverage than with sampling source. [src: enigma_carbon_census_1]
- The 74 dark compounds comprise 33 KEGG-linked compounds with no reaction in queried genomes, 29 fully orphan compounds with no KEGG link, 6 biosynthesis-known/catabolism-unknown compounds, and 6 compounds represented only by generic reactions. The biosynthesis-known group includes tyramine, guanidineacetic acid, cinnamic acid, caffeic acid, palmitic acid, and farnesol; these are candidates for MIBiG and literature review rather than immediate classification as true orphans. [src: enigma_carbon_census_1]
- Callable compounds cluster in pollutant-adjacent aromatic chemistry: salicylic acid, 3-hydroxybenzoic acid, 4-hydroxybenzaldehyde, phthalic acid, and terephthalic acid. Phenylethylamine and abscisic acid also received isolate calls. The apparent class gradient was directional but statistically unsupported: the χ² test for the 8 ENIGMA-isolate calls gave χ²=5.07, p=0.53 (df=6). [src: enigma_carbon_census_1]
- Xanthine was incorrectly included as a carbon-catabolic call because reaction R02107 represents purine nitrogen acquisition rather than carbon degradation. The effective carbon-callable set is therefore 8 rather than 9; the committed tables retain xanthine pending regeneration after the allowlist correction. [src: enigma_carbon_census_1]
- The callable aromatic compounds converge on the [[entities/beta-ketoadipate-pathway]] and related protocatechuate/catechol funnels. Phenylethylamine instead enters the [[entities/phenylacetyl-coa-pathway]] route. [src: enigma_carbon_census_1]

## Isolate and Phylogenetic Deliverables

The census produced 569 ENIGMA-isolate utilizer prediction rows across the 8 isolate-callable compounds. Salicylic acid, 3-hydroxybenzoic acid, and 4-hydroxybenzaldehyde had the largest prediction sets, with 129, 127, and 125 strains respectively. [src: enigma_carbon_census_1]

The phylogenetic deliverable contains 494 placements representing 359 distinct strains: 64 high-certainty placements, 387 medium-certainty Tier-2 placements, and 43 medium-certainty Tier-3 signature-enzyme placements. Utilizers are concentrated in Pseudomonadota and especially Burkholderiales, with compound-specific contributions from Pseudomonadales and Sphingomonadales. [src: enigma_carbon_census_1]

The callable phenotype is dominated by specialists: 675 genomes carry exactly one of the 8 scored capacities, whereas only 18 carry at least 3, with a maximum of 4. Generalists are concentrated in Paraburkholderia, Burkholderia, Hydrogenophaga, and related Burkholderiaceae. This supports phylogenetic specialization over a broadly portable catabolic-module model and relates to [[concepts/organism-specificity]]. [src: enigma_carbon_census_1]

## Co-occurrence and Source Tests

Broad cross-module modularity was not supported. Cross-block pairs had median Haldane-corrected odds ratio 2.28 but median Jaccard approximately 0; only 25 of 3109 genomes (0.8%) carried both an aromatic and a non-aromatic capacity. Phenylethylamine showed enrichment with 4-hydroxybenzaldehyde (OR 2.84, 95% CI 1.49–5.40, q=0.035) and phthalic acid (OR 3.37, 95% CI 1.46–7.75, q=0.071), but this is mechanistically consistent with phenylethylamine being an aromatic-derived substrate rather than evidence for independent module co-assembly. [src: enigma_carbon_census_1]

The groundwater-versus-necromass source hypothesis was untestable. Only two isolate-callable compounds were necromass-derived, both phthalate-class aromatics, making source inseparable from chemistry. The local field atlas instead found 62 implicated utilizer genera in the SSO field, with top aromatic-utilizer prevalences of approximately 0.7–0.9. [src: enigma_carbon_census_1]

## Environmental Atlas

The global atlas is a biome-occupancy proxy, not evidence of compound degradation or catabolic activity. In NMDC, 3825 taxonomy-bearing metagenomes were analyzed; 83 of 86 implicated genera were detected in 1719 metagenomes. Soil, freshwater, and periphyton patterns were biologically coherent, with Burkholderiales and Comamonadaceae especially prevalent in freshwater biofilms. [src: enigma_carbon_census_1]

Periphyton emerged as a distinct reservoir obscured by bulk freshwater labels: several Burkholderiales and Comamonadaceae genera reached approximately 96–97% prevalence with mean relative abundance around 0.005–0.009. Label-free abundance spikes were strongest in periphyton and soil, including Hydrogenophaga at 0.28 in epiphyton, Nocardioides at 0.43 in epipsammon, and Mycobacterium at 0.22 in soil. [src: enigma_carbon_census_1]

The marine contrast used 302 Planet Microbe runs. All 68 listed genera were detected, but most terrestrial/freshwater-associated genera occurred at roughly 1e-3 to 1e-4 abundance in open ocean; Alteromonas was a notable marine member at 0.048 in 240/302 runs. [src: enigma_carbon_census_1]

This distinction between organism occupancy and demonstrated function is central to [[concepts/environmental-occupancy-vs-activity]]. [src: enigma_carbon_census_1]

## Physicochemical and Annotation-Coverage Result

Callable compounds were smaller and structurally simpler than dark compounds, with median Complexity 133 versus 207 (uncorrected Mann–Whitney p=0.034), MolecularWeight 152 versus 179 (p=0.066), and HeavyAtomCount 11 versus 13 (p=0.057). With only 9 initial callable compounds, these are directional observations. The pattern likely reflects both biological accessibility and an [[concepts/annotation-gap]]: simple, common aromatic pollutants are better represented in KEGG, ModelSEED, and genome annotations. [src: enigma_carbon_census_1]

## Operational Implications

1. Prioritize the 29 fully orphan compounds—especially necromass-heavy alkaloids and terpenoids—for anonymous community enrichment, metagenomics, and genetic characterization. [src: enigma_carbon_census_1]
2. Treat the 6 biosynthesis-known compounds as a separate literature and MIBiG-consult track before wet-lab prioritization. [src: enigma_carbon_census_1]
3. Apply PaperBLAST and abstract-level literature mining to convert resource-dark compounds into testable pathway or organism hypotheses; the prior title-only PubMed screen is a method floor, not evidence of scientific absence. [src: enigma_carbon_census_1]
4. Use periphyton and freshwater-biofilm inocula to target aromatic-utilizer enrichments. [src: enigma_carbon_census_1]
5. Replace the exploratory soil/freshwater rank tests with study-aware mixed models or sample-level permutations that respect study structure. [src: enigma_carbon_census_1]

## Limitations

- Resource-darkness means not linkable through the queried resources, not unknown to science; class-level catabolic literature exists for some dark compounds. [src: enigma_carbon_census_1]
- The environmental atlas measures organism abundance and occupancy, not degradation, expression, or flux. [src: enigma_carbon_census_1]
- The H3 source comparison is confounded and cannot support a statistical contrast. [src: enigma_carbon_census_1]
- The callable/dark boundary depends on the catabolic-direction reaction filter, and certainty is not comparable across compounds with signatures of different lengths. [src: enigma_carbon_census_1]
- Marine data are relatively small and gene-blind, while soil/freshwater p-values are not calibrated for compositionality and sample non-independence. [src: enigma_carbon_census_1]

## Related Concepts
- [[concepts/cultivation-bias]]
- [[concepts/metabolic-model-gapfilling]]
- [[concepts/method-concordance]]
- [[concepts/subsurface-microbial-specialization]]

## Entities
- [[entities/bacdive]]
- [[entities/flux-balance-analysis]]
- [[entities/pqq-biosynthesis]]
- [[entities/protocatechuate-3-4-dioxygenase]]
