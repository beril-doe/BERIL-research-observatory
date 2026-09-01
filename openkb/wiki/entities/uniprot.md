---
sources: ["summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/pitfalls.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/conservation_vs_fitness__REPORT.md", "summaries/bacillota_b_subsurface_accessory__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md"]
type: "Dataset"
description: "Protein sequence resource linking gene clusters to functional and homology evidence"
---

# UniProt

## Overview

UniProt is the protein sequence and annotation resource used to connect bacterial gene clusters with AlphaFold MSA-depth records and to provide reviewed protein exemplars for metabolic annotation-gap resolution. [src: alphafold_msa_annotation, annotation_gap_discovery] The AlphaFold analysis uses real UniProt accessions obtained through the UniRef100 bridge in `bakta_annotations`, while UniParc-only identifiers are excluded when no corresponding AlphaFold entry is available. [src: alphafold_msa_annotation]

## Role in the AlphaFold MSA-depth analysis

Of 132,531,501 gene clusters in the pangenome table, 38,804,903 (29.3%) have a real UniProt accession through `bakta_annotations.uniref100`. [src: alphafold_msa_annotation] A total of 38,051,842 clusters (28.7% of all clusters) successfully bridge from the UniProt-linked records to `kescience_alphafold.alphafold_msa_depths`. [src: alphafold_msa_annotation]

The successful bridge provides the paired records needed to compare [[concepts/msa-depth]] with [[entities/interproscan]] domain annotation richness. [src: alphafold_msa_annotation] The analysis contains 38,051,842 gene-cluster–UniProt pairs and reports a Spearman correlation of ρ = 0.7563 between MSA depth and domain-hit count. [src: alphafold_msa_annotation]

## Role in annotation-gap discovery

UniProt's reviewed Swiss-Prot bacterial sequences supplied homology exemplars for the annotation-gap discovery pipeline. [src: annotation_gap_discovery] The study retrieved 328 exemplar sequences covering 75 of 84 unique EC numbers through the UniProt REST API and searched target proteomes with DIAMOND v2.1.16 blastp. [src: annotation_gap_discovery] The search used `--evalue 1e-5 --max-target-seqs 20 --id 25 --query-cover 50 --outfmt 6` and generated 154 BLAST hits. [src: annotation_gap_discovery]

These UniProt-derived sequence comparisons formed one component of [[concepts/evidence-triangulation]], alongside EC matching, alternative Bakta annotations, pangenome conservation, and fitness evidence. [src: annotation_gap_discovery] BLAST homology was the most impactful single evidence stream, resolving 70 of 201 reaction–organism pairs (34.8%), while the complete integrated pipeline resolved 96 pairs (47.8%). [src: annotation_gap_discovery] High-confidence BLAST support used thresholds of at least 30% identity, at least 70% coverage, and an e-value of at most 1e-10; medium-confidence support used thresholds of at least 25% identity, at least 50% coverage, and an e-value of at most 1e-5. [src: annotation_gap_discovery]

The UniProt exemplars were concentrated in reactions with well-characterized enzymes and broad phylogenetic distribution, including branched-chain amino acid biosynthesis and polyamine metabolism. [src: annotation_gap_discovery] This distribution supports use of UniProt homology as complementary evidence, but does not establish that a sequence hit alone resolves an annotation gap. [src: annotation_gap_discovery]

## Coverage and bias

The UniProt-linked subset is not a random sample of the bacterial pangenome: organisms with established reference proteomes, including *E. coli*, *Pseudomonas*, and *Bacillus*, are over-represented. [src: alphafold_msa_annotation] Consequently, the 70.7% of gene clusters without a usable AlphaFold bridge likely includes a larger [[concepts/annotation-gap]] than the analysed subset, although that inference is subject to the report's coverage and sampling limitations. [src: alphafold_msa_annotation]

The annotation-gap study also depended on the availability of reviewed exemplars for specific EC numbers: exemplar sequences were available for 75 of 84 unique ECs, leaving some reactions without this particular homology evidence stream. [src: annotation_gap_discovery] The study's unresolved cases were also enriched among “dark reactions” without EC numbers, for which only 8 of 50 reactions (16%) were resolved compared with 88 of 151 reactions with known EC numbers (58.3%). [src: annotation_gap_discovery]

## Relationship to annotation and structural novelty

In the AlphaFold analysis, UniProt-linked accessions are the entry point for measuring how deeply gene-cluster representatives are represented in AlphaFold's sequence-derived MSA data. [src: alphafold_msa_annotation] Low MSA depth among UniProt-linked clusters is associated with sparse InterProScan domain annotation and is used to identify conserved, poorly characterised proteins called “paradox proteins.” [src: alphafold_msa_annotation]

The 415,603 core clusters with MSA depth below 10 were identified through this linked analysis; 286,439 (68.9%) were hypothetical, 137 (0.033%) had EC annotations, and 346 (0.083%) were mapped to KEGG. [src: alphafold_msa_annotation] These results connect UniProt-linked sequence representation to the study of [[concepts/structural-novelty]], but they do not establish that UniProt coverage or MSA depth alone determines protein function. [src: alphafold_msa_annotation]

In the annotation-gap study, UniProt exemplars provided sequence-level support rather than definitive functional validation. [src: annotation_gap_discovery] The final assignments combined homology with fitness, pangenome, EC, and annotation evidence, and 105 of 201 reaction–organism pairs (52.2%) remained unresolved. [src: annotation_gap_discovery]

## Related resources

- [[entities/alphafold-protein-structure-database]] — provides the AlphaFold records whose MSA-depth values were joined to UniProt-linked gene clusters. [src: alphafold_msa_annotation]
- [[entities/interproscan]] — supplies domain annotations used to quantify functional annotation richness. [src: alphafold_msa_annotation]
- [[entities/diamond]] — performed the protein-sequence homology searches against UniProt Swiss-Prot exemplars. [src: annotation_gap_discovery]
- [[concepts/evidence-triangulation]] — frames the integration of UniProt homology with other evidence streams for resolving annotation gaps. [src: annotation_gap_discovery]
- [[concepts/annotation-gap]] — the broader knowledge gap examined through UniProt and AlphaFold coverage. [src: alphafold_msa_annotation]
- [[concepts/msa-depth]] — the principal sequence-representation measure associated with UniProt-linked clusters. [src: alphafold_msa_annotation]
- [[concepts/structural-novelty]] — the novelty dimension used to prioritise low-MSA-depth core proteins. [src: alphafold_msa_annotation]
- [[summaries/alphafold_msa_annotation__REPORT]] — source summary for the complete AlphaFold MSA-depth analysis. [src: alphafold_msa_annotation]
- [[summaries/annotation_gap_discovery__REPORT]] — source summary for the integrated metabolic annotation-gap study. [src: annotation_gap_discovery]

See also: [[summaries/bacillota_b_subsurface_accessory__REPORT]]

See also: [[summaries/conservation_vs_fitness__REPORT]]

See also: [[summaries/essential_genome__REPORT]]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/gene_function_ecological_agora__REPORT]]

See also: [[summaries/lanthanide_methylotrophy_atlas__REPORT]]

See also: [[summaries/pgp_pangenome_ecology__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]