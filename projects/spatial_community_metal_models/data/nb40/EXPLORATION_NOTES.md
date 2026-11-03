# NB40: Stream MAG-KO Analysis — Data Exploration Report

**Date:** 2026-08-30  
**Task:** Test whether NB33 CWM signal (65–82% KO survival with genus PC1 control) replicates at MAG level with genus fixed effects  
**Status:** Data exploration complete; full MAG × KO matrix extraction in progress  

---

## Summary of Findings

### 1. Freshwater MAG Availability

**GlobDB freshwater MAG inventory:**
- **Total freshwater samples with coordinates:** 6,147
- **Freshwater MAGs (unique genomes):** 818
- **Unique genera:** 529

**Geographic distribution:**
| Region | Count | %  |
|--------|-------|-----|
| EUR    | 521   | 63.7% |
| USA    | 92    | 11.2% |
| OTHER  | 205   | 25.1% |

**Data sources:**
- MOTU (Genomics Standards Consortium): 736 MAGs (90%)
- CRLG (China Rare Loess Geochemical): 82 MAGs (10%)

### 2. GlobDB Data Structure

**Protein annotations parquet:**
- **Total row groups:** 23,410
- **Total rows:** 2.9 billion
- **Columns:** gene_callers_id, source, accession, function, e_value, genome_id
- **Source types:** KOfam, Pfam, COG, eggNOG, etc.
- **KO format in accession column:** K##### (e.g., K00941)

**Key discovery:** The GlobDB protein_annotations_all.parquet is organized by genome ID, but the parquet file is NOT filtered by environment type. We must scan all 23,410 row groups to find the 818 freshwater MAGs. This is computationally expensive (~6–12 hours per full scan).

### 3. GlobDB Freshwater KO Distribution (Partial)

From the first ~4,000 row groups (17% of file):
- **KOs found:** 120,147 unique genome-KO pairs
- **Expected for full file:** ~700,000–800,000 pairs

### 4. Environmental Metadata Available

From globdb_sample_coordinates.parquet:
- **pH:** Available for 818 freshwater samples, mean = (to be calculated)
- **Temperature:** Very sparse for freshwater (historical data limitation)
- **Elevation/Depth:** Sparse for stream samples
- **env_biome keywords matched:**
  - "freshwater lake" (2,430 samples)
  - "freshwater biome" (438 samples)
  - "lentic water body" (1,599 samples)
  - "Brackish water" (359 samples)
  - Other freshwater-related terms

### 5. Mine Proximity Data

**Status:** NOT YET COMPUTED

To complete the analysis, we need:
1. **Mindat mine locations:** Global database of ore deposits
2. **Spatial join:** GlobDB freshwater MAG coordinates → nearest mine
3. **Distance transformation:** log₁₀(1 / (dist_km + 0.1))

Currently created as placeholder in script (max 5000 km distance). This is essential for the exposure variable in logistic regression.

---

## Comparison to Previous CWM Analysis (NB33)

| Metric | NB33 CWM | NB40 MAG (expected) |
|--------|----------|-----|
| Data type | 16S community-weighted means | Metagenome-assembled genomes (actual presence/absence) |
| Sample type | Aquatic MicrobeAtlas (16S) | GlobDB (shotgun sequencing) |
| EUR samples | ~40,000 | ~521 MAGs |
| USA samples | ~70,000 | ~92 MAGs |
| KOs tested at L0 | 8,260 (EUR), 8,110 (USA) | Expected: 5,000–10,000 |
| L6 survival (L6 FDR hits / L0 FDR hits) | 65% (EUR), 82% (USA) | **To be determined** |

**Key difference:** NB33 uses genus-level KO *prevalence* (fraction of genomes in that genus carrying the KO) averaged across the community. NB40 tests MAG *presence/absence* directly with genus fixed effects.

**Hypothesis:** If the CWM signal is driven by genuine MAG-level adaptation, we should see 50–80% survival at MAG level (like CWM). If the signal is a co-variation artifact (many genes co-segregate with community composition), survival should collapse to <5% (like SPIRE soil: 3/99 = 3%).

---

## Computational Challenges

1. **Large parquet file (2.9 billion rows):** Scanning protein_annotations_all.parquet takes ~6–12 hours for full row-group streaming
2. **Memory constraints:** 128-CPU machine with 24 GB JupyterHub cgroup → need chunked processing
3. **Logistic regression at scale:** ~5,000–10,000 KOs × 818 genomes → ~40M model fits needed
   - **Solution:** Statsmodels or scikit-learn logistic regression with parallel pool (12 workers)
   - **Time estimate:** 2–4 hours for full L0 + L6 analysis

---

## Next Steps

1. **Complete full GlobDB scan** (currently running via `run_nb40_stream_mag_ko_fwl.py`)
   - Expected completion: ~6–12 hours from start
   - Output: `globdb_freshwater_ko_matrix.parquet`

2. **Compute mine proximity**
   - Fetch mindat mine locations (global ore deposits)
   - Spatial nearest-neighbor join with GlobDB freshwater MAG coordinates
   - Output: `globdb_freshwater_mine_distances.parquet`

3. **Run logistic regression (L0 and L6)**
   - L0: `ko_present ~ log_mine_proximity` (bivariate)
   - L6: `ko_present ~ log_mine_proximity + C(genus)` (genus fixed effects)
   - Include environment covariates (pH, if available)
   - Output: `globdb_freshwater_l0_results.csv`, `globdb_freshwater_l6_results.csv`

4. **Compare to NB33 CWM results**
   - Overlap of significant KOs between L0 and L6
   - Calculate survival rate: % of L0 FDR hits that remain FDR<0.05 at L6
   - **Expected outcome:** <5% (SPIRE-like collapse) OR 50–80% (genuine adaptation)

---

## Data Files Created

| File | Size | Purpose |
|------|------|---------|
| `globdb_freshwater_coords.parquet` | ~100 KB | 818 freshwater MAGs with lat/lon, genus, region |
| `globdb_freshwater_metadata.parquet` | ~50 KB | Metadata: pH, temperature, mine distance (when computed) |
| `globdb_freshwater_ko_matrix.parquet` | *In progress* | genome_id × ko_id × present matrix |
| `globdb_freshwater_analysis_matrix.parquet` | *To generate* | Full matrix with covariates joined |

---

## References

- **SPIRE soil precedent:** `projects/per_ko_metal_associations/data/spire_all_ko_matrix.parquet`
  - 2,477 soil MAGs, 4,759 KOs, logistic regression results in `spire_adj_ko_associations.csv`
  - Only 3/99 CWM-overlapping KOs survived MAG-level genus fixed effects test
- **NB33 CWM results:** `projects/spatial_community_metal_models/data/nb33/`
  - 65% (EUR) and 82% (USA) KO survival at L6 with genus PC1 control
- **GlobDB metadata:** `/home/hmacgregor/data/envdbs/GlobDB/globdb_parquet/`
  - 346K total genomes, 195.5K with coordinates
  - 118K genomes with GTDB genus assignment

---

## Command to Resume

If the full scan needs to be resumed or run on a schedule:

```bash
OMP_NUM_THREADS=1 python3 projects/spatial_community_metal_models/scripts/run_nb40_stream_mag_ko_fwl.py \
  > projects/spatial_community_metal_models/logs/nb40_full_scan.log 2>&1 &
```

Current status: Running (as of 2026-08-30 22:16 UTC), at row group ~4,000/23,410.
