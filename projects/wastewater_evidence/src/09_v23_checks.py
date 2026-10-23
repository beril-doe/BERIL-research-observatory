"""Computation needed for the v2.3 edits (REVIEW_2 suggestions 1, 6 and 9).

  suggestion 1  BioProject coherence with the *flagged* sample count, not just the
                size of the binned projects, plus the base each percentage is of.
  suggestion 6  how much study-level overlap the accession-level hold-out exclusion
                leaves: test accessions sharing a BioProject with a training accession.
  suggestion 9  whether the two known lift distortions change which terms pass the
                lift >= 50 / purity >= 0.70 / n >= 3 filter.

Outputs ($BERIL_RUN_DIR):
  v23_coherence_flagged.csv   per channel and bin: projects, samples, flagged samples
  v23_coherence_base.csv      per channel: the denominator each share is taken over
  v23_study_overlap.csv       accession- vs BioProject-level overlap between the two sources
  v23_lift_recheck.csv        terms whose accept/reject flips under the corrected lift
  v23_lift_unresolved.csv     the candidate values with no background frequency
"""
import glob
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from berdl_spark import get_spark, run_dir  # noqa: E402
from ww_flags import KW_RE_SQL, PKG_RE, TAX_STRICT_RE_SQL, envo_views_sql  # noqa: E402

PROJ = Path(__file__).resolve().parent.parent
out = run_dir()
T0 = time.time()
N_BIOSAMPLE = 51_711_888
FIELDS = ["isolation_source", "env_medium", "env_local_scale", "env_broad_scale", "taxonomy_name"]
MIN_COUNT, MIN_LIFT, MIN_PURITY = 3, 50.0, 0.70


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


spark = get_spark("ww-v23")
for s in envo_views_sql():
    spark.sql(s)

# ---- rebuild the per-record channel flags and the term hits (same logic as 04) ----
terms_all = pd.read_csv(latest("runs/*-transfer-validate/out/term_table.csv"))
chunked_view(spark, terms_all[["field", "value", "ext_subtype"]], "terms")
join_terms = " OR ".join(f"(t.field='{f}' AND lower(trim(b.{f})) = t.value)" for f in FIELDS)
spark.sql(f"""
CACHE TABLE term_hits_c AS
SELECT DISTINCT b.accession FROM nmdc.ncbi_biosamples.biosamples_flattened b JOIN terms t ON {join_terms}
""")
spark.sql(f"""
CACHE TABLE chanc AS
SELECT b.accession,
  CASE WHEN lower(b.package_content) RLIKE '{PKG_RE}' THEN 1 ELSE 0 END AS pkg,
  CASE WHEN e.accession IS NOT NULL THEN 1 ELSE 0 END AS envo,
  CASE WHEN lower(b.taxonomy_name) RLIKE '{TAX_STRICT_RE_SQL}' THEN 1 ELSE 0 END AS tax,
  CASE WHEN lower(concat_ws(' ', b.isolation_source, b.env_broad_scale, b.env_local_scale, b.env_medium,
       b.sample_type, b.description_title, b.description_comment, b.project_name, b.env_package, b.host))
       RLIKE '{KW_RE_SQL}' THEN 1 ELSE 0 END AS kw,
  CASE WHEN h.accession IS NOT NULL THEN 1 ELSE 0 END AS term
FROM nmdc.ncbi_biosamples.biosamples_flattened b
LEFT JOIN envo_hits e ON e.accession = b.accession
LEFT JOIN term_hits_c h ON h.accession = b.accession
""")

# ---- suggestion 1: coherence with flagged counts ----
spark.sql("""
CACHE TABLE agg AS
SELECT s.bioproject_accession AS proj, COUNT(*) AS n,
       AVG(CAST(c.pkg AS DOUBLE)) AS f_pkg, AVG(CAST(c.term AS DOUBLE)) AS f_term,
       AVG(CAST(c.kw AS DOUBLE)) AS f_kw,
       SUM(c.pkg) AS s_pkg, SUM(c.term) AS s_term, SUM(c.kw) AS s_kw,
       MAX(c.pkg) AS any_pkg, MAX(c.term) AS any_term, MAX(c.kw) AS any_kw
FROM nmdc.ncbi_biosamples.sra_biosamples_bioprojects s JOIN chanc c ON c.accession = s.biosample_accession
GROUP BY s.bioproject_accession
""")
coh = spark.sql("""
SELECT channel, bin, COUNT(*) AS n_projects,
       SUM(n) AS samples_in_projects, SUM(flagged) AS flagged_samples
FROM (
  SELECT 'package' AS channel, FLOOR(LEAST(f_pkg,0.999)*5)/5 AS bin, n, s_pkg AS flagged FROM agg WHERE any_pkg=1 AND n>=5
  UNION ALL SELECT 'term_table', FLOOR(LEAST(f_term,0.999)*5)/5, n, s_term FROM agg WHERE any_term=1 AND n>=5
  UNION ALL SELECT 'keyword', FLOOR(LEAST(f_kw,0.999)*5)/5, n, s_kw FROM agg WHERE any_kw=1 AND n>=5
) GROUP BY channel, bin ORDER BY channel, bin
""").toPandas()
save(coh, "v23_coherence_flagged.csv")

base = coh.groupby("channel").agg(total_projects=("n_projects", "sum"),
                                  total_samples_in_projects=("samples_in_projects", "sum"),
                                  total_flagged=("flagged_samples", "sum")).reset_index()
top = coh[coh.bin >= 0.8].groupby("channel").agg(top_projects=("n_projects", "sum"),
                                                 top_samples=("samples_in_projects", "sum"),
                                                 top_flagged=("flagged_samples", "sum")).reset_index()
base = base.merge(top, on="channel")
base["pct_samples_in_top_projects"] = (100 * base.top_samples / base.total_samples_in_projects).round(1)
base["pct_flagged_in_top_projects"] = (100 * base.top_flagged / base.total_flagged).round(1)
save(base, "v23_coherence_base.csv")
print(base.to_string(index=False), flush=True)

# ---- suggestion 6: study-level overlap left by accession-level exclusion ----
lab = pd.read_parquet(latest("runs/*-external-vs-biosample/out/labelled_samples.parquet"))
found = lab[lab.found == 1]
chunked_view(spark, found[["accession", "source"]].drop_duplicates(), "labsrc")
ov = spark.sql("""
WITH ap AS (
  SELECT l.accession, l.source, s.bioproject_accession AS proj
  FROM labsrc l JOIN nmdc.ncbi_biosamples.sra_biosamples_bioprojects s
    ON s.biosample_accession = l.accession),
gold_proj AS (SELECT DISTINCT proj FROM ap WHERE source='GOLD'),
mg_proj   AS (SELECT DISTINCT proj FROM ap WHERE source='MGnify')
SELECT 'MGnify test accessions sharing a BioProject with GOLD' AS relation,
       COUNT(DISTINCT ap.accession) AS n
FROM ap JOIN gold_proj g ON g.proj = ap.proj WHERE ap.source='MGnify'
UNION ALL
SELECT 'GOLD test accessions sharing a BioProject with MGnify', COUNT(DISTINCT ap.accession)
FROM ap JOIN mg_proj m ON m.proj = ap.proj WHERE ap.source='GOLD'
""").toPandas()
both = found.groupby("accession").source.agg(set)
both_gm = {a for a, s in both.items() if {"GOLD", "MGnify"} <= s}
ov = pd.concat([pd.DataFrame([{"relation": "accessions labelled by both GOLD and MGnify",
                               "n": len(both_gm)}]), ov], ignore_index=True)
save(ov, "v23_study_overlap.csv")
print(ov.to_string(index=False), flush=True)

# ---- suggestion 9: do the lift distortions change any accept? ----
cand = []
for f in FIELDS:
    v = found[["accession", "source", "ext_subtype", f]].copy()
    v["value"] = v[f].astype(str).str.lower().str.strip()
    v = v[~v.value.isin(["", "nan", "none", "missing", "not applicable", "not collected", "na", "-", "unknown"])]
    v["field"] = f
    cand.append(v[["accession", "source", "ext_subtype", "field", "value"]])
cand = pd.concat(cand, ignore_index=True)

pairs = cand[["field", "value"]].drop_duplicates()
chunked_view(spark, pairs, "cand_pairs")
bg_h = spark.sql("""
SELECT p.field, p.value, SUM(c.biosample_count) AS bg_count
FROM cand_pairs p JOIN nmdc.ncbi_biosamples.content_pairs_aggregated c
  ON c.harmonized_name = p.field AND lower(trim(c.content)) = p.value
WHERE p.field <> 'taxonomy_name' GROUP BY p.field, p.value
""").toPandas()
bg_t = spark.sql("""
SELECT 'taxonomy_name' AS field, lower(trim(b.taxonomy_name)) AS value, COUNT(*) AS bg_count
FROM nmdc.ncbi_biosamples.biosamples_flattened b
JOIN (SELECT value FROM cand_pairs WHERE field='taxonomy_name') p ON lower(trim(b.taxonomy_name)) = p.value
GROUP BY lower(trim(b.taxonomy_name))
""").toPandas()
bg = pd.concat([bg_h, bg_t], ignore_index=True)

n_samples = found.accession.nunique()
# as built: numerator counts label ROWS
rows_n = cand.groupby(["field", "value"]).size().reset_index(name="n_rows")
# corrected: numerator counts distinct ACCESSIONS
acc_n = cand.groupby(["field", "value"]).accession.nunique().reset_index(name="n_acc")
pur = (cand.groupby(["field", "value", "ext_subtype"]).size().reset_index(name="n")
       .sort_values("n", ascending=False).drop_duplicates(["field", "value"]))
t = (rows_n.merge(acc_n, on=["field", "value"]).merge(bg, on=["field", "value"], how="left")
     .merge(pur[["field", "value", "ext_subtype", "n"]], on=["field", "value"]))
t["purity"] = t["n"] / t["n_rows"]
t["unresolved_background"] = t.bg_count.isna()
t["bg_as_built"] = t.bg_count.fillna(t.n_rows)
t["lift_as_built"] = (t.n_rows / n_samples) / (t.bg_as_built / N_BIOSAMPLE)
# corrected: accession numerator; unresolved values excluded rather than given max lift
t["lift_corrected"] = (t.n_acc / n_samples) / (t.bg_count / N_BIOSAMPLE)

t["pass_as_built"] = (t.n_rows >= MIN_COUNT) & (t.lift_as_built >= MIN_LIFT) & (t.purity >= MIN_PURITY)
t["pass_corrected"] = (t.n_acc >= MIN_COUNT) & (t.lift_corrected >= MIN_LIFT) & (t.purity >= MIN_PURITY)
flip = t[t.pass_as_built != t.pass_corrected]
save(flip[["field", "value", "ext_subtype", "n_rows", "n_acc", "bg_count", "unresolved_background",
           "lift_as_built", "lift_corrected", "purity", "pass_as_built", "pass_corrected"]]
     .sort_values("n_rows", ascending=False), "v23_lift_recheck.csv")
save(t[t.unresolved_background][["field", "value", "ext_subtype", "n_rows", "n_acc", "purity"]],
     "v23_lift_unresolved.csv")
print(f"  terms passing as built: {int(t.pass_as_built.sum())}; corrected: {int(t.pass_corrected.sum())}; "
      f"flips: {len(flip)} ({int(flip.pass_as_built.sum())} lost, {int(flip.pass_corrected.sum())} gained)",
      flush=True)
print("done", flush=True)
