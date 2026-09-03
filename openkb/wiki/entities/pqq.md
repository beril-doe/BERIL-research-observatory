---
sources: ["summaries/respiratory_chain_wiring__REPORT.md", "summaries/ibd_phage_targeting__REPORT.md", "summaries/discoveries.md", "summaries/aromatic_catabolism_network__REPORT.md"]
type: "Compound"
description: "PQQ is a redox cofactor required for ADP1 quinate catabolism."
---

# Pyrroloquinoline Quinone

## Identity

Pyrroloquinoline quinone, commonly abbreviated **PQQ**, is a redox cofactor used by quinoprotein dehydrogenases. [src: aromatic_catabolism_network]

## Role in ADP1 Aromatic Catabolism

In [[entities/acinetobacter-baylyi-adp1]], the quinate dehydrogenase QuiA is a PQQ-dependent quinoprotein that initiates quinate catabolism. [src: aromatic_catabolism_network] This links PQQ availability to the [[entities/quinate-aromatic-degradation|quinate-to-aromatic degradation pathway]], which proceeds through protocatechuate and the β-ketoadipate pathway before producing TCA-cycle intermediates. [src: aromatic_catabolism_network]

The report identifies **pqqC** and **pqqD** as two quinate-specific genes associated with PQQ biosynthesis. [src: aromatic_catabolism_network] These genes form part of a 51-gene [[concepts/metabolic-support-networks|metabolic support network]] for aromatic catabolism. [src: aromatic_catabolism_network]

## Evidence and Interpretation

PQQ biosynthesis was assigned as one of four major support subsystems in the network, alongside the aromatic pathway, Complex I, and iron acquisition. [src: aromatic_catabolism_network] The PQQ requirement is consistent with prior transcriptomic evidence that four of five PQQ biosynthesis genes are upregulated on quinate relative to succinate in ADP1. [src: aromatic_catabolism_network]

The PQQ dependency is not exclusive to aromatic catabolism: PQQ biosynthesis genes also show glucose-specific phenotypes in the ADP1 deletion-phenotypes analysis, consistent with PQQ-dependent glucose dehydrogenase activity. [src: aromatic_catabolism_network] Therefore, PQQ should be interpreted as a shared cofactor requirement whose importance depends on the substrate and the PQQ-dependent enzymes active under that condition. [src: aromatic_catabolism_network]

## Modeling Relevance

PQQ biosynthesis and related cofactor-supply functions are among the processes not represented by FBA reaction mappings for the ADP1 quinate-specific gene set. [src: aromatic_catabolism_network] This makes PQQ an example of a biochemical dependency that can be essential for growth while remaining outside the scope of a core metabolic model, contributing to the [[concepts/metabolic-model-gapfilling|metabolic model gap-filling]] problem. [src: aromatic_catabolism_network]

## Related Pages

- [[entities/pqq-biosynthesis]]
- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/quinate-aromatic-degradation]]
- [[concepts/metabolic-support-networks]]
- [[concepts/metabolic-model-gapfilling]]
- [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/ibd_phage_targeting__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]