---
type: "Summary"
description: "Sequential lignin enrichment reveals strong community turnover and ecological memory."
doc_type: short
full_text: "sources/lignin_community_enrichment__REPORT.md"
---

# Lignin Enrichment and Ecological Memory in Microbial Communities

## Overview

This study uses sequential enrichment and 16S/ITS amplicon sequencing to test how lignin, labile carbon, and prior enrichment history shape bacterial and fungal communities. The central result is strong, reproducible bacterial restructuring and quantitative evidence that Round 1 carbon history influences Round 2 composition more than the current carbon source. Fungal responses are more extreme but much less reproducible.

## Experimental design and data quality

The experiment analyzed 21 samples across seven treatment groups, with three replicates per group, using bacterial 16S V3–V4 and fungal ITS2 markers. Processing retained approximately 91% of 16S reads and 98% of ITS reads. The dataset contained 3,392 initial 16S OTUs and 893 initial ITS OTUs; after filtering, 1,793 and 440 OTUs remained, respectively. Reads were clustered at 97% identity with vsearch, assigned to SILVA 138.2 for 16S and NCBI ITS_RefSeq_Fungi for ITS, and analyzed using alpha diversity, Bray–Curtis distances, PCoA, PERMANOVA, PERMDISP, and CLR-based effect sizes.

## Key findings

### Lignin is a strong bacterial selective filter

A single lignin enrichment caused near-complete bacterial community turnover. The base community was dominated by unclassified taxa (Incertae Sedis, 44.3%), whereas lignin-enriched communities were dominated by [[entities/pseudomonas]] (39.3%) and [[entities/acinetobacter]] (25.2%). Shannon diversity fell from 6.46 to 3.16, and observed OTUs declined from 1,594 to 163, approximately a 90% reduction. Treatment explained 97.9% of bacterial community variance in the global PERMANOVA (R²=0.979, p=0.001).

This supports the broader idea of strong enrichment-driven community filtering: lignin-derived carbon strongly favors a small subset of organisms able to tolerate or metabolize aromatic substrates, although direct pathway activity was not measured. The result should therefore be distinguished from demonstrated metabolic function, consistent with [[concepts/capability-versus-kinetics]] and [[concepts/environmental-occupancy-vs-activity]].

### Labile carbon produces a distinct copiotrophic assemblage

Adding labile carbon to lignin shifted the bacterial community away from lignin-only enrichment. [[entities/acinetobacter]] increased from 25.2% to 41.7%, [[entities/pseudomonas]] decreased from 39.3% to 23.0%, and [[entities/aeromonas]] increased to 20.2%. Shannon diversity declined further to 2.41 and Pielou’s evenness to 0.49. The results support [[concepts/labile-carbon-priming]] at the community-composition level: supplemental carbon appears to enable fast-growing copiotrophs to co-dominate rather than merely activating the same lignin specialists.

The interpretation is supported by strong treatment differences but remains a community-level inference because lignin degradation rates and gene expression were not directly measured.

### Round 1 history generates ecological memory

Round 2 bacterial communities remained separated according to their Round 1 carbon history, even when the Round 2 condition was identical. Lignin histories produced [[entities/pseudomonas]]-dominated communities (52–53%), while lignin-plus-labile-carbon histories favored [[entities/acinetobacter]] (31–34%) and elevated [[entities/enterobacter]] (2.7–18.1%).

In the Round 2 factorial PERMANOVA, Round 1 history explained 58.9% of variance (F=14.31, R²=0.589, p=0.002), compared with 32.7% for the current Round 2 labile-carbon treatment (F=4.85, R²=0.327, p=0.018). History/current-condition distance ratios were 1.15 and 1.59, and the reported memory index was approximately 0.50. Bray–Curtis comparisons also showed persistent history effects under the same Round 2 condition: 0.507 for L-L versus LC-L and 0.486 for L-LC versus LC-LC.

These results provide strong experimental support for [[concepts/ecological-memory]] and historical contingency in microbial community assembly. OTU retention across passages was 81% for L → L-L and 91% for LC → LC-LC, consistent with persistence of core taxa through the passage series.

### Fungal communities respond strongly but reproducibility is poor

Fungal communities showed treatment-specific restructuring more extreme than bacterial communities. Base samples were [[entities/fusarium]]-dominated (26.5%) with 253 OTUs, lignin-only samples were dominated by [[entities/fusarium]] (43.4%) and [[entities/fusicolla]] (30.3%), and lignin plus labile carbon selected for [[entities/chrysosporium]] (61.4%) and [[entities/aspergillus]] (27.2%). In Round 2, [[entities/malassezia]] dominated L-L (63.4%) and LC-L (50.0%), while [[entities/pleurotus]] reached 50.0% in LC-LC.

ITS diversity collapsed to 3–8 OTUs per group, but within-group Bray–Curtis distances reached 0.99–1.00 for several Round 2 groups, compared with 0.09 for 16S. ITS PERMANOVA detected treatment structure globally (R²=0.582, p=0.001), but Round 1 history was not statistically significant in the factorial model (p=0.090). The fungal findings should therefore be treated as preliminary and interpreted through [[concepts/cross-kingdom-community-assembly]].

The planned Procrustes test of bacterial–fungal concordance was not completed because extreme ITS variability would make the comparison difficult to interpret biologically.

### Aromatic-associated bacterial genera show condition-specific responses

Several genera associated in the report with aromatic-compound degradation increased under selected conditions. [[entities/flavobacterium]] rose from 0.1% in the base community to 14.1% under lignin-only enrichment but fell to 1.4% with labile carbon, suggesting specialist-like selection by lignin-derived aromatics. [[entities/comamonas]] reached 3.6–5.1% in Round 2 groups, [[entities/aminobacter]] appeared at 7.6% in L-L and 6.4% in LC-L, and [[entities/rhodococcus]] was highest in lignin-only enrichment at 0.67%. [[entities/sphingomonas]] was more abundant in the base community (1.74%) than in enriched treatments, indicating that known aromatic-catabolic capacity does not necessarily predict enrichment under these conditions.

Because differential-abundance tests with n=3 per group have a minimum 3-versus-3 permutation p-value of 0.10, these genus-level patterns are reported primarily as effect sizes and ecological observations rather than individually FDR-significant discoveries. This limitation illustrates [[concepts/coverage-limited-inference]] and the need to match [[concepts/phenotype-resolution-matching]] to the available evidence.

## Statistical interpretation and limitations

Global Kruskal–Wallis tests were significant across the seven groups for all reported 16S and ITS diversity metrics. The factorial Round 2 PERMANOVA provided the strongest statistical support for history and current carbon effects. However, significant PERMDISP results for both markers (16S p=0.0004; ITS p=0.0001) indicate that dispersion differences contribute to PERMANOVA separation, so location and dispersion effects cannot be fully disentangled.

Important limitations include the small sample size, 97% OTU rather than ASV resolution, uneven ITS sequencing depth, exclusion of one ITS sample (LL_1, 74 retained reads), lack of UNITE taxonomy, uncertain environmental ITS assignments, absent extraction/library batch metadata, and failure to directly assay lignin-degradation activity. The claim that selected genera metabolize lignin-derived compounds remains partly extrapolative without metagenomic, transcriptomic, enzymatic, or chemical measurements. These constraints are relevant to [[concepts/annotation-gap]], [[concepts/batch-confounding]], and [[concepts/multi-omics-integration]].

## Main contribution

The study provides a controlled passage-based demonstration that lignin enrichment acts as a strong ecological filter and that labile-carbon exposure can redirect the resulting community. Its most important contribution is the quantitative ecological-memory result: Round 1 history explained more Round 2 bacterial variance than the current carbon source, and communities retained substantial divergence under matched conditions. It also highlights a contrast between robust bacterial assembly and highly stochastic fungal assembly under the same experimental scale.

## Future directions

- Increase replication to at least n>=5 per group to overcome pairwise permutation limits.
- Reanalyze with ASVs and improved ITS taxonomy using UNITE.
- Measure lignin disappearance, aromatic intermediates, extracellular enzymes, and expression of beta-ketoadipate and protocatechuate pathways.
- Map enriched taxa to [[entities/kbase-ke-pangenome]] for gene and pathway evidence.
- Use higher-depth ITS sequencing and technical metadata to distinguish biological stochasticity from technical variation.
- Add intermediate time points to resolve the kinetics of community turnover and memory formation.
- Test whether experimentally removing or reintroducing dominant taxa can reverse or reproduce the observed historical contingency.

## Related concepts

- [[concepts/ecological-memory]]
- [[concepts/labile-carbon-priming]]
- [[concepts/cross-kingdom-community-assembly]]
- [[concepts/capability-versus-kinetics]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/coverage-limited-inference]]
- [[concepts/phenotype-resolution-matching]]
- [[concepts/annotation-gap]]
- [[concepts/batch-confounding]]
- [[concepts/multi-omics-integration]]

## Related Concepts
- [[concepts/cultivation-bias]]
- [[concepts/functional-redundancy]]
- [[concepts/genome-ecology-validation]]
- [[concepts/pathway-completeness]]
