# Gene and Protein Function Annotations in BERDL, with Coordinates

## Research Question
Which BERDL tables (any tenant — including NMDC, KBase reference data, and
pangenome tables) assign a function to a gene or protein, and which give
structural or functional annotations over *regions* of genomes, genes, or
proteins (domains, motifs, BGC regions, operons)? For each such table: does it
carry coordinates (sequence/contig ID, start, end, strand), what coordinate
system are those coordinates in (genome/nucleotide vs protein/amino-acid), which
identifier systems does it use (Pfam, KO, EC, GO, InterPro, antiSMASH, …), and
how many rows does it have?

Secondary question: how useful is SemCat (`globalusers.semantic_catalog`) as the
discovery instrument for this census — for each table in the final answer, did
SemCat find it, miss it, or describe it wrongly?

## Status
Completed — of 17 coordinate-bearing BERDL region-annotation tables only 6 can be joined to genes by position, and SemCat's `content_type` labels are high-precision but low-recall, so they find a minority of the annotation tables a researcher needs.

## Overview
A census-and-instrument-evaluation project. The primary deliverable is a catalog
of BERDL annotation sources classified by coordinate availability and identifier
system; the secondary deliverable is an assessment of whether BERDL's semantic
catalog can be trusted to find them. The motivating downstream use case is
region-aware search — e.g. "which genes sit inside or near an antiSMASH BGC
region" or "find proteins with this combination of domains in this order" —
which is only possible where coordinates exist in a shared coordinate system.

## Quick Links
- [Research Plan](RESEARCH_PLAN.md) — competing hypotheses, discrimination strategy, per-notebook plan
- [Worklog](WORKLOG.md) — narrative record, including exploration findings
- [References](references.md) — dataset-discovery and BGC-mining literature
- [Pitfalls](memories/pitfalls.md) — ten traps (four SemCat, six tooling/analysis) found across exploration, analysis and review
- [Report](REPORT.md) — findings, the census, and the SemCat assessment
- [Scoreboard](SCOREBOARD.md) — per-hypothesis standing and both corrections

## Reproduction

**Prerequisites.** Run from BERDL JupyterHub (on-cluster). `python $BERIL_CORE/scripts/berdl_env.py --check`
must report `on-cluster`. Read access to the `kbase`, `kescience`, `nmdc`, `refdata` and
`globalusers` tenants. Python deps: `requirements.txt`.

**Note on tooling.** `$BERIL_CORE/scripts/run_sql.py` is an *off-cluster* tool and fails here
with `No module named 'spark_connect_remote'`. Use `./q.py "<SQL>"`, which wraps
`berdl_notebook_utils.setup_spark_session.get_spark_session`.

**Steps.** Run the notebooks in order — the ordering is load-bearing, not cosmetic. `01` must
run before `02`, because it freezes the SemCat-only answer before the independent ground truth
exists; reversing them makes the SemCat grade circular.

```bash
cd notebooks
for nb in 01_semcat_discovery 02_ground_truth_sweep 03_semcat_grade 04_bgc_region_joinability; do
  /opt/conda/bin/jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=7200 $nb.ipynb
done
```

Runtime ~25 min, dominated by value sampling in `03`.

**Reproducibility, stated precisely.** The audit is now deterministic end to end. The seed
(`SEED = 20261002`) fixes *which columns* are sampled, and `03`'s value sampler fixes *which
values* within them:

```sql
SELECT DISTINCT `col` AS v FROM <table>
WHERE `col` IS NOT NULL [AND pmod(abs(xxhash64(CAST(`col` AS STRING))), 256) = 0]
ORDER BY xxhash64(CAST(v AS STRING)) LIMIT 60
```

`DISTINCT` supplies diversity (hash-ordering alone groups identical values), `ORDER BY
xxhash64` supplies a total order on a pure function of the value, and the hash-bucket
prefilter — applied only where SemCat reports `ndv > 100,000` — keeps the cost of the
`DISTINCT` aggregation bounded on billion-row columns. Re-running the chain against an
unchanged catalog reproduces the audit figures exactly.

Earlier runs used `LIMIT 60` with no `ORDER BY`, which has no row-order guarantee; that caused
~±2 points of drift in lenient precision and one genuinely wrong published figure. See
Correction 7 in `REPORT.md`.

**Run all four, always.** `01` and `02` read live BERDL and SemCat state top-to-bottom, and
`03`/`04` consume their CSV outputs. Re-running one notebook alone silently desynchronises the
others — this happened during development and is recorded as Correction 3 in `REPORT.md`. If
you re-run anything, re-run the whole chain.

**Expected drift.** SemCat regenerates often: its `code_version` moved 0.19.28 → 0.21.6 →
0.24.2 → 0.26.1 → 0.27.0 within nine days during this project, with indexed tables going
2,599 → 2,509. Row
counts, stale/missing table counts and the exact precision/recall figures will therefore differ
from those in `REPORT.md`, which pins its snapshot (catalog generated 2026-10-06T19:38:26Z,
`code_version` 0.27.0) in the header. The
qualitative hypothesis verdicts (H1/H0 refuted, H2 supported) were stable
across two independent snapshots. The census itself (`src/census.py`) is a curated artifact and
does not change on re-run.

## Authors
Mark Andrew Miller (LBL, ORCID 0000-0001-9076-6066)

## Data Collections

`globalusers_semantic_catalog`, `kbase_ke_pangenome`, `kescience_mgnify`, `nmdc_results`,
`refdata_bvbrc`, `refdata_smag`, `kescience_interpro`, `refdata_interpro`,
`kescience_fitnessbrowser`, `kescience_pdb`, `kescience_paperblast`, `refdata_jgi_virus`,
`refdata_jgi_mycocosm`, `refdata_fungal_db`, `kbase_genomes`, `kbase_content`,
`refdata_cazy`, `refdata_tcdb`, `refdata_merops`, `refdata_rhea`,
`globalusers_gapmind_pathways`, `globalusers_carbon_source_phenotypes`,
`globalusers_kepangenome_parquet_1`, `kbase_nmdc_arkin`, `nmdc_metadata`, `nmdc_ref_data`,
`refdata_microagrobiome`
