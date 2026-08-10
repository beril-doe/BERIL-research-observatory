"""
NB04: Statistical Analysis and Figures

Reproduces all four results CSVs and generates figures from the integrated CSV.
No Spark needed — reads from species_integrated.csv (produced by NB03).

Outputs:
  data/multiscale_correlation_results.csv
  data/within_genus_correlations.csv
  data/mediation_results.csv
  data/environment_stratified_results.csv
  figures/openness_vs_pathway_scatter.png
  figures/lifestyle_stratified_scatter.png
  figures/multiscale_correlations.png
  figures/within_genus_rho_distribution.png
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
FIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

# --- Load data ---
df_all = pd.read_csv(os.path.join(DATA_DIR, 'species_integrated.csv'))
df10 = pd.read_csv(os.path.join(DATA_DIR, 'species_integrated_10plus.csv'))
print(f"Loaded: {len(df_all)} species (full), {len(df10)} species (10+ genomes)")

# Use 10+ genomes subset for all statistical analyses
# (matches the original Aug 6 session methodology)
df = df10.copy()

# ============================================================
# 1. Multi-scale taxonomic correlations (H0 test)
# ============================================================
print("\n=== Multi-scale correlations ===")

valid = df.dropna(subset=['openness', 'mean_complete_pathways'])

# Species level
sp_rho, sp_p = spearmanr(valid['openness'], valid['mean_complete_pathways'])
print(f"Species: rho={sp_rho:.4f}, n={len(valid)}")

# Genus level
genus_agg = valid.groupby('genus').agg(
    openness=('openness', 'mean'),
    pathways=('mean_complete_pathways', 'mean'),
    n_species=('openness', 'count')
).reset_index()
genus_agg = genus_agg[genus_agg['n_species'] >= 2]
g_rho, g_p = spearmanr(genus_agg['openness'], genus_agg['pathways'])
print(f"Genus: rho={g_rho:.4f}, p={g_p:.2e}, n={len(genus_agg)}")

# Family level
fam_agg = valid.groupby('family').agg(
    openness=('openness', 'mean'),
    pathways=('mean_complete_pathways', 'mean'),
    n_species=('openness', 'count')
).reset_index()
fam_agg = fam_agg[fam_agg['n_species'] >= 2]
f_rho, f_p = spearmanr(fam_agg['openness'], fam_agg['pathways'])
print(f"Family: rho={f_rho:.4f}, p={f_p:.2e}, n={len(fam_agg)}")

# Phylum level
phy_agg = valid.groupby('phylum').agg(
    openness=('openness', 'mean'),
    pathways=('mean_complete_pathways', 'mean'),
    n_species=('openness', 'count')
).reset_index()
phy_agg = phy_agg[phy_agg['n_species'] >= 2]
p_rho, p_p = spearmanr(phy_agg['openness'], phy_agg['pathways'])
print(f"Phylum: rho={p_rho:.4f}, p={p_p:.2e}, n={len(phy_agg)}")

# Within-genus correlations (genera with >= 10 species)
within_genus = []
for genus, grp in valid.groupby('genus'):
    if len(grp) >= 10:
        r, p = spearmanr(grp['openness'], grp['mean_complete_pathways'])
        within_genus.append({
            'genus': genus,
            'n_species': len(grp),
            'rho': r,
            'p_value': p,
            'significant': p < 0.05
        })
wg_df = pd.DataFrame(within_genus).sort_values('genus')
wg_median_rho = wg_df['rho'].median()
wg_pct_positive = (wg_df['rho'] > 0).mean()
wg_pct_sig = wg_df['significant'].mean()
print(f"\nWithin-genus: median rho={wg_median_rho:.4f}, "
      f"{wg_pct_positive:.1%} positive, {wg_pct_sig:.1%} significant, "
      f"n_genera={len(wg_df)}")

# Save multi-scale results
multiscale = pd.DataFrame([{
    'species_level_rho': sp_rho,
    'genus_level_rho': g_rho,
    'genus_level_p': g_p,
    'n_genera': len(genus_agg),
    'family_level_rho': f_rho,
    'family_level_p': f_p,
    'n_families': len(fam_agg),
    'phylum_level_rho': p_rho,
    'phylum_level_p': p_p,
    'n_phyla': len(phy_agg),
    'within_genus_median_rho': wg_median_rho,
    'within_genus_pct_positive': wg_pct_positive,
    'within_genus_pct_significant': wg_pct_sig,
    'h0_rejected': g_p < 0.01
}])
multiscale.to_csv(os.path.join(DATA_DIR, 'multiscale_correlation_results.csv'), index=False)
wg_df.to_csv(os.path.join(DATA_DIR, 'within_genus_correlations.csv'), index=False)
print("Saved: multiscale_correlation_results.csv, within_genus_correlations.csv")

# ============================================================
# 2. Mediation analysis: niche breadth (H1/H2 test)
# ============================================================
print("\n=== Mediation analysis ===")

med_valid = valid.dropna(subset=['niche_breadth'])
med_genus = med_valid.groupby('genus').agg(
    openness=('openness', 'mean'),
    pathways=('mean_complete_pathways', 'mean'),
    niche_breadth=('niche_breadth', 'mean'),
    n_species=('openness', 'count')
).reset_index()
med_genus = med_genus[med_genus['n_species'] >= 2]

# Uncontrolled
unc_rho, unc_p = spearmanr(med_genus['openness'], med_genus['pathways'])

# Controlled: residualize both openness and pathways against niche_breadth
z_open = np.polyfit(med_genus['niche_breadth'], med_genus['openness'], 1)
z_path = np.polyfit(med_genus['niche_breadth'], med_genus['pathways'], 1)
res_open = med_genus['openness'] - np.polyval(z_open, med_genus['niche_breadth'])
res_path = med_genus['pathways'] - np.polyval(z_path, med_genus['niche_breadth'])
ctrl_rho, _ = spearmanr(res_open, res_path)
reduction = (1 - abs(ctrl_rho) / abs(unc_rho)) * 100

# Openness-niche and niche-pathways
on_rho, on_p = spearmanr(med_genus['openness'], med_genus['niche_breadth'])
np_rho, np_p = spearmanr(med_genus['niche_breadth'], med_genus['pathways'])

mediation = pd.DataFrame([{
    'genus_rho_uncontrolled': unc_rho,
    'genus_p_uncontrolled': unc_p,
    'genus_rho_controlled': ctrl_rho,
    'reduction_pct': reduction,
    'n_genera': len(med_genus),
    'n_species_subset': len(med_valid),
    'rho_openness_niche': on_rho,
    'p_openness_niche': on_p,
    'rho_niche_pathways': np_rho,
    'p_niche_pathways': np_p,
    'h1_supported': reduction > 30,
    'h2_supported': np_p < 0.01
}])
mediation.to_csv(os.path.join(DATA_DIR, 'mediation_results.csv'), index=False)
print(f"Uncontrolled rho={unc_rho:.4f}, controlled rho={ctrl_rho:.4f}, "
      f"reduction={reduction:.1f}%")
print(f"Openness-niche: rho={on_rho:.4f}, p={on_p:.4f}")
print(f"Niche-pathways: rho={np_rho:.4f}, p={np_p:.2e}")
print("Saved: mediation_results.csv")

# ============================================================
# 3. Environment stratification (H3 test)
# ============================================================
print("\n=== Environment stratification ===")

env_valid = valid.dropna(subset=['environment_type'])
env_valid = env_valid[env_valid['environment_type'].isin(['host_associated', 'free_living'])]

env_genus = env_valid.groupby(['genus', 'environment_type']).agg(
    openness=('openness', 'mean'),
    pathways=('mean_complete_pathways', 'mean'),
    n_species=('openness', 'count')
).reset_index()

# Classify genera by their dominant environment type
genus_env_type = env_valid.groupby('genus')['environment_type'].agg(
    lambda x: x.value_counts().index[0]
).reset_index()
genus_env_type.columns = ['genus', 'dominant_env']

genus_means = env_valid.groupby('genus').agg(
    openness=('openness', 'mean'),
    pathways=('mean_complete_pathways', 'mean'),
    n_species=('openness', 'count')
).reset_index()
genus_means = genus_means[genus_means['n_species'] >= 2]
genus_means = genus_means.merge(genus_env_type, on='genus')

host_genera = genus_means[genus_means['dominant_env'] == 'host_associated']
free_genera = genus_means[genus_means['dominant_env'] == 'free_living']

if len(host_genera) >= 3 and len(free_genera) >= 3:
    h_rho, _ = spearmanr(host_genera['openness'], host_genera['pathways'])
    f_rho, _ = spearmanr(free_genera['openness'], free_genera['pathways'])

    # Fisher z-test
    z1 = np.arctanh(h_rho)
    z2 = np.arctanh(f_rho)
    se = np.sqrt(1/(len(host_genera)-3) + 1/(len(free_genera)-3))
    fisher_z = (z1 - z2) / se
    fisher_p = 2 * (1 - __import__('scipy').stats.norm.cdf(abs(fisher_z)))

    env_results = pd.DataFrame([{
        'host_genus_rho': h_rho,
        'host_genus_n': len(host_genera),
        'free_genus_rho': f_rho,
        'free_genus_n': len(free_genera),
        'fisher_z': fisher_z,
        'fisher_p': fisher_p,
        'h3_supported': fisher_p < 0.01
    }])
    env_results.to_csv(os.path.join(DATA_DIR, 'environment_stratified_results.csv'), index=False)
    print(f"Host: rho={h_rho:.4f}, n={len(host_genera)}")
    print(f"Free: rho={f_rho:.4f}, n={len(free_genera)}")
    print(f"Fisher z={fisher_z:.3f}, p={fisher_p:.4f}")
    print("Saved: environment_stratified_results.csv")
else:
    print("Insufficient genera for environment stratification")

# ============================================================
# 4. Figures
# ============================================================
print("\n=== Generating figures ===")
sns.set_style('whitegrid')
sns.set_context('paper', font_scale=1.2)

# Figure 1: Openness vs pathway completeness scatter
fig, ax = plt.subplots(figsize=(8, 6))
scatter_data = df10.dropna(subset=['openness', 'mean_complete_pathways', 'environment_type'])
colors = {'free_living': '#2196F3', 'host_associated': '#FF5722'}
for env_type, color in colors.items():
    mask = scatter_data['environment_type'] == env_type
    label = env_type.replace('_', '-')
    ax.scatter(scatter_data.loc[mask, 'openness'],
               scatter_data.loc[mask, 'mean_complete_pathways'],
               c=color, alpha=0.3, s=15, label=label, edgecolors='none')

# Also plot species without environment data
no_env = df[df['environment_type'].isna()].dropna(subset=['openness', 'mean_complete_pathways'])
ax.scatter(no_env['openness'], no_env['mean_complete_pathways'],
           c='#999999', alpha=0.15, s=10, label='unclassified', edgecolors='none')

ax.set_xlabel('Pangenome Openness')
ax.set_ylabel('Mean Complete Pathways')
ax.set_title(f'Pangenome Openness vs. Pathway Completeness\n'
             f'(GTDB r214, species with $\\geq$10 genomes, '
             f'Spearman $\\rho$ = {sp_rho:.3f})')
ax.legend(title='Lifestyle', loc='lower left')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'openness_vs_pathway_scatter.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/openness_vs_pathway_scatter.png")

# Figure 2: Lifestyle-stratified scatter (genus level)
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

for ax, (label, data, rho_val, n_val, color) in zip(axes, [
    ('Free-living genera', free_genera, f_rho, len(free_genera), '#2196F3'),
    ('Host-associated genera', host_genera, h_rho, len(host_genera), '#FF5722')
]):
    ax.scatter(data['openness'], data['pathways'], c=color, alpha=0.5, s=30, edgecolors='none')
    z = np.polyfit(data['openness'], data['pathways'], 1)
    x_line = np.linspace(data['openness'].min(), data['openness'].max(), 100)
    ax.plot(x_line, np.polyval(z, x_line), '--', color='black', alpha=0.7, linewidth=1.5)
    ax.set_xlabel('Mean Genus Openness')
    ax.set_title(f'{label}\n$\\rho$ = {rho_val:.3f}, n = {n_val}')
    ax.grid(alpha=0.3)

axes[0].set_ylabel('Mean Genus Pathway Completeness')
fig.suptitle(f'Lifestyle Reversal: Fisher z = {fisher_z:.2f}, p = {fisher_p:.4f}',
             fontsize=12, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'lifestyle_stratified_scatter.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/lifestyle_stratified_scatter.png")

# Figure 3: Multi-scale correlation bar chart
fig, ax = plt.subplots(figsize=(7, 5))
levels = ['Species', 'Genus', 'Family', 'Phylum']
rhos = [sp_rho, g_rho, f_rho, p_rho]
ps = [None, g_p, f_p, p_p]
bar_colors = ['#4CAF50' if (p is not None and p < 0.05) else '#BDBDBD'
              for p in ps]
bar_colors[0] = '#4CAF50'  # species level always significant at n=27k

bars = ax.bar(levels, rhos, color=bar_colors, edgecolor='black', linewidth=0.5)
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_ylabel('Spearman $\\rho$')
ax.set_title('Openness-Pathway Correlation\nAcross Taxonomic Scales')

for i, (bar, rho, p) in enumerate(zip(bars, rhos, ps)):
    label = f'{rho:.3f}'
    if p is not None:
        label += f'\np={p:.1e}' if p < 0.001 else f'\np={p:.3f}'
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.02,
            label, ha='center', va='top', fontsize=9, color='white', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'multiscale_correlations.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/multiscale_correlations.png")

# Figure 4: Within-genus rho distribution
fig, ax = plt.subplots(figsize=(7, 5))
sig_mask = wg_df['significant']
ax.hist(wg_df.loc[~sig_mask, 'rho'], bins=15, alpha=0.7, color='#BDBDBD',
        edgecolor='black', linewidth=0.5, label='Not significant')
ax.hist(wg_df.loc[sig_mask, 'rho'], bins=5, alpha=0.9, color='#F44336',
        edgecolor='black', linewidth=0.5, label='p < 0.05')
ax.axvline(x=0, color='black', linewidth=1, linestyle='-')
ax.axvline(x=wg_median_rho, color='blue', linewidth=1.5, linestyle='--',
           label=f'Median $\\rho$ = {wg_median_rho:.3f}')

for _, row in wg_df[sig_mask].iterrows():
    genus_short = row['genus'].replace('g__', '')
    ax.annotate(genus_short, xy=(row['rho'], 0.5), fontsize=7,
                ha='center', rotation=45)

ax.set_xlabel('Spearman $\\rho$ (openness vs. pathways)')
ax.set_ylabel('Number of Genera')
ax.set_title(f'Within-Genus Correlations (n = {len(wg_df)} genera with $\\geq$10 species)\n'
             f'Note: ~2/40 expected significant by chance at $\\alpha$ = 0.05')
ax.legend(loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'within_genus_rho_distribution.png'), dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/within_genus_rho_distribution.png")

print("\n=== Done ===")
print(f"Results CSVs: {os.listdir(DATA_DIR)}")
print(f"Figures: {[f for f in os.listdir(FIG_DIR) if f.endswith('.png')]}")
