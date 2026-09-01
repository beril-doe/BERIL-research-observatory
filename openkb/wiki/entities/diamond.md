---
sources: ["summaries/pitfalls.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/ecotype_functional_differentiation__REPORT.md", "summaries/discoveries.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md"]
type: "Method"
description: "Protein-sequence comparison method supporting pangenome and annotation-gap resolution"
---

# DIAMOND

## Overview

DIAMOND is a protein-sequence comparison method used in the [[summaries/amr_pangenome_atlas__REPORT]] to connect pangenome gene clusters with genes in the [[entities/fitness-browser]]. [src: amr_pangenome_atlas] In [[summaries/annotation_gap_discovery__REPORT]], DIAMOND was used to compare target proteomes with Swiss-Prot exemplar sequences as part of a multi-evidence metabolic annotation-gap resolution pipeline. [src: annotation_gap_discovery]

## Use in the AMR Pangenome Atlas

The analysis used a DIAMOND-based Fitness Browser–pangenome link table with a conservative 100% sequence-identity threshold. [src: amr_pangenome_atlas] The table contained 177,863 links and was used to identify AMR genes that could be associated with Fitness Browser fitness measurements. [src: amr_pangenome_atlas]

This cross-reference yielded 178 AMR genes across 37 Fitness Browser organisms and 29,386 fitness measurements. [src: amr_pangenome_atlas] The resulting analysis found that AMR genes had a median fitness of -0.007 versus -0.012 for the non-AMR baseline, although the report cautions that the linked organisms were predominantly environmental and may not represent recently acquired mobile resistance in clinical pathogens. [src: amr_pangenome_atlas]

## Use in Annotation-Gap Discovery

The annotation-gap study used DIAMOND v2.1.16 blastp with `--evalue 1e-5 --max-target-seqs 20 --id 25 --query-cover 50 --outfmt 6`. [src: annotation_gap_discovery] The search used 328 reviewed bacterial Swiss-Prot exemplar sequences representing 75 of 84 unique EC numbers retrieved through the UniProt REST API. [src: annotation_gap_discovery]

The search produced 154 BLAST hits against concatenated target proteomes. [src: annotation_gap_discovery] Hits were assessed with medium-confidence thresholds of at least 25% identity, at least 50% coverage, and an e-value of at most 1e-5, while high-confidence hits required at least 30% identity, at least 70% coverage, and an e-value of at most 1e-10. [src: annotation_gap_discovery]

BLAST alone resolved 70 of 201 gapfilled reaction–organism pairs (34.8%), making it the most impactful single evidence stream in the study. [src: annotation_gap_discovery] Integrating DIAMOND results with EC matching, Bakta annotations, fitness evidence, and pangenome conservation increased resolution to 96 of 201 pairs (47.8%). [src: annotation_gap_discovery] The top reactions by BLAST hit count included rxn02185, rxn03436, and rxn15947, which the report describes as well-characterized enzymes with broad phylogenetic distribution. [src: annotation_gap_discovery]

## Interpretation and Limitations

The 100% identity criterion used in the AMR pangenome analysis reduces paralog confusion and makes the links conservative, but it can miss closely related allelic variants, including variants differing by a single synonymous substitution. [src: amr_pangenome_atlas] Consequently, the Fitness Browser cross-reference may undercount AMR gene fitness effects. [src: amr_pangenome_atlas]

In the annotation-gap study, DIAMOND provided the strongest individual evidence stream but still resolved fewer pairs than the complete evidence-integration pipeline. [src: annotation_gap_discovery] Its effectiveness was also limited for “dark reactions”: reactions without ModelSEED EC numbers, for which sequence-homology searches and functional cross-referencing are more difficult. [src: annotation_gap_discovery]

The AMR pangenome report contains a coverage discrepancy that should be reconciled: the narrative describes 178 AMR genes across 37 organisms, while the generated-data table describes fitness measurements for 162 AMR genes in 36 organisms. [src: amr_pangenome_atlas]

DIAMOND therefore serves as a [[concepts/pangenome-integration]] method connecting [[concepts/core-accessory-resistance]] patterns to experimental gene-fitness data, and as an important [[concepts/evidence-triangulation]] component for resolving metabolic annotation gaps. [src: amr_pangenome_atlas, annotation_gap_discovery] Its matching thresholds and dependence on characterized exemplar sequences define important boundaries on both applications. [src: amr_pangenome_atlas, annotation_gap_discovery]

See also: [[summaries/discoveries]]

See also: [[summaries/ecotype_functional_differentiation__REPORT]]

See also: [[summaries/lanthanide_methylotrophy_atlas__REPORT]]

See also: [[summaries/pitfalls]]