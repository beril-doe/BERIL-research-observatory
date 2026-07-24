"""NB03 — Statistical analysis, figures, and derived tables.

Inputs (from prior Spark runs):
  data/biome_summary.csv
  data/biome_pfam_matrix.csv
  data/biome_top_uncovered.csv
  data/species_biome.csv
  data/genome_biome.csv

Outputs:
  data/biome_summary_annotated.csv     — with rates + Fisher enrichments
  data/biome_fisher_no_pfam.csv        — pairwise vs global rate + BH-FDR
  data/aggregate_glm_no_pfam.csv       — biome + is_core coefficients
  data/biome_uncovered_matrix.csv      — pivot: biome × top-uncovered-Pfam
  figures/NB03_biome_stacked_tier.png
  figures/NB03_biome_by_core_stacked.png
  figures/NB03_biome_no_pfam_rate.png
  figures/NB03_top_uncovered_heatmap.png
  figures/NB03_pfam_universe_venn.png  (simple 3-set)
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests
# statsmodels has import bug in this env; use scipy + manual chi-square instead

ROOT = "/home/justaddcoffee/BERIL-research-observatory/projects/structural_coverage_biome"
DATA = f"{ROOT}/data"
FIG  = f"{ROOT}/figures"
os.makedirs(FIG, exist_ok=True)

# Load
summary = pd.read_csv(f"{DATA}/biome_summary.csv")
matrix  = pd.read_csv(f"{DATA}/biome_pfam_matrix.csv")
top_unc = pd.read_csv(f"{DATA}/biome_top_uncovered.csv")

# ============================================================================
# 1) ANNOTATED SUMMARY + FISHER (global-rate no_pfam)
# ============================================================================
total_no_pfam = summary["n_no_pfam"].sum()
total_all     = summary["n_clusters_total"].sum()
global_no_pfam_rate = total_no_pfam / total_all
print(f"Global no-Pfam rate: {100*global_no_pfam_rate:.2f}%")

def fisher_vs_global(a, n):
    # 2x2: [biome has_no_pfam, biome has_pfam ; global rest has_no_pfam, has_pfam]
    b_a = a
    b_b = n - a
    g_a = total_no_pfam - a
    g_b = (total_all - total_no_pfam) - b_b
    if b_b < 0 or g_a < 0 or g_b < 0: return np.nan
    _, p = stats.fisher_exact([[b_a, b_b], [g_a, g_b]])
    return p

fisher_no_pfam = summary.apply(
    lambda r: fisher_vs_global(r["n_no_pfam"], r["n_clusters_total"]),
    axis=1)
q_no_pfam = multipletests(fisher_no_pfam.fillna(1.0), method="fdr_bh")[1]
summary["fisher_p_no_pfam_vs_global"] = fisher_no_pfam
summary["fisher_q_bh_no_pfam"]        = q_no_pfam
summary["log2_no_pfam_enrichment"]    = np.log2(
    (summary["n_no_pfam"] / summary["n_clusters_total"]) / global_no_pfam_rate)
summary.to_csv(f"{DATA}/biome_summary_annotated.csv", index=False)

# Same for "all_covered" (positive signal, structurally best-covered biomes)
total_all_cov = summary["n_pfam_all_covered"].sum()
global_all_cov_rate = total_all_cov / total_all

# ============================================================================
# 2) BOOTSTRAP 95% CIs for no_pfam rate per biome
# ============================================================================
rng = np.random.default_rng(42)
def bootstrap_ci(k, n, iters=2000, alpha=0.05):
    if n == 0: return (np.nan, np.nan)
    draws = rng.binomial(n, k/n, size=iters) / n
    return np.quantile(draws, [alpha/2, 1-alpha/2])

cis = np.array([bootstrap_ci(r["n_no_pfam"], r["n_clusters_total"])
                for _, r in summary.iterrows()])
summary["no_pfam_ci_lo"] = cis[:, 0]
summary["no_pfam_ci_hi"] = cis[:, 1]

# ============================================================================
# 3) GLM: no_pfam rate ~ biome + is_core (aggregate-level, freq-weighted binomial)
# ============================================================================
mtx = matrix.copy()
# outcome: no_pfam (binary) — but matrix has 4 pfam_tier values. Recode.
mtx["is_no_pfam"] = (mtx["pfam_tier"] == "no_pfam_annotation").astype(int)
mtx["is_all_cov"] = (mtx["pfam_tier"] == "pfam_all_covered").astype(int)
mtx["is_core_int"] = mtx["is_core"].astype(bool).astype(int)

# collapse to biome × is_core, sum n_clusters per outcome
glm_input = (mtx.groupby(["biome", "is_core_int"])
    .apply(lambda g: pd.Series({
        "n_total":    g["n_clusters"].sum(),
        "n_no_pfam":  (g["n_clusters"] * g["is_no_pfam"]).sum(),
        "n_all_cov":  (g["n_clusters"] * g["is_all_cov"]).sum(),
    })).reset_index())
glm_input["rate_no_pfam"] = glm_input["n_no_pfam"] / glm_input["n_total"]
glm_input["rate_all_cov"] = glm_input["n_all_cov"] / glm_input["n_total"]

# Chi-square: is biome associated with pfam_tier, and does effect survive stratification by is_core?
# Test 1: biome × pfam_tier omnibus (marginal)
ctab_marg = mtx.groupby(["biome", "pfam_tier"])["n_clusters"].sum().unstack(fill_value=0)
chi2_marg, p_marg, dof_marg, _ = stats.chi2_contingency(ctab_marg.values)

# Test 2: same, within is_core=True
ctab_core = (mtx[mtx["is_core"] == True]
    .groupby(["biome", "pfam_tier"])["n_clusters"].sum().unstack(fill_value=0))
chi2_core, p_core, dof_core, _ = stats.chi2_contingency(ctab_core.values)

# Test 3: within is_core=False
ctab_ncore = (mtx[mtx["is_core"] == False]
    .groupby(["biome", "pfam_tier"])["n_clusters"].sum().unstack(fill_value=0))
chi2_ncore, p_ncore, dof_ncore, _ = stats.chi2_contingency(ctab_ncore.values)

# Per-biome log-odds-ratio for no_pfam, computed within core-only clusters
core_rows = (mtx[mtx["is_core"] == True]
    .groupby("biome").agg(
        n_no_pfam=("n_clusters", lambda x: (x * mtx.loc[x.index, "is_no_pfam"]).sum()),
        n_total=("n_clusters", "sum")).reset_index())
core_rows["rate"] = core_rows["n_no_pfam"] / core_rows["n_total"]
global_core_rate = core_rows["n_no_pfam"].sum() / core_rows["n_total"].sum()
core_rows["log2_enrich_vs_core_global"] = np.log2(core_rows["rate"] / global_core_rate)

glm_out = pd.DataFrame({
    "test": ["biome × tier (marginal)", "biome × tier (is_core=True)", "biome × tier (is_core=False)"],
    "chi2": [chi2_marg, chi2_core, chi2_ncore],
    "dof":  [dof_marg, dof_core, dof_ncore],
    "p":    [p_marg, p_core, p_ncore],
})
glm_out.to_csv(f"{DATA}/biome_chi2_tests.csv", index=False)
core_rows.to_csv(f"{DATA}/biome_core_no_pfam_rates.csv", index=False)
print("\n=== Chi-square tests ===")
print(glm_out.to_string(index=False))
print(f"\nCore-only global no-Pfam rate: {100*global_core_rate:.2f}%")
print("\nCore-only per-biome no-Pfam enrichment:")
print(core_rows[["biome", "n_total", "rate", "log2_enrich_vs_core_global"]]
      .sort_values("log2_enrich_vs_core_global").round(4).to_string(index=False))

# ============================================================================
# 4) BIOME × TOP-UNCOVERED PFAM PIVOT
# ============================================================================
# Get the 30 most-mentioned uncovered Pfams globally (union across biomes)
pfam_global = top_unc.groupby("pfam_id")["n_clusters"].sum().nlargest(30).index
pivot_unc = (top_unc[top_unc["pfam_id"].isin(pfam_global)]
    .pivot_table(index="biome", columns="pfam_id", values="n_clusters", fill_value=0))
# Normalize by biome size (rate per 1000 clusters)
biome_size = summary.set_index("biome")["n_clusters_total"]
pivot_unc_rate = pivot_unc.div(biome_size, axis=0).mul(1000)
pivot_unc_rate.to_csv(f"{DATA}/biome_uncovered_matrix.csv")

# ============================================================================
# FIGURES
# ============================================================================
plt.rcParams.update({"figure.dpi": 120, "font.size": 10})

# --- F1: Stacked-bar biome × pfam_tier (fractions) ---
s = summary.set_index("biome").sort_values("n_clusters_total", ascending=True)
tier_cols = ["n_no_pfam", "n_pfam_no_covered", "n_pfam_partial", "n_pfam_all_covered"]
tier_lbls = ["No Pfam annotation", "Pfam, no PDB coverage",
             "Pfam, partial PDB", "Pfam, all PDB-covered"]
tier_colors = ["#4d4d4d", "#d95f02", "#e6ab02", "#1b9e77"]
fracs = s[tier_cols].div(s["n_clusters_total"], axis=0)

fig, ax = plt.subplots(figsize=(10, 7))
cum = np.zeros(len(fracs))
for c, l, col in zip(tier_cols, tier_lbls, tier_colors):
    ax.barh(fracs.index, fracs[c], left=cum, color=col, label=l, edgecolor="white", linewidth=0.5)
    cum += fracs[c].values
ax.set_xlabel("Fraction of gene clusters")
ax.set_title("Structural (PDB-Pfam) coverage tier by biome — all gene clusters")
ax.set_xlim(0, 1)
ax.legend(loc="lower right", frameon=True)
for i, (b, tot) in enumerate(zip(s.index, s["n_clusters_total"])):
    ax.text(1.01, i, f"n={tot/1e6:.1f}M", va="center", fontsize=8)
fig.tight_layout()
fig.savefig(f"{FIG}/NB03_biome_stacked_tier.png", bbox_inches="tight")
plt.close(fig)

# --- F2: Same, but faceted by is_core ---
mtx["frac"] = 0.0  # float dtype
for biome in mtx["biome"].unique():
    for core in mtx["is_core"].unique():
        mask = (mtx["biome"] == biome) & (mtx["is_core"] == core)
        tot = mtx.loc[mask, "n_clusters"].sum()
        if tot > 0:
            mtx.loc[mask, "frac"] = (mtx.loc[mask, "n_clusters"] / tot).astype(float)

fig, axes = plt.subplots(1, 2, figsize=(15, 7), sharey=True)
for ax, core_val, subtitle in zip(axes, [True, False], ["is_core = True", "is_core = False"]):
    sub = (mtx[mtx["is_core"] == core_val]
        .pivot_table(index="biome", columns="pfam_tier",
                     values="n_clusters", aggfunc="sum", fill_value=0))
    # Compute fraction per row
    frac = sub.div(sub.sum(axis=1), axis=0)
    # Reorder cols
    frac = frac.reindex(columns=["no_pfam_annotation", "pfam_no_covered",
                                  "pfam_partial_covered", "pfam_all_covered"])
    # Sort biomes by total cluster count (from summary)
    order = summary.sort_values("n_clusters_total", ascending=True)["biome"].tolist()
    frac = frac.reindex(order)
    cum = np.zeros(len(frac))
    for c, l, col in zip(frac.columns, tier_lbls, tier_colors):
        ax.barh(frac.index, frac[c], left=cum, color=col, label=l, edgecolor="white", linewidth=0.5)
        cum += frac[c].values
    ax.set_title(subtitle)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Fraction of gene clusters")
axes[0].legend(loc="lower right", fontsize=8)
fig.suptitle("Coverage tier by biome, stratified by pangenome core status", y=1.01)
fig.tight_layout()
fig.savefig(f"{FIG}/NB03_biome_by_core_stacked.png", bbox_inches="tight")
plt.close(fig)

# --- F3: no_pfam rate with bootstrap CIs, sorted ---
s2 = summary.sort_values("pct_no_pfam")
fig, ax = plt.subplots(figsize=(9, 7))
xerr = np.abs(np.vstack([s2["pct_no_pfam"] - 100*s2["no_pfam_ci_lo"],
                         100*s2["no_pfam_ci_hi"] - s2["pct_no_pfam"]]))
ax.errorbar(s2["pct_no_pfam"], s2["biome"], xerr=xerr, fmt="o", capsize=3, color="#4d4d4d")
ax.axvline(100 * global_no_pfam_rate, color="#c92222", linestyle="--",
           label=f"global rate = {100*global_no_pfam_rate:.1f}%")
ax.set_xlabel("% gene clusters without Pfam annotation")
ax.set_title("Pfam-annotation gap by biome (95% bootstrap CIs)")
ax.legend()
fig.tight_layout()
fig.savefig(f"{FIG}/NB03_biome_no_pfam_rate.png", bbox_inches="tight")
plt.close(fig)

# --- F4: Biome × top-uncovered-Pfam heatmap (rate per 1000 clusters) ---
# Reorder biomes by total size
biome_order = summary.sort_values("n_clusters_total", ascending=False)["biome"].tolist()
pivot_unc_rate = pivot_unc_rate.reindex(biome_order)

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot_unc_rate.T, cmap="YlOrRd", ax=ax,
            cbar_kws={"label": "Clusters per 1,000 (rate)"}, linewidths=0.3)
ax.set_title("Top-30 globally uncovered Pfams — rate per 1,000 clusters, by biome")
ax.set_xlabel("Biome")
ax.set_ylabel("Pfam ID (no PDB structure)")
fig.tight_layout()
fig.savefig(f"{FIG}/NB03_top_uncovered_heatmap.png", bbox_inches="tight")
plt.close(fig)

# --- F5: Pfam universe overview ---
n_pdb_only  = 12053 - 9266     # PDB Pfams NOT in pangenome
n_bakta_only= 20273 - 9266     # pangenome Pfams NOT in PDB
n_both      = 9266
fig, ax = plt.subplots(figsize=(7, 5))
labels = ["PDB Pfams\nnot in pangenome", "Pangenome Pfams\nnot in PDB",
          "Pangenome Pfams\nwith PDB structure"]
sizes  = [n_pdb_only, n_bakta_only, n_both]
colors = ["#7570b3", "#d95f02", "#1b9e77"]
ax.bar(labels, sizes, color=colors)
for i, v in enumerate(sizes):
    ax.text(i, v + 100, f"{v:,}", ha="center", fontsize=10)
ax.set_ylabel("Distinct Pfam IDs")
ax.set_title("Pfam universe: PDB ∩ environmental pangenome")
fig.tight_layout()
fig.savefig(f"{FIG}/NB03_pfam_universe.png", bbox_inches="tight")
plt.close(fig)

# ============================================================================
# Final printouts for report
# ============================================================================
print("\n=== FIGURES SAVED ===")
for f in sorted(os.listdir(FIG)):
    print(f"  {FIG}/{f}")

print("\n=== SUMMARY WITH ENRICHMENTS ===")
print(summary[["biome", "n_clusters_total", "pct_no_pfam", "pct_pfam_all_covered",
               "log2_no_pfam_enrichment", "fisher_q_bh_no_pfam"]]
      .round({"pct_no_pfam": 2, "pct_pfam_all_covered": 2,
              "log2_no_pfam_enrichment": 3, "fisher_q_bh_no_pfam": 4}).to_string(index=False))

print("\n=== Chi-square tests (see glm_out above) ===")
