---
type: "Summary"
description: "Pilot GapMind analysis finds near-universal metabolism with a possible serine gap in D. vulgaris."
doc_type: short
full_text: "sources/essential_metabolome__REPORT.md"
---

# Essential Metabolome GapMind Analysis

## Overview

This report analyzes [[entities/gapmind]] pathway-completeness predictions for seven organisms associated with essential-gene research. It evaluates amino acid biosynthesis, carbon-source utilization, and the availability of GapMind predictions for the intended organism set. The analysis supports [[concepts/pathway-completeness]] as a near-universal rather than strictly universal property, while emphasizing substantial coverage and prediction limitations. [src: essential_metabolome]

## Key Findings

### Amino Acid Biosynthesis

- **17 of 18** amino acid biosynthesis pathways were complete or likely complete in **all 7 organisms** analyzed: arginine, asparagine, chorismate, cysteine, glutamine, glycine, histidine, isoleucine, leucine, lysine, methionine, phenylalanine, proline, threonine, tryptophan, tyrosine, and valine. [src: essential_metabolome]
- Serine biosynthesis was complete or likely complete in **6 of 7 organisms (85.7%)**. [src: essential_metabolome]
- [[entities/desulfovibrio-vulgaris]] was the only organism lacking a complete serine pathway prediction, with **17/18 pathways (94.4%)** complete. The other six organisms had **18/18 (100%)**. [src: essential_metabolome]
- The result indicates strong conservation of amino acid biosynthesis in this sample, but it does not establish pan-bacterial universality because the sample contains only seven organisms and is phylogenetically limited. [src: essential_metabolome]

### Possible *D. vulgaris* Serine Auxotrophy

The apparent serine pathway gap in [[entities/desulfovibrio-vulgaris]] is consistent with a possible [[concepts/auxotrophy]], particularly because the organism occupies anaerobic, organic-rich environments where amino acids may be available through protein degradation. However, this interpretation remains a hypothesis: GapMind may have missed a non-canonical or divergent pathway, or relevant genes may be unannotated. Experimental growth tests on serine-free minimal medium would be needed to confirm auxotrophy. [src: essential_metabolome]

### Carbon-Source Utilization

The most widely conserved carbon sources were present in all seven organisms (**87.5%** of the sample):

- TCA-cycle intermediates: fumarate and succinate
- Fermentation products: acetate, propionate, and L-lactate
- Amino acids as carbon sources
- Nucleotide derivatives: deoxyribose and deoxyribonate
- Polyamines: putrescine

Ethanol and deoxyinosine were present in six of seven organisms (**75%**). These observations suggest broadly shared central catabolic capacity, but the report treats them as sample-level findings rather than universal bacterial properties. [src: essential_metabolome]

## GapMind Coverage Limitation

The intended analysis was based on 45 organisms with essential-gene data, but [[entities/escherichia-coli]] K-12 had **0** GapMind predictions and was absent from the relevant KBase pangenome collection. The report attributes this exclusion to *E. coli* having too many genomes for species-level GTDB pangenome construction. [src: essential_metabolome]

GapMind predictions were available for the other seven mapped organisms, ranging from **694** predictions for *D. vulgaris*, [[entities/shewanella-oneidensis]], and [[entities/caulobacter-vibrioides]] to **1,786** for [[entities/azospirillum-brasilense]]. The resulting analysis is therefore a seven-organism pilot rather than the planned 45-organism comparison. This limitation is relevant to [[concepts/coverage-limited-inference]] and to interpretation of [[concepts/gene-essentiality]]. [src: essential_metabolome]

## Interpretation and Hypothesis Outcome

The report’s revised hypothesis was that a core set of metabolic pathways is universally complete across bacteria. The evidence **partially supports** this hypothesis:

- Supported: amino acid pathways were highly conserved, most carbon-source pathways were widely shared, and a minimal metabolic repertoire was apparent in the sample.
- Not supported: no pathway was strictly universal across all evaluated pathway-organism combinations, and the *D. vulgaris* serine gap demonstrates organism-specific variation.

The report therefore favors the conclusion that bacterial metabolism exhibits **near-universal conservation with ecological and phylogenetic exceptions**, rather than strict universality. [src: essential_metabolome]

## Limitations

- Only **7 organisms** were analyzed instead of 45, with limited phylogenetic diversity.
- GapMind coverage for the remaining 38 essential-gene organisms is unknown.
- GapMind predictions are computational and may miss divergent, non-canonical, partial, or poorly annotated pathways.
- The analysis included “complete” and “likely_complete” predictions, which may not correspond directly to experimentally demonstrated pathway function.
- RB-TnSeq essential-gene experiments were conducted in rich media, so biosynthetic genes may appear non-essential because metabolites were supplied externally. Pathway completeness therefore cannot be equated with viability essentiality. [src: essential_metabolome]

## Data and Reproducibility

The analysis used `kbase_ke_pangenome` tables `gapmind_pathways` and `genome`, plus `projects/essential_genome/essential_families.tsv`. Generated outputs included pathway-completeness tables, raw GapMind predictions for **7,389** records, and manual organism-to-genome mappings. The principal analysis notebook was `02_gapmind_pathway_analysis.ipynb`; the visualization was `pathway_completeness.png`. [src: essential_metabolome]

## Follow-up Directions

1. Check lower-confidence GapMind results and the literature for experimental evidence of *D. vulgaris* serine auxotrophy.
2. Expand organism-to-genome mappings to recover more of the 45 essential-gene organisms.
3. Use [[entities/eggnog]] EC annotations and [[entities/kegg]] pathways to include *E. coli* and organisms absent from GapMind.
4. Combine GapMind pathway-level predictions with gene-level annotations.
5. Link essential gene families directly to pathway completeness and test whether pathway presence predicts [[concepts/condition-dependent-essentiality]].
6. Analyze whether pathway gaps cluster by phylogeny or ecological niche.

These directions connect pathway completeness with [[concepts/auxotrophy]], [[concepts/gene-essentiality]], [[concepts/condition-dependent-essentiality]], and [[concepts/organism-specificity]]. [src: essential_metabolome]

## Related Concepts
- [[concepts/metabolic-support-networks]]
- [[concepts/pangenome-integration]]
- [[concepts/method-concordance]]
- [[concepts/resource-darkness]]

## Entities
- [[entities/modelseed]]
- [[entities/flux-balance-analysis]]
