---
sources: ["summaries/module_conservation__REPORT.md", "summaries/lignin_community_enrichment__REPORT.md", "summaries/discoveries.md", "summaries/cog_analysis__REPORT.md"]
type: "Dataset"
description: "KBase dataset providing pangenome gene-cluster and conservation mappings"
---

# KBase KE Pangenome Database

## Overview

The KBase KE Pangenome Database is a dataset used for bacterial pangenome analysis, including gene-cluster relationships, conservation mappings, and functional annotations. [src: cog_analysis, module_conservation]

## Use in COG Functional Category Analysis

The database supplied data for the analysis reported in [[summaries/cog_analysis__REPORT]], which examined 357,623 genes from 32 bacterial species spanning 9 phyla. [src: cog_analysis]

The analysis used the following tables:

- `gene_cluster`, containing gene-cluster data. [src: cog_analysis]
- `gene_genecluster_junction`, linking genes to gene clusters. [src: cog_analysis]
- `eggnog_mapper_annotations`, providing functional annotations used to assign COG categories. [src: cog_analysis]

The resulting analysis compared functional-category distributions across core, auxiliary, and singleton gene classes. Novel genes were most strongly enriched for COG L mobile-element functions, while core genes were enriched for conserved functions including translation, nucleotide metabolism, coenzyme metabolism, amino acid metabolism, and energy production. [src: cog_analysis]

These results contribute to the [[concepts/two-speed-genome]] interpretation of bacterial pangenomes, in which conserved core genes support essential cellular functions while novel genes are associated with mobility, defense, and ecological adaptation. The enrichment of mobile-element functions was also interpreted in relation to [[concepts/horizontal-gene-transfer]]. [src: cog_analysis]

## Use in Fitness-Module Conservation Analysis

The KBase pangenome link table `conservation_vs_fitness/data/fb_pangenome_link.tsv` provided gene-to-cluster conservation mappings for the analysis reported in [[summaries/module_conservation__REPORT]]. [src: module_conservation]

Those mappings were used to compare conservation of ICA fitness-module genes with the genome-wide core-gene baseline. Module genes were 86.0% core compared with 81.5% of all genes, a +4.5 percentage-point difference (OR=1.46, p=1.6e-87). [src: module_conservation]

Among 974 modules with at least three mapped genes, 577 (59%) were classified as core modules (>90% core genes), 349 (36%) as mixed modules (50–90% core), and 48 (5%) as accessory modules (<50% core). The median module was 93.4% core. [src: module_conservation]

The same conservation mappings supported a family-level test showing no relationship between module-family breadth and core fraction (Spearman rho=-0.01, p=0.914). [src: module_conservation] This result informs [[concepts/pangenome-integration]] and the [[concepts/fitness-conservation]] relationship by extending conservation analysis from individual genes to co-regulated functional units. [src: module_conservation]

## Data and Interpretation Limitations

The COG analysis depended on eggNOG v6 annotations, which may differ from original COG assignments, and approximately 30% of genes lacked COG annotations. [src: cog_analysis] Composite multi-letter COG assignments were counted once per gene rather than split across component categories. [src: cog_analysis]

The fitness-module conservation analysis covered a 29/32-organism subset because Cola, Kang, and SB2B lacked pangenome links; their species had too few genomes in GTDB for pangenome construction. [src: module_conservation] Module conservation results also depend on upstream ICA membership criteria, including |Pearson r| >= 0.3 and a maximum of 50 genes per module, as well as convenient rather than biologically validated 90% and 50% core/accessory classification thresholds. [src: module_conservation]

The fitness-module analysis excluded essential genes because ICA requires measurable transposon-insertion fitness variation. Consequently, its conservation results describe the non-essential, fitness-measurable portion of the genome rather than all genes. [src: module_conservation]

## Related Resources

- [[entities/eggnog]]
- [[concepts/pangenome-integration]]
- [[concepts/two-speed-genome]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/fitness-conservation]]
- [[summaries/cog_analysis__REPORT]]
- [[summaries/module_conservation__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/lignin_community_enrichment__REPORT]]