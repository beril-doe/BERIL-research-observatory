---
type: "Summary"
description: "Shows how AlphaFold MSA depth reveals bacterial annotation gaps."
doc_type: short
full_text: "sources/alphafold_msa_annotation__REPORT.md"
---

# AlphaFold MSA Depth as a Lens on the Bacterial Annotation Gap

## Overview

This report evaluates AlphaFold multiple-sequence-alignment (MSA) depth as an indicator of bacterial protein representation and functional annotation across the BER pangenome. It joins pangenome classes, UniProt links, InterProScan domains, and AlphaFold MSA-depth data for 38,051,842 gene-cluster–UniProt pairs. The analysis frames MSA depth as both a structural-prediction variable and a proxy for existing biological knowledge, contributing to the broader [[concepts/annotation-gap]], [[concepts/structural-novelty]], and functional-annotation themes. [src: alphafold_msa_annotation]

## Dataset and coverage

The source pangenome contains 132,531,501 gene clusters. Of these, 38,804,903 (29.3%) have a real [[entities/uniprot]] accession, and 38,051,842 successfully bridge to the AlphaFold MSA-depth table. The remaining 70.7% lack usable UniRef100 identifiers or have UniParc-only identifiers without AlphaFold entries. The bridged subset is biased toward better-characterised organisms, so the unrepresented portion may contain an even larger annotation gap. [src: alphafold_msa_annotation]

InterProScan reaches substantially farther into sequence space: 111,035,431 clusters (83.8% of all clusters) have at least one domain annotation, with mean values of 7.5 domain hits and 3.3 distinct InterPro families. [src: alphafold_msa_annotation]

## Key findings

### Core genes have much greater MSA representation

Core gene clusters have a median MSA depth of 15,308, compared with 5,299 for auxiliary-plus-singleton clusters and 5,527 for auxiliary non-singletons. Thus, core genes have approximately 2.9 times the MSA depth of accessory genes. The lower tail is more strongly separated: the 10th-percentile depth is 334 for core genes versus 25–32 for accessory classes. [src: alphafold_msa_annotation]

Among bridged clusters:

| Pangenome class | Clusters | Median MSA depth | 10th percentile | 90th percentile | MSA depth < 10 | Hypothetical rate |
|---|---:|---:|---:|---:|---:|---:|
| Core | 25,571,299 | 15,308 | 334 | 19,500 | 415,733 (1.6%) | 3.8% |
| Auxiliary non-singleton | 5,384,900 | 5,527 | 32 | 19,192 | 245,002 (4.6%) | 11.6% |
| Auxiliary + singleton | 7,095,643 | 5,299 | 25 | 19,203 | 392,959 (5.5%) | 13.8% |

This establishes a strong [[concepts/pangenome-integration]] gradient in sequence and structural representation. [src: alphafold_msa_annotation]

### MSA depth predicts domain annotation richness

Across 38,051,842 pairs, MSA depth and domain-hit count show a strong monotone association (Spearman ρ = 0.7563). Mean domain hits increase from 0.59 for clusters with MSA depth below 10 to 10.83 for clusters with depth at least 10,000; mean distinct InterPro families increase from 0.059 to 4.601. This is an 18-fold span in mean domain hits. [src: alphafold_msa_annotation]

| MSA depth | Core clusters | Mean domain hits | Mean distinct InterPro families |
|---|---:|---:|---:|
| < 10 | 415,733 | 0.59 | 0.059 |
| 10–99 | 1,143,785 | 0.96 | 0.242 |
| 100–999 | 2,301,137 | 1.95 | 0.852 |
| 1,000–4,999 | 3,126,558 | 3.72 | 1.843 |
| 5,000–9,999 | 2,591,011 | 5.62 | 2.664 |
| ≥ 10,000 | 15,993,075 | 10.83 | 4.601 |

The relationship persists within core, auxiliary non-singleton, and auxiliary-plus-singleton classes, with core genes showing slightly greater domain richness at equivalent MSA depths. The result supports [[concepts/msa-depth]] as a proxy for functional annotation richness, while not establishing that MSA depth causes annotation quality. [src: alphafold_msa_annotation]

### Conserved, low-depth “paradox proteins” define a priority set

The analysis identifies 415,603 distinct core clusters with MSA depth below 10. These clusters occur across 14,768 species clades and have mean and median MSA depths of 4.57 and 4.0, respectively. Of them, 286,439 (68.9%) are hypothetical, only 137 (0.033%) have EC annotations, and 346 (0.083%) map to KEGG. [src: alphafold_msa_annotation]

These proteins combine broad conservation with very limited detectable sequence representation. The report interprets them as a high-priority subset of the [[concepts/annotation-gap]]: unlike random accessory hypothetical proteins, their core status suggests biological importance, while their MSA depth of 1–9 indicates isolation from currently characterised sequence space. This interpretation is a strong prioritisation hypothesis rather than direct evidence of essentiality or biochemical function. [src: alphafold_msa_annotation]

Top-ranked examples with MSA depth = 1 primarily derive from poorly characterised marine and soil bacteria, including *Oceanicoccus*, *Dwaynesavagella*, and CAILRJ01. Some non-hypothetical examples include an RNA polymerase omega-subunit family protein and an FXSXX-COOH domain protein without a solved structure for the relevant lineages. [src: alphafold_msa_annotation]

## Resolving the pangenome annotation pattern

Core genes have a much lower overall hypothetical rate than accessory genes: 3.8% versus 11.6% for auxiliary non-singletons and 13.8% for auxiliary-plus-singleton clusters. Chi-square tests are overwhelmingly significant (χ² > 500,000; p ≈ 0), with odds ratios of 0.25 and 0.31 for core versus the two accessory comparisons. [src: alphafold_msa_annotation]

The report distinguishes two annotation-gap mechanisms:

1. **Pangenome-class gap:** Accessory and singleton genes are more often hypothetical, plausibly because of horizontal transfer, rapid evolution, or narrow taxonomic distribution.
2. **MSA-depth-driven gap:** Within every class, low MSA depth corresponds to sparse domain annotation; in core genes, the low-depth subset has a 68.9% hypothetical rate despite the 3.8% global core rate.

Therefore, the apparent contradiction between better annotation of core genes overall and the existence of many poorly characterised core proteins is resolved by conditioning on MSA depth. [src: alphafold_msa_annotation]

## Interpretation and limitations

The report argues that MSA depth reflects the number of detectable evolutionary relatives and therefore overlaps with the sequence space used to build domain resources such as Pfam, Gene3D, SUPERFAMILY, and PANTHER. It should be treated as a useful annotation-knowledge proxy, not as an interchangeable causal measure of functional knowledge. [src: alphafold_msa_annotation]

Important limitations are:

- AlphaFold bridge coverage is only 29.3% and is biased toward well-studied organisms.
- MSA depth is assigned to the representative sequence, ignoring within-cluster diversity.
- The 293,000 genomes are taxonomically imbalanced, with common taxa such as *Pseudomonas* and *E. coli* over-represented.
- The reported Spearman correlation is not stratified by pangenome class or organism-level annotation bias.
- MSA depths come from a static BERDL AlphaFold version-6 snapshot and may change as databases grow.

## Follow-up analyses

- Experimentally characterise the top 1,000 paradox proteins using structural-genomics pipelines, cryo-EM, or AlphaFold-guided construct design.
- Recompute the MSA-depth/domain-richness relationship separately for core, auxiliary, and singleton classes.
- Compare AlphaFold MSA depth with the MSA-independent [[entities/esmfold]] confidence signal to separate sequence novelty from foldability.
- Map paradox proteins onto the [[entities/gtdb]] phylogeny to identify lineages enriched for conserved-yet-novel proteins.
- Join paradox proteins with [[entities/fitness-browser]] measurements to test whether any are conditionally essential or experimentally linked to growth phenotypes.

These analyses would test whether low-depth core proteins are genuinely novel structural families, identify taxonomic hotspots of unexplored biology, and connect computational novelty to experimentally observed function. [src: alphafold_msa_annotation]

## Related Concepts
- [[concepts/gene-essentiality]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/multi-omics-integration]]

## Entities
- [[entities/alphafold-protein-structure-database]]
- [[entities/interproscan]]
- [[entities/berdl]]
- [[entities/random-barcode-transposon-sequencing]]
