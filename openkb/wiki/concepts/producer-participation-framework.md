---
type: "Concept"
sources: ["summaries/gene_function_ecological_agora__REPORT.md"]
description: "A tree-aware framework classifying clade-level gene innovation and exchange."
---

# Producer × Participation Framework

## Definition

The **Producer × Participation Framework** classifies each clade–function tuple along two dimensions: **production**, representing paralog expansion relative to a prevalence- and rank-matched null, and **participation**, representing the extent to which the function is distributed across phylogenetic groups through acquisition or exchange. [src: gene_function_ecological_agora]

The framework was developed in the Gene Function Ecological Agora project as a direction-agnostic alternative to requiring complete donor–recipient reconstruction at large phylogenomic scale. [src: gene_function_ecological_agora] It is related to [[concepts/horizontal-gene-transfer]], [[concepts/acquisition-depth-signatures]], and [[concepts/method-concordance]].

## Two axes

### Production

The producer axis measures whether a function has more within-clade paralog expansion than expected for comparable functions at the same taxonomic rank and prevalence. [src: gene_function_ecological_agora] The project implemented this using clade-matched neutral-family null models and producer *z*-scores. [src: gene_function_ecological_agora]

The producer null was validated with a natural-expansion control class whose documented paralog signal produced increasingly positive producer scores from genus through phylum rank. [src: gene_function_ecological_agora] Dosage-constrained controls, including tRNA synthetases and RNAP core proteins, instead showed negative producer scores, consistent with reduced paralogy rather than expansion. [src: gene_function_ecological_agora]

### Participation

The participation axis measures whether a function is unusually dispersed across phylogenetic groups relative to the relevant null, providing a proxy for cross-clade exchange. [src: gene_function_ecological_agora] Early parent-rank dispersion metrics proved too coarse or rank-sensitive for some within-phylum HGT patterns, so the project replaced them as the primary metric with Sankoff parsimony on the GTDB-r214 species tree. [src: gene_function_ecological_agora]

Sankoff parsimony inferred 17,073,194 gain events in the KO atlas and enabled M22 attribution of gains to recipient-rank depth bins. [src: gene_function_ecological_agora] The resulting participation signal describes where acquisitions landed and how deep those gains appear in the species tree, but it does not identify a specific donor. [src: gene_function_ecological_agora]

## Four categories

Combining high or low production with high or low participation yields four principal categories. [src: gene_function_ecological_agora]

| Category | Production | Participation | Interpretation |
|---|---:|---:|---|
| **Innovator-Isolated** | High | Low | A clade shows elevated paralog expansion while the function remains phylogenetically restricted. [src: gene_function_ecological_agora] |
| **Innovator-Exchange** | High | High | A clade both expands the function and participates in broad cross-clade distribution. [src: gene_function_ecological_agora] |
| **Sink/Broker-Exchange** | Low | High | A clade participates in exchange without showing strong local paralog expansion. [src: gene_function_ecological_agora] |
| **Stable** | Low | Low | The function shows neither unusual local expansion nor unusual participation. [src: gene_function_ecological_agora] |

At KO resolution, the full atlas contained 11,829,746 Stable, 803,196 Innovator-Isolated, 741,587 Sink/Broker-Exchange, and 50,026 Innovator-Exchange clade–KO tuples, with 314,607 tuples classified as insufficient data. [src: gene_function_ecological_agora]

## What the framework reveals

The framework separates two evolutionary properties that can otherwise be conflated: local diversification within a lineage and distribution across lineages. [src: gene_function_ecological_agora] For example, Mycobacteriaceae mycolic-acid functions showed an Innovator-Isolated pattern at family rank, whereas Cyanobacteriia PSII functions showed an Innovator-Exchange pattern at class rank. [src: gene_function_ecological_agora]

The Mycobacteriaceae result was refined by [[concepts/leaf-consistency]]: mycolic-acid leaf consistency was 0.15 compared with an atlas reference of 0.20, indicating that the family-level signal is heterogeneous and concentrated in a mycolate-producing sub-clade rather than uniformly distributed across the family. [src: gene_function_ecological_agora]

The Cyanobacteriia PSII result was rank-dependent, with genus, family, and order analyses classified as Stable but the class-level analysis showing producer *d* = 1.50 and consumer *d* = 0.70. [src: gene_function_ecological_agora] The report interprets this as a class-level, rather than generic all-rank, innovation pattern consistent with PSII being broadly shared within Cyanobacteria. [src: gene_function_ecological_agora]

## Acquisition depth and uncertainty

The framework is complemented by acquisition-depth profiles that divide Sankoff gains into recent, older-recent, mid, older, and ancient categories. [src: gene_function_ecological_agora] These profiles showed strong function-class differences, including a 24.5× recent-to-ancient ratio for CRISPR-Cas and a 2.3× ratio for tRNA synthetases. [src: gene_function_ecological_agora]

The project added leaf consistency as a descriptive measure of the fraction of species under a recipient clade that carry the relevant KO. [src: gene_function_ecological_agora] Strict housekeeping controls had high leaf consistency, including 0.97 for RNAP core and 0.94 for tRNA synthetases, whereas HGT-associated classes such as CRISPR-Cas and TCS histidine kinases had lower values of 0.29 and 0.13, respectively. [src: gene_function_ecological_agora]

This combination allows the framework to distinguish a recent gain that has become broadly propagated within a clade from an ancient gain that remains patchy after subsequent loss. [src: gene_function_ecological_agora]

## Donor inference and scope

The original framework intentionally did not require donor identification, because full donor–recipient reconstruction was considered impractical at GTDB scale. [src: gene_function_ecological_agora] The project later added M26 tree-based donor-proxy labels at genus rank using candidate donor genera already carrying the KO, producing exploratory Open-Innovator, Broker, Sink, and Closed-Stable classifications. [src: gene_function_ecological_agora]

M26 is not equivalent to composition-based donor inference or full duplication–transfer–loss reconciliation. [src: gene_function_ecological_agora] Its algebraic candidate-donor calculation can favor Open-Innovator labels because every compatible genus may be counted as a potential donor, so those labels require independent validation. [src: gene_function_ecological_agora]

The framework therefore makes a deliberately weaker but scalable claim: it identifies clades that expand functions and/or participate in their phylogenetic distribution, while leaving exact transfer direction unresolved. [src: gene_function_ecological_agora]

## Evidence and methodological safeguards

The project used Sankoff parsimony as the primary tree-aware participation metric because it was tractable across 18,989 species representatives and 13,062 KOs. [src: gene_function_ecological_agora] Full DTL reconciliation and rooting-uncertainty analysis were not performed, so the framework remains an approximation to more explicit evolutionary-reconciliation methods. [src: gene_function_ecological_agora]

Annotation-density residualization found no producer-side association with the tested nuisance covariates, with producer R² = 0.000, while consumer scores carried a small association, with consumer R² = 0.053. [src: gene_function_ecological_agora] Repeating the principal hypothesis analyses after residualization preserved the reported directions and verdicts. [src: gene_function_ecological_agora]

The framework should be interpreted alongside independent ecological and phenotypic evidence rather than as a stand-alone causal model. [src: gene_function_ecological_agora] In the source project, ecological consistency and phenotype profiles were used to triangulate atlas signals, an approach related to [[concepts/evidence-triangulation]] and [[concepts/genome-ecology-validation]].

## Tensions and limitations

The framework's category labels are rank-dependent because production and participation can change when the same function is aggregated over genera, families, orders, classes, or phyla. [src: gene_function_ecological_agora] The PSII rank ladder illustrates this limitation: a class-level Innovator-Exchange result coexisted with Stable results at finer ranks and an insufficient-data phylum-level participation comparison. [src: gene_function_ecological_agora]

The Bacteroidota PUL hypothesis also exposed a threshold tension: the pre-registered absolute-zero Innovator-Exchange criterion was not met at UniRef50 resolution, although a Sankoff diagnostic recovered a small HGT-direction signal. [src: gene_function_ecological_agora] This indicates that category assignment depends on substrate resolution and threshold calibration, and that a small relative contrast should not be presented as a confirmed absolute Innovator-Exchange classification. [src: gene_function_ecological_agora]

The framework does not establish that environmental occupancy causes gene exchange. [src: gene_function_ecological_agora] Its ecological results are associations that make atlas patterns more biologically interpretable, not causal demonstrations. [src: gene_function_ecological_agora]

## Open Directions

- Benchmark Sankoff participation scores and M26 donor proxies against Liu et al.'s DTLOR framework and other reconciliation methods on a representative subset of the GTDB tree. [src: gene_function_ecological_agora]
- Develop rank-aware null models that distinguish true biological rank dependence from loss of statistical power at deep taxonomic levels. [src: gene_function_ecological_agora]
- Test whether architectural diversity, measured through Pfam combinations, predicts Producer × Participation category after controlling for prevalence, clade size, and annotation density. [src: gene_function_ecological_agora]
- Extend leaf-consistency analyses to formal hypothesis tests with appropriate multiple-testing correction, focusing on whether within-clade patchiness predicts acquisition depth or ecological specialization. [src: gene_function_ecological_agora]
- Complete batched or full-Spark gene-neighborhood analyses for PUL and mycolic-acid functions to test whether these functions occur as MGE cargo despite low MGE-machinery rates. [src: gene_function_ecological_agora]

## Related source

- [[summaries/gene_function_ecological_agora__REPORT]]