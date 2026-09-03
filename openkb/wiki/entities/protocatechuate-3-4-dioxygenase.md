---
sources: ["summaries/enigma_carbon_census_1__REPORT.md", "summaries/discoveries.md", "summaries/aromatic_catabolism_network__REPORT.md"]
type: "Gene_Or_Pathway"
description: "Iron-dependent enzyme that cleaves protocatechuate in ADP1 aromatic catabolism"
---

# Protocatechuate 3,4-Dioxygenase

## Identity

Protocatechuate 3,4-dioxygenase is an iron-dependent ring-cleavage enzyme in the β-ketoadipate pathway; its subunits are encoded by **pcaGH** in *Acinetobacter baylyi* ADP1. [src: aromatic_catabolism_network]

**Aliases:** PcaGH; protocatechuate 3,4-dioxygenase

## Role in ADP1

The enzyme catalyzes the ring-cleavage step that converts protocatechuate during aromatic degradation, enabling subsequent β-ketoadipate processing and entry of carbon into the TCA cycle. [src: aromatic_catabolism_network]

PcaGH is a non-heme Fe²⁺-dependent dioxygenase, so iron acquisition is a biochemical support requirement for protocatechuate degradation. [src: aromatic_catabolism_network] The aromatic-catabolism support network includes 7 iron-acquisition genes associated with this requirement, including siderophore biosynthesis, ExbD/TolR transport, a ferrichrome receptor, and a TonB-dependent receptor. [src: aromatic_catabolism_network]

## Network Context

In the ADP1 quinate-catabolism network, protocatechuate 3,4-dioxygenase links the [[entities/quinate-aromatic-degradation]] pathway to the [[concepts/metabolic-support-networks|metabolic support network]] required for aromatic growth. [src: aromatic_catabolism_network]

The enzyme is part of the core aromatic pathway subsystem, which contains 8 of the report's 51 quinate-specific genes. [src: aromatic_catabolism_network] Its iron requirement is distinct from the [[entities/pqq-biosynthesis|PQQ biosynthesis]] requirement of quinate dehydrogenase and from the [[entities/complex-i|Complex I]] requirement for NADH reoxidation during high-flux TCA-cycle oxidation. [src: aromatic_catabolism_network]

## Model and Experimental Implications

The report identifies iron acquisition as a support dependency of protocatechuate ring cleavage, but it does not provide a direct deletion phenotype or gene-level essentiality result for pcaGH in the summarized analysis. [src: aromatic_catabolism_network] More generally, 30 of the 51 quinate-specific genes lacked FBA reaction mappings, illustrating limitations of [[entities/flux-balance-analysis|flux-balance analysis]] for representing cofactor supply chains and regulatory infrastructure. [src: aromatic_catabolism_network]

## Related Source

- [[summaries/aromatic_catabolism_network__REPORT]] — analysis of the 51-gene ADP1 aromatic-catabolism support network. [src: aromatic_catabolism_network]

See also: [[summaries/discoveries]]

See also: [[summaries/enigma_carbon_census_1__REPORT]]