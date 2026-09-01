---
sources: ["summaries/paperblast_explorer__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/ecotype_functional_differentiation__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md"]
type: "Method"
description: "Sequence-based method for high-coverage functional and domain annotation"
---

# InterProScan

## Overview

InterProScan is a sequence-based domain-annotation method used in BER bacterial pangenome analyses to quantify functional annotation richness, characterize cofitness support networks, and compare annotation coverage with [[concepts/msa-depth]]. [src: alphafold_msa_annotation, amr_cofitness_networks]

## Role in the AlphaFold MSA-depth analysis

The AlphaFold MSA-depth analysis used InterProScan domain-hit counts and distinct InterPro family counts as measures of functional annotation richness for bacterial gene clusters. [src: alphafold_msa_annotation]

InterProScan assigned at least one domain annotation to 111,035,431 of 132,531,501 total gene clusters (83.8%), substantially exceeding the 29.3% coverage obtained by bridging gene clusters to [[entities/alphafold-protein-structure-database]] MSA-depth data through [[entities/uniprot]]. [src: alphafold_msa_annotation]

Among clusters with domain annotations, the mean number of hits was 7.5 and the mean number of distinct InterPro families was 3.3. [src: alphafold_msa_annotation]

## Role in AMR cofitness-network analysis

InterProScan GO annotations were used to functionally characterize antimicrobial-resistance (AMR) gene cofitness neighborhoods across 28 organisms. [src: amr_cofitness_networks]

The AMR analysis reported 68% gene coverage, described as 3.6 times better than the older SEED annotations. [src: amr_cofitness_networks] The resulting analysis detected 35 significant enrichment results among 3,193 tests, whereas the legacy SEED analysis detected 0 significant results among 280 tests. [src: amr_cofitness_networks]

InterProScan annotations revealed enrichment for flagellum-dependent motility, flagellum assembly, bacterial-type flagella, flagellum-dependent swarming, histidine biosynthesis, and tryptophan biosynthesis in AMR support networks. [src: amr_cofitness_networks] The strongest terms were observed across three to five organisms, with mean odds ratios from 4.7 to 5.3. [src: amr_cofitness_networks]

The AMR report treats these enrichment results cautiously because flagellar and biosynthetic genes may share dispensability under shaken liquid culture and supplemented media rather than direct co-regulation. [src: amr_cofitness_networks] Resolving this interpretation requires a fitness-matched permutation that compares AMR neighborhoods with random genes having similar mean fitness distributions. [src: amr_cofitness_networks]

InterProScan also supported cross-organism comparisons of AMR support networks: within-mechanism Jaccard similarity increased from 0.069 with old KEGG annotations to 0.207 with InterProScan GO annotations, while cross-mechanism similarity increased from 0.249 to 0.375. [src: amr_cofitness_networks] The analysis concluded that uniformly computed, high-coverage annotations are critical for detecting functional patterns in genome-wide cofitness studies. [src: amr_cofitness_networks]

## Relationship to MSA depth

Across 38,051,842 gene-cluster–UniProt pairs, MSA depth and InterProScan domain-hit count were strongly positively associated, with Spearman ρ = 0.7563. [src: alphafold_msa_annotation]

Mean domain hits increased from 0.59 for clusters with MSA depth below 10 to 10.83 for clusters with MSA depth at least 10,000, while mean distinct InterPro families increased from 0.059 to 4.601. [src: alphafold_msa_annotation]

The report interprets this association as evidence that MSA depth is a useful proxy for the amount of existing functional knowledge about a protein, while noting that the correlation does not establish causation. [src: alphafold_msa_annotation]

The MSA-depth/domain-richness relationship held within core, auxiliary non-singleton, and auxiliary-plus-singleton pangenome classes; core genes showed slightly higher domain richness than accessory genes at equivalent MSA-depth bins. [src: alphafold_msa_annotation]

## Relevance to the annotation gap

InterProScan provides a sequence-profile-based annotation channel that reaches more gene clusters than the AlphaFold bridge, helping distinguish broad domain coverage from structural representation. [src: alphafold_msa_annotation]

The method was used to identify the severe annotation deficit among 415,603 conserved core clusters with MSA depth below 10: 68.9% were hypothetical, only 137 (0.033%) had EC annotations, and 346 (0.083%) were mapped to KEGG. [src: alphafold_msa_annotation]

These results connect InterProScan to [[concepts/annotation-gap]] and [[concepts/structural-novelty]]: low MSA depth generally coincided with sparse domain evidence, including among the conserved “paradox protein” subset. [src: alphafold_msa_annotation]

In the AMR cofitness analysis, improved InterProScan coverage changed the apparent result from no detectable enrichment with legacy annotations to significant enrichment for several functional categories. [src: amr_cofitness_networks] This demonstrates that annotation quality can determine whether cofitness neighborhoods yield interpretable biological signals. [src: amr_cofitness_networks]

## Limitations in these analyses

The MSA-depth/domain-richness correlation was calculated on the full 38,051,842-pair dataset without subgroup stratification by pangenome class or organism-level annotation bias. [src: alphafold_msa_annotation]

InterProScan domain coverage is not equivalent to complete functional characterization, since the MSA-depth analysis measured domain hits and distinct InterPro families rather than experimentally validated biochemical functions. [src: alphafold_msa_annotation]

In the AMR analysis, differences between InterProScan and legacy annotation results may reflect improved coverage and consistency, but the flagellar and amino-acid enrichment remains vulnerable to the [[concepts/shared-dispensability]] confound. [src: amr_cofitness_networks]

The AMR cofitness calculation also used a relatively broad annotation framework and large support networks; confirmation with fitness-matched null models and more specific Pfam-level analyses was identified as future work. [src: amr_cofitness_networks]

## Related material

- [[summaries/alphafold_msa_annotation__REPORT]]
- [[summaries/amr_cofitness_networks__REPORT]]
- [[concepts/msa-depth]]
- [[concepts/annotation-gap]]
- [[concepts/structural-novelty]]
- [[concepts/cofitness-networks]]
- [[concepts/shared-dispensability]]
- [[entities/alphafold-protein-structure-database]]
- [[entities/uniprot]]

See also: [[summaries/ecotype_functional_differentiation__REPORT]]

See also: [[summaries/essential_genome__REPORT]]

See also: [[summaries/fitness_modules__REPORT]]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/lanthanide_methylotrophy_atlas__REPORT]]

See also: [[summaries/metal_fitness_atlas__REPORT]]

See also: [[summaries/paperblast_explorer__REPORT]]