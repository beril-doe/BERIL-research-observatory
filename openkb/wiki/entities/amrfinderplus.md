---
sources: ["summaries/pitfalls.md", "summaries/functional_dark_matter__REPORT.md", "summaries/discoveries.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md"]
type: "Method"
description: "AMR annotation method used to identify resistance genes and gene clusters"
---

# AMRFinderPlus

## Overview

AMRFinderPlus is an antimicrobial-resistance annotation method used to detect known AMR genes and gene clusters, including antibiotic-resistance and broader stress-response determinants in the NCBI Reference Gene Catalog. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Role in the environmental-resistome study

The environmental-resistome study used Bakta/AMRFinderPlus-based annotations to assemble a dataset of **82,908 AMR gene clusters across 14,723 species**. [src: amr_environmental_resistome]

These annotations supported comparisons of AMR abundance and [[concepts/core-accessory-resistance]] composition across clinical, human-gut, soil, aquatic, host-associated, and other environmental species. [src: amr_environmental_resistome]

AMR gene names or product annotations were also used to classify clusters into enzymatic inactivation, metal resistance, target modification, or efflux mechanisms. **15,550 clusters (18.7%)** could not be assigned to a mechanism and were excluded from mechanism-fraction analyses. [src: amr_environmental_resistome]

## Role in the pan-bacterial AMR atlas

The pan-bacterial atlas reported **83,008 AMRFinderPlus hits** on gene-cluster representatives, covering **82,908 distinct clusters** across **14,723 species**. [src: amr_pangenome_atlas]

The hits represented **1,939 distinct AMR gene families** and **2,079 AMR products**. Detection methods were HMM (51.5%), BLASTP (22.7%), EXACTP (13.0%), PARTIALP (9.7%), and ALLELEP (3.0%). [src: amr_pangenome_atlas]

The atlas used AMRFinderPlus calls to show that AMR genes are depleted from bacterial core genomes: **30.3%** were core versus **46.8%** for the pangenome baseline (OR=0.49, chi-squared=23,117, p≈0), while the auxiliary genome was enriched for AMR (**33.6%** versus **15.3%**). [src: amr_pangenome_atlas]

AMRFinderPlus-derived calls also supported the distinction between conserved intrinsic resistance and accessory acquired resistance. Beta-lactamases were **54.9% core**, whereas regulatory genes were **6.5% core**; the named mobile elements blaTEM, tet(C), and ant(2'')-Ia were **0% core** in the atlas. [src: amr_pangenome_atlas]

## Role in the within-species strain-variation study

The within-species AMR strain-variation study used AMRFinderPlus-based AMR gene identification to construct genome-by-AMR presence/absence matrices for **180,025 genomes from 1,305 species**. [src: amr_strain_variation]

These calls produced **37,444 AMR gene-species records** and supported within-species classification into fixed, variable, and rare prevalence classes. Across species, **51.3%** of AMR gene-species occurrences were rare, **41.3%** were variable, and **7.5%** were fixed. [src: amr_strain_variation]

AMRFinderPlus-derived profiles were also used to calculate strain-level AMR Jaccard distances, detect **1,517 resistance islands**, test AMR phylogenetic signal against ANI distances, and identify AMR ecotypes. [src: amr_strain_variation]

The strain-variation report found that **77.3% of atlas-defined Core AMR genes were fixed** within species, whereas **78.7% of Singleton genes were rare**, linking AMRFinderPlus-based calls to validation of the atlas's [[concepts/core-accessory-resistance]] classification at strain resolution. [src: amr_strain_variation]

## Interpretation and limitation

AMRFinderPlus focuses on known resistance genes, which may underestimate novel resistance determinants in environmental bacteria and other under-characterized organisms. [src: amr_environmental_resistome, amr_strain_variation]

This limitation can bias comparisons toward higher apparent AMR abundance in clinical species, where resistance genes are better characterized. [src: amr_environmental_resistome]

The pan-bacterial atlas emphasizes that AMRFinderPlus has a broad scope: mercury-resistance families such as merA and merP and arsenic-resistance families such as arsD and arsC are prominent in the catalog. Consequently, the **83,008 hits are not all antibiotic-resistance genes**, and AMR counts can include metal and other stress-response systems. [src: amr_pangenome_atlas]

Mechanism classification in the atlas used keyword matching against AMRFinderPlus product descriptions rather than the CARD Antibiotic Resistance Ontology. This left **22.2%** of hits in an Other/Unclassified category, including products whose names did not match the keyword sets. [src: amr_pangenome_atlas]

The strain-variation study similarly treated AMR gene identification as dependent on the AMRFinderPlus database and noted that novel resistance mechanisms absent from that database would be missed. [src: amr_strain_variation]

Because AMRFinderPlus-derived annotations form the basis for resistome profiles, its sensitivity, reference-gene scope, and annotation coverage directly affect estimates of total AMR, core versus accessory resistance, within-species prevalence, resistance-island composition, and mechanism-specific environmental differences. [src: amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation]

Singleton AMR clusters or rare within-species AMR calls may reflect annotation artifacts rather than true species-specific or strain-specific resistance genes. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Related pages

- [[concepts/environmental-resistome]]
- [[concepts/core-accessory-resistance]]
- [[concepts/resistance-islands]]
- [[concepts/phylogenetic-amr-structure]]
- [[summaries/amr_environmental_resistome__REPORT]]
- [[summaries/amr_pangenome_atlas__REPORT]]
- [[summaries/amr_strain_variation__REPORT]]

See also: [[summaries/amr_fitness_cost__REPORT]]

See also: [[summaries/bacdive_phenotype_metal_tolerance__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/pitfalls]]