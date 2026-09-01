---
sources: ["summaries/aromatic_catabolism_network__REPORT.md"]
type: "Gene_Or_Pathway"
description: "Alternative NADH dehydrogenase proposed to offset Complex I demand"
---

# NDH-2

## Identity

- **Type:** gene_or_pathway
- **Aliases:** type 2 NADH dehydrogenase; alternative NADH dehydrogenase

## What it is

NDH-2 is a non-proton-pumping NADH dehydrogenase that can provide an alternative route for NADH oxidation alongside proton-pumping Complex I. [src: aromatic_catabolism_network]

## Role in ADP1 aromatic catabolism

The aromatic-catabolism analysis proposes that NDH-2 may compensate for Complex I on substrates with lower NADH-generation demands, potentially explaining why Complex I genes appear quinate-specific in *Acinetobacter baylyi* ADP1. [src: aromatic_catabolism_network]

Complex I-associated genes showed the strongest defects on acetate and succinate as well as aromatic conditions, while Complex I was described as dispensable on glucose and lactate, consistent with the hypothesis that Complex I dependence reflects NADH flux rather than aromatic chemistry alone. [src: aromatic_catabolism_network]

The report did not establish the presence, identity, or gene locus of an ADP1 NDH-2; identifying this alternative dehydrogenase is explicitly proposed as future work. [src: aromatic_catabolism_network]

## Relationship to [[entities/complex-i]]

The report identifies [[entities/complex-i]] as the dominant support subsystem for quinate catabolism, with 21 of 51 quinate-specific genes associated with Complex I. [src: aromatic_catabolism_network]

NDH-2 is therefore a candidate compensatory pathway whose substrate-specific activity could help explain the condition-dependent essentiality of Complex I. [src: aromatic_catabolism_network]

## Evidence and limitations

The NDH-2 interpretation is a hypothesis based on cross-species ortholog-transferred fitness data and known respiratory-chain organization, rather than a direct ADP1 deletion or biochemical measurement. [src: aromatic_catabolism_network]

The cross-species data combine organisms with different respiratory-chain architectures, so the inference cannot by itself demonstrate that NDH-2 performs this compensatory role in ADP1. [src: aromatic_catabolism_network]

## Proposed validation

A direct test would search the ADP1 genome for an NDH-2 gene and compare its deletion phenotype on quinate, glucose, acetate, and succinate. [src: aromatic_catabolism_network]

Additional aromatic substrates and respiratory inhibitors could test whether NDH-2 compensation tracks NADH flux and clarify the [[concepts/nadh-flux-respiratory-constraints|NADH-flux respiratory constraint]]. [src: aromatic_catabolism_network]

## Related pages

- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/complex-i]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/metabolic-support-networks]]
- [[concepts/nadh-flux-respiratory-constraints]]
- [[summaries/aromatic_catabolism_network__REPORT]]