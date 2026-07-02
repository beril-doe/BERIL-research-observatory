"""Author NB03: H3 family-composition asymmetry + phylum-stratified controls.

Runs locally against NB01's cached TSVs and lifestyle_cog labels.
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
        """# NB03 — H3 family composition + phylum-stratified H1/H2

Runs locally against NB01 cached TSVs.

- **H3**: TA family composition (Shannon entropy of family fractions) differs by lifestyle.
- **Phylum control**: rerun H1 (paired non-core Wilcoxon) and H2 (Mann-Whitney per Mb) within each of the 10 lifestyle_cog phyla. Require ≥6/10 phyla to preserve direction of whole-cohort effect.
- **Family-level H3 test**: per-family per-Mb rate host vs free, BH-FDR corrected.
"""
    ),
    code_cell(
        """import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
import seaborn as sns

DATA = Path('../data')
FIG = Path('../figures')
FIG.mkdir(exist_ok=True)

sns.set_style('whitegrid')
plt.rcParams['figure.dpi'] = 110"""
    ),
    md_cell("## 1. Load NB01 outputs and lifestyle labels"),
    code_cell(
        """ta_species = pd.read_csv(DATA / 'ta_per_species.tsv', sep='\\t')
family_comp = pd.read_csv(DATA / 'ta_family_composition_per_species.tsv', sep='\\t')
baseline = pd.read_csv(DATA / 'species_gene_cluster_baseline.tsv', sep='\\t')
lifestyle = pd.read_csv('../../lifestyle_cog/data/species_lifestyle_classification.csv')

# Cohort with all pieces (TA + baseline + lifestyle + genome_size)
merged = (
    ta_species
    .merge(family_comp, on='gtdb_species_clade_id', how='left')
    .merge(baseline, on='gtdb_species_clade_id', how='left')
    .merge(lifestyle[['gtdb_species_clade_id', 'species_lifestyle', 'phylum']],
           on='gtdb_species_clade_id', how='inner')
    .dropna(subset=['median_size_mb'])
)
print(f"Cohort: {len(merged):,}")
print(merged['species_lifestyle'].value_counts())
print()
print(merged['phylum'].value_counts())"""
    ),
    md_cell(
        """## 2. H3 — Family composition asymmetry

We look at:
1. **Shannon entropy** of family-fraction distribution per species (higher → more diverse repertoire).
2. **Per-family per-Mb rate** (host vs free) with BH-FDR across families."""
    ),
    code_cell(
        """FAMILIES = [c for c in family_comp.columns if c != 'gtdb_species_clade_id']
print(f"Families in matrix: {FAMILIES}")

# Shannon entropy of family composition per species
def shannon(row):
    v = row.values.astype(float)
    v = v[v > 0]
    if v.size == 0:
        return np.nan
    p = v / v.sum()
    return float(-(p * np.log(p)).sum())

merged['family_entropy'] = merged[FAMILIES].apply(shannon, axis=1)
print(f"Species with defined entropy: {merged['family_entropy'].notna().sum()}")"""
    ),
    code_cell(
        """host = merged[merged['species_lifestyle'] == 'host_associated']
free = merged[merged['species_lifestyle'] == 'free_living']

# H3a: family_entropy — Mann-Whitney U
def mw(a, b, label):
    a = a.dropna()
    b = b.dropna()
    u = stats.mannwhitneyu(a, b, alternative='two-sided')
    r = 1.0 - (2.0 * u.statistic) / (len(a) * len(b))
    print(f"{label:>34s}  n_host={len(a)}  n_free={len(b)}  U={u.statistic:.3g}  p={u.pvalue:.3g}  r_rb={r:+.3f}  med_host={a.median():.3g}  med_free={b.median():.3g}")
    return u.pvalue, r

_ = mw(host['family_entropy'], free['family_entropy'], 'family_entropy (host vs free)')"""
    ),
    code_cell(
        """# H3b: per-family per-Mb rate, BH-FDR
family_stats = []
for fam in FAMILIES:
    a = (host[fam] / host['median_size_mb']).dropna()
    b = (free[fam] / free['median_size_mb']).dropna()
    if len(a) == 0 or len(b) == 0:
        continue
    u = stats.mannwhitneyu(a, b, alternative='two-sided')
    r = 1.0 - (2.0 * u.statistic) / (len(a) * len(b))
    family_stats.append({
        'family': fam,
        'n_host': int(len(a)), 'n_free': int(len(b)),
        'median_host_per_mb': float(a.median()),
        'median_free_per_mb': float(b.median()),
        'p_raw': float(u.pvalue),
        'r_rb': float(r),
    })

fs_df = pd.DataFrame(family_stats)
fs_df['p_bh'] = multipletests(fs_df['p_raw'], method='fdr_bh')[1]
fs_df['sig_bh_005'] = fs_df['p_bh'] < 0.05
fs_df = fs_df.sort_values('r_rb')
print(fs_df.to_string(index=False))
fs_df.to_csv(DATA / 'nb03_family_stats.tsv', sep='\\t', index=False)"""
    ),
    md_cell(
        """## 3. Phylum-stratified H1 and H2

Rerun H1 (paired non-core Wilcoxon vs baseline) and H2 (Mann-Whitney per Mb host vs free) within each phylum. Require ≥6/10 preserve direction."""
    ),
    code_cell(
        """# Prep non-core fractions and per-Mb rates for the phylum loop
merged['ta_frac_nonCore'] = ((merged['ta_accessory'] + merged['ta_singleton'])
                             / merged['ta_total'].replace(0, np.nan))
merged['baseline_frac_nonCore'] = ((merged['all_accessory'] + merged['all_singleton'])
                                   / merged['all_gene_clusters'])
merged['ta_per_mb'] = merged['ta_total'] / merged['median_size_mb']

phyla = merged['phylum'].value_counts()
phyla = phyla[phyla >= 20].index.tolist()  # need ≥ 20 species per phylum
print(f"Testable phyla: {phyla}")"""
    ),
    code_cell(
        """rows = []
for ph in phyla:
    sub = merged[merged['phylum'] == ph]
    # H1 paired Wilcoxon
    ss = sub.dropna(subset=['ta_frac_nonCore', 'baseline_frac_nonCore'])
    try:
        w = stats.wilcoxon(ss['ta_frac_nonCore'], ss['baseline_frac_nonCore'],
                           alternative='greater')
        delta_med = (ss['ta_frac_nonCore'] - ss['baseline_frac_nonCore']).median()
        h1_p = float(w.pvalue)
        h1_dir = '+' if delta_med > 0 else '-'
    except ValueError:
        h1_p = np.nan
        h1_dir = '?'
        delta_med = np.nan

    # H2 Mann-Whitney by lifestyle
    h_sub = sub[sub['species_lifestyle'] == 'host_associated']['ta_per_mb'].dropna()
    f_sub = sub[sub['species_lifestyle'] == 'free_living']['ta_per_mb'].dropna()
    if len(h_sub) >= 5 and len(f_sub) >= 5:
        u2 = stats.mannwhitneyu(h_sub, f_sub, alternative='two-sided')
        r_h2 = 1.0 - (2.0 * u2.statistic) / (len(h_sub) * len(f_sub))
        h2_dir = '+' if h_sub.median() > f_sub.median() else '-'
        h2_p = float(u2.pvalue)
    else:
        r_h2 = np.nan
        h2_dir = 'n<5'
        h2_p = np.nan

    rows.append({
        'phylum': ph,
        'n_species': len(sub),
        'n_host': int((sub['species_lifestyle'] == 'host_associated').sum()),
        'n_free': int((sub['species_lifestyle'] == 'free_living').sum()),
        'H1_delta_med': float(delta_med),
        'H1_p_greater': h1_p,
        'H1_direction': h1_dir,
        'H2_r_rb': float(r_h2) if not pd.isna(r_h2) else np.nan,
        'H2_p': h2_p,
        'H2_direction': h2_dir,
        'H2_med_host': float(h_sub.median()) if len(h_sub) else np.nan,
        'H2_med_free': float(f_sub.median()) if len(f_sub) else np.nan,
    })

phylum_df = pd.DataFrame(rows)
phylum_df.to_csv(DATA / 'nb03_phylum_stratified.tsv', sep='\\t', index=False)
print(phylum_df.to_string(index=False))"""
    ),
    code_cell(
        """# Consistency counters
h1_pos = (phylum_df['H1_direction'] == '+').sum()
h2_host_higher = (phylum_df['H2_direction'] == '+').sum()
n_testable_h2 = (phylum_df['H2_direction'].isin(['+', '-'])).sum()

print(f"H1 (accessory-enriched) preserved direction in {h1_pos}/{len(phylum_df)} phyla")
print(f"H2 (host higher TA/Mb) preserved direction in {h2_host_higher}/{n_testable_h2} testable phyla")"""
    ),
    md_cell("## 4. Visualizations"),
    code_cell(
        """fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: family composition, stacked bars of median per-Mb rate by lifestyle
ax = axes[0]
med_host_per_mb = [host[fam].sum() / host['median_size_mb'].sum() for fam in FAMILIES]
med_free_per_mb = [free[fam].sum() / free['median_size_mb'].sum() for fam in FAMILIES]
x = np.arange(len(FAMILIES))
w = 0.4
ax.bar(x - w/2, med_free_per_mb, w, label='free-living', alpha=0.85, color='steelblue')
ax.bar(x + w/2, med_host_per_mb, w, label='host-associated', alpha=0.85, color='darkorange')
ax.set_xticks(x)
ax.set_xticklabels(FAMILIES, rotation=35, ha='right')
ax.set_ylabel('TA loci per Mb (cohort sum / cohort Mb)')
ax.set_title('H3: Family composition by lifestyle')
ax.legend()

# Panel B: H2 direction by phylum
ax = axes[1]
sig_df = phylum_df.dropna(subset=['H2_r_rb']).sort_values('H2_r_rb')
colors = ['darkorange' if r > 0 else 'steelblue' for r in sig_df['H2_r_rb']]
ax.barh(sig_df['phylum'], sig_df['H2_r_rb'], color=colors, edgecolor='k', linewidth=0.5)
ax.axvline(0, color='k', linewidth=0.8)
ax.set_xlabel('rank-biserial r  (host − free)')
ax.set_title('H2 per phylum:  +r = host higher TA/Mb')

fig.tight_layout()
fig.savefig(FIG / 'nb03_family_and_phylum.png', dpi=150, bbox_inches='tight')
plt.show()"""
    ),
    md_cell("## 5. Persist NB03 summary"),
    code_cell(
        """summary = {
    'n_species_cohort': int(len(merged)),
    'families_tested': FAMILIES,
    'H3_family_entropy_host_median': float(host['family_entropy'].median()),
    'H3_family_entropy_free_median': float(free['family_entropy'].median()),
    'H3b_families_bh_significant': int(fs_df['sig_bh_005'].sum()),
    'H1_phylum_preserved_of_10': int((phylum_df['H1_direction'] == '+').sum()),
    'H2_phylum_host_higher_of_testable': int((phylum_df['H2_direction'] == '+').sum()),
    'H2_phylum_testable': int((phylum_df['H2_direction'].isin(['+','-'])).sum()),
}
(DATA / 'nb03_summary.json').write_text(json.dumps(summary, indent=2))
summary"""
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
    out = Path(__file__).parent.parent / "notebooks" / "NB03_family_composition.ipynb"
    out.write_text(json.dumps(NB, indent=1))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
