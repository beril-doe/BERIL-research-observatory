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
# # NB01 — Extract Defense-System Gene Clusters
#
# **Purpose**: For each of the 7 target defense system families, identify the
# `gene_cluster_id`s across the BERDL pangenome that carry the diagnostic markers.
# Persist a long-form table with one row per (gene_cluster_id, system, marker) hit
# for downstream species-level aggregation in NB02.
#
# **Two-source strategy** (from `RESEARCH_PLAN.md` §"Defense System Detection Rules"):
#
# 1. **Pfam-based (primary)**: `interproscan_domains` filtered by defense Pfam
#    accessions (version-free), joined to `gene_cluster` for species mapping.
# 2. **Description-based (secondary)**: `eggnog_mapper_annotations` for R-M
#    (Type I & II) and confirmatory CRISPR calls.
#
# **Output**: `data/defense_gene_clusters.tsv.gz` — columns `gene_cluster_id`,
# `gtdb_species_clade_id`, `is_core`, `is_auxiliary`, `is_singleton`, `system`,
# `subtype`, `marker`, `source`.

# %%
import os
import pandas as pd
from berdl_notebook_utils.setup_spark_session import get_spark_session

spark = get_spark_session()
print("Spark version:", spark.version)

DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

# %% [markdown]
# ## 1. Defense system → Pfam marker map
#
# Locked from Phase A. Note: `subtype` distinguishes CRISPR-Cas types.
# Broad-Pfam markers are flagged for species-level co-occurrence filtering in NB02.

# %%
# (system, subtype, pfam_accession, marker_name, is_broad)
PFAM_MARKERS = [
    # CRISPR-Cas — Cas1/2 are universal; others subtype
    ("CRISPR-Cas", "any",    "PF01867", "Cas1",             False),
    ("CRISPR-Cas", "any",    "PF09707", "Cas2",             False),
    ("CRISPR-Cas", "Type I", "PF18019", "Cas3_HD",          False),
    ("CRISPR-Cas", "Type I", "PF22590", "Cas3-like_C_2",    False),
    ("CRISPR-Cas", "Type I", "PF01881", "Cas_Cas6_C",       False),
    ("CRISPR-Cas", "Type II","PF22702", "Cas9_RuvC",        False),
    ("CRISPR-Cas", "Type II","PF16595", "Cas9_PI",          False),
    ("CRISPR-Cas", "Type III","PF22335","Cas10-Cmr2_palm2", False),
    ("CRISPR-Cas", "Type V", "PF07282", "Cas12f1-like",     False),
    # CBASS — all specific
    ("CBASS",      "any",    "PF18178", "CD-NTase",         False),
    ("CBASS",      "any",    "PF14090", "SAVED",            False),
    ("CBASS",      "any",    "PF19918", "Cap6",             False),
    # Gabija — GajA-specific
    ("Gabija",     "any",    "PF20473", "OLD_TOPRIM_C",     False),
    # Retron — broad RT (needs co-occurrence context in NB02)
    ("Retron",     "any",    "PF00078", "RVT_1",            True),
    # BREX
    ("BREX",       "any",    "PF08843", "PglZ",             False),
    ("BREX",       "any",    "PF13175", "BrxC",             False),
    ("BREX",       "any",    "PF13401", "BrxL_AAA_11",      False),
    # DISARM — broad PLD (needs DrmB context in NB02)
    ("DISARM",     "any",    "PF13091", "DrmC_PLD",         True),
    ("DISARM",     "any",    "PF00176", "DrmB_SNF2",        True),
]

markers_df = pd.DataFrame(PFAM_MARKERS, columns=["system", "subtype", "pfam_acc", "marker_name", "is_broad"])
print(f"{len(markers_df)} Pfam markers across {markers_df['system'].nunique()} systems")
markers_df

# %% [markdown]
# ## 2. Pfam-based defense hits
#
# Single query — filter `interproscan_domains` by the 19 signature Pfams, join
# to `gene_cluster` for species & core/aux/singleton flags. Cache to Parquet.

# %%
pfam_list = "', '".join(markers_df["pfam_acc"].tolist())

pfam_query = f"""
SELECT
    ipr.gene_cluster_id,
    ipr.signature_acc AS marker_pfam,
    gc.gtdb_species_clade_id,
    gc.is_core,
    gc.is_auxiliary,
    gc.is_singleton
FROM kbase_ke_pangenome.interproscan_domains ipr
JOIN kbase_ke_pangenome.gene_cluster gc
  ON ipr.gene_cluster_id = gc.gene_cluster_id
WHERE ipr.analysis = 'Pfam'
  AND ipr.signature_acc IN ('{pfam_list}')
"""

pfam_hits = spark.sql(pfam_query)
pfam_hits.createOrReplaceTempView("pfam_hits")

# Multi-hit accounting: one row per (gene_cluster_id, marker_pfam)
raw_count = spark.sql("SELECT COUNT(*) AS n FROM pfam_hits").collect()[0]["n"]
distinct_clusters = spark.sql("SELECT COUNT(DISTINCT gene_cluster_id) AS n FROM pfam_hits").collect()[0]["n"]
print(f"Pfam-based rows: {raw_count:,}")
print(f"Distinct gene clusters: {distinct_clusters:,}")

# %% [markdown]
# ## 3. Per-marker hit distribution (sanity check)

# %%
per_marker = spark.sql("""
    SELECT marker_pfam, COUNT(*) AS n_hits, COUNT(DISTINCT gene_cluster_id) AS n_clusters
    FROM pfam_hits
    GROUP BY marker_pfam
    ORDER BY n_hits DESC
""").toPandas()
per_marker = per_marker.merge(markers_df, left_on="marker_pfam", right_on="pfam_acc", how="left")
per_marker[["system", "subtype", "marker_pfam", "marker_name", "is_broad", "n_hits", "n_clusters"]]

# %% [markdown]
# ## 4. eggNOG description-based hits (R-M + CRISPR)
#
# R-M is best captured via eggNOG description strings (validated in Phase A:
# 27K Type II + 245K Type I). Also add CRISPR description hits as confirmatory.

# %%
eggnog_query = """
SELECT
    e.query_name AS gene_cluster_id,
    gc.gtdb_species_clade_id,
    gc.is_core,
    gc.is_auxiliary,
    gc.is_singleton,
    e.Description,
    e.PFAMs,
    CASE
        WHEN lower(e.Description) LIKE '%type ii restriction%'
          OR lower(e.Description) LIKE '%type-2 restriction%'
             THEN 'R-M Type II'
        WHEN lower(e.Description) LIKE '%type i restriction%'
          OR lower(e.Description) LIKE '%type-1 restriction%'
          OR lower(e.PFAMs) LIKE '%hsdr%'
          OR lower(e.PFAMs) LIKE '%hsdm%'
          OR lower(e.PFAMs) LIKE '%hsds%'
             THEN 'R-M Type I'
        WHEN lower(e.Description) LIKE '%crispr%' OR lower(e.Description) LIKE '%cas9%'
             THEN 'CRISPR-Cas'
        ELSE NULL
    END AS system_call
FROM kbase_ke_pangenome.eggnog_mapper_annotations e
JOIN kbase_ke_pangenome.gene_cluster gc
  ON e.query_name = gc.gene_cluster_id
WHERE lower(e.Description) LIKE '%type ii restriction%'
   OR lower(e.Description) LIKE '%type-2 restriction%'
   OR lower(e.Description) LIKE '%type i restriction%'
   OR lower(e.Description) LIKE '%type-1 restriction%'
   OR lower(e.PFAMs) LIKE '%hsdr%'
   OR lower(e.PFAMs) LIKE '%hsdm%'
   OR lower(e.PFAMs) LIKE '%hsds%'
   OR lower(e.Description) LIKE '%crispr%'
   OR lower(e.Description) LIKE '%cas9%'
"""

eggnog_hits = spark.sql(eggnog_query)
eggnog_hits.createOrReplaceTempView("eggnog_hits")

egg_count = spark.sql("SELECT COUNT(*) FROM eggnog_hits").collect()[0][0]
egg_distinct = spark.sql("SELECT COUNT(DISTINCT gene_cluster_id) FROM eggnog_hits").collect()[0][0]
print(f"eggNOG-based rows: {egg_count:,}")
print(f"Distinct clusters: {egg_distinct:,}")

egg_by_system = spark.sql("""
    SELECT system_call, COUNT(*) AS n_rows, COUNT(DISTINCT gene_cluster_id) AS n_clusters
    FROM eggnog_hits
    WHERE system_call IS NOT NULL
    GROUP BY system_call
    ORDER BY n_rows DESC
""").toPandas()
egg_by_system

# %% [markdown]
# ## 5. Assemble unified defense-hits table
#
# One row per (gene_cluster_id × marker × system × source). This is the raw hit
# table; NB02 aggregates to species-level and applies broad-Pfam co-occurrence
# rules.

# %%
# Build system+subtype+marker+is_broad lookup from markers_df; make it a
# Spark-side dataframe for a clean join
markers_spark = spark.createDataFrame(markers_df)
markers_spark.createOrReplaceTempView("markers_spark")

pfam_hits_labeled = spark.sql("""
    SELECT
        p.gene_cluster_id,
        p.gtdb_species_clade_id,
        p.is_core,
        p.is_auxiliary,
        p.is_singleton,
        m.system,
        m.subtype,
        p.marker_pfam AS marker,
        m.is_broad,
        'interproscan_pfam' AS source
    FROM pfam_hits p
    JOIN markers_spark m ON p.marker_pfam = m.pfam_acc
""")

eggnog_hits_labeled = spark.sql("""
    SELECT
        gene_cluster_id,
        gtdb_species_clade_id,
        is_core,
        is_auxiliary,
        is_singleton,
        system_call AS system,
        'any' AS subtype,
        'eggnog_description' AS marker,
        false AS is_broad,
        'eggnog_description' AS source
    FROM eggnog_hits
    WHERE system_call IS NOT NULL
""")

all_hits = pfam_hits_labeled.unionByName(eggnog_hits_labeled)
all_hits.createOrReplaceTempView("all_hits")

total = spark.sql("SELECT COUNT(*) FROM all_hits").collect()[0][0]
print(f"Total unified hit rows: {total:,}")

# %% [markdown]
# ## 6. Sanity: system × source summary

# %%
sys_source = spark.sql("""
    SELECT system, source, COUNT(*) AS n_rows,
           COUNT(DISTINCT gene_cluster_id) AS n_clusters,
           COUNT(DISTINCT gtdb_species_clade_id) AS n_species
    FROM all_hits
    GROUP BY system, source
    ORDER BY system, source
""").toPandas()
sys_source

# %% [markdown]
# ## 7. Persist to TSV
#
# Convert to pandas (~500K rows is fine on driver) then write as gzip-compressed
# TSV. Matches the pattern in `prophage_ecology/notebooks/01_prophage_gene_discovery.ipynb`.
# Spark Connect writes go to cluster storage, not local FS, so pandas-side write
# is the correct pattern for on-cluster notebook artifacts.

# %%
all_hits_pd = all_hits.toPandas()
output_path = os.path.abspath(os.path.join(DATA_DIR, "defense_gene_clusters.tsv.gz"))
all_hits_pd.to_csv(output_path, sep="\t", index=False, compression="gzip")
print(f"Wrote: {output_path}")
print(f"Rows: {len(all_hits_pd):,}")
print(f"Columns: {list(all_hits_pd.columns)}")

# Sanity: unique species covered by at least one defense hit
print(f"\nUnique species with any defense hit: {all_hits_pd['gtdb_species_clade_id'].nunique():,}")
print(f"Unique gene clusters: {all_hits_pd['gene_cluster_id'].nunique():,}")

# %% [markdown]
# ## Summary
#
# - Pfam-based defense hits extracted for 19 markers across 7 systems.
# - eggNOG description-based hits added for R-M Type I / II and CRISPR-Cas.
# - Unified long-form table cached to `data/defense_gene_clusters.tsv.gz`.
# - Broad-Pfam markers (`is_broad = true`) flagged for co-occurrence filtering in NB02.
#
# **Next**: `02_species_system_matrix.ipynb` — aggregate hits to per-species
# system-presence matrix; apply broad-Pfam co-occurrence rules; add covariates
# (genome size, phylum, no_genomes).
