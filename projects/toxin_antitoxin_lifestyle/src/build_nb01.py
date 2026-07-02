"""Author NB01: TA-Pfam Extraction against BERDL pangenome.

This script generates NB01_ta_pfam_extraction.ipynb. NB01 itself is
Spark-dependent and must be executed on BERDL JupyterHub (or with an
active spark_connect_remote proxy chain locally).

Matches against Pfam NAMES (e.g. "RelE", "HipA_C") in the comma-delimited
`PFAMs` column of `eggnog_mapper_annotations` — the column stores names,
not PFxxxxx accessions.
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

Extracts every gene cluster in `kbase_ke_pangenome` that carries at least one Type II toxin-antitoxin (TA) Pfam signature, joins core/accessory status and species assignment, and persists tidy TSVs for downstream lifestyle analysis.

## Panel

`data/ta_families_seed.tsv` lists Pfam NAMES (not PF accessions) — the `PFAMs` column of `eggnog_mapper_annotations` stores comma-delimited names like `RelE`, `HipA_C`, `MazE_antitoxin`. Panel audit in cell 6 reports zero-hit names for revision.

## Note on generic domains

- `PIN` is used by many non-TA ribonucleases; we count it only under family VapBC and flag it as "broad" in the coverage audit.
- Some antitoxins share `HTH_24`, `HTH_37` — we don't include generic HTH names in the panel to avoid contamination.
"""
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
        """# De-duplicated set of Pfam NAMES across toxin + antitoxin sides
pfam_names = sorted(
    set(panel['toxin_pfam_name'].dropna())
    | set(panel['antitoxin_pfam_name'].dropna())
)
print(f"Panel contains {len(pfam_names)} unique Pfam names:")
print(', '.join(pfam_names))"""
    ),
    md_cell("## 2. Baseline table sizes"),
    code_cell(
        """for t in ['eggnog_mapper_annotations', 'gene_cluster', 'genome', 'pangenome', 'gtdb_species_clade']:
    n = spark.sql(f"SELECT COUNT(*) c FROM kbase_ke_pangenome.{t}").collect()[0]['c']
    print(f"{t:>32s}  {n:>14,d} rows")"""
    ),
    md_cell(
        """## 3. Per-name panel-coverage audit

We probe each name with a token-safe LIKE (exact match OR leading OR trailing OR interior in the comma-delimited PFAMs string). Names hitting zero are flagged for revision — the seed panel notes suggest which."""
    ),
    code_cell(
        """def token_where(col: str, name: str) -> str:
    n = name.replace("'", "''")
    return (
        f"({col} = '{n}' OR "
        f"{col} LIKE '{n},%' OR "
        f"{col} LIKE '%,{n}' OR "
        f"{col} LIKE '%,{n},%')"
    )

rows = []
for name in pfam_names:
    q = f\"\"\"
        SELECT COUNT(*) AS c
        FROM kbase_ke_pangenome.eggnog_mapper_annotations
        WHERE {token_where('PFAMs', name)}
    \"\"\"
    n = spark.sql(q).collect()[0]['c']
    rows.append({'pfam_name': name, 'n_annotations': n})

coverage_df = pd.DataFrame(rows).sort_values('n_annotations', ascending=False)
print(f"Panel Pfams with zero hits: {(coverage_df['n_annotations'] == 0).sum()}")
coverage_df"""
    ),
    md_cell("## 4. Extract TA-carrying gene clusters"),
    code_cell(
        """# Restrict to Pfam names that actually hit (drops zero-hit names)
active_names = coverage_df.loc[coverage_df['n_annotations'] > 0, 'pfam_name'].tolist()
print(f"{len(active_names)} active Pfam names of {len(pfam_names)} in panel")

# Build a UNION of token-safe queries — one per name, small distinct sets
where_clauses = " OR ".join([token_where('PFAMs', n) for n in active_names])

hits_df = spark.sql(f\"\"\"
    SELECT query_name, PFAMs, COG_category
    FROM kbase_ke_pangenome.eggnog_mapper_annotations
    WHERE {where_clauses}
\"\"\")
n_hits = hits_df.count()
print(f"Gene clusters with at least one TA Pfam hit: {n_hits:,}")"""
    ),
    md_cell("## 5. Join core/accessory status + species assignment"),
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
print(f"Rows after join to gene_cluster: {len(hits_tidy):,}")
hits_tidy.head()"""
    ),
    md_cell(
        """## 6. Explode PFAMs → (gene_cluster, matched_pfam_name, side, family)"""
    ),
    code_cell(
        """name_set = set(active_names)

def matched_names(pfams_str: str) -> list[str]:
    if not isinstance(pfams_str, str) or pfams_str == '-':
        return []
    tokens = {tok.strip() for tok in pfams_str.split(',')}
    return sorted(tokens & name_set)

hits_tidy['matched_names'] = hits_tidy['PFAMs'].apply(matched_names)
hits_long = hits_tidy.explode('matched_names').rename(columns={'matched_names': 'pfam_name'})
hits_long = hits_long.dropna(subset=['pfam_name'])
print(f"Long-form rows (gene_cluster × pfam_name): {len(hits_long):,}")

# Annotate with family and toxin/antitoxin side (allow multi-family membership)
side_map: dict[str, str] = {}
family_map: dict[str, str] = {}
for _, row in panel.iterrows():
    fam = row['family']
    if pd.notna(row['toxin_pfam_name']):
        # If a name appears as both toxin and antitoxin (e.g. RelE for two families),
        # keep the toxin classification for the first-seen family
        side_map.setdefault(row['toxin_pfam_name'], 'toxin')
        family_map.setdefault(row['toxin_pfam_name'], fam)
    if pd.notna(row['antitoxin_pfam_name']):
        side_map.setdefault(row['antitoxin_pfam_name'], 'antitoxin')
        family_map.setdefault(row['antitoxin_pfam_name'], fam)

hits_long['side'] = hits_long['pfam_name'].map(side_map)
hits_long['family'] = hits_long['pfam_name'].map(family_map)
hits_long.head()"""
    ),
    md_cell("## 7. Persist gene-cluster-level TSV"),
    code_cell(
        """out1 = DATA / 'ta_hits_by_gene_cluster.tsv'
hits_long[
    ['gene_cluster_id', 'gtdb_species_clade_id', 'is_core', 'is_singleton',
     'pfam_name', 'side', 'family', 'PFAMs', 'COG_category']
].to_csv(out1, sep='\\t', index=False)
print(f"Wrote {out1}  ({out1.stat().st_size / 1e6:.1f} MB)")

out_cov = DATA / 'ta_panel_coverage.tsv'
coverage_df['side'] = coverage_df['pfam_name'].map(side_map)
coverage_df['family'] = coverage_df['pfam_name'].map(family_map)
coverage_df.to_csv(out_cov, sep='\\t', index=False)
print(f"Wrote {out_cov}")"""
    ),
    md_cell(
        """## 8. Species-level TA counts

Per-species: TA-carrying gene clusters partitioned into core / accessory / singleton buckets. A gene cluster hitting multiple TA Pfams counts once."""
    ),
    code_cell(
        """def bin_status(row):
    if row['is_core']:
        return 'core'
    if row['is_singleton']:
        return 'singleton'
    return 'accessory'

gene_cluster_status = (
    hits_long.drop_duplicates(subset=['gene_cluster_id'])
    .assign(status=lambda d: d.apply(bin_status, axis=1))
)

per_species = (
    gene_cluster_status.groupby(['gtdb_species_clade_id', 'status'])
    .size().unstack(fill_value=0)
    .reindex(columns=['core', 'accessory', 'singleton'], fill_value=0)
    .reset_index()
    .rename(columns={'core': 'ta_core', 'accessory': 'ta_accessory', 'singleton': 'ta_singleton'})
)
per_species['ta_total'] = per_species[['ta_core', 'ta_accessory', 'ta_singleton']].sum(axis=1)
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
    md_cell(
        """## 9. Median genome size per species (for per-Mb normalization in NB02)"""
    ),
    code_cell(
        """species_ids = per_species['gtdb_species_clade_id'].dropna().unique().tolist()
if not species_ids:
    raise RuntimeError("No species with TA hits — abort. Check the panel-coverage audit above.")

BATCH = 500
frames = []
for i in range(0, len(species_ids), BATCH):
    batch = species_ids[i:i+BATCH]
    in_clause = "', '".join([s.replace("'", "''") for s in batch])
    frames.append(spark.sql(f\"\"\"
        SELECT g.gtdb_species_clade_id,
               PERCENTILE_APPROX(m.genome_size, 0.5) AS median_size_bp,
               COUNT(*) AS n_genomes_seen
        FROM kbase_ke_pangenome.gtdb_metadata m
        JOIN kbase_ke_pangenome.genome g ON m.accession = g.genome_id
        WHERE g.gtdb_species_clade_id IN ('{in_clause}')
          AND m.genome_size IS NOT NULL
        GROUP BY g.gtdb_species_clade_id
    \"\"\").toPandas())

genome_size = pd.concat(frames, ignore_index=True)
genome_size['median_size_mb'] = genome_size['median_size_bp'] / 1e6
print(f"Species with genome-size info: {len(genome_size):,}")
genome_size.head()"""
    ),
    md_cell("## 10. Persist per-species outputs"),
    code_cell(
        """out2 = DATA / 'ta_per_species.tsv'
merged = per_species.merge(
    genome_size[['gtdb_species_clade_id', 'median_size_mb', 'n_genomes_seen']],
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
    md_cell(
        """## 11. Species-wide gene-cluster baseline

Genome-wide core/accessory/singleton counts per species (all gene clusters, not just TA). NB02 uses these as the null baseline for H1."""
    ),
    code_cell(
        """frames = []
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
        """## 12. Summary

Outputs:

| File | Purpose |
|---|---|
| `ta_hits_by_gene_cluster.tsv` | Long-form: one row per gene-cluster × ta_pfam_name hit |
| `ta_per_species.tsv` | Per-species TA counts (core / accessory / singleton) + genome size + per-Mb rate |
| `ta_family_composition_per_species.tsv` | Species × families matrix for H3 |
| `ta_panel_coverage.tsv` | Panel audit — flags zero-hit names |
| `species_gene_cluster_baseline.tsv` | Per-species genome-wide core/accessory baseline for H1 |

NB02 tests H1 (paired Wilcoxon + pooled chi-square) and H2 (Mann-Whitney U + rank-biserial on ta_per_mb by lifestyle) locally. NB03 will address H3 (family composition) + phylum stratification."""
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
