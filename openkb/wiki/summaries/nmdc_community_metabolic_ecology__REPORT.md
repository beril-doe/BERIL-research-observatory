---
type: "Summary"
description: "NMDC–pangenome integration reveals community-scale BQH and ecosystem metabolic structure."
doc_type: short
full_text: "sources/nmdc_community_metabolic_ecology__REPORT.md"
---

# Community Metabolic Ecology via NMDC × Pangenome Integration

## Overview

This report integrates NMDC community taxonomic and metabolomics data with GTDB pangenome and GapMind pathway annotations to test [[concepts/black-queen-dynamics]] and ecosystem-scale [[concepts/ecosystem-metabolic-niches]]. The analysis combines 220 community samples, 80 pathway-completeness measures, and metabolomics data from 175 samples. A taxonomy bridge mapped an average of 94.6% of community abundance to GTDB pangenome species, and all 220 samples passed the 30% bridge-quality threshold.

## Key Findings

### Community-scale Black Queen signal

Across 13 testable amino acid biosynthesis pathways, 11 (85%) had negative Spearman correlations between community pathway completeness and ambient amino acid intensity, significantly more than expected by chance (binomial sign test, p = 0.011). Leucine biosynthesis was significantly negatively correlated with metabolite intensity (r = −0.390, q = 0.022, n = 62), as was arginine biosynthesis (r = −0.297, q = 0.049, n = 80). Methionine had the largest effect size (r = −0.496) but was underpowered (n = 18, q = 0.117).

The leucine result remained significant in the soil-only sensitivity analysis (r = −0.390, q = 0.022), while arginine remained directionally consistent but lost FDR significance (r = −0.264, q = 0.117). The majority-negative pattern was unchanged. The H1 dataset was effectively single-study: 125 of 131 samples (95%) came from `nmdc:sty-11-r2h77870`, reducing concern that cross-study LC-MS variation explains the leucine result.

The positive tyrosine correlation (r = +0.419) is an important exception. Alternative production through phenylalanine hydroxylation may decouple tyrosine biosynthesis completeness from ambient tyrosine abundance. Isoleucine showed no detectable signal (r = −0.057, q = 0.823, n = 18).

### Ecosystem metabolic differentiation

PCA of the 220-sample × 80-pathway matrix separated communities strongly by ecosystem type. PC1 explained 49.4% of variance and PC2 explained 16.6%; the first five components explained 83.0% in total. Ecosystem differences were highly significant for PC1 (Kruskal-Wallis H = 52.98, p < 0.0001) and PC2 (H = 123.74, p < 0.0001). Soil and Freshwater communities were nearly non-overlapping, with median PC1 values of +3.86 and −6.28, respectively; the Soil–Freshwater Mann-Whitney test gave U = 3,674 and p < 0.0001.

PC1 was dominated by carbon-utilization pathways, including glucuronate, fumarate, succinate, cellobiose, and galactose. This suggests that carbon-substrate metabolic potential is the primary axis of ecosystem differentiation, while amino acid pathways contribute more strongly to PC2 and within-Soil separation. This result connects to [[concepts/ecosystem-metabolic-niches]] and [[concepts/metabolic-ecotypes]].

### Amino acid pathway variation

Seventeen of 18 amino acid biosynthesis pathways differed significantly across ecosystem types after Benjamini-Hochberg correction. The strongest differences occurred for glycine (H = 92.98, q = 1.2×10⁻¹⁹), asparagine (H = 66.19, q = 3.8×10⁻¹⁴), and cysteine (H = 62.66, q = 1.5×10⁻¹³). Tyrosine was the only pathway without significant ecosystem differentiation (q = 0.71).

## Methods and Interpretation

Community pathway completeness used GapMind's binary `frac_complete` metric: the fraction of community taxa with a GapMind score of 5, indicating an unambiguously complete pathway with no missing steps. The analysis used community-weighted genomic potential rather than expression or measured flux. The analysis therefore supports a weak but consistent environmental-scale BQH association, not proof that pathway loss directly causes higher metabolite availability. This distinction relates to [[concepts/pathway-completeness]], [[concepts/capability-versus-kinetics]], and [[concepts/metabolite-production-utilization-decoupling]].

The two significant pathways are energetically costly to synthesize—leucine at 37 ATP equivalents and arginine at 26 ATP equivalents—which is consistent with the hypothesis that biosynthetic functions are more likely to be lost when environmental supply is reliable. However, this interpretation remains sensitive to metabolite identification, environmental confounding, and the lack of freshwater metabolomics.

## Data and Reproducibility

The integration used `nmdc_arkin` tables for Centrifuge taxonomy, study and omics-file metadata, metabolomics, and abiotic features, together with `kbase_ke_pangenome` tables for GapMind pathways, GTDB species clades, and pangenomes. The analysis processed approximately 305M GapMind pathway records covering 27,690 GTDB species and 80 pathways. Key outputs included community pathway matrices, metabolomics matrices, bridge-quality measurements, H1 correlation results, and H2 PCA scores and loadings. The study exemplifies [[concepts/multi-omics-integration]] and [[concepts/pangenome-integration]].

## Limitations

- All 33 Freshwater samples lacked paired NMDC metabolomics, so the H1 test is effectively soil-only.
- Abiotic features were unavailable for the 174-sample merged matrix, preventing partial correlations or environmental-gradient controls.
- GapMind measures genomic potential, not transcription, translation, or pathway activity.
- Compound matching was primarily string-based; an isoleucine/leucine collision was corrected, but KEGG identifiers were available for only 2% of metabolomics records.
- Cysteine, histidine, and lysine lacked sufficient compound detections for H1 testing, while glutamine and proline had only 4 and 9 samples, respectively.
- Approximately 6.5% of mapped abundance came from genus-proxy-ambiguous taxa resolved using an alphabetical GTDB clade tiebreaker.
- Shikimic acid and 3-dehydroshikimic acid served as upstream proxies for chorismate, making the chorismate correlation difficult to interpret.

## Open Directions

1. Replicate leucine and arginine analyses across additional NMDC studies using study-level random effects and available abiotic covariates.
2. Add metabolomics for the 33 Freshwater samples to test whether BQH relationships differ between terrestrial and aquatic ecosystems.
3. Compare metatranscriptomic pathway activity with GapMind genomic completeness and metabolite abundance.
4. Improve KEGG compound annotation to expand the number of testable amino acid pathways.
5. Resolve the 61 Unknown ecosystem labels using ENVO and study metadata for finer-scale habitat analysis.

## Related Concepts
- [[concepts/functional-redundancy]]
- [[concepts/evidence-triangulation]]
- [[concepts/coverage-limited-inference]]
- [[concepts/phenotype-resolution-matching]]
- [[concepts/metabolic-model-gapfilling]]

- [[concepts/black-queen-dynamics]]
- [[concepts/ecosystem-metabolic-niches]]
- [[concepts/metabolic-ecotypes]]
- [[concepts/pathway-completeness]]
- [[concepts/capability-versus-kinetics]]
- [[concepts/metabolite-production-utilization-decoupling]]
- [[concepts/multi-omics-integration]]
- [[concepts/pangenome-integration]]

## Entities
- [[entities/kegg]]
- [[entities/modelseed]]
- [[entities/fitness-browser]]
