# NB40: Stream Per-KO MAG-Level FWL Analysis — Complete Workflow

**Analysis Date:** 2026-08-30  
**Project:** Metal ecology thesis — Do mine proximity effects on stream KO diversity persist at MAG level beyond community turnover?  
**Status:** Data extraction in progress; logistic regression and analysis ready  

---

## Research Question

**CWM Analysis (NB33) found:** 65% (EUR) and 82% (USA) of FDR-significant KOs survive L6 (genus PC1 control).

**MAG-level question:** Does this same signal replicate when testing actual genome presence/absence with genus fixed effects, or does it collapse like in soil (SPIRE: 3/99 KOs = 3% survival)?

**Biological interpretation:**
- If survival remains high (50–80%): Gene-level adaptation is real—specific genes are enriched in communities near mines *independent of which genera are present*
- If survival collapses (<5%): The CWM signal is metabolic co-variation—the genes co-segregate with community composition, not mines

---

## Data Sources

### 1. Freshwater MAG Inventory

**Source:** GlobDB r232 + NCBI SRA sample coordinates

| Metric | Count |
|--------|-------|
| **Total freshwater samples (env_biome keyword)** | 6,147 |
| **Freshwater MAGs with lat/lon** | 818 |
| **Unique genera** | 529 |
| **EUR MAGs** | 521 (63.7%) |
| **USA MAGs** | 92 (11.2%) |
| **Other regions** | 205 (25.1%) |

**Data sources:** MOTU (736, 90%), CRLG (82, 10%)

### 2. KO Annotations

**Source:** GlobDB protein_annotations_all.parquet (KOfam)

| Metric | Value |
|--------|-------|
| **Total genomes in parquet** | 346,232 |
| **Total protein entries** | 2.9 billion |
| **Row groups** | 23,410 |
| **KOs found in freshwater MAGs** | ~120,000+ genome-KO pairs (from ~4,000 RGs scanned) |
| **KO format** | K##### (e.g., K00941) |

**Note:** As of row group 9,100/23,410 (39% complete), found 120,147 unique genome-KO pairs. All freshwater MAGs appear to be in the scanned portion; remaining scan is for completeness.

### 3. Environmental Metadata

From globdb_sample_coordinates.parquet:

| Variable | Coverage | Notes |
|----------|----------|-------|
| **lat/lon** | 100% | Required for sample selection |
| **pH** | ~100% (818/818) | Most freshwater sites have pH; check range |
| **Temperature** | <5% | Too sparse for use as covariate; omitted |
| **Elevation/Depth** | <10% | Too sparse; lentic vs lotic inferred from env_biome |
| **env_biome** | Keyword-matched | 818 samples matched "freshwater", "lake", "lentic", "river", "stream" |

### 4. Mine Proximity (Placeholder)

**Status:** Not yet computed. Requires:
1. Mindat ore deposit database (global)
2. Spatial nearest-neighbor join (lat/lon → nearest mine distance)
3. Transformation: `exposure = log₁₀(1 / (dist_km + 0.1))`

**Placeholder in current script:** All samples set to 5,000 km (max distance), pending spatial join.

---

## Analysis Design

### Model Specification

**Response variable:** `ko_present` (0/1: genome lacks/carries the KO)

**Exposure variable:** `mine_exposure = log₁₀(1 / (mine_any_dist_km + 0.1))`

**Covariate levels (FWL residualization):**

| Level | Covariates | Purpose |
|-------|-----------|---------|
| **L0** | None | Bivariate: mine only |
| **L1** | pH, pH² | Soil acidity control |
| **L5** | L1 + BIO1 + BIO12 + lat | Climate + spatial gradient control |
| **L6** | L5 + C(genus) | **Genus fixed effects** (main test) |

**Statistical method:** Logistic regression (sklearn.linear_model.LogisticRegression or statsmodels)

**Multiple testing correction:** Benjamini-Hochberg FDR, q-value < 0.05

### KO Filtering Criteria

- **Prevalence:** Must be present in ≥5 genera
- **Abundance:** Must be present in ≥10% of all genomes (n ≥ 82 genomes for 818 total)
- **Sample size per KO:** ≥20 genomes with data per level

**Expected KO count:** 5,000–10,000 after filtering

---

## Comparison to Prior Work

### SPIRE Soil Analysis (Precedent)

**From `projects/per_ko_metal_associations/`:**

| Metric | SPIRE Soil |
|--------|-----------|
| MAGs | 2,477 (USGS SPIRE projects) |
| KOs tested (L0) | 4,759 |
| KOs FDR<0.05 (L0) | 1,012 |
| KOs FDR<0.05 (L6 with genus FE) | 33 |
| **Survival rate (L6 vs L0)** | **3.3%** |
| CWM-overlapping KOs | 99 |
| CWM-overlap KOs surviving L6 | 3 (**3%**) |
| **Interpretation** | Collapse: CWM signal is taxonomic co-variation, not gene-level adaptation |

### NB33 Aquatic CWM Analysis (Current Baseline)

**From NB33 stream per-KO FWL analysis:**

| Region | L0 hits | L6 hits | Survival |
|--------|---------|---------|----------|
| **EUR** | 8,260 | 5,385 | **65%** |
| **USA** | 8,110 | 6,622 | **82%** |
| **Combined** | ~16,370 | ~12,007 | **73%** |

**Interpretation:** High survival suggests genuine gene-level adaptation beyond community turnover.

### NB40 Prediction (This Analysis)

| Metric | SPIRE Precedent | NB33 CWM | NB40 Prediction |
|--------|-----------------|----------|-----------------|
| Data type | MAG presence/absence | CWM abundance | MAG presence/absence |
| Tax control | Genus FE | Genus PC1 | Genus FE |
| Expected L6 survival | 3–5% | 65–82% | <10% (SPIRE-like) OR 50–80% (genuine) |

**Two possible outcomes:**
1. **Collapse scenario (SPIRE-like):** <5% survival → CWM signal is driven by metabolic co-variation and community turnover, not gene-level selection
2. **Replication scenario (genuine adaptation):** 50–80% survival → Specific genes are genuinely associated with mine proximity independent of genus

---

## Computational Workflow

### Step 1: Extract Freshwater MAGs (COMPLETE)

**Script:** `projects/spatial_community_metal_models/scripts/run_nb40_stream_mag_ko_fwl.py`

**Output files:**
- ✅ `globdb_freshwater_coords.parquet` — 818 MAGs with lat/lon, genus, region
- ✅ `globdb_freshwater_metadata.parquet` — metadata (pH, mine distance placeholder)

### Step 2: Build MAG × KO Matrix (IN PROGRESS)

**Status:** Row group 9,100/23,410 (39% complete)

**Expected completion:** ~12–15 hours from start (2026-08-30 22:00 UTC → ~2026-08-31 10:00 UTC)

**Output file:**
- `globdb_freshwater_ko_matrix.parquet` — ~120,000 genome-KO pairs

### Step 3: Compute Mine Proximity (PENDING)

**Input:** GlobDB freshwater MAG coordinates + mindat mine database  
**Task:** Spatial nearest-neighbor join  
**Output:** `globdb_freshwater_mine_distances.parquet`

**Commands to fetch mindat data:**
```bash
# Example: Download mindat.org database (need API or CSV dump)
# Then spatial join with GlobDB coordinates
# See: projects/spatial_community_metal_models/scripts/compute_upstream_mine_dist.py (reference)
```

### Step 4: Run Logistic Regression (PENDING)

**After Step 2 completes:**

```bash
OMP_NUM_THREADS=1 python3 \
  projects/spatial_community_metal_models/scripts/run_nb40_logistic_regression.py
```

**Tasks:**
- L0 regression: ~5,000–10,000 KOs × 818 genomes
- L6 regression: same, with genus one-hot encoding
- FDR correction per level
- Comparison and survival calculation

**Time estimate:** 2–4 hours

**Output files:**
- `globdb_freshwater_l0_results.csv` — β, SE, p-value, n_present, n_total per KO
- `globdb_freshwater_l6_results.csv` — same for L6
- `globdb_freshwater_survival_summary.csv` — overlap analysis

### Step 5: Analysis & Visualization (PENDING)

**After Step 4 completes:**

- Q-Q plots for p-value distributions
- Manhattan plot: −log₁₀(p) vs KO index
- Venn diagram: L0 hits vs L6 hits
- Table: Top 20 KOs by effect size at L6
- Geographic breakdown (EUR vs USA)
- Comparison to NB33 CWM results

---

## Key Files & Locations

### Data (nb40 directory)

```
projects/spatial_community_metal_models/data/nb40/
├── EXPLORATION_NOTES.md                    # This file (data discovery summary)
├── NB40_ANALYSIS_REPORT.md                 # Full workflow (this document)
├── globdb_freshwater_coords.parquet        # ✅ 818 MAGs with lat/lon
├── globdb_freshwater_metadata.parquet      # ✅ pH, temperature, mine distance
├── globdb_freshwater_ko_matrix.parquet     # IN PROGRESS (120K+ pairs)
├── globdb_freshwater_analysis_matrix.parquet   # PENDING (full matrix with covariates)
├── globdb_freshwater_l0_results.csv        # PENDING (bivariate regression)
├── globdb_freshwater_l6_results.csv        # PENDING (genus FE regression)
└── survival_comparison_to_nb33.csv         # PENDING (overlap analysis)
```

### Scripts

```
projects/spatial_community_metal_models/scripts/
├── run_nb40_stream_mag_ko_fwl.py           # Main extraction & regression script
├── compute_upstream_mine_dist.py           # Reference for spatial join
└── run_nb33_stream_ko_fwl.py               # NB33 CWM reference
```

### Logs

```
projects/spatial_community_metal_models/logs/
└── nb40_exploration.log                    # Full scan log (updated in real-time)
```

---

## Expected Results

### Hypothesis 1: SPIRE-Like Collapse (Likely)

- **L6 survival:** <5%
- **Interpretation:** CWM signal driven by community composition and metabolic co-variation, not mine proximity at gene level
- **Biological meaning:** Gene content cannot be decoupled from taxonomic identity; community assembly trumps individual gene selection

### Hypothesis 2: CWM Replication (Alternative)

- **L6 survival:** 50–80%
- **Interpretation:** Stream communities exhibit genuine gene-level adaptation independent of genus
- **Biological meaning:** Specific genes are selected for mine proximity regardless of which genera carry them

### Geographic Breakdown

Expected to find stronger effects in EUR (concentrated Alpine mines) vs USA (diffuse distribution):
- **EUR MAGs:** 521 (sufficient for stratified analysis)
- **USA MAGs:** 92 (limited statistical power)

---

## Timeline & Next Steps

| Phase | Est. Duration | Target Date |
|-------|--------------|------------|
| **Step 2: Finish KO extraction** | 6–8 more hours | 2026-08-31 06:00 |
| **Step 3: Compute mine distances** | 1–2 hours | 2026-08-31 08:00 |
| **Step 4: Logistic regression** | 2–4 hours | 2026-08-31 12:00 |
| **Step 5: Visualization & report** | 2–3 hours | 2026-08-31 15:00 |
| **Final summary to REPORT.md** | 1 hour | 2026-08-31 16:00 |

---

## Critical Dependencies

1. **Mindat mine database:** Need to download/access global ore deposits
   - Option 1: Pre-computed from `projects/per_ko_metal_associations/` (soil SPIRE)
   - Option 2: Download from mindat.org API or CSV
   - Option 3: Use pre-computed `mine_any_dist_km` if available in GlobDB metadata

2. **Genus fixed effects coding:** Logistic regression with 529 genera → many singular matrices
   - **Solution:** Drop first genus (reference category), fit within-genus deviations

3. **Statistical power:** 818 MAGs << 2,477 SPIRE genomes
   - May have reduced power to detect small effects
   - Some KOs may have <10 genomes total → filter out

---

## References & Related Work

### SPIRE Soil Analysis
- **File:** `projects/per_ko_metal_associations/data/spire_all_ko_matrix.parquet`
- **Script:** `projects/per_ko_metal_associations/scripts/run_nb04_spire_rebuild.py`
- **Key finding:** Only 3/99 CWM-overlapping KOs survive genus FE test (3% survival)

### NB33 Aquatic CWM
- **Files:** `projects/spatial_community_metal_models/data/nb33/`
- **Script:** `projects/spatial_community_metal_models/scripts/run_nb33_stream_ko_fwl.py`
- **Key finding:** 65–82% KO survival with genus PC1 control (CWM level)

### GlobDB Documentation
- **Location:** `/home/hmacgregor/data/envdbs/GlobDB/globdb_parquet/`
- **Citation:** r232 release with 346K genomes and 2.9B protein annotations

### Memory/Previous Analysis Notes
- See `CLAUDE.md` → BLAS thread limiting, Spark Connect pitfalls, Cgroup memory management

---

## Appendix: Freshwater Environment Classification

**Keywords matched in env_biome column:**

| Keyword | Definition | Count in GlobDB |
|---------|-----------|---|
| `freshwater` | Catch-all | 438 samples |
| `lake` | Lentic system | 2,430 samples |
| `lentic` | Still water | 1,599 samples |
| `river` | Lotic system | (included in freshwater) |
| `stream` | Small lotic | (included in freshwater) |
| `aquatic` | Generic | (included if present) |

**Excluded (marine/soil):**
- "marine", "ocean", "salt"
- "soil", "sediment", "terrestrial"
- "gut", "host", "anthropogenic"

**Final set:** 6,147 samples → 818 unique MAGs with lat/lon

---

## Troubleshooting & Known Issues

### Issue 1: KO extraction very slow

**Cause:** Streaming 23,410 row groups from 2.9B-row parquet file  
**Solution:** Run overnight or on background job. Current ETA: 12–15 hours total.

### Issue 2: Memory spikes during logistic regression

**Cause:** 818 MAGs × 529 genera one-hot matrix → dense (818 × 529 = 432K features before dropping first)  
**Solution:** Use sklearn.preprocessing.StandardScaler, fit in batches of 100 KOs at a time.

### Issue 3: Singular matrices for rare genera

**Cause:** Some genera may have <2 genomes, causing perfect separation  
**Solution:** Filter to genera with ≥2 genomes in analysis set (within-KO filter).

---

**Document compiled:** 2026-08-30 22:30 UTC  
**Status:** Analysis ready pending data extraction completion
