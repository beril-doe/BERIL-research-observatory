---
sources: ["summaries/ibd_phage_targeting__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md"]
type: "Dataset"
description: "A pathway-level dataset for annotating amino acid biosynthesis completeness"
---

# GapMind

## Identity

GapMind is a pathway-annotation resource and analysis system used to evaluate the completeness of amino acid and carbon-use pathways. [src: annotation_gap_discovery]

## Role in Annotation-Gap Discovery

In the [[summaries/annotation_gap_discovery__REPORT]] study, GapMind was integrated with [[entities/modelseed]] gapfilling, Fitness Browser evidence, pangenome data, [[entities/bakta]] annotations, and [[entities/diamond]] sequence homology as part of an [[concepts/evidence-triangulation]] workflow. [src: annotation_gap_discovery]

GapMind pathway predictions were compared with ModelSEED gapfilling results for 104 GapMind–gapfill pathway pairings. [src: annotation_gap_discovery] GapMind frequently marked pathways as `not_present` or `steps_missing` for carbon sources where ModelSEED required gapfilling, providing partial corroboration for the gapfilled models. [src: annotation_gap_discovery]

## Interpretation and Limitations

Exact agreement between GapMind and gapfilling was limited because GapMind reports pathway-level completeness and step counts, whereas the available BERDL data did not identify the specific individual steps represented by those counts. [src: annotation_gap_discovery]

GapMind covers approximately 80 carbon and amino acid pathways rather than full metabolism, so many gapfilled reactions fall outside its scope. [src: annotation_gap_discovery] Consequently, GapMind evidence can support or prioritize [[concepts/annotation-gap]] investigations but cannot independently resolve every reaction–gene assignment. [src: annotation_gap_discovery]

## Related Resources

- [[entities/modelseed]] — source of the metabolic-model gapfilling comparisons. [src: annotation_gap_discovery]
- [[entities/bakta]] — alternative annotation source used alongside GapMind. [src: annotation_gap_discovery]
- [[concepts/metabolic-model-gapfilling]] — broader framework in which GapMind pathway evidence was applied. [src: annotation_gap_discovery]
- [[concepts/method-concordance]] — relevant to interpreting the partial agreement between pathway predictions and gapfilling. [src: annotation_gap_discovery]

See also: [[summaries/ibd_phage_targeting__REPORT]]