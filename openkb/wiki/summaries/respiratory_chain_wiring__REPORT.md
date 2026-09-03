---
type: "Summary"
description: "ADP1 uses substrate-specific respiratory wiring governed by NADH flux rate."
doc_type: short
full_text: "sources/respiratory_chain_wiring__REPORT.md"
---

# Condition-Specific Respiratory Chain Wiring in ADP1

## Overview

This report maps how *Acinetobacter baylyi* ADP1 configures its branched respiratory chain under different carbon sources. The central conclusion is that respiratory-chain use is qualitatively substrate-specific rather than a simple gradient of pathway activity: carbon-source-dependent NADH production rates and pathway distribution determine which electron-entry and terminal-oxidase components become limiting. This work contributes to the broader concepts of [[concepts/condition-dependent-essentiality]], [[concepts/functional-redundancy]], and [[concepts/nadh-flux-respiratory-constraints]].

## Key Findings

- ADP1 contains 62 respiratory-chain genes across eight subsystems, including Complex I, NDH-2, NADH-flavin oxidoreductases, cytochrome bo3, cytochrome bd, Complex II/SDH, ATP synthase, and other respiratory components. Thirty-six genes have growth data, while 26 lack data, including NDH-2 and several ATP synthase subunits.
- Carbon sources impose distinct respiratory requirements. Quinate requires Complex I but not cytochrome bo3, cytochrome bd, or succinate dehydrogenase; acetate is the most demanding condition and requires Complex I, cytochrome bo3, ACIAD3522, and additional components; lactate specifically requires cytochrome bo3 while Complex I is only mildly important; glucose has no individually required respiratory component; and urea is generally demanding across the respiratory chain.
- ADP1 has three candidate NADH dehydrogenases with different properties: proton-pumping [[entities/complex-i]], non-pumping [[entities/ndh-2]], and the single-gene NADH-FMN oxidoreductase [[entities/aciad3522]]. Complex I is strongly required on quinate and defective on acetate, while ACIAD3522 is dispensable on quinate and glucose but nearly lethal to remove on acetate, with a growth ratio of 0.013.
- NDH-2 (ACIAD_RS16420; KO K03885) is core-genome and TnSeq-dispensable, but it is absent from the deletion collection and therefore has no direct growth data. FBA predicts no NDH-2 flux on standard media because it favors the more ATP-efficient Complex I route.
- The quinate–Complex I paradox is explained by NADH production rate rather than total NADH yield. Quinate generates fewer NADH molecules per carbon atom than glucose or acetate, but β-ketoadipate-pathway ring cleavage produces succinyl-CoA and acetyl-CoA together, creating a concentrated TCA-cycle NADH burst. Glucose distributes reducing-equivalent production across Entner-Doudoroff and TCA-cycle steps, potentially keeping NADH production within NDH-2 capacity. This rate-versus-yield interpretation is a hypothesis based on theoretical stoichiometry rather than measured intracellular flux.
- Cross-species data do not support the prediction that NDH-2 presence reduces aromatic Complex I dependency. After filtering likely false-positive NDH-2 annotations, validated-NDH-2 organisms had a larger mean Complex I aromatic deficit (-0.297) than organisms without validated NDH-2 (-0.156); the difference was not significant (p = 0.52). The comparison included 14 organisms and only four without NDH-2, so it is underpowered.
- Proteomics indicates that the wiring difference is metabolic rather than transcriptional under standard conditions. Complex I, NDH-2, and ACIAD3522 had similar protein abundance values of 27.6, 27.0, and 26.2, respectively, compared with a genome median of 26.4. The observed spread was 1.4 units, suggesting that all three systems are constitutively present and that substrate-specific flux determines which becomes limiting.

## Proposed Wiring Model

- **Quinate:** Aromatic ring cleavage creates a concentrated TCA-cycle reducing-equivalent burst, making Complex I the bottleneck while terminal oxidases remain dispensable.
- **Acetate:** Direct TCA entry produces sustained NADH demand and requires multiple dehydrogenases, with cytochrome bo3 implicated as the primary terminal oxidase and ACIAD3522 especially important.
- **Lactate:** Pyruvate entry produces moderate NADH flux and creates a specific cytochrome bo3 requirement; the mild Complex I phenotype is consistent with partial compensation by NDH-2, though this remains untested.
- **Glucose:** Distributed NADH production through Entner-Doudoroff and TCA-cycle reactions allows respiratory redundancy under the tested conditions.

The model illustrates [[concepts/metabolic-niche-partitioning]] in which parallel respiratory components are simultaneously available but become functionally distinct under different substrate-driven flux regimes.

## Model and Evidence Limitations

FBA predicts zero flux through NDH-2 and ACIAD3522 because growth optimization preferentially routes NADH through ATP-generating Complex I. Consequently, the model does not represent capacity constraints or the use of suboptimal pathways that may be required at high NADH production rates. The central NDH-2 compensation prediction also lacks a direct ADP1 deletion experiment. Stoichiometric pathway analysis is theoretical, and the cross-species comparison is small and potentially affected by incomplete or inaccurate NDH-2 annotation. ACIAD3522 may not be a canonical respiratory NADH dehydrogenase and could instead have a specialized metabolic role in acetate utilization. These issues connect to [[entities/flux-balance-analysis]] and [[concepts/annotation-gap]].

## Main Contribution

The report provides a condition-specific respiratory wiring map for ADP1 and proposes that respiratory-chain configuration is controlled primarily by NADH flux rate and pathway concentration, not total reducing-equivalent yield or transcriptional switching. It also weakens the general hypothesis that NDH-2 presence predicts reduced aromatic dependence on Complex I, suggesting that the observed ADP1 wiring may be species-specific.

## Future Directions

1. Delete ADP1 NDH-2 to test whether Complex I becomes essential during glucose growth.
2. Measure NADH/NAD+ ratios across quinate, glucose, acetate, and other carbon sources to test the flux-rate hypothesis directly.
3. Use KO-based searches for K03885 and Complex I genes across the BERDL pangenome to assess NDH-2/Complex I co-occurrence at larger scale.
4. Characterize ACIAD3522 biochemically and determine whether it functions as a respiratory NADH dehydrogenase or an acetate-associated metabolic enzyme.
5. Reanalyze condition-specific respiratory-chain proteomics, including quinate versus succinate data, to test whether protein abundance changes despite similar standard-condition expression.

## Related Concepts
- [[concepts/metabolic-competitive-exclusion]]
- [[concepts/multi-omics-integration]]
- [[concepts/phenotypic-landscape]]
- [[concepts/gene-essentiality]]
- [[concepts/method-concordance]]
- [[concepts/pathway-completeness]]

## Entities
- [[entities/pqq-biosynthesis]]
- [[entities/pqq]]
- [[entities/iron]]
- [[entities/urease-complex]]
- [[entities/kegg]]
- [[entities/modelseed]]
- [[entities/berdl]]
