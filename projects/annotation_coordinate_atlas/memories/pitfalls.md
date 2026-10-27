# Pitfalls — annotation_coordinate_atlas

## 2026-10-02 — `scripts/run_sql.py` fails on-cluster

**Symptom.** `python $BERIL_CORE/scripts/run_sql.py --query "..."` exits with
`Cannot import spark_connect_remote: No module named 'spark_connect_remote'`,
even though `berdl_env.py --check` reports `on-cluster` and ready.

**Cause.** `run_sql.py` is an off-cluster tool. Its PEP 723 header declares
`spark_connect_remote` and `berdl_remote`, which it expects `uv run --script` to
resolve. Run under the JupyterHub conda interpreter (`/opt/conda/bin/python`) it
gets neither, because the JH kernel ships `berdl_notebook_utils` instead.

**Fix.** On-cluster, don't use `run_sql.py`. Use
`berdl_notebook_utils.setup_spark_session.get_spark_session()` directly. This
project wraps that in `q.py`.

**Generalization.** `berdl_env.py --check` reporting `on-cluster` means *skip the
proxy scripts entirely*, not *run the proxy scripts without `--berdl-proxy`*. The
two environments have disjoint Spark client libraries, not a shared one with an
optional proxy flag.

## 2026-10-02 — SemCat's `content_type='coordinate'` is not a genomic coordinate

**Symptom.** Filtering `globalusers.semantic_catalog.columns` on
`content_type = 'coordinate'` to find genome feature tables returns mostly
latitude/longitude columns (`usgs.ngwmn.wells`, `nmdc.metadata.biosample_set`,
`kbase.ke_pangenome.alphaearth_embeddings_all_years.cleaned_lat`).

**Cause.** SemCat uses one `coordinate` label for geographic coordinates,
nucleotide spans, and amino-acid/residue spans alike. 78 columns, all three
meanings mixed.

**Fix.** Don't trust the label for coordinate *system*. Disambiguate from the
`lower`/`upper` bounds SemCat already stores: geographic lat is within
[-90, 90] and lon within [-180, 180] and the type is usually `double`;
nucleotide spans are `int`/`bigint` running to ~10^7; protein/residue spans are
`int` topping out in the low thousands. Confirm against the table's own
sequence-reference column (`contig_id` → nucleotide, `protein_id`/`uniprot_acc`
→ amino acid) before asserting a coordinate system.

## 2026-10-02 — SemCat `content_type` recall is ~10% on some facets; `concepts` has no gene-function vocabulary

**Symptom.** A search for genome-feature tables driven by SemCat's semantic
labels silently returns a small fraction of the real answer.

**Cause.** 78,730 of 93,617 columns (84%) have `content_type = NULL`. On the
`strand` facet specifically, SemCat labels 6 columns; a plain name regex over
SemCat's own `columns` table finds 58. Separately, all 122 rows of
`semantic_catalog.concepts` are environmental/geochemical (temperature, nitrate,
depth, salinity, metals) — there is no concept for gene function, Pfam, KO, EC,
GO, domain, or BGC.

**Fix.** Treat `content_type` as a high-precision, low-recall hint: good for
*seeding* a search, never for bounding it. Union it with a name/type regex over
`columns`, and for any tenant you can actually read, confirm against live
`DESCRIBE`. Do not use `concepts` for molecular questions at all.

**Also beware false labels**, not just missing ones:
`nmdc.metadata.material_processing_set.is_stranded` is labeled `strand` but means
RNA-seq library strandedness, while real genomic strand columns
(`kescience.fitnessbrowser.gene.strand`, `refdata.bvbrc.bvbrc_feature_fact.strand`)
are labeled `annotation_text`.

## 2026-10-02 — SemCat indexes tables you cannot read, and misses tables you can

**Symptom.** Candidate tables found in SemCat fail at query time with a Spark
authorization error; meanwhile databases visible in your own inventory never
appear in SemCat.

**Cause.** SemCat covers 21 tenants / 154 databases / 2,599 tables globally,
independent of the caller's grants. This user's membership is 8 tenants.
Confirmed denied: `enigma.genome_depot_enigma.browser_gene`,
`arkinlab.dbcan.dbcan_pul`, `phagefoundry.phages_genomedepot.browser_gene`.
Confirmed absent from SemCat but readable: all of `bervodata` (bervo, chess,
fao_soils, hwsd2, watershed_sfa_soil_moisture) and `culturebotai`.

**Fix.** Intersect SemCat's table list with your accessible inventory before
planning any query work, and keep the two provenance classes separate in
write-ups: "verified against live data" vs "asserted by SemCat, unverifiable at
this access level". SemCat is a global catalog, not a view of your grants.

**Note.** SemCat's `tables.row_count` *is* reliable where checkable — exact
matches against live `COUNT(*)` on four tables spanning 35K to 2.68B rows. And
Iceberg makes those live counts cheap even at billion-row scale, so verify
rather than assume.

## 2026-10-02 — `get_db_structure()` returns a JSON string, not a dict

**Symptom.** `for db, tbls in bnu.get_db_structure().items()` raises
`AttributeError: 'str' object has no attribute 'items'`; worse, `for db in
bnu.get_db_structure()` succeeds and silently iterates **characters**, so a sweep
loop produces nothing and reports no error.

**Fix.** `struct = bnu.get_db_structure()` then
`if isinstance(struct, str): struct = json.loads(struct)`. Other
`berdl_notebook_utils` helpers take `return_json=False` for this; `get_db_structure`
in this build does not accept it, so parse defensively.

**Note.** The live listing is materially richer than
`data/berdl_inventory_cache.json`: 108 databases / 883 tables live vs 97 / 812 in
the cache, and the cache omits `globalusers` databases that hold real data
(`globalusers.kepangenome_parquet_1.feature`, 1,011,650,903 rows). Sweep live
when completeness matters.

## 2026-10-02 — notebook variable shadowing silently corrupted a reported metric

**Symptom.** A summary JSON contained an entire pretty-printed DataFrame where an
integer false-negative count belonged, and `json.dump` failed with
`TypeError: Object of type DataFrame is not JSON serializable`.

**Cause.** Section 3 computed `fn` as a false-negative **count**; section 5 reused
`fn` for a filtered DataFrame (`fn = cen[cen.category == "gene_function"]`).
Notebooks share one namespace across all cells, so the later assignment silently
replaced the metric. The `TypeError` was luck — had the shadowing variable been an
`int`, a wrong number would have been published with no error at all.

**Fix.** Give derived DataFrames suffixed names (`fn_df`), and guard any
serialization step:
```python
bad = {k: type(v).__name__ for k, v in summary.items()
       if not isinstance(v, (int, float, str, bool, type(None)))}
if bad: print("NON-SERIALIZABLE:", bad)
```
That guard is what located this one. Keep short names like `tp`/`fp`/`fn` for
metrics *or* for frames, never both in one notebook.

## 2026-10-02 — pandas attribute access collides with DataFrame members

**Symptom.** `int(scale.columns[0])` raises
`ValueError: invalid literal for int() with base 10: 'tables'`.

**Cause.** A Spark SQL alias named `columns` becomes a pandas column that
attribute access cannot reach — `df.columns` is the column **index**, not the
data. Same hazard for `index`, `size`, `shape`, `count`, `name`, `values`, `T`.

**Fix.** Prefer `df["columns"][0]`, or alias such columns in SQL
(`COUNT(*) AS n_columns`). This cost two notebook re-runs.

## 2026-10-06 — re-running one notebook in a live-data chain silently desynchronises the rest

**Symptom.** `REPORT.md` quotes figures the repository no longer produces: 883 accessible
tables vs 826 in the saved notebook, 159 stale SemCat tables vs 5, 13 sweep failures vs 0.
Nothing errors. Found only by an independent reviewer cross-checking notebook cell outputs
and file mtimes against the prose.

**Cause.** Notebooks that read live BERDL/SemCat state (`get_db_structure()`,
`semantic_catalog.*`) produce different numbers on every run. Re-executing one notebook to fix
a small thing — here, adding a row-count verification cell four days later — leaves its
downstream consumers holding the earlier snapshot. The CSVs on disk are from run B while the
saved outputs of the notebooks that read them are from run A.

**Fix.** Treat a live-data notebook chain as atomic: **re-run all of it, in order, or none of
it.** Pin the snapshot in the report header (lakehouse date *and* catalog `code_version`), and
state the ordering dependency in the README's Reproduction section.

**Detect it cheaply** — glob *everything* the chain writes, not just the summaries, or the
check misses exactly the cached intermediate that causes the problem:
```bash
ls -l --time-style=+%F_%H:%M notebooks/*.ipynb data/*.csv data/*.json figures/*.png \
  | awk '{print $6, $7}' | sort
```
More than one date across a chain is the signal. Worth running before every review and submit.

**Related failure, worth its own line.** A cell can *claim* to compute something live and
actually read a cached file. Grep for `json.load`/`read_csv` in cells whose prose says "live",
and prefer computing a figure in the notebook that reports it — a cached intermediate is a
snapshot waiting to desynchronise. In this project that exact pattern survived its own first
fix and had to be caught twice by review.

## 2026-10-06 — SemCat regenerates often enough to invalidate a measurement in progress

**Symptom.** Figures drift between analysis sessions with no change to the code.

**Cause.** `globalusers.semantic_catalog.catalog_meta.code_version` went **0.19.28**
(2026-09-29) → **0.21.6** (2026-10-06 04:12) → **0.24.2** (2026-10-06 19:38) — three
regenerations in eight days, two within one working day. Across those: indexed tables
2,599 → 2,509, columns 93,617 → 91,246, concepts 122 → 119, and three dated NMDC staging
databases dropped out of the index entirely.

**Fix.** Read `catalog_meta` at the start of any SemCat work and record `generated_at` and
`code_version` alongside every derived number. Any evaluation of SemCat is an evaluation of
one version of it. If a result must be stable, re-run the whole chain and check the version
did not move underneath you.

## 2026-10-06 — `float('nan')` defeats an `is not None` guard

**Symptom.** `ValueError: cannot convert float NaN to integer`, from code whose every
numeric use is guarded by `if x is not None`.

**Cause.** A coercion helper returned `float(v)` on success. When the input was NaN — which
SemCat 0.24.2 began returning for bounds that 0.19.28 gave as strings — it returned
`float('nan')`, which *is* not None, passes the guard, compares False against every threshold
(so the early branches silently skip), and finally reaches `format(int(hi), ',')` and dies.

**Fix.** Normalise NaN to None at the coercion boundary:
```python
try:
    f = float(v)
except (TypeError, ValueError):
    return None
return None if f != f else f      # f != f is the NaN test
```
A schema that was stable for one catalog version is not stable for the next; coerce
defensively at the edge rather than guarding at each use.

## 2026-10-22 — SemCat's verified single-column joins are in `edges`, not `verified_joins`

**Symptom.** `globalusers.semantic_catalog.verified_joins` has 6 rows for about 2,700 indexed
tables, which reads as "SemCat has almost no verified joins".

**Cause.** `verified_joins` holds only the joins SemCat verified by composite-key semijoin (the
notes `explain`/`joins` attach for composite keys). Single-column joins are rows of `edges`,
with a `verified` flag: 4,004 verified rows in the catalog generated 2026-10-21.

**Fix.** Count `edges WHERE verified`. Read SemCat's `docs/data-model.md` before judging a table
by its row count.

## 2026-10-22 — the table listing can name tables that cannot be read

**Symptom.** `get_db_structure()` lists 24 tables under `ese.ganymede`; every `DESCRIBE` on them
fails with `TABLE_OR_VIEW_NOT_FOUND`.

**Fix.** Treat "listed" and "readable" as different sets. Count the tables the sweep actually
read, and say which listed tables failed and why. A table-name comparison against SemCat still
counts them as present.

## 2026-10-22 — a hand-typed verdict list is not a result

**Symptom.** A per-table joinability table was a literal list in the notebook, and a later cell
counted it, so the headline count rested on one executed join and many typed judgements.

**Fix.** Derive the verdict table from query outputs under a stated rule. Mark each verdict as
"query" or "judgement" so a reader can see which is which.
