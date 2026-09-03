---
sources: ["summaries/fw300_metabolic_consistency__REPORT.md", "summaries/discoveries.md", "summaries/amr_cofitness_networks__REPORT.md"]
type: "Gene_Or_Pathway"
description: "A biosynthetic pathway enriched in AMR cofitness neighborhoods."
---

# Tryptophan Biosynthesis

## Overview

Tryptophan biosynthesis is represented in this analysis by Gene Ontology term GO:0000162. [src: amr_cofitness_networks]

## Evidence from AMR cofitness networks

GO:0000162 was among the six functional terms most consistently enriched in antimicrobial-resistance (AMR) cofitness support networks, appearing significantly in 3 organisms with a mean odds ratio of 5.3. [src: amr_cofitness_networks]

The enrichment was detected using InterProScan GO annotations, whereas the corresponding analysis with legacy SEED annotations found no significant enrichment among 280 tests. [src: amr_cofitness_networks] This result illustrates the [[concepts/annotation-gap]] in genome-wide functional analyses and the importance of higher-coverage annotation from [[entities/interproscan]]. [src: amr_cofitness_networks]

By resistance mechanism, tryptophan biosynthesis was significantly enriched in support networks for efflux AMR genes in 5 organisms. [src: amr_cofitness_networks] No GO term, including tryptophan biosynthesis, was significantly mechanism-specific after FDR correction. [src: amr_cofitness_networks]

## Interpretation

The observed association may reflect genuine co-regulation between AMR genes and amino-acid biosynthetic functions, but it may also result from [[concepts/shared-dispensability]] under Fitness Browser laboratory conditions. [src: amr_cofitness_networks] Many experiments used rich or defined media with amino-acid supplementation, potentially making biosynthetic genes redundant and producing shared fitness responses without direct regulatory linkage. [src: amr_cofitness_networks]

The report therefore treats tryptophan-biosynthesis enrichment as suggestive rather than established evidence of a mechanistic AMR connection. [src: amr_cofitness_networks] A permutation analysis matching random non-AMR genes to AMR genes by mean fitness level is needed to determine whether the enrichment is specific to AMR genes. [src: amr_cofitness_networks]

## Related analysis

This pathway is discussed in the [[summaries/amr_cofitness_networks__REPORT]], which maps AMR cofitness neighborhoods across 28 organisms. [src: amr_cofitness_networks] The broader analysis found that support networks were more [[concepts/organism-specificity]] than mechanism-specific, with within-organism cross-mechanism GO-term Jaccard similarity of 0.375 versus 0.207 for the same mechanism across organisms (MWU p = 4.3×10⁻¹³). [src: amr_cofitness_networks]

See also: [[summaries/discoveries]]

See also: [[summaries/fw300_metabolic_consistency__REPORT]]