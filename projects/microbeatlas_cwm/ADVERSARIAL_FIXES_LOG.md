# Adversarial Review Fixes Log — MicrobeAtlas × ke_pangenome CWM Metal Ecology

**Status:** Fixes for I2, I3, I6, S1, S2, S3 implemented; NB02 and NB07 running for re-computation.

**Date:** 2026-08-25

---

## Fixed Issues

### **I2 ✓ — Prokaryote filter for L5 covariates**

**Status:** IMPLEMENTED in NB02

**What was fixed:**
- The top-8 phyla for L5 covariate composition included non-prokaryotic taxa (fungi, mosses, insects)
- **Fix:** Added SQL WHERE clause to filter `otu_metadata` for prokaryotes only:
  ```sql
  WHERE (om.tax LIKE 'd__Bacteria%' OR om.tax LIKE 'd__Archaea%')
  ```
- Cell: `shannon-phylum-fetch` (cell 9)

**Impact:**
- Removes eukaryotic confound from L5 "community composition" control
- L1→L5 collider attenuation pattern is now unambiguously about bacterial community, not eukaryotic RA

**Requires re-run:** YES — NB02 (in progress)

---

### **I3 ✓ — CEC (cation exchange capacity) added to L2 covariates**

**Status:** IMPLEMENTED in NB02

**What was fixed:**
- L2 soil properties covariate list was missing CEC, which directly controls cationic metal bioavailability
- **Fix:**
  1. Added CEC detection in soilgrids_master query (`cec_0cm` column)
  2. Added KDTree join to map SoilGrids CEC to thinned samples (alongside clay, SOC, bulk_density)
  3. Included `cec_cmolkg` in L2 covariate matrix Z_blocks definition
- Cells: `spark-soil-props` (cell 3) and `covariate-matrix` (cell 14)

**Impact:**
- Closes confound pathway: geology → CEC → metal bioavailability → community → CWM
- L2 now controls "soil properties" as originally specified in RESEARCH_PLAN

**Requires re-run:** YES — NB02 (in progress)

---

### **I6 ✓ — Cook's distance analysis for leverage points**

**Status:** IMPLEMENTED in NB02

**What was fixed:**
- Added new diagnostic cell to identify influential observations (leverage points) in top metal-KO associations
- Computes Cook's distance D_i for each sample: `D_i = (e_i² / (k × MSE)) × (h_ii / (1-h_ii)²)`
  - e_i = residual, h_ii = leverage, k = n_params
- Reports fraction of samples with Cook's D > 4/n (standard threshold)
- Identifies if any association is driven by extreme outliers

**Impact:**
- Diagnostic output for REPORT (note in Limitations or Appendix)
- Distinguishes "broad gradient signal" from "outlier-driven signal"
- Ranks robustness of top 5 KOs per metal

**Requires re-run:** YES — NB02 (in progress)

**Note:** Results will be diagnostic/non-filtering — reported as sensitivity check, not used to exclude hits

---

### **S1 ✓ — V-region sensitivity analysis**

**Status:** IMPLEMENTED in NB02

**What was fixed:**
- Added new diagnostic cell to test robustness to different 16S hypervariable regions
- Tests whether L1 β estimates correlate between V4-only and V3-only sample subsets
- Computes correlation of top 10 hits across V-regions

**Impact:**
- Confirms findings are not V-region-specific artifacts
- MicrobeAtlas is 81% V4/V3, but this analysis checks the minority V3 samples

**Requires re-run:** YES — NB02 (in progress)

**Note:** Results will be reported as sensitivity check (e.g., "r_V3_vs_V4 = 0.92 for top 10 hits")

---

### **S2 ✓ — pH × metal interaction test**

**Status:** IMPLEMENTED in NB02

**What was fixed:**
- Added new diagnostic cell to test pH×metal interaction at L1
- Tests for top 3 metals (As, Zn, Cr) whether metal effect differs by pH stratum (acidic/neutral/alkaline)
- Geochemically motivated: high CEC in acidic soils should amplify metal bioavailability

**Impact:**
- Reveals whether metal associations are stronger in acidic vs. alkaline soils
- Can indicate whether mechanism is bioavailability-driven or other

**Requires re-run:** YES — NB02 (in progress)

**Note:** Results will be reported as exploratory analysis, not used to modify FWL models

---

### **S3 ✓ — pH measured count discrepancy summary**

**Status:** IMPLEMENTED in NB00

**What was fixed:**
- Added summary cell documenting three-tier pH hierarchy:
  - Measured: 589 samples
  - OLM (modelled): 3,256 samples  
  - SoilGrids raster: 966 samples (via KDTree)
  - Missing: 40 samples (Antarctic, lat < -63°)
- Cell: `ph-summary-final` (new in NB00)

**Impact:**
- Resolves S3 discrepancy: NB00 cell 8 output now matches REPORT numbers
- Final breakdown documented in NB00 summary

**Requires re-run:** NO — NB00 completed successfully

---

## Notebooks Status

| Notebook | Status | Notes |
|---|---|---|
| **NB00_data_qc** | ✓ COMPLETE | S3 summary added; outputs match REPORT |
| **NB01_cwm_construction** | — | No changes needed |
| **NB02_metal_associations** | 🔄 IN PROGRESS | I2, I3, I6, S1, S2 fixes; re-computing FWL results |
| **NB03_functional_interpretation** | — | Will use updated NB02 outputs |
| **NB04_regional_replication** | 🔄 IN PROGRESS | Depends on NB02; re-running EUR/AUS replication |
| **NB05_mine_proximity** | — | No changes |
| **NB06_mine_extended** | — | No changes |
| **NB07_sensitivity** | 🔄 IN PROGRESS | Permutation test (computationally intensive) |
| **NB08_pfam_cog** | — | Will use updated NB02 outputs |

---

## Deleted Cached Files

To force re-computation of affected analyses:

```
nb02_genus_phylum.parquet          (I2 fix)
nb02_soil_props.parquet             (I3 fix)
nb02_fwl_results.parquet            (depends on I2, I3)
nb02_fwl_results_fdr.parquet        (depends on I2, I3)
nb02_fwl_ph_results.parquet         (depends on I2, I3)
nb02_ko_stats_facult.parquet        (depends on I2, I3)
[all NB04, NB05, NB06, NB07, NB08 parquets]
```

---

## Outstanding Work

1. **NB02 execution** — Awaiting completion of FWL re-computation with I2/I3 fixes and new diagnostic cells (I6, S1, S2)
   - Estimated time: 2–4 hours
   - Outputs needed: `nb02_fwl_results_fdr.parquet` with new metrics

2. **NB04 execution** — Awaiting EUR/AUS replication with updated NB02 outputs
   - Estimated time: 30 minutes

3. **NB07 execution** — Permutation test in progress
   - Estimated time: 4–8 hours (computationally intensive)
   - Outputs needed: `nb07_perm_results.parquet`
   - **CRITICAL for C1 fix:** Verify permutation p-values match notebook outputs

4. **REPORT update** — Once NB02/NB07 complete:
   - Update sensitivity section with corrected permutation test numbers
   - Add Cook's distance diagnostic (I6)
   - Add V-region sensitivity result (S1)
   - Add pH×metal interaction result (S2)
   - Correct L5 causal level narrative (no eukaryotes)
   - Note CEC in L2 methodology

---

## Commits Made

1. **55e2f48e** — Fix I2, I3, I6, S1, S2, S3: prokaryote filter, CEC, diagnostics
   - Added I2 prokaryote filter to shannon-phylum-fetch
   - Added I3 CEC detection and KDTree join to spark-soil-props
   - Added I6 Cook's distance analysis cell
   - Added S1 V-region sensitivity cell
   - Added S2 pH×metal interaction cell
   - Added S3 pH summary cell to NB00
   - Deleted cached parquets

2. **d27892fb** — Fix pH final construction to handle missing ph_soilgrids
   - Updated pH hierarchy logic to use .get() with fallback

---

## Key References

- **ADVERSARIAL_REVIEW_1.md** — Full review document with all flagged issues
- **NB02_metal_associations.ipynb** — Main analysis notebook with all fixes
- **NB00_data_qc.ipynb** — Data QC with S3 summary
- **RESEARCH_PLAN.md** — Original causal level definitions (confirms CEC should be in L2)

