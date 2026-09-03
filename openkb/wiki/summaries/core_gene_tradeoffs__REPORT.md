---
type: "Summary"
description: "Shows why conserved bacterial genes can be costly under laboratory conditions."
doc_type: short
full_text: "sources/core_gene_tradeoffs__REPORT.md"
---

# Core Gene Paradox: Why Are Core Genes More Burdensome?

## Summary

This report investigates the relationship between core genes and [[concepts/condition-dependent-essentiality]]: core genes can impose greater measured burdens in laboratory conditions even though conservation suggests strong natural selection to retain them. It argues that laboratory environments are incomplete proxies for nature, where energetically costly functions may provide essential ecological benefits.

## Key Findings

- The burden pattern is function-specific. Core genes are disproportionately burdensome in Protein Metabolism (+6.2 percentage points), Motility (+7.8 percentage points), and RNA Metabolism (+12.9 percentage points). Cell Wall shows the reverse pattern: non-core cell wall genes are more burdensome (-14.1 percentage points).
- Of the analyzed genes, 25,271 (17.8%) are classified as true trade-off genes, being important in some conditions (fitness < -1) and burdensome in others (fitness > 1). These genes are 1.29 times more likely to be core (OR=1.29, p=1.2e-44), consistent with [[concepts/condition-dependent-essentiality]] and pathway-dependent costs and benefits.
- The selection-signature matrix identifies 28,017 costly and conserved genes, 5,526 costly and dispensable genes, 86,761 neutral and conserved genes, and 21,886 neutral and dispensable genes. The costly-and-conserved group is interpreted as the strongest signal that natural selection maintains genes whose costs are visible in the laboratory but whose benefits occur in natural environments.
- Motility genes illustrate the paradox: flagellar machinery is energetically expensive under laboratory conditions but may be retained because it supports chemotaxis in natural environments. Ribosomal and RNA-metabolism functions similarly combine metabolic expense with environmental value.
- Genes with strong condition-specific effects are more likely to be core, indicating that conservation can reflect active, environment-dependent functionality rather than universal essentiality.

## Interpretation

The report resolves the paradox by distinguishing laboratory burden from ecological value. A gene can be costly in a tested laboratory condition while remaining conserved because it is beneficial under unmeasured natural conditions. The function-specific results support this interpretation more strongly than a claim that all core genes are intrinsically burdensome. The report also treats burden as potentially reflecting trade-offs rather than true dispensability.

## Data and Methods

The analysis combines Fitness Browser RB-TnSeq mutant-fitness measurements, a KBase pangenome gene-to-cluster conservation table, per-gene fitness statistics, and SEED functional annotations. The main analysis is documented in `notebooks/01_burden_anatomy.ipynb`; generated outputs are figures covering burden by function and condition type, trade-off conservation enrichment, specific phenotype conditions, motility, and the selection-signature matrix.

## Literature Context and Limitations

The report situates its findings alongside Price et al. (2018) on genome-wide mutant fitness measurements, Rosconi et al. (2022) on strain-dependent essentiality in *Streptococcus pneumoniae* pangenomes, and Koskiniemi et al. (2012) on fitness costs and selection-driven gene loss. Key limitations are the restricted ecological coverage of laboratory conditions, the possibility that fitness > 1 reflects trade-offs, the use of a 90% DIAMOND identity threshold that may miss rapidly evolving genes, and experimental bias toward convenient rather than ecologically representative condition types.

## Related Concepts
- [[concepts/phenotypic-landscape]]
- [[concepts/evidence-triangulation]]

- [[concepts/condition-dependent-essentiality]]
- [[concepts/gene-essentiality]]
- [[concepts/pangenome-integration]]
- [[concepts/genome-ecology-validation]]