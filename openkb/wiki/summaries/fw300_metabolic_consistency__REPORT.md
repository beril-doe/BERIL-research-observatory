---
type: "Summary"
description: "Cross-database analysis finds high concordance but highlights tryptophan overflow."
doc_type: short
full_text: "sources/fw300_metabolic_consistency__REPORT.md"
---

# Metabolic Consistency of Pseudomonas FW300-N2E3 Across BERDL Databases

## Overview

This report compares exometabolomic production, mutant fitness, species-level utilization, and pathway-completeness data for [[entities/pseudomonas-fw300-n2e3]] across [[entities/web-of-microbes]] (WoM), [[entities/fitness-browser]] (FB), [[entities/bacdive]] (BacDive), and [[entities/gapmind]] (GapMind). It provides a systematic test of [[concepts/method-concordance]] and distinguishes metabolite production from the ability to utilize a compound as a growth substrate. [src: fw300_metabolic_consistency]

## Key Findings

- FW300-N2E3 produced or increased 58 WoM metabolites: 27 emerged and 31 increased. Of these, 21 could be compared with at least one additional database. Seventeen of 21 were fully concordant, four were partially concordant, and none were fully discordant; mean concordance was 0.94. Across 41 individual metabolite-database comparisons, 37 were concordant (90.2%). [src: fw300_metabolic_consistency]
- Concordance was partly structural: FB matched 21/21 metabolites and GapMind matched 13/13, while BacDive recorded utilization for only 3/7 WoM-produced metabolites. The BacDive rate for WoM-produced metabolites, 3/7 (43%), was not significantly different from the *P. fluorescens* baseline of 22/80 (27.5%; binomial p = 0.40). [src: fw300_metabolic_consistency]
- Excluding the two approximate FB mappings—cytosine→cytidine and uracil→uridine—reduced the testable set from 21 to 19 and changed mean concordance from 0.937 to 0.930. [src: fw300_metabolic_consistency]

## Tryptophan Overflow and Production–Utilization Decoupling

Tryptophan is the strongest biologically meaningful discordance. FW300-N2E3 increased tryptophan in WoM, had 231 significant FB fitness genes when grown on tryptophan, and had a complete GapMind tryptophan biosynthesis pathway. However, none of 50 *P. fluorescens* strains in BacDive utilized tryptophan as a carbon source (0 positive, 50 negative; high confidence). [src: fw300_metabolic_consistency]

This result supports the hypothesis that tryptophan release may represent overflow metabolism, secretion, signaling, or [[concepts/metabolic-cross-feeding]] rather than catabolic self-reassimilation. The report does not establish the mechanism: the FB gene set may include biosynthetic, transport, regulatory, and general growth functions, and the planned pathway-level analysis was deferred. [src: fw300_metabolic_consistency]

More generally, the report argues that production and utilization assay different capabilities. A metabolite can be secreted for ecological purposes or released as a biosynthetic byproduct without serving as an energy source for the producing organism, illustrating [[concepts/metabolite-production-utilization-decoupling]]. [src: fw300_metabolic_consistency]

## GapMind and Fitness Agreement

All 13 metabolites mapped to GapMind—lactate, valine, alanine, arginine, aspartate, glutamic acid, glycine, phenylalanine, proline, trehalose, tryptophan, malate, and lysine—had complete predicted pathways. All 13 also showed growth in FB experiments, providing strong organism-level agreement between computational pathway predictions and experimental fitness data. [src: fw300_metabolic_consistency]

Malate, arginine, and valine achieved four-way consistency: WoM production, FB growth, BacDive utilization, and a complete GapMind pathway. Malate was utilized by 49/49 BacDive strains, arginine by 40/48, and valine by 1/1. [src: fw300_metabolic_consistency]

## Fitness Landscapes and Pleiotropy

Across 21 WoM metabolites with matching FB experiments, FW300-N2E3 had 601 unique significant fitness genes and 4,764 significant gene-condition hits, using |fit| > 1 and |t| > 4. The most genetically complex conditions were carnitine (283 genes), alanine across D/L forms (295 genes), arginine (270 genes), and tryptophan (231 genes). [src: fw300_metabolic_consistency]

A total of 231 genes were significant in at least three metabolite conditions, and 18 were significant in all 21. These highly pleiotropic genes were primarily amino-acid biosynthesis enzymes involved in methionine, histidine, branched-chain amino acid, leucine, and aromatic amino acid biosynthesis. They likely represent general minimal-medium growth requirements rather than substrate-specific catabolism. Approximately 370 genes significant in only one or two conditions are more informative candidates for substrate-specific transport or metabolism. This distinction is relevant to [[concepts/condition-dependent-essentiality]] and [[concepts/phenotypic-landscape]]. [src: fw300_metabolic_consistency]

Emerged metabolites had a mean of 184.4 significant genes, compared with 163.5 for increased metabolites. Both categories showed roughly 10:1 detrimental-to-beneficial fitness ratios, although the emerged-metabolite estimate had high variance. [src: fw300_metabolic_consistency]

## BacDive Discordances and Data Quality

Four compounds showed WoM production but no or limited BacDive utilization, with confidence determined by sample size:

| Metabolite | WoM action | BacDive result | Interpretation |
|---|---|---|---|
| Tryptophan | Increased | 0+/50− | High-confidence discordance and cross-feeding candidate |
| Trehalose | Increased | 1+/5− | Moderate-confidence strain variation; possible osmoprotection |
| Lysine | Emerged | 0+/3− | Moderate-confidence negative result, but small sample |
| Glycine | Increased | 0+/1− | Low-confidence single-strain observation |

BacDive values used per-strain consensus to remove duplicate-record effects. The report emphasizes [[concepts/coverage-limited-inference]]: compound coverage ranged from one to 51 strains, and species-level aggregation may conceal strain-specific capabilities. Trehalose production is interpreted as potentially related to osmoprotection, but this remains an extrapolation from related *Pseudomonas* studies rather than a direct demonstration in FW300-N2E3. [src: fw300_metabolic_consistency]

## Coverage and Limitations

Only 28/58 WoM metabolites matched FB conditions, 8/58 matched BacDive utilization data, and 13/58 matched GapMind predictions. Thus, 37/58 metabolites (64%) were observed only in WoM and remained untested by the other resources. [src: fw300_metabolic_consistency]

The datasets also represent different conditions: WoM profiles were measured on R2A rich medium, whereas FB assays used minimal media with single carbon or nitrogen sources. BacDive aggregates diverse *P. fluorescens* strains, and GTDB reclassification spans a broad *Pseudomonas_E fluorescens_E* clade. Seven of 31 mapped FB conditions had no FW300-N2E3 experiments, and manual name matching may have missed additional correspondences. These limitations bear on [[concepts/organism-specificity]], [[concepts/condition-dependent-essentiality]], and [[concepts/coverage-limited-inference]]. [src: fw300_metabolic_consistency]

## Future Directions

1. Map FB fitness genes to individual GapMind pathway steps to distinguish tryptophan biosynthesis, catabolism, transport, and regulation.
2. Repeat the analysis for other ENIGMA isolates, including *Pseudomonas stutzeri* RCH2, to test whether production–utilization decoupling is organism-specific.
3. Use chemical identifiers such as InChIKeys or CHEBI identifiers to expand WoM–BacDive matching.
4. Build a community metabolic model for FW300-N2E3 and tryptophan-auxotrophic members of the Oak Ridge groundwater community.
5. Compare exometabolomes across growth media to separate constitutive secretion from condition-dependent production.

These analyses would test the [[concepts/metabolic-cross-feeding]] hypothesis while addressing the report's central gaps in pathway mechanism, strain specificity, chemical matching, and environmental dependence. [src: fw300_metabolic_consistency]

## Related Concepts
- [[concepts/pangenome-integration]]
- [[concepts/metabolic-model-gapfilling]]
- [[concepts/experimental-functional-prioritization]]
- [[concepts/resource-darkness]]
- [[concepts/cofitness-networks]]

## Entities
- [[entities/tryptophan-biosynthesis]]
