---
type: "Concept"
sources: ["summaries/soil_metal_functional_genomics__REPORT.md"]
description: "Correlated metals can obscure which contaminant drives microbial gene shifts."
---

# Metal Co-contamination Confounding

## Definition

Metal co-contamination confounding occurs when multiple environmental metals covary, making it difficult to determine whether a microbial functional association is specific to one metal or reflects a shared response to multi-metal stress. [[concepts/environmental-metal-tolerance]] [src: soil_metal_functional_genomics]

## Evidence from the Soil Metal Functional Genomics Report

The report identified 2,355 significant COG–metal associations across nine metals—copper, cobalt, chromium, nickel, zinc, lead, arsenic, cadmium, and mercury—in 51,748 soil samples. Chromium, copper, lead, and zinc co-vary in many industrial soils, creating a risk that nominal metal-specific associations instead capture a broader contamination or stress gradient. [src: soil_metal_functional_genomics]

This issue is especially important because the reported discovery rate is high: 2,355 significant associations among 3,915 metal-by-COG tests at FDR < 0.05. The report cautions that correlated tests may make the Benjamini–Hochberg correction anti-conservative under positive dependence, so the true false-discovery rate could exceed the reported value. [src: soil_metal_functional_genomics] This is a form of [[concepts/batch-confounding]]-like inferential risk, although the confounder here is environmental covariance rather than project accession. [src: soil_metal_functional_genomics]

## Consequences for Interpretation

A positive association between a COG and copper does not by itself demonstrate a copper-specific function. The association could arise because copper marks exposure to chromium, lead, zinc, or another correlated contaminant, or because the COG responds to generalized chemical stress. [src: soil_metal_functional_genomics]

The report’s copper analysis found associations involving cell division, nucleotide transport, and energy production. These patterns are consistent with copper toxicity mechanisms and possible energetic trade-offs, but the observational design cannot distinguish copper-specific selection from a response to co-occurring metals without additional adjustment. [src: soil_metal_functional_genomics] This motivates comparison with [[concepts/shared-stress-biology]] and [[concepts/environmental-resistome]], where broad stress or resistance responses may be mistaken for responses to a single environmental driver. [src: soil_metal_functional_genomics]

The issue also affects the interpretation of the db-RDA result. Metal concentrations explained 80% of residual community COG-profile variance after conditioning on project or batch effects (R² = 0.799, p = 0.005, 999 permutations), but this multivariate result does not establish that any individual metal uniquely explains the variation. [src: soil_metal_functional_genomics] The unconditional metals-only R² was not reported, so the relative contribution of project effects and correlated metals remains unresolved. [src: soil_metal_functional_genomics]

## Required Disambiguation Analyses

The report identifies partial-correlation modeling as the appropriate next step. A model such as `COG ~ Cr | Cu + Zn + Pb` can test whether a chromium association persists after adjustment for other co-varying metals. [src: soil_metal_functional_genomics] Applying analogous conditional models across the metal set would separate metal-specific signals from associations attributable to a shared contamination gradient. [src: soil_metal_functional_genomics]

Additional checks are needed to determine whether statistically significant associations are biologically meaningful. The report calls for an effect-size audit across all 2,355 associations, including identification of associations with Spearman ρ < 0.05. [src: soil_metal_functional_genomics] Spatial autocorrelation testing with Moran’s I, followed by SEVM if residual spatial dependence is significant, can assess whether geographic structure contributes to apparent metal–COG relationships. [src: soil_metal_functional_genomics]

## Tensions

The report presents a strong conditional community-level association between metal concentrations and COG profiles, but it also states that metal co-contamination prevents attribution of individual associations to particular metals. These findings are not contradictory: metals may jointly explain substantial residual variation while remaining difficult to disentangle as separate causal predictors. [src: soil_metal_functional_genomics]

## Open Directions

- Re-run the Spark-based analyses with partial-correlation models conditioning each metal on the major co-contaminants; determine which COG associations remain metal-specific. [src: soil_metal_functional_genomics]
- Compare conditional and unconditional db-RDA models to quantify how project effects and correlated metals alter explained variance. [src: soil_metal_functional_genomics]
- Combine effect-size filtering with functional classification into resistance, stress, membrane, energy, and unknown categories; test whether robust metal-specific signals are enriched in particular categories. [src: soil_metal_functional_genomics]
- Test Moran’s I on model residuals and apply SEVM where spatial autocorrelation is significant; determine whether apparent metal-specific associations persist after geographic structure is modeled. [src: soil_metal_functional_genomics]

## Source

- [[summaries/soil_metal_functional_genomics__REPORT]]