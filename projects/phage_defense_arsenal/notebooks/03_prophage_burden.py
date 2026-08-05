# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # NB03 — Prophage Burden per Species
#
# **Purpose**: Re-derive per-species prophage burden using the classifier from
# `projects/prophage_ecology/src/prophage_utils.py` (7 operationally defined
# modules A-G: packaging, head morphogenesis, tail, lysis, integration, lysogenic
# regulation, anti-defense). This gives us the "phage-side" data to correlate
# against species-level defense-system counts (NB04, arms race).
#
# **Approach**:
# 1. Import `prophage_utils.build_spark_where_clause()` and
#    `classify_gene_to_module()` from the sibling project.
# 2. Query `eggnog_mapper_annotations` for all prophage-candidate gene clusters
#    (single large OR-chain).
# 3. Classify each hit into one or more modules in Python.
# 4. Aggregate to per-species presence of each module → per-species prophage
#    burden = number of modules present out of 7.
#
# **Output**: `data/species_prophage_burden.tsv.gz`.

# %%
import os
import sys
import pandas as pd
from berdl_notebook_utils.setup_spark_session import get_spark_session

# Import prophage_utils from the sibling prophage_ecology project
sys.path.insert(0, "../../prophage_ecology/src")
import prophage_utils

spark = get_spark_session()

DATA_DIR = "../data"

# %% [markdown]
# ## 1. Sanity check: module list

# %%
print(prophage_utils.get_module_summary())

# %% [markdown]
# ## 2. Build and run the prophage-candidate query
#
# The WHERE clause matches any gene cluster whose eggNOG Description/PFAMs/
# KEGG_ko field mentions any of the 7 modules' markers. It's a large OR-chain
# — full-scans the 93M-row `eggnog_mapper_annotations` table, so budget a
# couple of minutes.

# %%
where_clause = prophage_utils.build_spark_where_clause()
print(f"WHERE clause length: {len(where_clause):,} chars")
print("First 3 conditions:")
for line in where_clause.split("\n")[:3]:
    print(" ", line.strip())

# %%
prophage_query = f"""
SELECT
    ann.query_name AS gene_cluster_id,
    gc.gtdb_species_clade_id,
    ann.Description,
    ann.PFAMs,
    ann.KEGG_ko,
    ann.COG_category
FROM kbase_ke_pangenome.eggnog_mapper_annotations ann
JOIN kbase_ke_pangenome.gene_cluster gc
  ON ann.query_name = gc.gene_cluster_id
WHERE {where_clause}
"""

prophage_hits_df = spark.sql(prophage_query).toPandas()
print(f"Prophage-candidate hits: {len(prophage_hits_df):,} rows")
print(f"Unique gene clusters: {prophage_hits_df['gene_cluster_id'].nunique():,}")
print(f"Unique species: {prophage_hits_df['gtdb_species_clade_id'].nunique():,}")

# %% [markdown]
# ## 3. Classify hits into modules
#
# Each gene cluster can match ≥1 module. `classify_gene_to_module` returns a
# list of module IDs.

# %%
prophage_hits_df["modules"] = prophage_hits_df.apply(
    lambda r: prophage_utils.classify_gene_to_module(
        r["Description"], r["PFAMs"], r["KEGG_ko"], r["COG_category"]
    ),
    axis=1,
)
# How many hits classified into at least one module?
n_classified = prophage_hits_df["modules"].apply(bool).sum()
print(f"Hits classified into at least one module: {n_classified:,} / {len(prophage_hits_df):,}")

# Explode into long-form: one row per (gene_cluster_id, module)
long = prophage_hits_df[["gene_cluster_id", "gtdb_species_clade_id", "modules"]].explode("modules")
long = long.dropna(subset=["modules"])
print(f"Exploded rows: {len(long):,}")

# Per-module hit counts
module_counts = long["modules"].value_counts()
print("\nHits per module:")
print(module_counts)

# %% [markdown]
# ## 4. Aggregate to per-species module presence + total burden

# %%
# Per-species per-module presence: 1 if any gene cluster in that species matches
species_module = (
    long.groupby(["gtdb_species_clade_id", "modules"])
    .size()
    .rename("n_clusters")
    .reset_index()
)

# Wide matrix: species x module → n_clusters
prophage_wide_counts = species_module.pivot_table(
    index="gtdb_species_clade_id",
    columns="modules",
    values="n_clusters",
    fill_value=0,
).astype(int)
prophage_wide_counts.columns.name = None

# Binary presence
prophage_wide_bin = (prophage_wide_counts > 0).astype(int)
prophage_wide_bin.columns = [f"prophage_{c}" for c in prophage_wide_bin.columns]

# Total prophage burden = number of modules present (0-7)
prophage_wide_bin["n_prophage_modules"] = prophage_wide_bin.sum(axis=1)

# Total prophage cluster count = sum across modules (double-counts multi-module clusters)
prophage_wide_bin["n_prophage_clusters"] = (
    prophage_hits_df.groupby("gtdb_species_clade_id")["gene_cluster_id"].nunique()
).reindex(prophage_wide_bin.index, fill_value=0)

burden = prophage_wide_bin.reset_index()
print(f"Species with prophage data: {len(burden):,}")
print(f"Species with n_prophage_modules >= 4 (heavy prophage load): {(burden['n_prophage_modules'] >= 4).sum():,}")

burden.head(5)

# %% [markdown]
# ## 5. Distribution of prophage burden

# %%
burden_dist = burden["n_prophage_modules"].value_counts().sort_index()
print("Distribution of prophage burden (# modules present out of 7):")
print(burden_dist)

# %% [markdown]
# ## 6. Save

# %%
out = os.path.join(DATA_DIR, "species_prophage_burden.tsv.gz")
burden.to_csv(out, sep="\t", index=False, compression="gzip")
print(f"Wrote: {out}")
print(f"Rows: {len(burden):,}")
print(f"Columns: {list(burden.columns)}")

# %% [markdown]
# ## Summary
#
# - Per-species prophage burden derived from the `prophage_ecology` classifier.
# - Wide table: 7 module presence flags + `n_prophage_modules` (0-7) + `n_prophage_clusters`.
# - Species with high prophage burden (≥4 modules) are candidates for high phage pressure.
#
# **Next**: `04_arms_race.ipynb` — join defense matrix (NB02) with prophage
# burden (NB03) and test whether defense-system count scales with prophage load.
