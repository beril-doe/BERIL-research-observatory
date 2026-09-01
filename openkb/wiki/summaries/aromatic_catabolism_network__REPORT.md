---
type: "Summary"
description: "ADP1 aromatic catabolism depends on a 51-gene support network beyond the core pathway."
doc_type: short
full_text: "sources/aromatic_catabolism_network__REPORT.md"
---

# Aromatic Catabolism Support Network in ADP1

## Overview

This report maps the genetic and metabolic dependencies of quinate catabolism in [[entities/acinetobacter-baylyi-adp1]]. It identifies a 51-gene support network around the [[entities/quinate-aromatic-degradation]], including the core aromatic pathway, NADH oxidation, iron acquisition, PQQ cofactor biosynthesis, and transcriptional regulation. The findings show that aromatic catabolism depends on a distributed [[concepts/metabolic-support-networks|metabolic support network]] that is substantially larger than the pathway itself.

## Key Findings

### A four-subsystem support network

Of the 51 quinate-specific genes, 44 (86%) were assigned through [[concepts/cofitness-networks|co-fitness analysis]] to four functional subsystems:

- **Aromatic degradation pathway:** 8 genes converting quinate through protocatechuate and β-ketoadipate into TCA-cycle intermediates.
- **[[entities/complex-i|Complex I]] / NADH dehydrogenase:** 21 genes supporting NADH reoxidation during high-flux aromatic catabolism.
- **Iron acquisition:** 7 genes supplying iron for [[entities/protocatechuate-3-4-dioxygenase|protocatechuate 3,4-dioxygenase]].
- **[[entities/pqq-biosynthesis|PQQ biosynthesis]]:** 2 genes supplying the cofactor for the PQQ-dependent quinate dehydrogenase.
- **Regulation:** 6 transcriptional regulators.
- **Unassigned:** 7 genes with weak co-fitness relationships.

The support network is more than eight times larger than the core pathway, with a support-to-core ratio of approximately 7:1.

### Complex I is the dominant support requirement

Complex I-associated genes account for 21 of the 51 quinate-specific genes (41%). [[entities/flux-balance-analysis|FBA]] predicts 1.76× higher Complex I flux on aromatic substrates (0.55 versus 0.31), but predicts 0% gene essentiality for these genes. This illustrates a [[concepts/metabolic-model-gapfilling|metabolic-model blind spot]]: flux demand is represented, while the threshold behavior of a multi-subunit respiratory complex is not.

Thirty of the 51 genes have no FBA reaction mappings. These unmapped genes include cofactor-supply, iron-homeostasis, regulatory, and putative accessory functions, showing that standard metabolic models omit important cofactor and support infrastructure.

### Biochemical coupling without genomic co-localization

The support subsystems are genomically separated but metabolically coupled. The Complex I operon is located at 714–729 kb, the pca/qui pathway at 1,709–1,724 kb, PQQ biosynthesis at 2,461 kb, and iron-acquisition genes occur across four loci. The chromosome contains 9 genomic clusters of at least 2 quinate-specific genes, with a mild overall clustering ratio of 0.89 observed/expected nearest-neighbor distance.

The Complex I region contains 13 nuo subunits on the same strand with intergenic distances below 100 bp. Disruption of any subunit is expected to eliminate the complex, consistent with 10 of the 13 subunits independently producing quinate-specific growth defects. The pca/qui region forms a separate 12-gene operon containing pathway and transport genes.

### Co-fitness resolves unknown genes

Co-fitness analysis assigned 16 of 23 initially Other/Unknown genes to support subsystems with medium or high confidence. Complex I genes had mean pairwise correlation of **r = 0.992**, while aromatic-pathway genes had **r = 0.961**. Two DUF proteins, ACIAD3137 (UPF0234) and ACIAD2176 (DUF2280), correlated with Complex I genes at **r > 0.98** and are candidate Complex I accessory factors. These assignments remain hypotheses because they are based on phenotypic correlation rather than physical interaction evidence.

### Complex I dependence tracks NADH flux rather than aromaticity alone

Ortholog-transferred [[entities/fitness-browser|Fitness Browser]] data covered 12,241 entries, 2,005 genes, and 13 conditions. Complex I orthologs had worse fitness on aromatic conditions than on non-aromatic conditions (mean **−1.35 versus −0.77**, Mann–Whitney **p < 0.0001**). However, the largest Complex I defects relative to background occurred on acetate (**−1.55**) and succinate (**−1.39**), both non-aromatic substrates that generate substantial TCA-cycle NADH.

This supports the hypothesis that ADP1's apparent quinate-specificity reflects respiratory-chain architecture and NADH load rather than a uniquely aromatic requirement. [[entities/ndh-2|An alternative NADH dehydrogenase, such as NDH-2]], may compensate for Complex I on lower-NADH substrates such as glucose and lactate.

## Biochemical Dependency Chain

Quinate catabolism creates three principal support requirements:

1. **PQQ supply:** QuiA is a PQQ-dependent quinoprotein, linking quinate utilization to PQQ biosynthesis.
2. **Iron supply:** PcaGH is a non-heme Fe²⁺-dependent protocatechuate 3,4-dioxygenase, linking aromatic ring cleavage to iron acquisition.
3. **NADH reoxidation:** β-ketoadipate-derived succinyl-CoA and acetyl-CoA enter the TCA cycle and generate NADH, increasing demand for respiratory NADH oxidation.

Together, these dependencies illustrate how [[entities/quinate-aromatic-degradation|aromatic catabolism]] recruits pathways that are not part of the substrate-conversion route itself.

## Interpretation and Contribution

The report extends prior biochemical and transcriptomic knowledge by quantifying support requirements at the whole-genome level. PQQ and iron dependencies are consistent with established properties of PQQ-dependent quinate dehydrogenases and iron-dependent intradiol dioxygenases. The principal novel finding is the scale and prominence of the Complex I dependency.

The analysis contributes five main results:

1. It defines a 51-gene aromatic-catabolism support network spanning four major biochemical subsystems.
2. It identifies Complex I as the largest support subsystem, with 21 associated genes.
3. It quantifies FBA incompleteness: 30 of 51 genes lack reaction mappings, and the model predicts no essentiality despite elevated Complex I flux.
4. It uses co-fitness to assign 16 previously uncharacterized genes, including two candidate Complex I accessory factors.
5. It reframes Complex I dependence as a [[concepts/nadh-flux-respiratory-constraints|high-NADH-flux respiratory constraint]] that also occurs on acetate and succinate.

## Limitations

- Co-fitness estimates use only 8 conditions, providing approximately 5 independent dimensions and limiting subsystem resolution.
- Ortholog-transferred fitness data combines organisms with potentially different respiratory-chain architectures.
- Complex I-associated assignments beyond the core nuo operon are based on phenotypic correlation and may represent indirect relationships.
- PQQ genes also show glucose-specific phenotypes in another ADP1 analysis, so PQQ dependence is not exclusive to aromatic catabolism.

## Open Directions

- Search the ADP1 genome for NDH-2 and compare its deletion phenotypes on quinate, glucose, acetate, and succinate.
- Test ACIAD3137 and ACIAD2176 through protein-interaction or Complex I co-purification experiments.
- Expand the condition matrix with benzoate, catechol, vanillate, iron limitation, and respiratory inhibitors to test the NADH-flux model.
- Compare pca-pathway-containing Acinetobacter genomes for retention of Complex I KOs K00330–K00343 using pangenome data.
- Extend the FBA model with PQQ biosynthesis, iron homeostasis, and respiratory-capacity constraints.

## Data and Supporting Analyses

The study used ADP1 genome features, gene phenotypes, gene–reaction mappings, ortholog-transferred Fitness Browser data, and pangenome annotations. Generated files include 51-gene network assignments, operon assignments, 1,275 pairwise co-fitness relationships, unknown-gene assignments, and 13-condition cross-species fitness comparisons. Supporting notebooks addressed metabolic dependencies, genomic organization, co-fitness structure, and cross-species testing.

## Related Concepts
- [[concepts/metabolic-support-networks]]
- [[concepts/nadh-flux-respiratory-constraints]]
- [[concepts/cofitness-networks]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/metabolic-model-gapfilling]]
- [[concepts/evidence-triangulation]]
- [[concepts/method-concordance]]
- [[concepts/multi-omics-integration]]
- [[concepts/phenotypic-landscape]]
- [[concepts/annotation-gap]]
- [[concepts/gene-essentiality]]
- [[concepts/pangenome-integration]]
- [[concepts/shared-dispensability]]

## Entities
- [[entities/complex-i]]
- [[entities/ndh-2]]
- [[entities/pqq]]
- [[entities/iron]]
- [[entities/protocatechuate-3-4-dioxygenase]]
- [[entities/fitness-browser]]
- [[entities/flux-balance-analysis]]
- [[entities/pqq-biosynthesis]]
- [[entities/berdl]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/modelseed]]
- [[entities/kegg]]
- [[entities/eggnog]]
