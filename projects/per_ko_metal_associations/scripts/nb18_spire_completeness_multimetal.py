#!/usr/bin/env python3
"""
NB18: NB16 + CheckM2 completeness/contamination + other-metal control.

Two extensions over NB16:
  A. Add CheckM2 completeness and contamination to Z — tests whether
     the As near-universal-gene depletion hits are MAG-incompleteness artifacts.
  B. Add log10 of the 5 other metals (median-imputed) to Z — tests
     whether each metal's associations are independent of co-occurring metals.

Output: nb18_spire_completeness_multimetal.csv
"""
import os
os.environ['OMP_NUM_THREADS'] = '1'
import numpy as np, pandas as pd, warnings, sys
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.stats import t as t_dist
from statsmodels.stats.multitest import multipletests

REPO  = Path('/home/hmacgregor/BERIL-research-observatory')
PROJ  = REPO / 'projects/per_ko_metal_associations'
MEP   = REPO / 'projects/microbeatlas_metal_ecology'
OUT   = PROJ / 'data'
METALS = ['As','Cd','Cr','Cu','Hg','Pb']

CONT_COVS = ['lat','lon','ph_soilgrids','usgs_mine_distance',
             'clay_pct','organic_matter',
             'lc_forest_pct','lc_cultivated_pct','lc_urban_pct']
CAT_COVS  = ['drainage_class','lith_class']
IMPUTE    = ['clay_pct','organic_matter']
MIN_PREV  = 20

def build_Z(sub, ph_dummies, completeness_col, other_metals):
    parts = [np.ones((len(sub),1))]
    for col in CONT_COVS:
        v = pd.to_numeric(sub[col], errors='coerce').fillna(0).values.reshape(-1,1)
        parts.append(v.astype(float))
    for col in CAT_COVS:
        if col in sub.columns:
            d = pd.get_dummies(sub[col], prefix=col, drop_first=True).astype(float)
            d = d.loc[:, d.std() > 1e-8]
            if len(d.columns): parts.append(d.values)
    if ph_dummies is not None and len(ph_dummies.columns):
        parts.append(ph_dummies.values)
    # CheckM2 completeness and contamination
    for col in completeness_col:
        if col in sub.columns:
            v = pd.to_numeric(sub[col], errors='coerce').fillna(sub[col].median()).values.reshape(-1,1)
            parts.append(v.astype(float))
    # Other metals (log10, median-imputed)
    for m in other_metals:
        if m in sub.columns:
            raw = pd.to_numeric(sub[m], errors='coerce')
            med = raw.median()
            lo = max(raw.quantile(0.01) if raw.notna().sum() > 0 else 1e-4, 1e-4)
            v = np.log10(np.maximum(raw.fillna(med).values, lo)).reshape(-1,1)
            parts.append(v.astype(float))
    Z = np.hstack(parts)
    std = Z.std(axis=0)
    Z = Z[:, std > 1e-8]
    return Z

def score_test(Y, x, Z):
    n, K = Y.shape
    try:
        ZtZ_inv = np.linalg.pinv(Z.T @ Z)
    except:
        return np.full(K, np.nan), np.full(K, np.nan), np.full(K, np.nan)
    H = Z @ ZtZ_inv @ Z.T
    x_res = x - H @ x
    x_ss  = x_res @ x_res
    if x_ss < 1e-12:
        return np.full(K, np.nan), np.full(K, np.nan), np.full(K, np.nan)
    Y_res  = Y - H @ Y
    beta   = (x_res @ Y_res) / x_ss
    df_r   = n - Z.shape[1] - 1
    if df_r < 2:
        return beta, np.full(K, np.nan), np.full(K, np.nan)
    rss = np.maximum((Y_res**2).sum(axis=0) - beta**2 * x_ss, 0)
    se  = np.sqrt(rss / df_r / x_ss)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        t_stat = beta / se
    p = 2 * t_dist.sf(np.abs(t_stat), df=df_r)
    return beta, t_stat, p

# ------------------------------------------------------------------
print('[1] Loading data...')
cov = pd.read_csv(MEP / 'data/usa_cwm/covariate_matrix_634.csv')
for col in IMPUTE:
    cov[col] = cov[col].fillna(cov[col].median())

geo = pd.read_csv(MEP / 'data/final_mags_geospatial_traits.csv')
usa = geo[(geo['lat']>=24)&(geo['lat']<=50)&(geo['lon']>=-125)&(geo['lon']<=-65)].copy()

# CheckM2 quality — mgnify_mag_quality.csv has MGYG IDs matching geo/KO matrix
qual = pd.read_csv(PROJ / 'data/mgnify_mag_quality.csv')[['genome_id','completeness','contamination']]
usa = usa.merge(qual, on='genome_id', how='left')
print(f'    MAGs with completeness: {usa["completeness"].notna().sum()} / {len(usa)}')

tree = cKDTree(cov[['lat','lon']].values)
dists, idxs = tree.query(usa[['lat','lon']].values, k=1)
usa['nn_dist'] = dists; usa['cov_idx'] = idxs
usa = usa[usa['nn_dist'] <= 1.0].copy().reset_index(drop=True)

cov_cols = CONT_COVS + CAT_COVS + METALS
joined = usa.join(
    cov[cov_cols].iloc[usa['cov_idx'].values].reset_index(drop=True),
    rsuffix='_cov'
)
print(f'    USA MAGs joined: {len(joined)}')

print('[2] Loading KO matrix...')
ko_long = pd.read_parquet(PROJ / 'data/mgnify_all_ko_matrix.parquet', columns=['genome_id','ko_id'])
ko_long = ko_long[ko_long['genome_id'].isin(set(joined['genome_id']))].copy()
ko_long['present'] = np.uint8(1)
ko_wide = ko_long.pivot_table(index='genome_id', columns='ko_id', values='present',
                               fill_value=0, aggfunc='max')
ko_wide.columns.name = None; ko_wide = ko_wide.reset_index()
df = joined.merge(ko_wide, on='genome_id', how='inner')
ko_cols_k = [c for c in ko_wide.columns if c.startswith('K')]

df['phylum'] = df['phylum'].fillna('Unknown')
df['phylum'] = df['phylum'].where(df['phylum'].map(df['phylum'].value_counts()) >= 5, 'Rare')
print(f'    Final df: {len(df)} MAGs, {len(ko_cols_k)} KOs')

# ------------------------------------------------------------------
print('\n[3] Score tests: completeness + other-metal control...')
all_results = []

for metal in METALS:
    other_m = [m for m in METALS if m != metal]
    core_needed = ['ph_soilgrids', 'lc_forest_pct', 'completeness', metal]
    mask = df[core_needed].notna().all(axis=1)
    sub = df[mask].copy().reset_index(drop=True)
    print(f'\n  [{metal}] n={len(sub)}', end='  ')

    prev = sub[ko_cols_k].sum()
    valid = prev[prev >= MIN_PREV].index.tolist()
    print(f'KOs={len(valid)}', end='  ')
    if not valid: print(); continue

    x_raw = sub[metal].values.astype(float)
    lo = max(np.nanpercentile(x_raw, 1), 1e-4)
    x_m = np.log10(np.maximum(x_raw, lo))
    x_m = (x_m - x_m.mean()) / (x_m.std() + 1e-12)

    ph_d = pd.get_dummies(sub['phylum'], prefix='ph', drop_first=True).astype(float)
    ph_d = ph_d.loc[:, ph_d.std() > 1e-8]

    Z = build_Z(sub, ph_d,
                completeness_col=['completeness','contamination'],
                other_metals=other_m)
    print(f'Z={Z.shape}', end='  ')

    Y = sub[valid].values.astype(float)
    beta, t_stat, p_vals = score_test(Y, x_m, Z)

    df_res = pd.DataFrame({
        'ko_id':   valid, 'metal': metal,
        'beta':    beta,  'p_value': p_vals,
        'n_mags':  len(sub), 'n_pos': prev[valid].astype(int).values,
    })
    n_valid = df_res['p_value'].notna().sum()
    all_results.append(df_res)
    print(f'valid={n_valid}')

# ------------------------------------------------------------------
print('\n[4] Pooled BH-FDR...')
results = pd.concat(all_results, ignore_index=True)
mask_all = results['p_value'].notna()
_, q, _, _ = multipletests(results.loc[mask_all, 'p_value'], method='fdr_bh')
results.loc[mask_all, 'q_value'] = q

out_path = OUT / 'nb18_spire_completeness_multimetal.csv'
results.to_csv(out_path, index=False)
print(f'Saved: {out_path}')

sig = results[results['q_value'] < 0.05]
print(f'\n=== NB18 SUMMARY ===')
print(f'Total tests: {mask_all.sum():,}, FDR<0.05: {len(sig)}')
print(results.groupby('metal').agg(
    n_tested=('ko_id','count'),
    n_sig=('q_value', lambda x: (x<0.05).sum())
).to_string())

# ------------------------------------------------------------------
print('\n[5] Comparison with NB16 (no completeness/inter-metal control)...')
nb16 = pd.read_csv(OUT / 'nb16_spire_full_covariate_mwas.csv')
nb16_sig = set(zip(nb16[nb16['q_value']<0.05]['ko_id'], nb16[nb16['q_value']<0.05]['metal']))
nb18_sig = set(zip(sig['ko_id'], sig['metal']))

survived = nb16_sig & nb18_sig
dropped  = nb16_sig - nb18_sig
new_hits = nb18_sig - nb16_sig
print(f'NB16 hits: {len(nb16_sig)}, NB18 hits: {len(nb18_sig)}')
print(f'NB16 hits surviving NB18: {len(survived)} / {len(nb16_sig)} ({len(survived)/max(len(nb16_sig),1)*100:.1f}%)')
print(f'NB16 hits dropped by completeness+multi-metal: {len(dropped)}')
print(f'New hits in NB18: {len(new_hits)}')

# Metal-by-metal survival
print('\nSurvival by metal:')
for m in METALS:
    nb16_m = {p for p in nb16_sig if p[1]==m}
    nb18_m = {p for p in nb18_sig if p[1]==m}
    surv   = nb16_m & nb18_m
    print(f'  {m}: NB16={len(nb16_m)}, NB18={len(nb18_m)}, survived={len(surv)} ({len(surv)/max(len(nb16_m),1)*100:.0f}%)')

# Specific check: As near-universal housekeeping genes
print('\nAs hits in NB16 that dropped in NB18 (sample):')
ann = pd.read_csv(OUT / 'all_ko_annotations.csv')[['ko_id','description']]
as_dropped = [p for p in dropped if p[1]=='As'][:15]
for ko, m in as_dropped:
    row = nb16[nb16['ko_id']==ko]
    prev_pct = (row['n_pos'].values[0]/row['n_mags'].values[0]*100) if len(row) else 0
    desc = ann[ann['ko_id']==ko]['description'].values
    d = str(desc[0])[:65] if len(desc) else '?'
    print(f'  {ko} ({prev_pct:.0f}%): {d}')

print('\nAs hits surviving NB18 (new or retained):')
as_surv = sorted([p for p in nb18_sig if p[1]=='As'], key=lambda p: sig[(sig['ko_id']==p[0])&(sig['metal']=='As')]['q_value'].values[0] if len(sig[(sig['ko_id']==p[0])&(sig['metal']=='As')]) else 1)[:15]
for ko, m in as_surv:
    r = sig[(sig['ko_id']==ko)&(sig['metal']==m)]
    if not len(r): continue
    row = r.iloc[0]
    desc = ann[ann['ko_id']==ko]['description'].values
    d = str(desc[0])[:65] if len(desc) else '?'
    print(f'  {"↑" if row["beta"]>0 else "↓"} {ko} β={row["beta"]:+.3f} q={row["q_value"]:.1e} prev={row["n_pos"]/row["n_mags"]*100:.0f}%: {d}')
