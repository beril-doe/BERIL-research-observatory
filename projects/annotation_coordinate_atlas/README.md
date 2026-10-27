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

Completed — 13 of 23 coordinate-bearing BERDL annotation tables can be placed against genes by position, but only 4 of the 14 region-annotation tables can, all in `kescience.mgnify`. SemCat's specific `content_type` labels flag 37 of the 51 census tables (13 more only by a generic label, 1 missed), but at column level they label 31.6% of the relevant columns, with strict precision 80.4% (95% interval 0.68–0.89), at the 0.80 threshold.

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
- [Pitfalls](memories/pitfalls.md) — thirteen traps (five SemCat, eight tooling/analysis) found across exploration, analysis, review and the 2026-10-22 revision
- [Report](REPORT.md) — findings, the census, and the SemCat assessment
- [Scoreboard](SCOREBOARD.md) — per-hypothesis standing and the corrections history

## Reproduction

**Prerequisites.** Run from BERDL JupyterHub (on-cluster). `python $BERIL_CORE/scripts/berdl_env.py --check`
must report `on-cluster`. Read access to the tenant prefixes listed in `src/semcat.py`
(`ACCESSIBLE_TENANTS`); NB02 stops if the account's live table listing shows a different set.
Python deps: `requirements.txt`.

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

Each notebook prints its wall time in its last cell. On 2026-10-22 they were NB01 19 s,
NB02 242 s, NB03 394 s and NB04 1,407 s (about 34 min in all). NB04 is dominated by the
joinability checks on the billion-row `kbase.genomes` and `bvbrc` tables.

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
drift in lenient precision and one wrong published figure (Correction 6 in `REPORT.md`), fixed by
this sampler (Correction 7). Plain `LIMIT` is the cheaper query; `DISTINCT` costs an
aggregation, which the hash-bucket prefilter bounds.

**Run all four, always.** `01` and `02` read live BERDL and SemCat state top-to-bottom, and
`03`/`04` consume their CSV outputs. Re-running one notebook alone silently desynchronises the
others — this happened during development and is recorded as Correction 3 in `REPORT.md`. If
you re-run anything, re-run the whole chain.

**Expected drift.** SemCat regenerates often, and its `code_version` can advance without the
catalog content changing. `REPORT.md` pins the snapshot measured: catalog generated
2026-10-21T16:33:03Z (regenerated 2026-10-21T17:49:36Z), `code_version` 0.32.2, read through
Spark on 2026-10-22; NB01 prints these from `catalog_meta`. Re-running against a later catalog
or a changed lakehouse will move row counts, coverage counts and the audit figures. Strict
precision sits within half a point of the 0.80 H2/H3 threshold, so a rerun can change the
point-estimate verdict between H2 and H3. The census itself (`src/census.py`) is a curated
artifact and does not change on re-run.

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
