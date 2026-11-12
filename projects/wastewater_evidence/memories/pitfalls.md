# Pitfalls — wastewater_evidence

## 2026-10-17 · spark_connect_remote cannot be installed; GitHub org is gone

**Symptom.** `bootstrap_client.sh` and `pip install git+https://github.com/BERDataLakehouse/spark_connect_remote.git`
fail with `remote: Repository not found`; `gh repo list BERDataLakehouse` says the
owner handle is not recognised. `run_sql.py` then fails at import. Also, the
bootstrap script's `pip install` hits `Can not perform a '--user' install` in this
environment; pass `--no-user`.

**Workaround.** On-cluster (spark.berdl.kbase.us:443 reachable), plain pyspark
Spark Connect works without the wrapper package:

```python
url = f"sc://spark.berdl.kbase.us:443/;use_ssl=true;x-kbase-token={KBASE_AUTH_TOKEN}"
spark = SparkSession.builder.remote(url).getOrCreate()
```

Needs `pyspark[connect]`, `pandas>=2.2`, `pyarrow`, `zstandard`, `pyyaml`
installed into `$BERIL_CORE/.venv-berdl`. Helper: `src/berdl_spark.py`.
First query returned in about half a second.

**Status.** Workaround in use for this project. Corpus scripts (`run_sql.py`,
`berdl_inventory.py` off-cluster path) still depend on the missing package.

## 2026-10-17 · `\b` in a Spark SQL RLIKE literal is a backspace, not a word boundary

**Symptom.** A regex with `\bsludge\b` embedded in `RLIKE '...'` returned almost no
hits (15 of 2.76M AllTheBacteria rows, all from the one alternative without `\b`).
No error. Spark SQL string literals process backslash escapes, so `\b` became a
backspace character.

**Fix.** Double the backslashes before embedding (`rx.replace("\\", "\\\\")`),
see `src/ww_flags.py:sql_re`. Alternatively set
`spark.sql.parser.escapedStringLiterals=true`. Runs before the fix:
`runs/20261017T012405Z-atb-ena-probe` (counts invalid, re-run supersedes it).

## 2026-10-17 · Spark Connect createDataFrame of ~10k rows fails with HTTP 413

**Symptom.** `spark.createDataFrame(list_of_tuples)` for ~10k rows x 4 string
columns raised `_InactiveRpcError ... Received http2 header with status: 413`
from `AddArtifacts`. The ingress in front of spark.berdl.kbase.us caps request
bodies, and pyspark ships a local relation above its cache threshold as an artifact.

**Fix.** Create the DataFrame in chunks of ~1,500 rows (each inlined in the plan)
and `unionAll` them, then `CACHE TABLE`. Also: pandas 3 Arrow-backed string
columns are rejected by the serializer (`Cannot convert ChunkedArray`); pass
plain Python tuples with an explicit column list.
