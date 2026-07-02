"""Author NB04: RelE co-annotation attribution + panel-scope sensitivity.

Addresses two REVIEW.md medium-priority items:
  1. RelE Pfam name is shared between RelBE and YoeB-YefM. Original
     attribution via `setdefault` collapsed all RelE hits to RelBE.
     Fix: split gene clusters carrying RelE into RelBE (if RelB is
     co-annotated in same PFAMs string) or YoeB-YefM (if
     PhdYeFM_antitox is co-annotated); flag "RelE_only" if neither.
  2. This IS the pre-registered toxin+antitoxin co-localization
     sensitivity check (RESEARCH_PLAN §Sensitivity Checks item 4).

Runs locally against NB01's cached ta_hits_by_gene_cluster.tsv.
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
        """# NB04 — RelE co-annotation attribution + panel sensitivity

Addresses REVIEW.md medium items #1 (RelE→RelBE collapse) and #2 (deferred sensitivity checks).

**Strategy**: For each gene cluster whose PFAMs contains `RelE`, inspect its full comma-delimited PFAMs string and attribute the family based on the co-annotated antitoxin:

- `RelE` + `RelB`  → RelBE
- `RelE` + `PhdYeFM_antitox` → YoeB-YefM
- Both antitoxins present → assigned to RelBE (F-plasmid convention) but flagged
- Neither antitoxin present → new "RelE_solo" bin (orphan toxin, sensitivity #4 partial)

Then re-run the per-family per-Mb H3 test to see whether the LARGE effect (r = −0.41) attributed to RelBE holds up, or whether it partitions between the two families."""
    ),
    code_cell(
        """import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt

DATA = Path('../data')
FIG = Path('../figures')

hits = pd.read_csv(DATA / 'ta_hits_by_gene_cluster.tsv', sep='\\t')
print(f"Loaded {len(hits):,} gene-cluster × pfam_name hits")

# Reduce to gene-cluster-level records (unique gene_cluster_id) with the
# full PFAMs string so we can inspect co-annotations
gc_pfams = (
    hits.drop_duplicates(subset=['gene_cluster_id'])
    [['gene_cluster_id', 'gtdb_species_clade_id', 'is_core', 'is_singleton', 'PFAMs']]
    .copy()
)
print(f"Distinct gene clusters carrying any TA Pfam: {len(gc_pfams):,}")"""
    ),
    md_cell("## 1. RelE co-annotation audit"),
    code_cell(
        """def has_token(pfams_str: str, name: str) -> bool:
    if not isinstance(pfams_str, str):
        return False
    tokens = {t.strip() for t in pfams_str.split(',')}
    return name in tokens

gc_pfams['has_RelE'] = gc_pfams['PFAMs'].apply(lambda s: has_token(s, 'RelE'))
rele_hits = gc_pfams[gc_pfams['has_RelE']].copy()

rele_hits['has_RelB'] = rele_hits['PFAMs'].apply(lambda s: has_token(s, 'RelB'))
rele_hits['has_PhdYeFM'] = rele_hits['PFAMs'].apply(lambda s: has_token(s, 'PhdYeFM_antitox'))

def bin_rele(row):
    if row['has_RelB'] and row['has_PhdYeFM']:
        return 'RelBE_ambig'
    if row['has_RelB']:
        return 'RelBE'
    if row['has_PhdYeFM']:
        return 'YoeB-YefM'
    return 'RelE_solo'

rele_hits['rele_bin'] = rele_hits.apply(bin_rele, axis=1)
print(f"RelE-carrying gene clusters: {len(rele_hits):,}")
print(rele_hits['rele_bin'].value_counts())"""
    ),
    md_cell(
        """## 2. Rebuild per-species per-family matrix with corrected attribution

For each species: count gene clusters attributed to RelBE (was correct), YoeB-YefM (previously undercounted), RelE_solo (new orphan bin). All other families keep the original attribution from NB01."""
    ),
    code_cell(
        """# Load the existing family composition + per-species TA counts
family_comp = pd.read_csv(DATA / 'ta_family_composition_per_species.tsv', sep='\\t')
per_species = pd.read_csv(DATA / 'ta_per_species.tsv', sep='\\t')

# The old NB01 attribution:
#   - RelE hits → RelBE (via setdefault first-seen)
#   - YoeB-YefM row of the panel: toxin_pfam_name=RelE (skipped), antitoxin_pfam_name=PhdYeFM_antitox (used)
#   - So YoeB-YefM count in family_comp was based on PhdYeFM_antitox hits only
#
# Corrected: split RelE gene clusters into three bins based on co-annotation.
# Then:
#   - RelBE_new = (gene clusters with RelE + RelB) ∪ (gene clusters with RelB but no RelE)
#   - YoeB-YefM_new = (gene clusters with RelE + PhdYeFM_antitox) ∪ (gene clusters with PhdYeFM_antitox but no RelE)
#   - RelE_solo = gene clusters with RelE only, neither RelB nor PhdYeFM_antitox
# Note: gene clusters carrying both RelE+RelB+PhdYeFM (RelBE_ambig) contribute to both new families.

# Distinct-gene-cluster indicator columns (already at gc_pfams level)
gc_pfams['has_RelB'] = gc_pfams['PFAMs'].apply(lambda s: has_token(s, 'RelB'))
gc_pfams['has_PhdYeFM'] = gc_pfams['PFAMs'].apply(lambda s: has_token(s, 'PhdYeFM_antitox'))

def relbe_indicator(row):
    return int(row['has_RelB'])
def yoebyefm_indicator(row):
    return int(row['has_PhdYeFM'])
def rele_solo_indicator(row):
    return int(row['has_RelE'] and not row['has_RelB'] and not row['has_PhdYeFM'])

gc_pfams['is_RelBE'] = gc_pfams.apply(relbe_indicator, axis=1)
gc_pfams['is_YoeB-YefM_new'] = gc_pfams.apply(yoebyefm_indicator, axis=1)
gc_pfams['is_RelE_solo'] = gc_pfams.apply(rele_solo_indicator, axis=1)

# Per-species aggregation
per_sp_new = (
    gc_pfams.groupby('gtdb_species_clade_id')
    [['is_RelBE', 'is_YoeB-YefM_new', 'is_RelE_solo']]
    .sum()
    .reset_index()
    .rename(columns={'is_RelBE': 'RelBE_new',
                     'is_YoeB-YefM_new': 'YoeB-YefM_new',
                     'is_RelE_solo': 'RelE_solo'})
)
print(f"Species with new-attribution counts: {len(per_sp_new):,}")
per_sp_new.head()"""
    ),
    md_cell("## 3. Rerun H3 with corrected attribution (H2-cohort scope)"),
    code_cell(
        """lifestyle = pd.read_csv('../../lifestyle_cog/data/species_lifestyle_classification.csv')

cohort = (
    per_species[['gtdb_species_clade_id', 'median_size_mb']]
    .merge(family_comp, on='gtdb_species_clade_id', how='left')
    .merge(per_sp_new, on='gtdb_species_clade_id', how='left')
    .merge(lifestyle[['gtdb_species_clade_id', 'species_lifestyle', 'phylum']],
           on='gtdb_species_clade_id', how='inner')
    .dropna(subset=['median_size_mb'])
)
for col in ['RelBE_new', 'YoeB-YefM_new', 'RelE_solo']:
    cohort[col] = cohort[col].fillna(0)

print(f"Cohort: {len(cohort):,}")
print(cohort['species_lifestyle'].value_counts())

host = cohort[cohort['species_lifestyle'] == 'host_associated']
free = cohort[cohort['species_lifestyle'] == 'free_living']

def mw_perm(a_vals, b_vals, label):
    u = stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
    r = 1.0 - (2.0 * u.statistic) / (len(a_vals) * len(b_vals))
    return {
        'group': label,
        'median_host_per_mb': float(a_vals.median()),
        'median_free_per_mb': float(b_vals.median()),
        'p_raw': float(u.pvalue),
        'r_rb': float(r),
    }

rows = []
for col in ['RelBE_new', 'YoeB-YefM_new', 'RelE_solo']:
    a = host[col] / host['median_size_mb']
    b = free[col] / free['median_size_mb']
    rows.append(mw_perm(a, b, col))

# Compare to the OLD attribution for RelBE and YoeB-YefM
for col in ['RelBE', 'YoeB-YefM']:
    a = host[col] / host['median_size_mb']
    b = free[col] / free['median_size_mb']
    rows.append(mw_perm(a, b, col + '_old'))

new_df = pd.DataFrame(rows)
new_df['p_bh'] = multipletests(new_df['p_raw'], method='fdr_bh')[1]
new_df = new_df.sort_values('group')
print(new_df.to_string(index=False))
new_df.to_csv(DATA / 'nb04_rele_reattribution.tsv', sep='\\t', index=False)"""
    ),
    md_cell(
        """## 4. Sensitivity: TA loci defined only by co-annotated T + AT

Pre-registered sensitivity check #4: restrict to gene clusters where both a toxin AND an antitoxin Pfam appear in the same PFAMs string. This excludes orphan toxins and antitoxins."""
    ),
    code_cell(
        """# For each gene cluster, do the PFAMs contain BOTH a toxin-side and an antitoxin-side name?
panel = pd.read_csv(DATA / 'ta_families_seed.tsv', sep='\\t')
toxin_names = set(panel['toxin_pfam_name'].dropna())
antitoxin_names = set(panel['antitoxin_pfam_name'].dropna())

def is_paired(pfams_str: str) -> bool:
    if not isinstance(pfams_str, str):
        return False
    tokens = {t.strip() for t in pfams_str.split(',')}
    return bool(tokens & toxin_names) and bool(tokens & antitoxin_names)

gc_pfams['ta_paired'] = gc_pfams['PFAMs'].apply(is_paired)
n_all = len(gc_pfams)
n_paired = gc_pfams['ta_paired'].sum()
print(f"Gene clusters with any TA-panel Pfam: {n_all:,}")
print(f"Gene clusters with BOTH toxin+antitoxin Pfams present: {n_paired:,}  ({100*n_paired/n_all:.1f}%)")"""
    ),
    code_cell(
        """# Aggregate paired-only counts per species
paired_per_sp = (
    gc_pfams[gc_pfams['ta_paired']]
    .groupby('gtdb_species_clade_id').size().rename('ta_paired').reset_index()
)
cohort2 = cohort.merge(paired_per_sp, on='gtdb_species_clade_id', how='left')
cohort2['ta_paired'] = cohort2['ta_paired'].fillna(0)
cohort2['ta_paired_per_mb'] = cohort2['ta_paired'] / cohort2['median_size_mb']

host2 = cohort2[cohort2['species_lifestyle'] == 'host_associated']
free2 = cohort2[cohort2['species_lifestyle'] == 'free_living']

# H2 sensitivity: paired-only TA per Mb host vs free
u = stats.mannwhitneyu(host2['ta_paired_per_mb'], free2['ta_paired_per_mb'], alternative='two-sided')
r = 1.0 - (2.0 * u.statistic) / (len(host2) * len(free2))
print(f"H2 SENSITIVITY (paired-only ta_per_mb):  U={u.statistic:.3g}  p={u.pvalue:.3g}  r_rb={r:+.3f}")
print(f"  median host: {host2['ta_paired_per_mb'].median():.3f}")
print(f"  median free: {free2['ta_paired_per_mb'].median():.3f}")

# H1 sensitivity: are paired TA gene clusters still non-core-enriched?
paired_gc = gc_pfams[gc_pfams['ta_paired']].copy()
paired_gc['bucket'] = np.where(paired_gc['is_core'], 'core',
                       np.where(paired_gc['is_singleton'], 'singleton', 'accessory'))
paired_pool = paired_gc['bucket'].value_counts().reindex(['core', 'accessory', 'singleton'], fill_value=0)
# Baseline = all TA panel hits (any name)
all_gc = gc_pfams.copy()
all_gc['bucket'] = np.where(all_gc['is_core'], 'core',
                    np.where(all_gc['is_singleton'], 'singleton', 'accessory'))
all_pool = all_gc['bucket'].value_counts().reindex(['core', 'accessory', 'singleton'], fill_value=0)
print("\\nPaired-only gene-cluster status distribution:")
print(paired_pool)
print("\\nAll TA panel gene-cluster status distribution (unchanged NB02 numerator):")
print(all_pool)

with open(DATA / 'nb04_summary.json', 'w') as f:
    json.dump({
        'n_ta_carrying_gc': int(n_all),
        'n_paired_gc': int(n_paired),
        'paired_pct': float(100*n_paired/n_all),
        'H2_sens_paired_median_host': float(host2['ta_paired_per_mb'].median()),
        'H2_sens_paired_median_free': float(free2['ta_paired_per_mb'].median()),
        'H2_sens_paired_p': float(u.pvalue),
        'H2_sens_paired_r': float(r),
    }, f, indent=2)"""
    ),
    md_cell(
        """## 5. Panel-scope sensitivity note

The pre-registered check #5 ("strict TADB-only vs expanded-panel comparison") is not implemented in this notebook because our executed panel is already the strict TADB-supported set. Two seed names (`HicA`, `HigA`) hit zero in the eggNOG-mapper index and were dropped; the remaining 15 names cover 10 well-established Type II families. Expanding the panel to newer Type II families (e.g., BREX-associated) would require a separate literature review and is deferred to future work."""
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
    out = Path(__file__).parent.parent / "notebooks" / "NB04_rele_reattribution.ipynb"
    out.write_text(json.dumps(NB, indent=1))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
