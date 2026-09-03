<!-- tension-hash: 6168cccb6fdd1be3 -->
# Does Cross-Method Discordance in Metabolic Prediction Reflect Biology or Incompleteness?

Across genome-scale metabolic and essentiality prediction pipelines — FBA, TnSeq, knockout screens, GapMind, gapfilling, and BacDive phenotype records — different methods frequently disagree with one another. The open question, discussed on [[concepts/method-concordance]], is whether this discordance is largely benign (different methods measure different biological endpoints, or differ in annotation quality) or whether it signals genuine, unresolved incompleteness in metabolic network reconstruction and strain-level generalization. The distinction matters because it determines how much confidence downstream users should place in any single method's essentiality or pathway call.

## Evidence Sides

**Discordance is explainable and not contradictory**
- FBA has moderate concordance with knockout lethality (κ ≈ 0.49) but no detectable association with growth defects among TnSeq-dispensable genes (p = 0.63); these concern different prediction targets and should not be treated as contradictory. [src: adp1_triple_essentiality]
- Binary essentiality from RB-TnSeq disagrees with knockout essentiality, while continuous fitness predicts knockout status with AUC = 0.700–0.725 — data representation and biological endpoint both shape apparent concordance. [src: adp1_triple_essentiality]
- InterProScan GO annotations reveal significant AMR-network enrichment where old SEED annotations produced a null result, showing annotation quality changes apparent concordance. [src: amr_cofitness_networks]
- GapMind often agrees with gapfilling at the pathway level, with exact reaction-level mismatch attributable to output granularity. [src: annotation_gap_discovery]
- FW300-N2E3 shows strong WoM–Fitness Browser–GapMind agreement. [src: fw300_metabolic_consistency]

**Discordance reflects real, unresolved incompleteness**
- The annotation-gap pipeline resolves only 47.8% of gapfilled pairs; 52.2% remain unresolved and dark reactions are resolved at just 16%. [src: annotation_gap_discovery]
- Pipeline resolution varies from 20.0% in *Bacteroides thetaiotaomicron* to 71.4% in *Klebsiella michiganensis*, and phylogenetic vs. annotation-quality causes cannot be separated. [src: annotation_gap_discovery]
- FW300-N2E3 shows robust tryptophan production–utilization discordance in BacDive, with confidence varying sharply by sample size (tryptophan n = 50, trehalose n = 6, lysine n = 3, glycine n = 1). [src: fw300_metabolic_consistency]
- FBA flux-growth correlations vary by carbon source, including an unexpected positive glucarate correlation, limiting extrapolation. [src: adp1_triple_essentiality]
- ADP1 Complex I fitness defects on acetate, succinate, and aromatic substrates leave the NADH-load vs. aromatic-specific mechanism unresolved without direct experiments. [src: aromatic_catabolism_network]
- AMR support-network enrichment for flagellar/biosynthetic genes may reflect real co-regulation or merely shared lab-condition dispensability. [src: amr_cofitness_networks]

## Possible Reconciliations

1. **Different-target hypothesis**: lethality, growth defect, and fitness are distinct biological endpoints, so partial concordance is expected, not a failure of either method.
2. **Annotation-confound hypothesis**: much apparent discordance (SEED vs. InterProScan, reaction-level GapMind mismatch) tracks annotation completeness rather than underlying biology.
3. **Strain-heterogeneity hypothesis**: species-level BacDive "discordance" may hide strain-specific capability, especially where n is small (n = 1, 3).
4. **Condition-specificity hypothesis**: the glucarate sign-flip and Complex I ambiguity reflect real substrate-dependent network behavior, not general model failure.

## Resolving Work

- Recompute FBA–TnSeq concordance (κ, correlation) across an expanded carbon-source panel to test whether the glucarate anomaly is substrate-specific or a constraint-modeling artifact.
- Re-annotate all AMR/GapMind comparison species with matched InterProScan pipelines to isolate annotation-quality effects from true biological discordance.
- Run defined NADH-generating vs. non-NADH aromatic conditions in ADP1 Complex I mutants to directly test the NADH-load hypothesis.
- Expand BacDive strain sampling for low-n traits (lysine, glycine, trehalose) to check whether species-level discordance survives larger samples.
- Prioritize experimental/curation follow-up on the 52.2% unresolved gapfilled pairs and "dark reactions" (16% resolved) to determine whether they reflect annotation gaps or genuinely novel biochemistry.
