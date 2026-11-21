# Wastewater Evidence

## Research Question
Across sample-metadata systems (NCBI BioSample, MGnify, NMDC, GOLD, and whatever
else is reachable in BERDL), which attributes and values best indicate that a
sample is wastewater, and which best indicate a wastewater subtype (influent,
effluent, activated sludge, anaerobic digester, sewer)? How can evidence learned
in systems with strong structured signal (packages, biomes, ecosystem paths,
ENVO terms) be transferred to classify samples in systems where the signal is
weak (mostly free text), and how can that transfer be validated without
hand-labeling thousands of records?

## Status

Completed — BioSample carries four non-nested wastewater evidence channels; the ENVO closure agrees best with the others; across studies, mined vocabulary recovers essentially nothing beyond a generic keyword regex; support screening removes most over-generalised idiom; subtype assignment should be multi-label.

## Overview
Starting observations from the author: keyword matching (wastewater, sewage,
activated sludge) over a few text fields in ~56M BioSample records yields
~503k hits, ~39% of them outside any wastewater package. MGnify wastewater
biomes cover ~4.3k samples, all in BioSample, but ~850 have no wastewater
wording there. Substring matching mis-fires (e.g. "digest" matching
"undigested primary sludge"). This project inventories the structured and
free-text evidence available in each reachable system, measures how each
indicator agrees with the others, and proposes a cross-system labelling and
validation scheme.

## Quick Links
- [Research Plan](RESEARCH_PLAN.md) — not written; this project is exploratory throughout
- [Report](REPORT.md) — findings, interpretation, supporting evidence
- [Review 1](REVIEW_1.md), [Review 2](REVIEW_2.md), [Review 3](REVIEW_3.md), [Review 4](REVIEW_4.md), [Review 5](REVIEW_5.md) — independent reviews; Review 5 is the approved one (canonical copy in [REVIEW.md](REVIEW.md))
- [Worklog](WORKLOG.md) — what was done and why

## Data Collections
`nmdc` (`ncbi_biosamples`, `metadata`), `kbase` (`ontology_source`), `refdata`
(`all_the_bacteria`), plus two external sources fetched over the public web:
the GOLD Excel export and the MGnify REST API.

## Reproduction

Prerequisites: on-cluster BERDL access with `KBASE_AUTH_TOKEN` in
`$BERIL_CORE/.env`. The documented `spark_connect_remote` client cannot be
installed (see `memories/pitfalls.md`); `src/berdl_spark.py` opens a plain
pyspark Spark Connect session instead, and every run uses the cluster Python at
`/opt/conda/bin/python`.

Run from inside this project directory, in order:

```bash
# 1. table schemas and row counts
uv run beril run --name schemas -- /opt/conda/bin/python -I src/00_schemas.py

# 2. external sources (GOLD export must be downloaded first, ~239 MB)
mkdir -p data/gold_raw && curl -sL -o data/gold_raw/goldData.bin \
  "https://gold.jgi.doe.gov/download?mode=site_excel"
uv run beril run --name gold-parse --input data/gold_raw/goldData.bin -- \
  /opt/conda/bin/python -I src/01_gold_xlsx_to_parquet.py data/gold_raw/goldData.bin
uv run beril run --name mgnify-fetch -- /opt/conda/bin/python -I src/01_mgnify_fetch.py

# 3. BioSample evidence channels
uv run beril run --name biosample-evidence -- /opt/conda/bin/python src/02a_biosample_evidence.py
uv run beril run --name atb-ena-probe   -- /opt/conda/bin/python src/05_atb_ena_probe.py

# 4. transfer and validation
uv run beril run --name external-vs-biosample -- /opt/conda/bin/python src/03_external_vs_biosample.py
uv run beril run --name transfer-validate     -- /opt/conda/bin/python src/04_transfer_validate.py
uv run beril run --name term-screen           -- /opt/conda/bin/python src/04b_term_screen.py

# 5. figures
uv run beril run --name figures -- /opt/conda/bin/python src/06_figures.py

# 6. verification runs cited by the report (field population counts, the
#    corrected hold-out, the per-term support basis, the coherence flagged
#    counts, the study-level overlap and the lift recheck)
uv run beril run --name review-checks -- /opt/conda/bin/python src/07_review_checks.py
uv run beril run --name v22-checks    -- /opt/conda/bin/python src/08_v22_checks.py
uv run beril run --name v23-checks    -- /opt/conda/bin/python src/09_v23_checks.py
uv run beril run --name v24-checks    -- /opt/conda/bin/python src/10_v24_checks.py
```

Steps 3 and 4 depend on step 2's parquet outputs; the scripts resolve the latest
matching run directory automatically. Shared regexes live in `src/ww_flags.py`
and must stay SQL-escaped (`sql_re`) wherever they are embedded in Spark SQL.

## Files not in git

The lakehouse archive holds the complete project, including the files below:
`s3a://cdm-lake/tenant-general-warehouse/microbialdiscoveryforge/projects/wastewater_evidence/`
(readable by members of the `microbialdiscoveryforge` tenant).

- `data/gold_raw/goldData_download_20261017.bin` (239 MB), the GOLD public export downloaded 2026-10-17. Step 2 of Reproduction downloads a current copy; GOLD changes over time, so a new download may not reproduce the counts exactly.
- Nine parquet outputs under `runs/*/out/`, including the parsed GOLD and MGnify tables and `labelled_samples.parquet`. The repository's `.gitignore` excludes parquet files. Rerun the steps above, or copy them from the archive.
- `runtime.json`, which is machine-local.

## Authors
- Mark Andrew Miller (LBL), ORCID 0000-0001-9076-6066
