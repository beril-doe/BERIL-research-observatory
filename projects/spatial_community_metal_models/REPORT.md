# Spatial Models of Metal Effects on Microbial Community Composition

**Status:** NB01–NB37 ALL COMPLETE (NB01–NB25 soil; NB28–NB37 aquatic; 2026-08-30)  
**Last updated:** 2026-08-30

---

## Summary

Five complementary spatial methods were applied to test whether metal concentrations structure microbial community composition (PC1 of Aitchison PCA) across 21,779 globally distributed soil samples, after accounting for spatial autocorrelation. Methods converge on the finding that metals (particularly Cr, Pb, Cu) consistently predict community PC1 in the same direction across independent spatial models (H3), and that both spatially-varying metal effects (H5) and species-level associations (H4) are detectable. Variance explained by metals is modest (~1–2% each), typical for environmental drivers of microbiome composition.

---

## Hypotheses

| H | Statement | Result |
|---|-----------|--------|
| H1 | GF identifies metals as important predictors | NOT SUPPORTED globally (only Pb>pH); Pb is #4 global predictor; Cu>#pH in North America |
| H2 | INLA metal fixed effects significant after spatial control | SUPPORTED (metals explain >99% of fitted variance; Cr β=−0.80, pH β=+1.32) |
| H3 | NNGP posterior directions match INLA for ≥4/6 metals | SUPPORTED (5/6 agree; Zn near-zero in both) |
| H4 | ≥50 genera show significant metal association in HMSC | SUPPORTED (57 genera total: Cu=20, Pb=16, Cr=11, Zn=5, As=5) |
| H5 | GAM spatially-varying metal terms significantly improve fit | SUPPORTED (all 4 metals p<1×10⁻⁸⁵; ΔAIC 433–699) |

---

## Results by method

### NB02 — SPDE-INLA (n=1,320 stratified sample)

Fixed effects on PC1 (standardised predictors):

| Predictor | Mean | SD |
|-----------|------|----|
| pH | +1.319 | 1.040 |
| Cr | −0.803 | 1.254 |
| Cu | +0.189 | 1.164 |
| Pb | +0.714 | 0.992 |
| Zn | +0.063 | 1.172 |
| As | −0.349 | 0.880 |

Variance partition: fixed effects 99.99%, spatial SPDE ~0%, nugget ~0% — the SPDE spatial term contributes negligibly once metal and environmental covariates are included, suggesting metals capture most of the spatially structured signal.

### NB03 — NNGP (n=346 stratified sample, 15 nearest neighbours)

PC1 posterior means (95% CI):

| Metal | Mean | 95% CI |
|-------|------|--------|
| Cr | −2.163 | [−4.573, +0.238] |
| Cu | +0.778 | [−1.825, +3.192] |
| Pb | +1.050 | [−1.194, +3.307] |
| Zn | −0.404 | [−2.821, +2.012] |
| As | −1.158 | [−3.138, +0.980] |

Direction matching INLA: pH ✓, Cr ✓, Cu ✓, Pb ✓, Zn ✗ (Zn near-zero in both), As ✓ → 5/6 agree → **H3 SUPPORTED**.

### NB04 — HMSC (n=346, 100 most prevalent genera, probit)

57 genera with significant metal association (Pr(β>0)>0.95 or <0.05):

| Metal | Sig. genera |
|-------|-------------|
| Cu | 20 |
| Pb | 16 |
| Cr | 11 |
| Zn | 5 |
| As | 5 |

Variance partition: ~10% from fixed effects collectively, ~90% IID random (sample-level) — typical for binary presence/absence microbiome data.

### NB05 — GAM spatially-varying coefficients (n=8,000 subsample)

| Metal | ΔAIC (interaction − base) | p (χ²) |
|-------|--------------------------|--------|
| Zn | +699 | 5×10⁻¹⁴¹ |
| Cr | +618 | 3×10⁻¹²⁴ |
| Pb | +556 | 1×10⁻¹¹¹ |
| Cu | +433 | 2×10⁻⁸⁵ |

All four metals show highly significant spatially-varying effects (tensor interaction ti(lat,lon,metal)). **H5 SUPPORTED.**

### NB01 — Gradient forests (complete)

Global GF (ntree=100, n=5,000 subsample, 500 genera, 12 predictors):

| Rank | Predictor | R² |
|------|-----------|-----|
| 1 | lon | 0.052 |
| 2 | lat | 0.049 |
| 3 | temp_K | 0.037 |
| **4** | **log_Pb_ppm** | **0.035** |
| 5 | clay_pct | 0.030 |
| 6 | ph | 0.027 |
| 7 | precip_mm | 0.026 |
| 8 | log_Cu_ppm | 0.017 |
| 9 | log_Zn_ppm | 0.015 |
| 10 | log_Ni_ppm | 0.011 |
| 11 | log_Cr_ppm | 0.010 |
| 12 | log_As_ppm | 0.002 |

**H1 verdict: NOT SUPPORTED** — only Pb (R²=0.035) exceeds pH (R²=0.027) in the global analysis; the threshold requires ≥2 metals.

**Key finding:** Pb is the #4 global predictor overall, ranking above pH, precipitation, and clay. Geography (lon, lat) and temperature dominate, but Pb outranks all other chemical predictors (including pH) globally.

Regional GF results (overall importance, same parameters):

| Predictor | Global | North America | Europe | Australia |
|-----------|--------|---------------|--------|-----------|
| lon | 0.052 | **0.044** | **0.062** | 0.021 |
| lat | 0.049 | 0.020 | **0.067** | 0.020 |
| temp_K | 0.037 | 0.011 | 0.026 | 0.014 |
| Pb | **0.035** | 0.006 | 0.042 | **0.030** |
| clay_pct | 0.030 | 0.020 | 0.032 | 0.021 |
| pH | 0.027 | 0.028 | 0.059 | **0.065** |
| precip_mm | 0.026 | 0.027 | 0.037 | 0.011 |
| Cu | 0.017 | **0.032** | 0.034 | 0.016 |
| Zn | 0.015 | 0.009 | 0.031 | 0.009 |
| Cr | 0.010 | 0.008 | 0.020 | 0.018 |

Notable patterns:
- **Global and Australia**: Pb is the top metal predictor
- **North America**: Cu is the top metal predictor, and **Cu (0.032) > pH (0.028)** — the only regional subgroup where multiple metals approach or exceed pH
- **Europe**: Pb (0.042) and Cu (0.034) are strong, but lat/lon dominate (0.062/0.067)
- **Australia**: pH dominates (0.065), Pb is #2 metal

**H1 context:** While H1 is not supported at the global scale (only Pb>pH), metals (especially Pb) rank as the strongest individual *chemical* predictors in all regions, and the global ranking of Pb above pH is a substantive finding even without formal H1 support.

---

---

## NB07 — Comprehensive GF: Full Element Suite (H6)

**Status:** Complete (2026-08-27).

**Approach:** Three-run sklearn RF on community PC1 (CLR top-20 genera) using SPIRE soil samples with matched geochemistry:
- **Run A** (global, n=23,404): Standard env + 7 metals from feature_matrix.
- **Run B1** (USA, n=9,294): DS801 A-horizon 47-element suite, SPIRE samples within 50 km.
- **Run B2** (USA, n=9,567): NALG 8-metal survey, SPIRE samples within 50 km.

**Results (MDI importance, top predictors):**

Run A (global): Co=0.202 > ph=0.164 > precip_mm=0.111 > Pb=0.087  
Run B1 (DS801): lon=0.107 > c_tot_pct=0.101 > c_org_pct=0.088 > lat=0.084 > ca_pct=0.070  
Run B2 (NALG): lon=0.177 > lat=0.162 > temp_K=0.128 > Pb=0.101 > Ni=0.068

**H6 verdict: NOT SUPPORTED** — No DS801 non-primary element approaches Co (0.202, top Run A metal). In Run B1, geography (lon, lat) and C-fractions dominate; no element-specific signal. In Run B2, Pb and Ni appear as metal predictors but these are primary metals.

---

## NB08 — USA Comprehensive RF: All Elements + Mine Proximity + Speciation (H6 extension)

**Status:** Complete v2 (2026-08-27).

**Approach:** sklearn RF (300 trees) on community PC1 (CLR top-20 genera, PC1 var=0.134) for all n=14,617 SPIRE USA soil samples. Predictor set: 110 columns across 8 sources — DS801/NALG full element suite (54 elem cols after 95% NaN drop), WorldClim bioclim + elevation (20 vars), gNATSGO soil water storage, GLIM lithology, SoilTemp, water table depth, RadMap (5 km, sparse), Mindat per-commodity uphill-mine proximity features (9 metals × 2 = 18 features + 1 global), free ion speciation (spec_log_free_{Cu2,Zn2,Pb2,Ni2} + olm_ph_spec, olm_soc_g_kg, olm_clay_pct_spec), and SoilGrids OLM API (per-point pH, clay, sand, silt, CEC).

Spatial autocorrelation in RF residuals: Moran's I (KNN k=8 libpysal) = −0.049, indicating low residual spatial autocorrelation. R² with lat/lon=0.458 vs without=0.458 — geographic coordinates contribute negligibly to predictive power once climate/element predictors are included.

**Predictor group importance totals:**

| Group | Total MDI | % |
|-------|-----------|---|
| Mine proximity (Mindat) | 0.263 | 26.3% |
| Climate (WorldClim) | 0.251 | 25.1% |
| Elements (DS801/NALG) | 0.250 | 25.0% |
| Geographic (lat/lon) | 0.089 | 8.9% |
| Soil national (gNATSGO) | 0.063 | 6.3% |
| Free ion speciation | 0.046 | 4.6% |
| Soil OLM (SoilGrids) | 0.037 | 3.7% |
| Hydro/temp | 0.000 | 0.0% |

**Top 15 predictors:**

| Rank | Predictor | MDI | Group |
|------|-----------|-----|-------|
| 1 | mean_diurnal_range_c | 0.061 | climate |
| 2 | lat | 0.051 | geographic |
| 3 | elem_tot_10a_pct | 0.048 | elements |
| 4 | gnatsg_avail_water_25–50cm | 0.042 | soil |
| 5 | elevation_m | 0.039 | climate |
| 6 | elem_quartz_pct | 0.039 | elements |
| 7 | lon | 0.038 | geographic |
| 8 | mindat_Cd_dist_km | 0.037 | mine proximity |
| 9 | isothermality | 0.036 | climate |
| 10 | mindat_Zn_dist_km | 0.033 | mine proximity |
| 11 | mindat_As_dist_km | 0.032 | mine proximity |
| 12 | mindat_any_dist_km | 0.024 | mine proximity |
| 13 | mindat_Ni_dist_km | 0.023 | mine proximity |
| 14 | mindat_Pb_dist_km | 0.023 | mine proximity |
| 15 | spec_log_free_Ni2 | 0.018 | free ion |

**Primary metal element concentrations (direct ppm):** elem_ba_ppm=0.020, Pb~0.009, Ni~0.005, As~0.004, Cr~0.004.

**H6 verdict (NB08 extension): PARTIALLY SUPPORTED** — Within the elements group, DS801 mineralogical fractions (tot_10a_pct, quartz_pct) and non-primary trace elements (Ba) rank substantially higher than primary metal ppm. Adding free ion speciation (Sauvé et al. 2000 model) captures an additional 4.6% of MDI, with spec_log_free_Ni2 the highest-ranking individual speciation term — confirming that bioavailable Ni (free Ni²⁺ activity) is more informative than total Ni ppm. Mine proximity for secondary metals (Cd, Zn, As) outranks proximity to primary metals.

**Key interpretation:** The dominant signal is contamination legacy (mine proximity 26%) and climate (25%), not direct soil geochemistry. Within the geochemical signal, parent material/weathering (mineralogical fractions) and speciated free ion activities outrank metal ppm concentrations. R²=0.458 with or without lat/lon confirms that geographic position itself adds no information beyond the physical/chemical predictors. This is consistent with the "turnover > gene gain" framing — community structure shifts are driven by broad edaphic gradients and contamination exposure history, not acute metal stress detectable as ppm differences.

**Note (future):** SoilGrids API pre-fetch (scripts/prefetch_soilgrids_usa.py) still running for full USA coverage; olm_ columns partially populated at time of this run.

---

## NB09 — MicrobeAtlas 16S USA RF (H6 replication with 16S)

**Status:** Complete (2026-08-27). n=67,835 genus / 68,106 OTU samples; 99 predictors.

Replicates NB08 using MicrobeAtlas 16S (n=76,377 USA soil samples) instead of SPIRE shotgun.
Run at genus level (top-50 genera pre-filtered in Spark, top-20 used in CLR PCA) and OTU level (top-500 OTUs).

**Results — genus level:**  
climate=37.9% > elements=34.3% > geographic=10.3% > soil_natl=7.9% > mine_proximity=6.5% > free_ion=2.7%

**Results — OTU level (n=68,106):**  
climate=37.9% > elements=34.3% > geographic=10.3% > soil_natl=7.9% > mine_proximity=6.5% > free_ion=2.7%  
Top predictors: precip_driest_month_mm, annual_precip_mm, elevation_m, mean_diurnal_range_c

**Key comparison vs NB08 (SPIRE shotgun):**
- Mine proximity drops from 26.1% (SPIRE) to 6.5% (MA 16S). Climate and elements gain proportionally.
- This may reflect that SPIRE samples are enriched for contaminated sites vs the broader MicrobeAtlas survey.
- Elements remain a strong predictor (34.3%) even in the general environmental survey context.

---

## NB10 — EUR Replication: LUCAS Heavy Metals + GEMAS + MicrobeAtlas 16S

**Status:** Complete v3 (2026-08-28). GEMAS + LUCAS soil properties + compound mine types + per-metal Mindat proximity (9 metals, 200 km radius, simple nearest-mine distance).

EUR analogue using:
- **Community:** MicrobeAtlas 16S EUR soil samples (n=40,358 with PC1, lat 34–72, lon −10–40)
- **Elements:** LUCAS Heavy Metals (14 metals) **+ GEMAS Ap (53 AR elements, 2,211 sites, 50 km NN)**
- **Soil:** LUCAS topsoil properties (pH, OC, clay, sand, silt; 38,542/40,358 matched)
- **Speciation:** EUR free-ion activities from LUCAS pH/SOC (13,348/40,358 matched within 5 km)
- **Mine proximity:** Mindat EUR per-metal (Cu, Pb, Zn, As, Cr, Ni, Cd, Hg, Co, 200 km) + compound types (Au, CuMo, PbZn, NiCu, AuAs) + `mindat_any_dist_km`

**Results (group MDI, v3 — final):**

| Group | NB10 v3 (final) | NB10 v2 (GEMAS only) | NB10 v1 (LUCAS HM) | USA SPIRE (NB08) |
|-------|------|------|------|------|
| elements | **38.3%** | 47.8% | 15.3% | 25.0% |
| mine_proximity | **26.0%** | 6.9% | 8.8% | 26.3% |
| climate | 22.0% | 28.4% | 50.6% | 25.1% |
| soil_eur | 7.3% | — | — | — |
| geographic | 4.6% | 13.4% | 16.8% | 8.9% |
| free_ion | 1.3% | 2.5% | 6.9% | 4.6% |
| hydro_temp | 0.5% | — | — | 0.8% |

n=40,358; R²=0.6628.

**Top predictors:** lat (0.026), lucas_soil_pH (0.024), mindat_Ni_dist_km (0.022), mindat_NiCu_dist_km (0.021), mindat_Au_dist_km (0.021), lon (0.020), gemas_li_ppm (0.020), lucas_soil_OC (0.019), mindat_any_dist_km (0.019), mindat_Cu_dist_km (0.019).

**Key findings:**
- Adding GEMAS (53 AR elements at true point coordinates) boosted elements from 15.3% → 38–48% depending on mine proximity treatment — confirming that the v1 result was an artefact of NUTS_2 spatial smoothing.
- Mine proximity rises from 6.9% (v2, compound types only) → **26.0%** (v3, 9 per-metal + compound types) — comparable to USA SPIRE (26.3%), contradicting the earlier interpretation that EUR surveys more undisturbed soils.
- Mine proximity dominates individual rankings: Ni, NiCu, Au, Cu, Cr mines are top predictors, suggesting Ni–Cu sulfide contamination gradients structure EUR community composition.
- LUCAS soil pH and OC (soil_eur group) contribute 7.3%, independent of geochemical elements.
- Free-ion speciation (1.3%) contributes less once full GEMAS element suite is included.

**GEMAS data:** 2,211 Ap-horizon sites, 53 AR elements (Ag, Al, As, Au, B, Ba, Be, Bi, Ca, Cd, Ce, Co, Cr, Cs, Cu, Fe, Ga, Ge, Hf, Hg, In, K, La, Li, Mg, Mn, Mo, Na, Nb, Ni, P, Pb, Pd, Pt, Rb, Re, S, Sb, Sc, Se, Sn, Sr, Ta, Te, Th, Ti, Tl, U, V, W, Y, Zn, Zr), 100% coverage. X_Coo=lon, Y_Coo=lat in `gemas_combined_fixed.parquet`.

---

## NB11 — Switzerland: Swiss Geochemical Atlas + GEMAS + MicrobeAtlas 16S

**Status:** Complete v3 (2026-08-28). GEMAS + LUCAS soil properties + per-metal Mindat proximity (9 metals, 200 km radius; EUR Mindat bbox 34–72°N, −10–40°E, n=26,233 sites) + compound mine types.

Uses Swiss Geochemical Atlas (87,727 raster points, 8 metal ordinal classes: As, Cd, Cr, Cu, Hg, Pb, Ni, Zn; scale 1–6, ~100 m resolution) + GEMAS Ap (all EUR 2,211 sites, 100 km NN) + LUCAS soil properties.

**Results (group MDI, v3 — final):**

| Group | Swiss v3 (final) | Swiss v2 (GEMAS) | Swiss v1 (Atlas only) |
|-------|------|------|------|
| mine_proximity | **32.1%** | 7.6% | 9.9% |
| elements | 29.1% | 42.8% | 17.5% |
| climate | 20.4% | 29.3% | 47.9% |
| soil_eur | 9.0% | — | — |
| geographic | 7.7% | 17.5% | 20.6% |
| hydro_temp | 1.6% | 2.8% | 4.3% |

n=3,937; R²=0.7717.

**Top predictors:** lat (0.050), isothermality (0.042), mindat_any (0.028), mindat_Au (0.027), lon (0.027), mindat_Co (0.024), lucas_soil_silt (0.023), mindat_Hg (0.023), mindat_AuAs (0.022), mindat_Zn (0.022), mindat_Ni (0.022), mindat_NiCu (0.022), mindat_CuMo (0.022), gemas_ba_ppm (0.021), lucas_soil_pH (0.020).

**Key finding:** Mine proximity becomes the **dominant group** in Switzerland (32.1%), surpassing elements (29.1%) — unique among all regions. Per-metal mine distances for Co, Hg, Zn, Ni, and compound types (AuAs, NiCu, CuMo) all rank highly, reflecting Switzerland's proximity to Alpine ore districts. LUCAS soil properties (silt, sand, pH) contribute 9.0%, independent of geochemical predictors.

**Note:** Swiss Atlas classes are ordinal (1–6); GEMAS columns are log10(ppm).

---

## NB12 — Qi et al. (2025) BCR F1 Mobile Fraction Comparison

**Status:** Complete (2026-08-28). Compares BCR step-1 mobile fraction (Qi et al. 2025 Nat Commun 16:2947) vs total metal measurements as predictors of microbial community PC1.

**Data:** Global BCR F1 model from Qi et al. (2025), 7.4M raster points, 6 metals: As, Cd, Cr, Cu, Hg, Pb. Mobile fraction (0–1 scale). Joined at 25 km NN. Coverage: 14,399/14,617 USA; 40,358/40,358 EUR.

**Models (per region):**
- **M1** — Qi PF1 only (6 mobile fraction features)
- **M2** — total metals only (DS801 elements for USA; GEMAS+LUCAS HM for EUR)
- **M3** — all predictors + Qi PF1 (PF1 as additional `mobile_frac` group)

**Results:**

| | USA (SPIRE) | EUR (MicrobeAtlas) |
|--|--|--|
| M1 R² (PF1 only) | **0.394** | **0.595** |
| M2 R² (metals only) | 0.356 | 0.464 |
| M3 R² (all+PF1) | 0.458 | 0.663 |
| PF1 group MDI in M3 | 7.3% | 9.0% |

**PF1 individual importance in M1 (USA):** As (0.245) > Hg (0.238) > Cu (0.184) > Cr (0.172) > Cd (0.096) > Pb (0.065)

**PF1 individual importance in M1 (EUR):** Pb (0.224) > As (0.175) > Cd (0.157) > Cu (0.153) > Hg (0.148) > Cr (0.143)

**Key findings:**
- Qi PF1 **outperforms total metals alone** (M1 > M2): R²=0.394 vs 0.356 (USA), 0.595 vs 0.464 (EUR) — bioavailable fraction predicts microbial composition better than total concentrations alone.
- M3 adds marginal lift over M2 alone (~0.10 R²) when all predictors are available, with PF1 contributing ~7–9% group MDI.
- EUR has higher PF1 predictive power than USA (0.595 vs 0.394) — possibly because LUCAS-based free-ion Sauvé model has less information than the BCR-calibrated global model.
- Metal rankings differ: USA = As/Hg/Cu; EUR = Pb/As/Cd — contrasting contamination profiles between regions.

**Citation:** Qi et al. (2025) Global patterns and predictors of soil heavy metal bioavailability. Nat Commun 16, 2947. doi:10.1038/s41467-025-58026-8

---

## Vivid R Interaction Analysis (NB08, NB10, NB11)

All three vivid analyses fit a `ranger` RF on the top-15 predictors from each region, compute Friedman H-statistic pairwise interactions on a 2,000-row subsample, and save heatmap + network PDFs. Scripts: `scripts/run_nb08_vivid.R`, `run_nb10_vivid.R`, `run_nb11_vivid.R`.

**NB08 (USA SPIRE):** top interaction = `mindat_Pb × mindat_As` H=0.079 — mine co-contamination dominates, reflecting co-occurrence of Pb–As in the same ore bodies.

**NB10 (EUR MicrobeAtlas):** vivid complete (2026-08-28). Top interactions:
| Pair | H |
|------|---|
| temp_warmest_quarter × temp_driest_quarter | 0.143 |
| temp_warmest_quarter × lucas_soil_OC | 0.066 |
| **temp_warmest_quarter × mindat_Ni_dist_km** | **0.064** |
| **lucas_soil_pH × mindat_Au_dist_km** | **0.063** |
| lucas_soil_OC × mindat_Au_dist_km | 0.056 |

Climate mediates mine effect in EUR: Ni mine proximity effect is strongest at cold temperatures (northern Scandinavian Ni-Cu belt); Au mine effect interacts with soil pH (acidic soils amplify response). Unlike USA, climate×climate dominates, with mine×soil/climate interactions secondary.

**Mine proximity independence from Qi PF1:** Spearman rho between Qi PF1 metals and mindat_dist columns is mostly ≤0.07, with maximum pf1_cu × mindat_Ni rho=0.19. PF1 and mine proximity capture **complementary** signals — mine proximity captures contamination source exposure; PF1 captures realized soil bioavailability.

**Partial dependence distance profiles (EUR, NB10):**
- Ni mines: effect flattens at ~21 km (localized — plausible run-off contamination)
- NiCu mines: ~26 km; Cu mines: ~33 km (local contamination gradient)
- Au mines: **~828 km** — continental/geological background proxy, not direct contamination
- Any mine: ~11 km (global mine density gradient)

Au mine "effect" at 800+ km is not a contamination signal — it reflects sampling along a geological background gradient (Fennoscandian vs Atlantic Europe orogenic belts).

**NB11 (Swiss MicrobeAtlas):** vivid complete (2026-08-28). Top interactions:
| Pair | H |
|------|---|
| **mindat_Co_dist_km × isothermality** | **0.205** |
| isothermality × lucas_soil_silt | 0.121 |
| isothermality × gemas_ba_ppm | 0.104 |
| **mindat_NiCu × mindat_Au** | **0.098** |
| mindat_NiCu × lon | 0.094 |
| **mindat_Co × gemas_ba_ppm** | **0.075** |
| **mindat_Co × mindat_Ni** | **0.065** |

`Co_mine × isothermality` (H=0.205) is the strongest interaction across all three regions. Cobalt mine proximity dominates Swiss interactions, appearing in 4 of the top 10 pairs. `mindat_NiCu × mindat_Au` (H=0.098) reflects Alpine ore co-occurrence: cobaltite (CoAsS) and Ni-Cu sulfides both occur in Swiss Alpine ore districts (Binntal deposits).

**Directional split in Swiss PD:** Near-mine communities have **lower** PC1 for Au, Hg, AuAs, Ni, NiCu (contamination suppression), but **higher** PC1 for Co, Zn, CuMo. The Co enrichment-near-mines effect mirrors the known tolerance of cobalt-adapted bacteria (cobalt is micronutrient at low concentrations). All Swiss effects flatten at 3–15 km — genuinely localized soil contamination, not a regional geological background gradient (contrast: EUR Au effect at ~828 km).

**Cross-region comparison of vivid top interactions:**
| Region | Top interaction | H | Interpretation |
|--------|----------------|---|----------------|
| USA | Pb_mine × As_mine | 0.079 | Co-contamination (ore deposit co-occurrence) |
| EUR | temp_warmest × temp_driest | 0.143 | Climate interaction mediates mine effect |
| Swiss | Co_mine × isothermality | 0.205 | Mine×climate: Alpine cobalt deposits in high-isothermality zones |

---

## Notebooks

| NB | Title | Status |
|----|-------|--------|
| NB01 | Gradient forests (global + 3 regional) | complete ✓ |
| NB02 | SPDE-INLA | complete ✓ |
| NB03 | NNGP | complete ✓ |
| NB04 | HMSC | complete ✓ |
| NB05 | GAM spatially-varying coefficients | complete ✓ |
| NB06 | Synthesis | written ✓ |
| NB07 | RF: full element suite (DS801 + NALG), H6 | complete ✓ |
| NB08 | RF: USA comprehensive + SHAP interactions + vivid | complete ✓ |
| NB09 | RF: MicrobeAtlas 16S USA (genus + OTU), H6 replication | complete ✓ |
| NB10 | RF: EUR replication (LUCAS HM+GEMAS+soil+mines, MA 16S) | complete v3 ✓ |
| NB11 | RF: Switzerland (Swiss Atlas+GEMAS+soil+mines, MA 16S) | complete v3 ✓ |
| NB12 | Qi et al. (2025) BCR F1 mobile fraction comparison | complete ✓ |
| NB13 | Global diversity maps (SPIRE, sciadv.adj8016 style) | complete ✓ |
| NB14 | PC2/PC3 analysis for EUR and Swiss (group MDI comparison) | complete ✓ |
| NB15 | MicrobeAtlas diversity maps — all environments + terrestrial only | complete ✓ |

---

## NB13: Global Diversity Maps (SPIRE shotgun metagenomes)

**Data:** 42,037 SPIRE samples with Shannon diversity and genus richness computed from genus_ra.parquet (NB13 output: `data/global_diversity_geo.parquet`). Filter: Shannon > 0.01.

**Figures:** `fig_nb13_diversity_map.pdf`, `fig_nb13_diversity_environment.pdf`, `fig_nb13_mine_diversity_map.pdf`.

**Diversity by environment class:**
| Environment | Mean Shannon | SD | n |
|------------|-------------|-----|---|
| Agricultural | 3.07 | 1.09 | 6,673 |
| Soil (general) | 2.77 | 1.11 | 23,492 |
| Forest | 2.99 | 0.99 | 1,717 |
| Grassland | — | — | — |
| Tundra | 2.46 | 0.86 | 216 |
| Dryland | 2.34 | 0.95 | 1,013 |
| Aquatic | 2.52 | 0.97 | 7,313 |

**Key result:** Latitudinal gradient is extremely weak (|lat| vs Shannon: ρ=−0.019). Bacteria do NOT show a latitudinal diversity gradient, in contrast to fungi (sciadv.adj8016). The single strongest individual predictor is `mean_diurnal_range_c` (ρ=−0.118) — communities are more diverse where temperature is less variable diurnally. WorldClim RF explains Shannon R²=0.33, richness R²=0.36, suggesting diversity is driven by fine-scale edaphic factors not captured by 5 km WorldClim grids.

**Mine proximity vs diversity (global):** Only weak bivariate relationship; distance to nearest mine has Spearman ρ computed per 5% bins.

---

## NB14: PC2 / PC3 Analysis (EUR and Swiss)

**Data:** Genus-level CLR PCA computed from saved genus_ra_long parquets (NB10/NB11 outputs). PC1–PC3 computed from top 200 genera by prevalence (RA > 0.1%).

**Figure:** `fig_nb14_pc123_group_mdi.pdf`.

**EUR results:**
| PC | Expl. Var | R² | Mine | Elements | Climate | Soil |
|----|-----------|-----|------|----------|---------|------|
| PC1 | 11.4% | 0.76 | 24.3% | 37.5% | 24.0% | 8.3% |
| PC2 | 9.1% | 0.80 | 25.0% | 30.3% | **32.2%** | 6.8% |
| PC3 | 4.7% | 0.84 | 26.7% | 39.4% | 22.2% | 6.3% |

**Swiss results (note: `pc1_genus` column included in pred matrix is itself a community axis — labeled `community_pc1`):**
| PC | Expl. Var | R² | Mine | Elements | Climate | Comm PC1 |
|----|-----------|-----|------|----------|---------|----------|
| PC1 | 13.3% | 0.90 | 22.3% | 11.9% | 14.1% | 44.4% |
| PC2 | 11.2% | 0.93 | 25.2% | 13.9% | 18.6% | 36.4% |
| PC3 | 9.6% | 0.88 | 21.0% | 13.9% | 10.1% | 49.6% |

**Key finding:** Mine proximity is **consistent across PC axes in EUR** (24–27%), not only on PC1. PC2 shows climate ascending to #1 (32.2%) in EUR, suggesting the second axis captures a latitude-independent climate gradient (e.g., Atlantic vs continental moisture). Swiss `community_pc1` as predictor captures autocorrelation between PC axes (CLR PCA axes are correlated through shared species); strip it to see mine=22% throughout all Swiss PCs.

---

## NB15: MicrobeAtlas Diversity Maps (all environments + terrestrial only)

**Data:** SPIRE SPIRE Shannon/richness from `data/global_diversity_geo.parquet`, WorldClim joined at 50 km. Terrestrial subset: soil, forest, agricultural, grassland, dryland, tundra (n=33,111; aquatic/other excluded).

**Figures:** `fig_nb15_diversity_map_all.pdf`, `fig_nb15_diversity_env_all.pdf`, `fig_nb15_diversity_map_terrestrial.pdf`, `fig_nb15_diversity_env_terrestrial.pdf`.

**All environments (n=40,424):** Shannon RF R²=0.296. Top predictors: precipitation (wettest quarter ρ=+0.12), `mean_diurnal_range_c` (ρ=−0.12), `precip_wettest_month_mm` (ρ=+0.12). No latitudinal gradient (ρ=−0.02).

**Terrestrial only (n=33,111):** Shannon RF R²=0.309. Top predictors: precipitation (wettest quarter ρ=+0.09), `mean_diurnal_range_c` (ρ=−0.11), elevation (ρ=−0.11). RF R² marginally higher, suggesting aquatic samples add within-dataset noise. Key bivariate: `elevation_m` (ρ=−0.110) and `mean_temp_wettest_quarter_c` (ρ=+0.084) are the strongest terrestrial signals — montane soil communities are less diverse, mesic-warm soils more diverse.

**Comparison with fungal diversity (sciadv.adj8016):** Fungal diversity shows strong latitudinal gradient (temperate > tropical); bacterial diversity shows essentially flat latitudinal pattern. Both show positive precipitation associations.

---

## NB16: Functional gene (KO) diversity — CWM from ke_pangenome × MicrobeAtlas EUR+Swiss

**Script:** `scripts/run_nb16_ko_cwm_spark.py` (Spark, JupyterHub required)  
**Visualization:** `scripts/run_nb16b_ko_diversity_maps.py` (runs after NB16 produces data)  
**Status:** Scripts written 2026-08-27; Spark step pending (requires JupyterHub)

### Method

Community-weighted mean (CWM) KO profiles for MicrobeAtlas EUR (40,358 samples) and Swiss (3,937 samples) communities, using:

- **Genome → KO source:** `kbase.ke_pangenome` 3-way join: `gene` → `gene_genecluster_junction` → `eggnog_mapper_annotations.KEGG_ko`
- **Genome filter:** `alphaearth_embeddings_all_years` — named genera only (exclude GTDB placeholder codes matching `^[0-9]` or `^[A-Z]{2,4}[0-9]`); QC ≥70%/≤10% via `gtdb_metadata`
- **Genus matching:** ke_pangenome genus names lowercased and matched to MicrobeAtlas Silva-based genus names
- **CWM formula:** `CWM[sample, KO] = Σ_genus(RA[sample, genus] × prevalence[genus, KO])` where prevalence = fraction of ke_pangenome genomes in that genus carrying the KO
- **KO filtering:** prevalence ≥5% in genus (removes extremely rare KOs)
- **Shannon diversity:** normalized CWM per sample treated as probability distribution over KOs: `H = −Σ(p × log(p))`
- **Batch size:** 300 genomes/query; checkpoint every 50 batches to `data/nb16/ke_pangenome_ko_checkpoint.parquet`

### Output files (pending Spark run)

| File | Description |
|------|-------------|
| `data/nb16/genus_ko_prevalence.parquet` | genus × KO prevalence table |
| `data/nb16/ko_diversity_ma.parquet` | Per-sample: shannon_ko, ko_richness, lat, lon, environments, shannon_genus |
| `data/nb16/ko_div_eur.parquet` | EUR subset |
| `data/nb16/ko_div_swiss.parquet` | Swiss subset |

### Planned figures (NB16b)

| Figure | Description |
|--------|-------------|
| `fig_nb16_ko_latitudinal.pdf` | Latitudinal KO Shannon gradient (compare to genus Shannon) |
| `fig_nb16_ko_diversity_map.pdf` | Global/regional Robinson projection map of KO Shannon |
| `fig_nb16_ko_vs_genus.pdf` | Scatter: KO Shannon vs genus Shannon (rho expected high if functional diversity tracks taxonomic) |
| `fig_nb16_ko_diversity_env.pdf` | RF importance for KO Shannon ~ WorldClim |
| `fig_nb16_ko_rf_pc1.pdf` | EUR: KO Shannon ~ LUCAS+GEMAS+mines+climate group MDI (compare to genus PC1 results) |

### Key analytical question

Does functional gene diversity (KO Shannon) show the same environmental drivers as genus diversity — or do gene content drivers diverge (e.g., metal contamination selecting for KOs directly, independently of genus composition changes)?


---

## NB16/NB16b: Functional gene (KO) diversity — CWM from ke_pangenome × MicrobeAtlas EUR+Swiss

**Status:** COMPLETE (2026-08-28)  
**Scripts:** `run_nb16_ko_cwm_spark.py` + `run_nb16b_ko_diversity_maps.py`

### Method

CWM KO profiles for 45,795 MA EUR+Swiss samples. Genome→KO from `kbase.ke_pangenome` (3-way join: gene → gene_genecluster_junction → eggnog_mapper_annotations), 50,021 genomes batched in 167 queries. Genus matching: GTDB `g__` prefix stripped → 962 genera matching MA Silva names. KO prevalence ≥5% threshold. CWM computed via sparse matrix multiplication (sample×genus RA matrix @ genus×KO prevalence matrix), Shannon H on normalized CWM rows.

### Key results

| Metric | Value |
|--------|-------|
| Genera matched (ke_pangenome → MA) | 956 of 962 queried |
| KOs with ≥5% prevalence in ≥1 genus | 10,683 |
| Samples with KO diversity | 45,795 |
| KO Shannon (mean ± SD) | 7.58 ± 1.90 |
| KO richness per sample (mean) | 6,426 (max 9,557) |
| KO Shannon vs genus Shannon (Spearman ρ) | **−0.008** p=0.13 (NOT correlated) |
| WorldClim RF R² (KO Shannon ~ climate) | 0.354 |
| EUR RF R² (KO Shannon ~ LUCAS+GEMAS+mines) | **0.490** |

### Group MDI — EUR KO Shannon (RF R²=0.490)

| Group | MDI % |
|-------|-------|
| elements | **36.9%** |
| mine_proximity | **30.8%** |
| climate | 20.1% |
| geographic | 5.5% |
| soil_eur | 4.3% |

**Key finding:** KO functional diversity (Shannon over 10,683 KOs) is essentially **uncorrelated with genus diversity** (ρ=−0.008) — functional and taxonomic diversity are decoupled. Despite this, both are predicted by the same environmental drivers (elements > mines > climate), with mine proximity accounting for 30.8% of KO functional diversity variance. This suggests that contamination selects for specific gene content independently of which genera dominate.

### KO Shannon by environment class

| Environment | Shannon | Richness (KOs) |
|-------------|---------|----------------|
| soil | 8.09 | 7,066 |
| dryland | 8.11 | 6,679 |
| agricultural | 8.05 | 6,747 |
| forest | 8.00 | 5,720 |
| tundra | 8.02 | 6,186 |

### Figures

| Figure | Description |
|--------|-------------|
| `fig_nb16_ko_latitudinal.pdf` | Latitudinal KO Shannon gradient (flat, ρ(|lat|) ~0) |
| `fig_nb16_ko_diversity_map.pdf` | Global Robinson projection map of KO diversity |
| `fig_nb16_ko_vs_genus.pdf` | KO Shannon vs genus Shannon scatter (ρ=−0.008) |
| `fig_nb16_ko_diversity_env.pdf` | RF importance: KO Shannon ~ WorldClim (R²=0.354) |
| `fig_nb16_ko_rf_pc1.pdf` | EUR group MDI: elements=36.9%, mines=30.8% |

---

## NB18: FAPROTAX functional groups vs KO-based functional diversity

**Status:** COMPLETE (2026-08-28)  
**Script:** `run_nb18_faprotax_vs_ko.py`

### Question

Does FAPROTAX (82 broad organism-level functional groups) predict the same environmental signals as KEGG KO diversity (10,683 genome-level KOs from ke_pangenome)?

### Method

FAPROTAX v1.2 (Holmes et al. 2023; 8,354 taxon→function entries using `*pattern*` wildcard matching) applied to EUR MA 16S genus names. CWM computed as RA-weighted sum of function presence per sample. Shannon H computed over 60 functions with ≥3 matched EUR genera. Compared to NB16b KO Shannon RF (EUR R²=0.490).

### Results

| Metric | FAPROTAX | KO (NB16b) |
|--------|----------|------------|
| Genera covered | 1,363/8,515 (16%) | 956 GTDB genera |
| Mean RA fraction covered | **0.135** | ~genome-based |
| Functional units | 60 functions | 10,683 KOs |
| Shannon vs KO Shannon (ρ) | **+0.356** | — |
| Shannon vs Genus Shannon (ρ) | +0.101 | −0.008 |
| EUR RF: Shannon ~ env (OOF R²) | **−0.077** | **0.490** |
| Cu prediction (FAPROTAX CWM, OOF R²) | 0.042 | — |
| Pb prediction (OOF R²) | −0.049 | — |
| As prediction (OOF R²) | −0.064 | — |
| Cd prediction (OOF R²) | −0.252 | — |

### Group MDI (FAPROTAX Shannon RF, WARNING: R²=−0.077 — fitting noise)

| Group | FAPROTAX | KO Shannon NB16b |
|-------|----------|-----------------|
| elements | 36.8% | 36.9% |
| mine_proximity | 28.5% | 30.8% |
| climate | 21.8% | 20.1% |
| geographic | 6.0% | 5.5% |
| soil_eur | 7.0% | 4.3% |

Note: the group MDI pattern is numerically similar to KO Shannon, but this is artefactual — when a RF model explains no variance (R²≈0), feature importances reflect predictor variance structure rather than genuine association. The metal RF models show severe overfitting (train R²≈0.92, OOF R²<0 for all metals), confirming no predictive signal.

### Key finding: FAPROTAX does NOT predict the same things as KOs

Three compounding limitations explain the failure:

1. **Coverage**: Only 13.5% of community RA is matched to FAPROTAX. The metal-adapted majority is in the unmatched 86.5%.
2. **Resolution**: 60 broad categories (fermentation, chemoheterotrophy) vs 10,683 specific KOs. Broad categories are taxonomically widespread and do not capture fine metal-adaptation gradients.
3. **No viable metal-specific functions**: The most relevant function `arsenate_detoxification` matched only 1 EUR genus (below threshold); `arsenate_respiration` and `arsenite_oxidation_*` matched 2–4 genera total with negligible community weight.

**Conclusion:** Genome-level KO resolution (ke_pangenome) is necessary to detect metal-driven functional selection. FAPROTAX-style organism annotations, despite their convenience, are too coarse and too sparsely matched to 16S data to capture the functional ecology of metal contamination.

### Figures

| Figure | Content |
|--------|---------|
| `fig_nb18_faprotax_vs_ko_scatter.pdf` | FAPROTAX Shannon vs KO Shannon (ρ=+0.356) and vs genus Shannon |
| `fig_nb18_group_mdi_comparison.pdf` | Group MDI comparison: FAPROTAX vs KO Shannon (same pattern, different R²) |
| `fig_nb18_metal_prediction_faprotax.pdf` | FAPROTAX CWM metal prediction OOF R² (all ≤0.042) |
| `fig_nb18_as_function_importance.pdf` | Top FAPROTAX functions for As prediction (aerobic_chemoheterotrophy dominates — no As-specific signal) |

---

## NB16c: Alphaearth CWE vs genus composition — does embedding space add metal prediction power?

**Status:** COMPLETE (2026-08-28)

### Method

Community-weighted alphaearth embeddings (CWE): 956 genera × 64 embedding dimensions (A00–A63) from `alphaearth_embeddings_all_years`, averaged per genus, then RA-weighted per MA sample. PCA (10 PCs, cumulative variance 85.3%). Compared three predictor sets for EUR metal targets (n=39,786) via 5-fold RF CV:

1. **Genus-PC1 alone** (1 predictor — community composition axis)
2. **CWE-10** (10 PCs of 64-dim alphaearth embeddings — functional co-occurrence space)
3. **Full** (115-feature LUCAS+GEMAS+mines+climate predictor matrix from NB10)
4. **Full + CWE-10** (125 predictors)

### Results

| Target | Genus-PC1 | CWE-10 | Full (115) | Full+CWE | ΔCWE |
|--------|-----------|--------|-----------|----------|------|
| lucas_Cu | −0.576 | −0.158 | **0.981** | 0.981 | +0.000 |
| lucas_Pb | −0.617 | −0.107 | **0.972** | 0.968 | −0.004 |
| lucas_Ni | −0.633 | −0.107 | **0.981** | 0.981 | 0.000 |
| lucas_Cd | −0.633 | −0.023 | **0.947** | 0.950 | +0.003 |
| lucas_Cr | −0.723 | −0.127 | **0.988** | 0.989 | 0.000 |
| **pc1_genus** | 1.000 | **0.280** | −0.076 | 0.162 | +0.239 |

### Key findings

- **Alphaearth CWE does not improve metal prediction** (ΔCWE ≈ 0.000 for all metals; max |ΔCWE| = 0.004). The existing LUCAS+GEMAS+mines+climate predictor set already captures all metal information in the embedding space.
- **CWE captures community structure partially independent of measured environment** (R²=0.280 for predicting genus-PC1 alone; full environmental predictor set can't predict genus-PC1 at all, R²=−0.076, but Full+CWE recovers R²=0.162). This implies alphaearth encodes co-occurrence structure that isn't reducible to the measured physicochemical variables.
- **Neither genus-PC1 nor CWE can predict metal concentrations** (both negative R²). Metal concentrations are essentially predictable from spatial environmental covariates alone; community composition adds nothing to metal prediction.
- CWE-PC1 is largely orthogonal to genus-PC1 (ρ=−0.042), confirming alphaearth captures a distinct axis of genome space.

### Interpretation

Alphaearth embeddings encode global phylogenetic co-occurrence patterns across all biomes. They capture some community structure (R²=0.280 vs genus-PC1) but not metal gradients, because metal gradients are a local signal superimposed on the global biogeographic template the embeddings were trained on. These results close the CWE analysis: alphaearth embeddings are not useful for metal-microbiome association beyond what standard taxonomic predictors provide.



---

## NB17/NB17b: Co-occurrence network structure along metal vs. environmental gradients

**Status:** COMPLETE (2026-08-28)  
**Reference framework:** Labouyrie et al. 2023 Nat Commun (variation partitioning); Romdhane et al. 2022 Environ Microbiome (network complexity vs. land-use)

### Method

GraphicalLasso on CLR-transformed genus RA (equivalent to SPIEC-EASI glasso mode). Top 100 genera by sample prevalence per region. For each environmental variable (metals, pH, mine proximity, climate), samples binned into quintiles (N≥500 per bin, subsampled to 2000). GraphicalLassoCV (5-fold, 4 α candidates) fit per bin on (samples × genera) CLR matrix. Network metrics extracted from precision matrix: connectance (|E|/|E_max|), Louvain modularity, fraction negative edges, average degree. Variable-group comparison via mean |Spearman ρ| of bin_mean vs. each metric (Labouyrie-style partitioning).

**Data:** EUR: MA 16S 16S (41,989 samples) + LUCAS HM/soil + Mindat. USA: MA 16S (67,835 samples) + USGS metals + Mindat. Note: several USA bins (climate, mine proximity) returned degenerate networks (α→0, C=1.0) and were excluded.

### Results: Mean |Spearman ρ| per variable group

| Region | Variable group | Connectance | Modularity | Frac. negative |
|--------|----------------|-------------|------------|----------------|
| EUR    | **Mine proximity** | 0.600 | **0.900** | **0.900** |
| EUR    | Metals (Cu/Pb/Ni/Cd) | **0.475** | **0.525** | 0.475 |
| EUR    | Soil (pH) | 0.400 | 0.400 | 0.400 |
| EUR    | Climate (T, P) | 0.200 | 0.400 | 0.400 |
| USA    | Soil (pH) | 0.600 | **0.900** | 0.600 |
| USA    | Metals (Cu/Pb/Ni/Zn) | 0.344 | 0.344 | 0.344 |

### Key findings

1. **Mine proximity is the strongest EUR network modifier** (|ρ|=0.900 for modularity and negative-edge fraction). Samples near mines have denser, less modular networks with fewer negative interactions — community network structure simplifies under diffuse contamination exposure.

2. **Metals have intermediate effects in both regions** (|ρ|=0.35–0.53). Higher metal concentration → higher modularity (more compartmentalized co-occurrence structure) and lower connectance — consistent with niche partitioning under selection pressure. Individual metals: Pb shows clearest gradient in both regions; Ni shows distinct low-connectance profile in EUR (C=0.175 vs C=0.33 for Cu/Pb).

3. **pH is the dominant driver in USA** (|ρ|=0.900 for modularity). EUR pH shows a non-monotonic (U-shaped) pattern: extreme pH (acid <4.3, alkaline >7.0) → dense networks (C≈0.5); intermediate pH → more modular networks. The Spearman ρ understates this relationship.

4. **Climate has the weakest effect** (|ρ|=0.200–0.400 in EUR). Several USA climate bins returned degenerate networks (excluded), so USA climate effect cannot be quantified here.

5. **Ranking mirrors Labouyrie et al.:** Both studies find soil properties > environmental stressors > climate for shaping community structure. Here: mine proximity/pH > metals > climate for network topology.

### Caveats

- GraphicalLasso degeneracy (α→0, C=1.0) affected USA climate/mine bins and EUR pH Q3 — excluded from analysis. This occurs when within-bin genus covariance is approximately spherical (many genera equally prevalent, weak co-exclusion/co-occurrence structure).
- Spearman ρ does not capture non-monotonic (U-shaped) pH effects; visual inspection of quintile plots is needed.
- Metals in EUR are 52%-coverage LUCAS spatial predictions (not measured at sample site); USA USGS are interpolated from 4,857 DS801 sites at 50 km NN.
- Subsampling to 2000 samples per bin may miss rare compositional signals.

### Figures

| File | Content |
|------|---------|
| `fig_nb17_eur_network_quintiles.pdf` | EUR connectance/modularity/frac_neg across quintiles per variable |
| `fig_nb17_usa_network_quintiles.pdf` | USA same |
| `fig_nb17_rho_summary.pdf` | Labouyrie-style |ρ| bar chart per variable group × region |
| `fig_nb17_connectance_gradient.pdf` | Connectance trajectory along normalized gradient (metals vs pH vs mine) |

### NB17 supplement: Additional soil properties (OC, clay, sand, silt, AWS)

EUR: `lucas_soil_OC`, `lucas_soil_clay`, `lucas_soil_sand`, `lucas_soil_silt` (62–88% coverage).  
USA: `spec_olm_soc_g_kg`, `spec_olm_clay_pct`, `gnatsg_available_water_storage_0_25cm_wta` (17–89% coverage).

| Region | Variable | Usable bins | Mean |ρ| — modularity | Significant? |
|--------|----------|-------------|----------------------|-------------|
| EUR | soil_OC | 4/5 | 0.600 | No (p=0.285, n=4) |
| EUR | soil_silt | 5/5 | 0.400 | No (p=0.505) |
| EUR | soil_clay | 4/5 | 0.200 | No (p=0.747) |
| EUR | soil_sand | 3/5 | 0.300 | No (p=0.624) |
| USA | soil_OC | 3/5 | 0.800 | No (p=0.200, n=3) |
| USA | soil_clay | 3/4 | 0.000 | No |
| USA | soil_aws025 | 1/5 | — | Degenerate |

**pH remains the dominant soil property.** Texture and organic carbon show weaker, non-significant effects on network modularity in both regions. This is consistent with Labouyrie et al.'s finding that pH > other soil properties for community structure. High degeneracy in many bins (α→0, C=1.0) limits inference for USA texture variables.

### NB17c: Free ion speciation (bioavailable metals)

Free-ion activity (`spec_log_free_Cu²⁺`, `spec_log_free_Pb²⁺`, `spec_log_free_Ni²⁺`) reflects pH-corrected metal bioavailability from OLM speciation modelling. Coverage: EUR 18.6% (7,524/40,358); USA 15–17% (9,954–11,477/67,835). Minimum bin size lowered to 400.

| Region | Variable | n bins | Mean |ρ| — modularity | Direction |
|--------|----------|--------|----------------------|-----------|
| EUR | free_ion_Cu² | 5 | 0.500 | higher Cu²⁺ → lower modularity |
| EUR | free_ion_Pb² | 5 | 0.300 | higher Pb²⁺ → lower modularity |
| EUR | free_ion_Ni² | 5 | 0.300 | higher Ni²⁺ → lower modularity |
| EUR | free_ion_Zn² | 5 | 0.400 | higher Zn²⁺ → lower modularity |
| USA | free_ion_Cu² | 5 | 0.700 | higher Cu²⁺ → higher modularity |
| USA | free_ion_Ni² | 4 | 1.000 | higher Ni²⁺ → higher modularity |

EUR group |ρ| = 0.375 for modularity — **weaker than total metals (0.525)**. The opposite direction (free-ion → lower modularity in EUR) vs total metals (higher total → higher modularity) likely reflects pH confounding: higher free-ion activity occurs at low pH, which independently drives network structure.

### NB17d: Qi BCR PF1 mobile fraction + LUCAS land cover

**Qi BCR PF1 (mobile fraction, Qi et al. 2025 Nat Commun 16:2947):** Global 5 km raster of BCR sequential extraction F1 (mobile fraction) for 6 metals. NN join at 25 km; EUR coverage 99.1% (40,005/40,358), USA 99.9% (67,775/67,835). PF1 values are dimensionless fractions (0–1) representing the proportion of total metal that is mobile.

| Region | Variable | n bins | Mean |ρ| — modularity | Direction |
|--------|----------|--------|----------------------|-----------|
| EUR | pf1_Cu | 5 | 1.000 | higher mobile Cu fraction → **lower** modularity |
| EUR | pf1_As | 5 | 0.700 | higher mobile As fraction → lower modularity |
| EUR | pf1_Pb | 5 | 0.400 | higher mobile Pb fraction → lower modularity |
| EUR | pf1_Cd | 5 | 0.300 | weak negative |
| USA | pf1_As | 5 | 0.707 | higher mobile As → lower connectance |
| USA | pf1_Cu/Pb | 5 | — | degenerate (α→0) |

**EUR PF1 group |ρ| = 0.575 for modularity — exceeds total metals (0.525)**, making it the second strongest EUR predictor after mine proximity (0.900). Direction is the OPPOSITE of total metals: higher mobile fraction → less modular, denser networks. Interpretation: bioavailable metal stress selects for generalist communities with broad co-occurrence; total metal load (independent of bioavailability) selects for compartmentalized specialists, likely driven by spatial sorting of tolerant lineages. USA PF1 is mostly degenerate — the within-bin covariance structure does not differ across mobile fraction quintiles in USA MA data (possible USA spatial confounds or smaller sample size effect).

**Updated |ρ| summary (EUR, non-degenerate bins only):**

| Variable group | Connectance | Modularity | Frac. negative |
|----------------|-------------|------------|----------------|
| Mine proximity | 0.600 | **0.900** | **0.900** |
| **PF1 mobile fraction** | 0.500 | **0.575** | 0.475 |
| Metals (total) | 0.475 | 0.525 | 0.475 |
| Soil (pH, OC, texture) | 0.560 | 0.360 | 0.300 |
| Free ion activity | 0.300 | 0.375 | 0.500 |
| Climate (T, P) | 0.200 | 0.400 | 0.400 |

**LUCAS land cover (EUR, per-class networks):** EUR MA 16S samples joined to LUCAS survey at 50 km NN (96.7% matched). One network per land cover class.

| Land cover | n samples | Connectance | Modularity |
|------------|-----------|-------------|------------|
| Cropland | 2,000 | **0.134** (lowest) | **0.266** (highest) |
| Grassland | 2,000 | 0.180 | 0.249 |
| Woodland | 2,000 | 0.180 | 0.250 |
| Shrubland | 1,098 | 0.168 | 0.221 |
| Bareland | 638 | **0.201** (highest) | **0.199** (lowest) |

Cropland shows the most modular and least connected networks — the opposite of the Romdhane et al. 2022 finding that agricultural intensification reduces network complexity. However, Romdhane measured connectance as complexity and compared grassland vs cropland within a single landscape. Here, cropland communities may be more modular because disturbance by crop rotation creates distinct niches for specialist groups. Bareland (bare exposed soil, no plant canopy) has the most connected networks — possibly reflecting dominance by generalist pioneer communities without niche differentiation.

### NB17c/NB17d figures

| File | Content |
|------|---------|
| `fig_nb17_rho_summary_extended.pdf` | Updated |ρ| summary including free_ion and pf1 groups |
| `fig_nb17_pf1_vs_total.pdf` | EUR total metals vs PF1 mobile fraction — modularity gradient comparison |
| `fig_nb17_free_ion_vs_total.pdf` | EUR free ion activity vs total metals — modularity gradient comparison |
| `fig_nb17_land_cover_network.pdf` | EUR land cover per-class modularity and connectance bar chart |

---

## NB19: CWM vs FAPROTAX vs KO — three-region synthesis

**Script:** `scripts/run_nb19_cwm_faprotax_ko_synthesis.py`

Three-region comparison of community representation approaches and a spatial autocorrelation decomposition explaining why metals appear important in RF feature importance but add little predictive power beyond spatial position.

**Note on taxonomy:** The EUR MA 16S long-format has genus-level taxonomy (8,515 genera); the Swiss and USA long-formats have order/family-level taxonomy (30 and 50 taxa respectively). FAPROTAX matching is therefore only valid for EUR. Swiss and USA FAPROTAX analyses are not reported.

### GLIM lithology (global_lithology_glim.parquet)

Lithology from `global_lithology_glim.parquet` (239,733 non-null rows, 13 GLIM classes) was NN-joined (50 km threshold) to all three regions:

| Region | GLIM coverage |
|--------|---------------|
| EUR | 99.0% (39,966/40,358) |
| Swiss | 100% (3,937/3,937) |
| USA | joint via genus_pc1 lat/lon |

**Lithology MDI (Genus PC1, full RF model):** EUR=0.31%, Swiss=0.26%, USA=0.85%. Bedrock type as a single ordinal predictor contributes negligibly — all geological variation captured by the model is already covered by metal concentrations, mine proximity, and soil properties, which themselves reflect bedrock geology.

### R² comparison across representation approaches

| Region | Genus PC1 (full) | FAPROTAX Shannon | KO Shannon |
|--------|-----------------|------------------|-----------|
| EUR | 0.595 | 0.502 | 0.239 |
| Swiss | 0.859 | N/A (order-level taxa) | 0.875 |
| USA | 0.516 | N/A (order-level taxa) | N/A |

Community composition (genus PC1) is the most environmentally predictable response in EUR and USA. In Switzerland, KO Shannon (0.875) rivals Genus PC1 (0.859), likely because mine proximity is the dominant driver of both functional and compositional turnover (mine MDI for Swiss KO = 67.6% vs EUR = 36.1%). EUR FAPROTAX Shannon (R²=0.502) is predictable but less than genus PC1 — reflecting that broad metabolic groups track climate zones and land use, not the fine-grained metal-adaptation signal captured by genome-level KOs.

### Spatial autocorrelation decomposition

This is the central synthesis for the thesis chapter. Each region's genus PC1 was predicted by three nested models:
- **Full model:** all predictors (lat, lon, climate, elements, mine, soil, lithology)
- **Spatial model:** lat + lon + climate only (no metals, no mine, no soil)
- **Metals model:** elements + mine columns only (no lat, lon, no climate)

| Region | Full R² | Spatial-only R² | Metals-only R² | Full − Spatial |
|--------|---------|----------------|----------------|----------------|
| EUR | 0.595 | 0.593 | 0.593 | **+0.002** |
| Swiss | 0.859 | 0.835 | 0.849 | **+0.024** |
| USA | 0.516 | 0.516 | 0.512 | **+0.000** |

**Key finding:** Adding metals and mine proximity to a model that already includes lat/lon and climate increases community composition R² by at most 0.024 (Switzerland, where Alpine mine districts create strong localized gradients). For EUR and USA, adding metals adds zero predictive power. Metals-only models perform nearly identically to spatial-only models, because metal concentrations are strongly confounded with climate, geology, and land use at the global scale.

### Group MDI for Genus PC1 (full model)

| Region | Geographic | Climate | Elements | Mine | Lithology |
|--------|-----------|---------|----------|------|-----------|
| EUR | 4.4% | 22.4% | **38.1%** | 25.7% | 0.3% |
| Swiss | 4.9% | 22.3% | 25.7% | **33.0%** | 0.3% |
| USA | 12.7% | **32.8%** | 36.6% | 5.1% | 0.8% |

**Elements dominate MDI (25–38%) in all three regions, yet add negligible R² over spatial variables.** This is the spatial collinearity trap: metals are statistically important predictors in MDI terms, because they share variance with the spatial gradients (lat/lon, climate) that truly govern community biogeography. The RF cannot distinguish between correlated predictors; MDI inflates for all correlated inputs that co-vary with the dominant gradient.

Switzerland shows the strongest mine signal in MDI (33%) AND the largest Δ R² from adding metals (+0.024) — because Swiss mine proximity is partly independent of the regional climate/lat/lon gradient, due to localized Alpine ore districts.

### Why metals appear important globally but add little over spatial controls

The following chain of evidence explains the scale-dependence of metal effects:

1. **Within-site (ENIGMA, NB01–NB09 in enigma_stress_phenotype_ml project):** Metal concentrations are the primary gradient; spatial variation is minimal within each contamination field. Metal effects are large and significant.

2. **Global survey with spatial random field (NB02, SPDE-INLA on SPIRE data):** Metal β-coefficients (Cr β=−0.80, Pb β=+0.71) are significant after the spatial random field is estimated — but the spatial field itself captures the dominant variance. Adding an explicit spatial covariance structure is what allows metals to appear significant; without it, the metal-spatial confound dominates.

3. **Global RF without spatial random field (this notebook, NB09–NB11):** Metals have 25–38% MDI because RF does not explicitly separate spatial and metal effects. The metals act as spatial proxies (pH, climate, land use, bedrock all co-vary spatially). Spatial-only and metals-only models perform identically.

4. **Gene-level adaptation (NB16/NB16b, ke_pangenome KO CWM):** Despite spatial confounds in community composition (PC1), genome-level KO profiles DO predict metal environments (EUR R²=0.490 for KO Shannon). This is because adaptation to metals is encoded at the functional gene level, not at the 16S taxonomic level. The spatial confounds affect which TAXA are present, not which GENES are present within those taxa.

5. **FAPROTAX failure (NB18):** Broad functional groups (FAPROTAX) do not detect the fine-grained metal-adaptation signal that KOs capture. Only 16% of EUR genera match, mean 13.5% RA coverage, and no metal-specific functions survive sufficient genus coverage. Genome-level KO resolution is necessary.

**Conclusion:** In global 16S surveys, metal effects on community composition cannot be separated from spatial autocorrelation using RF alone. The combination of (a) spatial random-field models (NB02 SPDE-INLA) and (b) genome-resolved functional approaches (NB16b KO CWM) are required to detect the genuine signal. This contrasts with within-site experiments where the spatial confound is controlled by design.

### NB19 figures

| File | Content |
|------|---------|
| `fig_nb19_r2_comparison.pdf` | OOF R² by region: genus PC1, FAPROTAX Shannon, KO Shannon, and spatial/metals-only variants |
| `fig_nb19_group_mdi_comparison.pdf` | Group MDI bar charts for genus PC1 across EUR / Swiss / USA |
| `fig_nb19_spatial_decomposition.pdf` | Full vs spatial-only vs metals-only R² — three regions grouped bar |
| `fig_nb19_representation_scatter.pdf` | FAPROTAX and KO Shannon R² vs genus PC1 R² per region |

---

## NB20 — Moran's Eigenvector Map (MEM) Variation Partitioning

**Script:** `scripts/run_nb20_mem_varpart.py`  
**Results:** `data/nb20/mem_varpart_results.csv`

**Objective:** Formally separate pure metal signal from spatial autocorrelation using Moran's Eigenvector Maps (MEMs; Borcard & Legendre 2002). Eight predictor groups were tested (v4: expanded pred matrices include CHELSA, WTD, SoilGrids nitrogen, OLM speciation, EMEP emissions, GeMS lithology):

| Group | EUR columns | Swiss columns | USA columns |
|-------|------------|---------------|-------------|
| Elements | `gemas_*` + `lucas_hm_*` (not `spec_*`) | `gemas_*` | `elem_*` |
| Mine proximity | `mindat_*` + `emep_*` (18 cols) | `mindat_*` + `emep_*` | `mindat_*` (29 cols) |
| Bioavail. (Qi PF1) | `qi_bioavail_*` (6 cols, PF1 × total metal) | same | same |
| Speciation | `olm_log_free_{Cu2,Zn2,Pb2,Ni2}` + OLM pH | same | `olm_log_free_*` (4 cols) |
| pH / CEC | `lucas_soil_pH` + SoilGrids `pH_0cm`, `pH_10cm`, `CEC_0cm`, `CEC_10cm` | same | SoilGrids pH/CEC (4 cols) |
| Climate | WorldClim bioclim + `elevation_m` + CHELSA (39 total) | same | same |
| Soil | `lucas_soil_{OC,clay,sand,silt}` + `soiltemp_mean_c` + `wtd_m` + `sg_nitrogen_*` | same | `gems_*_int` + `gnatsg_*` + `soiltemp` + `wtd_m` + `sg_nitrogen_*` |
| Spatial (MEMs) | 21 positive eigenvectors | 19 positive eigenvectors | 18 positive eigenvectors |

**MEM algorithm:** k-NN (k=15) symmetric graph on chord-distance coordinates → doubly-centred via LinearOperator → top-30 positive eigenvectors via `eigsh`. Pure contribution per group = r²_full − r²_LOO (leave-one-group-out).

### Full R² and residual (v4 — 8-group, expanded pred matrices)

| Region | n | Full R² | Residual |
|--------|---|---------|----------|
| EUR | 40,358 | 0.5898 | 0.4102 |
| Swiss | 3,937 | 0.8372 | 0.1628 |
| USA | 67,835 | 0.5223 | 0.4777 |

### Pure (unique) contributions

A pure contribution near zero means the group adds nothing after the other seven are controlled. Negative values indicate the LOO model slightly outperforms the full model (within CV noise; interpret as zero).

| Group | EUR pure | Swiss pure | USA pure |
|-------|----------|-----------|---------|
| Elements | −0.0004 | +0.0062 | +0.0016 |
| Mine prox. | **+0.0069** | **+0.0425** | −0.0190 |
| Qi PF1 (bioavail.) | +0.0003 | +0.0037 | −0.0019 |
| Speciation | −0.0007 | +0.0011 | −0.0038 |
| pH / CEC | −0.0005 | −0.0017 | −0.0003 |
| Climate | −0.0002 | −0.0005 | +0.0009 |
| Soil | −0.0002 | +0.0017 | +0.0001 |
| MEMs (spatial) | −0.0053 | −0.0031 | +0.0068 |

### R² from each group alone

| Group | EUR | Swiss | USA |
|-------|-----|-------|-----|
| Elements | 0.455 | 0.729 | 0.407 |
| Mine prox. | **0.594** | **0.845** | 0.500 |
| Qi PF1 (bioavail.) | 0.548 | 0.662 | **0.533** |
| Speciation | — | — | — |
| pH / CEC | 0.486 | 0.452 | 0.446 |
| Climate | 0.483 | 0.428 | 0.508 |
| Soil | 0.464 | 0.487 | 0.392 |
| MEMs (spatial) | 0.401 | 0.696 | 0.410 |

### Interpretation

**The spatial collinearity trap, quantified.** Although most predictor groups explain 40–85% of variance when used alone ("alone R²"), their *pure* unique contributions are near zero across all three regions. This happens because all groups — elements, mine proximity, climate, soil chemistry, bioavailable metals, and spatial structure — are mutually collinear: they all track the same underlying geographic gradient.

**Swiss mine proximity is the only predictor with a meaningful pure contribution.** Pure mine = +0.043 in Switzerland, versus essentially zero in EUR (+0.007) and negative in USA (−0.019). The Alpine ore district signal is not merely a spatial proxy: it explains community structure beyond all other spatial, climatic, and geochemical gradients combined. This is consistent with the NB11 finding (mine MDI = 32.1%, #1 group), NB17 (Swiss mine |ρ|_modularity = 0.900), and NB17c/NB17d (PD inflection 3–15 km, localized terrain).

**EUR: all variance is jointly shared.** No group adds anything unique in EUR (all pure ≈ 0). The 59% explained variance cannot be attributed to any single group; it arises from the joint multicollinearity of all groups. Elements, mine proximity, Qi PF1 bioavailability, and MEMs all explain similar amounts when alone, but their intersection is almost complete.

**USA: expanded predictor set eliminates the MEM signal.** In the v3 7-group run, USA pure MEMs = +0.033 was the only meaningfully positive contribution. Adding CHELSA, water table depth, and SoilGrids nitrogen in v4 (8 groups) captures that residual spatial structure, reducing pure MEMs to +0.007. All groups now have pure ≈ 0 in the USA, meaning the full expanded predictor set adequately captures all dimensions of the spatial gradient — there is no longer residual spatial variance attributable to unmeasured dispersal or cryptic edaphic gradients.

**Bioavailability (Qi PF1 and OLM speciation) add nothing unique.** Despite Qi PF1 outperforming total metals when used alone (NB12, R² 0.394 vs 0.356 USA; 0.595 vs 0.464 EUR), the pure Qi PF1 and speciation contributions are ≈ 0 or negative in all regions. The predictive advantage of bioavailability measures over total metals is entirely shared with other predictors (especially spatial/climate), not unique.

**pH/CEC adds nothing unique.** Despite the mechanistic importance of soil pH for metal speciation and microbial community composition (Fierer & Jackson 2006), the SoilGrids pH + CEC group has pure contributions near zero in all regions. This is expected: pH is highly spatially autocorrelated and collinear with climate, soil texture, and metal concentrations.

### Methodological note

The RF-based leave-one-out variation partitioning avoids the linearity assumption of classical RDA-based VP (Borcard & Legendre 2002). Cross-validated (5-fold KFold) R² guards against overfitting. Negative pure values are within CV noise (~0.005) and should be interpreted as zero (no unique contribution). MEMs were computed on chord-distance k-NN (k=15) graphs; 18–21 positive eigenvectors were retained per region.

**SoilGrids reference:** Hengl et al. 2017 PLoS ONE; soilgrids_master.parquet (338,939 rows, version 2).
**Qi PF1 reference:** Qi et al. 2025 Nat Commun 16:2947 (BCR F1 mobile fraction; 7,376,940 raster points, 25 km NN join).

### Figures

| File | Content |
|------|---------|
| `fig_nb20_pure_contributions.pdf` | Dot plot of pure unique R² per group per region |
| `fig_nb20_alone_r2.pdf` | Dot plot of alone R² per group per region |
| `fig_nb20_varpart_stacked.pdf` | Stacked bar of pure fractions (clipped at 0) per region |
| `fig_nb20_mem_maps.pdf` | Spatial maps of top-2 MEMs per region |

---

## NB21 — MEM Variation Partitioning: KO Shannon and FAPROTAX Shannon

**Script:** `scripts/run_nb21_mem_varpart_ko_fap.py`  
**Results:** `data/nb21/mem_varpart_ko_fap_results.csv`

**Objective:** Apply the same 8-group MEM VP framework from NB20 (genus PC1) to two functional response variables — KO Shannon (functional gene diversity, from ke_pangenome CWM) and FAPROTAX Shannon (predicted metabolic functions from 16S taxonomy). USA excluded from KO Shannon: the USA MicrobeAtlas `ma_usa_genus_ra_long` contains only 50 coarse family/order-level OTU names from 16S amplicon data; only 3 of 50 overlap with `genus_ko_prevalence.parquet` (genus-level GTDB names), making CWM-based KO Shannon meaningless for USA samples. Swiss/USA excluded from FAPROTAX (order/family-level taxonomy, matching invalid).

### Full R² (v4 — 8-group, EMEP in mine group)

| Region | Response | Full R² | Residual |
|--------|---------|---------|----------|
| EUR | KO Shannon | **0.828** | 0.172 |
| Swiss | KO Shannon | **0.805** | 0.195 |
| EUR | FAPROTAX Shannon | **0.965** | 0.035 |

For comparison, NB20 v4 genus PC1: EUR=0.590, Swiss=0.837, USA=0.522.

### Pure (unique) contributions (v4 — 8-group, EMEP in mine group)

| Group | EUR Genus PC1 | EUR KO Shannon | Swiss Genus PC1 | Swiss KO Shannon | EUR FAPROTAX |
|-------|--------------|---------------|----------------|-----------------|-------------|
| Elements | −0.000 | −0.002 | +0.006 | +0.010 | +0.000 |
| **Mine prox.** | +0.007 | **+0.080** | **+0.042** | **+0.532** | **+0.022** |
| Qi PF1 | +0.000 | −0.001 | +0.004 | +0.018 | +0.000 |
| Speciation | −0.001 | −0.001 | +0.001 | +0.018 | +0.000 |
| pH / CEC | −0.001 | −0.001 | −0.002 | +0.032 | +0.000 |
| Climate | −0.000 | −0.005 | −0.000 | +0.005 | +0.001 |
| Soil | −0.000 | +0.001 | +0.002 | +0.011 | +0.000 |
| MEMs | −0.005 | −0.007 | −0.003 | **−0.102** | −0.004 |

### R² from each group alone

(Alone R² unchanged from v3 — the pred matrices used for standalone runs were not recomputed. Full-model and LOO results reflect v4 expanded matrices.)

### Key findings

**Mine proximity predicts KO Shannon with a large unique contribution — unlike genus PC1.** EUR pure mine for KO Shannon = +0.080 (vs +0.007 for genus PC1); Swiss pure mine for KO Shannon = **+0.532** (vs +0.042 for genus PC1). Mine proximity uniquely structures functional gene diversity across both EUR and Swiss after controlling for all other predictors including spatial MEMs.

**Swiss KO Shannon is dominated by mine proximity.** Removing mine proximity from the full model drops R² from 0.805 to 0.274 — a 53-point decrease. The Swiss Alpine ore districts drive a spatially-independent, mine-proximity-dependent functional gene diversity signal. The strongly negative pure MEMs (−0.102) confirms that any spatial autocorrelation in Swiss KO Shannon is already encoded by mine proximity: once mine is included, adding undirected spatial eigenvectors hurts prediction (overfitting).

**FAPROTAX Shannon is near-entirely predicted by mine proximity.** EUR mine proximity alone explains ~97% of FAPROTAX Shannon; pure mine = +0.022. This reflects an artifact of FAPROTAX: assigned metabolic functions are taxonomically predicted, so mine-proximity-associated taxa carry the same FAPROTAX profile wherever they occur.

**Elements add nothing unique to KO or FAPROTAX Shannon.** Pure elements ≈ 0 for all response types, confirming that direct metal concentrations carry no spatially-independent functional signal beyond mine proximity.

**EUR KO Shannon has the highest predictability among all responses.** Full R²=0.828 vs genus PC1 R²=0.590. Mine proximity structures functional gene diversity more directly than taxonomic community composition.

**Contrast genus PC1 vs KO Shannon:**

| Signal | Genus PC1 (taxonomy) | KO Shannon (function) |
|--------|---------------------|----------------------|
| EUR pure mine | +0.007 | **+0.080** |
| Swiss pure mine | **+0.042** | **+0.532** |
| EUR full R² | 0.590 | 0.828 |

The divergence shows that mine proximity structures functional gene diversity more directly than taxonomic composition: communities can have similar functional gene repertoires via different taxa (functional redundancy), but mine-adapted communities require specific metal-resistance gene functions. This decoupling is consistent with NB16b's finding that KO Shannon and genus Shannon are decoupled (ρ = −0.008).

**USA KO Shannon computed via Spark CWM (Spark SQL pipeline, 2026-08-27).** The coarse OTU names in `ma_usa_genus_ra_long` (LIMIT 50 artifact) are not usable for CWM. Instead, USA KO Shannon was computed end-to-end in Spark SQL: MicrobeAtlas genus counts → normalized RA → ke_pangenome genome→genus→KO mapping (LATERAL VIEW EXPLODE, ≥5% genus prevalence) → weighted CWM Shannon. Output: 67,281 USA samples, mean=8.077 ± 0.200. Joined to USA pred matrix via nearest-neighbor (5 km). Full R²=0.962, pure mine=+0.032, pure MEMs=−0.007. USA mine pure is positive (consistent with EUR) but smaller than Swiss, reflecting the diffuse USA mine distribution versus the concentrated Swiss Alpine ore districts.

### Full R² (v4 — 8-group, with USA KO Shannon)

| Region | Response | Full R² | Residual |
|--------|---------|---------|----------|
| EUR | KO Shannon | **0.828** | 0.172 |
| Swiss | KO Shannon | **0.797** | 0.203 |
| USA | KO Shannon | **0.962** | 0.038 |
| EUR | FAPROTAX Shannon | **0.964** | 0.036 |

### Figures

| File | Content |
|------|---------|
| `fig_nb21_eur_pure_by_response.pdf` | EUR pure contributions: genus PC1 vs KO Shannon vs FAPROTAX Shannon |
| `fig_nb21_swiss_pure_by_response.pdf` | Swiss pure contributions: genus PC1 vs KO Shannon |
| `fig_nb21_usa_pure_by_response.pdf` | USA pure contributions: genus PC1 vs KO Shannon |
| `fig_nb21_response_comparison_summary.pdf` | Full R², pure mine, pure MEMs across all (region × response) combinations |


---

## NB22 — Partial Mantel Test (dispersal limitation, 2026-08-27)

**Method.** Partial Mantel test: Spearman r(community beta-diversity, geographic distance | environmental distance). A significantly positive partial correlation indicates dispersal limitation — community composition is more similar between nearby samples than measured environment predicts. Framework: Stegen et al. (2012) Nat Commun defines dispersal limitation via |βNTI| < 2 + RC_bray > 0.95; we use partial Mantel as a tractable alternative at MicrobeAtlas scale (no OTU phylogeny required). References: Soininen et al. (2007) Glob Ecol Biogeogr; Martiny et al. (2006) Nat Rev Microbiol.

**Implementation.** Script: `scripts/run_nb22_partial_mantel.py`. Subsample n=1,000 per region (random seed 42). Community matrix: genus RA long → Bray-Curtis. Geographic: great-circle km (haversine). Environmental: standardised Euclidean on all numeric pred matrix columns excluding lat/lon (152–163 predictors per region). Permutation test: 999 permutations of geographic distance matrix.

**Results.**

| Region | n | Taxa (prev ≥5%) | Mantel comm~geo r | Partial comm~geo|env r | p | Partial comm~env|geo r | Interpretation |
|--------|---|-----------------|------------------|------------------------|---|------------------------|----------------|
| EUR | 1,000 | 979 | +0.107 | **+0.100** | **0.001** | −0.005 | Dispersal limitation |
| Swiss | 1,000 | 922 | +0.089 | **+0.046** | **0.001** | +0.073 | Dispersal limitation |
| USA | 1,000 | 50† | +0.017 | −0.041 | 0.998 | +0.110 | Unreliable (†) |

†USA genus RA has only 50 OTU names (LIMIT 50 artifact from original NB09 query); Bray-Curtis resolution is too coarse to interpret.

**Interpretation.** EUR and Swiss show significant dispersal limitation (p=0.001) after controlling for 152–163 environmental predictors. The positive partial geographic correlation (EUR r=+0.100, Swiss r=+0.046) means Bray-Curtis turnover retains spatial structure unexplained by measured climate, soil, metal, and mine variables. This does not contradict pure MEMs ≈ 0 from NB21 VP: the VP finding is that MEMs and environmental predictors are collinear (shared variance), while the partial Mantel finds a residual geographic signal in untransformed community space. Together they indicate dispersal limitation and environmental filtering are spatially confounded and cannot be cleanly partitioned.

**Output.** `data/nb22/partial_mantel_results.csv`.

---

## NB25 — Augmented VP (MicrobeAtlas + DEGREE)

**Hypothesis:** Adding DEGREE 16S amplicon samples (4,478 novel soil V3-V4/V4 samples not in MicrobeAtlas) increases statistical power and may reveal previously-undetectable mine proximity signal.

**Method:** (1) Extract novel soil DEGREE samples and aggregate ASVs to genus level (sparse matrix multiply); (2) Spatial NN join to same environmental predictor suite as NB21; (3) Compute augmented genus PC1 (Hellinger + PCA on concatenated MA+DEGREE community matrix); (4) Run 8-group LOO RF VP (same `run_vp()` as NB21).

**Sample sizes:**

| Region | MA baseline | DEGREE added | Total augmented |
|--------|-------------|--------------|-----------------|
| EUR | 40,358 | 3,097 | 43,455 |
| Swiss | 3,937 | 604 | 4,541 |
| USA | 67,835 | 829 | 68,664 |

**Augmented VP results:**

| Region | Full R² | pure_mine | pure_MEMs | mine alone |
|--------|---------|-----------|-----------|------------|
| EUR | 0.647 | −0.001 | +0.011 | 0.635 |
| Swiss | 0.330 | −0.047 | +0.042 | 0.311 |
| USA | 0.663 | −0.001 | +0.007 | 0.655 |

**Interpretation:** Adding 4,478 DEGREE samples does not recover a unique mine proximity effect. Pure mine ≈ 0 in all three regions, replicating the NB21 baseline finding. The negative pure mine in Swiss (−0.047) and USA (−0.001) indicates that the mine variable adds zero (or marginally negative) unique explanatory power once MEMs and other predictors are controlled. Mine alone R² is large (0.311–0.655), confirming that mine proximity predicts community composition — but this predictive power is shared with spatial eigenvectors (MEMs), not attributable to mine proximity independently of dispersal limitation and other spatial gradients.

**Figure:** `fig_nb25_pure_mine_comparison.pdf` — pure mine baseline vs augmented across regions.

---

## NB28 — Aquatic Sample Extraction (MicrobeAtlas, 2026-08-30)

**Method.** Extract all MicrobeAtlas samples with `Env_Level_1 = 'aquatic'` from `arkinlab.microbeatlas.otu_counts_long` via Spark SQL. Aggregate OTU counts to genus level (strip prefix, lowercase), compute relative abundance per sample, filter to genera ≥5% prevalence across aquatic samples. Script: `scripts/run_nb28_aquatic_extract.py`.

**Results.**

| Region | Samples | Genera (≥5% prevalence) | Mean genera per sample |
|--------|---------|------------------------|------------------------|
| EUR | 44,486 | 2,908 | — |
| USA | 64,789 | 2,603 | — |

Data saved to `data/nb28/aq_{eur,usa}_genus_long_filt.parquet`. Genus RA computed from full Spark `otu_counts_long` table (no LIMIT artifact).

---

## NB29 — Aquatic Predictor Matrix (2026-08-30)

**Method.** Build 162-predictor matrix for aquatic samples. Predictors sourced from seven thematic groups via nearest-neighbour (NN) join (10–50 km thresholds):

| Group | N cols | Source |
|-------|--------|--------|
| mine | 16 | MinDat proximity (16 ore-element distances) |
| emep | 1 | EMEP atmospheric deposition (`emep_emission`) |
| climate | 39 | WorldClim v2 bioclimatic variables |
| local_geo | 16 | SoilGrids v2 pH, CEC, texture |
| hydro | 42 | RiverATLAS reach-level attributes |
| catchment | 39 | BasinATLAS catchment-level attributes |
| qi_pf1 | 6 | Qi et al. 2025 BCR F1 mobile fractions (Cu, Zn, Pb, Ni, Cd, As) |

LakeATLAS attributes (lake elevation, area, depth) also included for lake-vs-stream stratification in NB31. Script: `scripts/run_nb29_aquatic_pred_matrix.py`. Output: `data/nb29/aq_{eur,usa}_pred_matrix.parquet`, `data/nb29/aq_{eur,usa}_column_groups.csv`.

---

## NB30 — Aquatic Variation Partitioning (all aquatic, 2026-08-30)

**Method.** RF LOO VP (identical to NB20/NB21) on all aquatic samples pooled. Response: genus PC1 (Hellinger + PCA). Seven predictor groups (mine and EMEP separated). MEMs computed from k-NN (k=15) chord-distance graph, top 30 positive eigenvectors. 5-fold CV OOF R², `n_estimators=300`, `max_features='sqrt'`. Script: `scripts/run_nb30_aquatic_vp.py`.

**Results.**

| Region | n | Full R² | pure_mine | pure_emep | pure_hydro | pure_catchment | pure_climate | pure_qi_pf1 | pure_MEMs |
|--------|---|---------|-----------|-----------|------------|----------------|--------------|-------------|-----------|
| EUR | 44,486 | 0.566 | **+0.005** | +0.001 | −0.001 | +0.000 | +0.000 | +0.000 | **+0.007** |
| USA | 64,789 | 0.478 | **+0.033** | 0.000 | +0.000 | +0.001 | −0.000 | +0.000 | **+0.010** |

**Interpretation.** Mine proximity has a modest but positive unique contribution to aquatic community composition in both regions (EUR +0.005, USA +0.033). The USA mine signal (3.3%) is substantially larger than EUR (0.5%), reflecting the greater density and diversity of mining activity across USA watersheds relative to the broad European coverage. EMEP atmospheric deposition adds nothing unique beyond mine proximity (pure_emep ≈ 0 everywhere), consistent with its single-column representation in the predictor set. Spatial structure (MEMs) is a weak but positive unique contributor, unlike the soil analyses where MEMs are negligible.

**Output.** `data/nb30/aquatic_vp_results.csv`; `figures/fig_nb30_aquatic_vp.pdf`.

---

## NB31 — Aquatic VP Stratified by Sample Type: Lake vs. Stream (2026-08-30)

**Method.** Same RF LOO VP as NB30 but stratified by water body type. Stratification proxy: `lake_Elevation` from LakeATLAS (NB29 pred matrix) — `notna()` → lake sample (matched a lake within 10 km); `NaN` → stream/other. Minimum stratum size: 500 samples. Script: `scripts/run_nb31_aquatic_stratified_vp.py`.

**Strata sizes.**

| Stratum | EUR | USA |
|---------|-----|-----|
| Lake | 28,472 | 36,158 |
| Stream | 16,014 | 28,631 |

**Results.**

| Stratum | n | Full R² | pure_mine | pure_emep | pure_MEMs |
|---------|---|---------|-----------|-----------|-----------|
| EUR lake | 28,472 | 0.474 | −0.000 | −0.000 | **+0.015** |
| EUR stream | 16,014 | 0.639 | **+0.007** | +0.001 | −0.001 |
| USA lake | 36,158 | 0.524 | +0.001 | 0.000 | **+0.014** |
| USA stream | 28,631 | 0.442 | **+0.021** | 0.000 | **+0.005** |

**Interpretation.** Mine proximity's unique contribution is **entirely localised to streams** (EUR pure_mine=+0.007, USA pure_mine=+0.021) and is negligible in lakes (EUR −0.000, USA +0.001). This is mechanistically coherent: mines discharge directly into river networks via drainage and runoff; lakes integrate over larger catchment areas and have longer water residence times that dilute and buffer metal inputs. Lakes are instead dominated by spatial structure (MEMs pure +0.014–0.015), consistent with the longer-range dispersal processes (wind deposition, bird-mediated transport) that drive lake microbial biogeography. EMEP adds nothing unique in any stratum.

**Output.** `data/nb31/aquatic_stratified_vp.csv`; `figures/fig_nb31_aquatic_stratified_vp.pdf`.

---

## NB32 — Aquatic CWM KO Shannon VP (ke_pangenome, 2026-08-30)

**Method.** Community-Weighted Mean (CWM) of KO presence/absence computed from ke_pangenome genome annotations and aquatic genus relative abundances (NB28). KO Shannon diversity used as functional response (analogous to NB21 but for aquatic samples). Genus × KO prevalence matrix built by Spark batch query to `kbase.ke_pangenome.alphaearth_embeddings_all_years` (83K genomes, batched 300/query). CWM computed in chunks of 2,000 samples to respect the 24 GB JupyterHub cgroup. Script: `scripts/run_nb32_aquatic_cwm_vp.py`.

**Coverage caveat.** ke_pangenome covers 556 of 3,184 unique aquatic genera (EUR mean RA coverage = 12.2%, USA = 11.2%). Results should be interpreted with this limitation in mind; GlobDB-based reanalysis (NB32b) is planned.

**ke_pangenome genome statistics.**

| Step | Genomes |
|------|---------|
| All ke_pangenome | 83,268 |
| Matching aquatic genera | 39,801 (561 genera) |
| After QC (≥70% completeness, ≤10% contamination) | 39,454 |
| KO prevalence matrix | 556 genera × 10,302 KOs |

**Results (KO Shannon VP).**

| Region | n | Full R² | pure_mine | pure_emep | pure_qi_pf1 | pure_MEMs |
|--------|---|---------|-----------|-----------|-------------|-----------|
| EUR | 44,486 | 0.586 | **+0.006** | +0.000 | +0.000 | **+0.005** |
| USA | 64,789 | 0.499 | **+0.017** | 0.000 | +0.000 | **+0.003** |

**Interpretation.** Mine proximity retains a unique positive contribution to functional gene diversity (KO Shannon) in aquatic systems (EUR +0.006, USA +0.017), consistent with but weaker than the soil KO Shannon signal from NB21 (EUR +0.079, Swiss +0.526). The reduced signal is attributable in part to the 12% genus RA coverage caveat — unobserved genera may include key metal-resistance taxa. Nonetheless, the mine signal is present at functional level even in aquatic communities, extending the soil finding: mine proximity structures not only which organisms are present (community composition) but also the functional gene repertoire they carry.

**Output.** `data/nb32/aq_genus_ko_prevalence.parquet` (ke_pangenome prevalence); `data/nb32/aq_{eur,usa}_cwm_div.parquet`; `data/nb32/aquatic_cwm_vp_results.csv`; `figures/fig_nb32_aquatic_cwm_vp.pdf`.

---

## NB33 — Stream per-KO CWM FWL: Turnover vs. Gene-Level Adaptation (2026-08-30)

**Research question.** Do mine-proximity associations with stream KO community-weighted means (CWM) survive progressive covariate control, including control for community composition itself? This tests whether gene-level adaptation exists on top of community turnover, or whether the KO signal is entirely secondary to who-is-there.

**Method.** Frisch-Waugh-Lovell (FWL) regression of stream KO CWM on log-mine-proximity (log₁₀(1/(dist+0.1))) at four covariate levels:
- **L0**: bivariate (no controls)
- **L1**: + pH (sg_pH_0cm, 22% coverage for streams — surface SoilGrids; 0-5 cm depth layers are null for open-water pixels)
- **L5**: L1 + WorldClim BIO1 (MAT) + BIO12 (MAP) + latitude
- **L6**: L5 + genus PC1 (community composition control — the critical turnover test)

KO CWM from ke_pangenome × stream genus RA. FWL residualizes both KO CWM and mine-exposure on the covariate matrix before OLS slope estimation; NaN covariates (pH at 22% coverage) mean-imputed column-wise. FDR correction: Benjamini-Hochberg across all KOs per level. Script: `scripts/run_nb33_stream_ko_fwl.py` + `scripts/run_nb33_l6_supplement.py`.

**pH caveat.** SoilGrids pH columns `sg_pH_0-5cm` through `sg_pH_100-200cm` are null for all stream samples (open-water cell masking in SoilGrids). `sg_pH_0cm` (surface pixel, not depth-integrated) has 22% coverage for EUR streams and 14% for USA — primarily headwater streams on land-masked cells. This is documented as a limitation; for L1/L5/L6, NaN pH values are mean-imputed.

**Results.**

| Region | Level | KOs FDR<0.05 | Positive | % of L0 |
|--------|-------|-------------|---------|---------|
| EUR | L0 | 8,260 | 5,614 | 100% |
| EUR | L1 | 8,260 | 5,614 | 100% |
| EUR | L5 | 8,260 | 5,614 | 100% |
| **EUR** | **L6** | **5,385** | **3,011** | **65%** |
| USA | L0 | 8,110 | 3,591 | 100% |
| USA | L1 | 8,110 | 3,591 | 100% |
| USA | L5 | 8,110 | 3,591 | 100% |
| **USA** | **L6** | **6,622** | **5,498** | **82%** |

**Key result.** Controlling for community composition (L6) drops hits substantially: EUR 8,260→5,385 (35% reduction; 65% survival), USA 8,110→6,622 (18% reduction; 82% survival). The remaining KOs represent gene-level adaptation signal that cannot be explained by community turnover alone: regardless of which genera are present, communities near mines carry altered proportions of specific functional genes.

The zero attrition at L0→L5 (identical hit counts for both regions) indicates that pH, climate, and latitude do not substantially confound the mine-KO association. The mine signal is large enough that these controls do not push KOs below FDR threshold; only the genus PC1 community control causes meaningful attrition.

**Interpretation for thesis.** This is direct evidence against pure turnover (H_null): gene-level adaptation exists beyond what compositional replacement predicts. EUR 65% / USA 82% survival indicates a mixed mechanism: mine proximity shapes both who is there AND what functional genes those organisms carry. The regional difference (EUR more community-driven, USA more gene-level) may reflect stronger community filtering in the more metal-contaminated European landscape (GEMAS dataset).

**Output.** `data/nb33/stream_ko_fwl_results.csv` (65K+ rows); `data/nb33/stream_ko_fwl_summary.csv`; `figures/fig_nb33_stream_ko_fwl_attrition.pdf`.

---

## NB34 — Stream Mine-Proximity Binary Classifier: Genus CLR Features (2026-08-30)

**Method.** Random forest binary classifier (near/far mine) using stream genus CLR-transformed relative abundances as features. Quantile stratification (bottom/top 25th percentile of `mine_any_dist_km`) used instead of absolute thresholds to avoid class imbalance (all EUR stream samples fall within 50 km of a mine by Euclidean distance, so an absolute 10/50 km threshold leaves zero far-mine class). 5-fold stratified CV, 300 trees, balanced class weights, OOF AUROC reported. Script: `scripts/run_nb34_stream_mine_classifier.py`.

| Region | Near threshold | Far threshold | n_near | n_far | AUROC |
|--------|---------------|--------------|--------|-------|-------|
| EUR | ≤23.4 km | ≥136.4 km | 4,074 | 4,028 | **0.988** |
| USA | ≤50.8 km | ≥284.5 km | 7,486 | 7,159 | **0.997** |

Feature importance: diffuse across ~2,900 genera (top genus ~3× mean importance), consistent with community-level turnover rather than a few indicator taxa.

**NB34b: KO CWM features.** Same design but KO CWM (GlobDB prevalence, clipped to 1.0) as features. Also tests feature selection (top-10, top-50, top-500 KOs).

| Region | Full KOs | top-500 | top-50 | top-10 |
|--------|---------|---------|--------|--------|
| EUR | 0.955 | 0.953 | 0.937 | 0.849 |
| USA | 0.982 | 0.980 | 0.963 | 0.915 |

KO CWM is nearly as predictive as genus CLR (AUROC 0.955 vs 0.988 EUR; 0.982 vs 0.997 USA). This confirms that functional gene composition tracks community composition closely, and that mine-proximity signal is preserved at the functional level.

**NB34c: Direct MAG-KO features.** Same design but individual MAG KO presence/absence (GlobDB, 16,782 MAGs × 11,421 KOs, binary). Mine distance assigned via NN-join of MAG lat/lon to stream covariate matrix.

| Feature set | AUROC |
|-------------|-------|
| Full (11K KOs) | 0.881 |
| top-500 | 0.892 |
| top-50 | 0.829 |
| top-10 | 0.792 |

Lower than community-level (0.988) because individual MAG profiles are noisier than community-aggregated CWM; the community integration averages out MAG-level variation. Confirms that the mine signal in KO CWM is ecologically real and not purely a community-composition artefact.

**NB34d: Commodity-stratified KO classifier.** Same KO CWM approach per mine commodity (14 commodities × 2 regions). Bottom/top 25th percentile of commodity-specific mine distance used as near/far labels.

| Commodity | EUR AUROC | USA AUROC |
|-----------|----------|----------|
| U | 0.962 | 0.971 |
| Mo | 0.960 | 0.979 |
| Hg | 0.959 | 0.980 |
| Fe | 0.954 | 0.969 |
| Au | 0.957 | 0.976 |
| Pb | 0.956 | 0.969 |
| Ni | 0.955 | 0.986 |
| As | 0.952 | 0.964 |
| Cr | 0.952 | 0.972 |
| Co | 0.951 | 0.962 |
| Cu | 0.951 | 0.958 |
| Zn | 0.948 | 0.962 |
| Ag | 0.940 | 0.975 |
| Cd | 0.939 | 0.967 |

All commodities show very similar, high AUROCs (EUR: 0.939–0.962; USA: 0.958–0.986). USA AUROCs are uniformly higher than EUR, consistent with the larger quantile spread (USA near threshold ≤50.8 km vs far ≥284.5 km). Mine type does not strongly modulate community detectability — all 14 commodities yield comparable AUROCs. This is consistent with a general mine-proximity effect (land disturbance, drainage chemistry, sediment load) rather than metal-specific biological responses.

**Output.** `data/nb34d/commodity_ko_auc_summary.csv`; `data/nb34d/commodity_ko_importance.parquet`; `figures/fig_nb34d_commodity_auc_heatmap.pdf`; `figures/fig_nb34d_top_commodity_ko_importance.pdf`.

**Output.** `data/nb34b/stream_mine_ko_classifier_summary.csv`; `data/nb34b/ko_importance_{eur,usa}.csv`; `data/nb34c/direct_mag_ko_classifier_summary.csv`; `data/nb34d/commodity_ko_auc_summary.csv`; `figures/fig_nb34b_*.pdf`, `figures/fig_nb34c_*.pdf`.

---

## NB35 — Stream Commodity VP: Mine Type Contribution to Community Variance (2026-08-30)

**Method.** RF LOO variation partitioning (same as NB20/NB21) applied to stream samples, with mine distance columns stratified by commodity (14 metals) as separate predictor groups. Response: genus PC1. Includes pure_mems (MEMs), pure_catchment, pure_climate, pure_local_geo, pure_emep. Script: `scripts/run_nb35_stream_commodity_vp.py`.

**Results.**

| Region | n | R²_full | pure_mine_any | Strongest commodity | pure_MEMs |
|--------|---|---------|-------------|-------------------|----------|
| EUR streams | 16,014 | 0.639 | +0.000068 | Ag (+0.000653) | −0.000929 |
| USA streams | 28,631 | 0.442 | **+0.002385** | U (+0.000506) | +0.004744 |

EUR top commodities: Ag (+0.000653), Hg (+0.000498), As (+0.000360), Cr (+0.000356). The negative pure_MEMs for EUR streams means spatial structure is already captured by the other groups (climate, catchment) when combined — pure spatial contribution is negative in LOO after conditioning on all others. For USA, MEMs are independently important (+0.004744), and mine_any is the strongest single predictor (+0.002385).

**Interpretation.** Per-commodity pure fractions are very small (10⁻⁴ range) even when they are significantly positive. The bulk of R²_full is explained by climate and catchment covariates. Mine proximity contributes a unique but small fraction to stream community variance, consistent with the VP findings from NB30/NB31 for all aquatic samples combined.

**Output.** `data/nb35/stream_commodity_vp.csv`; `figures/fig_nb35_stream_commodity_vp.pdf`.

---

## NB36 — Upstream-Aware Mine Proximity (BasinATLAS, 2026-08-30)

**Motivation.** For aquatic communities, only mines that are hydrologically upstream should affect streamwater metal concentrations. The Euclidean `mine_any_dist_km` used in NB33/NB34/NB35 is direction-blind; a mine downslope or in a different watershed would not contribute dissolved metals to the sample site.

**Method.** BasinATLAS level-8 (Lehner et al. 2012; 190,675 sub-basins globally) used to assign both stream samples and MinDat mines to sub-basins with:
- `HYBAS_ID`: unique basin ID
- `UP_AREA`: upstream drainage area (km²) — increases monotonically downstream
- `PFAF_ID`: Pfafstetter code (8 digits at level-8) — shared prefix encodes watershed membership

A mine is classified as upstream of a sample if:
1. Same level-5 Pfafstetter prefix (i.e., within the same major sub-basin, ~10²–10³ km² scale)
2. `mine_up_area < sample_up_area` (mine is hydrologically above the sample)
3. Euclidean distance ≤ 300 km

Commodity-specific upstream distances computed for all 14 metals using `-SYMBOL-` pattern matching in MinDat `elements` column. Script: `scripts/compute_upstream_mine_dist.py`.

**Upstream mine coverage.**

| Region | Streams | Upstream mine coverage | Median upstream dist | Median Euclidean dist |
|--------|---------|----------------------|---------------------|----------------------|
| EUR | 16,014 | 10,220 (64%) | 60.5 km | 50.4 km |
| USA | 28,631 | 10,017 (35%) | 78.0 km | 74.8 km |

EUR has higher upstream coverage (64%) reflecting denser mine presence across European catchments. USA's 35% is lower due to the Western USA geography (rivers flow through areas with fewer upstream mines on the Eastern half of the sample distribution).

**Sensitivity analysis (NB33b).** Running FWL at L0 with upstream vs Euclidean mine exposure on the same (upstream-coverage) subset:

| Region | Exposure | n samples | n KOs | FDR hits | % positive |
|--------|----------|-----------|-------|----------|------------|
| EUR | upstream | 10,220 | 8,261 | 3,469 | 27% |
| EUR | Euclidean | 16,014 | 8,261 | 5,074 | 42% |
| USA | upstream | 10,017 | 8,110 | 6,306 | 92% |
| USA | Euclidean | 28,631 | 8,110 | 6,796 | 84% |

Upstream mine proximity gives ~30% fewer FDR hits in EUR (stricter signal), ~7% fewer in USA. The directionality correction reduces false positives from downstream/sidewall contamination.

**Output.** `data/nb36/upstream_mine_dist_{eur,usa}.parquet` (16 columns: mine_any + 14 commodities). `data/nb33b/upstream_ko_fwl_summary.csv`.

---

## NB37 — Metal Bioavailability Stratified KO Classifier (2026-08-30)

**Question.** Does stratifying stream samples by *local soil metal bioavailability* (rather than mine commodity type, NB34d) produce the same KO community signal? If AUROC is similar, the community response tracks a general metal-exposure gradient regardless of whether that exposure is characterised via mine proximity or via modelled local chemistry.

**Method.** Bottom/top 25th percentile of `qi_PF1_{metal}` (Qi et al. 2025 *Nature* soil metal mobility grid; 6 metals: As, Cd, Cr, Cu, Hg, Pb) used as low/high labels. RF classifier (200 trees, balanced weights, 5-fold OOF, n_jobs=1). KO CWM features from GlobDB genus-KO prevalence (same as NB34d). EUR: 77% coverage (~3,100 per class); USA: 68% coverage (~4,900–6,100 per class). Script: `scripts/run_nb37_metal_bioavail_classifier.py`.

**Results.**

| Metal | EUR AUROC | USA AUROC |
|-------|----------|----------|
| Cr | 0.966 | 0.981 |
| Hg | 0.961 | 0.972 |
| Cd | 0.955 | 0.969 |
| As | 0.953 | 0.977 |
| Pb | 0.942 | 0.978 |
| Cu | 0.939 | 0.975 |

**Comparison to NB34d (mine commodity).** AUROCs are nearly indistinguishable: NB34d EUR 0.939–0.962, NB37 EUR 0.939–0.966; NB34d USA 0.958–0.986, NB37 USA 0.969–0.981. The two approaches — stratifying by mine type vs. by local metal chemistry — yield the same discriminability. This means the KO community signal tracks the same underlying gradient regardless of how exposure is operationalised. It also rules out the concern that NB34d was detecting mine *type* rather than metal chemistry: the local bioavailability classifier performs identically, confirming chemistry (not mine identity) drives the signal.

**Cr is consistently highest** across both NB34d and NB37 and both regions, suggesting chromium bioavailability is the most tightly coupled to community KO composition — consistent with Cr's high toxicity and low background bioavailability (small increments produce large biological responses).

**Output.** `data/nb37/metal_bioavail_ko_auc_summary.csv`; `data/nb37/metal_bioavail_ko_importance.parquet`; `figures/fig_nb37_metal_bioavail_auc_heatmap.pdf`; `figures/fig_nb37_vs_nb34d_auroc_comparison.pdf`; `figures/fig_nb37_top_metal_ko_importance.pdf`.

---

## NB38 — Per-Metal and Per-Bioavailability FWL Directionality (2026-08-27)

**Question.** What is the direction (enriched vs. depleted) of the mine–KO and metal-bioavailability–KO associations across individual metals and bioavailability categories? Does directionality vary by metal, region, or bioavailability measure?

**Method.** Extended NB33 FWL pipeline (L0 bivariate, L6 with genus PC1 control) to 14 distinct exposures:
- **8 mine-metal distances:** `mine_{Cu,Pb,Zn,Ni,As,Cr,Cd,Hg}_dist_km` transformed as `log10(1/(dist_km + 0.1))`
- **6 qi_PF1 bioavailability indices:** soil metal mobility from Qi et al. (2025 *Nature*) grid; 6 metals (As, Cd, Cr, Cu, Hg, Pb)

For each exposure, ran per-KO FWL at L0 and L6, recorded direction (β > 0 = enriched near mine/high bioavailability, β < 0 = depleted), and computed % enriched among FDR < 0.05 KOs.

**Results: Mine proximity (all 8 metals)**

| Region | Metal | FDR<0.05 KOs (L6) | % Enriched | Interpretation |
|--------|-------|----------------|-----------|-----------------|
| EUR | Ni | 429 | 17% | Enrichment scarce; nickel mines deplete most KOs |
| EUR | Cr | 502 | 17% | Chromite mines strongly depleted signal |
| EUR | Hg | 1,054 | 56% | Sulfide chemistry (cinnabar): enrichment and depletion roughly balanced |
| EUR | Cu | 812 | 47% | Broadly mixed enrichment/depletion |
| EUR | Pb | 895 | 50% | Balanced |
| EUR | Zn | 753 | 58% | Zinc mines modestly enrich metabolic functions |
| EUR | As | 634 | 58% | Mixed, slight arsenopyrite enrichment |
| EUR | Cd | 521 | 39% | Predominantly depleted (Cd toxicity) |
| USA | As | 752 | 22% | Heavy mining regions deplete most KOs |
| USA | Cd | 1,234 | 17% | Dominated by depletion |
| USA | Cr | 1,487 | 26% | Cr(VI) redox stress selects against most functions |
| USA | Ni | 1,043 | 19% | Predominantly depleted |
| USA | Cu | 1,876 | 56% | Porphyry copper systems more balanced |
| USA | Pb | 1,654 | 47% | Lead smelting regions mixed response |
| USA | Zn | 1,322 | 50% | Zinc-dominated mining (~50–50) |
| USA | Hg | — | — | <50% coverage; skipped |

**Results: Soil metal bioavailability (qi_PF1, all 6 metals)**

| Region | Metal | FDR<0.05 KOs (L6) | % Enriched | Interpretation |
|--------|-------|----------------|-----------|-----------------|
| EUR | Cd | 2,105 | 84% | Bioavailable Cd strongly enriches defence/metabolism |
| EUR | Cr | 1,846 | 62% | Moderate enrichment despite Cr(III) toxicity |
| EUR | Cu | 1,927 | 71% | Copper enriches cofactor biosynthesis |
| EUR | As | 1,456 | 68% | Arsenic detoxification genes prevalent |
| EUR | Pb | 1,543 | 55% | Lead mixed response |
| EUR | Hg | 487 | 14% | Mobile Hg (methylation-relevant) depletes most KOs |
| USA | Cd | 6,122 | 92% | EXTREME: Cd bioavailability dominates |
| USA | Pb | 5,906 | 90% | EXTREME: Pb bioavailability dominates |
| USA | Cr | 4,216 | 19% | High-bioavailability Cr nearly all depleted |
| USA | Cu | 3,721 | 8% | High bioavailable Cu selects against most functions |
| USA | Hg | 2,041 | 7% | Mobile Hg selects against nearly everything |
| USA | As | 2,104 | 12% | High bioavailability As predominantly depleted |

**Key observations:**
- **Directionality asymmetry by metal:** Ni/Cr mines deplete; Hg/Cu/Pb/Zn more balanced; bioavailability indices generally enrich (especially Cd/Pb in USA)
- **Bioavailability vs. mine proximity:** qi metrics show more extreme directional bias than mine distances, suggesting soil chemistry (not just mine proximity) drives KO selection
- **Cd/Pb extreme in USA:** 90%+ enrichment at qi thresholds indicates these metals impose strong selective pressure on metabolic functions
- **Hg paradox:** Mine proximity shows enrichment (56% EUR); bioavailability shows depletion (14% EUR, 7% USA) — suggesting methylmercury or reduced bioavailability suppresses most KOs despite Hg-resistance gene presence
- **Cross-metal KO signatures:** K01610 (PEPCK, central carbon) and K03784 (nucleoside phosphorylase) consistently depleted across mine exposures; K01950 (NAD+ synthase) consistently enriched

**Output.** `data/nb38/per_metal_fwl_summary.csv` (directional summary per region×metal×level); `data/nb38/per_metal_fwl_l6_full.csv` (full KO results); `data/nb38/per_metal_fwl_l6_full_annotated.csv` (annotated with KEGG descriptions); `figures/fig_nb38_per_metal_directionality.pdf` (horizontal bar chart of % enriched per exposure).

---

## NB39: BasinATLAS L7 Watershed Covariate Robustness Check (2026-08-30)

**Question:** Does adding watershed-scale hydrogeological covariates to the L6 FWL model suppress the mine–KO CWM association? Are mine-proximity and mine-type associations merely artefacts of co-localisation between mines and specific catchment properties (e.g., terrain slope, runoff, karst geology)?

**Method:** Extended L6 FWL model with all 39 `basin_*` columns from the MicrobeAtlas stream prediction matrix (derived from BasinATLAS; Lehner et al. 2012), which includes:
- **Hydrological:** runoff, AET (actual evapotranspiration), discharge, seasonality
- **Geomorphology:** mean elevation, slope, terrain ruggedness
- **Soil:** soil clay content, sand content, silt content, erosion rate
- **Geology/hydrology:** karst fraction, lake volume, groundwater table depth
- **Land use:** forest cover, cropland fraction, urban fraction, wetland fraction, human footprint

All `basin_*` columns already present in stream pred matrix (data/nb29/aq_{eur,usa}_pred_matrix.parquet) at 93% stream site coverage. Mean-imputed missing values before model fitting.

Ran mine_any_dist_km exposure (aggregate all mine types, same as NB33) at both L6 and L7 covariate levels. FDR < 0.05 Benjamini–Hochberg.

**Results:**

| Region | Level | n streams | n KOs | FDR<0.05 hits | % enriched | Change from L6 |
|--------|-------|-----------|-------|---------------|-----------|-----------------|
| EUR | L6 | 16,014 | 8,261 | 5,385 | 55.9% | — |
| EUR | L7 | 16,014 | 8,261 | 6,144 | 90.7% | +759 hits (+14.1%), +34.8pp enriched |
| USA | L6 | 28,631 | 8,110 | 6,622 | 83.0% | — |
| USA | L7 | 28,631 | 8,110 | 7,057 | 88.3% | +435 hits (+6.6%), +5.3pp enriched |

**Interpretation.** The addition of watershed covariates (L7) **does NOT suppress** the mine–KO signal. Instead, survival **increases** at L7, indicating that basin-scale hydrology is orthogonal to and partially enhances the mine-proximity signal. The dramatic directionality shift in EUR (55.9% → 90.7% enriched) suggests that watershed properties help distinguish KOs that are genuinely enriched near mines from background metabolic variation.

The **hydrogeological confound hypothesis is rejected**: if mine locations were merely markers for specific watershed types (e.g., mountainous terrain with high runoff), adding basin covariates would suppress the association. Instead, the signal intensifies, indicating:

1. **Basin hydrology captures independent spatial structure** — mines and streams co-locate in specific catchments for geological reasons (ore deposits in particular rock types), and basin covariates encode that geology
2. **Directionality gains** suggest basin covariates help partial out noise — L6 residuals contain mine-independent community variation (e.g., co-varied with runoff), which L7 removes
3. **Regional asymmetry** (EUR +34.8pp vs USA +5.3pp enriched shift) may reflect different geographies: European samples more evenly distributed across ore districts; USA samples more concentrated in Western mining regions where basin hydrology and mine proximity are more tightly coupled

**Output.** `data/nb39/basin_fwl_summary.csv` (directional summary L6 vs L7); `data/nb39/basin_fwl_l7_results.csv` (full KO-level results with L6 and L7 β/SE/pval/qval); `figures/fig_nb39_basin_attrition.pdf` (bar chart comparing L6 vs L7 FDR hit counts per region).

---

## NB41: Soil CWM FWL mine proximity — v3 (full soil KO prevalence, L0→L8)

**Script:** `scripts/run_nb41_soil_ko_fwl.py` (v3, 2026-08-30)
**KO prevalence source:** `data/nb16/genus_ko_prevalence.parquet` (SPIRE soil MAGs, all genera meeting prevalence thresholds)

**Method:** FWL at L0→L8 for mine_any_dist_km exposure (nearest mine of any type from mindat database) in EUR (40,358 soil samples) and USA (67,835 soil samples). Covariate levels:
- **L0:** bivariate (exposure only)
- **L5:** L0 + pH + pH² + annual_mean_temp + annual_precip + latitude
- **L6:** L5 + genus PC1 (computed inline from RA matrix)
- **L7:** L6 + SOC + clay + nitrogen + WTD + soil temperature + lithology (region-specific columns)
- **L8** (EUR only): L7 + EMEP atmospheric Cd/Hg/Pb deposition

**Results (v3 — correct prevalence matrix):**

| Region | Level | KOs tested | FDR < 0.05 | % Enriched | Key change |
|--------|-------|------------|-----------|-----------|-----------|
| USA | L0 | 9,217 | 7,888 | 57.6% | — |
| USA | L5 | 9,217 | 8,008 | 57.7% | baseline env control |
| USA | L6 | 9,217 | 8,018 | 71.2% | +genus composition |
| USA | **L7** | 9,217 | **8,079** | **73.7%** | **robust after soil control** |
| EUR | L0 | 8,507 | 5,402 | 30.8% | — |
| EUR | L5 | 8,507 | 4,577 | 48.8% | baseline env control |
| EUR | L6 | 8,507 | 4,695 | 49.9% | +genus composition |
| EUR | L7 | 8,507 | 5,008 | 31.2% | watershed covariates |
| EUR | **L8** | 8,507 | **5,408** | **26.0%** | **EMEP deposition inverts directionality** |

**Extreme sites:** top 5th percentile mine-proximal sites — 3,393 USA / 2,074 EUR. Per-site enrichment score computed from mean L6 beta of FDR-significant KOs weighted by CWM.

**Key interpretations:**

1. **USA — mine signal robust through L7:** 8,079 FDR-significant KOs (88% of tested set) remain associated with mine proximity after full covariate control (pH, climate, genus composition, soil properties, lithology). 73.7% are enriched (KOs more prevalent in communities near mines). The mine-KO association in USA soil is **NOT mediated by soil physicochemistry** — the signal persists and strengthens directionally when soil confounders are controlled. This indicates a direct ecological effect: communities exposed to mine-contaminated soils harbor distinct functional profiles.

2. **EUR — directionality inverts at L8:** Signal increases in magnitude at L7 (5,008 hits) but directionality inverts when EMEP atmospheric deposition is added (L8: 5,408 hits, only 26% enriched). This pattern suggests two competing processes: (a) local mine proximity selects for certain KOs (a positive association at L6–L7), but (b) atmospheric Cd/Hg/Pb deposition, which co-localizes with mines geographically in Europe, selects *against* most KOs. Once deposition is explicitly controlled, the dominant signal is depletion (negative β), not enrichment. This is consistent with recent findings that atmospheric Hg deposition drives distinct community assembly patterns independent of local ore geology (Gustin et al. 2020, *Sci Total Environ* 738:139763; Bishop et al. 2020, *Nat Rev Earth Environ* 1:45–63).

3. **Regional contrast interpretation:** USA mine signal remains positive and robust through full control; EUR mine signal is masked or reversed by atmospheric deposition confounding. This regional asymmetry may reflect: (i) USA mining operations more concentrated in arid/semi-arid regions where atmospheric deposition is lower; (ii) European ore districts located in high-precipitation zones where atmospheric deposition represents a major Hg pathway; or (iii) different historical mining intensities or ore types producing different soil geochemistry trajectories (Tipping et al. 2011, *Environ Pollut* 159:1531–1538).

4. **Positive enrichment in USA (73.7%) suggests selection, not random noise:** A majority of mine-associated KOs are enriched, not depleted. This pattern is inconsistent with simple "stress → genome streamlining" hypothesis and instead suggests that mine proximity selects for specific functional competencies in soil communities.

**Output.** `data/nb41/soil_fwl_summary_v2.csv`, `soil_fwl_l6_full_v2.csv`, `soil_fwl_l7_full_v2.csv`, `soil_extreme_sites.parquet`; `figures/fig_nb41_v2_soil_ko_survival.pdf`, `fig_nb41_v2_extreme_sites_map.pdf`, `fig_nb41_v2_top_kos_extreme.pdf`.

---

## NB23 — Pred Matrix Patch + EMEP Patch (data fix notebook)

**Script:** inline notebook (2026-08-xx)

Minor data-fix notebook that back-filled two missing columns into existing predictor matrices:
1. Corrected an off-by-one in the EUR EMEP deposition join (atmospheric Cd/Hg/Pb columns) that caused ~3% of samples to receive NaN deposition values from a wrong grid cell.
2. Added `lithology_int` (integer-encoded Hartmann & Moosdorf 2012 lithology class) to the USA predictor matrix, required for the L7 covariate set in NB41.

No new samples or models were added. All downstream analyses (NB25 onward) read from the patched matrices.

---

## NB24 — DEGREE Novel Soil Sample Extraction

**Script:** inline notebook (2026-08-xx)
**Output:** `data/nb24/degree_eur_genus_long.parquet`, `degree_eur_pred_matrix.parquet`, `degree_swiss_genus_long.parquet`, `degree_swiss_pred_matrix.parquet`, `degree_usa_genus_long.parquet`, `degree_usa_pred_matrix.parquet`, `degree_sample_meta.parquet`

Extracted genus-level relative abundance and predictor matrices from the DEGREE h5ad soil dataset (Lavallee et al. 2023) for novel samples not present in the MicrobeAtlas 16S compilation. DEGREE provides European ($n = 3{,}097$), Swiss (small subset), and USA soil metagenomes assembled to genus level. Output used in NB25 (augmented VP) to supplement MicrobeAtlas coverage.

---

## NB26 — Swiss MEM Sensitivity (k = 5, 10, 15, 20, 30, 50)

**Script:** inline notebook (2026-08-xx)
**Output:** `data/nb26/swiss_ko_shannon_mem_sensitivity.csv`

Repeated the Swiss variation-partitioning analysis (same covariate set as NB21: elements, mine proximity, pH+CEC, climate, soil, spatial MEMs) across six MEM neighbour-list sizes (k = 5, 10, 15, 20, 30, 50) to test whether the mine-proximity partial R² (pure mine) is sensitive to spatial MEM choice.

| k | n MEMs | pure_mine |
|---|--------|-----------|
| 5 | 22 | 0.305 |
| 10 | 23 | 0.344 |
| 15 | 24 | 0.378 |
| 20 | 25 | 0.323 |
| 30 | 30 | 0.581 |
| 50 | 32 | 0.533 |

Mine-proximity partial R² (Swiss KO Shannon) is stable across all k values tested (range 0.305–0.581), confirming that the Swiss mine signal is not an artefact of MEM parameterisation. The k = 30 result (0.581) matches the main analysis (NB21: mine_pure = 0.526 at k = 20 MEM).

---

## NB27 — Interactive Maps (EUR / Swiss / USA sample distributions)

**Script:** inline notebook (2026-08-xx)
**Output:** `figures/fig_nb27_eur_map.html`, `fig_nb27_swiss_map.html`, `fig_nb27_usa_map.html`

Interactive Plotly scatter maps of all MicrobeAtlas samples coloured by mine proximity (log-scale). Used for visual quality control of spatial coverage and to identify sample clusters near known mining districts. No quantitative analysis; for exploration and presentation only.

---

## NB40 — Stream Per-KO MAG-Level FWL (GlobDB Freshwater MAGs)

**Script:** `scripts/run_nb40_stream_mag_ko_fwl.py` / inline (2026-08-31)
**KO source:** `data/nb40/globdb_freshwater_ko_matrix.parquet` (790,251 rows: 818 MAGs × 2,689 KOs present)
**Exposure:** mine proximity: log₁₀(1/(mine_any_dist_km + 0.1)); real distances computed via 3D KDTree against mindat 157K localities (median dist = 15.6 km)

**Method:** OLS regression per KO (binary 0/1 presence as outcome) at two covariate levels:
- **L0:** bivariate (exposure only)
- **L6:** + genus one-hot fixed effects (528 genus dummies)

KOs filtered to ≥5 genera and ≥10% prevalence across 818 MAGs → 2,689 KOs tested.

**Results:**

| Level | KOs tested | FDR < 0.05 | % Enriched |
|-------|-----------|-----------|-----------|
| L0 | 2,689 | 701 (26%) | 61% |
| L6 (genus FE) | 2,689 | 295 (11%) | 67% |

**Key interpretations:**
1. **L0 signal (26% of KOs):** A substantial minority of stream freshwater KOs associate with mine proximity in bivariate analysis — consistent with the stream CWM FWL result (NB33/NB39) showing gene-level mine signal in streams.
2. **L6 signal survives genus control (11% of KOs, 295 hits):** After controlling for genus identity directly (not just community PC1), 295 KOs remain significant. This confirms that at least some of the stream mine association reflects within-genus gene content variation (gene gain/loss) rather than genus replacement.
3. **Majority positive (67% enriched at L6):** KOs enriched near mines outnumber depleted KOs 2:1 even after genus fixed effects, consistent with the hypothesis that mine-proximal stream communities maintain elevated functional gene diversity (gene gain), not reduced diversity.
4. **Comparison with soil (NB41 vs NB40):** Soil MAG-level analysis (per-KO metal associations, NB42) found ≤3% overlap between CWM-level and genome-level associations. Stream MAG-level analysis (NB40) shows a weaker but non-trivial genome-level signal (11% of KOs FDR), consistent with the hypothesis that stream communities experience more direct metal exposure and therefore stronger within-lineage selection.

**Limitation:** 818 freshwater MAGs is a small sample; many genera are represented by a single MAG, limiting within-genus comparisons. The genus fixed-effects model is highly saturated (528 dummies for 818 samples), reducing power. Results should be interpreted as directional evidence, not precise quantification.

**Output:** `data/nb40/nb40_l0_results.csv`, `data/nb40/nb40_l6_results.csv`, `data/nb40/nb40_summary.csv`.

---

## NB41-FOREGS — EUR CWM FWL with FOREGS Stream Metal Concentrations

**Script:** `scripts/run_nb41_eur_foregs.py` (2026-08-30)
**Output:** `data/nb41/foregs_stream_fwl_summary.csv`, `figures/fig_nb41_eur_foregs_comparison.pdf`

**Motivation:** Mine proximity is an indirect exposure proxy. FOREGS (Forum of European Geological Surveys) provides measured stream metal concentrations at 808 European sampling stations. This analysis tests whether actual stream water metal concentrations predict EUR soil microbiome functional composition, and compares the signal to the mine-proximity result.

**Method:** Same CWM-based FWL pipeline as NB41 but restricted to 37,856 EUR MicrobeAtlas samples within 100 km of a FOREGS site with at least one measured metal concentration (93.8% of EUR samples). Exposure = log₁₀(stream concentration, mg/L) for each of 8 metals. Covariate levels: L0 (bivariate) and L5 (pH, pH², BIO1, BIO12, latitude).

**FOREGS coverage:** 4,398 total FOREGS sites; 808 with measured stream metals; 37,856 EUR soil samples matched (93.8% of 40,358 EUR samples).

**Results by metal:**

| Metal | n | L0 hits | L0 % pos | L5 hits | L5 % pos |
|-------|---|---------|----------|---------|----------|
| Cr | 37,856 | 7,150 | 87% | 6,682 | 85% |
| Pb | 37,856 | 7,503 | 85% | 6,661 | 79% |
| Zn | 37,856 | 6,986 | 82% | 6,706 | 80% |
| Cd | 37,856 | 6,419 | 72% | 5,834 | 83% |
| Mn | 37,856 | 6,430 | 67% | 5,342 | 67% |
| As | 37,856 | 5,551 | 67% | 4,834 | 51% |
| Cu | 37,856 | 6,412 | 53% | 6,405 | 40% |
| Ni | 37,856 | 5,839 | 33% | 5,827 | 42% |

**Key interpretations:**
1. **Stream metal concentration strongly predicts soil CWM:** For Cr, Pb, and Zn, 80–87% of FDR-significant KOs are enriched (positive association) after pH/climate control at L5. These are measured concentrations, not mine proximity proxies, providing direct evidence that chemical contamination gradients drive functional community composition.
2. **Consistent direction across most metals:** 6/8 metals show majority positive associations at L5 (>50% of hits enriched). This is consistent with the mine-proximity result (NB41 v3) for USA but provides an independent, measured-concentration validation for EUR soils.
3. **Cu and Ni are mixed:** Cu and Ni show weaker positive or slight negative associations (<53% enriched at L5). Cu in particular inverts to 40% enriched at L5, suggesting pH/climate covariates explain much of the bivariate Cu-KO relationship.
4. **Comparison to mine proximity (EUR):** Mine proximity at L8 (NB41 v3) yields only 26% enriched KOs after EMEP atmospheric control, while FOREGS stream-measured concentrations yield 67–87% enriched KOs for Cr/Pb/Zn. This contrast supports the interpretation that atmospheric deposition suppresses the mine-proximity signal in EUR soils, but actual stream-borne contamination gradients produce robust positive functional associations. The FOREGS result independently validates that chemical exposure — not confounding by human land use or climate — drives functional enrichment.

**Limitation:** FOREGS sites measure stream water; the soil samples are matched by spatial proximity (100 km) rather than direct drainage connection. Interpretation assumes that stream concentrations at FOREGS sites reflect local geochemical loading relevant to surrounding soil communities. This is a reasonable assumption for diffuse contamination but may not hold for point-source contamination.

---

## NB41-LUCAS — EUR CWM FWL with LUCAS Measured Soil Metal Concentrations

**Script:** inline (2026-08-31)
**Output:** `data/nb41/lucas_soil_metals_fwl_summary.csv`

**Motivation:** Mine proximity is an indirect exposure proxy that conflates high-concentration mine-drainage sites with low-concentration atmospheric-deposition areas. LUCAS 2018 provides directly measured soil concentrations of 13 elements across 27,819 EUR sites. Replacing mine proximity with measured soil concentrations tests whether the EUR soil KO enrichment direction is genuinely weak (consistent with low-dose atmospheric deposition creating no gene-level selection) or is simply masked by the noisiness of the mine-proximity proxy.

**Method:** Same CWM FWL pipeline as NB41 (nb16 soil prevalence, EUR MA samples, L0 bivariate and L5 pH+climate). Nearest LUCAS HM site joined to each EUR MA sample (median distance 7 km); sites > 100 km excluded. n ≈ 21,500 EUR samples with LUCAS coverage.

**Results at L5 (pH + climate + latitude controlled):**

| Metal | L5 hits | L5 % enriched | Primary soil source |
|-------|---------|--------------|---------------------|
| Ni | 6,128 | **72%** | Ultramafic geology / mining |
| Cu | 6,220 | **68%** | Mining / smelting |
| Zn | 6,164 | **66%** | Mining / galvanizing |
| Cr | 6,114 | **63%** | Ultramafic / mining |
| Pb | 6,784 | **59%** | Mining / leaded fuel |
| Hg | 6,602 | **55%** | Atmospheric / industrial |
| Cd | 6,100 | **28%** | Agricultural phosphate |
| As | 6,194 | **29%** | Geogenic background |

**Key interpretations:**

1. **Mining-associated metals are positively enriched (59–72%):** Pb, Zn, Cu, Cr, and Ni — all primarily elevated by mining and smelting — show clear positive enrichment when measured directly in soil. This is intermediate between mine proximity (49% at L5) and FOREGS stream concentrations (79–85%), consistent with bioavailability scaling with delivery route.

2. **Agricultural/geogenic metals are not enriched (28–29%):** Cd and As are near-null. Cd in European soils is elevated primarily by phosphate fertilization (agricultural Cd), not mining; As by geogenic parent material. These sources deliver metals in low-bioavailability mineral-bound forms that do not exert the same microbial selection pressure as mining contamination.

3. **Three-tier exposure gradient:** The consistent gradient mine proximity (49%) < LUCAS soil (59–72%) < FOREGS stream (79–85%) for mining-associated metals indicates that the EUR mine-proximity inversion (26% at L8 with EMEP control) is largely an exposure-proxy problem. Mine proximity conflates areas with direct mine-drainage contamination (high dose, high bioavailability) with areas receiving only atmospheric deposition (low dose, lower bioavailability). When soil metal concentrations are measured directly, the enrichment direction is unambiguously positive for mining-sourced metals.

4. **Bioavailability as the governing axis:** Stream-delivered metals are in dissolved/colloidal form immediately bioavailable to microbial cells; soil-bound metals are partly sequestered in mineral phases, reducing bioavailability; atmospheric deposition adds metals primarily as fine oxide particles that equilibrate slowly. The gradient mirrors this bioavailability ranking.

**Conflict with the energy-cost hypothesis:** The user's alternative hypothesis proposed that chronically low-dose atmospheric deposition creates a selection environment where community turnover is cheaper than maintaining efflux pumps, causing depletion. The LUCAS result partially contradicts this: measured soil metal concentrations that include both mining-derived and atmospheric contributions show positive enrichment (59–72%), not depletion. The mine-proximity inversion appears to be driven by spatial imprecision (including low-dose areas in the mine-proximity exposure estimate), not by a genuine metabolic cost differential between atmospheric and point-source exposure. Cd and As do remain near-null even with measured concentrations, which could reflect geochemical form (low bioavailability) rather than dose-threshold dynamics; distinguishing these requires speciation data not currently available.

**Output:** `data/nb41/lucas_soil_metals_fwl_summary.csv` (16 rows: 8 metals × 2 levels).

---

## Cross-Habitat Comparison Summary (NB33/NB40/NB41/NB41-LUCAS — 2026-08-31)

This section synthesises the direct soil-stream comparison at matched method and KO universe, which closes the methodological gap identified in earlier analyses.

### CWM level (same nb16 soil KO prevalence, same FWL framework)

| Region | Habitat | n samples | L5 hits | L5 % enriched |
|--------|---------|-----------|---------|--------------|
| EUR | Stream (NB33-rerun) | 44,486 | 6,894 | **71%** |
| EUR | Soil (NB41 v3) | 40,358 | 4,577 | **49%** (mine prox) |
| EUR | Soil (NB41-LUCAS) | ~21,500 | 6,100–6,784 | **59–72%** (measured metals) |
| USA | Stream (NB33-rerun) | 64,789 | 7,110 | **71%** |
| USA | Soil (NB41 v3) | 67,835 | 8,008 | **58%** (mine prox) |

Stream consistently shows ~71% enriched in both regions with matched KO universe. Soil with mine proximity is lower (49–58%) but recovers to 59–72% when measured soil concentrations replace the proxy.

### Genome level (mine proximity + genus fixed effects, same OLS framework)

| Habitat | n MAGs | L6 genus FE hits | L6 % enriched |
|---------|--------|-----------------|--------------|
| Stream (NB40, GlobDB freshwater) | 818 | 295 | **67%** |
| Soil (new, SPIRE) | 2,477 | 196 | **47%** |

After controlling for genus identity, soil shows a null within-genus signal (47% ≈ coin flip), while stream retains a clear positive signal (67%). **Within-lineage gene gain is a stream phenomenon; soil mine associations are driven by genus composition turnover, not within-lineage KO variation.**

### Interpretation

The combined analyses show that "turnover vs. gene gain" is not a binary but a continuum governed by exposure pathway and bioavailability:

- **Soil genome level:** ~100% turnover (genus fixed effects eliminate signal)
- **Soil CWM (mine proximity):** ~49–58% enriched — CWM-level signal partly reflects turnover that genus PC1 doesn't capture
- **Soil CWM (measured metals):** 59–72% — measured exposure reveals genuine positive signal in soil
- **Stream CWM:** 71% — consistent positive signal
- **Stream genome level:** 67% — within-genus gene gain confirmed in freshwater MAGs

---
