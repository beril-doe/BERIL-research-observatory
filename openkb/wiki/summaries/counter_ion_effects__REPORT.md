---
type: "Summary"
description: "Shows metal–NaCl overlap reflects shared stress biology, not counter-ion confounding."
doc_type: short
full_text: "sources/counter_ion_effects__REPORT.md"
---

# Counter-Ion Effects on Metal Fitness Measurements

## Overview

This study tests whether counter ions—especially chloride delivered by metal salts—confound genome-wide metal fitness measurements. Across 19 organisms, 14 metals, and 86 organism–metal pairs, it compares metal-important genes with genes important under NaCl stress and reanalyzes core-genome enrichment after removing shared-stress genes. [src: counter_ion_effects]

The central conclusion is that metal and ionic/osmotic stress share substantial biology, but the overlap is not primarily caused by chloride counter ions and does not invalidate the [[entities/metal-fitness-atlas]]. [src: counter_ion_effects]

## Key Findings

### Shared stress is widespread but not an artifact of chloride

Of 10,821 metal-important gene records, 4,304 (39.8%) were also important under NaCl stress. The overlap occurred for every metal, ranging from 9.2% for molybdenum to 57.6% for manganese. Excluding the outlier [[entities/synechococcus-elongatus]], whose 12 NaCl experiments make the threshold easier to satisfy, reduced the overall overlap only to 36.7% (3,739/10,183). [src: counter_ion_effects]

Counter-ion dose did not explain the pattern. Chloride-delivered metals had a mean overlap of 41.6%, compared with 37.8% for non-chloride metals. [[entities/zinc]] sulfate, which delivers zero chloride, showed 44.6% overlap—higher than [[entities/cobalt]] (41.3%), [[entities/copper]] (41.0%), and [[entities/nickel]] (39.3%). [[entities/uranium]] acetate also had zero chloride and showed 37.2% overlap. [src: counter_ion_effects]

The results support a [[concepts/shared-stress-biology]] interpretation involving cell-envelope integrity, ion homeostasis, DNA repair, oxidative damage, and general stress responses, rather than counter-ion confounding. NaCl is not a pure chloride control because it also produces sodium and osmotic stress. [src: counter_ion_effects]

### DvH reveals a toxicity-mechanism hierarchy

In [[entities/dvh]], whole-genome correlations between metal and NaCl fitness profiles ranked as follows: zinc (r=0.715), manganese (0.545), copper (0.532), cobalt (0.498), mercury (0.478), nickel (0.446), aluminum (0.420), molybdenum (0.396), uranium (0.350), selenium (0.342), chromium (0.318), tungsten (0.298), and iron (0.086). [src: counter_ion_effects]

This ranking did not follow chloride concentration: zinc ranked first despite being supplied as sulfate. The authors interpret high-correlation metals as broad cellular disruptors, including cofactor displacement and widespread ionic damage, whereas lower-correlation metals more often affect specific pathways such as molybdopterin enzymes, iron-sulfur clusters, or selenoprotein biosynthesis. This mechanistic interpretation is supported by the DvH data but remains partly extrapolative because the hierarchy is based on one organism. [src: counter_ion_effects]

### Metal-specific genes comprise the majority of the signal

Across all records, 6,517 of 10,821 metal-important genes (60.2%) were classified as metal-specific, while approximately 40% were shared-stress genes. In DvH, 422 of 495 unique metal-important genes (85.3%) were metal-specific and 73 (14.7%) were shared-stress. Shared-stress genes were important for a mean of 4.1 metals, compared with 2.5 metals for metal-specific genes. [src: counter_ion_effects]

Metal-specific DvH genes were also more frequently SEED-annotated (90.5%) than shared-stress genes (78.1%), suggesting that the metal-specific set contains more recognizable metal-homeostasis functions, while shared-stress genes include more uncharacterized general stress proteins. This comparison was descriptive and was not supported by formal functional-enrichment tests. [src: counter_ion_effects]

### Core-genome enrichment remains robust

Removing shared-stress genes preserved core-genome enrichment for all 14 metals. Enrichment strengthened for molybdenum, tungsten, mercury, selenium, nickel, chromium, and uranium; for example, the core-enrichment delta changed from +0.132 to +0.145 for molybdenum and from +0.115 to +0.131 for selenium. Zinc and aluminum weakened modestly, from +0.145 to +0.115 and from +0.099 to +0.068, respectively. [src: counter_ion_effects]

Cadmium changed from a delta of -0.008 to -0.108, but this estimate used only 92 genes from one organism. Iron changed from -0.040 to +0.182, but used only 9 genes from one organism. Manganese reached 1.000 core fraction before and after correction from only 30 genes in one organism. These low-powered cases require caution. [src: counter_ion_effects]

The analysis therefore supports a core-genome robustness model: the reported core enrichment of metal fitness genes is not simply inherited from general stress genes. [src: counter_ion_effects]

### The psRCH2 salt comparison is informative but confounded

[[entities/psrch2]] provided the only within-metal comparison, testing copper as CuCl₂ under anaerobic conditions and CuSO₄ under aerobic conditions. Cross-salt fitness correlation was r=0.439, lower than within-replicate correlations for CuCl₂ (r=0.720) and CuSO₄ (r=0.859). Because aerobic and anaerobic growth differ independently of copper, this result cannot isolate counter-ion effects. [src: counter_ion_effects]

CuSO₄ nevertheless correlated more strongly with NaCl (r=0.450) than CuCl₂ (r=0.212), which argues against chloride as the primary explanation but may instead reflect shared aerobic stress mechanisms. [src: counter_ion_effects]

## Quantitative Scope

- 71 NaCl or RbCl experiments across 25 organisms
- 4,648 NaCl-important genes
- 10,821 metal-important gene records
- 86 organism–metal pairs across 14 metals
- 19 organisms included in the overlap analysis
- 559 effective-chloride concentration records
- 13 DvH metal–NaCl whole-genome correlations

[src: counter_ion_effects]

## Hypothesis Outcomes

- **H1a, substantial overlap:** supported; 39.8% of metal-important records also responded to NaCl.
- **H1b, chloride dose dependence:** rejected; overlap did not scale with effective chloride.
- **H1c, atlas fragility:** rejected; core enrichment persisted and often strengthened after correction.
- **H1d, anion-specific functional profiles:** not tested.
- **H0, negligible counter-ion effects:** partially supported; counter ions appear negligible as a specific confound, while shared stress biology is substantial.

[src: counter_ion_effects]

## Limitations

The study uses NaCl rather than a pure chloride control, and overlap depends on the NaCl-importance threshold. Several metals were tested in only one organism, and the psRCH2 comparison is confounded by oxygen regime. Putative essential genes, approximately 14.3% of protein-coding genes, lack transposon insertions and are absent from both metal and NaCl fitness measurements. The shared-versus-specific gene classification also lacks formal COG, KEGG, or PFAM enrichment testing. [src: counter_ion_effects]

## Open Directions

1. Compare metal fitness with choline chloride or KCl to separate chloride, sodium, and osmotic effects.
2. Perform formal COG, KEGG, and PFAM enrichment tests for shared-stress versus metal-specific genes.
3. Apply module-level decomposition using fitness modules to test whether stress overlap is concentrated in particular fitness modules.
4. Run matched CuCl₂/CuSO₄, ZnCl₂/ZnSO₄, and CoCl₂/CoSO₄ experiments in the same organism and growth condition.
5. Generate DvH NaCl dose-response data to compare NaCl stress directly with effective chloride delivered by metal salts.

[src: counter_ion_effects]

## Related Concepts
- [[concepts/evidence-triangulation]]
- [[concepts/gene-essentiality]]
- [[concepts/organism-specificity]]
- [[concepts/pangenome-integration]]
- [[concepts/annotation-gap]]
