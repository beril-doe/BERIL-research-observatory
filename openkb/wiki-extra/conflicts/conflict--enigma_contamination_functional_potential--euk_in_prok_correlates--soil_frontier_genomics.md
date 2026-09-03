<!-- tension-hash: 3dca8875ef88e5bd -->
# Coverage-Adjusted Signal vs. Confirmatory Null: Real Effect or Sequencing-Depth Artifact?

Across several ENIGMA analyses, models that adjust for or condition on sequencing coverage detect positive associations — defense responses, environmental drivers, genomic frontiers — that predeclared confirmatory tests, cross-study holdouts, or effort-controlled analyses then fail to reproduce. The disagreement matters because it determines whether coverage adjustment is *rescuing* real biological signal buried under confounding, or *manufacturing* false positives that a stricter, unadjusted test correctly rejects. See [[concepts/coverage-limited-inference]], [[concepts/euk_in_prok_correlates]] (referenced within), and [[concepts/soil_frontier_genomics]].

## Evidence Sides

**Side A — Adjustment/exploratory analysis reveals signal**
- Coverage-adjusted exploratory models yielded positive defense estimates, including an FDR-significant relaxed-mode coefficient with q = 0.0462. [src: enigma_contamination_functional_potential]
- In NMDC, matrix was strongly associated with eukaryotic fraction in the pooled collection. [src: euk_in_prok_correlates]
- Within the NEON study, vegetation and geography were predictive, with within-study R²=+0.17 ± 0.06. [src: euk_in_prok_correlates]
- Frontier areas had mean pH = 6.74 versus 5.94 in mapped areas. [src: soil_frontier_genomics]

**Side B — Confirmatory/portable/controlled tests show null**
- Predeclared Spearman tests were non-significant in both mapping modes, and fraction-stratified tests did not show a strong within-fraction monotonic signal. [src: enigma_contamination_functional_potential]
- Species-proxy mapping reduced mean mapped abundance fraction to 0.031 and produced a non-significant defense trend of rho = 0.169, p = 0.081. [src: enigma_contamination_functional_potential]
- Environment failed to generalize under whole-study holdout (R²=−0.30, AUC 0.56). [src: euk_in_prok_correlates]
- All three soil model families had negative out-of-sample R². [src: soil_frontier_genomics]
- The GDI analysis did not yet control for the number of 16S samples per pH bin. [src: soil_frontier_genomics]

## Possible Reconciliations

- **Power/scope hypothesis**: adjustment corrects a real confound but the predeclared marginal test lacks power to detect a conditional effect — both results could be technically correct at different analysis stages. [src: enigma_contamination_functional_potential]
- **Locality hypothesis**: associations are real but study-specific (within-study, within-fraction) rather than globally portable, so pooled/cross-study tests correctly reject a generalized claim. [src: euk_in_prok_correlates]
- **Resolution-cost hypothesis**: higher-resolution (species-level) mapping trades coverage for specificity, so the null there may reflect underpowering rather than absence of effect. [src: enigma_contamination_functional_potential]
- **Effort-confound hypothesis**: the alkaline-soil "frontier" pH gap may reflect under-sequencing rather than a genuine biological/assembly difficulty. [src: soil_frontier_genomics]

## Resolving Work

- Re-run predeclared confirmatory Spearman tests alongside adjusted models on identical covariate sets, reporting both explicitly rather than separately. [src: enigma_contamination_functional_potential]
- Conduct batch-controlled, multi-study replication of the environment–eukaryotic-fraction association beyond NMDC and NEON. [src: euk_in_prok_correlates]
- Apply spatially blocked validation and influence diagnostics to the soil model families before treating negative R² as a biological null. [src: soil_frontier_genomics]
- Re-run the GDI pH analysis with explicit control for 16S sampling density per pH bin to separate effort from genomic difficulty. [src: soil_frontier_genomics]
- Improve species-proxy mapping retention (currently 0.031 mean fraction) and re-test the defense association at higher resolution with adequate coverage. [src: enigma_contamination_functional_potential]
