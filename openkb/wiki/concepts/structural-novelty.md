---
type: "Concept"
sources: ["summaries/truly_dark_genes__REPORT.md", "summaries/paperblast_explorer__REPORT.md", "summaries/discoveries.md", "summaries/berdl_data_atlas__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md"]
description: "Low sequence representation can reveal conserved proteins with unexplored structures and functions."
---

# Protein Structural Novelty

Protein structural novelty describes the extent to which a protein lacks detectable evolutionary relatives and established structural or functional annotation in available databases. In the BER bacterial pangenome analysis, AlphaFold MSA depth is used as an operational proxy: low MSA depth indicates that few homologous sequences are available for constructing an alignment, while high depth indicates stronger representation in known sequence space. [src: alphafold_msa_annotation]

## Relationship to the annotation gap

Structural novelty is one dimension of the broader [[concepts/annotation-gap]]. The AlphaFold MSA-depth analysis found a strong positive relationship between MSA depth and functional annotation richness across 38,051,842 gene-cluster–UniProt pairs: Spearman ρ = 0.7563. [src: alphafold_msa_annotation] Mean domain hits increased from 0.59 for clusters with MSA depth below 10 to 10.83 for clusters with MSA depth of at least 10,000, while mean distinct InterPro families increased from 0.059 to 4.601. [src: alphafold_msa_annotation]

This association supports MSA depth as a useful indicator of how deeply a protein is embedded in existing sequence and domain knowledge. It does not by itself prove that a protein has a novel fold, because low MSA depth may also reflect database sampling bias, taxonomic imbalance, or divergence from known sequences. [src: alphafold_msa_annotation]

## Conserved-yet-novel proteins

The most informative structural-novelty class in the report is the set of “paradox proteins”: core gene clusters with MSA depth below 10. The analysis identified 415,603 such clusters, represented across 14,768 species clades, with mean and median MSA depths of 4.57 and 4.0. [src: alphafold_msa_annotation]

Within this subset, 286,439 clusters (68.9%) were hypothetical, only 137 (0.033%) had EC annotations, and 346 (0.083%) were mapped to KEGG. [src: alphafold_msa_annotation] These values contrast with the 3.8% hypothetical rate for all bridged core clusters, indicating that low MSA depth identifies an unusually poorly annotated subset within otherwise conserved genes. [src: alphafold_msa_annotation]

The combination of core status and low MSA depth suggests the hypothesis that these proteins perform biologically important functions despite having little similarity to characterized protein families. Core classification indicates broad pangenomic conservation, but it is not direct evidence of essentiality, biochemical activity, or a particular structural fold. [src: alphafold_msa_annotation]

## Pangenome context

Structural representation follows a strong pangenome gradient. Core clusters have a median MSA depth of 15,308, compared with 5,527 for auxiliary non-singletons and 5,299 for auxiliary-plus-singleton clusters. [src: alphafold_msa_annotation] The 10th-percentile MSA depth is 334 for core clusters versus 32 and 25 for the two accessory categories, respectively. [src: alphafold_msa_annotation]

Overall hypothetical rates show the opposite pattern: 3.8% for core clusters, 11.6% for auxiliary non-singletons, and 13.8% for auxiliary-plus-singleton clusters. [src: alphafold_msa_annotation] These results imply two overlapping forms of novelty: accessory genes are generally less represented in sequence databases, while a distinct low-depth subset of core genes remains structurally and functionally obscure. [src: alphafold_msa_annotation]

## Evidence and interpretation

The strongest evidence for the concept is the large-scale MSA-depth/domain correlation and the sharply elevated hypothetical rate among low-depth core clusters. [src: alphafold_msa_annotation] The interpretation that low-depth core proteins are priority targets for structural biology is a well-supported prioritization strategy, but the claim that they possess unprecedented folds remains a hypothesis until structures and broader homology analyses are obtained. [src: alphafold_msa_annotation]

The analysis covers 38,051,842 AlphaFold-bridged pairs, representing 28.7% of the 132,531,501 total gene clusters. [src: alphafold_msa_annotation] Because the bridged subset is enriched for organisms with established reference proteomes, the full bacterial sequence space may contain even more structural novelty than this analysis observes. [src: alphafold_msa_annotation]

MSA depth should therefore be interpreted alongside complementary measures, including domain assignments from [[entities/interproscan]], structure-prediction confidence, taxonomic distribution, and independent sequence-model approaches such as [[entities/esmfold]]. [src: alphafold_msa_annotation]

## Open Directions

- Compare AlphaFold MSA depth with ESMFold confidence for the same clusters to distinguish proteins that are novel in sequence space from proteins that are difficult to fold computationally. [src: alphafold_msa_annotation]
- Map the 415,603 paradox proteins onto the [[entities/gtdb]] phylogeny to test whether particular bacterial lineages are enriched for conserved, low-depth proteins. [src: alphafold_msa_annotation]
- Cross-reference paradox proteins with [[entities/fitness-browser]] measurements to test whether low-depth core proteins show condition-dependent growth effects. [src: alphafold_msa_annotation]
- Determine experimentally whether top-ranked proteins with MSA depth 1–9 have novel folds or instead belong to highly divergent known structural families. [src: alphafold_msa_annotation]

## Related Documents
- [[summaries/alphafold_msa_annotation__REPORT]]


See also: [[summaries/berdl_data_atlas__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/paperblast_explorer__REPORT]]

See also: [[summaries/truly_dark_genes__REPORT]]