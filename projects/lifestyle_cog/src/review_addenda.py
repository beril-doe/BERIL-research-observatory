"""Post-hoc analyses requested by REVIEW.md.

Computes:
1. Rank-biserial effect sizes from existing Mann-Whitney U statistics (review #5)
2. BH correction across all phylum x COG within-phylum tests (review #7)
3. Log-ratio re-formulation of enrichment scores as sensitivity check (review #2)

Reads from data/, writes to data/review_addenda/.

Inputs are the CSVs already saved by NB02/NB03; no Spark required.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "review_addenda"
OUT.mkdir(exist_ok=True)


def rank_biserial_from_stats() -> pd.DataFrame:
    """Compute rank-biserial r = 1 - 2U/(n1*n2) for each COG.

    The U statistic in cog_lifestyle_stats.csv is the host-vs-free
    Mann-Whitney U (alternative='two-sided'). Rank-biserial >0 means
    host enrichment scores tend to be higher than free.
    """
    df = pd.read_csv(DATA / "cog_lifestyle_stats.csv")
    df["rank_biserial"] = 1.0 - 2.0 * df["U_statistic"] / (df["n_host"] * df["n_free"])
    # Cliff's delta is identical to rank-biserial for two-group rank tests
    df["cliffs_delta"] = df["rank_biserial"]
    df["effect_size_abs"] = df["rank_biserial"].abs()
    df["effect_size_class"] = pd.cut(
        df["effect_size_abs"],
        bins=[-0.01, 0.147, 0.33, 0.474, 1.01],
        labels=["negligible", "small", "medium", "large"],
    )
    df = df.sort_values("effect_size_abs", ascending=False).reset_index(drop=True)
    out_path = OUT / "effect_sizes.csv"
    df.to_csv(out_path, index=False)
    return df


def phylum_bh_correction() -> pd.DataFrame:
    """Recompute the within-phylum Mann-Whitney tests with BH correction.

    NB03 cell 5 ran phylum x COG tests but did not BH-correct across the
    ~120 tests. We need to recompute them since NB03 didn't save them.
    """
    enrich = pd.read_csv(DATA / "cog_enrichment_by_lifestyle.csv")
    target_cogs = ["V", "L", "E", "G", "C", "P", "I", "J", "M", "K", "T"]
    records = []
    for phy, phy_df in enrich.groupby("phylum"):
        host_count = phy_df[phy_df["species_lifestyle"] == "host_associated"][
            "gtdb_species_clade_id"
        ].nunique()
        free_count = phy_df[phy_df["species_lifestyle"] == "free_living"][
            "gtdb_species_clade_id"
        ].nunique()
        if host_count < 5 or free_count < 5:
            continue
        for cog in target_cogs:
            sub = phy_df[phy_df["COG_category"] == cog]
            host = sub[sub["species_lifestyle"] == "host_associated"][
                "enrichment_score"
            ].dropna()
            free = sub[sub["species_lifestyle"] == "free_living"][
                "enrichment_score"
            ].dropna()
            if len(host) < 5 or len(free) < 5:
                continue
            u, p = stats.mannwhitneyu(host, free, alternative="two-sided")
            records.append(
                {
                    "phylum": phy,
                    "COG_category": cog,
                    "n_host": len(host),
                    "n_free": len(free),
                    "median_host": float(host.median()),
                    "median_free": float(free.median()),
                    "diff_median": float(host.median() - free.median()),
                    "U": float(u),
                    "p_value": float(p),
                }
            )
    df = pd.DataFrame(records)
    df["p_bh"] = stats.false_discovery_control(df["p_value"].to_numpy(), method="bh")
    df["sig_uncorrected"] = df["p_value"] < 0.05
    df["sig_bh"] = df["p_bh"] < 0.05
    df = df.sort_values("p_bh").reset_index(drop=True)
    df.to_csv(OUT / "phylum_within_bh.csv", index=False)
    return df


def log_ratio_sensitivity() -> pd.DataFrame:
    """Recompute enrichment with log2((acc+eps)/(core+eps)) and rerun tests.

    Compare with the original (acc - core) / (core + 1e-4) formula.
    Use eps = 1e-3 to dampen low-coverage distortion.
    """
    df = pd.read_csv(DATA / "cog_enrichment_by_lifestyle.csv")
    eps = 1e-3
    df["enrichment_log2"] = np.log2(
        (df["prop_accessory"] + eps) / (df["prop_core"] + eps)
    )
    records = []
    for cog, sub in df.groupby("COG_category"):
        host = sub[sub["species_lifestyle"] == "host_associated"][
            "enrichment_log2"
        ].dropna()
        free = sub[sub["species_lifestyle"] == "free_living"][
            "enrichment_log2"
        ].dropna()
        if len(host) < 5 or len(free) < 5:
            continue
        u, p = stats.mannwhitneyu(host, free, alternative="two-sided")
        r = 1.0 - 2.0 * float(u) / (len(host) * len(free))
        records.append(
            {
                "COG_category": cog,
                "n_host": int(len(host)),
                "n_free": int(len(free)),
                "median_host_log2": float(host.median()),
                "median_free_log2": float(free.median()),
                "diff_median_log2": float(host.median() - free.median()),
                "U": float(u),
                "p_value": float(p),
                "rank_biserial": r,
            }
        )
    out = pd.DataFrame(records)
    out["p_bh"] = stats.false_discovery_control(out["p_value"].to_numpy(), method="bh")
    out = out.sort_values("p_bh").reset_index(drop=True)

    # Compare with original direction
    orig = pd.read_csv(DATA / "cog_lifestyle_stats.csv")[
        ["COG_category", "diff_median", "p_adjusted"]
    ].rename(columns={"diff_median": "diff_orig", "p_adjusted": "p_bh_orig"})
    out = out.merge(orig, on="COG_category", how="left")
    out["sign_preserved"] = (out["diff_median_log2"] > 0) == (out["diff_orig"] > 0)
    out["both_sig"] = (out["p_bh"] < 0.05) & (out["p_bh_orig"] < 0.05)
    out.to_csv(OUT / "log_ratio_sensitivity.csv", index=False)
    return out


def main() -> None:
    print("=== Rank-biserial effect sizes (review #5) ===")
    eff = rank_biserial_from_stats()
    print(eff[
        [
            "COG_category",
            "description",
            "rank_biserial",
            "effect_size_class",
            "p_adjusted",
        ]
    ].head(24).to_string(index=False))

    print("\n=== Phylum-stratified tests with BH correction (review #7) ===")
    ph = phylum_bh_correction()
    print(f"Total within-phylum tests: {len(ph)}")
    print(f"Significant uncorrected (p<0.05): {ph['sig_uncorrected'].sum()}")
    print(f"Significant after BH (q<0.05): {ph['sig_bh'].sum()}")
    print("\nTop 10 by p_bh:")
    print(
        ph[
            ["phylum", "COG_category", "diff_median", "p_value", "p_bh", "sig_bh"]
        ].head(10).to_string(index=False)
    )
    print("\nCampylobacterota H3 / target rows:")
    targets = ph[ph["COG_category"].isin(["V", "E", "G", "I", "P"])]
    print(targets[
        ["phylum", "COG_category", "diff_median", "p_value", "p_bh", "sig_bh"]
    ].to_string(index=False))

    print("\n=== Log-ratio sensitivity check (review #2) ===")
    lr = log_ratio_sensitivity()
    print(f"Categories tested: {len(lr)}")
    print(f"Sign preserved (vs original): {lr['sign_preserved'].sum()}/{len(lr)}")
    print(f"Both significant after BH: {lr['both_sig'].sum()}/{len(lr)}")
    print("\nKey categories:")
    key = lr[lr["COG_category"].isin(["V", "L", "E", "G", "C", "P", "I", "A", "S"])]
    print(
        key[
            [
                "COG_category",
                "diff_median_log2",
                "diff_orig",
                "rank_biserial",
                "p_bh",
                "p_bh_orig",
                "sign_preserved",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
