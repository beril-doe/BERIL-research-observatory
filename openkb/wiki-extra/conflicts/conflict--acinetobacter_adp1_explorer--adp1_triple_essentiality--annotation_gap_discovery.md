<!-- tension-hash: 729e736f8e3702c2 -->
# Does Flux Balance Analysis Predict Metabolic Gene Essentiality, or Just Metabolic Necessity in the Abstract?

A recurring tension in the [[concepts/metabolic-model-gapfilling]] work is whether FBA-based predictions actually track experimental gene importance. Some evidence shows moderate, real agreement between FBA-predicted essentiality and knockout lethality; other evidence from the same and related models shows FBA failing outright to predict growth defects, misclassifying experimentally important genes as blocked, and assigning near-zero essentiality to genes supporting flux it itself predicts is elevated. Resolving this matters because gapfilled, unvalidated reactions already account for 87% of growth predictions, so any systematic mismatch between FBA output and real fitness data threatens the interpretability of the whole model class.

## Evidence Sides

**FBA has real, if moderate, predictive power**
Across genes, FBA-predicted essentiality agrees with knockout lethality at κ = 0.486 in rich medium and κ = 0.493 in minimal medium. [src: adp1_triple_essentiality]

**FBA fails to predict fitness outcomes in specific, important cases**
- Among 478 TnSeq-dispensable genes, FBA-predicted essentiality class does not predict growth defects (p = 0.63). [src: adp1_triple_essentiality]
- Aromatic degradation genes can be experimentally important while being predicted as FBA-blocked. [src: adp1_triple_essentiality]
- FBA predicts 1.76× higher Complex I flux on aromatic substrates, yet assigns 0% essentiality to the Complex I genes carrying that demand. [src: aromatic_catabolism_network]

## Possible Reconciliations

- **Threshold vs. continuous-cost hypothesis**: FBA may be a valid *threshold* model (does removing a gene make growth impossible?) without being a valid model of *continuous* growth cost or fitness defect magnitude, which would explain the κ~0.49 agreement alongside the p=0.63 null result. [src: adp1_triple_essentiality]
- **Gapfilling/connectivity hypothesis**: aromatic-pathway blocked-but-important genes may reflect missing gapfills or wrong reaction directionality rather than a real biological absence of need, consistent with the broader observation that 87% of predictions depend on gapfilled reactions. [src: acinetobacter_adp1_explorer]
- **Alternative-pathway/threshold-effect hypothesis**: the Complex I flux/essentiality mismatch may arise because linear FBA cannot represent complex-level threshold or capacity constraints, or because alternative respiratory routes are assumed available in the model but are not physiologically interchangeable. [src: aromatic_catabolism_network]
- **Environment-definition hypothesis**: media definitions in the model may omit trace aromatic substrates or growth conditions under which these genes' importance would appear, producing false "blocked" or "non-essential" calls. [src: adp1_triple_essentiality]

## Resolving Work

- Re-run FBA essentiality calls under expanded media definitions that include trace aromatic and respiratory substrates, and check whether previously mismatched genes (aromatic degradation, Complex I) flip to correctly predicted. [src: adp1_triple_essentiality, aromatic_catabolism_network]
- Stratify the κ = 0.486/0.493 agreement analysis by gapfilled vs. non-gapfilled reactions to test whether disagreement concentrates in inferred reactions. [src: adp1_triple_essentiality, acinetobacter_adp1_explorer]
- Compare FBA flux predictions against direct measurements of Complex I activity (not just TnSeq fitness) to test whether the flux/essentiality mismatch reflects a modeling artifact or a real biological buffering mechanism. [src: aromatic_catabolism_network]
- Apply the same essentiality-vs-TnSeq comparison across additional organisms from the annotation-gap panel to see whether the p=0.63 null result is ADP1-specific or general. [src: annotation_gap_discovery]
