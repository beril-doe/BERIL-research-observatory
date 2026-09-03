---
sources: ["summaries/amr_cofitness_networks__REPORT.md"]
type: "Dataset"
description: "Legacy annotation dataset used for comparison with InterProScan GO."
---

# SEED

## Overview

SEED is a legacy functional-annotation source used in the [[entities/fitness-browser]] comparison for AMR cofitness analysis. [src: amr_cofitness_networks]

## Role in the AMR cofitness analysis

The report compared SEED/KEGG annotations with uniformly computed [[entities/interproscan]] Gene Ontology annotations to assess functional enrichment in AMR support networks. [src: amr_cofitness_networks]

SEED annotation coverage varied between 40% and 80% across organisms, whereas the InterProScan GO annotations provided more uniform coverage. [src: amr_cofitness_networks]

Using legacy SEED annotations, none of 280 enrichment tests reached FDR < 0.05, and no GO terms were significantly enriched in at least three organisms. [src: amr_cofitness_networks]

The same cofitness data analyzed with InterProScan GO annotations produced 35 significant results among 3,193 tests, including recurring enrichment for flagellar motility and amino-acid biosynthesis. [src: amr_cofitness_networks]

## Interpretation

The comparison identifies an [[concepts/annotation-gap]]: annotation coverage and consistency can determine whether functional structure is detectable in genome-wide cofitness analyses. [src: amr_cofitness_networks]

The null result from SEED annotations does not establish that AMR support networks lack functional enrichment, because incomplete or uneven annotations can reduce statistical power. [src: amr_cofitness_networks]

The report also cautions that enrichment detected after improving annotations may still reflect [[concepts/shared-dispensability]] rather than direct co-regulation, particularly for flagellar and biosynthetic functions under standard Fitness Browser laboratory conditions. [src: amr_cofitness_networks]

## Related pages

- [[entities/fitness-browser]]
- [[entities/interproscan]]
- [[entities/kegg]]
- [[concepts/annotation-gap]]
- [[concepts/cofitness-networks]]
- [[concepts/shared-dispensability]]
- [[summaries/amr_cofitness_networks__REPORT]]