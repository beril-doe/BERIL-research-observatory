---
type: "Summary"
description: "Pangenome-scale atlas linking prophage prevalence with AMR co-localization and repertoire breadth."
doc_type: short
full_text: "sources/prophage_amr_comobilization__REPORT.md"
---

# Prophage-AMR Co-mobilization Atlas

## Overview

This report evaluates whether prophage markers are associated with the distribution, genomic proximity, and potential mobility of antimicrobial-resistance (AMR) genes across the BER pangenome. It combines a pangenome-scale census, gene-neighborhood analysis, species-level correlation tests, and an attempted fitness-cost comparison. The report contributes to the cross-document themes of [[concepts/core-accessory-resistance]], [[concepts/mobile-genetic-elements]], [[concepts/horizontal-gene-transfer]], pangenome openness, and [[concepts/fitness-conservation]].

## Key Findings

### AMR and prophage co-localization

Among AMR gene instances in the 100 most AMR-burdened species, 55.7% occurred on contigs carrying strict prophage markers. The median distance from a co-localized AMR gene to the nearest prophage marker was 34 genes, and 10.4% of all AMR genes were within 10 genes of a prophage marker. The analysis covered 36,041 AMR gene instances from 1,953 genomes, sampling up to 20 genomes per species.

Across the full pangenome, the study identified 83,008 AMR gene clusters and 3,465,244 broad prophage-marker clusters, including 1,261,929 strict-marker clusters. Of 27,702 species, 14,669 (52.9%) carried both AMR and prophage markers. Prophage markers were more frequently accessory and singleton than AMR genes: 83.8% of prophage clusters were accessory and 53.8% singleton, compared with 69.7% and 36.1% for AMR clusters.

### Proximity is only a weak and heterogeneous mobility proxy

AMR genes within 10 genes of a prophage marker were modestly more likely to be accessory than more distant AMR genes: 67.6% versus 65.5%. This difference was statistically significant (Fisher's exact OR=1.10, p=0.005; bootstrap 95% CI [1.024, 1.185]) but small.

The result depended strongly on the distance threshold. The association was absent or reversed at very close distances (OR=0.78 at 3 genes and OR=0.92 at 5 genes), then increased at broader thresholds (OR=1.19 at 15 genes and OR=1.28 at 50 genes). Only 33 of 74 testable species had species-level OR>1, with a median species-level OR of 0.85. These results weaken any simple claim that immediate prophage proximity reliably identifies recently mobilized AMR cargo. The report instead suggests that broader genomic islands containing both prophage remnants and laterally acquired genes may account for part of the aggregate association, consistent with [[concepts/gene-neighborhood-inference]] and [[concepts/resistance-islands]].

### Prophage density predicts AMR repertoire breadth

The strongest result was a species-level relationship between prophage density and AMR repertoire breadth. Across 4,770 species, Spearman correlation was rho=0.572 with p<10^-300. A log-log model estimated a slope of 0.823 (SE=0.018; p<10^-300; R²=0.30), meaning that a 10-fold increase in prophage density predicted an approximately 6.6-fold increase in AMR breadth. The association remained strong after controlling for genome count (partial Spearman rho=0.464, p=1.0×10^-253).

The correlation was observed across five major phyla: Pseudomonadota (rho=0.54), Bacillota_A (rho=0.55), Bacillota (rho=0.40), Bacteroidota (rho=0.59), and Actinomycetota (rho=0.29). This broad phylogenetic consistency argues against a purely lineage-specific explanation, although the observational design cannot distinguish direct phage-mediated transfer from shared propensity for gene acquisition. The need to separate association from lineage effects connects this result to [[concepts/phylogenetic-confounding]] and [[concepts/phylogenetic-amr-structure]].

### Fitness-cost comparison was not testable

The attempted comparison of fitness costs could not be completed because the BERDL Fitness Browser contained RB-TnSeq data for only 48 model organisms, with limited overlap with the GTDB pangenome species. Whether prophage-proximal AMR genes have distinct fitness effects therefore remains unresolved and is an open question for [[concepts/fitness-conservation]] and [[concepts/coverage-limited-inference]].

## Interpretation and Mechanisms

The prophage-density result is consistent with two non-exclusive mechanisms. First, prophages may directly mobilize AMR genes through specialized or generalized transduction. Second, species containing many prophages may have generally higher recombination or gene-acquisition potential and may independently accumulate both prophages and AMR genes through multiple mobile-element classes. The report therefore treats the species-level association as strong correlational evidence, not proof of phage-mediated AMR transfer. This distinction is central to [[concepts/horizontal-gene-transfer]] and [[concepts/mobile-genetic-elements]].

The threshold-dependent gene-level result provides an important qualification. Very close neighbors of phage structural genes may be conserved phage components rather than recently acquired resistance cargo, explaining the reversal at 3–5 genes. Associations at 15–50 genes may instead capture larger genomic islands containing prophage remnants, AMR genes, and other mobile elements.

The report places its findings in the context of prior studies linking capsules, prophages, and AMR across bacterial pangenomes; detecting ARG–MGE associations in river metagenomes; and experimentally demonstrating phage-mediated transfer of resistance plasmids or chromosomal islands in *Salmonella* and *Staphylococcus epidermidis*. These studies motivate the phage-mediated gene-transfer hypothesis but do not establish that the associations observed here are causally mediated by prophages.

## Limitations

- Prophage markers were identified through keyword and Pfam matching in bakta annotations rather than dedicated tools such as geNomad or PHASTER, allowing false positives and missed divergent prophages.
- Gene distances are ordinal positions parsed from gene identifiers, not base-pair distances from genome sequences.
- Gene-neighborhood analysis sampled 20 genomes per species rather than all 293,000 genomes.
- Core/accessory assignments depend on species-level motupan pangenomes; conservation status may differ for homologous genes across species.
- The H2 association remains correlational and could reflect open pangenomes or other mobile elements rather than prophage-mediated transfer.
- Limited overlap with fitness-browser organisms prevented testing H3.

These constraints illustrate broader issues of [[concepts/annotation-gap]], [[concepts/coverage-limited-inference]], [[concepts/pangenome-integration]], and [[concepts/computational-reproducibility]].

## Data and Reproducibility

The analysis used `bakta_amr`, `bakta_annotations`, `bakta_pfam_domains`, gene and gene-cluster tables, genome and pangenome metadata, GTDB taxonomy, and attempted Fitness Browser tables. Generated files include AMR and prophage cluster inventories, species summaries, AMR–prophage distances, and JSON results for the census, H1, H2, H3, and integrated synthesis. Supporting notebooks were `01_amr_prophage_census.py`, `02_gene_neighborhood_coloc.py`, `03_conservation_test.py`, `04_species_breadth_test.py`, and `05_synthesis.py`.

## Future Directions

1. Re-run prophage identification with geNomad or PHASTER to test whether the associations survive validated prophage calls.
2. Use contig sequences to calculate base-pair distances and distinguish true neighborhood structure from ordinal gene-position effects.
3. Expand Fitness Browser coverage and test whether prophage-proximal AMR genes have different measured fitness costs.
4. Partition prophage, plasmid, and integrative-conjugative-element contributions to AMR co-localization.
5. Analyze all available genomes from *Klebsiella pneumoniae*, *Acinetobacter baumannii*, *Pseudomonas aeruginosa*, and *Escherichia coli* to assess clinical-pathogen-specific patterns.

## Bottom Line

Prophage markers are widespread alongside AMR genes, and prophage density is a robust species-level predictor of AMR repertoire breadth. However, local prophage proximity is only a weak, threshold-sensitive, and species-heterogeneous indicator of AMR mobility; dedicated prophage calls, sequence-resolved distances, and expanded fitness and mobile-element data are needed to test causality.

## Related Concepts
- [[concepts/two-speed-genome]]
- [[concepts/evidence-triangulation]]
