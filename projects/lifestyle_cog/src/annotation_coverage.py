"""Annotation-coverage confounder check (review #6).

For each species in the lifestyle cohort, compute the fraction of gene
clusters that have a non-null, non-'-' COG annotation. Test whether the
fraction differs between host-associated and free-living lifestyles
(Mann-Whitney U).

Single-query strategy: register the lifestyle CSV as a temp view in Spark
and join inside the warehouse rather than batched IN-clauses. Much faster
than per-batch Python loops.

Run on BERDL JupyterHub or any environment with the on-cluster Spark
session (we are running on JupyterHub).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
from scipy import stats

from berdl_notebook_utils.setup_spark_session import get_spark_session

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "review_addenda"
OUT.mkdir(exist_ok=True)


def main() -> None:
    species_df = pd.read_csv(DATA / "species_lifestyle_classification.csv")
    print(f"Species in lifestyle cohort: {len(species_df)}", flush=True)
    print("Connecting to Spark...", flush=True)
    spark = get_spark_session()
    print("Spark session ready", flush=True)

    # Register the lifestyle classification as a temp view so the join
    # happens inside Spark rather than in a Python loop.
    species_spark = spark.createDataFrame(
        species_df[["gtdb_species_clade_id", "species_lifestyle", "phylum"]]
    )
    species_spark.createOrReplaceTempView("lifestyle_species")
    print("Registered lifestyle_species temp view", flush=True)

    print("Running single coverage query against gene_cluster x eggnog...", flush=True)
    t0 = time.time()
    coverage_df = spark.sql(
        """
        SELECT
            gc.gtdb_species_clade_id,
            COUNT(*) AS total_clusters,
            COUNT(ann.query_name) AS annotated_clusters,
            SUM(CASE WHEN ann.COG_category IS NULL
                      OR ann.COG_category = '-' THEN 0 ELSE 1 END)
                AS cog_annotated_clusters
        FROM kbase_ke_pangenome.gene_cluster gc
        LEFT JOIN kbase_ke_pangenome.eggnog_mapper_annotations ann
            ON gc.gene_cluster_id = ann.query_name
        JOIN lifestyle_species ls
            ON gc.gtdb_species_clade_id = ls.gtdb_species_clade_id
        GROUP BY gc.gtdb_species_clade_id
        """
    ).toPandas()
    print(
        f"Coverage query returned {len(coverage_df)} rows in {time.time()-t0:.0f}s",
        flush=True,
    )

    coverage_df["cog_fraction"] = (
        coverage_df["cog_annotated_clusters"] / coverage_df["total_clusters"]
    )
    coverage_df["any_anno_fraction"] = (
        coverage_df["annotated_clusters"] / coverage_df["total_clusters"]
    )
    coverage_df = coverage_df.merge(
        species_df[["gtdb_species_clade_id", "species_lifestyle", "phylum"]],
        on="gtdb_species_clade_id",
        how="inner",
    )
    coverage_df.to_csv(OUT / "annotation_coverage_per_species.csv", index=False)
    print(
        f"Saved per-species coverage: {len(coverage_df)} species",
        flush=True,
    )

    host = coverage_df[coverage_df["species_lifestyle"] == "host_associated"][
        "cog_fraction"
    ].dropna()
    free = coverage_df[coverage_df["species_lifestyle"] == "free_living"][
        "cog_fraction"
    ].dropna()
    u, p = stats.mannwhitneyu(host, free, alternative="two-sided")
    r = 1.0 - 2.0 * float(u) / (len(host) * len(free))

    print("\n=== COG annotation coverage by lifestyle ===", flush=True)
    print(
        f"  Host-associated:  n={len(host)}, median={host.median():.4f}, "
        f"mean={host.mean():.4f}",
        flush=True,
    )
    print(
        f"  Free-living:      n={len(free)}, median={free.median():.4f}, "
        f"mean={free.mean():.4f}",
        flush=True,
    )
    print(f"  Mann-Whitney U:   {u:.0f}", flush=True)
    print(f"  p-value:          {p:.3e}", flush=True)
    print(f"  Median diff:      {host.median() - free.median():+.4f}", flush=True)
    print(f"  Rank-biserial r:  {r:+.3f}", flush=True)

    summary = pd.DataFrame(
        [
            {
                "metric": "cog_fraction",
                "n_host": int(len(host)),
                "n_free": int(len(free)),
                "median_host": float(host.median()),
                "median_free": float(free.median()),
                "diff_median": float(host.median() - free.median()),
                "U": float(u),
                "p_value": float(p),
                "rank_biserial": r,
            }
        ]
    )
    summary.to_csv(OUT / "annotation_coverage_summary.csv", index=False)
    print(f"\nSaved summary: {OUT / 'annotation_coverage_summary.csv'}", flush=True)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
