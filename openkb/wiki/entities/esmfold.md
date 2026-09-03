---
sources: ["summaries/alphafold_msa_annotation__REPORT.md"]
type: "Method"
description: "An MSA-independent protein-folding method proposed as a novelty comparator."
---

# ESMFold

## Overview

ESMFold is a protein-structure prediction method discussed as a complementary approach to [[entities/alphafold-protein-structure-database]] and AlphaFold-based analysis. [src: alphafold_msa_annotation]

## Relevance to the BERIL analysis

The report notes that ESMFold does not use multiple-sequence-alignment (MSA) depth, making it an orthogonal structural-novelty signal to [[concepts/msa-depth]]. [src: alphafold_msa_annotation] Comparing ESMFold confidence, such as ESM pLDDT, with AlphaFold MSA depth could distinguish proteins that are novel in sequence space from proteins that are difficult to fold accurately without homologous sequences. [src: alphafold_msa_annotation]

This comparison is especially relevant to the 415,603 conserved core clusters identified as low-MSA-depth “paradox proteins,” which are candidates for investigation within [[concepts/structural-novelty]] and the broader [[concepts/annotation-gap]]. [src: alphafold_msa_annotation]

## Proposed follow-up

The report proposes applying ESMFold to the same gene-cluster representatives used in the AlphaFold analysis, then comparing ESMFold confidence with MSA depth. [src: alphafold_msa_annotation] The resulting categories could identify proteins that are sequence-space novelties but remain plausibly foldable without homologs, as well as proteins for which both sequence representation and structure prediction are uncertain. [src: alphafold_msa_annotation]

## Source

- [[summaries/alphafold_msa_annotation__REPORT]] — proposes ESMFold as a complementary novelty axis for prioritising conserved, poorly annotated bacterial proteins. [src: alphafold_msa_annotation]