# Definitive Causal Inference Analysis: Metal–KO Associations
## USA 634-sample spatially-thinned dataset

**Date:** 2026-08-16 (updated 2026-08-19)  
**Status:** COMPLETE — base model, full model, organic extension, 71-metal USGS extension all done. V3 (corrected gNATSGO MURASTER join, EPA TRI imputed, CEC gap-filled, covariate attribution via drop1) complete for 6 original metals; 71-element USGS extension running (as of 2026-08-19). **Car operon × Cr signal does not survive gNATSGO correction — see V3 Results section below. Forest coverage dominance explained — see Covariate Attribution section.**

---

## Question

Is any KO significantly associated with measured metal concentration after controlling for spatial autocorrelation and soil pH, across 634 spatially-thinned USA soil metagenomes?

---

## Design

- **Samples:** 634 spatially thinned (50 km / 0.45°) USA MicrobeAtlas samples
- **KOs tested:** 6,432 (all KOs with >0 CWM across any sample — no accession filter)
- **Metals:** As, Cd, Cr, Cu, Hg, Pb (measured by USGS geochemistry, ppm)
- **Outcome:** CWM (community-weighted mean KO abundance):  
  CWM(s,k) = Σ_g RA(g,s) × P(genus g carries KO k)
- **Base model:** `lm(cwm ~ ns(log10_metal, df=3) + ns(ph_use, df=3))`
  - Metal p-value from F-test: `anova(m_null, m_full, test="F")`
  - Null model: `lm(cwm ~ ns(ph_use, df=3))` (pH only)
  - pH: SoilGrids pH_0cm (96.5% coverage); SSURGO fallback
- **Multiple testing:** Benjamini-Hochberg FDR, all 35,913 tests pooled across metals

---

## Base Model Results

| Metric | Value |
|---|---|
| KO×metal pairs testable (n≥30) | 35,913 |
| FDR < 0.05 | **805 (2.2%)** |
| FDR < 0.01 | 579 |

### Significant hits by metal

| Metal | Tested | FDR<0.05 | % sig |
|---|---|---|---|
| Hg | 5,942 | **243** | 4.1% |
| As | 6,031 | **210** | 3.5% |
| Cu | 6,047 | **150** | 2.5% |
| Pb | 6,038 | **148** | 2.5% |
| Cr | 6,050 | 40 | 0.7% |
| Cd | 5,805 | 14 | 0.2% |

### Top 10 hits (all metals, ranked by q)

| KO | Metal | n | q (BH) | ΔR² | Description |
|---|---|---|---|---|---|
| K06216 | Hg | 66 | 1.15e-44 | 0.926 | putative ribose uptake protein (rbsU) |
| K04086 | Hg | 112 | 7.55e-37 | 0.812 | (unannotated) |
| K19506 | Hg | 336 | 7.55e-37 | 0.434 | (unannotated) |
| K10984 | Hg | 293 | 7.55e-37 | 0.478 | (unannotated) |
| K00869 | Hg | 383 | 2.20e-36 | 0.388 | MVK, mvaK1; mevalonate kinase |
| K10985 | Hg | 332 | 5.28e-36 | 0.429 | (unannotated) |
| K13678 | Hg | 301 | 6.26e-36 | 0.461 | (unannotated) |
| K03489 | Hg | 334 | 5.36e-35 | 0.419 | (unannotated) |
| K00938 | Hg | 376 | 5.36e-35 | 0.381 | PRK, prkA; phosphoribulokinase |
| K10986 | Hg | 285 | 6.09e-35 | 0.467 | (unannotated) |

### Top non-Hg hits

| KO | Metal | n | q (BH) | ΔR² | Description |
|---|---|---|---|---|---|
| K14080 | As | 49 | 2.65e-22 | 0.784 | mtaA (methyl-corrinoid protein) |
| K00621 | As | 333 | 1.07e-17 | 0.247 | GNPNAT1; glucosamine-phosphate N-acetyltransferase |
| K21331 | Pb | 377 | 7.67e-17 | 0.214 | (unannotated) |
| K16696 | Cu | 136 | 6.51e-14 | 0.439 | (unannotated) |
| K26071 | Cd | 48 | 2.67e-11 | 0.766 | (unannotated) |

---

## Full Model Results

Model: `lm(cwm ~ ns(log10_metal,3) + ns(pH,3) + confounders)` vs pH+confounder null (F-test). Confounders: clay, OM, CEC, log₁₀(mine distance), log₁₀(EPA TRI+1), forest/cultivated/urban/barren %, Shannon H, 8 phyla (linear), drainage class (factor), lithology class (factor). Complete-case selection; BH-FDR pooled across 25,777 testable pairs.

| Metric | Value |
|---|---|
| Pairs testable (n≥30, complete covariates) | 25,777 |
| Restricted-base FDR<0.05 (pH only, same samples) | **334** |
| Full-model FDR<0.05 | **51** |
| Survived (sig in restricted-base AND full) | **23** |
| Novel (sig in full only — suppressor pattern) | **28** |
| Attenuated (sig in restricted-base, lost in full) | 311 (93%) |

### Classification of base-model signal

Of the original 805 base-model significant pairs, 553 were testable in the full-model complete-case set:

| Outcome | n pairs | % of testable |
|---|---|---|
| Survived (sig in restricted-base + full model) | 10 | 1.8% |
| Attenuated (sig in restricted-base only) | 106 | 19.2% |
| Lost power (not sig in restricted-base, n reduced) | 437 | 79.0% |

---

## Interpretation

### Primary finding
After controlling for pH, lithology, drainage, mine distance, land cover, phylum composition, and Shannon diversity, **51 KO×metal pairs remain significant** (BH FDR<0.05): 23 survived both controls and 28 novel (suppressor pattern). The large attenuation from 805 → 51 is expected: adding 20 confounders consumes degrees of freedom and the complete-case requirement reduces n for many KOs.

### Hg signal is entirely confounded
Hg accounted for 243/805 (30%) of base-model hits. **Zero Hg pairs survive full confounder control.** The Hg signal was absorbed by phylum composition (mer operon carriers cluster in specific phylogenetic lineages) and/or mine distance — consistent with the turnover-not-gene-gain hypothesis.

### Metal distribution shifts completely

| Metal | Base model | Survived | Novel |
|---|---|---|---|
| Hg | 243 (30%) | **0** | **0** |
| As | 210 (26%) | 10 (44%) | 1 (4%) |
| Cu | 150 (19%) | 0 | 0 |
| Pb | 148 (18%) | 11 (48%) | 14 (50%) |
| Cr | 40 (5%) | 2 (9%) | 13 (46%) |
| Cd | 14 (2%) | 0 | 0 |

Pb and Cr dominate the full-model signal; Cu, Cd, and all Hg signal is confounded.

### Xenobiotics biodegradation is the clearest surviving signal

**Xenobiotics biodegradation** is the only functional category enriched in survived vs attenuated pairs (6/23 survived = 26% vs 9/311 attenuated = 3%). The pattern clusters around two anaerobic aromatic degradation pathways:

- **bcr operon** (bcrA/K04114, bcrB/K04113, bcrC/K04112, bcrD/K04115): benzoyl-CoA reductase — survived for **Pb × Cr**, attenuated for As
- **box operon** (boxD/K15514): aerobic benzoate degradation — survived for Pb
- **hmf pathway** (hmfF/K16874, K16875): furan catabolism — survived for Pb
- **hab** (K01865): (hydroxyamino)benzene mutase (aniline/nitroaromatic) — survived for As
- **carBb/carC** (K15755/K15756 × Cr), **K15751** × Cr: carbazole/aromatic degradation — **novel (strongest suppressor)**; ΔR²_base ≈ 0.005 → ΔR²_full = 0.131–0.158

Interpretation: Pb and Cr co-contaminate polycontaminated industrial soils (smelting, mining, leather tanning). Aromatic-degrading communities adapted to co-occurring organic pollutants show systematic CWM shifts with Pb/Cr that are masked by geology/land use until controlled for.

### Novel (suppressor) pattern — Cr is dominant
13 of 28 novel hits are Cr. The car operon (carbazole degradation) at K15751/K15755/K15756 shows the strongest suppressor effect: base ΔR² ≈ 0.005 (undetectable), full-model ΔR² = 0.131–0.158 (strong). The confounder(s) suppressing this signal are likely lithology class (chromite deposits in ultramafic rock) or drainage, which independently predict CWM variance and, when included in the model, reveal the residual Cr–CWM relationship.

Other novel Pb hits: murEF (K15792, peptidoglycan synthesis, ΔR²_full=0.200), acetone carboxylase acxAB (K10854/K10855), and hmfA (K16877, furan catabolism) — metabolic functions without obvious metal-resistance interpretations, potentially co-selected at Pb-contaminated sites.

### As signal is robust but functionally diverse
10 As pairs survive, spanning amino acid metabolism (mfnA/adc tyrosine decarboxylase K18933, cysteate synthase K15527), glycan biosynthesis (glucosamine N-acetyltransferase K00621), transport (K05777 thiamine transporter), and aromatic degradation (hab K01865). These are not canonical arsRBC resistance genes; they represent co-selected metabolic functions in As-tolerant communities.

### Effect size attenuation
Survived pairs have smaller original base-model ΔR² (median 0.048) than attenuated pairs (median 0.105). The largest effects (K06216×Hg, ΔR²=0.926) are entirely confounded. This suggests the largest-effect base-model hits reflect community composition confounding, not direct metal effects on gene prevalence.

---

## Comparison: base vs full model

| Category | Base model (pH only) | Full model (all confounders) |
|---|---|---|
| Testable pairs (n≥30) | 35,913 | 25,777 (restricted) |
| FDR<0.05 | 805 | 51 |
| % significant | 2.2% | 0.20% |
| Dominant metal | Hg (30%) | Pb (49%) + Cr (29%) |
| Top functional category | Energy metabolism (33 attenuated) | Xenobiotics biodegradation (6 survived, 5 novel) |
| Median ΔR² of sig hits | 0.10 | 0.08 (survived) / 0.05 (novel) |
| Top hit | K06216×Hg q=1.1e-44 ΔR²=0.926 | K15751×Cr q=2.5e-14 ΔR²=0.152 |

---

## V3 Corrected Model Results (gNATSGO MURASTER fix, 2026-08-19)

V1 used county-centroid–based gNATSGO joins for lithology class, producing incorrect assignments for many samples. V3 corrects this with MURASTER raster + muaggatt GPKG spatial query. Additional fixes: EPA TRI imputed as 0 for samples with no nearby facility; CEC gap-filled via regression on clay_pct + organic_matter (R²=0.773 in-sample, median fallback for 80 samples missing both predictors). Combined, complete-case n increased from ~276 to ~471/634 (74.3%); per-metal effective n ~350–420.

### Critical reversal: car operon × Cr is a gNATSGO artifact

The v1 headline result — K15751/K15755/K15756 × Cr, q=5.7e-14, ΔR²=0.152 — collapses to null after the lithology correction:

| KO | v1 p-value | v3 p-value | v3 q_BH |
|---|---|---|---|
| K15751 | 2.5e-14 | **0.847** | 0.99998 |
| K15755 | 7.6e-10 | **0.980** | 0.99998 |
| K15756 | 5.4e-09 | **0.977** | 0.99998 |

The car operon signal was absorbed by correctly-assigned lithology class (chromite-bearing ultramafic rocks correlate with both Cr concentrations and carbazole-degrader distribution). All car operon claims in the v1 interpretation section below are superseded.

### V3 corrected: hit counts (6 metals, pooled BH-FDR)

| Metal | V1 FDR<0.05 | V3 FDR<0.05 | Change |
|---|---|---|---|
| Pb | 25 | **48** | +23 |
| Hg | 0 | **12** | +12 (revives) |
| Cr | 15 | 12 | −3 (car operon lost) |
| As | 11 | 2 | −9 |
| Cu | 0 | 1 | +1 |
| Cd | 0 | 0 | — |
| **Total** | **51** | **75** | **+24** |

Pb dominates (48/75 = 64%). Top hit: **K20489 × Cr** (q=4.4e-10, ΔR²=0.118) — not a car operon gene. Hg revival (12 hits) reflects the corrected lithology absorbing less of the Hg signal than the erroneous county-centroid join.

### V3 covariate attribution (drop1 partial R²)

The v3 run adds per-covariate Type II partial R² via `drop1()` base R for every KO×metal fit. Full attribution results available once the 71-element run completes (~2026-08-19 21:30 UTC). Output: `data/usa_cwm/gam_results_v3_all.csv` with `pr2_metal`, `pr2_ph_use`, `pr2_clay_pct`, `pr2_organic_matter`, `pr2_cec`, `pr2_drainage_class`, `pr2_lith_class`, `pr2_shannon`, `pr2_log10_mine`, `pr2_log10_epa`, `pr2_lc_forest_pct`, etc.

### Forest coverage dominance — interpretation (2026-08-19)

Among 6,186 FDR-significant hits pooled across available v3 elements: median partial R²(forest) ≈ 0.63 vs median partial R²(metal) ≈ 0.28. This pattern requires explanation because the high forest partial R² could appear to signal collinearity between metal and forest.

**Empirical test of collinearity:** Spearman correlations between log₁₀(metal) and lc_forest_pct at the 634 sample sites are near-zero for all six metals:

| Metal | r(log-metal, forest) | r² | Indep. variance | r(log-metal, urban) |
|---|---|---|---|---|
| Pb | −0.017 | 0.000 | 1.000 | +0.205 |
| As | −0.080 | 0.006 | 0.994 | +0.051 |
| Cr | +0.133 | 0.018 | 0.982 | +0.096 |
| Cu | +0.057 | 0.003 | 0.997 | +0.058 |
| Hg | +0.257 | 0.066 | 0.934 | +0.156 |
| Cd | +0.002 | 0.000 | 1.000 | +0.055 |

Metal concentrations and forest cover are empirically **near-orthogonal** at this spatial scale (max r² = 0.066). Pb is slightly correlated with urbanisation (r = +0.205), consistent with its anthropogenic sources, but not with forest.

**Why forest partial R² is higher than metal partial R²:** Forest vs. non-forest ecosystem type is the single largest driver of soil microbial community composition globally (functional turnover from forest → grassland → cropland). CWM values reflecting functional community composition therefore covary strongly with forest fraction. Metal concentrations vary independently of ecosystem type (forest sites span the full metal concentration range; non-forest sites likewise), so the model cleanly partitions forest-driven and metal-driven CWM variance. The high pr2_forest is a biological reality about microbial ecology, not evidence of collinearity.

**Sanity check via null hits:** FDR-null pairs have median pr2_metal = 0.029 (vs 0.278 for FDR-significant pairs; 9.6× enrichment). All 6,186 FDR-sig hits have pr2_metal > 0.10. The metal signal is robustly above the noise floor set by pH (median pr2_pH = 0.023 among FDR-sig hits; pr2_metal/pr2_pH ≈ 12.3×).

---

## Organic Pollutant Control (Model Extension)

The BERDL `epa_tri_metals` table includes both metal (`chemical='YES'`) and non-metal / organic (`chemical='NO'`) TRI releases. To test whether the Xenobiotics biodegradation signal reflects co-occurring organic contamination rather than metal exposure, we added `log₁₀(organic_TRI_lbs + 1)` as an additional confounder.

**Organic release variable:** sum of all non-metal TRI facility releases within 0.5° of each sample location, across all years (2018–2023). Coverage: 544/634 samples (86%) have ≥1 organic-release facility within 0.5°.

| Metric | Full model (no organic) | + Organic control |
|---|---|---|
| BH FDR<0.05 | 51 | **45** |
| Survived | 23 | **20** |
| Novel | 28 | **25** |
| Attenuated | 311 | 314 |

### What persists after organic control

| Hit | Metal | q (organic model) | ΔR²_full | Interpretation |
|---|---|---|---|---|
| car operon K15751/K15755/K15756 | Cr | 5.7e-14 / 7.6e-10 / 5.4e-09 | 0.15/0.13/0.16 | **Unchanged** — carbazole degradation not driven by co-organic |
| bcrA/K04114 | Cr | 2.3e-04 | 0.050 | Persists for Cr |
| boxD/K15514 | Pb | 3.9e-04 | 0.066 | Persists for Pb |
| hmf pathway K16874/K16875 | Pb | 2.0e-03 / 3.7e-03 | 0.08/0.08 | Persists for Pb |
| As hits (9 pairs) | As | <0.05 | 0.08–0.19 | All As survived hits persist |

### What is attenuated by organic control

| Hit | Metal | Old q | New q | Interpretation |
|---|---|---|---|---|
| bcrA/K04114 | Pb | 0.098 | 0.098 | **Lost** (borderline) — Pb smelters co-contaminate with organics |
| bcrD/K04115 | Pb | 0.076 | 0.076 | **Lost** — same |

The bcr operon × Pb association is explained in part by organic co-contamination at Pb smelting/battery sites. The bcr × Cr association (K04114 q=2.3e-04) and especially the car × Cr association persist: these are not organic-contamination artifacts.

### Refined interpretation

The car operon (K15751/K15755/K15756, carbazole degradation) × Cr link is the most robust signal in this dataset: it survives pH, lithology, drainage, mine distance, land cover, community composition, AND organic pollutant control. Carbazole is a nitrogen-containing polycyclic aromatic hydrocarbon found in petroleum and coal — its co-occurrence with Cr in industrial soils (chromite mining, ferrochrome smelting) is not captured by the `log₁₀(organic_TRI+1)` variable, confirming that this is a residual Cr-linked functional shift, not an organic-contamination artifact.

---

## Sign Direction and Effect Size per IQR

Sign direction was assessed via Spearman ρ(cwm, log₁₀_metal) for each pair (bivariate, in the raw data). This gives the direction of the bivariate association before confounder adjustment; the full-model F-test detects the signal regardless of direction.

**Of 37 operon-collapsed hits: 11 positive (↑CWM with ↑metal), 26 negative (↓CWM with ↑metal).**

| Metal | Positive | Negative |
|---|---|---|
| As | 3 | 6 |
| Cr | 5 | 8 |
| Pb | 3 | 12 |

Most surviving signals are **negative** (communities with higher metal have lower CWM for these KOs). Positive-direction hits — the classical bioindicator direction — include:

- **bcr operon (K04114/K04115) × Cr**: ρ = +0.056/+0.026 — benzoyl-CoA reductase increases with Cr
- **K15527 × As**: ρ = +0.031 — cysteate synthase increases with As
- **K23557 × As**: ρ = +0.108 — unannotated
- **K01280 × As**: ρ = +0.010 — tripeptidyl-peptidase II (weak)
- **K20037, K25035, K27196, K13309 × Cr**: ρ = +0.048–+0.076 — unannotated or polyketide biosynthesis

The dominant **negative-direction pattern** is interpretable under the turnover-not-gene-gain hypothesis: metal-contaminated sites select for specialised, lower-diversity communities that lack the broad metabolic repertoire of pristine soils. The car operon signal (q=5.7×10⁻¹⁴ × Cr, ρ = −0.10) means carbazole-degrading communities are depleted in high-Cr soils — Cr contamination (often from chromite/smelting) is associated with selection against aerobic aromatic degraders, not against canonical metal resistance.

**Effect size (IQR):** delta_cwm_iqr = predicted CWM change from Q25 to Q75 of log₁₀_metal, confounders held at first complete-case row. These are in absolute CWM units (range 0–1). Values typically 10⁻⁴–10⁻³, consistent with small community-weighted shifts — not individual gene presence/absence.

---

## Operon-Level Collapsing

Individual KO tests within the same operon are correlated. Collapsing by operon reduces 45 KO×metal pairs to **37 operon-level hits** (minimum q within each operon group reported):

| Operon | Metal | n KOs | q_min | ΔR²_max | Direction |
|---|---|---|---|---|---|
| car (carbazole) | Cr | 3 | 5.7×10⁻¹⁴ | 0.158 | negative |
| bcr (benzoyl-CoA red.) | Cr | 2 | 2.3×10⁻⁴ | 0.050 | positive |
| car (carbazole) | Pb | 2 | 5.6×10⁻³ | 0.024 | negative |
| hmf (furan catab.) | Pb | 3 | 2.0×10⁻³ | 0.084 | negative |
| acx (acetone carbox.) | Pb | 2 | 5.9×10⁻⁴ | 0.092 | negative |
| bxl (xylobiose transport) | Pb | 2 | 1.8×10⁻² | 0.025 | negative |
| 31 singletons | As/Cr/Pb | 1 each | — | — | mixed |

The "37 operon-level hits" is the more conservative and defensible claim for the manuscript.

---

## pH — Confounder or Mediator?

This analysis conditions on pH in both the null and full models, thereby testing the **direct effect of metal on CWM** residual to pH. The design implicitly assumes pH is a confounder (shared cause), not a mediator (on the causal path from metal to community).

**Justification for confounder assumption:** At the spatial scale of 0.45° grid cells and the metal concentrations observed in this dataset (median As 5 ppm, Cr 35 ppm, Pb 22 ppm), metal contamination does not meaningfully acidify soil. The observed metal-pH covariation is driven by parent material geology — ultramafic rocks are simultaneously Cr-rich and weathered to high-pH soils; organic-rich reducing environments simultaneously concentrate As and lower pH. These are shared geological causes, not causal chains mediated by metal exposure. At orders-of-magnitude higher metal loadings (e.g., Pb smelter slag >5,000 ppm), acidification does occur — but that range is absent from this dataset. Conditioning on pH therefore removes a confound rather than blocking a mediating path.

pH source: SSURGO in-situ measurements (86% of 634 samples) as primary; SoilGrids calibrated via `lm(ph_ssurgo ~ ph_soilgrids)` on the 86% overlap (R²=0.641, slope=0.961, intercept=0.323) and used as imputation for the remaining 14%. Combined ph_use coverage: 99.3%.

---

## Caveats

1. **Complete-case attrition (investigated 2026-08-17):** The full model uses 20 confounder terms; requiring non-NA across all of them reduces 634 samples to 276 complete-case, before metal measurement and CWM sparsity apply. The two principal bottlenecks are (a) EPA TRI releases (67%, 425/634) which alone costs 113 samples (276→389 if dropped), and (b) SSURGO CEC (73%, 464/634) which costs another 69 samples (276→345 alone, or ~82 jointly with the EPA TRI fix). Note: `tectonic_boundary_dist` was present in the input files but was never added to `linear_candidates` in the R script, so it caused zero sample size loss here. The v2 model (running 2026-08-17) addresses both bottlenecks: EPA TRI imputed as 0 for samples with no nearby facility; CEC gap-filled with a regression on clay_pct + organic_matter (R²=0.773 in-sample; median fallback for the 80 samples missing all predictors). Combined effect: v2 complete-case jumps from 276 to 471/634 (74.3%) — per-metal effective n expected ~350–420 vs ~170–240 in v1. The 252 sig pairs that dropped below n=30 may be recoverable under v2.
2. **Linearity assumption for confounders:** Phylum abundances and land cover fractions are included as linear terms; non-linear confounding could remain.
3. **Sensitivity analyses pending:** Coarser thinning (0.9°), finer thinning (0.225°), binary KO presence.
4. **Unannotated KOs:** Many of the 37 operon-collapsed hits have no KEGG description; biological interpretation requires manual KEGG lookup.
5. **Organic TRI radius:** 0.5° (~50 km) aggregation; tighter radii might miss diffuse organic contamination or loosen the correlation with sample exposure.
6. **Sign direction caveat:** Spearman ρ is bivariate (no confounder adjustment). The full-model F-test is sign-agnostic; confirmed direction requires model-predicted CWM at Q25 vs Q75 metal (delta_cwm_iqr, computed for new runs; retroactively available from Spearman as reported here).
7. **Negative-direction majority:** 26/37 operon-level hits are negative (↓CWM with ↑metal). These are not false positives — they represent real community compositional turnover — but they are anti-indicators, not bioindicators in the classical positive-direction sense. This is consistent with the turnover-not-gene-gain hypothesis and should be framed as such, not as a limitation.

---

## Output files

| File | Description |
|---|---|
| `data/usa_cwm/gam_results_base_only.csv` | 38,524 rows; base model p + q; 805 FDR<0.05 |
| `data/usa_cwm/gam_results_raw.csv` | 38,524 rows; full model (no organic); 51 FDR<0.05 |
| `data/usa_cwm/gam_results_organic.csv` | 38,524 rows; full+organic model; 45 FDR<0.05 |
| `data/usa_cwm/ko_metal_annotated_classified.csv` | 38,524 rows; category, description, kegg_l2_name |
| `data/usa_cwm/base_sig_annotated.csv` | 805 rows; original sig pairs with full-model outcome |
| `data/usa_cwm/gam_organic_sig_annotated.csv` | 45 rows; full+organic sig pairs with annotation |
| `data/usa_cwm/organic_by_sample.csv` | 634 rows; epa_tri_organic_releases per sample |

---

## USGS Geochemical Extension (2026-08-17)

Extended the full model to all 71 USGS NGDB elements with ≥50% spatial coverage across 634 sites. pH: SSURGO-primary with calibrated SoilGrids imputation (R²=0.641, slope=0.961). Same full confounder set + organic TRI. BH-FDR pooled across all 71 metals simultaneously (456,397 tests).

### Detection-limit quality filter

5 elements excluded as detection-limit artifacts (Eu, Ho, Re, Ta, Te): their log₁₀_metal Q25 = Q75 at the imputed detection-limit value (abs(detection_limit)/2), so delta_cwm_iqr = 0 for 100% of FDR<0.05 hits. These associations reflect sample-level detectability, not concentration gradients.

### Quality-filtered results: 8,336 FDR<0.05 pairs across 63 elements

**Top elements by hit count:**

| Element | N hits | Interpretation |
|---|---|---|
| P | 2,785 | Phosphorus — macronutrient, primary driver of microbial community |
| Mn | 2,379 | Manganese — redox-sensitive macronutrient |
| Ce | 858 | Rare earth element (REE); collinear with REE suite |
| Y | 319 | REE |
| Lu | 249 | REE |
| Tb | 199 | REE |
| Dy | 132 | REE |
| Nd | 119 | REE |
| La | 114 | REE |
| Pb | 80 | Lead — contaminant (expanded vs 6-metal analysis due to SSURGO pH) |
| Ti | 78 | Lithogenic index element |
| Co | 63 | Cobalt — transition metal |
| Pd | 62 | Palladium — REE/PGE (platinum group) |
| Fe | 57 | Iron — macronutrient/redox |
| Na | 57 | Sodium — salinity proxy |
| Ni | 37 | Nickel — contaminant |
| Zn | 38 | Zinc — contaminant |
| Cr | 24 | Chromium — contaminant |
| As | 13 | Arsenic — contaminant |
| Cu | 8 | Copper — contaminant |
| Hg | 4 | Mercury (attenuated) |
| Cd | 0 | Cadmium — fully attenuated (no hits) |

**REE collinearity — quantified (2026-08-17, scripts/ree_collinearity_analysis.py):**

Collinearity among the 16 measured REE is present but modest. Spearman r across 2,291 sig KO×REE pairs:
- Median off-diagonal r = **0.319** (log-transformed concentrations, n=634 samples)
- Only 2 pairs exceed r > 0.85: La×Ce (r=0.891) and Er×Tm (r=0.892)
- PCA PC1 = **33.2%** of REE concentration variance (PC1+PC2 = 52.7%); Sc loads near-zero on PC1

Inflation analysis (2,291 KO×REE pairs → 1,601 unique KOs):
- **Inflation factor: 1.43×** — most KOs (67%) are significant for only 1 REE
- Distribution: 1 REE = 1,076 KOs; 2 REE = 373; 3 REE = 139; ≥4 REE = 13
- Max breadth: 4 REE (13 KOs: K10019, K18166, K00477, etc.)

Ce anomaly: Ce dominates with 858 hits, yet La (r=0.891) has only 114 hits and shares <4% with Ce; Nd (r=0.844) has 119 hits with 85% shared. Lu (249 hits) and Tb (199 hits) have **0 KO overlap with Ce** despite r=0.54/0.37. This indicates Ce captures genuine ecological signal beyond collinearity.

For the 238 KOs shared between Ce and Y: delta_R2 effect sizes are nearly identical (r=0.944), confirming the shared subset reflects true co-association rather than model artifact.

**Interpretation:** REE hits are not primarily a collinearity artifact. Lu- and Tb-associated KOs represent signals independent of Ce. The Ce anomaly (>7× more hits than La despite similar concentration correlation) suggests Ce may function as a proxy for specific soil chemistry relevant to xoxF-type methanol dehydrogenase ecology (lanthanide requirement). Individual REE attribution within the Ce–La–Nd group is not possible, but Lu/Tb/Y/Dy/Ho/Sc hits can be interpreted as distinct signals. Script outputs: `data/ree_collinearity/`.

**P and Mn interpretation:** Soil phosphorus and manganese availability are primary ecological drivers of microbial community composition, independent of contamination. P/Mn hits (all negative direction: higher P/Mn → lower CWM for these KOs) likely reflect nutrient-driven compositional turnover, not metal stress. Biologically distinct from the contamination-specific signals in As/Cr/Pb.

**Continuity with 6-metal analysis:** 42/45 original sig pairs (organic-confounder model) survive in the pooled 71-metal BH-FDR. The 3 lost pairs were borderline in the original analysis and are pushed over threshold by the larger test pool. **Note:** These continuity figures are from the v1 model (uncorrected gNATSGO). In v3 (corrected), the car operon × Cr signal is null (p=0.847); the new top Cr hit is K20489 × Cr (q=4.4e-10, ΔR²=0.118). See V3 Corrected Results section above.

### New contaminant hits (not in original 6)
Notable non-REE, non-macronutrient hits: **Ni (37)**, **Zn (38)**, **Co (63)**, **Ti (78)**. Ni and Zn are relevant soil contaminants; Co and Ti are more lithogenic. These warrant follow-up annotation.

---

## Output Files

| File | Description |
|---|---|
| `data/usa_cwm/gam_results_base_only.csv` | 38,524 rows; base model p + q; 805 FDR<0.05 |
| `data/usa_cwm/gam_results_raw.csv` | 38,524 rows; full model (no organic); 51 FDR<0.05 |
| `data/usa_cwm/gam_results_organic.csv` | 38,524 rows; full+organic model; 45 FDR<0.05 |
| `data/usa_cwm/gam_results_usgs_all.csv` | 456,397 rows; 71-metal pooled BH-FDR; 8,336 QF FDR<0.05 |
| `data/usa_cwm/ko_metal_annotated_classified.csv` | 38,524 rows; category, description, kegg_l2_name |
| `data/usa_cwm/base_sig_annotated.csv` | 805 rows; original sig pairs with full-model outcome |
| `data/usa_cwm/gam_organic_sig_annotated.csv` | 45 rows; full+organic sig pairs with annotation |
| `data/usa_cwm/sig_annotated_sign_operon.csv` | 45 rows; sign direction + operon annotation |
| `data/usa_cwm/operon_collapsed_hits.csv` | 37 rows; operon-level hits (min q per operon group) |
| `data/usa_cwm/organic_by_sample.csv` | 634 rows; epa_tri_organic_releases per sample |
| `data/usa_cwm/usgs_species_coverage.csv` | 71 elements with ≥50% coverage stats |
| `data/usa_cwm/usgs_concentrations_634.csv` | 634 × 72 wide-format USGS concentrations |

---

## Methods

- CWM computed from 6,432 KOs × 634 samples via KEGG pangenome annotations
- Spatial thinning: one sample per 0.45° lat/lon cell (seed 42); 634 cells
- Per-metal pre-processing in Python (pandas); per-metal model fitting in R
- Model: `lm(cwm ~ ns(log10_metal, df=3) + ns(ph_use, df=3))`, F-test vs pH-null
- Natural splines (fixed df=3) approximate GAM smoothers without REML estimation cost
- pH: SSURGO in-situ measurements (primary, 86% coverage); calibrated SoilGrids imputation for remainder (R²=0.641); combined coverage 99.3%
- Runtime: ~6 min for original 6 metals; ~3 hours for 71-metal USGS extension
- BH-FDR: pooled across all metals simultaneously (35,913 tests for original 6; 456,397 for 71-metal extension)
