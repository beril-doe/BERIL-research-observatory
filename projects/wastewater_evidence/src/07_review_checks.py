"""Verify the independent review's claims and recompute what needs correcting.

REVIEW_1.md raised five corrections affecting stated numbers. This script checks each
against the recorded outputs and produces the replacement figures, plus the counts the
review flagged as untraceable to any run.

Outputs ($BERIL_RUN_DIR):
  chk_subtype_denominator.csv   finding 10: which denominator subtype_assignment.csv uses
  chk_gold_industrial.csv       finding 6: composition of unsupported GOLD industrial records
  chk_holdout_overlap.csv       finding 7: hold-out with doubly-labelled accessions removed
  chk_holdout_by_group.csv      finding 7: no-native recall split by external subtype
  chk_screen_basis.csv          finding 8: which support leg carries each accepted term
  chk_screen_envo_dropped.csv   finding 8: accept count if env_* terms lose the ENVO leg
  chk_field_population.csv      finding 4: how many records populate each field
  chk_aviary_fields.csv         finding 6: which BioSample field actually holds 'aviary'
  chk_study_clustering.csv      scope: BioProject concentration of the no-signal cohort
  chk_digest_package.csv        finding 5: package counts for the digest substring vs subset
"""
import glob
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from berdl_spark import get_spark, run_dir  # noqa: E402

PROJ = Path(__file__).resolve().parent.parent
out = run_dir()
T0 = time.time()
FIELDS = ["isolation_source", "env_medium", "env_local_scale", "env_broad_scale", "taxonomy_name"]


def latest(p):
    return sorted(glob.glob(str(PROJ / p)))[-1]


def save(df, name):
    df.to_csv(out / name, index=False)
    print(f"[{time.time()-T0:5.0f}s] {name}: {len(df)} rows", flush=True)


def chunked_view(spark, df, name, ch=1000):
    df = df.astype(object).where(df.notna(), None)
    rows = [tuple(r) for r in df.itertuples(index=False)]
    parts = []
    for i in range(0, len(rows), ch):
        p = f"{name}_c{i // ch}"
        spark.createDataFrame(rows[i:i + ch], schema=list(df.columns)).createOrReplaceTempView(p)
        parts.append(p)
    spark.sql(f"CACHE TABLE {name} AS " + " UNION ALL ".join(f"SELECT * FROM {p}" for p in parts))


# ---- 1. finding 10: subtype denominator ----
sa = pd.read_csv(latest("runs/*-transfer-validate/out/subtype_assignment.csv"))
typed = sa[sa.subtype != "unspecified"].n_acc.sum()
unspec = sa[sa.subtype == "unspecified"].n_acc.sum()
save(pd.DataFrame([{
    "typed_records": int(typed), "unspecified_records": int(unspec),
    "denominator_in_file": int(typed + unspec),
    "native_only_denominator": 601863,
    "pct_typed_correct": round(100 * typed / (typed + unspec), 1),
    "pct_typed_as_reported": round(100 * (1 - unspec / 601863), 1),
}]), "chk_subtype_denominator.csv")

# ---- 2. finding 6: GOLD industrial composition ----
lab = pd.read_parquet(latest("runs/*-external-vs-biosample/out/labelled_samples.parquet"))
found = lab[lab.found == 1]
gi = found[(found.source == "GOLD") & (found.ext_subtype == "industrial_ww")]
gi_ns = gi[gi.any_signal == 0]
save(gi_ns.ext_label.value_counts().reset_index().rename(columns={"index": "ext_label", "count": "n"}),
     "chk_gold_industrial.csv")
print(f"  GOLD industrial: {len(gi)} found, {len(gi_ns)} with no signal", flush=True)

# ---- 3. finding 7: hold-out with overlap removed ----
acc_src = found.groupby("accession").source.agg(set)
both_gm = {a for a, s in acc_src.items() if {"GOLD", "MGnify"} <= s}
print(f"  accessions labelled by both GOLD and MGnify: {len(both_gm)}", flush=True)

terms_g = pd.read_csv(latest("runs/*-transfer-validate/out/term_table_gold_only.csv"))
terms_m = pd.read_csv(latest("runs/*-transfer-validate/out/term_table_mgnify_only.csv"))


def apply_terms(df, terms):
    hit = pd.Series(False, index=df.index)
    for f in FIELDS:
        vals = set(terms[terms.field == f].value)
        if vals:
            hit |= df[f].astype(str).str.lower().str.strip().isin(vals)
    return hit


rows, grp_rows = [], []
for train, test, tt in [("GOLD", "MGnify", terms_g), ("MGnify", "GOLD", terms_m)]:
    te_all = found[found.source == test]
    te_cl = te_all[~te_all.accession.isin(both_gm)]
    for tag, te in [("as reported", te_all), ("overlap excluded", te_cl)]:
        hit = apply_terms(te, tt)
        ns = te.any_signal == 0
        rows.append({"trained_on": train, "tested_on": test, "cohort": tag, "n_test": len(te),
                     "pct_recovered": round(100 * hit.mean(), 1),
                     "n_no_native": int(ns.sum()),
                     "pct_recovered_no_native": round(100 * hit[ns].mean(), 1) if ns.any() else None})
    # split the no-native denominator by external subtype
    ns_te = te_cl[te_cl.any_signal == 0]
    hit_ns = apply_terms(ns_te, tt)
    for st, idx in ns_te.groupby("ext_subtype").groups.items():
        grp_rows.append({"trained_on": train, "tested_on": test, "ext_subtype": st,
                         "n_no_native": len(idx), "pct_recovered": round(100 * hit_ns.loc[idx].mean(), 1)})
save(pd.DataFrame(rows), "chk_holdout_overlap.csv")
save(pd.DataFrame(grp_rows).sort_values(["tested_on", "n_no_native"], ascending=[True, False]),
     "chk_holdout_by_group.csv")

# ---- 4. finding 8: which leg carries each accepted term ----
sc = pd.read_csv(latest("runs/*-term-screen/out/term_screen.csv"))
ok = sc[sc.verdict == "accept"].copy()
ok["pkg_ok"] = ok.support_pkg >= 0.10
ok["envo_ok"] = ok.support_envo >= 0.10
ok["proj_ok"] = (ok.support_proj >= 0.10) & (ok.field != "taxonomy_name")
ok["is_env_field"] = ok.field.str.startswith("env_")


def basis(r):
    legs = [n for n, v in [("pkg", r.pkg_ok), ("envo", r.envo_ok), ("proj", r.proj_ok)] if v]
    return "+".join(legs) if legs else "none"


ok["basis"] = ok.apply(basis, axis=1)
save(ok.groupby(["basis", "is_env_field"]).agg(n_terms=("value", "size"), n_records=("n_records", "sum"))
     .reset_index().sort_values("n_terms", ascending=False), "chk_screen_basis.csv")
print(f"  accepted on package alone: {int((ok.basis=='pkg').sum())}; "
      f"ENVO alone: {int((ok.basis=='envo').sum())} "
      f"(env_* fields: {int(((ok.basis=='envo') & ok.is_env_field).sum())}); "
      f"project alone: {int((ok.basis=='proj').sum())}", flush=True)

# counterfactual: env_* terms screened on package and project only
alt = sc.copy()
env_mask = alt.field.str.startswith("env_")
alt["alt_support"] = alt[["support_pkg", "support_envo", "support_proj"]].max(axis=1)
alt.loc[env_mask, "alt_support"] = alt.loc[env_mask, ["support_pkg", "support_proj"]].max(axis=1)
alt.loc[alt.field == "taxonomy_name", "alt_support"] = alt.loc[alt.field == "taxonomy_name",
                                                               ["support_pkg", "support_envo"]].max(axis=1)
alt["alt_verdict"] = (alt.alt_support >= 0.10).map({True: "accept", False: "reject"})
save(pd.crosstab(alt.verdict, alt.alt_verdict).reset_index(), "chk_screen_envo_dropped.csv")
lost = alt[(alt.verdict == "accept") & (alt.alt_verdict == "reject")]
print(f"  dropping the ENVO leg for env_* terms loses {len(lost)} accepts "
      f"({int(lost.n_records.sum())} records)", flush=True)

# ---- Spark-side checks ----
spark = get_spark("ww-review-checks")

save(spark.sql("""
SELECT harmonized_name, unique_biosamples_count, unique_bioprojects_count
FROM nmdc.ncbi_biosamples.harmonized_name_usage_stats
WHERE harmonized_name IN ('isolation_source','env_broad_scale','env_medium','env_local_scale',
                          'sample_type','source_name','project_name','host','env_package','samp_mat_process')
ORDER BY unique_biosamples_count DESC
""").toPandas(), "chk_field_population.csv")

save(spark.sql("""
SELECT 'env_broad_scale' AS field, COUNT(*) AS n FROM nmdc.ncbi_biosamples.biosamples_flattened
  WHERE lower(trim(env_broad_scale))='aviary'
UNION ALL SELECT 'env_local_scale', COUNT(*) FROM nmdc.ncbi_biosamples.biosamples_flattened
  WHERE lower(trim(env_local_scale))='aviary'
UNION ALL SELECT 'env_medium', COUNT(*) FROM nmdc.ncbi_biosamples.biosamples_flattened
  WHERE lower(trim(env_medium))='aviary'
UNION ALL SELECT 'isolation_source', COUNT(*) FROM nmdc.ncbi_biosamples.biosamples_flattened
  WHERE lower(trim(isolation_source))='aviary'
""").toPandas(), "chk_aviary_fields.csv")

ns_all = found[found.any_signal == 0][["accession", "source", "ext_subtype"]]
chunked_view(spark, ns_all, "nosig")
save(spark.sql("""
SELECT n.source, n.ext_subtype, COUNT(DISTINCT n.accession) AS n_samples,
       COUNT(DISTINCT s.bioproject_accession) AS n_bioprojects,
       MAX(pc.c) AS largest_project_samples
FROM nosig n LEFT JOIN nmdc.ncbi_biosamples.sra_biosamples_bioprojects s
  ON s.biosample_accession = n.accession
LEFT JOIN (SELECT s2.bioproject_accession AS p, COUNT(DISTINCT s2.biosample_accession) AS c
           FROM nmdc.ncbi_biosamples.sra_biosamples_bioprojects s2
           JOIN nosig n2 ON n2.accession = s2.biosample_accession
           GROUP BY s2.bioproject_accession) pc ON pc.p = s.bioproject_accession
GROUP BY n.source, n.ext_subtype ORDER BY n_samples DESC
""").toPandas(), "chk_study_clustering.csv")

sb = pd.read_csv(latest("runs/*-biosample-evidence/out/subtype_by_field.csv"))
save(sb[(sb.field == "env_broad_scale") & sb.subtype.isin(["trap_digest_substring", "trap_digestive"])],
     "chk_digest_package.csv")
print("done", flush=True)
