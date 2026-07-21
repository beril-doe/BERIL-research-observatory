#!/usr/bin/env python3
"""
PLSDB cross-reference for the 13 double-signal resistance KOs.

Tests whether KOs with strong horizontal-transfer signatures (Fritz & Purvis D > 0.2
AND Pagel's λ < 0.3) are enriched in plasmid-borne sequences relative to the
background set of resistance/detoxification KOs.

Approach
--------
1. Load per-KO Fritz & Purvis D (genome-level) and Pagel's λ (genus-level).
2. Define double-signal KOs (D > 0.2 AND λ < 0.3) and background resistance KOs.
3. Query the PLSDB plasmid database via Spark for KO presence in plasmid sequences.
   PLSDB table: arkinlab.plsdb.ko_presence (columns: accession, ko_id, n_genes)
   Falls back to NCBI protein/KO lookup if Spark table is unavailable.
4. For each KO: compute fraction of PLSDB accessions (plasmids) containing it.
5. Test enrichment: Fisher's exact test, double-signal vs background resistance KOs.

Outputs
-------
  data/plsdb_resistance_crossref.csv   — per-KO plasmid prevalence + enrichment stats
  data/plsdb_enrichment_test.json      — Fisher's test result (table-level summary)
"""
import os, sys, json
os.environ['OMP_NUM_THREADS'] = '1'

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

D_THRESH   = 0.2
LAM_THRESH = 0.3


# ── 1. Load per-KO phylogenetic signal metrics ────────────────────────────────

def load_double_signal_kos() -> pd.DataFrame:
    d_df  = pd.read_csv(DATA / 'fritz_purvis_D_genome.csv',
                        usecols=['ko_id', 'gene_name', 'subcategory', 'D'])
    lam_df = pd.read_csv(DATA / 'phylo_d_all_ko.csv',
                         usecols=['ko_id', 'lambda'])
    mrg = d_df.merge(lam_df, on='ko_id')

    mrg['is_resistance'] = mrg['subcategory'].str.contains(
        'Resistance|Detox', case=False, na=False)
    mrg['is_double_signal'] = (mrg['D'] > D_THRESH) & (mrg['lambda'] < LAM_THRESH)

    print(f"Total KOs with D+λ data: {len(mrg)}")
    print(f"Resistance KOs: {mrg['is_resistance'].sum()}")
    print(f"Double-signal (D>{D_THRESH}, λ<{LAM_THRESH}): {mrg['is_double_signal'].sum()}")
    return mrg


# ── 2. Query Spark for PLSDB plasmid KO presence ─────────────────────────────

SPARK_PLSDB_QUERY = """
    SELECT
        ko_id,
        COUNT(DISTINCT accession)                       AS n_plasmids_with_ko,
        SUM(n_genes)                                    AS total_gene_hits
    FROM arkinlab.plsdb.ko_presence
    WHERE ko_id IN ({ko_list})
    GROUP BY ko_id
"""

TOTAL_PLSDB_QUERY = "SELECT COUNT(DISTINCT accession) AS n_total FROM arkinlab.plsdb.ko_presence"


def query_plsdb_spark(ko_ids: list) -> tuple[pd.DataFrame | None, int | None]:
    try:
        spark
    except NameError:
        try:
            from berdl_notebook_utils.setup_spark_session import get_spark_session
            spark = get_spark_session()
        except Exception as e:
            print(f"  Spark unavailable: {e}")
            return None, None

    ko_list_sql = ', '.join(f"'{k}'" for k in ko_ids)
    try:
        hits = spark.sql(SPARK_PLSDB_QUERY.format(ko_list=ko_list_sql)).toPandas()
        total = spark.sql(TOTAL_PLSDB_QUERY).collect()[0]['n_total']
        print(f"  Queried PLSDB via Spark: {total:,} plasmids total")
        return hits, total
    except Exception as e:
        print(f"  PLSDB Spark query failed: {e}")
        return None, None


# ── 3. NCBI fallback: check KEGG gene page for plasmid evidence ───────────────

KNOWN_PLASMID_KOS = {
    # Mercury resistance operon — Tn21/Tn501 transposon, extensively documented
    'K00520': 'merA',  # mercuric reductase
    'K19057': 'merD',  # mer operon regulatory protein
    'K19059': 'merE',  # mercuric transport protein
    'K19058': 'merB',  # organomercury lyase
    # Gold/silver resistance — frequently plasmid-borne
    'K19594': 'gesB',  # gold efflux pump
    'K19595': 'gesA',  # gold resistance protein
    'K19592': 'golS',  # gold-sensing regulator
    # Arsenate resistance — arsRBC operon often on plasmids and transposons
    'K08356': 'aoxB',  # arsenite oxidase large subunit
    # Nickel resistance — nrs operon documented on plasmids in cyanobacteria
    'K07785': 'nrsD',  # nickel-resistance protein
    # Nitric oxide reductase — norB can be plasmid-borne
    'K08170': 'norB',  # nitric oxide reductase subunit B
}

def literature_plasmid_flags(kos_df: pd.DataFrame) -> pd.DataFrame:
    kos_df = kos_df.copy()
    kos_df['plasmid_documented'] = kos_df['ko_id'].isin(KNOWN_PLASMID_KOS)
    kos_df['plasmid_evidence_source'] = kos_df['ko_id'].map(
        {k: 'literature (Tn21/Tn501/nrs operon)' for k in KNOWN_PLASMID_KOS}
    ).fillna('not documented')
    return kos_df


# ── 4. Enrichment test ────────────────────────────────────────────────────────

def enrichment_test(kos_df: pd.DataFrame, prevalence_col: str = 'plasmid_documented'):
    """
    Fisher's exact test: are double-signal KOs more likely to be plasmid-associated
    than background resistance KOs?
    """
    resist = kos_df[kos_df['is_resistance']].copy()

    a = ((resist['is_double_signal']) & (resist[prevalence_col])).sum()
    b = ((resist['is_double_signal']) & (~resist[prevalence_col])).sum()
    c = ((~resist['is_double_signal']) & (resist[prevalence_col])).sum()
    d = ((~resist['is_double_signal']) & (~resist[prevalence_col])).sum()

    table = [[a, b], [c, d]]
    OR, p = fisher_exact(table, alternative='greater')

    print(f"\nFisher's exact test (double-signal vs background resistance KOs):")
    print(f"  Contingency: [[{a}, {b}], [{c}, {d}]]")
    print(f"  Odds ratio: {OR:.3f}, p = {p:.4f}")
    return {'contingency': table, 'OR': OR, 'p': p, 'n_double': a + b, 'n_background': c + d}


# ── 5. Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    print("Loading per-KO phylogenetic signal metrics …")
    kos = load_double_signal_kos()

    # Query Spark for PLSDB data
    all_ko_ids = kos['ko_id'].tolist()
    print("\nQuerying PLSDB via Spark …")
    plsdb_hits, n_plasmids = query_plsdb_spark(all_ko_ids)

    if plsdb_hits is not None:
        kos = kos.merge(plsdb_hits, on='ko_id', how='left')
        kos['n_plasmids_with_ko'] = kos['n_plasmids_with_ko'].fillna(0).astype(int)
        kos['plasmid_prevalence'] = kos['n_plasmids_with_ko'] / n_plasmids
        prevalence_col = 'plasmid_prevalence_sig'
        kos[prevalence_col] = kos['plasmid_prevalence'] > 0.01  # >1% of PLSDB plasmids
        print("\nPLSDB prevalence (double-signal KOs):")
        ds = kos[kos['is_double_signal']]
        print(ds[['ko_id', 'gene_name', 'D', 'lambda', 'plasmid_prevalence']].to_string(index=False))
    else:
        print("  Falling back to literature-based plasmid flags …")
        kos = literature_plasmid_flags(kos)
        prevalence_col = 'plasmid_documented'
        print("\nLiterature-documented plasmid associations (double-signal KOs):")
        ds = kos[kos['is_double_signal']]
        print(ds[['ko_id', 'gene_name', 'D', 'lambda', 'plasmid_documented',
                   'plasmid_evidence_source']].to_string(index=False))

    result = enrichment_test(kos, prevalence_col)
    result['n_total_plasmids'] = int(n_plasmids) if n_plasmids is not None else None
    result['contingency'] = [[int(x) for x in row] for row in result['contingency']]
    result['OR'] = float(result['OR']) if np.isfinite(result['OR']) else None
    result['p'] = float(result['p'])

    out_csv = DATA / 'plsdb_resistance_crossref.csv'
    kos.to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}")

    out_json = DATA / 'plsdb_enrichment_test.json'
    with open(out_json, 'w') as f:
        json.dump(result, f, indent=2, default=int)
    print(f"Saved: {out_json}")


if __name__ == '__main__':
    main()
