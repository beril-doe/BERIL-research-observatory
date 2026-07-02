"""Author NB02: Lifestyle partition + H1/H2 hypothesis tests.

Runs locally against NB01's cached TSVs. No Spark required.
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
        """# NB02 — Lifestyle Partition and H1/H2 Tests

Runs locally from NB01's cached TSVs. No BERDL access required.

- **H1**: TA loci are predominantly accessory (rank-biserial |r| ≥ 0.2 vs genome-wide baseline).
- **H2**: Host-associated species carry fewer TA loci per Mb than free-living (Mann-Whitney U + rank-biserial |r| ≥ 0.15).
- Sensitivity: partial correlation controlling for genome size (per Mb already normalizes, but we report the raw-count check as well)."""
    ),
    code_cell(
        """import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
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
baseline = pd.read_csv(DATA / 'species_gene_cluster_baseline.tsv', sep='\\t')
panel_coverage = pd.read_csv(DATA / 'ta_panel_coverage.tsv', sep='\\t')

print(f"ta_species: {len(ta_species):,} species with TA hits")
print(f"baseline: {len(baseline):,} species with baseline gene-cluster counts")
print(f"panel_coverage: {len(panel_coverage)} Pfams; zero-hit = {(panel_coverage['n_annotations'] == 0).sum()}")"""
    ),
    code_cell(
        """lifestyle = pd.read_csv('../../lifestyle_cog/data/species_lifestyle_classification.csv')
print(f"lifestyle labels: {len(lifestyle):,} species")
print(lifestyle['species_lifestyle'].value_counts())"""
    ),
    code_cell(
        """# Merge on gtdb_species_clade_id — inner join keeps only species with lifestyle labels
merged = (
    ta_species
    .merge(baseline, on='gtdb_species_clade_id', how='left')
    .merge(lifestyle[['gtdb_species_clade_id', 'species_lifestyle', 'phylum']],
           on='gtdb_species_clade_id', how='inner')
)
print(f"Cohort (species with both TA hits AND lifestyle label): {len(merged):,}")
print(merged['species_lifestyle'].value_counts())"""
    ),
    code_cell(
        """# Species with lifestyle label but zero TA hits — important for H2 (they're TA-poor)
lifestyle_no_ta = lifestyle.merge(
    ta_species[['gtdb_species_clade_id']],
    on='gtdb_species_clade_id', how='left', indicator=True)
lifestyle_no_ta = lifestyle_no_ta[lifestyle_no_ta['_merge'] == 'left_only']
print(f"Species with lifestyle label but zero TA hits: {len(lifestyle_no_ta)}")
print(lifestyle_no_ta['species_lifestyle'].value_counts())"""
    ),
    md_cell(
        """## 2. H1 — Are TA loci predominantly accessory?

We compare the (core, accessory, singleton) distribution of TA-carrying gene clusters to the genome-wide baseline. Two variants:

- **Species-averaged**: for each species, compute TA accessory-fraction and baseline accessory-fraction; test the paired difference with a Wilcoxon signed-rank test.
- **Pooled**: sum TA counts and baseline counts across all species; chi-square goodness-of-fit."""
    ),
    code_cell(
        """# Add species with zero TA hits (they contribute nothing to TA sums but their
# baseline still counts if we're pooling)
for col in ['ta_core', 'ta_accessory', 'ta_singleton', 'ta_total']:
    merged[col] = merged[col].fillna(0)

# Species-averaged: per-species TA accessory + singleton fraction vs baseline
merged['ta_frac_nonCore'] = (merged['ta_accessory'] + merged['ta_singleton']) / merged['ta_total'].replace(0, np.nan)
merged['baseline_frac_nonCore'] = (merged['all_accessory'] + merged['all_singleton']) / merged['all_gene_clusters']

per_species_frac = merged.dropna(subset=['ta_frac_nonCore', 'baseline_frac_nonCore']).copy()
print(f"Species with defined fractions (ta_total > 0): {len(per_species_frac)}")

# Wilcoxon signed-rank (paired) — one-sided, alt: TA more accessory
try:
    w = stats.wilcoxon(per_species_frac['ta_frac_nonCore'],
                       per_species_frac['baseline_frac_nonCore'],
                       alternative='greater')
    delta = (per_species_frac['ta_frac_nonCore'] - per_species_frac['baseline_frac_nonCore']).median()
    # Rank-biserial for paired signed rank
    d = per_species_frac['ta_frac_nonCore'] - per_species_frac['baseline_frac_nonCore']
    ranks = stats.rankdata(np.abs(d))
    pos = ranks[d > 0].sum()
    neg = ranks[d < 0].sum()
    r_rb = (pos - neg) / ranks.sum()
    print(f"H1 (paired) Wilcoxon:  W={w.statistic:.3g}  p_one_sided={w.pvalue:.3g}")
    print(f"       median Δfraction (TA − baseline) = {delta:+.3f}")
    print(f"       rank-biserial r = {r_rb:+.3f}  (target |r| ≥ 0.2)")
except Exception as e:
    print(f"Wilcoxon failed: {e}")"""
    ),
    code_cell(
        """# Pooled: chi-square goodness-of-fit
ta_pool = merged[['ta_core', 'ta_accessory', 'ta_singleton']].sum().values
base_pool = merged[['all_core', 'all_accessory', 'all_singleton']].sum().values
expected = ta_pool.sum() * (base_pool / base_pool.sum())
chi2, p = stats.chisquare(f_obs=ta_pool, f_exp=expected)
print(f"H1 (pooled) chi-square: chi2={chi2:.3g}  p={p:.3g}")
print("               observed (TA)          expected (baseline)")
for name, o, e in zip(['core', 'accessory', 'singleton'], ta_pool, expected):
    print(f"    {name:>10s}  {o:>10.0f}          {e:>10.0f}")"""
    ),
    md_cell("## 3. H2 — Host-associated species carry fewer TA loci per Mb"),
    code_cell(
        """# Include species with zero TA hits (they belong in the count-per-Mb distribution)
lifestyle_full = lifestyle.merge(
    ta_species[['gtdb_species_clade_id', 'ta_total', 'ta_core', 'ta_accessory', 'ta_singleton', 'median_size_mb']],
    on='gtdb_species_clade_id', how='left')
for col in ['ta_total', 'ta_core', 'ta_accessory', 'ta_singleton']:
    lifestyle_full[col] = lifestyle_full[col].fillna(0)

# For median_size_mb, fill in from a second query — but a reasonable fallback
# is the species' own no_gene_clusters × avg gene length. For now, drop species
# without a size estimate.
n_before = len(lifestyle_full)
lifestyle_full = lifestyle_full.dropna(subset=['median_size_mb'])
print(f"Species dropped for missing genome-size: {n_before - len(lifestyle_full)}")

lifestyle_full['ta_per_mb'] = lifestyle_full['ta_total'] / lifestyle_full['median_size_mb']
lifestyle_full['ta_accessory_per_mb'] = (lifestyle_full['ta_accessory'] + lifestyle_full['ta_singleton']) / lifestyle_full['median_size_mb']

host = lifestyle_full[lifestyle_full['species_lifestyle'] == 'host_associated']
free = lifestyle_full[lifestyle_full['species_lifestyle'] == 'free_living']
print(f"host_associated: n={len(host)}, median ta_per_mb = {host['ta_per_mb'].median():.3f}")
print(f"free_living:     n={len(free)}, median ta_per_mb = {free['ta_per_mb'].median():.3f}")"""
    ),
    code_cell(
        """def mw_test(a, b, label):
    u = stats.mannwhitneyu(a, b, alternative='two-sided')
    # rank-biserial r
    n1, n2 = len(a), len(b)
    r_rb = 1.0 - (2.0 * u.statistic) / (n1 * n2)
    # Direction as printed: positive r means group `a` values are LARGER
    print(f"{label:>28s}  n_host={n1}  n_free={n2}  U={u.statistic:.3g}  p={u.pvalue:.3g}  r_rb={r_rb:+.3f}")
    return u.pvalue, r_rb

mw_test(host['ta_per_mb'], free['ta_per_mb'], 'ta_per_mb (host vs free)')
mw_test(host['ta_accessory_per_mb'], free['ta_accessory_per_mb'], 'accessory_ta_per_mb')
mw_test(host['ta_total'], free['ta_total'], 'ta_total (raw counts)')"""
    ),
    code_cell(
        """# Sensitivity: genome-size confounder
sp_gs = stats.spearmanr(lifestyle_full['median_size_mb'], lifestyle_full['ta_total'])
print(f"Spearman(genome_size, ta_total): rho={sp_gs.statistic:+.3f}  p={sp_gs.pvalue:.3g}")
sp_gs_mb = stats.spearmanr(lifestyle_full['median_size_mb'], lifestyle_full['ta_per_mb'])
print(f"Spearman(genome_size, ta_per_mb): rho={sp_gs_mb.statistic:+.3f}  p={sp_gs_mb.pvalue:.3g}")

# Report medians by lifestyle for both metrics
print("\\nMedian genome size (Mb):")
print(lifestyle_full.groupby('species_lifestyle')['median_size_mb'].median())"""
    ),
    md_cell("## 4. Visualizations"),
    code_cell(
        """fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# Left: H1 — ta accessory-fraction vs baseline, per-species
ax = axes[0]
ax.scatter(per_species_frac['baseline_frac_nonCore'],
           per_species_frac['ta_frac_nonCore'],
           s=8, alpha=0.4)
ax.plot([0, 1], [0, 1], 'k--', lw=0.8, label='y = x')
ax.set_xlabel('Baseline non-core fraction (genome-wide)')
ax.set_ylabel('TA-locus non-core fraction')
ax.set_title('H1: TA loci accessory-enrichment per species')
ax.legend()

# Right: H2 — ta_per_mb distributions by lifestyle
ax = axes[1]
sns.violinplot(data=lifestyle_full, x='species_lifestyle', y='ta_per_mb',
               order=['free_living', 'host_associated'], inner='quartile', ax=ax, cut=0)
ax.set_xlabel('')
ax.set_ylabel('TA loci per Mb')
ax.set_title('H2: TA carriage by lifestyle')

fig.tight_layout()
fig.savefig(FIG / 'nb02_h1_h2_overview.png', dpi=150, bbox_inches='tight')
plt.show()"""
    ),
    md_cell("## 5. Persist summary statistics"),
    code_cell(
        """summary = {
    'n_species_cohort': int(len(merged)),
    'n_host': int((lifestyle_full['species_lifestyle'] == 'host_associated').sum()),
    'n_free': int((lifestyle_full['species_lifestyle'] == 'free_living').sum()),
    'H1_pooled_chi2': float(chi2),
    'H1_pooled_p': float(p),
    'H1_wilcoxon_p': float(w.pvalue) if 'w' in dir() else None,
    'H1_rank_biserial': float(r_rb) if 'r_rb' in dir() else None,
    'H2_ta_per_mb_median_host': float(host['ta_per_mb'].median()),
    'H2_ta_per_mb_median_free': float(free['ta_per_mb'].median()),
}
import json as _json
(Path(DATA) / 'nb02_summary.json').write_text(_json.dumps(summary, indent=2))
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
    out = Path(__file__).parent.parent / "notebooks" / "NB02_lifestyle_partition.ipynb"
    out.write_text(json.dumps(NB, indent=1))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
