---
type: "Summary"
description: "Classifies metal-important genes by specificity and prioritizes novel resistance candidates."
doc_type: short
full_text: "sources/metal_specificity__REPORT.md"
---

# Metal-Specific vs General Stress Genes

## Overview

This analysis classifies metal-important genes according to whether they cause fitness defects primarily under metal stress or across many experimental conditions. It analyzes 7,609 gene records across 24 organisms, representing 59.3% of 12,838 metal-important records in the [[entities/metal-fitness-atlas]]. The results support a distinction between metal-specificity and general stress fitness effects, while identifying several candidate metal-resistance genes for follow-up. [src: metal_specificity]

## Key Findings

### Metal-specific genes are the majority of analyzed metal-important genes

Of the 7,609 analyzed records, 4,177 (54.9%) were classified as metal-specific: they had significant metal-stress fitness defects and a sick rate below 5% across 5,945 non-metal experiments. Another 2,888 genes (38.0%) were generally sick, and 544 (7.2%) were both metal-specific and broadly stress-sensitive. Classification was qualitatively stable across thresholds: approximately 41% were metal-specific at a 2% threshold and approximately 67% at 10%. [src: metal_specificity]

Specificity differed by metal. Manganese (60.6%), molybdenum (60.5%), tungsten (56.5%), cadmium (55.9%), copper (51.9%), and cobalt (50.2%) had relatively high metal-specific fractions, whereas iron had the lowest fraction at 21.9%, plausibly reflecting its central role in core metabolism. [src: metal_specificity]

### Metal-specific genes are core-enriched, but less than general sick genes

Across 22 organisms with pangenome links, metal-specific genes had a pooled core fraction of 84.8% (2,969/3,500) and an organism-mean core fraction of 88.0%, compared with 90.2% for general sick genes and 81.1% for the baseline organism mean. A Cochran-Mantel-Haenszel comparison found that metal-specific genes were significantly less core-enriched than general sick genes (p=0.011). [src: metal_specificity]

This supports a two-tier [[concepts/core-accessory-resistance]] model: general cellular and stress functions are more conserved, while specialized metal-resistance mechanisms have a modestly greater accessory-genome contribution. However, both categories remain strongly core-enriched. The estimate is conservative because approximately 14% of protein-coding genes, including many putatively essential and core genes, are absent from fitness data. [src: metal_specificity]

### Functional enrichment supports biological specificity

Metal-specific genes were more likely than general sick genes to match metal-resistance keywords, including efflux, transporters, metal-binding, CDF, and siderophore terms (12.2% versus 7.8%; Fisher exact OR=1.64, p=2.4e-8). General sick genes instead showed greater representation of general-stress keywords (11.5% versus 13.7% as reported for general sick and metal-specific categories, respectively). These results support the interpretation that the classification captures biologically distinct [[concepts/environmental-metal-tolerance]] functions rather than merely general stress effects. [src: metal_specificity]

### Candidate prioritization

Three candidates showed the strongest combination of metal specificity and cross-organism support:

- **UCP030820 (OG01015):** 2/3 records metal-specific, 67%; associated with 7 metals and described as an oxidoreductase involved in sulfite reduction.
- **YebC (OG01383):** 7/12 records metal-specific, 58%; found across 11 organisms and 6 metals.
- **DUF1043/YhcB (OG03264):** 3/6 records metal-specific, 50%; associated with cell-division or envelope coordination.

YebC is a mechanistically interesting hypothesis candidate. Its reported role in resolving ribosome stalling at polyproline motifs could become important when metal stress increases expression of proline-rich metal transporters or chaperones. This proposed translation-bottleneck mechanism is plausible but remains untested. [src: metal_specificity]

YfdZ and the Mla/Yrb proteins were less attractive as metal-specific targets because they showed pleiotropic fitness defects. DUF39 was not metal-specific in this analysis: 0/2 records met the criterion and its mean sick rate was 0.637. [src: metal_specificity]

Novel candidate families were less likely than annotated families to have a dominant metal-specific classification: 45.6% versus 58.2% (Fisher exact OR=0.60, p=0.003). The report attributes this pattern partly to novel candidates from deeply profiled organisms, where more experiments increase opportunities to detect non-metal defects. [src: metal_specificity]

## Cross-validation and failed analyses

The analysis found that 14.7% of metal-important genes were sick under osmotic stress, compared with 39.8% overlap reported by the [[summaries/counter_ion_effects__REPORT]] between metal-important and NaCl-stress genes. The discrepancy is attributed mainly to a stricter threshold here, which required fit < -1 and |t| > 4, whereas the comparison used fit < -1 alone, as well as partially different organism sets. The direction of overlap is consistent between analyses, but exact validation remains incomplete. [src: metal_specificity]

The ICA module analysis identified no metal-specific modules because per-module z-normalization compressed most metal-experiment scores below |z|=2.0. The report recommends reanalyzing modules with precomputed z-scores from the [[entities/metal-fitness-atlas]], which previously identified 600 metal-responsive module records. [src: metal_specificity]

## Limitations and open directions

- Seven organisms—ANA3, Dino, Keio, MR1, Miya, PV4, and SB2B—were excluded because metal-atlas locus IDs did not match fitness-matrix index formats. Resolving this mismatch would recover 5,229 gene records and test whether the current specificity estimates generalize to the remaining 40.7% of records.
- The arbitrary 5% sick-rate cutoff should be compared against the Fitness Browser `specificphenotype` annotations.
- Counter-ion validation should repeat the analysis using the exact threshold from the comparison project.
- Module specificity should be recalculated using the atlas's precomputed z-scores.
- AlphaFold-based structural analysis could test for metal-binding sites in [[entities/ucp030820]], [[entities/yebc]], and [[entities/duf1043-yhcb]].

## Data products

The report generated experiment classifications for 6,504 experiments, per-gene specificity classifications for 7,609 records, a 12,838-row metal-gene join including excluded records, 56 organism-category conservation summaries, and 2,891 ortholog-group specificity records. [src: metal_specificity]

## Related Concepts
- [[concepts/fitness-conservation]]
- [[concepts/gene-essentiality]]
- [[concepts/organism-specificity]]
- [[concepts/two-speed-genome]]
