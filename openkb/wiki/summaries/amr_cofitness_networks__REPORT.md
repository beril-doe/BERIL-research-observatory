---
type: "Summary"
description: "Pan-bacterial AMR cofitness networks are organism-specific and annotation-sensitive."
doc_type: short
full_text: "sources/amr_cofitness_networks__REPORT.md"
---

# AMR Co-Fitness Support Networks

## Overview

This report presents the first pan-bacterial mapping of antimicrobial-resistance (AMR) gene cofitness neighborhoods across 28 organisms. It combines Fitness Browser fitness matrices, ICA fitness modules, AMR gene catalogs, and InterProScan functional annotations to test whether AMR genes share support networks, whether those networks differ by resistance mechanism, and whether network size predicts fitness cost. The main findings concern [[concepts/cofitness-networks]], [[concepts/organism-specificity]], [[concepts/annotation-gap]], and the [[concepts/shared-dispensability]] confound in functional interpretation.

## Dataset and approach

- The analysis included 28 organisms with AMR genes, fitness matrices, and ICA modules.
- There were 801 AMR genes with fitness data; 769 (96%) had at least one extra-operon cofitness partner at |r| > 0.3.
- The analysis identified 180,370 total cofitness partners, including 179,375 extra-operon partners.
- Mean support-network size was 233 genes at |r| > 0.3, 110 at |r| > 0.4, and 71 at |r| > 0.5.
- [[entities/interproscan]] GO annotations provided 68% gene coverage, compared with lower and more variable coverage from legacy SEED/KEGG annotations.

## Key findings

### AMR genes occupy large, conserved modules

Only 192 of 801 AMR genes (24%) were assigned to ICA fitness modules. AMR-containing modules were significantly larger than non-AMR modules, with median sizes of 46 and 27 genes, respectively (MWU p = 1.7×10⁻⁸). Of 209 AMR gene–module assignments, 208 (99%) belonged to cross-organism conserved module families. Module size did not differ among efflux, enzymatic, and metal-resistance mechanisms (median 48; MWU p = 0.91). These results support the view that AMR genes that participate in condition-specific programs are embedded in broad cellular systems rather than small isolated units.

### Flagellar and amino-acid functions are enriched, but interpretation is unresolved

Using [[entities/interproscan]] GO annotations, AMR support networks showed significant enrichment for flagellum-dependent motility, flagellum assembly, bacterial-type flagella, flagellum-dependent swarming, histidine biosynthesis, and tryptophan biosynthesis. The six top terms were enriched across three to five organisms, with mean odds ratios from 4.7 to 5.3. The old SEED annotation analysis detected no significant enrichment in 280 tests, whereas the InterProScan analysis detected 35 significant results among 3,193 tests.

The enrichment may indicate genuine co-regulation linking AMR, motility, signaling, and biosynthesis. However, it may instead reflect [[concepts/shared-dispensability]]: AMR genes are often unnecessary without antibiotics, flagella are of limited value in shaken liquid culture, and biosynthetic genes can be redundant in supplemented media. Shared responses to laboratory conditions could generate cofitness without direct regulatory linkage. A fitness-matched permutation test is therefore required before treating the flagellar and biosynthetic signals as AMR-specific biology.

### Support networks are primarily organism-specific

Support networks differed more by organism than by AMR mechanism. Within the same organism, different mechanisms had a mean GO-term Jaccard similarity of 0.375, whereas the same mechanism across organisms had a mean similarity of 0.207; the difference was highly significant (MWU p = 4.3×10⁻¹³). Thus, an organism’s regulatory, metabolic, and signaling architecture appears to shape AMR support networks more strongly than whether resistance is mediated by efflux, enzymatic inactivation, or metal resistance.

The conserved core across mechanisms included transmembrane transport (87–100% of organisms), signal transduction (87–100%), transcription regulation (96–100%), and phosphorelay signaling (91–100%). Flagellar motility occurred in 53–61% of organisms and amino-acid biosynthesis in 30–73%. No mechanism-specific GO term remained significant after FDR correction; histidine biosynthesis showed the strongest uncorrected hint of specificity, with efflux at 68% versus metal resistance at 30% of organisms (p = 0.013; q = 0.18).

### Network size does not explain AMR fitness cost

There was no relationship between support-network size and AMR gene fitness cost (Spearman rho = −0.006, p = 0.87, N = 769). The null result held separately for efflux (rho = −0.049), enzymatic resistance (rho = +0.038), and metal resistance (rho = −0.031), with all p-values > 0.4. The approximately uniform resistance cost of +0.086 was therefore not explained by the size of the co-regulatory neighborhood.

This result complements the distinction between AMR fitness cost and AMR conservation: resistance mechanism may influence evolutionary conservation or accessory-gene status without determining the measured fitness cost.

### Annotation quality changes the biological conclusion

Replacing legacy SEED/KEGG annotations with uniformly computed [[entities/interproscan]] GO annotations converted a null enrichment result into a significant one. Cross-organism Jaccard similarity also increased: within-mechanism similarity rose from 0.069 to 0.207, and cross-mechanism similarity from 0.249 to 0.375. The report therefore identifies annotation coverage and consistency as methodological determinants of genome-wide cofitness inference, not merely technical details.

## Interpretation and limitations

The organism-specificity result is considered robust because it concerns the relative structure of support networks and persists despite uncertainty about why individual functions co-vary. The larger-module result is likewise interpreted as evidence that AMR genes can participate in broad condition-specific programs. In contrast, the flagellar and amino-acid enrichment is provisional because cofitness measures shared fitness phenotypes rather than direct transcriptional regulation.

Important limitations include the [[concepts/shared-dispensability]] confound, large support networks at |r| > 0.3, broad GO-term granularity, limited variance in fitness costs, phylogenetic and ecological bias among the 28 organisms, and an operon-exclusion heuristic based on matrix row position rather than genomic coordinates. Missing fitness values were treated as zero in z-score space, approximating but not exactly reproducing pairwise-complete Pearson correlation.

## Open directions

1. Perform a fitness-matched permutation using random non-AMR genes with the same mean-fitness distribution as AMR genes.
2. Recompute cofitness separately under antibiotic stress and standard growth conditions to test whether AMR–motility associations are condition-specific.
3. Directly measure the mean fitness of flagellar-gene knockouts across Fitness Browser experiments.
4. Test Pfam-domain enrichment, which has 88% coverage and may provide more specific signals than broad GO terms.
5. Compare AMR genes with other conditionally dispensable classes, including phage-defense and secondary-metabolite genes.

## Source

[src: amr_cofitness_networks]

## Related Concepts
- [[concepts/condition-dependent-essentiality]]
- [[concepts/method-concordance]]
- [[concepts/gene-essentiality]]
- [[concepts/pangenome-integration]]

## Entities
- [[entities/independent-component-analysis]]
- [[entities/seed]]
- [[entities/kegg]]
- [[entities/flagellar-motility]]
- [[entities/histidine-biosynthesis]]
- [[entities/tryptophan-biosynthesis]]
- [[entities/fitness-browser]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/berdl]]
