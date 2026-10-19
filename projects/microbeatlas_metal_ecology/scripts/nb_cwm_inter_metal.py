#!/usr/bin/env python3
"""
CWM inter-metal control + CWM/SPIRE genus-gene coherence test.

Part A: Apply inter-metal control to CWM (same methodology as NB18 SPIRE).
  - Vectorized OLS score test on CWM, Z = same 28 covariates as the full GAM model
    plus log10 of the other 5 metals (median-imputed).
  - Compare surviving CWM hits with NB18 hits.

Part B: CWM direction test for NB18 hits.
  - For each NB18-sig KO×metal pair, compute partial correlation between
    CWM and metal (residualizing Z without other-metal covariates).
  - Reports how many NB18 hits show directional agreement in CWM even if non-significant.
  - Tests genus-gene coherence: if CWM direction matches NB18 β, then the genera
    carrying the SPIRE-enriched gene are also enriched (or depleted) in high-metal
    CWM sites.
"""
import os
os.environ['OMP_NUM_THREADS'] = '1'
import numpy as np
import pandas as pd
import warnings
from pathlib import Path
from scipy.stats import t as t_dist
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests

REPO  = Path('/home/hmacgregor/BERIL-research-observatory')
PROJ  = REPO / 'projects/microbeatlas_metal_ecology'
PKO   = REPO / 'projects/per_ko_metal_associations'
CWM_D = PROJ / 'data/usa_cwm'
METALS = ['As', 'Cd', 'Cr', 'Cu', 'Hg', 'Pb']
MIN_N  = 30  # min non-NA sites per metal

CONT_COVS = ['lat', 'lon', 'ph_soilgrids', 'usgs_mine_distance',
             'clay_pct', 'organic_matter', 'lc_forest_pct',
             'lc_cultivated_pct', 'lc_urban_pct', 'shannon']
CAT_COVS  = ['drainage_class', 'lith_class']
PHYLUM_COLS = [c for c in [
    'phylum_Acidobacteria', 'phylum_Actinobacteria', 'phylum_Ascomycota',
    'phylum_Bacteroidetes', 'phylum_Basidiomycota', 'phylum_Planctomycetes',
    'phylum_Proteobacteria', 'phylum_Thaumarchaeota'
] if True]

# ------------------------------------------------------------------
def build_Z(sub, include_other_metals=None):
    parts = [np.ones((len(sub), 1))]
    for col in CONT_COVS:
        v = pd.to_numeric(sub[col], errors='coerce').fillna(0).values.reshape(-1, 1)
        parts.append(v.astype(float))
    for col in CAT_COVS:
        if col in sub.columns:
            d = pd.get_dummies(sub[col], prefix=col, drop_first=True).astype(float)
            d = d.loc[:, d.std() > 1e-8]
            if len(d.columns):
                parts.append(d.values)
    for col in PHYLUM_COLS:
        if col in sub.columns:
            v = sub[col].fillna(0).values.reshape(-1, 1)
            parts.append(v.astype(float))
    if include_other_metals:
        for m in include_other_metals:
            if m in sub.columns:
                raw = pd.to_numeric(sub[m], errors='coerce')
                med = raw.median() if raw.notna().any() else 0.0
                lo  = max(raw.quantile(0.01) if raw.notna().sum() > 0 else 1e-4, 1e-4)
                v   = np.log10(np.maximum(raw.fillna(med).values, lo)).reshape(-1, 1)
                parts.append(v.astype(float))
    Z = np.hstack(parts)
    Z = Z[:, Z.std(axis=0) > 1e-8]
    return Z


def score_test(Y, x, Z):
    """Vectorized OLS partial correlation score test."""
    n, K = Y.shape
    try:
        ZtZ_inv = np.linalg.pinv(Z.T @ Z)
    except Exception:
        return np.full(K, np.nan), np.full(K, np.nan), np.full(K, np.nan)
    H     = Z @ ZtZ_inv @ Z.T
    x_res = x - H @ x
    x_ss  = x_res @ x_res
    if x_ss < 1e-12:
        return np.full(K, np.nan), np.full(K, np.nan), np.full(K, np.nan)
    Y_res = Y - H @ Y
    beta  = (x_res @ Y_res) / x_ss
    df_r  = n - Z.shape[1] - 1
    if df_r < 2:
        return beta, np.full(K, np.nan), np.full(K, np.nan)
    rss  = np.maximum((Y_res ** 2).sum(axis=0) - beta ** 2 * x_ss, 0)
    se   = np.sqrt(rss / df_r / x_ss)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        t_stat = beta / se
    p = 2 * t_dist.sf(np.abs(t_stat), df=df_r)
    return beta, t_stat, p


# ------------------------------------------------------------------
print('[1] Loading data...')
cov = pd.read_csv(CWM_D / 'covariate_matrix_634.csv')
# Fill standard continuous covariates
for col in ['clay_pct', 'organic_matter']:
    cov[col] = cov[col].fillna(cov[col].median())

print('[2] Loading CWM parquet (long format)...')
cwm_long = pd.read_parquet(CWM_D / 'cwm_all_ko_thinned_634.parquet')
print(f'    {len(cwm_long):,} rows, {cwm_long["ko_id"].nunique()} KOs')

# Pivot to wide: samples × KOs
print('[3] Pivoting CWM to wide format...')
cwm_wide = cwm_long.pivot_table(index='sample_id', columns='ko_id',
                                 values='cwm', fill_value=0)
cwm_wide.columns.name = None
cwm_wide = cwm_wide.reset_index()
print(f'    Wide: {cwm_wide.shape}')

# Merge with covariates
df = cwm_wide.merge(cov, on='sample_id', how='inner')
ko_cols = [c for c in cwm_wide.columns if c.startswith('K')]
print(f'    Merged df: {df.shape[0]} samples, {len(ko_cols)} KOs')

# ------------------------------------------------------------------
# PART A: CWM inter-metal control score test
print('\n[PART A] CWM inter-metal control score test...')
all_results_A = []

for metal in METALS:
    other_m = [m for m in METALS if m != metal]
    mask = df[metal].notna() & df['ph_soilgrids'].notna()
    sub  = df[mask].copy().reset_index(drop=True)
    n    = len(sub)
    print(f'\n  [{metal}] n={n}', end='  ')
    if n < MIN_N:
        print('SKIP'); continue

    # Focal metal (log10, standardized)
    x_raw = sub[metal].values.astype(float)
    lo    = max(np.nanpercentile(x_raw, 1), 1e-4)
    x_m   = np.log10(np.maximum(x_raw, lo))
    x_m   = (x_m - x_m.mean()) / (x_m.std() + 1e-12)

    Z = build_Z(sub, include_other_metals=other_m)
    print(f'Z={Z.shape}', end='  ')

    Y = sub[ko_cols].values.astype(float)
    beta, t_stat, p_vals = score_test(Y, x_m, Z)

    res = pd.DataFrame({'ko_id': ko_cols, 'metal': metal,
                        'beta_cwm': beta, 'p_value': p_vals, 'n': n})
    all_results_A.append(res)
    print(f'tests={len(ko_cols)}')

results_A = pd.concat(all_results_A, ignore_index=True)
mask_ok   = results_A['p_value'].notna()
_, q, _, _ = multipletests(results_A.loc[mask_ok, 'p_value'], method='fdr_bh')
results_A.loc[mask_ok, 'q_value'] = q

out_A = PROJ / 'data/usa_cwm/cwm_inter_metal_score_test.csv'
results_A.to_csv(out_A, index=False)
print(f'\nSaved Part A: {out_A}')

sig_A  = results_A[results_A['q_value'] < 0.05]
print(f'\n=== CWM inter-metal hits (FDR<0.05) ===')
print(results_A.groupby('metal').agg(
    n_tests=('ko_id', 'count'),
    n_sig=('q_value', lambda x: (x < 0.05).sum())
).to_string())

# ------------------------------------------------------------------
# Load NB18 for comparison
print('\n[PART A continued] Comparing CWM-interacted vs NB18...')
nb18 = pd.read_csv(PKO / 'data/nb18_spire_completeness_multimetal.csv')
nb18_sig = set(zip(nb18[nb18['q_value'] < 0.05]['ko_id'],
                   nb18[nb18['q_value'] < 0.05]['metal']))
cwm_A_sig = set(zip(sig_A['ko_id'], sig_A['metal']))

# Also load the original 75 CWM hits
hits75 = pd.read_csv(CWM_D / 'hits_75_annotated.csv') if (CWM_D / 'hits_75_annotated.csv').exists() else pd.DataFrame()
sig75 = (set(zip(hits75['ko_id'], hits75['metal']))
         if 'ko_id' in hits75.columns and 'metal' in hits75.columns
         else set())

print(f'CWM inter-metal hits: {len(cwm_A_sig)}')
print(f'NB18 hits: {len(nb18_sig)}')
if sig75:
    print(f'Original CWM 75 hits surviving inter-metal control: '
          f'{len(sig75 & cwm_A_sig)} / {len(sig75)}')

overlap_AB = cwm_A_sig & nb18_sig
print(f'CWM-interacted × NB18 overlap: {len(overlap_AB)}')
if overlap_AB:
    print('Overlapping pairs:')
    for ko, m in sorted(overlap_AB):
        r_cwm = sig_A[(sig_A['ko_id']==ko) & (sig_A['metal']==m)].iloc[0]
        r_nb18 = nb18[(nb18['ko_id']==ko) & (nb18['metal']==m)].iloc[0]
        print(f'  {ko}×{m}: CWM β={r_cwm["beta_cwm"]:+.4f} q={r_cwm["q_value"]:.2e}  '
              f'NB18 β={r_nb18["beta"]:+.4f} q={r_nb18["q_value"]:.2e}')

# Hypergeometric p-value for overlap (same shared-test-space logic as before)
# shared test space: KOs tested in BOTH
cwm_A_pairs = set(zip(results_A['ko_id'], results_A['metal']))
nb18_pairs  = set(zip(nb18['ko_id'], nb18['metal']))
shared      = cwm_A_pairs & nb18_pairs
N_shared    = len(shared)
cwm_A_hits_shared  = {p for p in cwm_A_sig if p in shared}
nb18_hits_shared   = {p for p in nb18_sig  if p in shared}
K_cwm   = len(cwm_A_hits_shared)
K_nb18  = len(nb18_hits_shared)
overlap_shared = len(cwm_A_hits_shared & nb18_hits_shared)
from scipy.stats import hypergeom
p_enrichment = hypergeom.sf(overlap_shared - 1, N_shared, K_cwm, K_nb18)
p_depletion  = hypergeom.cdf(overlap_shared,     N_shared, K_cwm, K_nb18)
exp_overlap  = K_cwm * K_nb18 / max(N_shared, 1)
print(f'\nHypergeometric (shared test space={N_shared:,}):')
print(f'  CWM hits in shared: {K_cwm}, NB18 hits in shared: {K_nb18}')
print(f'  Observed overlap: {overlap_shared}, Expected: {exp_overlap:.1f}')
print(f'  p_enrich={p_enrichment:.4f}  p_deplete={p_depletion:.4f}')

# ------------------------------------------------------------------
# PART B: CWM direction test for NB18 hits (genus-gene coherence)
print('\n[PART B] CWM direction test for NB18 hits (genus-gene coherence)...')
# Build Z WITHOUT other-metal control (same Z as NB16 / original CWM)
nb18_sig_list = nb18[nb18['q_value'] < 0.05][['ko_id', 'metal', 'beta']].copy()

results_B = []
for metal in METALS:
    mask = df[metal].notna() & df['ph_soilgrids'].notna()
    sub  = df[mask].copy().reset_index(drop=True)
    if len(sub) < MIN_N:
        continue
    x_raw = sub[metal].values.astype(float)
    lo    = max(np.nanpercentile(x_raw, 1), 1e-4)
    x_m   = np.log10(np.maximum(x_raw, lo))
    x_m   = (x_m - x_m.mean()) / (x_m.std() + 1e-12)
    Z = build_Z(sub, include_other_metals=None)
    H     = Z @ np.linalg.pinv(Z.T @ Z) @ Z.T
    x_res = x_m - H @ x_m

    hits_m = nb18_sig_list[nb18_sig_list['metal'] == metal]
    for _, row in hits_m.iterrows():
        ko = row['ko_id']
        if ko not in sub.columns:
            continue
        y = sub[ko].values.astype(float)
        y_res = y - H @ y
        x_ss  = x_res @ x_res
        beta_cwm = (x_res @ y_res) / x_ss if x_ss > 1e-12 else np.nan
        # simple Spearman for interpretability
        rho, rho_p = spearmanr(x_m, y)
        results_B.append({
            'ko_id': ko, 'metal': metal,
            'beta_nb18': row['beta'], 'beta_cwm_partial': beta_cwm,
            'rho_cwm': rho, 'rho_p': rho_p,
            'direction_agree': (row['beta'] * beta_cwm) > 0
        })

dfB = pd.DataFrame(results_B)
dfB = dfB.dropna(subset=['beta_cwm_partial'])
n_agree = dfB['direction_agree'].sum()
n_total = len(dfB)
print(f'\nNB18 hits with CWM data: {n_total}')
print(f'Directional agreement (CWM partial corr): {n_agree}/{n_total} ({n_agree/max(n_total,1)*100:.1f}%)')

# Expected by chance: 50%
from scipy.stats import binomtest
bt = binomtest(n_agree, n_total, 0.5)
print(f'Binomial test vs 50%: p={bt.pvalue:.4f}')

# By metal
print('\nAgreement by metal:')
for m in METALS:
    sub_m = dfB[dfB['metal'] == m]
    if len(sub_m) == 0: continue
    ag = sub_m['direction_agree'].sum()
    print(f'  {m}: {ag}/{len(sub_m)} ({ag/len(sub_m)*100:.0f}%)')

# Key NB18 biological hits — are they directionally consistent in CWM?
KEY_HITS = {
    ('K05566', 'Cu'): 'mrpB Mrp antiporter',
    ('K05570', 'Cu'): 'mrpF Mrp antiporter',
    ('K01546', 'Hg'): 'kdpA K+ ATPase',
    ('K01547', 'Hg'): 'kdpB K+ ATPase',
    ('K01548', 'Hg'): 'kdpC K+ ATPase',
    ('K05563', 'Pb'): 'phaF K+:H+ antiporter',
    ('K06048', 'Pb'): 'gshA GSH biosynthesis',
    ('K17883', 'Cd'): 'mtr mycothiol reductase',
    ('K02591', 'Cd'): 'nifK nitrogenase',
    ('K02168', 'Cr'): 'betT betaine transporter',
    ('K02000', 'Cr'): 'proV betaine/proline ABC',
}
print('\nKey NB18 biological hits — CWM direction:')
for (ko, metal), name in KEY_HITS.items():
    row = dfB[(dfB['ko_id'] == ko) & (dfB['metal'] == metal)]
    if len(row) == 0:
        print(f'  {ko}×{metal} {name}: not in CWM data')
        continue
    r = row.iloc[0]
    agree = '✓ AGREE' if r['direction_agree'] else '✗ OPPOSE'
    print(f'  {agree} | {ko}×{metal} {name}: NB18β={r["beta_nb18"]:+.3f}  CWM_partial={r["beta_cwm_partial"]:+.3f}  ρ={r["rho_cwm"]:+.3f}')

out_B = PROJ / 'data/usa_cwm/nb18_cwm_direction_check.csv'
dfB.to_csv(out_B, index=False)
print(f'\nSaved Part B: {out_B}')

print('\n=== DONE ===')
