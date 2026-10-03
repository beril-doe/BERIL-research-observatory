#!/usr/bin/env python3
"""
NB16: SPIRE per-KO MWAS with the same full covariate set used in the CWM analysis.

NB14 controlled only for latitude + phylum.  This script adds the full soil/
environmental confounder stack from covariate_matrix_634.csv (same 634 thinned
USA cells used for CWM), making the SPIRE and CWM analyses methodologically
symmetric for cross-dataset comparison.

Join: each SPIRE MAG is matched to its nearest thinned cell (≤1 degree) via
KDTree. Metal values come from the covariate matrix (same USGS source as NB14).

Covariates in Z (null model):
  intercept, lat, lon,
  ph_soilgrids,
  drainage_class (dummies, 5 levels),
  lith_class (dummies, ≤13 levels),
  usgs_mine_distance,
  clay_pct  (median-imputed if NA ≤20%),
  organic_matter (median-imputed if NA ≤20%),
  lc_forest_pct, lc_cultivated_pct, lc_urban_pct,
  phylum (MAG's own phylum, dummies)

Excluded (vs CWM):
  shannon, phylum_Acidobacteria, etc. — community-level, not per-MAG
  cec (26.8% NA), epa_tri_releases (33% NA), tectonic_boundary_dist (82.5% NA)

Statistical method: same vectorized OLS score test as NB14.
  BH-FDR pooled across all 6 metals (matching CWM pooling strategy).
"""
import os
os.environ['OMP_NUM_THREADS'] = '1'

import sys
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.stats import t as t_dist
from statsmodels.stats.multitest import multipletests

REPO = Path('/home/hmacgregor/BERIL-research-observatory')
PROJ = REPO / 'projects' / 'per_ko_metal_associations'
MEP  = REPO / 'projects' / 'microbeatlas_metal_ecology'
OUT  = PROJ / 'data'

METALS     = ['As', 'Cd', 'Cr', 'Cu', 'Hg', 'Pb']
MIN_PREV   = 20        # min positive MAGs per KO per metal analysis
MAX_NN_DEG = 1.0       # max nearest-neighbour distance (degrees)

# Covariates to include (complete-case per cell after imputation)
CONT_COVS  = ['lat', 'lon', 'ph_soilgrids', 'usgs_mine_distance',
               'clay_pct', 'organic_matter',
               'lc_forest_pct', 'lc_cultivated_pct', 'lc_urban_pct']
CAT_COVS   = ['drainage_class', 'lith_class']   # will be one-hot encoded
IMPUTE_COLS = ['clay_pct', 'organic_matter']     # median-impute up to 20% NA


def score_test_metal(Y, x, Z, ko_names, label):
    """
    Vectorized OLS partial-correlation score test.
    Residualizes both x and each y_k on Z (OLS), then tests r² via F-stat.
    Returns (beta_ols, t_stat, p_value) arrays of length K.
    """
    n, K = Y.shape
    # Residualize Z out of x
    Zt    = Z.T
    ZtZ   = Zt @ Z
    try:
        ZtZ_inv = np.linalg.pinv(ZtZ)
    except np.linalg.LinAlgError:
        return np.full(K, np.nan), np.full(K, np.nan), np.full(K, np.nan)
    H = Z @ ZtZ_inv @ Zt        # hat matrix for Z
    x_res = x - H @ x           # residualized x  (n,)
    x_ss  = x_res @ x_res       # scalar

    if x_ss < 1e-12:
        return np.full(K, np.nan), np.full(K, np.nan), np.full(K, np.nan)

    # Residualize Z out of all KO columns simultaneously
    Y_res = Y - H @ Y           # (n, K)
    y_ss  = (Y_res ** 2).sum(axis=0)   # (K,)

    # OLS beta: x_res.T @ Y_res / x_ss
    cov_xy = x_res @ Y_res      # (K,)
    beta   = cov_xy / x_ss      # (K,)

    # Residual SS for regression y ~ x (after removing Z)
    df_res = n - Z.shape[1] - 1
    if df_res < 2:
        return beta, np.full(K, np.nan), np.full(K, np.nan)

    # t-stat: beta / SE, SE = sqrt(MSE / x_ss)
    fitted_var = (beta ** 2) * x_ss   # explained SS (K,)
    rss        = np.maximum(y_ss - fitted_var, 0)   # (K,)
    mse        = rss / df_res         # (K,)
    se         = np.sqrt(mse / x_ss)  # (K,)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        t_stat = beta / se            # (K,)
    p_val  = 2 * t_dist.sf(np.abs(t_stat), df=df_res)
    return beta, t_stat, p_val


def build_Z(df, phylum_dummies):
    """Build null design matrix from covariate df + phylum dummies."""
    parts = [np.ones((len(df), 1))]   # intercept
    for col in CONT_COVS:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors='coerce').fillna(0).values.reshape(-1, 1)
            parts.append(vals.astype(float))
    for col in CAT_COVS:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True).astype(float)
            # Drop near-constant columns
            std = dummies.std()
            dummies = dummies.loc[:, std > 1e-8]
            parts.append(dummies.values)
    if phylum_dummies is not None:
        parts.append(phylum_dummies.values)
    Z = np.hstack(parts)
    # Drop near-constant columns globally
    col_std = Z.std(axis=0)
    Z = Z[:, col_std > 1e-8]
    return Z


def main():
    print('=== NB16: SPIRE full-covariate MWAS ===')
    print(f'Covariates: {CONT_COVS + CAT_COVS} + MAG phylum dummies')
    print()

    # ------------------------------------------------------------------
    # 1. Load covariate matrix (634 thinned USA cells)
    # ------------------------------------------------------------------
    print('[1] Loading covariate matrix...')
    cov = pd.read_csv(MEP / 'data' / 'usa_cwm' / 'covariate_matrix_634.csv')
    print(f'    Covariate matrix: {cov.shape}')

    # Median-impute selected continuous covariates
    for col in IMPUTE_COLS:
        if col in cov.columns:
            med = cov[col].median()
            na_rate = cov[col].isna().mean()
            if na_rate <= 0.25:
                print(f'    Imputing {col} (NA={na_rate:.1%}) with median={med:.2f}')
                cov[col] = cov[col].fillna(med)

    # ------------------------------------------------------------------
    # 2. Load SPIRE MAG geospatial traits, filter to USA
    # ------------------------------------------------------------------
    print('\n[2] Loading MAG geospatial traits...')
    geo = pd.read_csv(MEP / 'data' / 'final_mags_geospatial_traits.csv')
    usa = geo[(geo['lat'] >= 24) & (geo['lat'] <= 50) &
              (geo['lon'] >= -125) & (geo['lon'] <= -65)].copy()
    print(f'    USA MAGs: {len(usa)}')

    # Nearest-neighbour join to thinned cells
    tree   = cKDTree(cov[['lat', 'lon']].values)
    dists, idxs = tree.query(usa[['lat', 'lon']].values, k=1)
    usa['nn_dist']  = dists
    usa['cov_idx']  = idxs
    usa = usa[usa['nn_dist'] <= MAX_NN_DEG].copy()
    print(f'    USA MAGs within {MAX_NN_DEG}°: {len(usa)}')

    # Attach covariate columns to each MAG row
    cov_cols = CONT_COVS + CAT_COVS + METALS
    cov_sub  = cov[cov_cols].reset_index(drop=True)
    joined   = usa.reset_index(drop=True).join(
        cov_sub.iloc[usa['cov_idx'].values].reset_index(drop=True),
        rsuffix='_cov'
    )
    print(f'    After NN join: {len(joined)} MAGs')

    # ------------------------------------------------------------------
    # 3. Load KO matrix
    # ------------------------------------------------------------------
    print('\n[3] Loading KO matrix...')
    usa_ids = set(joined['genome_id'])
    ko_long = pd.read_parquet(
        PROJ / 'data' / 'mgnify_all_ko_matrix.parquet',
        columns=['genome_id', 'ko_id']
    )
    ko_long = ko_long[ko_long['genome_id'].isin(usa_ids)].copy()
    ko_long['present'] = np.uint8(1)
    ko_wide = ko_long.pivot_table(
        index='genome_id', columns='ko_id', values='present',
        fill_value=0, aggfunc='max'
    )
    ko_wide.columns.name = None
    ko_wide = ko_wide.reset_index()
    print(f'    KO wide matrix: {ko_wide.shape}')

    df = joined.merge(ko_wide, on='genome_id', how='inner')
    print(f'    Merged: {len(df)} MAGs')

    # Phylum dummies (MAG's own phylum)
    df['phylum'] = df['phylum'].fillna('Unknown')
    df['phylum'] = df['phylum'].where(
        df['phylum'].map(df['phylum'].value_counts()) >= 5, 'Rare'
    )
    print(f'    Unique phyla: {df["phylum"].nunique()}')

    ko_cols   = [c for c in ko_wide.columns if c.startswith('K')]

    # ------------------------------------------------------------------
    # 4. Score test per metal
    # ------------------------------------------------------------------
    print('\n[4] Score tests...')
    all_results = []

    for metal in METALS:
        print(f'\n  [{metal}]', end=' ')

        # Complete-case filter: need metal + core covariates
        core_needed = ['ph_soilgrids', 'lc_forest_pct'] + [metal]
        mask = df[core_needed].notna().all(axis=1)
        sub  = df[mask].copy().reset_index(drop=True)
        print(f'n={len(sub)} MAGs with complete data', end='  ')

        # Prevalence filter
        prev     = sub[ko_cols].sum()
        valid_kos = prev[prev >= MIN_PREV].index.tolist()
        print(f'KOs≥{MIN_PREV}: {len(valid_kos)}')

        if len(valid_kos) == 0:
            continue

        # Metal: log10 transform (USGS metals are in mg/kg or ppm — already positive)
        x_raw = sub[metal].values.astype(float)
        lo    = np.nanpercentile(x_raw, 1)
        if lo <= 0:
            lo = 1e-4
        x_m = np.log10(np.maximum(x_raw, lo))
        x_m = (x_m - x_m.mean()) / (x_m.std() + 1e-12)   # standardize

        # Build Z
        ph_dummies = pd.get_dummies(sub['phylum'], prefix='ph', drop_first=True).astype(float)
        std = ph_dummies.std()
        ph_dummies = ph_dummies.loc[:, std > 1e-8]
        Z = build_Z(sub, ph_dummies)
        print(f'    Z shape: {Z.shape}', end='  ')

        Y  = sub[valid_kos].values.astype(np.float64)
        beta_ols, t_stat, p_vals = score_test_metal(Y, x_m, Z, valid_kos, metal)

        df_res = pd.DataFrame({
            'ko_id':   valid_kos,
            'metal':   metal,
            'beta':    beta_ols,
            't_stat':  t_stat,
            'p_value': p_vals,
            'n_mags':  len(sub),
            'n_pos':   prev[valid_kos].astype(int).values,
        })
        all_results.append(df_res)
        valid = df_res['p_value'].notna().sum()
        print(f'valid tests: {valid}')

    # ------------------------------------------------------------------
    # 5. Pool BH-FDR across all 6 metals (matching CWM strategy)
    # ------------------------------------------------------------------
    results = pd.concat(all_results, ignore_index=True)
    mask_valid = results['p_value'].notna()
    qs = np.full(len(results), np.nan)
    _, q, _, _ = multipletests(results.loc[mask_valid, 'p_value'], method='fdr_bh')
    qs[mask_valid] = q
    results['q_value'] = qs

    out_path = OUT / 'nb16_spire_full_covariate_mwas.csv'
    results.to_csv(out_path, index=False)
    print(f'\n[5] Saved: {out_path}')

    sig = results[results['q_value'] < 0.05]
    print(f'\n=== SUMMARY ===')
    print(f'Total tests: {mask_valid.sum():,}')
    print(f'FDR q<0.05: {len(sig)}')
    print('\nPer metal:')
    print(results.groupby('metal').agg(
        n_tested=('ko_id', 'count'),
        n_sig=('q_value', lambda x: (x < 0.05).sum())
    ).to_string())

    # ------------------------------------------------------------------
    # 6. Compare with CWM 75 hits
    # ------------------------------------------------------------------
    print('\n=== COMPARISON WITH CWM 75 HITS ===')
    from statsmodels.stats.multitest import multipletests as mtp
    usa_cwm = MEP / 'data' / 'usa_cwm'
    df_all  = pd.read_csv(usa_cwm / 'gam_results_v3_all.csv')
    six     = df_all[df_all['metal'].isin(METALS)].copy()
    mv      = six['p_metal_full'].notna()
    qs2     = np.full(len(six), np.nan)
    _, q2, _, _ = mtp(six.loc[mv, 'p_metal_full'], method='fdr_bh')
    qs2[mv] = q2
    six['q_6metal'] = qs2
    cwm_hits = six[six['q_6metal'] < 0.05].copy()

    cwm_pairs   = set(zip(cwm_hits['ko_id'], cwm_hits['metal']))
    spire_pairs = set(zip(sig['ko_id'], sig['metal']))
    exact       = cwm_pairs & spire_pairs
    ko_overlap  = set(cwm_hits['ko_id']) & set(sig['ko_id'])

    print(f'CWM hits (FDR<0.05):          {len(cwm_pairs)}')
    print(f'NB16 SPIRE hits (FDR<0.05):   {len(spire_pairs)}')
    print(f'Exact KO×metal overlap:        {len(exact)}')
    print(f'KO-level overlap (any metal):  {len(ko_overlap)}')

    total_tests = mask_valid.sum()
    expected = len(cwm_pairs) * len(spire_pairs) / total_tests if total_tests > 0 else 0
    print(f'Expected under null:           {expected:.1f}')

    if exact:
        print('\nExact overlapping pairs:')
        for ko, m in sorted(exact):
            cwm_sign  = cwm_hits[(cwm_hits['ko_id']==ko) & (cwm_hits['metal']==m)]['beta_sign'].values
            spire_b   = sig[(sig['ko_id']==ko) & (sig['metal']==m)]['beta'].values
            spire_sign = np.sign(spire_b[0]) if len(spire_b) else np.nan
            concordant = '✓' if (len(cwm_sign) > 0 and cwm_sign[0] == spire_sign) else '✗'
            print(f'  {ko}×{m}: CWM β_sign={cwm_sign}, SPIRE β={spire_b[0] if len(spire_b) else "?":.3f} {concordant}')

    if ko_overlap:
        print(f'\nKO-level overlap: {sorted(ko_overlap)}')

    # NB14 vs NB16 comparison
    nb14_path = OUT / 'nb14_usa_usgs_per_ko_mwas.csv'
    if nb14_path.exists():
        nb14 = pd.read_csv(nb14_path)
        nb14_sig = nb14[nb14['q_value'] < 0.05]
        print(f'\n=== NB14 (lat+phylum only) vs NB16 (full covariates) ===')
        print(f'NB14 FDR<0.05: {len(nb14_sig)}')
        print(f'NB16 FDR<0.05: {len(sig)}')
        nb14_pairs = set(zip(nb14_sig['ko_id'], nb14_sig['metal']))
        survival   = nb14_pairs & spire_pairs
        print(f'NB14 hits surviving NB16 full covariates: {len(survival)} / {len(nb14_pairs)} ({len(survival)/len(nb14_pairs)*100:.1f}%)')
        print(f'New hits in NB16 (not in NB14): {len(spire_pairs - nb14_pairs)}')


if __name__ == '__main__':
    main()
