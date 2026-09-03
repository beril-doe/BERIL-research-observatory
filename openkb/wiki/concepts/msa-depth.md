---
type: "Concept"
sources: ["summaries/paperblast_explorer__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md"]
description: "MSA depth measures evolutionary representation and predicts protein annotation richness."
---

# Multiple-Sequence-Alignment Depth

Multiple-sequence-alignment (MSA) depth is the number of detectable evolutionary relatives contributing to a protein sequence alignment. In AlphaFold workflows, it is commonly treated as a structural-prediction input associated with confidence, but the BER analysis evaluates it as a proxy for how extensively a protein is represented in existing sequence and functional-annotation resources. [[entities/alphafold-protein-structure-database]] [[concepts/structural-novelty]] [src: alphafold_msa_annotation]

## Evidence from the bacterial pangenome

Across the bridged portion of the BER pangenome, core gene clusters had a median MSA depth of 15,308, compared with 5,299 for auxiliary-plus-singleton clusters and 5,527 for auxiliary non-singletons. The 10th-percentile depth was 334 for core genes and 25–32 for accessory classes, showing that the strongest separation occurs among poorly represented sequences. [src: alphafold_msa_annotation]

The analysis covered 38,051,842 gene-cluster–UniProt pairs, representing 28.7% of 132,531,501 total gene clusters. The bridge is biased toward organisms with established reference proteomes, so the measured distributions may understate the annotation gap among the unrepresented 70.7%. [[entities/uniprot]] [[concepts/annotation-gap]] [src: alphafold_msa_annotation]

## Relationship to functional annotation

MSA depth was strongly and positively associated with InterProScan domain annotation richness, with Spearman ρ = 0.7563 across 38,051,842 pairs. Mean domain hits rose from 0.59 for sequences with MSA depth below 10 to 10.83 for sequences with depth of at least 10,000, while mean distinct InterPro families rose from 0.059 to 4.601. [[entities/interproscan]] [[concepts/annotation-gap]] [src: alphafold_msa_annotation]

The relationship was monotone and remained present within core, auxiliary non-singleton, and auxiliary-plus-singleton pangenome classes. Core genes had slightly higher domain richness than accessory genes at equivalent MSA-depth bins. These results support MSA depth as a useful proxy for functional annotation richness, although they do not demonstrate that MSA depth causes better annotation. [[concepts/pangenome-integration]] [src: alphafold_msa_annotation]

## MSA depth and the annotation gap

The report identifies two related but distinct patterns. First, accessory genes had higher overall hypothetical-protein rates than core genes: 13.8% for auxiliary-plus-singleton clusters, 11.6% for auxiliary non-singletons, and 3.8% for core clusters. Second, low MSA depth marked a severe annotation gap within every pangenome class. [src: alphafold_msa_annotation]

This distinction explains why core genes can be better represented overall while still containing a large set of poorly characterised proteins. Pangenome class captures broad distribution and evolutionary history, whereas MSA depth captures the extent to which detectable homologous sequence space surrounds a particular protein. [[concepts/pangenome-integration]] [[concepts/annotation-gap]] [src: alphafold_msa_annotation]

## Conserved low-depth proteins

The report defines “paradox proteins” as core gene clusters with MSA depth below 10. It identifies 415,603 such clusters spanning 14,768 species clades, with mean MSA depth 4.57 and median MSA depth 4.0. Of these clusters, 286,439 (68.9%) were hypothetical, 137 (0.033%) had EC annotations, and 346 (0.083%) were mapped to KEGG. [src: alphafold_msa_annotation]

These proteins combine broad pangenome conservation with limited detectable representation in the AlphaFold-associated sequence space. This makes them a high-priority hypothesis set for investigating [[concepts/structural-novelty]], but low MSA depth alone does not establish essentiality, biochemical activity, or genuine structural uniqueness. [src: alphafold_msa_annotation]

## Interpretation and limitations

MSA depth likely tracks annotation richness because detectable evolutionary relatives are also part of the sequence evidence from which domain and functional resources are built. The observed association should therefore be interpreted as a measure of embedding in existing biological knowledge rather than as a direct functional annotation. [src: alphafold_msa_annotation]

Several limitations constrain interpretation. AlphaFold bridge coverage excludes most gene clusters and is non-random; MSA depth is assigned to a representative sequence rather than the full within-cluster sequence distribution; the sampled genomes are taxonomically imbalanced; the reported correlation was not stratified by pangenome class or organism-level annotation bias; and the database is a static snapshot whose values may change as sequence resources expand. [src: alphafold_msa_annotation]

## Open Directions

- Recalculate the MSA-depth/domain-richness association separately for core, auxiliary, and singleton genes to test whether the gradient differs by pangenome class. [src: alphafold_msa_annotation]
- Compare AlphaFold MSA depth with ESMFold confidence for the same clusters to distinguish homologous-sequence scarcity from proteins that remain structurally foldable without deep alignments. [[entities/esmfold]] [[concepts/structural-novelty]] [src: alphafold_msa_annotation]
- Map the 415,603 low-depth core clusters onto the GTDB phylogeny to identify bacterial lineages enriched for conserved-yet-novel proteins. [[entities/gtdb]] [src: alphafold_msa_annotation]
- Join the low-depth core-protein set with Fitness Browser measurements to test whether any candidates show condition-dependent essentiality. [[entities/fitness-browser]] [[concepts/condition-dependent-essentiality]] [src: alphafold_msa_annotation]

## Related Documents
- [[summaries/alphafold_msa_annotation__REPORT]]


See also: [[summaries/paperblast_explorer__REPORT]]