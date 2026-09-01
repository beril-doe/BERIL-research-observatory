---
type: "Concept"
sources: ["summaries/soil_frontier_genomics__REPORT.md"]
description: "When a model predicts worse out of sample than a training-mean baseline."
---

# Negative Out-of-Sample Prediction

## Definition

Negative out-of-sample R² means that a model performs worse on held-out data than a baseline that predicts the training-set mean for every test observation. It is a predictive failure, but it does not by itself distinguish biological unpredictability from distributional shift, influential observations, or other modeling problems. [src: soil_frontier_genomics]

## Evidence from Soil Microbial Genomics

The [[summaries/soil_frontier_genomics__REPORT]] evaluated functional gene counts across **5,441 soil samples** using soil-and-climate, geochemical, and industrial predictor families. All three model families had negative cross-validated R²: −0.205 ± 0.197, −0.331 ± 0.071, and −0.221 ± 0.042, respectively. [src: soil_frontier_genomics]

The associated clay-shield test also produced negative cross-validated R² for both low-clay soils (−0.268) and high-clay soils (−0.292). Their difference was 0.024, with a 95% confidence interval of −0.423 to 0.161, which includes zero. Thus, the analysis found no significant evidence that high clay improves predictive performance for functional gene counts. [src: soil_frontier_genomics]

These results weaken the global-scale claim that clay content provides a predictive shield against the measured environmental and industrial stressors. However, they do not establish that functional potential is intrinsically unpredictable. [src: soil_frontier_genomics]

## Diagnostic Alternatives

The report identifies three explanations that have not yet been separated: [src: soil_frontier_genomics]

1. **Distributional shift:** spatial structure or the use of spatially grouped folds may make the training and test distributions substantially different. This links negative R² to [[concepts/geographic-distance-decay]], [[concepts/geospatial-coverage-gaps]], and [[concepts/spatial-sampling-effort]]. [src: soil_frontier_genomics]
2. **Outlier leverage:** a small number of high-leverage test samples may dominate the mean squared error and drive R² below zero. [src: soil_frontier_genomics]
3. **Genuine global-scale unpredictability:** the measured predictors may simply lack sufficient information to predict functional gene counts at this spatial scale. This interpretation should be treated as a hypothesis until the first two alternatives are tested. [src: soil_frontier_genomics]

Batch effects and unmeasured confounding are additional possible contributors to poor generalization. These concerns connect the analysis to [[concepts/batch-confounding]], [[concepts/coverage-limited-inference]], and [[concepts/adversarial-methodological-review]]. [src: soil_frontier_genomics]

## Interpretation Standard

Negative out-of-sample R² should be reported as evidence of failed generalization under the evaluated validation design, not automatically as evidence of a biological null. A strong null interpretation requires diagnostics showing that spatial distributional shift and influential observations do not account for the failure. [src: soil_frontier_genomics]

If spatial blocking reveals that performance improves under a validation scheme matching the intended deployment setting, the original result primarily indicates a validation-design problem. If performance remains negative after robust spatial blocking, outlier analysis, and confounding checks, the evidence for limited predictability from the measured stressors becomes stronger. [src: soil_frontier_genomics]

## Open Directions

- Re-run the models with explicit spatial blocking to test whether geographic distributional shift explains the negative R² values. [src: soil_frontier_genomics]
- Decompose test-set error by sample and fold to determine whether high-leverage outliers dominate the mean squared error. [src: soil_frontier_genomics]
- Compare models with and without batch or data-source covariates to assess the contribution of [[concepts/batch-confounding]]. [src: soil_frontier_genomics]
- Evaluate residual spatial autocorrelation and performance across soil, climate, and industrial regimes before treating the result as a global biological null. [src: soil_frontier_genomics]