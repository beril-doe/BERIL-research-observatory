"""Author NB01: TA-Pfam Extraction against BERDL pangenome.

This script generates NB01_ta_pfam_extraction.ipynb. NB01 itself is
Spark-dependent and must be executed on BERDL JupyterHub (or with an
active proxy chain to spark_connect_remote).
"""

from __future__ import annotations

import json
from pathlib import Path


def code_cell(src: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in src.rstrip().split("\n")],
    }


def md_cell(src: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in src.rstrip().split("\n")],
    }


CELLS = [
    md_cell(
        """# NB01 — TA-Pfam Extraction

**Requires BERDL JupyterHub** (or an active `spark_connect_remote` proxy chain locally).

Extracts every gene cluster in `kbase_ke_pangenome` that carries at least one Type II toxin-antitoxin (TA) Pfam signature, joins core/accessory status and species assignment, and persists two tidy TSVs:

- `data/ta_hits_by_gene_cluster.tsv` — one row per gene-cluster × Pfam hit
- `data/ta_per_species.tsv` — per-species TA-locus counts partitioned by core / accessory / singleton

Panel of TA Pfam accessions is loaded from `data/ta_families_seed.tsv`. This seed panel covers the 12 best-characterized Type II TA families with high-confidence Pfam assignments. NB01 audits the seed against `pangenome.eggnog_mapper_annotations` coverage and reports any families that produce zero hits (a signal that the Pfam ID may need revision)."""
    ),
    code_cell(
        """spark = get_spark_session()

import numpy as np
import pandas as pd
from pathlib import Path

DATA = Path('../data')
DATA.mkdir(exist_ok=True)"""
    ),
    md_cell("## 1. Load the TA family panel"),
    code_cell(
        """panel = pd.read_csv(DATA / 'ta_families_seed.tsv', sep='\\t')
print(f"Loaded {len(panel)} TA families")
panel"""
    ),
    code_cell(
        """# Build a de-duplicated set of Pfam accessions across toxin + antitoxin sides
pfam_ids = sorted(set(panel['toxin_pfam'].dropna()) | set(panel['antitoxin_pfam'].dropna()))
print(f"Panel contains {len(pfam_ids)} unique Pfam accessions:")
print(', '.join(pfam_ids))"""
    ),
    md_cell("## 2. Baseline table sizes"),
    code_cell(
        """for t in ['eggnog_mapper_annotations', 'gene_cluster', 'genome', 'pangenome', 'gtdb_species_clade']:
    n = spark.sql(f"SELECT COUNT(*) c FROM kbase_ke_pangenome.{t}").collect()[0]['c']
    print(f"{t:>32s}  {n:>14,d} rows")"""
    ),
    md_cell(
        """## 3. Confirm PFAMs column format

Sample a handful of non-null PFAMs strings to confirm the delimiter (comma expected, but may include Pfam version suffixes like `PF06769.5`)."""
    ),
    code_cell(
        """spark.sql(\"\"\"
    SELECT query_name, PFAMs
    FROM kbase_ke_pangenome.eggnog_mapper_annotations
    WHERE PFAMs IS NOT NULL AND PFAMs != '-'
    LIMIT 20
\"\"\").show(20, truncate=False)"""
    ),
    md_cell(
        """## 4. Query TA-Pfam-carrying gene clusters

Rather than a single expensive regex over 93M rows, we issue the panel as an `IN`-list of concrete substrings and use Spark's predicate pushdown. The `LIKE ANY (...)` idiom expands to `PFAMs LIKE '%PFxxxxx%' OR PFAMs LIKE ...`."""
    ),
    code_cell(
        """# Build a SQL disjunction: PFAMs LIKE '%PF06769%' OR PFAMs LIKE '%PF04221%' OR ...
# Anchored on the accession stem so that version suffixes are matched too.
like_clauses = " OR ".join([f"PFAMs LIKE '%{pf}%'" for pf in pfam_ids])
print(f"OR-clauses: {len(pfam_ids)}")

hits_sql = f\"\"\"
    SELECT query_name, PFAMs, COG_category
    FROM kbase_ke_pangenome.eggnog_mapper_annotations
    WHERE ({like_clauses})
\"\"\"
hits_df = spark.sql(hits_sql)
n_hits = hits_df.count()
print(f"Gene clusters with at least one TA Pfam hit: {n_hits:,}")"""
    ),
    md_cell(
        """## 5. Join core/accessory status + species assignment

The `gene_cluster` table gives us `is_core` (bool) and `gtdb_species_clade_id` per gene cluster. Singleton status is available through the pangenome table by convention (a species' singleton_gene_clusters is a subset of accessory)."""
    ),
    code_cell(
        """hits_df.createOrReplaceTempView("ta_hits")

joined = spark.sql(\"\"\"
    SELECT
        gc.gene_cluster_id,
        gc.gtdb_species_clade_id,
        gc.is_core,
        gc.is_singleton,
        h.PFAMs,
        h.COG_category
    FROM ta_hits h
    JOIN kbase_ke_pangenome.gene_cluster gc
        ON gc.gene_cluster_id = h.query_name
\"\"\")

hits_tidy = joined.toPandas()
print(f"Rows after join: {len(hits_tidy):,}")
hits_tidy.head()"""
    ),
    md_cell("## 6. Explode into (gene_cluster, matched_pfam) long form"),
    code_cell(
        """# One gene cluster may hit multiple TA Pfams (e.g., a fused toxin-antitoxin ORF)
# or the same PFAMs entry may list an unrelated Pfam alongside a TA Pfam.
# Explode to (gene_cluster, ta_pfam) so downstream counts are unambiguous.

pfam_set = set(pfam_ids)

def matched_ta_pfams(pfams_str: str) -> list[str]:
    if not isinstance(pfams_str, str) or pfams_str == '-':
        return []
    tokens = {tok.split('.')[0].strip() for tok in pfams_str.split(',')}
    return sorted(tokens & pfam_set)

hits_tidy['matched_ta_pfams'] = hits_tidy['PFAMs'].apply(matched_ta_pfams)
hits_long = hits_tidy.explode('matched_ta_pfams').rename(columns={'matched_ta_pfams': 'ta_pfam'})
hits_long = hits_long.dropna(subset=['ta_pfam'])
print(f"Long-form rows (gene_cluster × ta_pfam): {len(hits_long):,}")

# Annotate with family and toxin/antitoxin side
side_map = {}
family_map = {}
for _, row in panel.iterrows():
    fam = row['family']
    if pd.notna(row['toxin_pfam']):
        side_map[row['toxin_pfam']] = 'toxin'
        family_map[row['toxin_pfam']] = fam
    if pd.notna(row['antitoxin_pfam']):
        # If a Pfam is shared between families, first family wins
        side_map.setdefault(row['antitoxin_pfam'], 'antitoxin')
        family_map.setdefault(row['antitoxin_pfam'], fam)

hits_long['side'] = hits_long['ta_pfam'].map(side_map)
hits_long['family'] = hits_long['ta_pfam'].map(family_map)
hits_long.head()"""
    ),
    md_cell("## 7. Panel-coverage audit"),
    code_cell(
        """coverage = hits_long.groupby('ta_pfam').size().reindex(pfam_ids, fill_value=0).rename('n_hits')
coverage_df = pd.DataFrame({'ta_pfam': coverage.index, 'n_hits': coverage.values})
coverage_df['side'] = coverage_df['ta_pfam'].map(side_map)
coverage_df['family'] = coverage_df['ta_pfam'].map(family_map)
coverage_df = coverage_df.sort_values('n_hits', ascending=False)

zero_hit = coverage_df[coverage_df['n_hits'] == 0]
print(f"Panel Pfams with zero hits (candidate for revision): {len(zero_hit)}")
print(zero_hit)
coverage_df"""
    ),
    md_cell("## 8. Persist gene-cluster-level TSV"),
    code_cell(
        """# Save a compact long-form table for NB02/NB03
out1 = DATA / 'ta_hits_by_gene_cluster.tsv'
hits_long[
    ['gene_cluster_id', 'gtdb_species_clade_id', 'is_core', 'is_singleton',
     'ta_pfam', 'side', 'family', 'PFAMs', 'COG_category']
].to_csv(out1, sep='\\t', index=False)
print(f"Wrote {out1}  ({out1.stat().st_size / 1e6:.1f} MB)")"""
    ),
    md_cell(
        """## 9. Aggregate to species-level counts

For each species: number of TA-locus gene clusters overall, and split by core / accessory / singleton. Also compute median genome size (Mb) so we can normalize to per-Mb rates in NB02."""
    ),
    code_cell(
        """# Species-level TA gene-cluster counts, partitioned by core/accessory/singleton
def bin_status(row):
    if row['is_core']:
        return 'core'
    if row['is_singleton']:
        return 'singleton'
    return 'accessory'

# Distinct gene clusters (a cluster may have hit both toxin and antitoxin Pfams)
gene_cluster_status = (
    hits_long.drop_duplicates(subset=['gene_cluster_id'])
    .assign(status=lambda d: d.apply(bin_status, axis=1))
)

per_species = (
    gene_cluster_status.groupby(['gtdb_species_clade_id', 'status'])
    .size().unstack(fill_value=0)
    .reindex(columns=['core', 'accessory', 'singleton'], fill_value=0)
    .reset_index()
)
per_species['ta_total'] = per_species[['core', 'accessory', 'singleton']].sum(axis=1)
per_species = per_species.rename(columns={
    'core': 'ta_core', 'accessory': 'ta_accessory', 'singleton': 'ta_singleton'})
print(f"Species with at least one TA hit: {len(per_species):,}")
per_species.head()"""
    ),
    code_cell(
        """# Family composition per species: for each TA family, count of gene clusters carrying that family
per_species_family = (
    gene_cluster_status.groupby(['gtdb_species_clade_id', 'family'])
    .size().unstack(fill_value=0)
    .reset_index()
)
print(f"Family composition matrix: {per_species_family.shape}")
per_species_family.head()"""
    ),
    md_cell("## 10. Median genome size per species (for per-Mb normalization)"),
    code_cell(
        """species_ids = per_species['gtdb_species_clade_id'].dropna().unique().tolist()
# Batch to keep the IN-list manageable
BATCH = 500
frames = []
for i in range(0, len(species_ids), BATCH):
    batch = species_ids[i:i+BATCH]
    in_clause = "', '".join([s.replace("'", "''") for s in batch])
    frames.append(spark.sql(f\"\"\"
        SELECT gtdb_species_clade_id,
               PERCENTILE_APPROX(total_length, 0.5) AS median_size_bp,
               COUNT(*) AS n_genomes_seen
        FROM kbase_ke_pangenome.genome
        WHERE gtdb_species_clade_id IN ('{in_clause}')
        GROUP BY gtdb_species_clade_id
    \"\"\").toPandas())

genome_size = pd.concat(frames, ignore_index=True)
genome_size['median_size_mb'] = genome_size['median_size_bp'] / 1e6
print(f"Species with genome-size info: {len(genome_size):,}")
genome_size.head()"""
    ),
    md_cell("## 11. Persist per-species outputs"),
    code_cell(
        """out2 = DATA / 'ta_per_species.tsv'
merged = per_species.merge(genome_size[['gtdb_species_clade_id', 'median_size_mb', 'n_genomes_seen']],
                            on='gtdb_species_clade_id', how='left')
merged['ta_per_mb'] = merged['ta_total'] / merged['median_size_mb']
merged.to_csv(out2, sep='\\t', index=False)
print(f"Wrote {out2}  ({merged.shape[0]:,} species)")
merged.head()"""
    ),
    code_cell(
        """out3 = DATA / 'ta_family_composition_per_species.tsv'
per_species_family.to_csv(out3, sep='\\t', index=False)
print(f"Wrote {out3}  ({per_species_family.shape[0]:,} species × {per_species_family.shape[1]-1} families)")"""
    ),
    code_cell(
        """out4 = DATA / 'ta_panel_coverage.tsv'
coverage_df.to_csv(out4, sep='\\t', index=False)
print(f"Wrote {out4}")"""
    ),
    md_cell(
        """## 12. Baselines for H1 (genome-wide gene-cluster status distribution)

To test H1 (TA loci are predominantly accessory), we need the null: the fraction of *all* gene clusters that are core, accessory, singleton, per-species. NB02 uses these as the baseline for TA-cluster enrichment."""
    ),
    code_cell(
        """# Species-level baseline: core / accessory / singleton counts across ALL gene clusters
frames = []
species_ids = per_species['gtdb_species_clade_id'].dropna().unique().tolist()
for i in range(0, len(species_ids), BATCH):
    batch = species_ids[i:i+BATCH]
    in_clause = "', '".join([s.replace("'", "''") for s in batch])
    frames.append(spark.sql(f\"\"\"
        SELECT
            gtdb_species_clade_id,
            SUM(CASE WHEN is_core THEN 1 ELSE 0 END) AS all_core,
            SUM(CASE WHEN is_singleton THEN 1 ELSE 0 END) AS all_singleton,
            SUM(CASE WHEN NOT is_core AND NOT is_singleton THEN 1 ELSE 0 END) AS all_accessory,
            COUNT(*) AS all_gene_clusters
        FROM kbase_ke_pangenome.gene_cluster
        WHERE gtdb_species_clade_id IN ('{in_clause}')
        GROUP BY gtdb_species_clade_id
    \"\"\").toPandas())

baseline = pd.concat(frames, ignore_index=True)
out5 = DATA / 'species_gene_cluster_baseline.tsv'
baseline.to_csv(out5, sep='\\t', index=False)
print(f"Wrote {out5}  ({len(baseline):,} species)")
baseline.head()"""
    ),
    md_cell(
        """## 13. Summary

Outputs:

| File | Rows | Purpose |
|---|---|---|
| `ta_hits_by_gene_cluster.tsv` | one row per gene-cluster × ta_pfam | Long-form Pfam hits with core/accessory/species |
| `ta_per_species.tsv` | one row per species | TA counts partitioned by status + genome size |
| `ta_family_composition_per_species.tsv` | species × families | For H3 (family-composition asymmetry) |
| `ta_panel_coverage.tsv` | one row per Pfam | Panel audit — flags Pfams with zero hits |
| `species_gene_cluster_baseline.tsv` | one row per species | Genome-wide core/accessory baseline for H1 |

Downstream: NB02 joins on lifestyle labels and runs H1/H2 tests locally; NB03 computes family composition (H3) and phylum-stratified controls."""
    ),
]

NB = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main() -> None:
    out = Path(__file__).parent.parent / "notebooks" / "NB01_ta_pfam_extraction.ipynb"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(NB, indent=1))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
