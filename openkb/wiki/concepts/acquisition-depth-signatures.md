---
type: "Concept"
sources: ["summaries/gene_function_ecological_agora__REPORT.md"]
description: "Function classes show distinct recent-to-ancient acquisition profiles on a species tree."
---

# Acquisition-Depth Signatures

## Definition

**Acquisition-depth signatures** are function-class profiles that describe where inferred gene gains occur along a phylogenetic tree, from recent gains near the leaves to ancient gains near deep taxonomic nodes. In the Gene Function Ecological Agora, the signatures are derived with Sankoff parsimony and M22 recipient-rank attribution on the GTDB-r214 species tree. [src: gene_function_ecological_agora]

The approach is a tractable, tree-aware proxy for [[concepts/horizontal-gene-transfer]] at atlas scale: it estimates the phylogenetic depth and recipient location of gains, but does not identify the actual donor or distinguish every transfer from other evolutionary processes. [src: gene_function_ecological_agora]

## How the signature is constructed

For each KO, presence and absence across 18,989 bacterial species representatives are mapped onto the GTDB-r214 tree. Sankoff parsimony identifies gain events, and M22 assigns each gain to the lowest common ancestor of its descendant leaves and to a depth bin: `recent`, `older_recent`, `mid`, `older`, or `ancient`. [src: gene_function_ecological_agora]

The full analysis produced 17,073,194 Sankoff gain events and 13,739,162 rank–clade–KO Producer × Participation scores. The resulting acquisition profile can be summarized as the percentage of gains in each depth bin or by a recent-to-ancient ratio. [src: gene_function_ecological_agora]

The method measures **recipient-side acquisition depth**, not donor–recipient flow. This distinction is important for interpreting the atlas alongside [[concepts/gene-neighborhood-inference]], [[concepts/mobile-genetic-elements]], and more comprehensive reconciliation methods. [src: gene_function_ecological_agora]

## Function-class patterns

The report finds that acquisition-depth distributions differ systematically among control classes. CRISPR-Cas gains are strongly recent-skewed: 58.7% are recent and 2.4% ancient, yielding a recent-to-ancient ratio of 24.5. TCS histidine kinases show 45.1% recent and 4.4% ancient gains, with a ratio of 10.3, while beta-lactamases show 44.2% recent and 4.9% ancient gains, with a ratio of 9.0. [src: gene_function_ecological_agora]

Clean housekeeping controls are less recent-skewed. RNAP-core gains are 38.5% recent and 6.0% ancient, whereas tRNA-synthetase gains are 24.7% recent and 10.7% ancient, producing a ratio of 2.3. The report interprets this contrast as a quantitative distinction between HGT-active function classes and functions dominated by long-term vertical inheritance. [src: gene_function_ecological_agora]

The acquisition-depth profile is therefore a **function-class signature**, rather than merely a count of genes transferred. It captures whether inferred gains are concentrated near recent lineage diversification or distributed throughout deeper branches of the bacterial tree. [src: gene_function_ecological_agora]

## Relationship to other atlas signals

Acquisition depth complements the Producer × Participation framework. Producer scores measure clade-level paralog expansion relative to a prevalence-matched null, while participation scores describe phylogenetic distribution; M22 adds the estimated timing or depth of gains. Together, these measures distinguish recent, patchy exchange from ancient, broadly retained inheritance. [src: gene_function_ecological_agora]

The report's leaf-consistency analysis provides an additional uncertainty and persistence axis. Mean leaf consistency declines from 0.34 for recent gains to 0.20 for ancient gains, consistent with ancient gains having more opportunity for subsequent lineage-specific loss. Strict RNAP-core and tRNA-synthetase classes have high leaf consistency, whereas CRISPR-Cas, TCS histidine kinases, and AMR classes have lower values. [src: gene_function_ecological_agora]

This combination of acquisition depth and leaf consistency connects the concept to [[concepts/leaf-consistency]], [[concepts/producer-participation-framework]], and [[concepts/phylogenetic-confounding]]. It also supports [[concepts/evidence-triangulation]] when acquisition profiles are compared with ecology, phenotype, or independent MGE measurements. [src: gene_function_ecological_agora]

## Hypothesis-specific examples

The Mycobacteriaceae mycolic-acid result has a particularly strong recent-depth profile: among 53,916 Mycobacteriaceae-associated mycolic-acid gains, 79.87% are recent, 16.72% are older-recent, and 0.00% are in both the older and ancient bins. The report interprets this as consistent with within-clade innovation and limited deep transfer, while later leaf-consistency analysis narrows the claim to a mycolate-producing sub-clade rather than the entire family uniformly. [src: gene_function_ecological_agora]

Cyanobacteriia PSII gains show a different pattern. Cyanobacteria-associated PSII gains contain 32.26% recent and 2.05% ancient events, compared with 27.37% recent and 14.90% ancient events across all PSII gains. The report treats the much lower ancient fraction in Cyanobacteria as consistent with a donor-origin or class-defining history for PSII, while emphasizing that the supported Producer × Participation result is specifically class-rank dependent. [src: gene_function_ecological_agora]

The Bacteroidota PUL hypothesis illustrates why acquisition depth should not be treated as a standalone verdict. The original UniRef50 Innovator-Exchange criterion was falsified, although a Sankoff diagnostic recovered a small HGT-direction signal. Bacteroidota's ecological and phenotype associations were consistent with PUL biology, but those independent observations did not convert the original absolute-zero atlas test into a confirmed hypothesis. [src: gene_function_ecological_agora]

## Interpretation and evidence grade

The strongest claim supported by the report is that acquisition-depth distributions differ among function classes at GTDB scale, with recent-to-ancient ratios separating several HGT-associated controls from housekeeping controls. This is a direct computational measurement on a species tree, but its biological interpretation remains proxy-based because Sankoff gains are not equivalent to fully reconciled transfer events. [src: gene_function_ecological_agora]

Ecological enrichment and phenotype matching provide convergent context rather than causal proof. For example, Cyanobacteriia is enriched 2.77× in photic aquatic environments, Mycobacteriaceae 7.88× in host-pathogen environments, and Bacteroidota 1.40× in gut/rumen environments; these associations support ecological consistency but do not establish that environment caused the acquisition pattern. [src: gene_function_ecological_agora]

Pangenome openness does not provide an independent validation of the acquisition-depth measure in the current data. Across 894 genera, the atlas-wide relationship between openness and log recent-gain counts was null by Spearman correlation (*r* = −0.011), suggesting that within-species strain diversity and between-species lineage-level acquisition represent distinct evolutionary phenomena. [src: gene_function_ecological_agora]

## Tensions and limitations

### Recipient depth is not donor inference

M22 identifies where a gain is placed on the recipient-side tree, not which lineage donated the gene. The exploratory M26 tree-based donor proxy adds candidate-donor labels at genus rank, but its algebraic construction can favor Open-Innovator classifications and requires composition-based or reconciliation-based validation. [src: gene_function_ecological_agora]

### Parsimony versus reconciliation

Sankoff parsimony was selected because it is computationally tractable for 17 million gain events on an 18,989-leaf tree. Full DTL or DTLOR reconciliation, gene-tree uncertainty analysis, and systematic cross-validation were not performed at this scale. The report therefore presents acquisition-depth signatures as scalable approximations rather than definitive transfer histories. [src: gene_function_ecological_agora]

### Depth and subsequent loss

Ancient gains can have lower present-day leaf consistency because more time has elapsed for lineage-specific loss. Consequently, a low ancient-gain prevalence or low ancient leaf consistency should not be interpreted as evidence that ancient acquisition was biologically unimportant. It may partly reflect subsequent diversification and loss. [src: gene_function_ecological_agora]

## Relation to the source report

The complete analysis, including the M22 gain-attribution tables, control-class comparisons, hypothesis-specific profiles, leaf-consistency overlays, and limitations, is documented in [[summaries/gene_function_ecological_agora__REPORT]]. [src: gene_function_ecological_agora]

## Open Directions

- Benchmark Sankoff/M22 gain locations against Liu 2021 DTLOR or another modern reconciliation method on a representative, taxonomically diverse subset to quantify false gains, missed transfers, and depth-bin agreement. [src: gene_function_ecological_agora]
- Test whether acquisition-depth signatures remain stable after stratifying by annotation density, genome quality, clade size, and phylogenetic breadth beyond the completed D2 residualization. [src: gene_function_ecological_agora]
- Compare M22 profiles with independently curated transfer cases for PSII, beta-lactamases, CRISPR-Cas, and ICE-associated PULs to determine which depth bins best track known HGT histories. [src: gene_function_ecological_agora]
- Evaluate whether leaf consistency and acquisition depth jointly improve prediction of ecological or phenotypic specialization beyond Producer × Participation scores alone. [src: gene_function_ecological_agora]
