---
type: "Summary"
description: "ICA identifies conserved bacterial fitness modules for process-level annotation."
doc_type: short
full_text: "sources/fitness_modules__REPORT.md"
---

# Pan-bacterial Fitness Modules via Independent Component Analysis

## Summary

This report evaluates [[entities/independent-component-analysis]] on RB-TnSeq fitness data from 32 bacterial organisms. The resulting modules capture co-regulated biological processes and conserved fitness programs, but are complementary to—not substitutes for—sequence-based gene-function prediction. [src: fitness_modules]

## Key Findings

- A strict membership rule, using absolute ICA weights of at least 0.3 and no more than 50 genes per module, produced biologically coherent modules. The resulting modules were 94% functionally enriched and showed 2.8-fold within-module cofitness enrichment, whereas the initial D'Agostino K-squared selection produced larger modules with weaker signal. [src: fitness_modules]
- ICA identified **1,116 stable modules** across 32 organisms, with **94.2%** showing significantly elevated within-module cofitness (Mann–Whitney U, p < 0.05). Mean within-module absolute correlation was 0.34 versus 0.12 for the background, and module genes showed **22.7-fold genomic adjacency enrichment**, consistent with operon-level organization. [src: fitness_modules]
- Adding PFam domains and lowering the enrichment-overlap threshold from 3 to 2 increased the annotation rate from 8% to 80%, covering 890 rather than 92 modules. [[entities/pfam]] provided the broadest coverage, while KEGG KOs were generally too gene-specific for module-level enrichment. [src: fitness_modules]
- Cross-organism alignment found **1.15 million BBH pairs**, 13,402 ortholog groups, and 156 module families spanning at least two organisms. Of these, 145 had consensus functional labels; the largest family spanned 21 organisms. [src: fitness_modules]
- The analysis generated **6,691 function predictions** for hypothetical proteins. Of these, 2,455 were backed by conserved module families and 4,236 were module-only predictions. These should be interpreted as biological-process associations rather than precise molecular-function assignments. [src: fitness_modules]

## Benchmarking and Interpretation

Held-out benchmarking showed that ortholog transfer was substantially better for gene-level KEGG prediction than module-based approaches: ortholog transfer achieved 95.8% strict precision, 91.2% coverage, and an F1 score of 0.934. Domain-based prediction achieved 29.1% precision and 66.6% coverage. Module-ICA and cofitness voting had below-1% strict KO precision, despite module-ICA coverage of 23.3% and cofitness-voting coverage of 73.0%. [src: fitness_modules]

The low KO precision is expected because KEGG KOs are usually gene-level assignments, whereas modules represent coordinated biological processes. A module containing 20 annotated genes may contain approximately 20 distinct KOs. Thus, [[concepts/cofitness-networks]] and [[concepts/fitness-conservation]] are best used to infer process context, while orthology remains the preferred method for specific function transfer. [src: fitness_modules]

The approach extends prior uses of [[entities/independent-component-analysis]] for transcriptomic module detection and applies the same general idea to phenotypic fitness compendia. Its cofitness validation also builds on the use of correlated mutant-fitness profiles to infer gene function. [src: fitness_modules]

## Limitations

- Module-ICA has near-zero precision for exact KEGG KO assignments and should not be treated as a gene-level function predictor. [src: fitness_modules]
- Organisms with fewer than approximately 100 experiments produce weaker modules; the report specifically notes that Caulo, with 198 experiments, showed only 2.9-fold correlation enrichment. [src: fitness_modules]
- Limiting components to at most 40% of the experiment count helps avoid FastICA convergence failures but may omit modules in organisms with few experiments. [src: fitness_modules]
- PFam annotations provide broad domain-level coverage but may overcount functional associations. [src: fitness_modules]

## Open Directions

The report proposes extending the analysis to additional RB-TnSeq organisms, integrating modules with core/auxiliary/singleton pangenome classes, testing module enrichment in specific biological questions, and developing a browser for module families and predictions. [src: fitness_modules]

## Supporting Data and Provenance

The workflow includes notebooks for data selection, matrix extraction, ICA decomposition, module annotation, cross-organism alignment, function prediction, and benchmarking. Generated outputs include per-organism fitness matrices, ICA module definitions and weights, annotations, BBH orthologs, module families, predictions, and benchmark results. Primary data came from the [[entities/fitness-browser]] tables for gene fitness, metadata, experiments, and orthologs, together with pangenome gene-cluster assignments from [[entities/kbase-ke-pangenome]]. [src: fitness_modules]

## Related Concepts
- [[concepts/annotation-gap]]
- [[concepts/pangenome-integration]]
- [[concepts/coverage-limited-inference]]
- [[concepts/organism-specificity]]

## Entities
- [[entities/berdl]]
- [[entities/gtdb]]
- [[entities/eggnog]]
- [[entities/interproscan]]
- [[entities/bakta]]
