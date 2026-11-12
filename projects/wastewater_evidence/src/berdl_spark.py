"""Minimal Spark Connect session for BERDL, used by every script in src/.

The documented client package (spark_connect_remote) could not be installed:
its GitHub org no longer resolves (see memories/pitfalls.md). On-cluster, a
plain pyspark Spark Connect URL with the KBase token works directly.

Usage:
    from berdl_spark import get_spark, run_dir
    spark = get_spark()
"""
from __future__ import annotations

import os
from pathlib import Path


def _load_env() -> None:
    core = os.environ.get("BERIL_CORE")
    candidates = []
    if core:
        candidates.append(Path(core) / ".env")
    candidates.append(Path.home() / "beril-workbench-v2" / "core" / ".env")
    for p in candidates:
        if p.exists():
            for raw in p.read_text().splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'").strip('"'))
            return


def get_spark(app_name: str = "wastewater_evidence"):
    _load_env()
    tok = os.environ.get("KBASE_AUTH_TOKEN")
    if not tok:
        raise RuntimeError("KBASE_AUTH_TOKEN not set and no .env found")
    host = os.environ.get("BERDL_SPARK_HOST", "spark.berdl.kbase.us")
    port = os.environ.get("BERDL_SPARK_PORT", "443")
    from pyspark.sql import SparkSession

    url = f"sc://{host}:{port}/;use_ssl=true;x-kbase-token={tok}"
    return SparkSession.builder.remote(url).appName(app_name).getOrCreate()


def run_dir() -> Path:
    """Output directory: $BERIL_RUN_DIR under `beril run`, else ./data/scratch."""
    d = Path(os.environ.get("BERIL_RUN_DIR", "data/scratch"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def sql_pd(spark, query: str):
    """Run a bounded query and return pandas."""
    return spark.sql(query).toPandas()
