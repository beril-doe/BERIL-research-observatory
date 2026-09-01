---
type: "Summary"
description: "ADP1 multi-omics database exploration and BERDL integration analysis"
doc_type: short
full_text: "sources/acinetobacter_adp1_explorer__REPORT.md"
---

# Acinetobacter baylyi ADP1 Data Explorer

## Overview

This report evaluates a user-provided SQLite database for *Acinetobacter baylyi* ADP1 and 13 related genomes, assessing its internal multi-omics structure, connectivity with BERDL collections, pangenome identifier mapping, metabolic-model behavior, gene essentiality, mutant fitness, proteomics, and growth predictions. The database provides a rare integrated resource combining [[concepts/multi-omics-integration|multi-omics integration]], condition-specific fitness, TnSeq essentiality, [[entities/proteomics|proteomics]], and [[entities/flux-balance-analysis|flux-balance analysis (FBA)]] for ADP1.

## Database and BERDL connectivity

The database contains 15 tables, 461,522 total rows, and 135 MB of data. Its central `genome_features` table contains 5,852 genes and 51 annotation columns spanning six modalities: TnSeq essentiality, FBA flux, mutant growth fitness, proteomics, pangenome classification, and COG/KO/Pfam/UniRef functional annotations. Coverage ranges from 15% for FBA flux to 58% for TnSeq essentiality, and no gene has measurements in all six modalities.

Connectivity with [[entities/berdl|BERDL]] is strong for four of five tested connection types: genome IDs match the pangenome at 100% (13/13), reactions match [[entities/modelseed|ModelSEED]] biochemistry at 91% (1,210/1,330), compounds match at 100% (230/230), and pangenome cluster IDs map at 100% (4,891/4,891). ADP1 is not present in the [[entities/fitness-browser|Fitness Browser]], so its mutant growth data fills a unique gap in BERDL. The 13 BERDL-format genomes belong to *s__Acinetobacter_baylyi*, whose pangenome contains 3,207 core and 1,684 accessory gene clusters.

## Pangenome identifier bridge

ADP1 uses mmseqs2-style cluster identifiers, whereas BERDL uses centroid gene identifiers; direct string matching produces no matches. A three-table bridge through `gene_genecluster_junction`, BERDL member genes, and the ADP1 `pan_genome_features` table maps all 4,891 BERDL clusters to 4,081 unique ADP1 clusters, with 100% gene-level matching across 43,754 genes. The generated `cluster_id_mapping.csv` enables BERDL pangenome annotations, including eggNOG and other functional predictions, to be joined to ADP1 genes. This is a practical example of [[concepts/pangenome-integration|pangenome identifier integration]].

## Essentiality, FBA, and fitness

FBA flux predictions and TnSeq essentiality calls are available for 866 genes. They agree for 639 genes, or 73.8%, while 227 genes are discordant. These discordances are candidates for metabolic-model refinement and may identify regulatory or non-metabolic effects that FBA does not capture. Essentiality is condition-dependent: 499 genes are essential in minimal media compared with 346 in LB.

Mutant growth fitness across eight carbon sources has a mean pairwise correlation of 0.44. Urea is an outlier, showing weak correlations with the other conditions (r = 0.12–0.28) and a correlation of r = 0.11 with quinate, suggesting the hypothesis that urea catabolism depends on a relatively distinct gene set. Butanediol-acetate and butanediol-lactate have the strongest correlations, at r = 0.58 and r = 0.53, respectively, consistent with shared central-carbon requirements. These results contribute to the study of condition-specific microbial fitness.

FBA flux classes are condition-dependent: 177 of 866 genes (20%) change class between rich and minimal media, indicating substantial metabolic rewiring between growth conditions.

## Annotation and pangenome patterns

Essential genes are substantially more annotation-rich than dispensable genes. COG assignments occur in 33% of essential genes versus 5% of dispensable genes, while KEGG KO assignments occur in 92% versus 53%, respectively. Approximately 8% of essential genes lack KO assignments and may represent novel essential functions, although this interpretation requires further validation. Essential genes are also more likely to belong to the core pangenome, linking conservation with essentiality. These findings relate to gene essentiality and functional annotation bias.

## Metabolic model conservation and gapfilling

Across 14 genomes and 1,330 unique reactions, 1,248 reactions (94%) are shared by all genomes, 62 are variable, and 20 are genome-unique. Gapfilling accounts for 7.7% of reactions on average, with 243 missing functions cataloged. Despite the high reaction conservation, 105,376 of 121,519 growth phenotype predictions (87%) require at least one gapfilled reaction. Prediction accuracy is therefore tightly coupled to gapfilling quality, and false-negative predictions have higher mean gap counts than correct predictions. This is a central issue for [[concepts/metabolic-model-gapfilling|metabolic-model gapfilling]] and phenotype prediction.

## Proteomics and engineered strains

Seven engineered ADP1 strains are represented, including wild-type ADP1 and six derivatives involving aromatic amino acid pathway modifications such as ΔaroF, ΔaroG, and dgoA variants. Proteomics covers 2,383 genes across all seven strains. High cross-strain abundance correlations indicate that the engineered modifications have targeted rather than globally disruptive effects on the proteome.

## Main contribution and limitations

The database adds four data resources not otherwise available for ADP1 in BERDL: mutant growth fitness on eight carbon sources, proteomics across seven engineered strains, TnSeq essentiality on minimal and LB media, and FBA predictions with gapfilling metadata. Its main limitations are sparse overlap among modalities, especially FBA coverage; indirect rather than direct pangenome cluster mapping; the strong dependence of growth predictions on gapfilled reactions; and restriction to a single species.

## Open directions

- Analyze the 227 FBA–TnSeq discordant genes for pathway, annotation, regulatory, and pangenome enrichment.
- Use the cluster bridge to compare ADP1 fitness patterns with related organisms represented in the Fitness Browser.
- Identify urea-specific fitness genes and test their conservation across the *A. baylyi* pangenome.
- Assess gapfill confidence using pangenome conservation and genomic evidence, focusing on the 243 missing functions.
- Extend the analysis to the identified 37-table PhageFoundry *Acinetobacter* genome browser and test links between genome features and phage susceptibility.

## Supporting materials

The analysis is documented in five notebooks covering database exploration, BERDL connection scanning, cluster-ID mapping, gene essentiality and fitness, and metabolic modeling and phenotypes. Generated outputs include `data/cluster_id_mapping.csv` and `data/berdl_connection_summary.csv`.

## Related Concepts
- [[concepts/multi-omics-integration]]
- [[concepts/pangenome-integration]]
- [[concepts/metabolic-model-gapfilling]]

## Entities
- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/berdl]]
- [[entities/fitness-browser]]
- [[entities/modelseed]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/flux-balance-analysis]]
- [[entities/proteomics]]
