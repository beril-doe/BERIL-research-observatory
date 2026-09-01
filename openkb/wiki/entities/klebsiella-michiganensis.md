---
sources: ["summaries/annotation_gap_discovery__REPORT.md"]
type: "Organism"
description: "Fitness Browser organism with the highest reported annotation-gap resolution rate"
---

# Klebsiella michiganensis

*Klebsiella michiganensis* is a bacterial organism represented in the Fitness Browser dataset and identified as “Koxy” in the annotation-gap discovery study. [src: annotation_gap_discovery]

## Role in Annotation-Gap Discovery

The study selected *K. michiganensis* among 14 organisms with rich carbon-source RB-TnSeq coverage and used its fitness data, draft metabolic model, pangenome annotations, GapMind results, Bakta annotations, and sequence-homology evidence in an integrated [[concepts/evidence-triangulation]] pipeline. [src: annotation_gap_discovery]

*K. michiganensis* had 7 evaluated gapfilled reaction–organism pairs, of which 5 were resolved, giving it a resolution rate of 71.4%. This was the highest organism-level rate reported in the study. [src: annotation_gap_discovery]

## Interpretation

The high rate for *K. michiganensis* demonstrates strong organism-specific variation in [[concepts/annotation-gap]] resolution. The report associates higher resolution with better-annotated reference genomes and stronger Fitness Browser coverage, although it does not establish that either factor caused the observed rate. [src: annotation_gap_discovery]

The organism was evaluated using conditional [[concepts/metabolic-model-gapfilling]]: gapfilled reactions were added to draft models when baseline flux-balance analysis failed to reproduce observed growth. [src: annotation_gap_discovery]

## Related Resources

- [[summaries/annotation_gap_discovery__REPORT]]
- [[entities/fitness-browser]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/modelseed]]
- [[concepts/organism-specificity]]
- [[concepts/pangenome-integration]]