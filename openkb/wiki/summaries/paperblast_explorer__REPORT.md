---
type: "Summary"
description: "Quantifies severe literature bias across organisms, genes, and protein families."
doc_type: short
full_text: "sources/paperblast_explorer__REPORT.md"
---

# PaperBLAST Data Explorer — Summary

## Overview

This report characterizes literature coverage bias in the BERDL-hosted [[entities/paperblast]] collection by combining database inventory, organism and gene coverage analysis, Lorenz-curve inequality measures, and [[entities/mmseqs2]] protein-sequence clustering. It identifies a highly concentrated research landscape alongside a substantial set of poorly studied or entirely dark protein families. [src: paperblast_explorer]

The analysis contributes evidence for the cross-document concepts of [[concepts/literature-coverage-bias]], [[concepts/research-attention-inequality]], [[concepts/resource-darkness]], and protein-sequence space.

## Key Findings

- [[entities/homo-sapiens]] accounts for **46.7%** of all gene-paper records; the top five organisms account for **72.8%**. Among **20,723** organisms with literature, the top 1,000 capture **94.2%** of records. [src: paperblast_explorer]
- Of **841K** genes with a text-mined paper link, **551K (65.6%)** have exactly one paper. The median is 1 and the mean is 3.8; the top 50 genes are all human, led by p53 with **9,988** papers, TNF with **6,002**, and EGFR with **5,895**. [src: paperblast_explorer]
- Literature inequality is extreme: the organism Gini coefficient is **0.967**, while the gene Gini coefficient is **0.669**. [src: paperblast_explorer]
- Bacterial literature is also concentrated: the top 100 of **15,312** bacterial organisms capture **44.3%** of bacterial records. The leading bacteria are [[entities/mycobacterium-tuberculosis]] H37Rv (**9,079** papers), [[entities/escherichia-coli]] K-12 (**8,860**), and [[entities/pseudomonas-aeruginosa]] PAO1 (**5,928**). [src: paperblast_explorer]
- MMseqs2 clustering of **815,571** protein sequences produced **628,441** clusters at 90% identity, **344,981** at 50%, and **214,534** at 30%. At 50% identity, major families include HSP70/BiP, GAPDH, enolase, and GroEL. [src: paperblast_explorer]
- At the 50% identity level, **31,653 (9.2%)** protein families have no papers and **159,046 (46.1%)** have exactly one paper. Only **14,904 (4.3%)** have at least 20 papers. [src: paperblast_explorer]
- **5,218** multi-member families containing **14,534** sequences have no literature coverage. These dark families are dominated by REBASE methyltransferases and biolip structural entries. [src: paperblast_explorer]

## Database and Coverage Structure

The collection contains **12.4 million rows** across 14 tables, including **3,195,890** gene-paper links, **1,135,366** gene records, **815,571** unique protein sequences, and **2,089,192** structural-site records. The data connect text-mined and curated literature evidence with sequence, functional annotation, and PDB structural information. [src: paperblast_explorer]

The database covers publications from **1951 to 2026**, with **30.6%** of records from 2020 onward. It contains **27,718** organisms and approximately **1.1M** genes. Bacteria account for **5,997** organisms and **397,544** genes, Eukarya for **822** organisms and **290,537** genes, and an approximate heuristic classification leaves **14,798** organisms and **397,511** genes in an Unknown category. [src: paperblast_explorer]

The gene-paper structure is many-to-many: approximately **845K** genes connect to **1.1M** unique papers through **3.2M** associations. Each gene averages 3.8 papers and each paper mentions 2.9 genes, while **25.6%** of genes in the gene table have no text-mined paper link. [src: paperblast_explorer]

## Curated and Structural Evidence

[[entities/uniprot]] SwissProt contributes **110,171** proteins and **181,916** papers, but PaperBLAST contains only approximately **19%** of the full SwissProt database. EcoCyc has the highest paper density at **5.3 papers per protein**, compared with 1.7 for SwissProt, 0.6 for biolip, 1.3 for BRENDA, and 3.6 for MetaCyc. [src: paperblast_explorer]

PaperBLAST includes **132,179** PDB structures and **2.1M** site records covering binding, functional, modified, and mutagenesis sites. Among **48,991** unique ligands, zinc ions, chlorophyll A, calcium ions, and heme are the most frequent. [src: paperblast_explorer]

## Interpretation

The findings support a strong [[concepts/literature-coverage-bias]]: research attention is concentrated on human disease genes, model organisms, pathogens, and a small number of well-known protein families. The report relates this pattern to a self-reinforcing “rich-get-richer” dynamic in gene research and to prior work on the dark proteome and functional unknomics. [src: paperblast_explorer]

The report’s central contribution is to connect literature inequality with protein-sequence space at the protein-family level. It quantifies a literature “dark matter” consisting of multi-member sequence families with no associated papers, while showing that larger families are more likely to have at least one documented member. [src: paperblast_explorer]

## Limitations

- Text-mined mentions do not necessarily represent functional characterization. [src: paperblast_explorer]
- Reliance on PubMed Central full text creates an open-access and journal-coverage bias. [src: paperblast_explorer]
- Domain assignments are heuristic, with 35% of organisms classified as Unknown. [src: paperblast_explorer]
- The 90%, 50%, and 30% sequence-identity thresholds are analytical conventions rather than universal biological boundaries. [src: paperblast_explorer]
- Partial SwissProt representation and missing negative controls prevent direct determination of whether dark families are genuinely unstudied or merely absent from the text-mined corpus. [src: paperblast_explorer]

These limitations motivate [[concepts/coverage-limited-inference]], especially the distinction between absent evidence and evidence of absence.

## Follow-up Analyses

1. Combine the approximately **130K** VIMSS cross-references to the [[entities/fitness-browser]] with literature coverage to identify fitness-important but understudied genes. [src: paperblast_explorer]
2. Replace heuristic domain assignments with NCBI taxonomy lookups to improve organism-level coverage estimates. [src: paperblast_explorer]
3. Analyze coverage by publication year to test whether research attention is broadening or narrowing over time. [src: paperblast_explorer]
4. Apply AlphaFold structure prediction and domain annotation to the **5,218** dark families to generate functional hypotheses. [src: paperblast_explorer]
5. Build a gene-gene co-citation network to find related genes with sharply different literature coverage. [src: paperblast_explorer]

## Related Concepts
- [[concepts/structural-novelty]]
- [[concepts/msa-depth]]
- [[concepts/evidence-triangulation]]
- [[concepts/provenance-aware-data-discovery]]
- [[concepts/pangenome-integration]]

## Entities
- [[entities/gtdb]]
- [[entities/kegg]]
- [[entities/interproscan]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/alphafold-protein-structure-database]]
