#!/opt/conda/bin/python
"""On-cluster SQL helper for this project.

The corpus's run_sql.py targets off-cluster Spark Connect via spark_connect_remote,
which is not installed in the JH kernel's conda env. berdl_env.py --check reports
on-cluster, so we use berdl_notebook_utils directly.

Usage:
    ./q.py "SELECT ..."            # pretty-print up to --limit rows
    ./q.py -f query.sql
    ./q.py "..." --limit -1 --tsv  # full result as TSV (for data/ dumps)
"""

from __future__ import annotations

import argparse
import sys

from berdl_notebook_utils.setup_spark_session import get_spark_session

_SPARK = None


def spark():
    global _SPARK
    if _SPARK is None:
        _SPARK = get_spark_session(app_name="annotation_coordinate_atlas")
    return _SPARK


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("query", nargs="?")
    p.add_argument("-f", "--query-file")
    p.add_argument("--limit", type=int, default=100, help="-1 for no limit")
    p.add_argument("--tsv", action="store_true")
    p.add_argument("--truncate", type=int, default=120)
    a = p.parse_args()

    sql = a.query
    if a.query_file:
        sql = open(a.query_file).read()
    if not sql:
        p.error("need a query or --query-file")

    df = spark().sql(sql)

    if a.tsv:
        rows = df.collect() if a.limit < 0 else df.limit(a.limit).collect()
        cols = df.columns
        print("\t".join(cols))
        for r in rows:
            print("\t".join("" if r[c] is None else str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols))
    else:
        n = 10_000 if a.limit < 0 else a.limit
        df.show(n=n, truncate=a.truncate, vertical=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
