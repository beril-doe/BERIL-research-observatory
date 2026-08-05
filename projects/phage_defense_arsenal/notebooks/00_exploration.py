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
# # NB00 — Exploration & Feasibility
#
# **Purpose**: Confirm Phase-A findings — the seven target anti-phage defense system
# families (CRISPR-Cas, R-M Type I/II, CBASS, Gabija, Retron, BREX, DISARM) are
# detectable at pangenome scale via `interproscan_domains` (primary) and
# `eggnog_mapper_annotations` (secondary), and to record baseline pangenome and
# gene_cluster sizes that inform the extraction strategy in NB01.
#
# This notebook is intentionally lightweight — the substantive extraction work is
# in NB01. Detection Pfam accessions and per-system rules are locked in
# `RESEARCH_PLAN.md`.

# %%
import os
import pandas as pd
from berdl_notebook_utils.setup_spark_session import get_spark_session

spark = get_spark_session()
print("Spark version:", spark.version)

# %% [markdown]
# ## 1. Load Phase-A detection feasibility table
#
# Written during Phase A (see `RESEARCH_PLAN.md` §"Defense System Detection Rules").
# This table records the raw hit counts per marker in `interproscan_domains` and
# `eggnog_mapper_annotations` and is our reference for interpreting the extraction
# in NB01.

# %%
feas = pd.read_csv("../data/detection_feasibility.csv")
print(f"Rows: {len(feas)}")
feas

# %% [markdown]
# ## 2. Per-system marker summary
#
# Confirms Phase A findings: all seven systems are detectable. Broad Pfams
# (Gabija UvrD, Retron RVT_1, DISARM PLD) are flagged for anchor+context filtering
# in NB01.

# %%
summary = (
    feas.groupby("system", as_index=False)
    .agg(markers=("marker", "count"), max_hits=("n_hits", "max"))
    .sort_values("max_hits", ascending=False)
)
summary

# %% [markdown]
# ## 3. Confirm pangenome-side table sizes
#
# Sanity-check the sizes we plan to filter against in NB01 (`gene_cluster`,
# `pangenome`, `genome`) — informs whether broadcast joins are appropriate.

# %%
sizes = {}
for tbl in ["gene_cluster", "pangenome", "genome", "gtdb_taxonomy_r214v1", "gtdb_metadata", "gtdb_species_clade"]:
    n = spark.sql(f"SELECT COUNT(*) FROM kbase_ke_pangenome.{tbl}").collect()[0][0]
    sizes[tbl] = n
    print(f"  {tbl:<28s}  {n:>15,}")

# %% [markdown]
# ## 4. Species with sufficient genome sampling
#
# Arms-race and syndrome analyses require reliable core/accessory calls, which
# depend on species with enough sequenced genomes. Restrict downstream analyses
# to species with `no_genomes >= 5`.

# %%
species_counts = spark.sql("""
    SELECT
        SUM(CASE WHEN no_genomes >= 5 THEN 1 ELSE 0 END) AS species_ge5,
        SUM(CASE WHEN no_genomes >= 10 THEN 1 ELSE 0 END) AS species_ge10,
        SUM(CASE WHEN no_genomes >= 50 THEN 1 ELSE 0 END) AS species_ge50,
        COUNT(*) AS species_total
    FROM kbase_ke_pangenome.pangenome
""").toPandas()
species_counts

# %% [markdown]
# ## 5. Confirm the Pfam-version-suffix issue is table-specific
#
# In Phase A we discovered that `bakta_pfam_domains.pfam_id` includes a version
# suffix (e.g., `PF01867.29`) while `interproscan_domains.signature_acc` is
# version-free (`PF01867`). NB01's extraction query relies on the version-free
# form of `signature_acc` — confirm here.

# %%
sample = spark.sql("""
    SELECT DISTINCT signature_acc
    FROM kbase_ke_pangenome.interproscan_domains
    WHERE analysis = 'Pfam'
      AND signature_acc IN ('PF01867','PF08843','PF14090','PF20473','PF13091','PF00078')
""").toPandas()
print("Version-free Pfam accessions confirmed in interproscan_domains.signature_acc:")
sample

# %% [markdown]
# ## Summary
#
# - All 7 defense system families are detectable.
# - `interproscan_domains` (833M rows) uses version-free Pfam accessions.
# - `bakta_pfam_domains` (18.8M rows) uses versioned accessions (`PFXXXXX.Y`) and is a narrower cross-check.
# - `eggnog_mapper_annotations` (93M rows) description-based classification is best for R-M and CRISPR confirmation.
# - Species with `no_genomes >= 5` will be the analysis set for arms-race and syndromes tests.
#
# **Next**: `01_extract_defense_clusters.ipynb` runs the primary Pfam-based extraction and caches to `data/defense_gene_clusters.tsv.gz`.
