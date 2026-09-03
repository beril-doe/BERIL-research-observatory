---
sources: ["summaries/respiratory_chain_wiring__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/ibd_phage_targeting__REPORT.md", "summaries/discoveries.md", "summaries/aromatic_catabolism_network__REPORT.md"]
type: "Compound"
description: "Iron supports protocatechuate ring cleavage during ADP1 quinate catabolism."
---

# Iron

## Identity

- **Canonical name:** Iron
- **Symbol:** Fe
- **Relevant form:** Fe²⁺ (ferrous iron)
- **Type:** Compound

## Role in ADP1 Aromatic Catabolism

Iron is required by protocatechuate 3,4-dioxygenase, the enzyme that performs ring cleavage during conversion of quinate-derived protocatechuate in [[entities/acinetobacter-baylyi-adp1]]. [src: aromatic_catabolism_network]

The iron requirement links [[entities/protocatechuate-3-4-dioxygenase]] to a seven-gene iron-acquisition subsystem within the 51-gene [[concepts/metabolic-support-networks|aromatic catabolism support network]]. [src: aromatic_catabolism_network]

The identified iron-acquisition functions include siderophore biosynthesis, ExbD/TolR transport, a ferrichrome receptor, and a TonB-dependent receptor. [src: aromatic_catabolism_network]

## Model and Network Context

Iron acquisition is one of four major support subsystems associated with quinate-specific growth phenotypes, alongside the aromatic pathway, Complex I, and [[entities/pqq-biosynthesis|PQQ biosynthesis]]. [src: aromatic_catabolism_network]

Iron-acquisition genes are distributed across four chromosomal loci rather than being co-localized with the pca/qui pathway genes, illustrating the distinction between genomic organization and biochemical coupling in the [[concepts/metabolic-support-networks|support network]]. [src: aromatic_catabolism_network]

The report identifies iron homeostasis and acquisition as part of a class of functions that are incompletely represented in the [[entities/flux-balance-analysis|FBA]] model; 30 of 51 quinate-specific genes lack FBA reaction mappings overall. [src: aromatic_catabolism_network]

## Related Pages

- [[entities/protocatechuate-3-4-dioxygenase]]
- acinetobacter bayli adp1
- [[concepts/metabolic-support-networks]]
- [[concepts/metabolic-model-gapfilling]]
- [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/ibd_phage_targeting__REPORT]]

See also: [[summaries/metal_fitness_atlas__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]