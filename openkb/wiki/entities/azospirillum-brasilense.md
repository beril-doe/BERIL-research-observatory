---
sources: ["summaries/annotation_gap_discovery__REPORT.md"]
type: "Organism"
description: "Bacterial Fitness Browser organism with 61.9% annotation-gap resolution."
---

# Azospirillum brasilense

*Azospirillum brasilense* is one of the 14 organisms analyzed in the annotation-gap discovery study, where it is identified by the shorthand **azobra**. [src: annotation_gap_discovery]

## Role in the Study

The organism was selected from the [[entities/fitness-browser]] collection because it had rich carbon-source RB-TnSeq coverage for integration with metabolic-model gapfilling and pangenome evidence. [src: annotation_gap_discovery] Its analysis illustrates the study's [[concepts/evidence-triangulation]] approach to [[concepts/annotation-gap]] resolution. [src: annotation_gap_discovery]

## Annotation-Gap Results

The study evaluated 21 gapfilled reaction–organism pairs for *A. brasilense* and assigned candidate genes to 13 of them, for a resolution rate of **61.9%**. [src: annotation_gap_discovery] This was the third-highest organism-level resolution rate reported in the study, following *Klebsiella michiganensis* at 71.4% and *Marinobacter* at 66.7%. [src: annotation_gap_discovery]

Candidate identification combined EC-based matching, alternative [[entities/bakta]] annotations, pangenome conservation, fitness profiles, and [[entities/diamond]] sequence homology. [src: annotation_gap_discovery] The pangenome and fitness components were intended to support evidence transfer across organisms rather than resolving each organism in isolation. [src: annotation_gap_discovery]

## Interpretation

The 61.9% resolution rate indicates that a majority of the evaluated gapfilled pairs in *A. brasilense* received candidate gene assignments under the study's confidence framework. [src: annotation_gap_discovery] Because the analysis used draft models, non-unique [[entities/modelseed]] gapfill solutions, manually curated carbon-source mappings, and fitness data with organism-dependent coverage, these assignments require experimental validation rather than being treated as uniformly confirmed functions. [src: annotation_gap_discovery]

The organism provides a comparison point for [[concepts/organism-specificity]] in annotation-gap resolution: rates differed from 20% in *Bacteroides thetaiotaomicron* to 71.4% in *Klebsiella michiganensis* across the study organisms. [src: annotation_gap_discovery]

## Source

- [[summaries/annotation_gap_discovery__REPORT]] — integrated phenotype, fitness, pangenome, GapMind, and BLAST analysis of metabolic annotation gaps. [src: annotation_gap_discovery]
