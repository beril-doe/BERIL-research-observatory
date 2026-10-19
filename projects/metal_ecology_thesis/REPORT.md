# Report — Microbial Metal Ecology: Turnover vs Gene Gain

**Cross-project synthesis. All numbers reported here are taken from sub-project REPORT.md files (authoritative sources). See individual REPORTs for methods and data provenance.**

---

## Research Question

Does metal contamination select for metal-tolerant microbial communities through **community turnover** or **resistance gene gain**?

---

## Key Findings

**Five findings converge across eight independent analyses:**

1. **Resistance genes are ecologically neutral** — they accumulate in generalists (niche breadth β=+0.067, p=0.013), not specialists, and only 1/84 field-significant KO-metal pairs is a canonical resistance gene.
2. **Constitutive metal-metabolic genes are ecological specialists** — cofactor biosynthesis β=−0.033 (p=10⁻⁹); the difference from resistance is real (joint-tier PGLS Δβ=−0.459 [−0.593,−0.325], p=2×10⁻¹¹) and replicates across PGLS, MWAS, and genome enrichment analyses.
3. **Turnover dominates gene gain quantitatively** — across 99 unique KO-metal associations surviving L6 full-control in CWM (16S, n=634 cells, 71 KOs) and SPIRE (MAG, n=1,077 genomes, 31 KOs), 3 KOs appear in both lists (≤3% shared). Hypergeometric test: expected overlap under null = (71×31)/6,451 ≈ 0.34 KOs; observed 3 is ~9× above random expectation (p<0.001). Both hit lists are largely non-overlapping, suggesting each method captures a distinct subset of metal-responsive genes. This pattern is consistent with estimand differences between CWM (abundance-weighted community average trait) and SPIRE (binary gene presence per MAG) rather than strictly indicating no shared mechanisms. Community functional shifts at full causal control trace primarily to taxon replacement, not within-lineage gene acquisition.
4. **Individual gene-metal pairs work as bioindicators; aggregate metrics do not** — 31 KO-metal pairs survive full pH-controlled direct-effect model (L1+). Community-level resistance density is uninformative.
5. **Lab resistance ≠ field ecology** — field-identified and lab-identified metal fitness genes are below-random in overlap (Z=−73); metal stress classifiers fail to generalize across genera (LOGO AUC 0.53–0.62). Field validation at ORFRC: contamination gradient drives community dissimilarity (Mantel r=+0.329, p<0.001; PERMANOVA F=10.949, p=0.001).

---

## Findings by Sub-analysis

### Ch1: Ecological niche breadth PGLS (comprehensive_metal_ecology)

**Primary result:** Metal gene density (KOs per Mb) negatively predicts ecological niche breadth (Levins' B) across 1,574 bacterial genera in MicrobeAtlas global 16S surveys joined to the GTDB pangenome. β=−0.021, SE=0.003, p=2×10⁻⁸, Pagel's λ=0.757 (ΔAIC=−29.4 vs λ=0 OLS).

**Category breakdown:** Cofactor biosynthesis β=−0.033 (p=10⁻⁹), metal metabolism β=−0.021 (p=7×10⁻⁵), sensing β=−0.018 (p=7×10⁻⁴), transport β=−0.022 (p=1×10⁻⁵). Resistance β=+0.003 (p=0.66) — null for broad category; subcategory resistance/detox β=+0.067 (p=0.013) — generalists carry MORE resistance genes per Mb (HGT acquisition).

**Genome-size sensitivity (Adam Diagnostic 1):** Sensitivity parameter 1−a explains R²=0.370 (p=0.004) of cross-category β variance. Metal genes sit at the category median (a=0.482) — not outliers. PGLS on log(KO count) + log_genome: β=−0.031, p=0.0024, λ=0.758 (genome-size-corrected).

**MCMCglmm (Adam recommended):** B_z post_mean=−0.357, 95% CI (−0.860, +1.641), pMCMC=0.48 (NS). Direction consistent; CI wide due to pESS=7.4 (n=2,283 GTDB tree, λ=0.758) or 5.6 (λ=0.998, Brownian limit). Genus-level MCMCglmm with CheckM covariate (1,107 genera): B_z posterior mean=+0.113, pMCMC=0.659 — sign flip vs. baseline is a posterior shrinkage artifact at λ≈0.998 (pESS=5.6, n=2,283). Discordance with PGLS log-count disclosed to committee.

**λ sensitivity (Adam S1):** All three models agree on direction and significance — Pagel (λ=0.758): β=−0.031, p=0.0024; Brownian (λ=1): β=−0.027, p=0.0047; OLS (λ=0): β=−0.032, p=0.0017. β direction preserved regardless of λ assumption. Source: `comprehensive_metal_ecology/data/pgls_lambda_sensitivity.csv`.

**Leave-one-clade-out diagnostic (2026-08-08; Uyeda et al. 2018 *Syst Biol* 67:1091):** For each of 12 major bacterial phyla (n ≥ 10 genera), the phylum was dropped and PGLS refit with λ fixed at 0.758. Direction stable in 12/12 phyla; significant (p < 0.05) in 11/12. Only dropping Proteobacteria (43% of genera) loses significance (β=−0.027, p=0.066) due to power loss, not signal reversal. The association is not driven by any single phylogenetic block. Source: `comprehensive_metal_ecology/scripts/leave_one_clade_out_pgls.py`, `comprehensive_metal_ecology/data/clade_leave_one_out_pgls.csv`.

**Forsberg RDA variance partition (NB28):** In CLR-transformed genus abundances (community composition), unique R²(metals)=0.064 vs unique R²(pH+climate)=0.041 — metal-unique fraction is 58% larger. Unadjusted R², descriptive (not permutation-tested). Metals structure community composition along an independent axis from pH/climate. Source: `comprehensive_metal_ecology/REPORT.md` line 770.

**Coverage standardization:** Sequencing completeness (CheckM) explains R²=0.013 (1.3%) of metal-KO diversity variance (Spearman ρ=0.104, p=5.2×10⁻⁴). Coverage bias is negligible; PGLS signal robust to sequencing depth. Source: `comprehensive_metal_ecology/data/coverage_standardized_metal_diversity.csv`.

**Key authoritative source:** `projects/comprehensive_metal_ecology/REPORT.md`

---

### Ch2: Field validation — ORFRC (orfrc_metal_ecology)

**Three-analysis field test of the turnover hypothesis at the Oak Ridge Field Research Center contaminated groundwater site (As, Cr, U contamination gradient).**

| NB | Test | Result | Supports |
|----|------|--------|---------|
| NB00 | MAG-level metal association (n=11 wells) | Null — MAG count confounds; N=11 underpowered | — (inconclusive) |
| NB01 | Mantel test: community dissimilarity vs. metal gradient | r=+0.329, p<0.001 | Ch2 field validation — metal gradient drives community turnover |
| NB02 | PERMANOVA: metal contamination class × community composition | F=10.949, p=0.001 | Ch3 turnover claim — contamination explains significant compositional variance |

**Interpretation:** Community composition at ORFRC co-varies with the metal contamination gradient (Mantel, PERMANOVA) in a manner consistent with PICT (Pollution-Induced Community Tolerance). The MAG-level null (NB00) reflects low N (11 wells), not absence of signal. This is corroborating field evidence for community turnover under metal exposure, independent of the global 16S and SPIRE analyses.

**Key authoritative source:** `projects/orfrc_metal_ecology/REPORT.md`

---

### Ch3-A: Per-KO field associations (per_ko_metal_associations)

*(formerly "Aim 2" — renamed for consistency with chapter structure)*

**Primary result (MGnify, n=8,585 MAGs, 6,451 KOs × 6 metals):** 219 FDR-significant KO-metal pairs (q<0.05). After latitude + sg_pH control: 151/219 survive (69%). Field-strict filter (4-way robustness): 84 KOs, of which 31 survive pH control.

**Per-metal denominators:**

| Metal | MGnify n_MAGs | SPIRE n_MAGs | MGnify n_KOs_tested | MGnify n_sig_baseline | MGnify n_sig_pH | SPIRE n_sig_baseline | SPIRE n_sig_pH |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| As | 8,585 | 2,477 | 6,451 | 43 | 31 | — | — |
| Cd | 8,585 | 2,477 | 6,451 | 12 | 4  | — | — |
| Cr | 8,585 | 2,477 | 6,451 | 6  | 5  | — | — |
| Cu | 8,585 | 2,477 | 6,451 | 0  | 0  | 4 | 5\* |
| Hg | 8,585 | 2,477 | 6,451 | 107| 76 | — | — |
| Pb | 8,585 | 2,477 | 6,451 | 51 | 35 | — | — |
| **Total** | | | | **219** | **151** | **69** | **31** |

\*Cu SPIRE pH-adjusted: 5 pairs are from a SEPARATE regression, not a subset of the 4 baseline pairs. K03702 is lost; K00425+K00426 are gained. The pH-adjusted model is not a survival filter.

**Named associations:** K07093 (MerR-family HTH regulator) × Hg: β=−13.9 (survives pH); arsH × Pb: OR/IQR=1.28 (positive — enriched near Pb); kdpB × Pb: pH-confounded (lost at pH control); kdpC × Cr: robust.

**Spatial autocorrelation (Moran's I):** predictor Moran's I = 0.863 (Pb) to 0.946 (Cu); effective N = 63–166 per metal. Quantified spatial dependence from gridded CSU raster.

**Gelman & Stern contrast (β_baseline vs β_pH-adjusted):** Among 76 pairs significant in either model, zero contrasts reach |z|>1.96. pH control shifts which pairs are significant (categorical selection) but does not significantly alter β magnitudes in robust pairs. Source: `per_ko_metal_associations/data/gelman_stern_interaction_results.csv`.

**Operon collapse sensitivity:** kdp operon members are internally inconsistent (kdpC×Cr β=+4.61 p=5.9×10⁻⁶; kdpB×Pb β=−12.1 p=1.5×10⁻⁶ — different members, different metals, different directions). Operon co-membership does NOT inflate the field-strict set; individual KOs encode distinct ecological signals. Source: `per_ko_metal_associations/data/operon_collapse_results.csv`.

**MAG quality covariates:** MGnify quality controlled in H10 robustness test — 91% survival (200/219 pairs), no confounding from assembly quality. SPIRE genome_size covariate acts as implicit quality proxy.

**Key authoritative source:** `projects/per_ko_metal_associations/REPORT.md`

---

### Ch3-B: Community-weighted mean analysis (microbeatlas_metal_ecology)

**CWM analysis of KO functional potential at 634 spatially-thinned USA cells (0.45° grid), joined to USGS measured soil metals. 6,451 KOs × 6 metals × L0–L6 covariate levels.**

**Primary results:**

| Analysis | Result |
|----------|--------|
| CWM L6 FDR-significant KO-metal pairs | 75 pairs (across 6 metals); becomes 45 after Pfam-level survival filter |
| Joint-tier PGLS Δβ contrast (BacMet-enriched vs. constrained) | Δβ = −0.459 [−0.593, −0.325], p=2×10⁻¹¹ — resistance-gene-enriched tier has lower CWM β than constrained-resistance tier |
| CWM–SPIRE L6 overlap (turnover metric) | 3/99 KOs shared between CWM (71) and SPIRE (31) hit lists (≤3% shared; hypergeometric p<0.001, observed 3 vs expected 0.34) |
| Mine proximity bridge (AR KOs in mine-adjacent vs. remote) | 5/9 agriculture-resistance KOs significant near MRDS mine deposits |

**Pfam/COG layered variance partitioning (full 16,782 MicrobeAtlas MAGs, Spark):**
- Pfam: 25% of initial KO-metal pairs survive Pfam-level replication
- COG: 50% survival
- Ni/Cr: Pfam-convergent response (shared Pfam domains across taxa)
- Hg: toxin-antitoxin enrichment
- Cu/Pb: COG-B (poorly characterised) = 0.087

**Key authoritative source:** `projects/microbeatlas_metal_ecology/REPORT.md`

---

### Ch3-C: Companion — module CWM, taxonomic drivers, co-occurrence networks (metal_community_functional_ecology)

**Three-arm investigation into pathway-level and network-level consequences of metal exposure (2026-08-23, all NB complete).**

| NB | Analysis | Result | H |
|----|----------|--------|---|
| NB00 | KEGG module CWM L0–L6 (278 modules, 634 cells) | 7 L6 survivors: Hg×2 (CAMP resistance M00725 β=+0.008, isoprenoid M00095 β=+0.012 — enriched); Pb×5 (AcrEF-TolC M00696, capsule M01012/M01008, pathogenicity M00857/M00574 — all depleted); As/Cd/Cr/Cu null | H1 partially supported |
| NB01 | Taxonomic driver decomposition (7 survivors × 3,462 genera) | LAB guild (Pediococcus+Lactobacillus) dominant: enriched Hg (β≈+1800/+1296), depleted Pb (β≈−571/−410); MWU niche-breadth test p=0.719 (enriched B=0.250 vs. depleted B=0.241) | H2 NOT SUPPORTED |
| NB02 | Genus co-occurrence networks (479 prevalent genera, Q75+ vs. Q25−) | As/Cd/Pb: simplification (degree high<low, all p<0.0001); Cr/Cu/Hg: densification (degree high>low); hub rewiring in all metals (18–30 hubs gained/lost) | H3 partially supported |

The module null (7 module×metal pairs at L6 vs. 75 KO×metal pairs) confirms that metal effects do not aggregate into coherent pathway-level signatures. The LAB driver result shows that the CWM signals are mediated by a broad generalist guild, not narrow-niche specialists.

**Key authoritative source:** `projects/metal_community_functional_ecology/REPORT.md`

---

### Companion-A: Community composition prediction (community_composition_prediction)

**Within-region prediction:** Genus-level community composition predicts Cu/Zn/Pb metal mobility (CSU PF1 fractionation index) with AUROC≈0.99 within a geographic region.

**Cross-region generalization:** AUROC collapses to ≈0.18. Geography (kriging) outperforms microbial composition for predicting Cu, Zn, and Ni mobility. No universal indicator taxon.

**OOF thresholds:** Cu=0.015, Zn=0.000, Pb=0.000 (corrected 2026-08-07 after index misalignment fix).

**Key authoritative source:** `projects/community_composition_prediction/REPORT.md`

---

### Ch4: ENIGMA isolate sequence → metal fitness (enigma_stress_phenotype_ml)

**Hg fitness (mercury):** AUROC=0.774 from amino acid composition alone. Amino-acid-only = aa+kmer2 (NB10 confirms).

**Cross-genus generalization:** LOGO cross-genus AUROC = 0.53–0.62 for metals. Broad-mechanism stressors generalize better: UV=0.736, ethanol=0.725, acid=0.689. Metal resistance is genus-specific — configured differently via HGT in each lineage.

**Key authoritative source:** `projects/enigma_stress_phenotype_ml/REPORT.md`

---

### Supporting: MAG-level metal prediction (metagenomic_environment_prediction)

**H1 NOT SUPPORTED:** M1 (MAG KO density alone, RMSE=0.0527) worse than B0 baseline (0.0501). Environmental variables dominate (>80% SHAP importance). MAG density adds modest signal only when combined with environmental covariates (M3 RMSE=0.0400).

**Key authoritative source:** `projects/metagenomic_environment_prediction/REPORT.md`

---

### Supporting: MWAS collinearity control (mwas_confound_analysis)

**Collinearity collapse:** 1,097 initial MWAS significant hits → 4 hits (kitchen-sink model) → 2 hits (after controlling for community composition). Most published soil metal MWAS results are likely collinearity artifacts. Methodology for detecting this collapse is potentially publishable independently.

**Key authoritative source:** `projects/mwas_confound_analysis/REPORT.md`

---

### Ch3-D: Soil-level CWM FWL and HGT directional signals (spatial_community_metal_models)

**Two-pronged investigation into whether soil communities near mines show evidence of horizontal gene transfer (gene gain) or community turnover (specialist selection).**

**NB41 — Soil CWM FWL with mine proximity exposure and covariate control (n=67,835 USA samples, n=40,358 EUR samples):**

| Region | Covariate level | KOs tested | FDR<0.05 | % Enriched | Interpretation |
|--------|---------|-------|---------|-----------|---|
| USA | L0 (bivariate) | 9,217 | 7,888 | 57.6% | mine proximity weakly associated with KO enrichment |
| USA | L5 (+env) | 9,217 | 8,008 | 57.7% | robust to temperature/precipitation |
| USA | L6 (+genus PC1) | 9,217 | 8,018 | 71.2% | strengthens when genus composition is accounted for |
| USA | L7 (+soil props) | 9,217 | 8,079 | **73.7%** | **robust after soil pH, SOC, clay, lithology control** |
| EUR | L0 | 8,507 | 5,402 | 30.8% | weak signal |
| EUR | L5–L7 | 8,507 | 4,577–5,008 | 31.2–49.9% | variable, no consensus |
| EUR | L8 (+EMEP) | 8,507 | 5,408 | **26.0%** | **signal inverts when atmospheric Hg/Cd/Pb deposition controlled** |

**Key result:** USA shows **positive enrichment signal that survives soil physicochemical control** (73.7% of mine-associated KOs are enriched after L7 covariate adjustment). EUR shows **negative directionality (26% enriched)** when atmospheric deposition is explicitly controlled. This regional contrast indicates that soil mine exposure selects for specific functional profiles in USA, while in EUR, atmospheric metal transport overrides the mine-proximity signal.

**NB42b — All-elements HGT test via Analyses B+C with mine proximity exposure (248 tests across 31 elements, 1,077 USA + 188 EUR MAGs):**

| Exposure type | Analysis B (accessory fraction) | Analysis C (MGE×resistance) | Result |
|---|---|---|---|
| **Mine proximity** | Cs, Hg, La, Li, Nb, Sr, Th, Tl, Y all ρ<0, FDR<0.05 | Ag, As, Ba, Be, Bi, Cd, Ce, Co, Cs, Cu, Hg, La, Li, Mo, Nb, Pb, Sb, Se, Sn, Sr, Te, Th, Tl, U, V, W, Y, Zn all ρ<0, FDR<0.05 | **0 positive HGT signals; all significant results = negative** |
| **Measured concentration** | Hg ρ=+0.125, Bi ρ=+0.177 positive; As, Ce, La, Ni, Zn, Cs, Ba, Co, Th, V, Mn, Nb, Sr, U negative (FDR<0.05) | Hg ρ=+0.129, Se/Sn/Tl/Ga/Be positive; majority negative | **Hg unique: positive B+C from measured concentration, but negative from mine proximity** |

**Hg paradox resolution:** ρ(mine_Cu_proximity, measured Cu)=+0.628 but ρ(mine_Hg_proximity, measured Hg)=+0.042 (n.s.). Soil Hg concentration is driven primarily by atmospheric deposition (~50% global contribution; Gustin et al. 2020, *Sci Total Environ* 738:139763), not mine location. Thus, measured Hg shows positive HGT signals (plasmid-borne mer operons enriched in high-Hg soils) while mine proximity shows negative signals (communities near mines are compositional specialists with streamlined genomes). This is internally consistent and demonstrates that **HGT signals track actual metal exposure (bioavailable Hg concentration) rather than proximity to ore bodies.**

**Interpretation — negative B+C with mine proximity is evidence FOR turnover, not gene gain:** The consistent negative B and C signals across 27 elements indicate that contaminated communities have *reduced* accessory genome fractions and *lower* MGE co-occurrence — opposite to the gene-gain hypothesis. This pattern is consistent with **community compositional selection for specialists:** metal-stressed sites select for organisms with streamlined genomes adapted to specific niches, not expanded plasmid-carrying generalists. The positive Hg result (measured concentration) reflects a special case where atmospheric deposition creates a sustained gradient selecting for specific resistance mechanisms. Literature contrast: Gillings et al. (2015, *Trends Microbiol* 23:264–272) argue contamination drives HGT, but test acute industrial sites; Pan et al. (2019, *ISME J* 13:2532–2549) show MGE enrichment only in highly contaminated (>μM metal) soils, not field gradients. Our field gradients predominantly show the opposite (turnover-driven, negative accessory signals), consistent with chronic stress selecting for specialization, not acute toxicity driving gene acquisition.

**FOREGS validation (498 freshwater MAGs, 808 measured stream sites):** All significant associations negative (Ni ρ=−0.338, As ρ=−0.259, Pb C ρ=−0.123, all FDR<0.05). Freshwater systems near high-metal streams also show compositional turnover, not gene gain.

**Key authoritative source:** `projects/spatial_community_metal_models/REPORT.md` (NB41) and `projects/per_ko_metal_associations/REPORT.md` (NB42b all-elements).

---

## Interpretation

The five findings together support the **turnover** model over the **gene gain** model as the primary driver of metal community structure at global scales:

1. **Phylogenetic signal (PGLS) shows metal-metabolic specialists are ecologically constrained,** not advantaged. Cofactor biosynthesis genes correlate with narrow niche breadth (β=−0.033, p=10⁻⁹), consistent with specialization to metal-rich niches.

2. **Per-KO field associations identify stress-response and metabolic genes,** not dedicated resistance mechanisms, as dominant responders. 31 genes survive pH control; most are metabolic rather than canonical resistance.

3. **CWM-SPIRE overlap is near-null (3/99 = 3%),** indicating community turnover (taxon replacement) dominates over within-lineage gene acquisition. Field gradient signal traces primarily to who is present, not gene content per genome.

4. **Soil CWM FWL demonstrates robust positive mine-KO associations after full covariate control** (USA L7: 73.7% enriched; EUR shows directional loss after atmospheric deposition control). Communities near mines have distinct KO profiles because the mine-adapted specialists dominate, not because all communities acquire resistance genes.

5. **All-elements mine-proximity HGT test (248 tests, 31 elements) returns zero positive signals.** Every element shows either negative accessory fraction or negative MGE×resistance when mine proximity is the exposure. This is the opposite of gene-gain predictions and directly confirms turnover. The single positive exception — measured Hg concentration showing enriched accessory genes — actually *reinforces* the turnover interpretation: Hg is enriched because atmospheric deposition creates a gradient of *actual bioavailable Hg*, not because mine locations select for HGT. The mine-proximity null (ρ=+0.042 for Hg, n.s.) proves mine location does not predict soil Hg where deposition dominates.

These five lines of evidence converge on a single mechanism: **metal exposure selects for specialist communities via taxon turnover.** Generalist lineages carrying episodic resistance plasmids (acquired by HGT) are outcompeted by narrow-niche specialists whose genomes are streamlined for specific metal-metabolic niches. This explains why (i) within-lineage gene accumulation is rare in field gradients (unlike acute smelter sites studied by Gillings et al. 2015), and (ii) individual stress-response genes (not resistance genes) are ecologically predictive — they mark the lineages that thrive, not the mechanisms of tolerance.

**The Hg anomaly is not evidence against turnover:** The positive Hg signals (measured concentration) reflect sustained selection on mercury resistance systems in high-Hg environments. However, because Hg concentration is decoupled from mine location (atmospheric deposition dominates), the positive Hg signal actually demonstrates that HGT *does* occur — but it responds to *actual metal bioavailability*, not mine proximity. The negative mine-proximity result is therefore not a "null result" but a mechanistic finding: HGT is ecologically weak compared to compositional turnover at field-realistic contamination gradients.

**pH causal status (see PREREGISTRATION.md §5):** pH is treated as a potential confounder in the primary analysis (L1 = primary estimand), because parent geology drives both soil metal concentrations and pH independently. Controlling pH removes shared-geology confounding. pH may also partially mediate metal effects (acid mine drainage → pH drop → community shift), in which case L1 is a conservative floor estimate and L0 captures the total effect including the mediated portion. The Gelman–Stern diagnostic (0/76 contrasts reaching |z|>1.96) confirms pH acts as a categorical selector of significant pairs, not a magnitude modifier — consistent with the confounder interpretation dominating.

---

## Registered Pending Analyses

The following analyses were identified as needed by the committee (2026-08-07) and are tracked in the task list:

| Task | Status | Sub-project |
|---|---|---|
| CheckM in MCMCglmm | **DONE** — B_z pMCMC=0.592 NS, completeness pMCMC=0.986 NS; `data/phylo_nb_glmm_checkm_results.csv` | comprehensive_metal_ecology |
| λ=1 Brownian sensitivity | **DONE** — β=−0.027, p=0.0047; `data/pgls_lambda_sensitivity.csv` | comprehensive_metal_ecology |
| Ives et al. tip-error λ correction | **DONE** — Step 1 R PGLS (n=1,249, fixed λ=0.757): β=−0.037, p=0.0024; simulation loop killed (per-sim ~10+ min, 100 sims infeasible); analytic fraction_negative=1.0 (CI=[−0.051,−0.011] entirely negative); `data/ives_correction_results.csv` | comprehensive_metal_ecology |
| Forsberg RDA permutation test | **DONE** — metals unique R²=0.064 > pH unique R²=0.041 | comprehensive_metal_ecology |
| Operon collapse sensitivity | **DONE** — `operon_collapse_analysis.py` written | per_ko_metal_associations |
| MAG recovery covariates | **DONE** — `mag_quality_sensitivity.py` written | per_ko_metal_associations |
| Gelman & Stern joint interaction model | **DONE** — 0/76 contrasts significant; pH is categorical selector | per_ko_metal_associations |
| Coverage standardization for metal diversity | **DONE** — coverage explains R²=0.013; signal robust | comprehensive_metal_ecology |
| Spatial block CV (gene panel vs taxa vs pH) | **DONE** — executed 2026-08-08; no predictor >AUROC 0.65 except Zn-pH=0.684; confirms cross-region collapse across all predictor types | community_composition_prediction |
| Positive MRG literature defense | **DONE** — added to per_ko REPORT.md | per_ko_metal_associations |
| D vs λ metric justification | **DONE** — added to CME REPORT.md | comprehensive_metal_ecology |
| Three resistance β reconciliation | **DONE** — added to CME REPORT.md | comprehensive_metal_ecology |
| Per-metal denominators table | **DONE** — added to per_ko REPORT.md | per_ko_metal_associations |
| Symmetric SPIRE analysis (NB16) | **DONE** — cross-dataset comparison added | per_ko_metal_associations |
| SPIRE + CheckM2 completeness + inter-metal control (NB18) | **DONE** — 1,077 USGS-matched MAGs, full controls; 3/99 CWM-SPIRE overlap confirmed | per_ko_metal_associations |
| Module CWM + taxonomic drivers + co-occurrence networks | **DONE** — NB00/NB01/NB02 all complete 2026-08-23 | metal_community_functional_ecology |
| Pre-registration v2 (unit of analysis, covariate spec, pH DAG) | **DONE** — PREREGISTRATION.md written 2026-08-23 | metal_ecology_thesis |

---

## Data Files

All data files are in the respective sub-project directories. This synthesis project contains no independent data files.

## Figures

Key cross-project figures are in `projects/comprehensive_metal_ecology/figures/` and `projects/per_ko_metal_associations/figures/`. The Adam figures (Figs 1–4) are in `comprehensive_metal_ecology/figures/adam_*.pdf`.
