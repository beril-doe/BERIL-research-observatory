# Research Plan: Metadata Correlates of Eukaryotic Contamination in NMDC Prokaryote-Targeted Metagenomes

## Research Question
Among ~3,500 NMDC shotgun metagenomes collected for prokaryotic community analysis, which
**sample-collection, environmental, and sequencing metadata factors** most strongly predict the
**eukaryotic read fraction** (host, plant, fungal, protist, plastid) — and how much of the
variance in eukaryotic contamination is explained by *where/how a sample was collected* versus
left unexplained (the unmeasured wet-lab residual)?

## Hypothesis
- **H0**: Eukaryotic read fraction is not systematically associated with sample matrix,
  ecosystem, collection device, sequencing platform, or read depth — variation is idiosyncratic
  / dominated by unmeasured protocol factors.
- **H1a (matrix)**: Eukaryotic fraction differs systematically by sample matrix / ecosystem,
  highest in plant-associated, rhizosphere, and vegetated-terrestrial samples and lowest in
  groundwater / engineered / open-water samples.
- **H1b (source attribution)**: The *composition* of the eukaryotic signal tracks environment —
  plastid/plant signal in vegetated terrestrial & plant-associated samples, Metazoan (host)
  signal in host-associated samples, resolvable by combining classifiers.
- **H1c (upstream, not sequencing)**: After adjusting for matrix, sequencing platform and read
  depth add little explanatory power — contamination is set at collection, not at sequencing.

## Literature Context
Full citations in `references.md`. Sample matrix/biome is the strongest, most scalable reported
driver (SPF, Eisenhofer/Alberdi/Woodcroft 2026, 136K metagenomes — prokaryotic fraction varies
biome-by-biome). Host-DNA depletion method and extraction kit are large levers but are wet-lab
factors **not captured in NMDC metadata**. Microbial biomass is a master modifier (Salter 2014).
**Identified gap**: no published study regresses *measured eukaryotic read fraction* against the
full set of upstream collection/sequencing metadata across a public multi-biome collection; SPF
relates prokaryotic fraction to biome only. This project fills the matrix/collection portion of
that gap with NMDC.

## Query Strategy

### Tables Required
| Table | Purpose | Est. rows | Filter strategy |
|---|---|---|---|
| `kbase.nmdc_arkin.gottcha_gold` | **Primary** euk signal (Eukaryota + plastid) | ~480K | `rank='superkingdom'`; group by `file_id` |
| `kbase.nmdc_arkin.kraken_gold` | Metazoa (host) source + robustness | ~29M | `rank IN ('superkingdom','kingdom')` |
| `kbase.nmdc_arkin.centrifuge_gold` | Eukaryota robustness | ~26M | `rank='superkingdom'` |
| `kbase.nmdc_arkin.omics_files_table` | `file_id`→`sample_id`,`study_id` bridge | 385,562 | join key only |
| `nmdc.metadata.biosample_set` | Matrix/env/collection predictors (wide MIxS) | ~10^5 | select ~12 columns only; never `SELECT *` |
| `nmdc.metadata.data_generation_set*` | Sequencing platform (subset) | — | via `*_has_input.has_input=sample_id`, join `parent_id` |
| `nmdc.metadata.instrument_set` | Platform model/vendor | small | `id = instrument_used` |

### Response variable
Per `file_id`, **relative eukaryotic abundance** =
`SUM(abundance WHERE label LIKE 'Eukaryota%') / SUM(abundance)` from `gottcha_gold` at
`rank='superkingdom'` (GOTTCHA `abundance` is within-sample relative, sums ≈ 1). Aggregate to
biosample (mean across that sample's metagenome files). Companion source variables:
plastid-only fraction (GOTTCHA), Metazoa fraction (Kraken kingdom), Eukaryota fraction
(Centrifuge). Distribution is zero-inflated (~55% zero, 12.5% > 20%).

### Predictors
`env_medium_term_name`, `env_broad_scale_term_name`, `ecosystem_category/type/subtype` (94/89%
coverage), `samp_collec_device` (63%), sequencing `instrument model` (~17%, n≈1,000),
`depth_has_numeric_value` (9%). `study_id` retained as a batch/random-effect blocking variable.

### Performance Plan
- **Tier**: JupyterHub Spark SQL (on-cluster, `get_spark_session()`).
- **Complexity**: moderate. Aggregate classifier tables to one row per `file_id` **before**
  joining to the wide `biosample_set` (select only needed columns). Never `SELECT *` on
  `biosample_set` (~1,400 columns). Final analysis table (~5,800 rows) → pandas for modeling.
- **Known pitfalls** (see `memories/pitfalls.md`): Kraken DB is prokaryote-restricted — do not
  use it for total euk fraction; NMDC child tables join on `parent_id`; bridge via
  `omics_files_table` (99.7%).

## Analysis Plan

### Notebook 00: Response-variable construction & classifier concordance
- **Goal**: Build per-sample euk fraction from GOTTCHA; compare against Kraken/Centrifuge;
  quantify cross-classifier rank concordance (Spearman) and document DB-driven differences.
- **Output**: `data/euk_fraction_per_sample.csv`, concordance figure.

### Notebook 01: Analysis table assembly
- **Goal**: Join euk fraction (+ source breakdown) to matrix/env/collection/platform/depth
  predictors + `study_id`; report per-predictor coverage; freeze the modeling table.
- **Output**: `data/analysis_table.parquet`, coverage table.

### Notebook 02: Univariate hypothesis tests
- **Goal**: Euk fraction by `ecosystem_category/type` and `env_medium` (Kruskal–Wallis +
  Dunn, FDR-corrected); H1b plant-plastid vs environment; H1c marginal platform/depth effects.
- **Output**: effect tables, boxplots by ecosystem, source-attribution stacked bars.

### Notebook 03: Multivariable model & variance partitioning
- **Goal**: Model euk fraction ~ matrix + platform + depth with **zero-inflated / hurdle**
  structure (logistic detectable-vs-not + beta/Gamma magnitude) and/or gradient-boosted trees;
  include `study_id` as random effect (report ICC / batch share). Partition explained variance
  (matrix vs sequencing vs residual) → directly answers H1c and quantifies the residual.
- **Output**: coefficient/importance tables, variance-partition figure, model diagnostics.

### Notebook 04 (optional): Robustness & source map
- **Goal**: Repeat key results across the 3 classifiers; map plant/host/fungal source by biome.

## Expected Outcomes
- **If H1a/H1b supported**: matrix/ecosystem explains a substantial, interpretable share of
  euk-fraction variance with a clear plant-vs-host source structure → an actionable QC prior
  ("expect elevated eukaryotic fraction for these environments").
- **If H1c supported**: sequencing platform/depth add little beyond matrix → contamination is an
  upstream/collection phenomenon.
- **If H0 not rejected**: euk fraction is dominated by unmeasured protocol/biomass factors →
  motivates the wet-lab metadata that NMDC lacks (evidence for improved metadata capture).
- **Potential confounders**: study/batch effects (studies cluster by environment *and*
  protocol — mitigated via `study_id` random effect and within-study checks); read-depth
  detection sensitivity for rare euk taxa; classifier reference-DB composition; strong
  terrestrial class imbalance (4,467 terrestrial vs 571 aquatic); GOTTCHA/Centrifuge abundance
  normalization semantics.

## Revision History
- **v1** (2026-07-10): Initial plan. NMDC-only, matrix-focused scope (wet-lab factors framed as
  unmeasured residual). Response variable set to GOTTCHA relative eukaryotic abundance after
  discovering the NMDC Kraken DB is prokaryote-restricted.
- **v2** (2026-07-10): After NB01–03 showed the association is confounded (environment ≈ study;
  out-of-study GroupKFold R² = −0.21) and a data-landscape scan (`data/01_data_landscape.md`)
  confirmed no on-system source gives per-sample euk read fraction across many studies, the scope
  is refined (not abandoned):
  1. **Switch response source to the native `nmdc.results`** tables
     (`gottcha2/kraken2/centrifuge_classification_report`) — more recent and more euk-positive
     (Eukaryota 807 + plastid 1,787 files). Measurement **unit = `workflow_run_id`** (one
     ReadbasedAnalysis run; the three classifiers share it), bridged to biosample/study via
     `nmdc.metadata.biosample_to_workflow_run`. Run-level avoids pooling pseudo-replication.
  2. **Within-study contrast (the key addition):** analyse the one dominant soil study
     `nmdc:sty-11-34xj1150` (~3,200 samples) on its own, where batch/protocol is largely constant.
     Test whether euk fraction varies with *within-study* metadata that genuinely varies there
     (`env_local_scale` 11 values, `ecosystem_subtype` 6, geography 47) — a batch-controlled test of
     the environment effect. If it survives here, the biome signal is not purely batch.
  3. Reframe the causal claim honestly: cross-study environment effects are reported as
     *confounded/associational*; the within-study test is the closest thing to a controlled estimate.

## Authors
Mark Andrew Miller (LBL), ORCID [0000-0001-9076-6066](https://orcid.org/0000-0001-9076-6066)
