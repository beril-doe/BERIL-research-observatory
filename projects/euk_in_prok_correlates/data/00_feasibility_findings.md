# Phase A Exploration — Data Feasibility Findings

_Generated 2026-07-10. Source probes: `src/probe1.py`–`src/probe7.py` (run on-cluster via `get_spark_session`)._

## Response variable — eukaryotic read fraction per metagenome

NMDC read-based taxonomy is in `kbase.nmdc_arkin`, tidy format, joinable by `file_id`:

| Table | Key columns | Domain resolution | # metagenome files |
|---|---|---|---|
| `gottcha_gold` | `rank`,`label`,`taxid`,`abundance`,`read_count`,`file_id` | superkingdom (Bacteria/Archaea/Eukaryota/Eukaryota(plastid)/Viruses) | 3,354 |
| `kraken_gold` | `rank`,`name`,`percent`,`clade_reads`,`lineage`,`file_id` | superkingdom → **kingdom** (Metazoa/Viridiplantae/Fungi separable) | 3,579 |
| `centrifuge_gold` | `rank`,`label`,`numReads`,`abundance`,`lineage`,`file_id` | superkingdom | 3,577 |

**Eukaryotic signal is real and variable.** GOTTCHA superkingdom labels across files:
Bacteria 3319 · Viruses 1290 · **Eukaryota (plastid) 1162 (~35%)** · Archaea 469 · **Eukaryota 359 (~11%)**.

GOTTCHA euk-fraction (Eukaryota+plastid abundance / total) distribution over 3,354 files:
`0`: 1833 (55%) · `<1%`: 372 · `1–5%`: 377 · `5–20%`: 352 · **`>20%`: 420 (12.5%)**.

Kraken's kingdom rank additionally separates **Metazoa (host/animal), Viridiplantae (plant), Fungi** — lets us attribute contamination *source*, not just amount.

## Linkage chain (confirmed working)

```
gottcha/kraken/centrifuge_gold.file_id  (nmdc:dobj-11-*)
  → kbase.nmdc_arkin.omics_files_table (.file_id → .sample_id, .omics_processing_id, .study_id)   [385,562 rows]
    → nmdc.metadata.biosample_set.id                          [99.7% join: 5,853 / 5,871 samples]
    → nmdc.metadata.data_generation_set (via *_has_input.has_input = sample_id, join on parent_id)
    → nmdc.metadata.material_processing_set (via *_has_input)
```

5,871 distinct biosamples sit behind the classified files; **5,853 (99.7%) join to `biosample_set`.**
(The bsm-11 vs bsm-13 minting-code difference is cosmetic — the join works.)

## Predictor coverage among 5,853 classified biosamples

| Predictor (lit rank) | NMDC column(s) | Coverage | Verdict |
|---|---|---|---|
| **Environment / matrix (#1)** | `env_medium_term_name`, `env_broad_scale_term_name` | **5,512 (94%)** | ✅ well-powered |
| **Ecosystem type/category (#1)** | `ecosystem_type`, `ecosystem_category` | **5,203 (89%)** | ✅ well-powered |
| Sample collection device | `samp_collec_device` | 3,716 (63%) | ✅ usable |
| **Sequencing platform (#5)** | `instrument_set.model` (via data_generation) | 982 (17%) | ⚠️ partial (novaseq_6000/novaseq/hiseq_2500 clean where present) |
| Depth | `depth_has_numeric_value` | 517 (9%) | ⚠️ sparse |
| Sample size / biomass proxy | `samp_size_has_numeric_value` | 516 (9%) | ⚠️ sparse |
| Host | `host_taxid_term_name` / `host_name` | 158 (3%) | ⚠️ sparse (soil-dominated cohort) |
| **DNA extraction (#3)** | `material_processing_set.extraction_targets` | 76 (~1%) | ❌ not usable |
| **Size fractionation / filtration (#5, Tara lever)** | `size_frac_*`, `filter_pore_size_*` | **0** | ❌ not captured |
| Sample material processing | `samp_mat_process_term_name` | **0** | ❌ not captured |
| **Library prep / host-depletion (#2)** | `library_preparation_kit`, `library_type` | **0** | ❌ not captured |

### Ecosystem_category of classified samples
Terrestrial 4,467 · Aquatic 571 · Plants 148 · Artificial 17 · null 650. Soil-dominated but real cross-biome spread.

## Bottom line
- **Testable now, at n≈5,000, from NMDC alone:** environment/matrix, ecosystem type, collection device; platform at n≈1,000.
- **NOT testable from NMDC:** size fraction, extraction kit, host-depletion method, library prep, lysis — NMDC leaves these slots empty. These are exactly the wet-lab factors ranked #2–3 in the literature and would require user-supplied protocol metadata or a second collection.
- Candidate external levers in BERDL: `refdata.tara_ocean` (size-fractionated by design), `refdata.jgi_gem` / `smag` / `spire` (MAG metadata), `refdata.emp_16s`. External: SPF (Eisenhofer/Woodcroft 2026) prokaryotic-fraction for 136K metagenomes.
