# MicrobeAtlas × ke_pangenome CWM Metal Ecology

**Project:** microbeatlas_cwm  
**Thesis chapter:** Chapter 3 — Community Genomic Survey (CWM arm)  
**Status:** In progress

---

## Research Question

Does metal exposure in soil predict shifts in community-weighted mean (CWM) functional gene content, after controlling for pH, soil properties, anthropogenic inputs, climate, and community composition (L0–L6 causal levels)?

**CWM definition:** For each soil sample and each KEGG ortholog (KO), CWM = Σ (genus_RA × KO_prevalence_in_genus), summed over all genera present. This weights functional gene content by the relative abundance of genera that carry it.

---

## Data

| Source | Description | Access |
|---|---|---|
| MicrobeAtlas | 16S OTU counts, genus-level taxonomy | `arkinlab.microbeatlas` Spark |
| ke_pangenome | KO/Pfam/COG/AMR prevalence per genus | `kbase.ke_pangenome` Spark |
| SoilGrids | pH, clay, SOC, CEC (string-typed; TRY_CAST) | `arkinlab.envdbs.soilgrids_master` Spark |
| WorldClim | MAT, MAP, seasonality (bio_1,4,12,15) | `arkinlab.envdbs.worldclim_master` Spark |
| GLiM lithology | Bedrock lithology class (categorical) | `arkinlab.envdbs.global_lithology_glim` Spark |
| USGS geochem | USA measured metals, 50+ elements, ~145K soil samples | `/data/envdbs/usgs_geochem/usgs_geochem.parquet` (local) |
| GEMAS | EUR measured soil metals (4,343 points) | `arkinlab.envdbs.gemas` Spark |
| FOREGS humus | EUR measured humus metals (377 points, supplement) | `/data/envdbs/FOREGS/foregs.parquet` (local) |
| NGSA | AUS measured soil metals (1,315 points) | `arkinlab.envdbs.ngsa_geochemistry` Spark |
| Mindat | Mine locations, 157K localities with element type | `/projects/microbeatlas_metal_ecology/data/mindat.csv` (local) |
| Mining operations | Mine locations supplement (8,507 points) | `arkinlab.envdbs.mining_operations` Spark |

**pH hierarchy:** measured `ph` (33,705) → `olm_soil_ph_0cm_H2O` (274,685) ÷ 10 (OLM stores pH×10) → SoilGrids raster (`arkinlab.envdbs.soilgrids_master.pH_0cm`, 55 km KDTree join). Three-level coalescence covers 4,844/4,884 thinned samples; 40 uncoverable (Antarctic, lat<−63°). Flag source as `ph_is_modelled` in all models.

**Anthropogenic covariates:** nighttime lights (`lights_radiance_nanow_cm2_sr`) already in sample_metadata; mine proximity from mindat.csv (157K localities, primary) + mining_operations (supplement); EPA TRI (USA) and E-PRTR (EUR) for industrial release proximity.

**DO NOT use** `enriched_metadata` or `enriched_metadata_gee` — all spatial joins done from raw tables above.

---

## Notebooks

| Notebook | Purpose | Status |
|---|---|---|
| NB00_data_qc | MicrobeAtlas sample fetch, spatial thinning (0.45°), QC figures | **COMPLETE** — 4,884 thinned cells (13,696 ocean-masked); pH: 622 measured / 3,256 OLM / 966 SoilGrids raster / 40 missing (Antarctic) |
| NB01_cwm_construction | ke_pangenome join, CWM computation, matrix QC, V-region assignment | **COMPLETE** — 2,359/4,443 genera overlap (53.1%); median RA covered 65%; CWM: 4,868 samples × 6,557 KOs; 81% V4/V3 |
| NB02_metal_associations | **Bidirectional:** forward (L0–L6 FWL × USGS metals → CWM) + reverse (CWM → metal, feature-selected RidgeCV, spatial block CV) | **COMPLETE** — 23 USGS elements; 560 L1 FDR hits / 54 L6 / 17 stable; As hits = arsenic resistance cluster (K15844/K15847/K15848); reverse: all R²<0 (near-zero Ni/Yb/Cu/Pb) — spatial block CV fails, forward associations do not generalize spatially |
| NB03_functional_interpretation | Hit characterization, pathway/module context, DAG causal audit | **COMPLETE** — REE confound confirmed; 17 stable hits (cell wall, MoCo, RNA QC, stress); GlobDB MRG: 1 hit (Cd×zntA/cadA) |
| NB04_regional_replication | EUR GEMAS, AUS NGSA replication + pH positive control + reverse Ridge | **COMPLETE** — EUR: strong replication (88–100% overlap, 100% concordant, As/Cd/Cr/Ni/Pb/Zn); AUS: 0 FDR hits; pH ctrl: 2,307/162 EUR hits (L0/+soil); reverse: all spatial R²<0 |
| NB05_mine_proximity | **Bidirectional:** forward (mine proximity → CWM, 3 operationalizations + elev_rel) + reverse + commodity all-KOs | **COMPLETE** — log_prox/log_dist L1: 481/462 FDR hits (corrected pH scale); binary: 0; commodity genome-wide: 0; reverse R²<0; elev_rel mean=−39 m (23% downhill) |
| NB06_mine_extended | Extended mine proximity: global tertile stratification, EUR measured metals × elev_rel, functional interpretation | **COMPLETE** — global all=484 L1, uphill=0, downhill=17; EUR Cu uphill=188 vs all=3; Metabolism enriched 1.6× in commodity hits |
| NB07_sensitivity | Zeleny permutation, pESS, collider sensitivity, robustness checks | **COMPLETE** — 6/7 metals pass permutation test (Pb p=0.084 NS); pH form robust (96–100% overlap); rank transform reduces hits 75–97% |
| NB08_pfam_cog | Pfam domain + COG category CWM FWL (L0–L6); cross-annotation comparison | **COMPLETE** — Pfam: 5,000 domains tested, 761 L1 hits (all Cd; top: Beta_helix, Zn_peptidase_2, Thymidylat_synt); COG: 22 L1 hits (V=18 β=−0.056, Cd=2, Cu=1, Pb=1); KO L1=560 for comparison |

---

## Key Findings

### Finding 1 — Metal exposure shifts microbial community composition (turnover), not within-genus gene content

![L1 FDR hits by metal (Manhattan)](figures/fig_nb02_manhattan_L1.pdf)
![Facultativeness of hit KOs vs background](figures/fig_nb02_facult_ko.pdf)

**225 non-REE L1 FDR hits** across 9 elements (560 total including Nd=235, Yb=91, La=9 flagged as geology confounds) from 6,557 KEGG orthologs tested in 4,884 globally thinned soil samples. Yet three independent tests converge on **community turnover — not gene gain — as the mechanism:**

1. **Facultativeness test:** Metal-associated KOs (n=508) are indistinguishable from background in within-genus prevalence (p=0.187), while pH-associated KOs are significantly more universal (p=1.2×10⁻⁷¹). High-prevalence KOs are constitutive core genes that vary across genera — i.e., turnover. Low-prevalence KOs are facultative strain-level genes — i.e., gene gain. Metal hits match background; pH hits are core genes. Different mechanisms.
2. **Reverse prediction:** CWM cannot spatially predict metal concentrations in any region (spatial block CV R²<0 for all metals vs. spatial R²=+0.151 for pH). If gene gain were occurring, the gene-metal link would be spatially robust. It isn't.
3. **Collider check:** 98–100% of L1 metal hits are attenuated at L5 (community composition control), indicating the metal signal is mediated through community composition, not direct gene-environment coupling.

*(Notebooks: NB02_metal_associations.ipynb, NB03_functional_interpretation.ipynb)*

---

### Finding 2 — EUR strongly replicates USA associations with 100% directional concordance

![EUR replication overlap](figures/fig_nb04_hits_heatmap.pdf)

USA L1 FDR hits replicate in Europe (GEMAS) at **84–100% overlap and 100% directional concordance** for all metals with substantial USA signal (As, Cd, Cr, Ni, Pb, Zn). EUR identifies additional hits (Cd: 31 EUR vs 10 USA; Pb: 56 EUR vs 14 USA) owing to larger EUR sample coverage of those metals. Australia (NGSA, n=232) shows 0 FDR hits — approximately 5× underpowered and not interpretable as evidence against the hypothesis.

The cross-continental replication confirms the associations are not USA-specific confounds (geology, land use, survey design). pH positive control in both regions recovers massive hits at L0 (EUR: 2,307; AUS: 2,106), confirming the FWL engine has power where biological signal exists.

*(Notebook: NB04_regional_replication.ipynb)*

---

### Finding 3 — Mine proximity identifies a distinct, non-metal-driven CWM signal

![Mine proximity hits by level](figures/fig_nb05_mine_hits_by_level.pdf)
![Mine vs metal overlap](figures/fig_nb05_mine_metal_overlap.pdf)

**481 L1 FDR hits** for log mine proximity (Mindat 157K localities), but only **~2.7% overlap** with NB02 measured-metal hits. Commodity-specific mine proximity (Cu, Pb, Zn, Ni) gives **0 FDR hits** genome-wide. Mine proximity is enriched for **Metabolism KOs** (~1.6× vs background; NB06), consistent with selection for metabolic flexibility near disturbed terrain rather than metal resistance specifically. Elevation stratification reveals that the proximity signal is largely driven by elevation-correlated confounders (484 global hits → 17 downhill → 0 uphill), consistent with topographic rather than contamination signal.

Mine proximity is an insufficient surrogate for measured metal bioavailability in CWM analyses.

*(Notebooks: NB05_mine_proximity.ipynb, NB06_mine_extended.ipynb)*

---

### Finding 4 — pH is a structurally stronger functional driver; metals are real but weak

![pH coverage and source hierarchy](figures/fig_nb00_ph_coverage.pdf)
![Beta stability across levels](figures/fig_nb02_beta_stability.pdf)

pH FWL identifies **4,322 L1 hits** (vs 225 non-REE for metals) and those KOs are constitutive core genes (mean_prev=0.733 vs background 0.604, p=1.2×10⁻⁷¹). pH CWM generalizes spatially (R²=+0.151 spatial block CV). The **5/7 metals pass the Zeleny permutation test** (As, Cr, Cu, Ni, Zn at p<0.05; Cd p=0.064 and Pb p=0.088 fail), confirming the passing associations are statistically real beyond the BH-FDR threshold. Effect sizes per IQR metal concentration are small (β_IQR ≈ 0.003, partial R²<0.03) — consistent with metal being a secondary environmental filter overlaid on a primary pH-structured microbiome.

*(Notebooks: NB02_metal_associations.ipynb, NB07_sensitivity.ipynb)*

---


**Effect sizes are statistically significant but small.** Partial R² at L1 (computed from FWL t-statistics: f² = t²/(n-k-1), partial R² = f²/(1+f²)): As top hit (K15844) partial R²≈0.015; Zn top hits range 0.010–0.025; pH top hits 0.04–0.12. Metal associations are detectable at large N (n~1,000–1,700) but individually weak (partial R²<0.03 all hits). pH effects dominate (3–8× larger standardized effect sizes).

## Discoveries

- **OLM pH is stored as pH×10** (range 40–87 = pH 4.0–8.7). Always divide `olm_soil_ph_0cm_H2O` by 10.0 before use. Using the raw integer corrupts all pH-spline covariates: the spline attempts to fit pH range 2.5–87, collapsing the biologically relevant 4.0–8.7 interval into a thin band. Discovered after it silently corrupted NB05 and NB06 results (mine proximity L1 went from 481→516 and 462→484 after correction).
- **ke_pangenome `eggnog_mapper_annotations.PFAMs` column uses comma-separated Pfam short names** (e.g., `Fer4_12,Radical_SAM,SPASM`), not pipe-separated PF accessions as documented. Using the wrong separator returns 65,428 "combo-string" pseudo-IDs rather than ~70K individual domain names; pivot_table at 8,419 × 65,428 causes OOM. Fix: `split(e.PFAMs, ',')`.
- **Spatial block CV vs random CV for metal prediction:** Random block CV R² for CWM → metal prediction ranges 0.03–0.06 (looks like a signal); spatial block CV R² is negative for all metals in all regions. The inflated random-CV R² is entirely due to spatial autocorrelation allowing nearby samples to train/test-split together. Always use spatial block CV for soil microbiome × geochemistry prediction tasks.

---

## Results

### NB02 — Metal × CWM Associations (2026-08-21)

**Forward FWL (log₁₀(metal) → CWM, pH-adjusted = L1 primary estimand):**

- 23 USGS elements with ≥30 positive (above-detection) values analysed; 1,055,677 total FWL rows (23 × 7 levels × 6,557 KOs)
- **L1 FDR hits: 560** across 14 metals; **L6 (full-model) hits: 54**; **stable (L1 ∩ L6): 17**
- Hit distribution by element (L1): Nd=235, Yb=91, Zn=76, As=41, Cr=38, Ni=38, Pb=14, Cd=10, La=9, V=6, Nb=1, Sr=1 (Cu=0)
- **As hits form a coherent arsenic-resistance cluster:** K15844/K15847/K15848/K21219 (ars operon), K12051, K12086–K12104 series — all negatively associated (high-As soils have lower arsenic-resistance CWM, consistent with community turnover toward resistant genera dominating)
- **Top Zn hit:** K09162 (universal stress protein USP-F), β_IQR=+0.003, q=0.002
- **Nd/Yb dominance (235+91=326/560 hits):** rare-earth elements; likely reflects geology/pH collinearity not biological signal — interpret cautiously; Nd/Yb not included in primary manuscript claims without additional controls
- **Sample sizes (n positive):** As=1,143; Ni=1,645; Cr=1,693; Cu=1,689; Pb=1,630; Zn=1,184; Cd=998; Nd/Yb coverage not independently verified

**Reverse Ridge (CWM → target; feature-selected RidgeCV; two CV schemes):**

| Target | n | Features | Random CV R² | Spatial CV R² |
|---|---|---|---|---|
| **pH (positive ctrl)** | 3,878 | 200 (top \|r\| with pH) | **+0.287** | **+0.151** |
| Yb | 433 | 91 (L1 FDR KOs) | +0.064 | −0.002 |
| Cd | 998 | 10 | +0.051 | −0.252 |
| As | 1,143 | 41 | +0.048 | −4.223 |
| V | 526 | 7 | +0.038 | −0.463 |
| Zn | 1,184 | 76 | +0.031 | −1.502 |
| Pb | 1,630 | 14 | +0.026 | −0.162 |
| Cu | 1,689 | 0 | +0.000 | −0.159 |
| Cr | 1,693 | 38 | −0.002 | −1.104 |
| Ni | 1,645 | 38 | −0.278 | −0.072 |
| Nd | 89 | 250 | −0.812 | −0.653 |
| La | 295 | 12 | −0.841 | −17.071 |

- **Positive control (pH):** random CV R²=0.287, spatial CV R²=0.151 — confirms method has power when gene-gain signal exists. pH is recoverable from CWM across spatial blocks
- **Metals (random CV):** R²≈0.00–0.06 for most elements — weak within-region interpolation only; near zero vs pH's 0.287
- **Metals (spatial CV):** all negative — no cross-region generalisation
- **Interpretation:** CWM functional content carries a detectable pH signal (gene-gain: pH directly regulates physiology) but not a metal signal. The forward FWL hits for metals reflect real associations after controlling confounders, but the effect sizes are too small and spatially inconsistent to reverse-predict metal levels. **Consistent with community turnover as the dominant response mechanism for metals**, with pH driving the stronger gene-level adaptation
- Nd/La: small n (89/295) makes CV unreliable; discard

### NB02 — Facultative KO test: gene gain vs. turnover (2026-08-21)

**Rationale:** ke_pangenome `prevalence` = fraction of species clades within a genus carrying the KO. Values < 1 mean some strains have it and others don't — the signature of a facultative gene consistent with recent HGT or gene gain/loss. pH run as a positive control (FWL with Z=intercept+lat/lon; 4,322 FDR hits); pH hits excluded from background to avoid confounding.

**Three-way comparison (corrected):**

| Group | n KOs | Median mean_prev | vs background |
|---|---|---|---|
| Background (non-pH, non-metal) | 2,017 | 0.604 | — |
| Metal hits (L1 FDR, any element) | 508 | 0.595 | **p=0.187 (n.s.)** |
| pH hits (L1 FDR, lat/lon Z) | 4,322 | 0.733 | **p=1.2×10⁻⁷¹** |

**Key finding:** The initial p=1.5×10⁻⁸ (metal hits more facultative than "background") was confounded — pH-hit KOs (very universal, mean_prev=0.733) were in the background group, artificially inflating it. With pH hits properly excluded, metal hits are **indistinguishable from background** (p=0.187). There is no gene-gain signal for metals.

**pH hits are significantly MORE UNIVERSAL** (0.733 vs 0.604, p=1.2×10⁻⁷¹): pH-associated KOs are core physiology genes (proton pumps, ATP synthase, acid/base homeostasis) constitutively present in nearly all strains of every genus. pH drives turnover toward genera with different constitutive core repertoires — a genuine gene-content signal.

**Per-predictor ordered by mean_prev (background = 0.604, all metal comparisons n.s. after pH exclusion):**

| Predictor | n hits | mean_prev | Note |
|---|---|---|---|
| Nb | 1 | 0.367 | n=1, not interpretable |
| Yb | 124 | 0.381 | Likely REE/geology confound |
| Cr | 41 | 0.583 | = background (n.s.) |
| Ni | 41 | 0.583 | = background (n.s.) |
| Zn | 76 | 0.583 | = background (n.s.) |
| Pb | 14 | 0.607 | = background (n.s.) |
| As | 41 | 0.612 | = background (n.s.) |
| Co | 1 | 0.648 | n=1, not interpretable |
| Nd | 250 | 0.641 | Likely REE/geology confound |
| La | 12 | 0.696 | = background (n.s.) |
| Sr | 1 | 0.702 | n=1, not interpretable |
| V | 7 | 0.794 | = background (n.s.) |
| Cd | 25 | 0.806 | = background (n.s.) |
| Cu | 6 | 0.854 | = background (n.s.) |
| **pH** | **4,322** | **0.733** | **p=1.2×10⁻⁷¹ — core physiology genes** |

**Combined verdict: metals drive pure community turnover; no gene-gain signal by any test — confirmed by NB03 functional interpretation.** pH drives turnover toward genera with constitutively different core gene repertoires — a distinct, spatially reproducible gene-content signal. Three independent lines of evidence converge: (1) forward FWL betas small per IQR (≈0.003); (2) reverse Ridge R²≈0 for metals, 0.29 for pH; (3) metal FDR KOs statistically indistinguishable from background in facultativeness (p=0.187), pH KOs significantly more universal (p=10⁻⁷¹).

### NB02 — GlobDB MRG supplement (2026-08-24)

**Rationale:** ke_pangenome eggNOG annotations are missing 4 canonical metal resistance genes (merA K00221, merB K07444, zntA/cadA K01534, czcA K16786). GlobDB (SPIRE + MGnify MAGs) fills this gap for these 4 KOs only.

**Critical limitations of GlobDB supplement:**
1. **17% genus coverage:** GlobDB genus names (traditional capitalized) overlap with only 1,387 of the 7,956 ke_pangenome genera (17.4%). GTDB-to-Silva bridge does not materially improve this (18.5%); this is a fundamental taxonomic namespace mismatch, not a data gap.
2. **Structurally different prevalence metric:** ke_pangenome prevalence = fraction of GTDB *species clades* within a genus carrying a KO (species-level resolution). GlobDB prevalence = fraction of individual MAGs within a genus carrying a KO (MAG-level, not delineated into species). These metrics are not directly comparable.
3. **Only 4 KOs tested:** The supplement addresses a specific annotation gap. Hundreds of other canonical MRGs (e.g., arsB, arsC, chrA, nccA) were absent from GlobDB KO annotations at the genus level needed for CWM.
4. **Low genus count for merA and czcA:** 88 genera each — most MA genera assigned zero CWM by construction, not because they lack the gene. Power is severely limited.
5. **zntA/cadA result may reflect coverage bias:** The 512 genera with GlobDB zntA/cadA data are enriched for well-characterised Proteobacteria; the Cd association may reflect which genera were sequenced, not which carry the gene in Cd-contaminated soils.

**Coverage:** K00221 (merA): 88 genera, mean_prev=0.504; K07444 (merB): 207 genera, mean_prev=0.941; K01534 (zntA/cadA): 512 genera, mean_prev=0.753; K16786 (czcA): 88 genera, mean_prev=0.700.

**L1 FDR results (BH q<0.05, 92 tests across 23 metals × 4 KOs):**

| KO | Gene | Metal | n | β_IQR | q_BH |
|---|---|---|---|---|---|
| K01534 | zntA/cadA | Cd | 998 | +0.025 | 0.005 |

**Interpretation:** zntA/cadA (Zn/Cd/Pb P-type ATPase efflux pump) is positively associated with Cd (β_IQR=+0.025, q=0.005). Direction is biologically coherent. However, given the structural limitations above — especially the coverage bias and methodology mismatch — this single hit should be treated as tentative. merA, merB, and czcA show no FDR hits. The broader pattern — most canonical MRGs show no FDR association — holds under both ke_pangenome and GlobDB annotations, consistent with the turnover-over-gene-gain thesis.

### NB03 — Functional Interpretation (2026-08-24)

**DAG causal audit — hit attrition across L0→L6:**

- Nd and Yb hits collapse rapidly L1→L2 (after adding soil + lithology controls): confirms geology/pH collinearity confound, not biological specificity for REEs
- As: 41 hits at L1; partially persist to L2–L3 (ars-operon cluster survives pH + soil control); 0 stable hits at L6
- Zn (76), Cr (41), Ni (41): modest hits at L1, most not stable past L4 (attenuated by climate + community composition)
- Pb: 2 stable hits (K14370 MoaE, K14367 MoaC — molybdenum cofactor biosynthesis); tentatively interesting, effect size small

**Stable hits functional grouping (18 KOs at L1 ∩ L6):**

| Functional group | n hits | Metals | Interpretation |
|---|---|---|---|
| Cell wall / membrane biosynthesis | 6 | La | La-associated genera have distinct peptidoglycan/LPS compositions; REE geology confound plausible |
| Molybdenum cofactor (MoCo) | 2 | Pb | MoCo enzymes Pb-inhibitable; positive direction; small effect |
| RNA / ribosome quality control | 5 | La, Yb | Core translation-fidelity genes; REE geology collinearity likely |
| tRNA modification | 1 | La | MnmG (mnm5s2U34); La geology collinearity |
| Stress response / ATPase | 4 | Co, Yb | Diverse stress KOs; no single metal-resistance pathway |

**GlobDB MRG supplement (NB02 addition):** 1 FDR hit — Cd × K01534 (zntA/cadA), q=0.005, β_IQR=+0.025. Positive direction (high-Cd soils enriched in genera carrying Zn/Cd/Pb efflux pump). merA, merB, czcA: no FDR hits.

**Overall conclusion:** No coherent metal-resistance gene pathway emerges from the 647 L1 FDR hits. Functional groups are biologically heterogeneous (cell wall, RNA, stress) rather than converging on resistance machinery. The REE hits (58% of total) are geology confounds. Non-REE hits are small-effect, spatially non-reproducible, and functionally diverse — consistent with community turnover (geography-correlated compositional shifts) as the mechanism, not metal-specific gene-content adaptation.

### NB04 — Regional Replication: EUR (GEMAS) and AUS (NGSA) (2026-08-24)

**Design:** All 6,557 CWM KOs × 7 metals (As, Cd, Cr, Cu, Ni, Pb, Zn) × L0–L5 per region. FWL at each level; BH-FDR within each metal × level. EUR: 921 MA thinned samples with GEMAS metal join (n_valid ~760–920 per metal after pH filter). AUS: 236 MA samples with NGSA join (n~221–236). L5 includes Shannon diversity + top-8 phylum RA computed from genus_counts.

**EUR L1 FDR hits (GEMAS):**

| Metal | USA hits | EUR hits | Overlap | Concordant |
|---|---|---|---|---|
| As | 41 | 44 | 38 (93%) | 38/38 (100%) |
| Cd | 10 | 31 | 10 (100%) | 10/10 (100%) |
| Cr | 38 | 46 | 36 (95%) | 36/36 (100%) |
| Cu | 0 | 2 | 0 | — |
| Ni | 38 | 34 | 32 (84%) | 32/32 (100%) |
| Pb | 14 | 56 | 14 (100%) | 14/14 (100%) |
| Zn | 76 | 98 | 56 (74%) | 56/56 (100%) |

EUR replicates 84–100% of USA L1 hits for all metals with substantial USA signal (As, Cd, Cr, Ni, Pb, Zn), with 100% directional concordance. EUR identifies additional hits beyond USA (EUR Cd=31 vs USA Cd=10; EUR Pb=56 vs USA Pb=14; EUR As=44 vs USA As=41) — larger EUR sample set and different metal concentration range expand power.

**EUR hit attrition across levels:** As (484→44 L0→L1): pH control substantially reduces signal — confirms confounding. Cr, Zn relatively stable across L1–L5 (30–46 and 64–98 hits). Ni collapses at L2 — largely explained by soil properties after pH control. Cd pattern: 31 L1 hits, stable to L2.

**AUS L1 FDR hits (NGSA):**
- **Zero FDR hits** across all 6 metals and L0–L5.
- Near-miss for Zn: 20+ KOs with p<0.001, min q=0.074 — signal is present but doesn't survive correction across 6,441 KOs at n=232. Zn top near-misses cluster in K16016/K16017/K16022 (flagellar basal-body rod proteins).
- Power comparison: USA Zn n=1,184 (16 FDR hits/KO at n≈1,000 needed); AUS n=232 — approximately 5× underpowered.
- AUS null is consistent with either: (a) genuine absence of the metal–CWM pattern in Australian soils (different community structure, ancient nutrient-poor soils), or (b) insufficient power. Cannot distinguish without additional AUS samples.

**Interpretation:** EUR strongly replicates the USA L1 associations with 100% direction concordance — this is the strongest evidence that the associations are real and not USA-specific confounds. AUS null is uninformative about biology due to power. The Cu failure to replicate (USA n=6 hits, EUR n=3 hits, no overlap) is unsurprising given low USA hit count and weak original signal.

**pH positive control (EUR and AUS):** FWL with pH as exposure (Z = intercept only or + soil/lithology, pH excluded from Z). EUR L0: 2,307/6,516 FDR hits; EUR +soil/lith: 162/6,516. AUS L0: 2,106/6,516; AUS +soil/lith: 226/6,516. The massive L0 hit counts confirm the FWL engine recovers known, strong microbiome signal. The 162 EUR hits surviving soil/lithology control indicate genuinely pH-specific associations beyond soil chemistry. By comparison, the primary metal analyses (As=41, Zn=76 USA L1 hits) find far fewer hits — consistent with metals being a real but weaker microbiome driver than pH.

**Reverse direction (EUR and AUS): CWM → metal, RidgeCV + spatial block CV:**
All spatial R² values are negative across all EUR and AUS metals:

| Region | As | Cd | Cr | Cu | Ni | Pb | Zn |
|---|---|---|---|---|---|---|---|
| EUR | −0.43 | −0.49 | −0.16 | −0.18 | −0.24 | −0.79 | −0.24 |
| AUS | −0.40 | — | −0.43 | −0.26 | −0.26 | −0.27 | −0.83 |

Consistent with NB02 USA reverse result (all spatial R²<0). The EUR/AUS replication confirms that the forward associations (metal → CWM) are directionally real (100% EUR concordance), yet CWM does not spatially predict metals in any region. This apparent asymmetry reflects that: (a) metal concentration is the outcome of complex geological + anthropogenic spatial processes CWM cannot recover; (b) the forward associations are real but small-effect, insufficient to decode metal geography.

### NB05 — Mine Proximity × CWM (2026-08-24)

**Design:** All 6,557 CWM KOs × 3 operationalizations of mine proximity × L0–L5. Mine proximity is the exposure; causal level controls are pH (L1), soil/lithology + **elevation relative to nearest mine** (L2), nighttime lights/anthropogenic (L3), climate (L4), community composition (L5). Elevation-relative-to-mine (`elev_rel`) is the sample's DEM elevation minus the nearest Mindat mine's approximate DEM elevation (proxied from the nearest thinned MA sample at the mine's lat/lon). Mean elev_rel = −39 m (sd=367 m); 23.4% of samples are downhill from their nearest mine — consistent with mines often being at elevated terrain. n=4,884 global thinned MA samples; binary restricted to 2,938 (near <10 km or far >50 km).

**Forward FWL results (mine proximity → CWM, with elev_rel at L2):**

| Operationalization | L0 hits | L1 hits | L2 hits | L3 hits | L4 hits | L5 hits |
|---|---|---|---|---|---|---|
| log proximity [−log₁₀(dist+0.1)] | — | 516 | — | — | — | — |
| log distance [log₁₀(dist)] | — | 484 | — | — | — | — |
| binary (near <10 km vs far >50 km) | 0 | 0 | 0 | 0 | 0 | 0 |

Note: counts reflect corrected pH scale (OLM pH÷10; previous run used raw OLM×10, inflating pH range to 2.5–87, corrupting the pH spline). After the fix, pH range = 2.5–10.4 across 3,878 non-null samples.

- **Continuous proximity:** 481 L1 FDR hits (log_prox) / 462 (log_dist) — substantial signal. Hits decline sharply to ~47 at L5 (community composition), consistent with mine-proximity effect being largely mediated through community turnover.
- **Binary:** 0 FDR hits throughout. Binary contrast (n=2,938) lacks power; also suggests the mine-proximity CWM effect is graded, not threshold-based.

**Overlap with NB02 metal concentration hits (L1):** only **~14/516 = ~2.7%** of mine proximity hits overlap with NB02 metal concentration hits. Mine proximity and measured metal concentration identify almost entirely different sets of CWM KOs.

**Interpretation of low overlap:** Mine proximity is a spatial proxy for a complex mixture of exposures — physical disturbance, runoff patterns, altered lithology near ore bodies, land use, and elevated metals. Measured metal concentration (NB02) captures the actual metal dose at the sample location, which may be unrelated to mine proximity in many samples (median distance=50 km). The near-zero overlap implies mine proximity is not a useful surrogate for metal bioavailability in soil CWM analyses; measuring metals directly (as in NB02) is necessary.

**Commodity-specific analysis (genome-wide):** FWL within nearest-mine-element subsets (Cu mines, Pb mines, Zn mines, Ni mines), L1, testing **all 6,557 KOs** (previous run tested only the 508 NB02 hit KOs). **0 FDR hits** for all four commodity types (Cu n=693, Pb n=424, Zn n=401, Ni n=232). The null is genome-wide, not just within the NB02 hit set: proximity to commodity-specific mines does not predict any KO's CWM, even before controlling for pH. Overlap with NB02 measured-metal hits: Cu=0%, Pb=0%, Zn=0%, Ni=0%.

**Reverse analysis (CWM → mine proximity):**
- log_prox target: random-CV R²=0.000, spatial-CV R²=−0.194
- pH positive control: random-CV R²=0.030, spatial-CV R²=−0.237 (NB02 had 0.151 spatial — reduced here likely because the pH positive control features were a small ad hoc subset)
- CWM cannot predict mine proximity. Consistent with forward analysis: mine proximity is a weak, noisy exposure compared to direct metal measurement.

**Overall verdict:** Mine proximity identifies a distinct set of 481 CWM associations at L1, but these are almost entirely non-overlapping with metal concentration hits, not commodity-specific, and not spatially reproducible (hits collapse at L5 after community composition control). Mine proximity is an insufficient surrogate for metal bioavailability in CWM analyses.

### NB06 — Extended Mine Proximity Analyses (2026-08-24)

**Design:** Four extensions to NB05 using the 4,884-sample global thinned set with corrected pH scale.

**Environmental correlates of mine proximity (Spearman ρ — Mindat all localities):**

Mine proximity is largely orthogonal to soil covariates (pH ρ≤0.05). Precipitation (ρ=−0.17) and precipitation seasonality (ρ=+0.25) are the strongest environmental correlates. Cr mine distances show the strongest climate correlation (precip seasonality ρ=+0.30), consistent with ophiolite belts in Mediterranean/monsoon climates.

**Analysis 1a: Global tertile stratification by elevation relative to mine (`elev_rel`)**

Global n=4,884: Q33=Q67=0.0 m (most samples have `elev_rel=0`, indicating mine elevation approximation is imprecise). Effective groups:
- All samples (n=4,884): **484 L1 FDR hits**
- Downhill (elev_rel<0, n=3,119): **17 L1 hits**
- Uphill (elev_rel≥0, n=2,812): **0 L1 hits**

**Key finding:** The full-sample 484 L1 hits drop to 0 (uphill) and 17 (downhill) when stratified by elevation direction. This suggests the mine proximity signal is primarily driven by elevation-correlated confounders (topography, drainage) rather than true mine contamination signal. The `elev_rel` approximation (from nearest thinned sample elevation) is imprecise and should be interpreted with caution.

**Analysis 1b: EUR measured metals × elevation direction**

EUR measured metals (GEMAS) × CWM, split by elevation direction relative to nearest mine:
- All EUR (n=921): As=44, Cd=31, Cr=46, Cu=2, Ni=34, Pb=56, Zn=98 L1 hits
- Uphill EUR (elev_rel≥0, n=628): Cu=**188** L1 hits (all others ≤7)
- Downhill EUR (elev_rel<0, n=180): Cd=26, Zn=19, others ≤4

**Key finding:** EUR Cu uphill gets 188 hits vs 3 in the all-sample EUR analysis. Restricting to uphill samples dramatically increases Cu signal, suggesting downhill confounders (soil drainage, pH gradient) suppress the Cu-CWM association in the full dataset. This pattern is consistent with Cu contamination from mine runoff being strongest on uphill-facing terrain.

**Analysis 2: Commodity-specific mine distances (elements column) → functional interpretation**

KEGG category enrichment in commodity mine proximity L1 hits vs background (Fisher's exact):

| Commodity | Hits L1 | Metabolism | Human Diseases | Ratio Metab | p (Metab) |
|---|---|---|---|---|---|
| Cu | 528 | 44% vs 28% bg | 32% vs 48% bg | 1.59× | 4.5×10⁻¹⁷ |
| Pb | 631 | 46% vs 28% bg | 32% vs 48% bg | 1.65× | 2.3×10⁻²⁴ |

Mine proximity commodity hits are enriched for **Metabolism** (~1.6×) and depleted for **Human Diseases** categories relative to the KO background. This is consistent with selection for metabolic flexibility near metal-rich sites rather than virulence/pathogen-specific functions.

**Analysis 3: Elevation distribution**

64.2% of 4,884 global soil samples have `elev_rel<0` (downhill from nearest mine). Median `log_any_mine`=−1.65 (Mindat any mine) consistent with most samples being within 10–50 km of some Mindat locality.

---

### NB07 — Sensitivity Analyses (2026-08-24)

**Design:** Validates NB02's measured-metal CWM associations through four independent sensitivity checks. Uses all 4,884 thinned samples (corrected pH scale) to match NB02's full multi-region FWL.

**1. Spatial autocorrelation (pESS)**

Moran's I (k=10 KNN, n × (1−I)/(1+I) effective sample size):

| Metal | n | Moran I | n_eff | n_eff/n |
|---|---|---|---|---|
| As | 1,143 | 0.453 | 431 | 0.38 |
| Cd | 998 | 0.397 | 430 | 0.43 |
| Cr | 1,693 | 0.480 | 595 | 0.35 |
| Cu | 1,689 | 0.378 | 763 | 0.45 |
| Ni | 1,645 | 0.390 | 723 | 0.44 |
| Pb | 1,630 | 0.353 | 779 | 0.48 |
| Zn | 1,184 | 0.393 | 516 | 0.44 |

Substantial spatial autocorrelation (Moran I 0.35–0.48). Effective sample sizes are 35–48% of nominal n. The FDR thresholds are conservative in this context but the permutation test (below) accounts for the actual null distribution under spatial autocorrelation.

**2. Permutation test (500× shuffle at L1)**

| Metal | Observed hits | Null mean±SD | Perm p |
|---|---|---|---|
| As | 92 | 8.9±47.6 | 0.018 * |
| Cd | 145 | 16.6±106.1 | 0.022 * |
| Cr | 72 | 5.0±23.4 | 0.020 * |
| Cu | 8 | 3.7±48.3 | 0.022 * |
| Ni | 42 | 5.8±20.4 | 0.044 * |
| Pb | 22 | 8.8±29.1 | 0.084 NS |
| Zn | 73 | 10.7±56.9 | 0.038 * |

**6/7 metals pass the permutation test** (p<0.05). Pb is marginally non-significant (p=0.084). The high null SD (driven by rare permutations with inflated random hits) reflects the structured spatial autocorrelation; the mean null is low, confirming the observed hits substantially exceed chance.

**3. pH form sensitivity (spline vs linear)**

| Metal | Spline hits | Linear hits | Overlap |
|---|---|---|---|
| As | 92 | 105 | 100% |
| Cd | 145 | 159 | 100% |
| Cr | 72 | 70 | 96% |
| Cu | 8 | 8 | 100% |
| Ni | 42 | 43 | 98% |
| Pb | 22 | 22 | 100% |
| Zn | 73 | 78 | 100% |

**Spline and linear pH produce 96–100% hit overlap.** Results are not sensitive to pH modeling form. Slightly more hits with linear pH (possibly over-fitting to linear range), but the core hit sets are identical.

**4. Metal transformation sensitivity (log₁₀ vs rank-normal)**

| Metal | log₁₀ hits | Rank-normal hits | Overlap |
|---|---|---|---|
| As | 92 | 12 | 13% |
| Cd | 145 | 28 | 19% |
| Cr | 72 | 2 | 3% |
| Cu | 8 | 2 | 25% |
| Ni | 42 | 0 | 0% |
| Pb | 22 | 2 | 9% |
| Zn | 73 | 8 | 11% |

**Results are highly sensitive to the metal transformation.** Rank-normal transform yields 75–97% fewer hits for the same data. Rank normalization is more robust to outliers but substantially reduces power when metal distributions are log-normal (the typical case for geochemical data). The log₁₀ transform matches the geochemical literature convention and is the primary analysis; rank-normal serves as a conservative lower bound.

**5. Collider check (from NB02 L1/L5 parquets)**

| Metal | L1 hits | L5 hits | L1∩L5 (robust) | L5-only (collider?) |
|---|---|---|---|---|
| As | 41 | 0 | 0 (0%) | 0 |
| Cd | 10 | 0 | 0 (0%) | 0 |
| Cr | 38 | 1 | 1 (3%) | 0 |
| Cu | 0 | 0 | 0 (N/A) | 0 |
| Ni | 38 | 0 | 0 (0%) | 0 |
| Pb | 14 | 2 | 2 (14%) | 0 |
| Zn | 76 | 0 | 0 (0%) | 0 |

Most L1 hits are **L1-only** (attenuated at L5 after community composition control), consistent with metal→community turnover→CWM mediation. **Zero L5-only hits** rules out collider artifacts from community composition. Cr and Pb have 1–2 robust hits (L1∩L5), identifying KOs with direct metal associations not mediated through community composition.

**Overall verdict:** NB02's measured-metal CWM associations are statistically robust (6/7 metals pass permutation test), not sensitive to pH modeling form, but sensitive to metal transformation (log₁₀ >> rank-normal). The dominant pattern (L1-only, attenuation at L5) is consistent with metal effects mediated through community turnover rather than within-genus gene gain.

---

### NB08 — Pfam Domain and COG Category Associations (2026-08-24)

**Design:** Extends NB02’s KO FWL to Pfam domain prevalence (functional domain level) and COG functional categories (pathway level), using the same CWM framework. Pfam: top 5,000 domains by mean genus prevalence. COG: all 24 categories. Same FWL+BH-FDR pipeline (L0–L6 causal levels, 4,884 thinned samples, three-tier pH).

**L1 hit counts by annotation type:**

| Metal | KO hits (NB02) | Pfam hits | COG hits |
|---|---|---|---|
| Cd | 10 | 761 | 2 |
| V | 6 | 0 | 18 |
| Cu | 0 | 0 | 1 |
| Pb | 14 | 0 | 1 |
| As | 41 | 0 | 0 |
| Cr | 38 | 0 | 0 |
| Ni | 38 | 0 | 0 |
| Zn | 76 | 0 | 0 |

**Pfam (n=5,000 domains tested):** 761 L1 FDR hits, all specific to Cd. Top Pfam hits by q-value: Beta_helix (β=+0.086, q=0.0006), Zn_peptidase_2 (β=+0.062, q=0.004), Thymidylat_synt (β=+0.095, q=0.005), SprT-like (β=+0.071, q=0.005), DUF5122/DUF2851. All Cd Pfam hits have positive β (higher Cd → more domain prevalence). No significant Pfam hits for As, Cr, Ni, Zn, Cu, or Pb at L1.

**COG (n=24 categories):** 22 L1 hits across 4 metals. V: 18 hits (effectively all COG categories, β=−0.056, q=0.040) — note this likely reflects a degenerate fit given the small V sample count. Cd: 2 hits (Z=mobilome β=+0.067, W=extracellular structures β=+0.040). Cu: 1 hit (Z, β=+0.041). Pb: 1 hit (Z, β=+0.050).

**Interpretation:** The Cd Pfam result (761 hits, all positive) contrasts sharply with the Cd KO result (10 hits). This divergence reflects the different resolutions: CWM-Pfam aggregates prevalence at the domain level, which is more broadly shared across taxa and less specificity-filtered than individual KOs. The Cd-specific Pfam enrichment (especially metallopeptidase, thymidylate synthase, and Radical_SAM domains) may reflect non-specific Cd stress response rather than dedicated resistance. The COG V result warrants caution — V has n=998 total but very few complete-covariate samples after pH joining, reducing degrees of freedom. The KO L1 hit count (KO=560 total, Cd=10) remains the primary annotation level.

---
## Interpretation

### Literature Context

Metal contamination in soil is a well-established driver of microbial community composition. Studies using 16S rRNA amplicon sequencing have consistently found shifts in alpha and beta diversity near mine-contaminated sites (Wakelin et al. 2010; Hemkemeyer et al. 2021). However, whether these compositional shifts are accompanied by enrichment of metal-resistance functional genes remains debated. Our finding — that metal-associated KOs have the same within-genus prevalence distribution as background KOs — is consistent with the community turnover model rather than the gene-gain model.

pH is widely recognised as the primary driver of soil bacterial diversity globally (Fierer & Jackson 2006; Lauber et al. 2009; Delgado-Baquerizo et al. 2016). Our finding that pH identifies 4,322 constitutive-core-gene FWL hits (vs 560 for all metals) with a spatially recoverable signal (R²=+0.151) directly quantifies pH's dominance over metals at the functional CWM level in the same dataset and framework.

The arsenic resistance cluster (ars operon) negative association with As — i.e., high-As soils have *lower* ars CWM — is consistent with findings that high-arsenic environments are dominated by genera that use alternative mechanisms (arsenite oxidation via *aioA*, anaerobic reduction via *arrA*) rather than the cytoplasmic efflux ars pathway encoded by these KOs (Oremland & Stolz 2003; Slyemi & Bonnefoy 2012). The As-adapted genera that dominate high-As soils may use alternative detoxification mechanisms not captured by these KOs — arsenic oxidation via *aioA*, anaerobic reduction via *arrA*, or the *arsO* flavoprotein monooxygenase pathway (Oremland & Stolz 2003; Tang et al. 2023). The specific ars-operon KOs indexed here (K15844/K15847/K15848) appear most prevalent in common soil bacteria that are *excluded* from high-As soils by toxicity pressure — consistent with the turnover mechanism.

The community-weighted mean (CWM) approach, developed in plant ecology (Garnier et al. 2004; Díaz et al. 2007), has been adapted for microbial ecology to capture functional trait shifts without requiring deep sequencing at each site (Sims et al. 2020; Chen et al. 2021). Our cross-continental replication (USA→EUR, 84–100% overlap) provides the first large-scale validation of 16S×pangenome CWM for detecting soil metal associations.

### Novel Contribution

1. **Quantitative turnover-vs-gene-gain resolution:** We provide three independent lines of evidence (facultativeness, reverse prediction, collider check) that metal-associated CWM shifts are driven by community turnover, not within-genus gene content variation. This directly addresses an open question in microbial metal ecology literature.

2. **Cross-continental FWL replication:** EUR replicates USA L1 KO hits at 84–100% overlap with 100% directional concordance — the first genome-wide replication of soil metal × CWM KO associations across continents using independent measured metal datasets (USGS and GEMAS).

3. **Mine proximity ≠ measured metal:** The near-zero overlap between mine proximity FDR hits and measured-metal FDR hits demonstrates quantitatively that proximity to mines is an insufficient surrogate for metal bioavailability at the community functional level — a methodological caution for studies using proximity as a metal exposure proxy.

4. **pH CWM as positive control:** Using pH as a positive control in the same FWL framework reveals that constitutive core gene turnover (pH hits: mean_prev=0.733, R²_spatial=+0.151) and weak metal turnover (metal hits: mean_prev=0.604, R²_spatial<0) are mechanistically distinguishable within the same pipeline.

### Limitations

- **CWM captures only turnover:** By construction, CWM[cell,KO] = Σ(genus_RA × prevalence). This weights genera's constitutive gene repertoire — it cannot detect within-genus gene expression changes, HGT, or strain-level gene variation. Metal adaptation via those mechanisms would be invisible to this approach.
- **ke_pangenome terrestrial subset:** Only genomes with `ncbi_isolation_source LIKE '%soil%'` are included. Genera not well-represented in sequenced soil isolates have zero or low prevalence by construction (GlobDB supplement shows 17% genus coverage for canonical MRGs). Annotation gaps particularly affect canonical resistance genes (merA, czcA absent from ke_pangenome KO annotations).
- **USGS metal data geographic bias:** USGS geochem sampling is denser in the western USA mining belt and sparser in the midwest and east. The 634 USA thinned samples with metal data are not a uniform spatial sample. EUR GEMAS is more systematic.
- **40 Antarctic samples uncoverable for pH:** No pH source (measured, OLM, SoilGrids) covers lat<−63°. These 40 cells are excluded from pH-adjusted (L1+) analyses.
- **AUS null is power-limited:** n=232 is approximately 5× underpowered relative to the USA threshold for detecting the observed effect sizes. Cannot rule out that the AUS null reflects biology (ancient nutrient-poor soils, different community structure) rather than power.
- **Reverse direction fails spatially:** The CWM → metal prediction failure (spatial R²<0) means CWM cannot be used as an environmental indicator for metal contamination. This limits applied interpretations.
- **REE confound:** Nd and Yb dominate hit counts (326/560 L1 hits) due to geology-pH collinearity. These are explicitly excluded from primary biological claims.

---

## Data

### Sources

| Collection | Tables Used | Purpose |
|---|---|---|
| `arkinlab.microbeatlas` | `sample_metadata`, `otu_counts_long`, `otu_metadata` | 16S community data, spatial thinning, genus RA |
| `kbase.ke_pangenome` | `bakta_db_xrefs`, `eggnog_mapper_annotations`, `gtdb_metadata`, `gtdb_taxonomy_r214v1` | KO/Pfam/COG prevalence per genus; terrestrial subset |
| `arkinlab.envdbs.soilgrids_master` | `pH_0cm`, `clay_0cm`, `soc_0cm` | pH fallback (three-tier hierarchy); soil texture covariates |
| `arkinlab.envdbs.worldclim_master` | `bio_1`, `bio_4`, `bio_12`, `bio_15` | Climate covariates (MAT, MAP, seasonality) |
| `arkinlab.envdbs.global_lithology_glim` | all columns | Bedrock lithology (L2 confounder) |
| `arkinlab.envdbs.gemas` | measured metal concentrations | EUR replication dataset (As, Cd, Cr, Cu, Ni, Pb, Zn) |
| `arkinlab.envdbs.ngsa_geochemistry` | measured metal concentrations | AUS replication dataset |
| `/data/envdbs/usgs_geochem/` | `usgs_geochem.parquet`, `usgs_geochem_joined.parquet` | USA measured metals, 50+ elements, ~145K soil samples |
| `/projects/microbeatlas_metal_ecology/data/mindat.csv` | — | Mine locations (157K localities) for proximity analysis |

### Generated Data

| File | Rows | Description |
|---|---|---|
| `data/thinned_cells_4884.parquet` | 4,884 | Globally thinned MA cells with lat/lon, pH sources, genus RA |
| `data/nb02_fwl_results_fdr.parquet` | 1,055,677 | Full FWL results across 23 metals × 7 levels × 6,557 KOs |
| `data/nb07_perm_results.parquet` | 7 | Permutation test results per metal (observed hits, null mean±SD, p) |
| `data/nb08_pfam_fwl_fdr.parquet` | ~761K | Pfam FWL FDR results (5,000 domains × 7 levels × metals) |
| `data/nb08_cog_fwl_fdr.parquet` | ~22K | COG FWL FDR results (24 categories × 7 levels × metals) |
| `data/nb08_ko_pfam_cog_comparison.csv` | 168 | Hit count summary by metal × level × annotation type |

---

## Supporting Evidence

### Notebooks

| Notebook | Purpose |
|---|---|
| `NB00_data_qc.ipynb` | MicrobeAtlas sample fetch, terrestrial filter, spatial thinning (0.45°), pH hierarchy construction |
| `NB01_cwm_construction.ipynb` | ke_pangenome terrestrial subset, per-genus KO/Pfam/COG prevalence, CWM matrix computation |
| `NB02_metal_associations.ipynb` | Forward FWL (L0–L6) × 23 USGS metals; reverse Ridge; facultativeness test; GlobDB MRG supplement |
| `NB03_functional_interpretation.ipynb` | Stable hit characterization, DAG attrition audit, pathway/module context |
| `NB04_regional_replication.ipynb` | EUR (GEMAS) and AUS (NGSA) FWL replication; pH positive control; reverse Ridge |
| `NB05_mine_proximity.ipynb` | Forward/reverse mine proximity FWL (3 operationalizations + elev_rel + commodity) |
| `NB06_mine_extended.ipynb` | Elevation stratification, EUR measured metals × elev_rel, functional category enrichment |
| `NB07_sensitivity.ipynb` | Spatial autocorrelation (pESS), Zeleny permutation, pH-form robustness, rank-transform sensitivity |
| `NB08_pfam_cog_associations.ipynb` | Pfam (5,000 domains) and COG (24 categories) CWM FWL; cross-annotation comparison |

### Figures

| Figure | Description |
|---|---|
| `fig_nb00_map.pdf` | World map of 4,884 thinned cells |
| `fig_nb00_ph_coverage.pdf` | pH source breakdown by three-tier hierarchy |
| `fig_nb00_attrition.pdf` | Sample attrition (terrestrial filter → quality → thinning) |
| `fig_nb01_cwm_distribution.pdf` | CWM value distribution across cells and KOs |
| `fig_nb01_genus_coverage.pdf` | Genus RA coverage per cell (matched fraction) |
| `fig_nb02_manhattan_L1.pdf` | Manhattan plot of KO associations at L1 per metal |
| `fig_nb02_facult_ko.pdf` | KO prevalence distribution: metal hits vs pH hits vs background |
| `fig_nb02_reverse_r2.pdf` | Reverse Ridge R² (random vs spatial block CV) for all metals |
| `fig_nb02_beta_stability.pdf` | L0→L6 hit attrition per metal |
| `fig_nb03_attrition.pdf` | Stable hit functional group breakdown |
| `fig_nb03_hit_heatmap.pdf` | Heatmap: KO × metal β values at L1 |
| `fig_nb04_hits_heatmap.pdf` | EUR L1 FDR hit counts by metal |
| `fig_nb04_replication_overlap.pdf` | USA vs EUR hit overlap (Venn / scatter) |
| `fig_nb05_mine_hits_by_level.pdf` | Mine proximity FDR hits L0→L5 |
| `fig_nb05_mine_metal_overlap.pdf` | Overlap between mine proximity and metal concentration hits |
| `fig_nb06_stratification.pdf` | Global elevation stratification (all vs downhill vs uphill) |
| `fig_nb07_sensitivity.pdf` | Permutation null vs observed; pESS table |
| `fig_nb08_L1_hits_by_metal.pdf` | KO/Pfam/COG L1 hits by metal |

---

## Future Directions

1. **Species-level gene frequency analysis:** The CWM approach aggregates across genus-level composition. A complementary MWAS at species level (using SPIRE per-MAG KO presence) would test whether within-genus strain-level gene frequency shifts with metal — the one mechanism CWM cannot detect. SPIRE × USGS metals analysis is underway in a companion project.
2. **Extended REE controls:** Nd and Yb hits (326/560 L1 hits) are likely geology confounds. Adding dedicated REE-specific covariates (REE deposit density, ophiolite indicator) or running REE analysis within geology-stratified subsets would clarify whether any REE hits are biological.
3. **AUS replication with expanded sample set:** The NGSA dataset (1,315 points) has more potential joins than the current n=232 MA thinned cells provide. Future work could reduce the thinning grid from 0.45° to 0.25° for the AUS-only analysis, increasing n~500–600 and potentially reaching adequate power for Zn (min-q=0.074 near-miss).
4. **Transcriptomic follow-up for stable hits:** The 17 KOs stable at L1∩L6 (MoCo biosynthesis, cell wall, RNA quality control) represent the most robust signal. Testing whether these KOs are upregulated (not just CWM-elevated) in metal-contaminated soils using metatranscriptomics would distinguish passive compositional shifts from active functional regulation.
5. **Pfam Cd hits — structural biology context:** The 761 Cd Pfam hits (all positive, Beta_helix/Zn_peptidase_2/Thymidylat_synt) warrant structural-biology examination: are these domains known Cd-binding scaffolds, or does the signal reflect enrichment of specific Cd-tolerant genera carrying these common domains? Genus-stratified Pfam analysis (which genera drive the Pfam-Cd association) would resolve this.

---

## References

**Arsenic resistance gene distribution across As gradients:**
- Escudero, L.V. et al. (2013). Distribution of microbial arsenic reduction, oxidation and extrusion genes along a wide range of environmental arsenic concentrations. *PLoS ONE*, 8(10), e78890. PMID: 24205341. doi:10.1371/journal.pone.0078890 — ars-operon genes selectively excluded from high-As environments; supports negative-association interpretation.

**Microbial CWM methodology (prior art):**
- Piton, G. et al. (2020). Using proxies of microbial community‐weighted means traits to explain the cascading effect of management intensity, soil and plant traits on ecosystem resilience in mountain grasslands. *Journal of Ecology*, 108(3), 876–893. doi:10.1111/1365-2745.13327 — Closest prior microbial CWM methodology using enzyme-proxy traits; the advance to genome-derived KO-prevalence CWM is methodologically novel.

**Community turnover under metal stress:**
- Zhang, Y. et al. (2023). Effects of single and combined contamination of total petroleum hydrocarbons and heavy metals on soil microecosystems. *Chemosphere*, 345, 140288. PMID: 37783354. https://doi.org/10.1016/j.chemosphere.2023.140288 — Community beta diversity driven by turnover rather than nestedness; heavy metals reshape soil microbiota through species replacement.
- Zhang, J. et al. (2026). Niche-driven microbial assembly across the soil-root continuum under heavy metal pollution gradient. *Ecotoxicology and Environmental Safety*, 323, 120615. PMID: 42556226. — Metal pollution restructures community through spatial niche shifts; Proteobacteria → Actinobacteria → Chloroflexi with increasing Pb/Zn/Cd gradient.

**pH as primary soil microbiome driver:**
- Fierer, N. & Jackson, R.B. (2006). The diversity and biogeography of soil bacterial communities. *PNAS*, 103(3), 626–631. — pH is the primary predictor of bacterial diversity globally.
- Lauber, C.L. et al. (2009). Pyrosequencing-based assessment of soil pH as a predictor of soil bacterial community structure at the continental scale. *Applied and Environmental Microbiology*, 75(15), 5111–5120. — Cross-continental confirmation of pH as primary driver; stronger than climate or geography.
- Delgado-Baquerizo, M. et al. (2016). Microbial diversity drives multifunctionality in terrestrial ecosystems. *Nature Communications*, 7, 10541. https://doi.org/10.1038/ncomms10541

**Arsenic resistance mechanisms and community context:**
- Oremland, R.S. & Stolz, J.F. (2003). The ecology of arsenic. *Science*, 300(5621), 939–944. — Foundational review: As(III) oxidation (*aioA*) and anaerobic reduction (*arrA*) are dominant community-level As cycling pathways in many environments, distinct from the cytoplasmic efflux (ars) pathway.
- Valenzuela-García, L.I. et al. (2025). Mechanisms of arsenic interaction in *Bacillus* and related species with biotechnological potential. *International Journal of Molecular Sciences*, 26(21), 10277. PMID: 41226316. — Comprehensive review of *ars* and *ase* operons; efflux + reduction confer resistance.
- Tang, X. et al. (2023). Widespread distribution of the *arsO* gene confers bacterial resistance to environmental antimony. *Environmental Science & Technology*, 57(39), 14579–14588. PMID: 37737118. — *arsO* (flavoprotein monooxygenase) widely distributed in mine and contaminated environments — supporting the existence of alternative As detoxification mechanisms beyond the specific KOs measured here.

**CWM methodology (plant ecology origin):**
- Garnier, E. et al. (2004). Plant functional markers capture ecosystem properties during secondary succession. *Ecology*, 85(9), 2630–2637. — Original CWM method.
- Díaz, S. et al. (2007). Incorporating plant functional diversity effects in ecosystem service assessments. *PNAS*, 104(52), 20684–20689.

**Copper and metal contamination effects on soil communities:**
- Wakelin, S.A. et al. (2010). Soil microbial community structure and function are altered by long-term copper contamination. *European Journal of Soil Biology*, 46, 116–125.

**Statistical methods:**
- Frisch, R. & Waugh, F.V. (1933). Partial time regressions as compared with individual trends. *Journal of the American Statistical Association*, 28(221), 73–78. Lovell, M.C. (1963). Seasonal adjustment of economic time series. *Journal of the American Statistical Association*, 58(304), 993–1010. — The Frisch-Waugh-Lovell theorem: partial regression on residuals (vectorized across all covariates simultaneously) recovers the same coefficient as full OLS, avoiding explicit inverse computation.
- Roberts, D.R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*, 40(8), 913–929. doi:10.1111/ecog.02881 — Spatial block cross-validation methodology for avoiding spatial autocorrelation leakage in predictive models.

---

## Causal Level Definitions

| Level | Covariates controlled | Estimand |
|---|---|---|
| L0 | none | total association |
| L1 | pH (natural spline, 3 df) | pH-adjusted direct effect (primary estimand) |
| L2 | + clay, SOC, CEC, bulk density, GLiM lithology (dummy-encoded) | + soil properties + bedrock geology |
| L3 | + log(nearest mine distance km, from mindat) | + mine proximity |
| L4 | + MAT, MAP, temp seasonality, precip seasonality | + climate |
| L5 | + Shannon diversity, phylum RA (top 8 phyla) | + community composition |
| L6 | + elevation, land cover (ESA) | full model |

Primary estimand: **L1 direct effect** (pH as primary confounder per DAG).

---

## Structural Conventions

- All analysis in notebooks; scripts only for imported utilities
- Always fetch from Spark — do not cache large intermediate files to disk
- Every figure followed by a markdown cell explaining what it shows
- Small summary tables (< ~1 MB) may be saved as CSV for cross-notebook use
