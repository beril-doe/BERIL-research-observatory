# Research Plan: Pan-Bacterial Anti-Phage Defense Arsenal — Distribution, Arms Race, and Syndromes

## Research Question

Across the 293K-genome BERDL pangenome, how are the seven major anti-phage defense system families (CRISPR-Cas, restriction-modification, CBASS, Gabija, Retron, BREX, DISARM) distributed at the species level; does species-level defense-system count scale with prophage burden (the coevolutionary arms-race prediction); and which system combinations co-occur beyond phylogenetic expectation, defining "defense syndromes" that may represent mobile defense islands?

## Hypothesis

- **H0**: Anti-phage defense system counts are randomly distributed with respect to prophage burden and to each other after controlling for phylogeny and genome size — i.e., there is no evidence of an arms race or of systems co-occurring beyond random.
- **H1a (arms race)**: After controlling for genome size and host phylum, species-level anti-phage defense-system counts are positively correlated with per-species prophage burden (module presence from `projects/prophage_ecology/src/prophage_utils.py` reclassification).
- **H1b (syndromes)**: Specific defense-system combinations (e.g., CRISPR-Cas + R-M, CBASS + Gabija, BREX + DISARM) co-occur at species level more often than expected under a null model that preserves phylum composition and per-system marginal prevalence — consistent with mobile defense-island transfer.
- **H1c (accessory-genome enrichment)**: Defense systems are enriched in the accessory genome (`is_auxiliary` and `is_singleton`) relative to the pangenome-wide accessory fraction, consistent with horizontal mobility being a hallmark of defense.

## Literature Context

Anti-phage defense diversity has expanded dramatically since 2018 with systematic discovery of tens of new families — Gabija, Thoeris, Kiwa, Druantia, Wadjet, Zorya (Doron et al. 2018, Science 359:eaar4120); CBASS (Cohen et al. 2019, Nature 574:691; Millman et al. 2020, Nat Microbiol 5:1608); BREX (Goldfarb et al. 2015, EMBO J 34:169); DISARM (Ofir et al. 2018, Nat Microbiol 3:90); retrons as anti-phage systems (Millman et al. 2020, Cell 183:1551). DefenseFinder (Tesson et al. 2022, Nat Commun 13:2561) and PADLOC (Payne et al. 2021, NAR 49:10868) consolidated ~30–130 systems into HMM-based detection rules. Meta-surveys (Tesson et al. 2022; Vassallo et al. 2022, Nat Microbiol 7:1568) established that bacterial genomes carry ~5 defense systems on average, that most defense systems concentrate in mobile defense islands, and that gene content varies substantially across phyla and lifestyles.

The arms-race prediction is longstanding (Stern & Sorek 2011, BioEssays 33:43; Koskella & Brockhurst 2014, FEMS Microbiol Rev 38:916): higher phage pressure → higher defense investment. Empirical tests at pangenome scale are scarce because they require harmonized defense-system and prophage calls on the same genome set. The BERDL pangenome (293K genomes, 27,690 species, uniformly re-annotated) provides the substrate for such a test at unprecedented scale. Rocha & Bikard (2022, PLoS Biol 20:e3001514) proposed that "defense islands" — clusters of co-occurring defense systems — are the ecological units of defense diversity. Sanchez-Serrano et al. (2024, mBio) showed BREX + DISARM + R-M co-occur significantly in Enterobacteria; whether such syndromes are pan-bacterial is open.

Prior BERDL work on defense: `snipe_defense_system` (single system, DUF4041+GIY-YIG) established the methodology of Pfam-based defense detection using `eggnog_mapper_annotations` (though eggNOG v6 misses most 2018+ discoveries) and `bakta_pfam_domains`. This project extends to a 7-system panel using `interproscan_domains` as the primary detection table (validated broader coverage).

### Key References

- Doron S et al. (2018) Science 359:eaar4120
- Cohen D et al. (2019) Nature 574:691
- Millman A et al. (2020) Cell 183:1551
- Goldfarb T et al. (2015) EMBO J 34:169
- Ofir G et al. (2018) Nat Microbiol 3:90
- Tesson F et al. (2022) Nat Commun 13:2561 (DefenseFinder)
- Payne LJ et al. (2021) NAR 49:10868 (PADLOC)
- Vassallo CN et al. (2022) Nat Microbiol 7:1568
- Rocha EPC, Bikard D (2022) PLoS Biol 20:e3001514
- Koskella B, Brockhurst MA (2014) FEMS Microbiol Rev 38:916
- Sanchez-Serrano et al. (2024) mBio (BREX+DISARM+R-M syndromes)

## Defense System Detection Rules

Detection is on a per-`gene_cluster_id` basis via `interproscan_domains` (primary, 833M rows, ~24K Cas1 hits confirmed) and `eggnog_mapper_annotations` (secondary, description-based, best for R-M). A system is **called present in a species** iff at least one gene cluster with a required marker (or combination) is present in the pangenome for that species.

| System | Required markers | Notes |
|---|---|---|
| **CRISPR-Cas** | PF01867 (Cas1) OR PF09707 (Cas2) via `interproscan_domains` | Cas1 is universal; subtype by PF18019 (Cas3, Type I), PF22702/PF16595 (Cas9, Type II), PF22335 (Cas10, Type III), PF07282 (Cas12, Type V). |
| **R-M Type II** | eggNOG `Description LIKE '%type ii restriction%'` OR `%type-2 restriction%` | 27,663 clusters; well-detected via eggNOG. |
| **R-M Type I** | eggNOG `Description LIKE '%type i restriction%'` OR PFAMs contain HsdR/HsdM/HsdS | 245,609 clusters. |
| **CBASS** | PF14090 (SAVED) OR PF18178 (CD-NTase) OR PF19918 (Cap6) | Highly specific effectors. 2,558 + 283 + 155 clusters. |
| **Gabija** | PF20473 (GajA OLD_TOPRIM_C) | 12,941 clusters. GajA anchor avoids the widespread UvrD false-positive. |
| **Retron** | PF00078 (RVT_1) AND co-occurrence with retron-specific effector Pfams (msr/msd context, coding contig proximity) | RVT_1 alone (72K clusters) is not retron-specific — must intersect with retron effector Pfam list (Millman 2020 Cell, Table S1). |
| **BREX** | Any of PF08843 (PglZ), PF13175 (BrxC), PF13401 (BrxL) present in same species | 43,816 + 55,701 + 41,545 clusters. PglZ is diagnostic. |
| **DISARM** | PF13091 (DrmC PLD) AND co-occurrence with DrmB SNF2 helicase in same species | PLD alone (106K clusters) is broad — needs DrmB (PF00176) anchor. |

Detection feasibility (raw hit counts) recorded in `data/detection_feasibility.csv`.

## Query Strategy

### Tables Required

| Table | Purpose | Rows | Filter Strategy |
|---|---|---|---|
| `kbase_ke_pangenome.interproscan_domains` | Primary Pfam-based defense detection | 833M | Filter `analysis = 'Pfam' AND signature_acc IN (defense_pfam_list)`; anti-join to `gene_cluster` on `gene_cluster_id` |
| `kbase_ke_pangenome.eggnog_mapper_annotations` | Secondary; R-M and CRISPR-Cas description-based confirmation | 93M | Filter by `LIKE '%crispr%'`, `%restriction%`, etc.; join on `query_name = gene_cluster.gene_cluster_id` |
| `kbase_ke_pangenome.bakta_pfam_domains` | Cross-validation of Pfam calls (Bakta uses narrower Pfam subset) | 18.8M | Filter by versioned `pfam_id LIKE 'PFXXXXX.%'` |
| `kbase_ke_pangenome.gene_cluster` | Species mapping + core/aux/singleton flags | 132M | Filter by `gene_cluster_id` from detection step; used to build species × system matrix |
| `kbase_ke_pangenome.pangenome` | Per-species pangenome stats (total cluster count, is_core count) | 27,702 | Safe to scan |
| `kbase_ke_pangenome.genome` | Per-genome → species mapping; sequenced-genome counts per species | 293K | Safe to scan |
| `kbase_ke_pangenome.gtdb_taxonomy_r214v1` | Phylum-level taxonomy for stratification | 293K | Safe to scan |
| `kbase_ke_pangenome.gtdb_metadata` | Genome size and CheckM completeness — arms-race covariates | 293K | Safe to scan |
| `kbase_ke_pangenome.gtdb_species_clade` | ANI stats, needed to validate pangenome grouping | 27,690 | Safe to scan |

### Key Queries

1. **Extract Pfam-based defense hits** (single query, results cached to Parquet):
```sql
SELECT ipr.gene_cluster_id, ipr.signature_acc, ipr.signature_desc, gc.gtdb_species_clade_id,
       gc.is_core, gc.is_auxiliary, gc.is_singleton
FROM kbase_ke_pangenome.interproscan_domains ipr
JOIN kbase_ke_pangenome.gene_cluster gc ON ipr.gene_cluster_id = gc.gene_cluster_id
WHERE ipr.analysis = 'Pfam'
  AND ipr.signature_acc IN (
    'PF01867','PF09707','PF18019','PF22702','PF16595','PF22335','PF07282',  -- CRISPR-Cas
    'PF14090','PF18178','PF19918',                                             -- CBASS
    'PF20473',                                                                 -- Gabija (GajA-specific)
    'PF00078',                                                                 -- Retron RT (broad; needs context)
    'PF08843','PF13175','PF13401',                                             -- BREX
    'PF13091','PF00176'                                                        -- DISARM (PLD + DrmB context)
  )
```

2. **Extract eggNOG-based R-M and CRISPR confirmations**:
```sql
SELECT gc.gene_cluster_id, gc.gtdb_species_clade_id, gc.is_core, gc.is_auxiliary, gc.is_singleton,
       e.Description, e.PFAMs, e.COG_category
FROM kbase_ke_pangenome.gene_cluster gc
JOIN kbase_ke_pangenome.eggnog_mapper_annotations e ON gc.gene_cluster_id = e.query_name
WHERE lower(e.Description) LIKE '%type ii restriction%'
   OR lower(e.Description) LIKE '%type i restriction%'
   OR lower(e.Description) LIKE '%crispr%'
   OR lower(e.PFAMs) LIKE '%hsdr%' OR lower(e.PFAMs) LIKE '%hsdm%' OR lower(e.PFAMs) LIKE '%hsds%'
```

3. **Reuse prophage_ecology classifier for prophage burden**:
```python
from projects.prophage_ecology.src.prophage_utils import build_spark_where_clause  # 7 module WHERE clause
# Reclassify prophage clusters, aggregate to species-level module presence
```

### Performance Plan

- **Tier**: JupyterHub Spark (on-cluster, direct catalog access).
- **Estimated complexity**: Moderate. The single Pfam-filtered join with a modest signature_acc IN-list is well-indexed and completes in a few minutes. Prophage reclassification is heavier (~93M-row description filter) but was already validated in `prophage_ecology`.
- **Known pitfalls**:
  - `interproscan_domains.signature_acc` for Pfam is versionless (`PF01867`) — do NOT append version suffix like `bakta_pfam_domains` requires (`PF01867.29`). Cross-checked in Phase A.
  - eggNOG `PFAMs` stores domain NAMES, not accessions (validated in `snipe_defense_system`).
  - `gtdb_species_clade_id` contains `--` which is a SQL comment — use `LIKE` with equality prefix or single-string equality, not `IN (...)`.
  - Some broad-Pfam systems (Retron RVT_1, DISARM PLD, Gabija UvrD) require operon-context filtering — do the anchor-only detection first, then post-filter by co-occurrence with the specificity partner in the same species. Do not use the broad Pfam alone.
  - Genome-size covariate matters: bigger genomes tend to have more defense systems (Vassallo 2022). All arms-race regressions must control for `gtdb_metadata.genome_size`.
  - Species must have ≥5 genomes to reliably call a system as "core" vs "accessory" — filter `pangenome.no_genomes >= 5`.

## Analysis Plan

### Notebook 00: Exploration & Feasibility (`00_exploration.ipynb`)
- **Goal**: Document Phase-A detectability check (already captured in `data/detection_feasibility.csv`); verify per-species pangenome sizes and Pfam version handling.
- **Expected output**: Confirmation counts, summary table.

### Notebook 01: Defense-System Cluster Extraction (`01_extract_defense_clusters.ipynb`)
- **Goal**: Run the two extraction queries above; cache to `data/defense_gene_clusters.tsv.gz` (columns: `gene_cluster_id`, `system`, `subtype`, `marker_pfam`, `gtdb_species_clade_id`, `is_core`, `is_auxiliary`, `is_singleton`).
- **Broad-Pfam post-filter**: For Retron/DISARM/Gabija-UvrD, require anchor+partner co-occurrence at species level.
- **Expected output**: `data/defense_gene_clusters.tsv.gz` (~200K–500K clusters expected); per-system cluster counts table.

### Notebook 02: Species × System Matrix (`02_species_system_matrix.ipynb`)
- **Goal**: Aggregate cluster hits to per-species (long-form and wide matrix). Add phylum, genome_size (median across genomes), no_genomes, and total pangenome cluster count as covariates.
- **Expected output**: `data/species_defense_matrix.tsv.gz` (~27K species × 7 systems + subtypes + covariates); `figures/system_prevalence_by_phylum.png`.

### Notebook 03: Prophage Burden Reclassification (`03_prophage_burden.ipynb`)
- **Goal**: Import `prophage_utils.build_spark_where_clause()` from `prophage_ecology`; classify prophage gene clusters into 7 modules; aggregate to per-species module-presence indicator (module count out of 7). Save as `data/species_prophage_burden.tsv.gz`.
- **Expected output**: `data/species_prophage_burden.tsv.gz` (~27K species × prophage module indicators + total count).

### Notebook 04: Arms-Race Test (`04_arms_race.ipynb`)
- **Goal**: Join species-level defense counts and prophage burden; test correlation of defense-system count vs prophage module count. Primary model: partial Spearman correlation controlling for `log10(genome_size)` and phylum. Secondary: negative-binomial regression `defense_count ~ prophage_count + log10(genome_size) + phylum`.
- **Expected output**: `data/arms_race_results.tsv`, `figures/arms_race_scatter.png` (defense_count vs prophage_count colored by phylum), `figures/partial_correlation_barplot.png` (per-phylum partial ρ).

### Notebook 05: Defense Syndromes (`05_defense_syndromes.ipynb`)
- **Goal**: Test which system pairs (and triples) co-occur beyond random. Null model: fixed marginal per system and per phylum, permuted species-level assignments (1,000 permutations). Compute empirical odds ratio + p-value per pair. Cluster systems by co-occurrence (hierarchical, Jaccard).
- **Expected output**: `data/syndrome_pairs.tsv` (pairwise OR, p, q), `figures/syndrome_heatmap.png`, `figures/syndrome_network.png`.

### Notebook 06: Accessory-Genome Enrichment (`06_accessory_enrichment.ipynb`)
- **Goal**: Test whether defense systems are enriched in the accessory pangenome (H1c). Compute per-system core/auxiliary/singleton fractions; compare to background pangenome-wide fraction with χ² tests.
- **Expected output**: `data/accessory_enrichment.tsv`, `figures/core_vs_accessory_by_system.png`.

## Expected Outcomes

- **If H1a supported (arms race)**: Positive partial correlation between species-level defense-system count and prophage burden after controlling for genome size and phylum. Effect size and cross-phylum consistency indicate whether the arms race is a universal or lineage-restricted pattern.
- **If H1b supported (syndromes)**: One or more system pairs (candidate: CBASS+Gabija, BREX+DISARM, R-M+CRISPR) co-occur significantly more than expected under the null. Cluster analysis will reveal whether systems partition into distinct "syndrome" families.
- **If H1c supported (accessory)**: Systems are enriched in `is_auxiliary`/`is_singleton` gene-cluster classes, consistent with mobile defense-island transfer being the dominant transmission mode.
- **If H0 not rejected**: Defense counts are randomly distributed with respect to prophage burden and to each other — this would imply that defense diversity is driven by phylogeny/genome-size effects, not by direct phage-selective pressure at the ecological/HGT timescale.
- **Potential confounders**:
  - Pfam detection sensitivity varies by system age — recently characterized systems have narrower profiles.
  - Some Pfams (UvrD, RVT_1, PLD, SNF2) are widespread; anchor+context filtering is essential.
  - Prophage burden inferred from eggNOG description matches is coarse (validated in `prophage_ecology` but sensitivity is ~unknown).
  - Genome-size covariate captures both bigger-genome-more-genes effect AND life-history correlates (free-living vs host-restricted) — partial-correlation results should be interpreted with this in mind.
  - Species with <5 genomes have unstable core/accessory calls — restrict arms-race and syndrome analyses to species with `no_genomes >= 5` (~11K species).

## Revision History

- **v1** (2026-07-15): Initial plan. Phase A detectability check confirmed all 7 systems detectable via `interproscan_domains` (primary) + `eggnog_mapper_annotations` (secondary). Scope locked at 7 focused families; third-pillar emphasis on defense syndromes over environment.
- **v3** (2026-07-16, post-hoc, no re-analysis): Artifact-format switch from Parquet to gzip TSV. The plan specified caching intermediate outputs as Parquet, but Spark Connect writes go to cluster storage (S3), not the client-side notebook filesystem — a `df.write.parquet(local_path)` call produces only an empty `_SUCCESS` marker locally. Standard on-cluster pattern is `.toPandas()` then `pandas.to_csv(..., compression="gzip")`. All `.parquet` references in the Analysis Plan sections above have been updated to `.tsv.gz` to match the actual artifacts (`data/defense_gene_clusters.tsv.gz`, `data/species_defense_matrix.tsv.gz`, `data/species_prophage_burden.tsv.gz`). Captured as a performance-note pitfall in `REPORT.md`.
- **v2** (2026-07-16, post-hoc, no re-analysis): Deviation from the plan's Retron specificity rule recorded. The plan specified filtering RVT_1 hits by co-occurrence with retron-specific effector Pfams (Millman 2020, Cell 183:1551, Table S1). The implementation in NB02 instead defines `Retron_stringent` as RVT_1 present AND ≥1 other narrow defense system present in the species — a *defense-context* proxy rather than a *retron-specificity* filter. Because narrow defense systems are near-universal across species carrying RVT_1, this filter drops only 11 of 15,109 candidate species (Retron_candidate 15,109 vs Retron_stringent 15,098). Downstream results for Retron (arms-race, syndrome, accessory) should be interpreted as "reverse-transcriptase in defense-syndrome context," not "characterized retron systems." A subsequent refinement adopting the Millman-2020-effector Pfam set would sharpen specificity; the qualitative conclusions (arms race supported, syndromes supported) are not expected to change but effect sizes for Retron pairs may shift. Documented in `REPORT.md` §Limitations.

## Authors

- Justin Reese ([0000-0002-2170-2250](https://orcid.org/0000-0002-2170-2250)), LBL
