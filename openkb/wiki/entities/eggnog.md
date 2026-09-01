---
sources: ["summaries/pitfalls.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/essential_metabolome__REPORT.md", "summaries/clay_confined_subsurface__REPORT.md", "summaries/cf_formulation_design__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md"]
type: "Dataset"
description: "Orthology-based annotations used to interpret microbial gene and AMR functions."
---

# eggNOG

## Overview

eggNOG is an orthology-based functional annotation resource used in the [[summaries/amr_pangenome_atlas__REPORT]] to characterize antimicrobial-resistance (AMR) gene clusters and compare their functional categories with the broader pangenome. [src: amr_pangenome_atlas] In BERDL pangenome analyses, eggNOG annotations are stored in `eggnog_mapper_annotations`, where `query_name` identifies the annotated gene-cluster representative rather than a row in the per-gene `gene` table. [src: pitfalls]

## Use in the AMR pangenome analysis

The report analyzed eggNOG annotations for 77K AMR clusters and compared them with an 86M-cluster pangenome baseline. [src: amr_pangenome_atlas] COG category analysis showed that AMR genes were enriched 7.05-fold in COG V (Defense mechanisms), 1.93-fold in COG P (Inorganic ion transport), and 1.50-fold in COG J (Translation). [src: amr_pangenome_atlas]

The COG P enrichment was associated with mercury- and arsenic-resistance gene families, while COG J enrichment was consistent with ribosomal-protection genes. [src: amr_pangenome_atlas] Categories related to replication, lipid metabolism, and cell motility were depleted among AMR genes relative to the pangenome baseline. [src: amr_pangenome_atlas]

Because gene-cluster identifiers are species-specific, an eggNOG annotation count and a count after joining to `gene_cluster` measure different quantities: the former counts annotation records, whereas the latter can count species-level gene-cluster entries when the same annotation query name occurs in multiple species pangenomes. [src: pitfalls]

## Annotation coverage

The analysis found that 93.0% of AMR clusters had both Bakta product annotations and eggNOG hits, while the remaining 7.0% had Bakta annotations only. [src: amr_pangenome_atlas] The sparsely annotated one-source AMR clusters were enriched for singletons, which represented 55.4% of that group compared with 34.6% of clusters with two annotation sources. [src: amr_pangenome_atlas]

No AMR clusters had Pfam domain hits in the reported `bakta_pfam_domains` table, suggesting that the eggNOG/Bakta annotation space and the reported Pfam results did not substantially overlap for these AMR families. [src: amr_pangenome_atlas]

The `eggnog_mapper_annotations` table contains approximately 93M rows and should be filtered before joins or other large operations. [src: pitfalls] Its `PFAMs` field stores comma-separated Pfam domain names, such as `DUF4041` and `GIY-YIG`, rather than Pfam accession identifiers; searches should therefore use wildcard matching on domain names, not accession strings. [src: pitfalls] Pfam accession assignments inferred from names should be independently checked against InterPro or UniProt because similarly named or numerically adjacent Pfam families can be distinct. [src: pitfalls]

## Related resources and concepts

- [[entities/bakta]] provided the complementary product annotations used with eggNOG hits. [src: amr_pangenome_atlas]
- [[entities/amrfinderplus]] supplied the AMR annotations whose functional context was evaluated with eggNOG. [src: amr_pangenome_atlas]
- The eggNOG analysis supports [[concepts/pangenome-integration]] by comparing AMR-associated functions with a large pangenome baseline. [src: amr_pangenome_atlas]
- Its defense-mechanism enrichment helps characterize [[concepts/core-accessory-resistance]] beyond gene presence alone. [src: amr_pangenome_atlas]
- Correct gene-cluster-level joining and annotation-source comparison contribute to [[concepts/identifier-resolution-and-crosswalks]] and [[concepts/annotation-gap]]. [src: pitfalls, amr_pangenome_atlas]
- Large eggNOG joins are subject to [[concepts/scalable-spark-data-analysis]] constraints and should generally be executed with filtered direct Spark SQL rather than by collecting full annotation matrices to pandas. [src: pitfalls]

See also: [[summaries/annotation_gap_discovery__REPORT]]

See also: [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/cf_formulation_design__REPORT]]

See also: [[summaries/clay_confined_subsurface__REPORT]]

See also: [[summaries/essential_metabolome__REPORT]]

See also: [[summaries/fitness_modules__REPORT]]

See also: [[summaries/gene_function_ecological_agora__REPORT]]

## Related Documents
- [[summaries/pitfalls]]
