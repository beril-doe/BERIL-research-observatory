"""Annotation-coverage confounder check (review #6).

For each species in the lifestyle cohort, compute the fraction of gene
clusters that have a non-null, non-'-' COG annotation. Test whether the
fraction differs between host-associated and free-living lifestyles
(Mann-Whitney U).

Run on BERDL JupyterHub or any environment with the on-cluster Spark
session (we are running on JupyterHub).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats

from berdl_notebook_utils.setup_spark_session import get_spark_session

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "review_addenda"
OUT.mkdir(exist_ok=True)


def main() -> None:
    spark = get_spark_session()

    species_df = pd.read_csv(DATA / "species_lifestyle_classification.csv")
    species_list = species_df["gtdb_species_clade_id"].tolist()
    print(f"Species to query: {len(species_list)}")

    BATCH_SIZE = 20
    rows = []
    for i in range(0, len(species_list), BATCH_SIZE):
        batch = species_list[i : i + BATCH_SIZE]
        in_clause = "', '".join(batch)
        q = f"""
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
            WHERE gc.gtdb_species_clade_id IN ('{in_clause}')
            GROUP BY gc.gtdb_species_clade_id
        """
        batch_df = spark.sql(q).toPandas()
        rows.append(batch_df)
        if (i // BATCH_SIZE + 1) % 10 == 0:
            print(
                f"Batch {i // BATCH_SIZE + 1}/"
                f"{(len(species_list) + BATCH_SIZE - 1) // BATCH_SIZE}"
            )

    cov = pd.concat(rows, ignore_index=True)
    cov["cog_fraction"] = cov["cog_annotated_clusters"] / cov["total_clusters"]
    cov["any_anno_fraction"] = cov["annotated_clusters"] / cov["total_clusters"]
    cov = cov.merge(
        species_df[["gtdb_species_clade_id", "species_lifestyle", "phylum"]],
        on="gtdb_species_clade_id",
        how="inner",
    )
    cov.to_csv(OUT / "annotation_coverage_per_species.csv", index=False)

    host = cov[cov["species_lifestyle"] == "host_associated"]["cog_fraction"].dropna()
    free = cov[cov["species_lifestyle"] == "free_living"]["cog_fraction"].dropna()
    u, p = stats.mannwhitneyu(host, free, alternative="two-sided")
    r = 1.0 - 2.0 * float(u) / (len(host) * len(free))

    print("\n=== COG annotation coverage by lifestyle ===")
    print(f"  Host-associated:  n={len(host)}, median={host.median():.4f}, "
          f"mean={host.mean():.4f}")
    print(f"  Free-living:      n={len(free)}, median={free.median():.4f}, "
          f"mean={free.mean():.4f}")
    print(f"  Mann-Whitney U:   {u:.0f}")
    print(f"  p-value:          {p:.3e}")
    print(f"  Median diff:      {host.median() - free.median():+.4f}")
    print(f"  Rank-biserial r:  {r:+.3f}")
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


if __name__ == "__main__":
    main()
