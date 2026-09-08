#!/usr/bin/env python3
"""Append staged S. mutans Parquet to kbaseincubator.llmagent.* via Spark only.

Spark Connect (hub session) has working cluster-side credentials; the local MinIO
client does not. So instead of the bronze-upload + ingest() path, we read each
staged Parquet locally, createDataFrame under the *live* table schema (guaranteeing
a type/name match), and writeTo(...).append() straight to the Iceberg table.

Guards: aborts if org_id already present; asserts per-table row deltas afterward.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pyarrow.parquet as pq
import berdl_notebook_utils as bnu

STAGE = Path("/home/cjneely/repos/BERIL-research-observatory/data/llmagent_ingest_smutans")
NAMESPACE = "kbaseincubator.llmagent"
ORG_ID = "SmutansUA159"
TABLES = ["annotation", "annotation_evidence", "interproscan", "protein"]

spark = bnu.get_spark_session()


def fqn(t):
    return ".".join(f"`{p}`" for p in NAMESPACE.split(".") + [t])


def count(t, where=""):
    return spark.sql(f"SELECT COUNT(*) n FROM {fqn(t)} {where}").collect()[0]["n"]


# ── Guard: refuse to double-append ──────────────────────────────────
existing = {t: count(t, f"WHERE org_id = '{ORG_ID}'") for t in TABLES}
if any(existing.values()):
    print("ABORT — org_id already present:", existing)
    sys.exit(2)

before = {t: count(t) for t in TABLES}
expected = {t: pq.ParquetFile(STAGE / f"{t}.parquet").metadata.num_rows for t in TABLES}
print("before totals:", before)
print("to append   :", expected)

# ── Append each table under its live schema ─────────────────────────
for t in TABLES:
    live = spark.table(fqn(t)).schema          # StructType from the existing table
    cols = [f.name for f in live.fields]
    tbl = pq.read_table(STAGE / f"{t}.parquet")
    recs = tbl.to_pylist()                       # python int/float/str/None
    rows = [tuple(r.get(c) for c in cols) for r in recs]
    sdf = spark.createDataFrame(rows, schema=live)
    sdf = sdf.select(*cols)                      # enforce column order
    print(f"  APPEND {t}: {sdf.count():,} rows ...", flush=True)
    sdf.writeTo(fqn(t)).append()

# ── Verify deltas ───────────────────────────────────────────────────
print("\n=== verification ===")
all_ok = True
for t in TABLES:
    after = count(t)
    smu = count(t, f"WHERE org_id = '{ORG_ID}'")
    delta = after - before[t]
    ok = (delta == expected[t]) and (smu == expected[t])
    all_ok &= ok
    print(f"  {t:22s} total {before[t]:,} -> {after:,}  (+{delta:,}), {ORG_ID}={smu:,}  expected +{expected[t]:,}  {'OK' if ok else 'MISMATCH'}")

print("\nALL OK" if all_ok else "\nWARNING: mismatch")
sys.exit(0 if all_ok else 1)
