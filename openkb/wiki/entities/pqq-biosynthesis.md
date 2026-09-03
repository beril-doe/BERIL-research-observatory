---
sources: ["summaries/respiratory_chain_wiring__REPORT.md", "summaries/enigma_carbon_census_1__REPORT.md", "summaries/discoveries.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md"]
type: "Gene_Or_Pathway"
description: "PQQ pathway supplying cofactors for quinate and glucose oxidation in ADP1"
---

# PQQ Biosynthesis

## Identity

**PQQ biosynthesis** is a gene pathway that produces pyrroloquinoline quinone (PQQ), a cofactor used by PQQ-dependent dehydrogenases. [src: adp1_deletion_phenotypes, aromatic_catabolism_network]

**Type:** gene_or_pathway  
**Aliases:** PQQ biosynthetic pathway; *pqq* pathway

## Evidence in ADP1

In the *Acinetobacter baylyi* ADP1 deletion collection, *pqqC* and *pqqD* are among the top genes specifically required during growth on quinate. [src: adp1_deletion_phenotypes] These genes occur alongside *pca* and *qui* genes involved in [[entities/quinate-aromatic-degradation]], linking PQQ biosynthesis to aromatic-compound utilization. [src: adp1_deletion_phenotypes]

The aromatic-catabolism network analysis identified two PQQ-biosynthesis genes, *pqqC* and *pqqD*, among 51 quinate-specific genes. [src: aromatic_catabolism_network] Their association is biochemically consistent with QuiA, the PQQ-dependent quinoprotein that catalyzes quinate dehydrogenation during conversion of quinate toward protocatechuate and the β-ketoadipate pathway. [src: aromatic_catabolism_network]

PQQ biosynthesis genes are also condition-specific during growth on glucose, consistent with PQQ-dependent dehydrogenases catalyzing the first step of both quinate and glucose utilization pathways. [src: adp1_deletion_phenotypes] Thus, the PQQ requirement is shared across at least these two carbon sources rather than being exclusive to aromatic catabolism. [src: aromatic_catabolism_network]

## Phenotypic significance

The shared specificity of PQQ biosynthesis genes across quinate and glucose indicates that PQQ-dependent oxidation contributes to metabolism of both carbon sources in ADP1. [src: adp1_deletion_phenotypes] This finding contributes to the broader [[concepts/condition-dependent-essentiality]] and [[concepts/phenotypic-landscape]] results, in which 625 genes show growth importance concentrated on particular carbon sources. [src: adp1_deletion_phenotypes]

In the aromatic-catabolism support network, PQQ biosynthesis is one of four biochemically defined support subsystems, alongside the aromatic pathway, Complex I, and iron acquisition. [src: aromatic_catabolism_network] The two PQQ genes represent cofactor-supply infrastructure that enables the core pathway but is not itself part of the quinate-to-β-ketoadipate conversion sequence. [src: aromatic_catabolism_network]

PQQ biosynthesis is also an example of a metabolic-model gap: 30 of the 51 quinate-specific genes lacked FBA reaction mappings overall, including cofactor-supply genes and other support functions outside the model's reaction scope. [src: aromatic_catabolism_network] The pathway is therefore a candidate connection between carbon-source-specific growth phenotypes and the metabolic architecture represented in the [[summaries/adp1_deletion_phenotypes__REPORT]]. [src: adp1_deletion_phenotypes]

See also: [[summaries/adp1_triple_essentiality__REPORT]]

## Related Documents
- [[summaries/aromatic_catabolism_network__REPORT]]


See also: [[summaries/discoveries]]

See also: [[summaries/enigma_carbon_census_1__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]