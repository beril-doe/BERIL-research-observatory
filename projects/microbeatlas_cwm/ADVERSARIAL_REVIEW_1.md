---
reviewer: BERIL Adversarial Review (Claude, opus)
type: project
date: 2026-08-25
project: microbeatlas_cwm
review_number: 1
round_number: 1
prompt_version: adversarial_project.v1 (depth=standard)
severity_counts:
  critical: 1
  important: 7
  suggested: 3
prior_round_disposition:
  resolved: 0
  partially_addressed: 0
  still_open: 0
  obsolete: 0
biological_claims_checked: 5
biological_claims_flagged: 2
prior_reviews_considered: []
---

# Adversarial Review — MicrobeAtlas × ke_pangenome CWM Metal Ecology (round 1)

## Summary

This is round 1 of an iterative review. No prior adversarial baseline exists. This round raises 1 critical, 7 important, and 3 suggested issues.

The project asks a well-scoped question — whether soil metal exposure predicts CWM functional gene shifts after confound control — and executes a carefully structured causal-level hierarchy (L0–L6) across 9 notebooks with cross-continental replication. The overall scientific architecture is strong: the FWL regression framework is appropriate, the bidirectional (forward + reverse) analysis design is genuinely informative, and the turnover-vs-gene-gain triangulation (facultativeness, reverse prediction, collider check) is a creative contribution. The project is commendably honest about its limitations (REE confounds, AUS power, CWM construction limitations).

However, a critical data-support failure undermines the permutation test conclusions: the REPORT's sensitivity section reports numbers that do not match the saved notebook outputs, changing the Cd permutation result from significant to non-significant. Several important methodological concerns — non-prokaryotic taxa in L5 covariates, omission of CEC from L2, asymmetric overlap reporting for EUR replication, and an unexplained anti-attrition pattern in Pfam Cd hits — require attention before the analysis can be considered publication-ready.

## Carryover from Prior Rounds

(no prior rounds)

## Overall Scientific Critique

**Scientific soundness.** The question, approach, and analyses form a coherent scientific argument. The causal-level hierarchy is a genuine strength — it maps directly to a well-specified DAG, and the attrition curves across L0–L6 provide interpretable evidence about which confounders absorb signal. The three-way turnover test (facultativeness, reverse R², collider attenuation) is creative and internally consistent. The overall conclusion — metals drive community turnover, not gene gain, and pH dominates — is well-supported by the analytical framework.

**Logical clarity.** The analytical chain is mostly clear. NB02 establishes the forward associations and turnover evidence; NB03 interprets the surviving hits; NB04 replicates cross-continentally; NB05–NB06 test mine proximity as an alternative exposure; NB07 validates robustness; NB08 extends to alternative annotations. Each step follows logically from the prior. The one exception is the Pfam Cd anti-attrition pattern (see I1) — the project presents L1 Pfam results but does not discuss the anomalous increase in hits at higher causal levels, which undermines confidence in the Pfam Cd finding.

**Scope-of-claim vs. scope-of-evidence.** The project is generally careful, but three claims drift beyond their evidence:
1. "560 L1 FDR hits" as a headline embeds 335 REE hits (59.8%) that the project itself flags as geology confounds (see I5).
2. "84–100% overlap" for EUR replication uses an asymmetric recall metric that overstates agreement (see I4).
3. "6/7 metals pass permutation test" does not match the saved permutation results (see C1).

**Narrative honesty.** The Limitations section is unusually thorough for a BERDL project — CWM's inability to detect gene expression, strain-level variation, or HGT is explicitly acknowledged. The REE confound is flagged. The AUS null is correctly attributed to power. This is commendable. The main honesty gap is in the sensitivity section, where the REPORT appears to report results from a prior run that differ from the saved data.

## Statistical Rigor

### Critical

- **C1: REPORT permutation test numbers do not match saved notebook outputs — Cd changes from significant to non-significant** — NB07_sensitivity.ipynb cell 5 outputs and `data/nb07_perm_results.parquet`.

  The REPORT's NB07 sensitivity section (§ "Permutation test") reports the following observed hit counts and permutation p-values:

  | Metal | REPORT obs | REPORT p | NB07 parquet obs | NB07 parquet p |
  |---|---|---|---|---|
  | As | 92 | 0.018 | 79 | 0.020 |
  | **Cd** | **145** | **0.022** | **30** | **0.064** |
  | Cr | 72 | 0.020 | 66 | 0.022 |
  | Cu | 8 | 0.022 | 8 | 0.022 |
  | Ni | 42 | 0.044 | 41 | 0.044 |
  | Pb | 22 | 0.084 | 20 | 0.088 |
  | Zn | 73 | 0.038 | 76 | 0.030 |

  Verified via Tier 1 inspection of saved data:
  ```
  python3 -c "import pandas as pd; print(pd.read_parquet('data/nb07_perm_results.parquet').to_string())"
  ```
  Output confirms: Cd n_obs=30, perm_p=0.064.

  The Cd discrepancy is conclusion-altering: the REPORT claims Cd passes the permutation test (p=0.022), but the saved data shows Cd fails (p=0.064). The REPORT claims "6/7 metals pass the permutation test" — the correct statement from the saved data is **5/7** (both Cd and Pb fail at α=0.05). Multiple other metals show discrepancies in observed hit counts (As: 92 vs 79; Cr: 72 vs 66), suggesting the REPORT's sensitivity section was written from a prior run — likely before the OLM pH×10 correction documented in the Discoveries section — and never updated to match the current notebook outputs.

  The Moran I values also diverge slightly (REPORT As I=0.453, NB07 output I=0.448), consistent with a stale-results hypothesis.

  **Suggested fix:** Re-run NB07 from the current NB02 FWL outputs (or confirm the saved parquet is definitive), then update all numbers in the REPORT's NB07 sensitivity section. Change the "6/7 metals pass" claim to match the saved data. If both Cd and Pb fail the permutation test, discuss the implications for Cd's 10 L1 FDR hits — their statistical reality is weaker than currently stated.

### Important

- **I6: Rank-transform sensitivity reduces hits by 75–97% but the source of sensitivity is not investigated** — NB07_sensitivity.ipynb cell 7.

  Rank-normal transformation of metal concentrations reduces L1 FDR hits by 75–97% across all metals (NB07: As log₁₀=79 → rank=13; Cr log₁₀=66 → rank=0; Ni log₁₀=41 → rank=0). The project correctly reports this and notes that log₁₀ matches geochemical convention, but does not investigate *why* the results are so sensitive to transformation.

  The key question is whether the log₁₀ results are driven by a small number of extreme concentration values (leverage points) that rank-normalization compresses. If a few high-concentration sites drive most of the L1 signal, the associations reflect site-specific effects rather than a general metal–CWM relationship. A Cook's distance or DFBETAS analysis on the L1 FWL residuals would distinguish "broad gradient signal" from "outlier-driven signal."

  **Suggested fix:** For each metal at L1, compute Cook's distance on the FWL residuals for the top 5 KO hits. Report what fraction of L1 hits survive when the top 5% most influential samples are removed. If most hits persist, the log₁₀ result is robust; if they collapse, the rank-transform sensitivity reflects genuine outlier-dependence.

- **I7: Effect sizes very small (β_IQR ≈ 0.003) with no standardized effect size or practical-significance assessment** — NB02_metal_associations.ipynb, REPORT § Finding 4.

  The REPORT states β_IQR ≈ 0.003, meaning a one-IQR change in log₁₀(metal concentration) shifts CWM by 0.3 percentage points. No Cohen's d, partial η², or partial R² is reported. For the ars operon KOs (K15844/K15847/K15848), I verified from `nb02_fwl_results_fdr.parquet`:

  ```
  K15844: β = -0.0062, β_IQR = -0.0032, p = 2.64e-05, q = 0.0077
  K15847: β = -0.0056, β_IQR = -0.0029, p = 2.64e-05, q = 0.0077
  ```

  At n=1,143, even tiny effects achieve statistical significance. The BH-FDR threshold for As L1 (41 hits from 6,557 tests) is p ≤ 0.000313 — stringent, but achievable with n>1,000 even for near-zero effect sizes. Without a standardized effect size, the reader cannot assess whether these associations are biologically meaningful or merely statistically detectable at large N.

  **Suggested fix:** Report partial R² (or partial η²) for each metal at L1. Compute Cohen's f² from the FWL t-statistics. For the top 5 hits per metal, report both the unstandardized β_IQR and the standardized effect size. Discuss a threshold for practical significance — e.g., partial R² > 0.01 (small effect per Cohen's conventions).

### Suggested

- **S3: Minor data-support gap — pH measured count discrepancy between NB00 output and REPORT** — NB00_data_qc.ipynb cell 8 vs REPORT § Data.

  NB00 cell 8 shows pH source breakdown: Measured=589, OLM=3,289, Missing=1,006. The REPORT says: "622 measured / 3,256 OLM / 966 SoilGrids raster / 40 missing." The "measured" counts differ (589 vs 622) and the categories differ (NB00 shows a two-tier breakdown before SoilGrids fallback; REPORT shows the final three-tier breakdown). The NB00 output is likely an intermediate step, and the final numbers are computed in a later cell — but the mismatch should be resolved by showing the final breakdown explicitly in NB00's output with all three tiers.

  **Suggested fix:** Add a summary cell at the end of NB00 that prints the final three-tier pH breakdown matching the REPORT exactly.

## Hypothesis Vetting

### H1: Metal exposure shifts community-weighted mean functional gene content (primary hypothesis)

- **Falsifiable?** Yes. The hypothesis predicts FDR-significant associations between metal concentrations and CWM KO values after pH control (L1). Falsified if zero L1 FDR hits survive across all metals.
- **Evidence presented:** 560 L1 FDR hits across 14 elements (NB02); 225 non-REE hits across 9 elements; EUR replication at 84–100% USA recall (NB04); 6/7 [corrected: 5/7] metals pass permutation test (NB07).
- **Alternative explanations:** (1) Residual spatial autocorrelation inflates significance — partially addressed by pESS (n_eff = 35–48% of nominal n) and permutation test, though the permutation test itself may not fully account for spatial structure in the CWM matrix. (2) Log₁₀ transformation amplifies extreme-concentration leverage — supported by the 75–97% hit reduction under rank-normalization (I6). (3) REE hits (59.8%) are geology-pH collinearity artifacts — explicitly acknowledged by the project.
- **Null-result handling:** Cu produces 0 L1 FDR hits in USA — honestly reported. AUS produces 0 hits for all metals — honestly attributed to power (~5× underpowered). These are correctly handled.
- **Verdict:** Partially supported. The non-REE associations (As, Cr, Ni, Zn) are real (permutation-validated) but very small in effect size. The Cd and Pb associations require caveats (Cd fails permutation in saved data; Pb marginally non-significant).

### H2: The mechanism is community turnover, not within-genus gene gain

- **Falsifiable?** Partially. The hypothesis predicts that metal-associated KOs will be indistinguishable from background in within-genus prevalence (i.e., not facultative/HGT-acquired). Falsified if metal-hit KOs are significantly *more* facultative than background.
- **Evidence presented:** (1) Facultativeness test: metal hits median_mean_prev=0.595 vs background 0.604, p=0.187 (n.s.) — NB02. (2) Reverse prediction failure: spatial block CV R²<0 for all metals — NB02, NB04. (3) Collider check: 98–100% of L1 hits attenuated at L5 — NB07.
- **Alternative explanations:** CWM *by construction* captures turnover (Σ genus_RA × genus_prevalence); it cannot detect within-genus allele frequency shifts, gene expression changes, or recent HGT. The three "independent" tests are all within the CWM framework: (1) the facultativeness test compares CWM-derived statistics; (2) the reverse prediction uses CWM as features; (3) the collider check uses CWM as the outcome. They are conceptually complementary but not statistically independent — all share the same CWM construction, and any systematic bias in CWM construction propagates to all three. The absence of gene-gain signal in CWM does not preclude gene gain detectable by other methods (strain-level pangenome analysis, metatranscriptomics).
- **Null-result handling:** The facultativeness p=0.187 is correctly reported as non-significant. The reverse R²<0 is correctly interpreted as "CWM cannot predict metals" rather than "metals don't affect CWM."
- **Verdict:** Supported within the CWM framework's resolution. The project is appropriately careful in acknowledging CWM's blind spots (Limitations section). However, claiming "three independent lines of evidence" overstates the independence — all three are CWM-derived. Recommend reframing as "three complementary analyses within the CWM framework."

### H3: pH is a structurally stronger functional driver than metals

- **Falsifiable?** Yes. Predicts pH produces more FDR hits, higher prevalence among hit KOs, and positive spatial predictive R². Falsified if metals match or exceed pH on any metric.
- **Evidence presented:** pH: 4,322 L1 hits (vs 560 metals), mean_prev=0.733 (vs 0.604 background), spatial R²=+0.151 (vs <0 for metals) — NB02. EUR and AUS pH positive controls recover massive hits — NB04.
- **Alternative explanations:** pH and metal concentrations are correlated (geology drives both). The L1 estimand controls for pH, so metal hits are pH-residual effects. Comparing L1 metal hits to L0 pH hits (where pH is the exposure, not a covariate) is not a like-for-like comparison. The proper comparison would be L0 metal hits vs L0 pH hits (both unconditioned), or metal hits with pH as exposure vs pH hits with metal as exposure.
- **Null-result handling:** N/A (pH is a positive control, not a null-tested hypothesis).
- **Verdict:** Supported. The quantitative dominance of pH is clear and well-documented, though the comparison framework (L1 metals vs L0 pH) is slightly apples-to-oranges.

### H4: Mine proximity is an insufficient surrogate for measured metal bioavailability (implicit hypothesis)

- **Falsifiable?** Yes. Predicts low overlap between mine proximity hits and metal concentration hits. Falsified if overlap >50%.
- **Evidence presented:** 2.7% overlap (14/516) between mine proximity L1 hits and NB02 metal L1 hits — NB05. Commodity-specific analysis: 0 FDR hits genome-wide — NB05. Elevation stratification: signal collapses from 484 (all) → 17 (downhill) → 0 (uphill) — NB06.
- **Alternative explanations:** The low overlap could reflect different effective sample sizes (mine proximity uses all 4,884 samples; metal analysis uses subsets with measured metals, n=545–1,693). The different N could produce different FDR thresholds and different hit sets even if the underlying signal is related.
- **Verdict:** Supported. The elevation stratification is particularly convincing — the signal being driven by elevation confounders rather than contamination is a strong empirical finding.

### H5: Cross-continental replication validates the associations (implicit hypothesis)

- **Falsifiable?** Yes. Predicts EUR independently recovers USA L1 FDR hits. Falsified if EUR overlap with USA < chance.
- **Evidence presented:** EUR replicates USA L1 hits at 84–100% USA recall, 100% directional concordance — NB04.
- **Alternative explanations:** The EUR and USA analyses share the same CWM construction pipeline (same ke_pangenome prevalence reference). They differ in community composition (different samples), metal measurements (GEMAS vs USGS), and environmental covariates. The shared pipeline means any systematic bias in CWM construction propagates to both. The overlap metric (USA recall) is asymmetric — see I4.
- **Verdict:** Partially supported. The directional concordance (100%) is strong evidence. However, the asymmetric overlap metric (I4) and shared CWM pipeline mean this is replication of the statistical method on independent metal data, not fully independent replication.

## Biological Claims

### Claim 1: "High-As soils have lower arsenic-resistance CWM, consistent with community turnover toward resistant genera dominating" (REPORT § Finding 1, Interpretation)

The ars operon KOs (K15844/K15847/K15848) show β_IQR = −0.003 (q=0.008) with As at L1. Verified from `nb02_fwl_results_fdr.parquet`. The direction is confirmed: higher As concentration is associated with lower CWM of these specific ars-operon genes.

The REPORT interprets this as consistent with high-As environments being dominated by genera that use alternative mechanisms (aioA, arrA, arsO) rather than the cytoplasmic efflux ars pathway. This interpretation is plausible but requires stronger citation:

**Escudero LV, Casamayor EO, Chong G, et al. (2013). "Distribution of microbial arsenic reduction, oxidation and extrusion genes along a wide range of environmental arsenic concentrations." PLoS ONE 8(10):e78890.** doi:10.1371/journal.pone.0078890 [PMID:24205341]

- **Studied:** Natural As-contaminated environments across 6 orders of magnitude As concentration (Northern Chile)
- **Finding:** "Enterobacterial arsC genes appeared only in lowest-As environments; Firmicutes-like arsC genes present throughout; arrA found in all systems"
- **Scope alignment:** ✓ direct match — studies the same gene distribution question across an As gradient
- **Assessment:** ✓ supports the negative-association interpretation — ars-operon genes are selectively excluded from high-As environments, exactly matching the CWM pattern

The project cites Oremland & Stolz 2003 (a foundational review) but not this empirically closer reference. Additionally, arsM (arsenic methylation) is absent from ke_pangenome KO space and from the GlobDB supplement. This annotation gap means the CWM cannot capture methylation-specialist genera.

**Assessment:** ⚠ Partially supported. The negative association is real in the data. The biological interpretation (alternative mechanism dominance) is plausible and supported by Escudero et al. 2013. However, the missing arsM annotation limits the scope of the claim.

### Claim 2: "First large-scale validation of 16S×pangenome CWM for detecting soil metal associations" (REPORT § Novel Contribution 2)

I searched for prior work on CWM approaches in microbial ecology applied to metals. The CWM method has been used extensively in plant ecology (Garnier et al. 2004, cited) and adapted for microbial enzyme activities, but I could not find a prior study that specifically combines 16S community data with pangenome-derived KO prevalence to compute microbial CWM and tests it against soil metal gradients at cross-continental scale.

The closest prior art in microbial CWM is:

**Piton G, Legay N, Arnoldi C, et al. (2020). "Using proxies of microbial community‐weighted means traits to explain the cascading effect of management intensity, soil and plant traits on ecosystem resilience in mountain grasslands." Journal of Ecology 108(3):876-893.** doi:10.1111/1365-2745.13327

- **Studied:** Mountain grassland mesocosms (France), multi-management-intensity gradient; microbial enzyme stoichiometry used as CWM trait proxies
- **Finding:** "We used microbial biomass and enzyme stoichiometry, and mass-specific enzymes activity as proxies of microbial community-weighted mean (CWM) traits, to infer trade-offs in microbial strategies of resource use with cascading effects on ecosystem resilience"
- **Scope alignment:** ⚠ uses enzyme stoichiometry as CWM proxies (not genome-derived gene prevalence), grassland mesocosms only — the current project's genome-derived KO-prevalence approach at continental scale is methodologically distinct
- **Assessment:** ✓ establishes the microbial CWM framework as prior art; the gap between enzyme-proxy CWM and genome-derived KO-prevalence CWM is genuine and supports the novelty claim

**Assessment:** ⚠ Cannot verify as definitively novel via WebSearch, but no directly overlapping prior art was found. The novelty claim is plausible. The project should cite Piton et al. 2020 (Journal of Ecology 108(3):876-893, doi:10.1111/1365-2745.13327) as the closest prior art in microbial CWM, making explicit the methodological advance from enzyme-proxy CWM to genome-derived KO-prevalence CWM.

### Claim 3: "pH is widely recognised as the primary driver of soil bacterial diversity globally" (REPORT § Literature Context)

Well-established. Fierer & Jackson 2006 (cited), Lauber et al. 2009 (cited), and Delgado-Baquerizo et al. 2016 (cited) all support this claim directly. No further verification needed.

**Assessment:** ✓ Supported by cited literature.

### Claim 4: "Community beta diversity driven by turnover rather than nestedness" under metal stress (REPORT § References, citing Zhang Y et al. 2023)

The cited paper (PMID:37783354) addresses petroleum + heavy metal co-contamination in soil microcosms. However, the project's own finding — that metal-associated KOs have the same within-genus prevalence as background — is a CWM-level analogue of turnover, not a direct observation of species turnover vs nestedness. The interpretation is sound but the evidence is indirect.

Recent genome-resolved metagenomics work provides stronger support:

**Pan Z et al. (2026). "Multi-metal contamination is associated with microbial network simplification and functional adaptation in paddy soils." Journal of Hazardous Materials 470:142406.** doi:10.1016/j.jhazmat.2026.142406

- **Studied:** 48 paddy soils (China), multi-metal gradient, 600+ MAGs
- **Finding:** "Multi-metal contamination triggered significant restructuring of microbial communities...accompanied by increased alpha diversity and enrichment of metal-tolerant taxa"
- **Scope alignment:** ⚠ paddy soils, not the globally diverse terrestrial soils in this project
- **Assessment:** ✓ supports the community-restructuring mechanism via genome-resolved evidence

**Assessment:** ⚠ Partially supported. The project's CWM-based evidence for turnover is internally consistent but indirect. Citing Pan et al. 2026 and Escudero et al. 2013 would strengthen the case.

### Claim 5: "Mine proximity is a spatial proxy for a complex mixture of exposures" (REPORT § NB05 Interpretation)

This is a straightforward interpretive claim supported by the data: 2.7% overlap between mine proximity and metal hits, plus elevation stratification showing the signal is topographically driven. No external citation needed — the claim is empirically demonstrated within the project.

**Assessment:** ✓ Supported by internal evidence.

## Data Support

### Critical

See **C1** above (permutation test numbers).

### Important

- **I1: Pfam Cd hits show anti-attrition from L1 to L6 — possible collider bias or overfitting unreported** — `data/nb08_ko_pfam_cog_comparison.csv`.

  The cross-annotation comparison table reveals an anomalous pattern for Pfam Cd hits across causal levels:

  | Level | KO hits | Pfam hits |
  |---|---|---|
  | L0 | 101 | 795 |
  | L1 | 10 | 761 |
  | L2 | 0 | 587 |
  | L3 | 0 | 518 |
  | L4 | 0 | 1,039 |
  | L5 | 0 | 1,966 |
  | L6 | 0 | 2,058 |

  KO hits show normal attrition (101→10→0). But Pfam Cd hits drop from L1 (761) to L3 (518), then *increase dramatically* to L4 (1,039), L5 (1,966), and L6 (2,058). Adding climate (L4) and community composition (L5) covariates *increases* the number of Pfam-Cd associations — the opposite of the confound-attrition pattern seen in KO results and expected under a causal model.

  This anti-attrition pattern is diagnostic of either: (a) collider bias — conditioning on a descendant of Cd and Pfam prevalence opens a non-causal path; (b) overfitting — the L4–L6 covariate matrices have many columns relative to the Cd sample size (n=998), reducing residual degrees of freedom and inflating t-statistics; or (c) a suppressor variable effect — a legitimate statistical phenomenon, but one that requires explicit diagnosis and discussion.

  The REPORT presents only the L1 Pfam result (761 hits) without discussing the attrition curve. This omission is significant because the L1 result could be artifactual if the pattern at higher levels reflects model instability.

  **Suggested fix:** Plot the Pfam Cd attrition curve (like the KO curves in fig_nb02_beta_stability.pdf). Compute the effective degrees of freedom at each level. If d.f. < 50 at L6, flag the result as potentially overfitted. Examine whether the L5 increase is driven by specific phylum RA covariates acting as suppressors.

- **I5: Headline "560 L1 FDR hits" includes 59.8% REE confounds the project itself flags** — REPORT § Finding 1, § NB02.

  The primary L1 hit count (560) includes Nd=235, Yb=91, La=9 — totaling 335 REE hits (59.8% of the total). The project explicitly acknowledges these as "likely geology/pH collinearity confounds" (NB03) and excludes them from primary manuscript claims. Yet the headline number in Finding 1 and the Summary is "560 L1 FDR hits."

  Verified via `nb02_fwl_results_fdr.parquet`:
  ```python
  l1_hits = fdr[(fdr['level']=='L1') & (fdr['q_bh']<0.05)]
  ree = l1_hits[l1_hits['metal'].isin(['Nd','Yb','La'])]
  # REE: 335/560 = 59.8%
  ```

  A reader encountering "560 L1 FDR hits across 14 elements" forms a qualitatively different impression than "225 non-REE L1 FDR hits across 9 elements, plus 335 REE hits flagged as geology confounds." The non-REE count is the scientifically defensible number.

  **Suggested fix:** Lead with the non-REE hit count (225) in all summary statements. Reserve "560 total including REE" for completeness in the detailed NB02 results. Restructure Finding 1 to foreground: "225 L1 FDR hits across 9 non-REE elements."

- **I4: EUR replication overlap metric is asymmetric — Jaccard index substantially lower than reported 84–100%** — REPORT § Finding 2, NB04_regional_replication.ipynb.

  The REPORT states "EUR replicates 84–100% of USA L1 hits." This is USA recall: the fraction of USA hits also found in EUR. The symmetric Jaccard index (|USA ∩ EUR| / |USA ∪ EUR|) tells a different story:

  | Metal | USA hits | EUR hits | Overlap | USA recall | Jaccard |
  |---|---|---|---|---|---|
  | As | 41 | 44 | 38 | 92.7% | 80.9% |
  | Cd | 10 | 31 | 10 | 100% | 32.3% |
  | Cr | 38 | 46 | 36 | 94.7% | 75.0% |
  | Ni | 38 | 34 | 32 | 84.2% | 80.0% |
  | Pb | 14 | 56 | 14 | 100% | 25.0% |
  | Zn | 76 | 98 | 56 | 73.7% | 47.5% |

  For Cd (Jaccard=32.3%) and Pb (Jaccard=25.0%), the symmetric overlap is low — EUR identifies many hits that USA does not, meaning the two regions' hit sets are substantially different despite the REPORT's "100% overlap" framing. 100% directional concordance (all overlapping hits have the same sign) is a genuine strength, but the asymmetric overlap metric inflates the impression of cross-continental agreement.

  **Suggested fix:** Report both USA recall (current "overlap") and Jaccard index. Discuss the asymmetry — EUR's additional hits (e.g., Cd: 21 EUR-only, Pb: 42 EUR-only) could reflect either greater EUR power (larger n, different concentration ranges) or region-specific associations. A correlation of effect sizes (β_USA vs β_EUR for all KOs, not just significant ones) would be more informative than a threshold-dependent overlap count.

## Reproducibility

**Notebook outputs:** All 9 analysis notebooks (NB00–NB08) have saved outputs consistent with the analysis described. The figure directory contains 31 figures, all referenced in the REPORT. The data directory contains 39 intermediate files that support cross-notebook reproducibility.

**Missing outputs:** The `references.md` file does not exist — the REPORT contains inline references but no separate bibliography file. This is acceptable given the REPORT's inline citation style.

**Figure format:** All figures are saved as PDF (conforming to CLAUDE.md conventions). Figure naming follows the `fig_nb{NN}_` convention.

**Reproduction notes:** The README does not include a `## Reproduction` section with runtime estimates or Spark requirements. Given the 9-notebook pipeline with Spark dependencies, this would help reviewers estimate reproduction cost.

**Suggested fix:** Add a `## Reproduction` section to README.md with estimated runtimes per notebook and Spark session requirements.

## Literature and External Resources

### Missing foundational and recent citations

The project's citation base is adequate for classic references (Fierer & Jackson 2006, Oremland & Stolz 2003, Garnier et al. 2004) but has significant gaps in recent (2023–2026) primary research directly addressing metal × microbial functional genes:

1. **Escudero et al. (2013)** — Distribution of As resistance/metabolism genes across As gradient (see Biological Claims § Claim 1). Directly supports the ars-operon negative-association interpretation. Missing from references.

2. **Piton et al. (2020)** — Microbial CWM enzyme proxies (Journal of Ecology 108(3):876-893, doi:10.1111/1365-2745.13327; see Biological Claims § Claim 2). Closest prior art in microbial CWM methodology. Not cited.

3. **Zhang SY et al. (2021). "High Arsenic Levels Increase Activity Rather than Diversity or Abundance of Arsenic Metabolism Genes in Paddy Soils." Applied and Environmental Microbiology 87(20):e0138321.** doi:10.1128/AEM.01383-21 [PMID:34378947, PMCID:PMC8478449]

   - **Studied:** Paddy soils with As gradient (~10 vs ~100 mg/kg As), metagenomics + metatranscriptomics
   - **Finding:** "the relative DNA abundances and diversities of [ars genes] were not significantly different between low and high As soils...metatranscriptomics revealed that relative to low-As soils, high-As soils showed a significant increase in transcription of ars and aioA genes"
   - **Scope alignment:** ⚠ paddy soils only; the current project studies globally diverse terrestrial soils
   - **Assessment:** ✓ directly demonstrates transcriptional upregulation without abundance change — a distinct mechanism CWM cannot detect, directly relevant to the project's turnover-not-gene-gain claim. Not cited.

4. **Guo Y et al. (2023). "Copper and cadmium co-contamination affects soil bacterial taxonomic and functional attributes in paddy soils." Environmental Pollution 329:121724.** doi:10.1016/j.envpol.2023.121724 [PMID:37105465]

   - **Studied:** Paddy soils along a polluted river in southern China, Cu/Cd gradient, shotgun metagenomics
   - **Finding:** "Soil Cu and Cd contamination led to drastic changes in the cumulative relative abundance of ecological modules in bacterial co-occurrence networks...Cu and Cd contaminant fractions were positively correlated with the genes involved in metal resistance, carbon fixation, nitrification, and denitrification"
   - **Scope alignment:** ⚠ paddy soils, China; the current project studies globally diverse terrestrial soils
   - **Assessment:** ✓ provides a direct methodological parallel (metals × shotgun metagenomics × functional genes); supports the metal-functional-gene association inference. Not cited.

5. **Spatial block cross-validation is not cited.** The project uses spatial block CV as the primary test distinguishing metals (R²<0) from pH (+0.151), making this methodological choice foundational to Finding 4. The project provides no citation for spatial block CV methodology, leaving the block-construction choices (block size, number of blocks, block-assignment algorithm) unanchored to validated implementations. **Suggested fix:** Add a foundational spatial CV citation and explicitly describe block-size selection and block-assignment method in the Methods section where spatial CV is introduced.

6. **The Frisch-Waugh-Lovell (FWL) theorem is not cited.** The FWL theorem — which proves that a partial regression on residuals from regressing out covariates recovers the same coefficient as the full OLS model — is the econometric foundation of the L0–L6 partial regression implementation used throughout the project. The project uses FWL extensively but cites no econometric literature establishing the theorem. **Suggested fix:** Add a citation to the FWL theorem (either the original econometrics papers or a standard econometrics textbook stating the theorem with proof) in the Methods section where FWL residuals are first introduced, so the equivalence claim is formally grounded.

### External tools and datasets

- **PaperBLAST** (available in BERDL): Could be applied to the 17 stable L1∩L6 KOs to surface experimental fitness or functional evidence. Specifically, PaperBLAST queries on MoCo biosynthesis KOs (K14370 MoaE, K14367 MoaC — the stable Pb hits) could reveal whether Pb inhibition of MoCo enzymes has been experimentally demonstrated, strengthening the interpretation in NB03.

- **CARD (Comprehensive Antibiotic Resistance Database)**: For the COG category V (defense mechanisms) hits and the AMR-related claims. The project uses ke_pangenome's bakta_amr table but does not cross-reference with CARD's broader metal resistance gene annotations.

- **gcMeta**: This large MAG catalog (>2.7M MAGs across biomes) could increase genus-level coverage beyond the 53.1% genus overlap (2,359/4,443 genera) currently achieved between MicrobeAtlas and ke_pangenome terrestrial. However, different taxonomy schemes would require careful bridging before adoption.

- **Companion projects**: The REPORT's Future Directions mention "companion project" for species-level MWAS (SPIRE × USGS). Cross-referencing with the `per_ko_metal_associations` project (SPIRE-based, USGS measured metals only, 1,077 MAGs) could test whether the turnover-not-gene-gain finding holds at species level.

## Statistical Rigor (continued)

### Important

- **I2: Non-prokaryotic taxa in L5 community composition covariates** — NB02_metal_associations.ipynb cell 10.

  The top 8 "phyla" by relative abundance used as L5 covariates include: alphaproteobacteria, **sordariomycetes** (fungi, class Ascomycota), actinomycetia, gammaproteobacteria, **bryopsida** (mosses), **insecta** (insects), nitrososphaeria (archaea), **wallemiomycetes** (fungi, class Basidiomycota).

  Four of eight L5 covariates are non-prokaryotic classes. MicrobeAtlas is a 16S-based database; these entries likely reflect either: (a) non-bacterial OTUs in the SILVA taxonomy database used by MicrobeAtlas, (b) cross-kingdom amplification artifacts, or (c) mitochondrial/chloroplast sequences classified as eukaryotic source organisms.

  Using non-prokaryotic RA as covariates in L5 means the "community composition control" partially controls for non-bacterial components of the amplicon data. This affects the collider check interpretation: the L1→L5 attrition (98–100% of metal hits attenuated) is presented as evidence that "the metal signal is mediated through community composition." But if L5 includes eukaryotic RA, the attenuation could reflect spatial correlation between eukaryotic abundance and both metals and bacterial CWM, rather than bacterial community-mediated effects.

  Additionally, these are class-level names (GTDB/SILVA classes), not phyla as labeled. Alphaproteobacteria is class, not phylum (phylum = Pseudomonadota in GTDB).

  **Suggested fix:** (1) Filter the "phylum" RA covariates to prokaryotic entries only before computing L5. (2) Re-run the collider check with bacteria-only L5 covariates. (3) Correct the nomenclature: these are classes, not phyla.

- **I3: CEC omitted from L2 implementation despite being listed in the causal level definition** — RESEARCH_PLAN § 2 Causal Level Definitions vs NB02_metal_associations.ipynb cell 14.

  The causal level definitions (RESEARCH_PLAN and REPORT) state L2 controls for "clay, SOC, **CEC**, bulk density, GLiM lithology." But `data/nb02_soil_props.parquet` contains only 4 columns (clay_pct, som_pct, bulk_density, soil_moisture) — no CEC. NB02 cell 14 confirms CEC is not in the covariate matrix.

  CEC (cation exchange capacity) directly determines the bioavailability of cationic metals (Cd²⁺, Cu²⁺, Ni²⁺, Pb²⁺, Zn²⁺). High-CEC soils bind more metals, reducing bioavailability. Omitting CEC from L2 means the "soil properties control" does not account for bioavailability — the L2 estimate still contains a confound pathway: geology → CEC → metal bioavailability → community → CWM. This weakens the "after controlling for soil properties" claim.

  **Suggested fix:** Either (a) add CEC from SoilGrids (available as `cec_0cm` in `soilgrids_master`) and re-run L2+ FWL, or (b) remove CEC from the causal level definitions and explicitly acknowledge that metal bioavailability is not controlled at L2. Option (a) is preferable — CEC is a standard soil covariate and available from the same source already used for pH fallback.

### Suggested

- **S1: V-region sensitivity analysis planned but not executed** — RESEARCH_PLAN § NB08 (8a).

  The RESEARCH_PLAN specifies "Repeat NB05 L1 analysis within V3-only samples and V4-only samples...flag KOs where direction flips across V-regions." NB01 tracks V-region assignment (81% V4/V3). But no V-region sensitivity analysis appears in any completed notebook. The actual NB08 implements Pfam/COG associations instead.

  V-region sensitivity is important because different 16S hypervariable regions capture different taxonomic profiles, which would produce different genus RA vectors and therefore different CWM values. If the L1 hits are not robust across V-regions, the findings may be V-region-specific rather than biologically general.

  **Suggested fix:** Add a V-region sensitivity check — either as a new cell in NB07 (sensitivity) or a standalone analysis. At minimum, report the V-region composition of the thinned sample set and test whether L1 β estimates correlate between V4-only and V3-only subsets.

- **S2: Planned interaction terms not implemented** — RESEARCH_PLAN § 2a.

  The RESEARCH_PLAN specifies four interaction terms to test (pH×metal, log(metal)×lithology, mine_dist×elev_diff, metal×MAT), each with LRT and δ-R² analysis. None appear in any completed notebook. pH×metal is particularly relevant: if acidic soils amplify metal bioavailability (a well-established geochemical relationship), the main-effects model may underestimate the metal effect in acidic soils and overestimate it in alkaline soils.

  **Suggested fix:** Test at minimum the pH×metal interaction at L1 for the top 3 metals (As, Zn, Cr). Report whether the interaction is significant and whether it changes the L1 hit list.

## Review Metadata

- **Reviewer**: BERIL Adversarial Review (Claude, opus)
- **Date**: 2026-08-25
- **Scope**: Read README.md, RESEARCH_PLAN.md, REPORT.md (615 lines); inspected all 11 notebooks (cell outputs, not full source); checked 39 data files in data/; verified 31 figures in figures/; read docs/pitfalls.md; computed Tier 1 statistics (BH-FDR thresholds, Jaccard indices, effect sizes); verified claims against nb02_fwl_results_fdr.parquet and nb07_perm_results.parquet; spawned literature-scan subagent (PubMed, arXiv, Google Scholar, Semantic Scholar); conducted 3 WebSearch biological-claim verifications; checked 5 biological claims, flagged 2.
- **Note**: AI-generated review. Treat as advisory input, not definitive.


## Citation Verification

Programmatically verified 7 citation block(s) against Crossref (DOI) and NCBI PubMed (PMID).

- Verified: 7
- Fabricated: 0
- Unverifiable (network failure): 0
- Missing identifier (no DOI/PMID): 0

## Run Metadata

- **Elapsed**: 40:57
- **Model**: opus
- **Tokens**: input=780 output=53,074 (cache_read=630,582, cache_create=500,043)
- **Estimated cost**: $7.164
- **Pipeline**: main + critic + fix + re-critic (4 calls)
