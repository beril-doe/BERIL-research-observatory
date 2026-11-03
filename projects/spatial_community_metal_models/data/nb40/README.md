# NB40: Stream Per-KO MAG-KO Analysis — Quick Start

This analysis tests whether the NB33 CWM signal (65–82% KO survival with community control) replicates at the MAG level using genus fixed effects, analogous to the SPIRE soil analysis.

## Quick Summary

| Metric | Value |
|--------|-------|
| **Freshwater MAGs** | 818 (GlobDB) |
| **Unique genera** | 529 |
| **Geographic regions** | EUR: 521, USA: 92, Other: 205 |
| **KOs found (via KOfam)** | ~120,000+ genome-KO pairs |
| **Expected KOs after filtering** | 5,000–10,000 |
| **Analysis type** | Logistic regression L0 (mine) vs L6 (mine + genus FE) |
| **FDR threshold** | q < 0.05 |

## Files in This Directory

### Data Files (Generated During Analysis)

1. **`globdb_freshwater_coords.parquet`** ✅ READY
   - 818 freshwater MAGs with coordinates, genus, and region
   - Columns: globdb_id, latitude, longitude, genus, region, source
   
2. **`globdb_freshwater_metadata.parquet`** ✅ READY
   - Environmental metadata per MAG
   - Columns: globdb_id, latitude, longitude, genus, region, mine_any_dist_km (placeholder), mine_exposure, ph, temperature_c
   
3. **`globdb_freshwater_ko_matrix.parquet`** 🔄 IN PROGRESS
   - Genome × KO presence/absence matrix
   - Columns: genome_id, ko_id, present, genus
   - Expected size: ~120,000 rows, ~600–800 MB
   
4. **`globdb_freshwater_analysis_matrix.parquet`** (PENDING)
   - Full matrix with covariates joined
   - Used for logistic regression at all levels
   
5. **`globdb_freshwater_l0_results.csv`** (PENDING)
   - Bivariate regression: ko_present ~ mine_exposure
   - Columns: ko_id, beta, se, p_value, odds_ratio, n_present, n_total
   
6. **`globdb_freshwater_l6_results.csv`** (PENDING)
   - Genus fixed effects: ko_present ~ mine_exposure + C(genus)
   - Same columns as L0
   
7. **`globdb_freshwater_survival_summary.csv`** (PENDING)
   - Overlap analysis: KOs significant at both L0 and L6
   - Columns: ko_id, l0_hit, l6_hit, survival, comparison_to_nb33

### Documentation Files

- **`EXPLORATION_NOTES.md`** — Data discovery summary (what's available, challenges, next steps)
- **`NB40_ANALYSIS_REPORT.md`** — Complete workflow, hypothesis, expected results, troubleshooting
- **`README.md`** — This file

## How to Run the Analysis

### If the Main Script is Still Running

The script `/home/hmacgregor/BERIL-research-observatory/projects/spatial_community_metal_models/scripts/run_nb40_stream_mag_ko_fwl.py` is currently extracting the full KO matrix from GlobDB. **Do not interrupt it.**

**Current status** (as of 2026-08-30):
```
Row groups processed: ~9,100 / 23,410 (39%)
KOs found: 120,147 unique genome-KO pairs
Estimated completion: 2026-08-31 06:00 UTC (12–15 hours from start)
```

Check progress:
```bash
tail -f projects/spatial_community_metal_models/logs/nb40_exploration.log
```

### When KO Matrix is Ready (After Step 2)

Once `globdb_freshwater_ko_matrix.parquet` is generated, the script will automatically:

1. Filter to KOs present in ≥5 genera and ≥10% of genomes
2. Build the full analysis matrix
3. Run logistic regression at L0 and L6
4. Compare to NB33 results

If the script doesn't complete, run the regression separately:

```bash
OMP_NUM_THREADS=1 python3 << 'EOF'
# (Simplified regression script to run after manual KO matrix generation)
# See bottom of run_nb40_stream_mag_ko_fwl.py for code
EOF
```

## Key Results to Expect

### Outcome A: SPIRE-Like Collapse (Most Likely)

If <5% of L0-significant KOs remain significant at L6:
- **Interpretation:** CWM signal is driven by community composition, not gene-level selection
- **Biological meaning:** You cannot separate gene effects from genus effects
- **Citation:** SPIRE soil precedent: 3/99 = 3% survival

### Outcome B: CWM Replication (Alternative)

If 50–80% of L0-significant KOs remain significant at L6:
- **Interpretation:** Genes are genuinely selected for mine proximity independent of genus
- **Biological meaning:** Gene-level adaptation exists beyond community turnover
- **Citation:** NB33 CWM precedent: 65–82% survival

## What's Missing (Placeholder)

### Mine Proximity Distances

Currently set to max distance (5,000 km) as placeholder. To complete properly:

1. **Get mindat mine database**
   - Download from mindat.org or use pre-computed from SPIRE soil project
   - Reference: `projects/per_ko_metal_associations/` (check if mindat parquet exists)

2. **Spatial join to freshwater MAG coordinates**
   - Use GeoPandas or PostGIS nearest-neighbor
   - Compute minimum distance to any mine
   - Columns: globdb_id, mine_any_dist_km

3. **Update metadata**
   - Replace `mine_any_dist_km` column in `globdb_freshwater_metadata.parquet`
   - Re-run logistic regression

**Command reference:**
```bash
# See projects/spatial_community_metal_models/scripts/compute_upstream_mine_dist.py
python3 compute_upstream_mine_dist.py --input globdb_freshwater_coords.parquet
```

## Comparison Table

| Aspect | SPIRE Soil | NB33 Aquatic CWM | NB40 Aquatic MAG |
|--------|-----------|------------------|------------------|
| **MAGs** | 2,477 | 45,795 samples | 818 |
| **Data source** | USGS soil cores | MicrobeAtlas 16S | GlobDB shotgun |
| **KOs tested** | 4,759 | 10,683 | ~5,000–10,000 |
| **Analysis type** | Logistic regression + genus FE | FWL + genus PC1 | Logistic regression + genus FE |
| **L0→L6 survival** | 3.3% | 65–82% | ??? (This analysis) |

## Troubleshooting

### Script is Very Slow (Still at Row 9,100/23,410)

**Expected.** The GlobDB protein annotation parquet is 2.9 billion rows × 23,410 row groups. Streaming takes ~12–15 hours total.

**Options:**
1. Let it run (safe, eventually completes)
2. Kill and re-run with sampling (faster, may miss some KOs)
3. Use pre-computed GlobDB genus-KO prevalence if available

### Logistic Regression Fails (Singular Matrix)

**Cause:** Some genera have <2 genomes, causing perfect separation.

**Fix:** The script filters to genera with ≥2 genomes per KO before fitting. Check the covariance matrix conditioning.

### Memory Spikes During Regression

**Cause:** Fitting 529-dimensional model (one per genus) for 5,000+ KOs.

**Solution:** Already handled in script via chunked processing and StandardScaler. If still issues, reduce to top 2,000 KOs by prevalence.

## Contact & Context

- **Thesis arc:** This is Part 3 (turnover vs gene gain) of the metal ecology thesis
- **Related projects:**
  - `projects/per_ko_metal_associations/` — SPIRE soil (precedent)
  - `projects/spatial_community_metal_models/` — Parent analysis
  - NB33 in same project — CWM baseline
- **Key question:** Does gene-level adaptation exist in streams, or is it taxonomic co-variation?

## Next Steps After Analysis

1. **Write NB40 summary** in parent `REPORT.md`
2. **Compare to NB33:** survival rate, overlap, geographic patterns
3. **Integrate into thesis:** Part 3 narrative (turnover vs gene gain)
4. **Create figures:** Manhattan plot, Q-Q plot, effect size distribution
5. **Consider replication:** Can we validate findings in soil (SPIRE) freshwater genomes?

---

**Analysis scaffold created:** 2026-08-30  
**Expected completion:** 2026-08-31 midday  
**Status:** Data extraction in progress; logistic regression ready to run
