---
type: "Summary"
description: "Fitness modules are enriched in conserved genes but show no breadth-conservation gradient."
doc_type: short
full_text: "sources/module_conservation__REPORT.md"
---

# Fitness Modules and Pangenome Conservation

## Overview

This analysis tests whether ICA-derived fitness modules and cross-organism module families are associated with pangenome conservation. It compares module genes with the genome-wide core-gene baseline and evaluates whether module-family breadth predicts conservation. [src: module_conservation]

## Key Findings

- **Module genes are modestly enriched in the conserved core genome:** 86.0% of module genes are core, compared with 81.5% of all genes, a difference of +4.5 percentage points (OR=1.46, p=1.6e-87). [src: module_conservation]
- **Most modules are predominantly core:** among 974 modules with at least three mapped genes, 577 (59%) are core modules (>90% core genes), 349 (36%) are mixed modules (50–90% core), and 48 (5%) are accessory modules (<50% core). The median module is 93.4% core. [src: module_conservation]
- **Family breadth does not predict conservation:** the relationship between the number of organisms spanned by a module family and its core fraction is effectively null (Spearman rho=-0.01, p=0.914). [src: module_conservation]
- **Accessory module families exist:** 38 families contain fewer than 50% core genes, potentially representing horizontally transferred functional units or niche-specific operons; this interpretation remains a hypothesis. [src: module_conservation]
- **Essential genes are absent from modules:** no essential genes occur in the analyzed modules, because ICA requires measurable fitness variation from genes with transposon insertion data. [src: module_conservation]

## Interpretation

The results support the conclusion that [[concepts/fitness-conservation]] preferentially occupies the conserved core-genome portion of bacterial genomes. However, the absolute enrichment is modest because the genome-wide core rate is already high, creating a ceiling effect. [src: module_conservation]

The null association between family breadth and conservation suggests that conservation may be primarily a property of individual genes rather than the cross-organism scope of their regulatory module. Because the analysis is observational and based on a 29/32-organism subset with pangenome links, this should be treated as an interpretation rather than a general law. [src: module_conservation]

The finding that 59% of modules are more than 90% core extends [[concepts/pangenome-integration]] from individual genes to functionally coherent, co-regulated units. The accessory families provide candidates for studying niche-specific or horizontally transferred regulatory modules. [src: module_conservation]

## Limitations

- The 81.5% baseline core rate limits the maximum observable enrichment.
- Three module organisms—Cola, Kang, and SB2B—lack pangenome links because their species had too few GTDB genomes for pangenome construction.
- Module membership depends on an upstream threshold of |Pearson r| >= 0.3 and a maximum of 50 genes per module.
- The 90% and 50% core cutoffs for classifying modules as core, mixed, or accessory are convenient rather than biologically validated.
- Essential genes are invisible to ICA modules, so the results describe the non-essential, fitness-measurable genome fraction rather than all genes.

## Data and Provenance

The analysis used 1,116 ICA fitness modules across 32 organisms, cross-organism module families, a KBase pangenome gene-to-cluster link table, and essential-gene classifications. Main outputs are `data/module_conservation.tsv` and `data/family_conservation.tsv`; supporting analyses are provided in `notebooks/01_module_conservation.ipynb` and `notebooks/02_family_conservation.ipynb`. [src: module_conservation]

## Related Concepts
- [[concepts/two-speed-genome]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/core-accessory-resistance]]

- [[concepts/fitness-conservation]]
- [[concepts/pangenome-integration]]
- [[concepts/gene-essentiality]]
- [[entities/independent-component-analysis]]
- [[entities/kbase-ke-pangenome]]
- [[entities/gtdb]]