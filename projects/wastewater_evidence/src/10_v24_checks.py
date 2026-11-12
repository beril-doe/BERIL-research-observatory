"""Computation for the v2.4 edits (REVIEW_3 suggestions 1, 2, 6 and 7).

  suggestion 2  the true study-level overlap residual, excluding the 589 accessions
                that carry both a GOLD and an MGnify label (each of which trivially
                shares a BioProject with itself, inflating the earlier figure).
  suggestion 1  which accepted term actually carries the 1,283 `Gallus gallus`
                records that survive screening. REVIEW_3 could not identify it.
  suggestion 6  the real composition of the MGnify cohort the 94-term table is
                mined from, instead of "mostly activated sludge and nutrient removal".
  suggestion 7  a three-class breakdown of the unscreened no-native gain, by where
                each term's labelled carriers come from and whether the screen keeps it.

Outputs ($BERIL_RUN_DIR):
  v24_overlap_residual.csv    overlap before and after excluding the doubly-labelled
  v24_gallus_carrier.csv      the accepted term(s) matching the chicken records
  v24_mgnify_composition.csv  MGnify labelled cohort by group, with shares
  v24_gain_classes.csv        unscreened no-native records by term class and verdict
  v24_gain_class_totals.csv   the same rolled up to the three classes
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


spark = get_spark("ww-v24")
for s in envo_views_sql():
    spark.sql(s)

lab = pd.read_parquet(latest("runs/*-external-vs-biosample/out/labelled_samples.parquet"))
found = lab[lab.found == 1]
src_sets = found.groupby("accession").source.agg(set)
both_gm = {a for a, s in src_sets.items() if {"GOLD", "MGnify"} <= s}
print(f"  doubly-labelled (GOLD and MGnify): {len(both_gm)}", flush=True)

# ---- suggestion 2: true residual overlap ----
chunked_view(spark, found[["accession", "source"]].drop_duplicates(), "labsrc")
chunked_view(spark, pd.DataFrame({"accession": sorted(both_gm)}), "dual")
ov = spark.sql("""
WITH ap AS (
  SELECT l.accession, l.source, s.bioproject_accession AS proj
  FROM labsrc l JOIN nmdc.ncbi_biosamples.sra_biosamples_bioprojects s
    ON s.biosample_accession = l.accession),
-- projects reached by each source through accessions that are NOT doubly labelled
gold_proj AS (SELECT DISTINCT proj FROM ap WHERE source='GOLD'
              AND accession NOT IN (SELECT accession FROM dual)),
mg_proj AS (SELECT DISTINCT proj FROM ap WHERE source='MGnify'
            AND accession NOT IN (SELECT accession FROM dual)),
gold_proj_all AS (SELECT DISTINCT proj FROM ap WHERE source='GOLD'),
mg_proj_all AS (SELECT DISTINCT proj FROM ap WHERE source='MGnify')
SELECT 'MGnify, as first reported (includes doubly-labelled)' AS measure,
       COUNT(DISTINCT ap.accession) AS n FROM ap JOIN gold_proj_all g ON g.proj=ap.proj
  WHERE ap.source='MGnify'
UNION ALL SELECT 'GOLD, as first reported (includes doubly-labelled)',
       COUNT(DISTINCT ap.accession) FROM ap JOIN mg_proj_all m ON m.proj=ap.proj
  WHERE ap.source='GOLD'
UNION ALL SELECT 'MGnify test accessions sharing a BioProject with a GOLD-only accession',
       COUNT(DISTINCT ap.accession) FROM ap JOIN gold_proj g ON g.proj=ap.proj
  WHERE ap.source='MGnify' AND ap.accession NOT IN (SELECT accession FROM dual)
UNION ALL SELECT 'GOLD test accessions sharing a BioProject with an MGnify-only accession',
       COUNT(DISTINCT ap.accession) FROM ap JOIN mg_proj m ON m.proj=ap.proj
  WHERE ap.source='GOLD' AND ap.accession NOT IN (SELECT accession FROM dual)
UNION ALL SELECT 'doubly-labelled accessions with any BioProject link',
       COUNT(DISTINCT ap.accession) FROM ap WHERE ap.accession IN (SELECT accession FROM dual)
""").toPandas()
save(ov, "v24_overlap_residual.csv")
print(ov.to_string(index=False), flush=True)

# ---- rebuild channels and term hits ----
terms_all = pd.read_csv(latest("runs/*-transfer-validate/out/term_table.csv"))
screen = pd.read_csv(latest("runs/*-term-screen/out/term_screen.csv"))
chunked_view(spark, terms_all[["field", "value", "ext_subtype"]], "terms")
join_terms = " OR ".join(f"(t.field='{f}' AND lower(trim(b.{f})) = t.value)" for f in FIELDS)
spark.sql(f"""
CACHE TABLE base AS
SELECT b.accession, b.taxonomy_name,
  CASE WHEN lower(b.package_content) RLIKE '{PKG_RE}' THEN 1 ELSE 0 END AS pkg,
  CASE WHEN e.accession IS NOT NULL THEN 1 ELSE 0 END AS envo,
  CASE WHEN lower(b.taxonomy_name) RLIKE '{TAX_STRICT_RE_SQL}' THEN 1 ELSE 0 END AS tax,
  CASE WHEN lower(concat_ws(' ', b.isolation_source, b.env_broad_scale, b.env_local_scale, b.env_medium,
       b.sample_type, b.description_title, b.description_comment, b.project_name, b.env_package, b.host))
       RLIKE '{KW_RE_SQL}' THEN 1 ELSE 0 END AS kw
FROM nmdc.ncbi_biosamples.biosamples_flattened b LEFT JOIN envo_hits e ON e.accession = b.accession
""")
spark.sql(f"""
CACHE TABLE hit_term AS
SELECT DISTINCT b2.accession, t.field AS term_field, t.value AS term_value
FROM nmdc.ncbi_biosamples.biosamples_flattened b2 JOIN terms t ON {join_terms.replace('b.', 'b2.')}
""")

# ---- suggestion 1: which accepted term carries the Gallus gallus records ----
acc_terms = screen[screen.verdict == "accept"][["field", "value"]]
chunked_view(spark, acc_terms, "terms_ok")
gal = spark.sql("""
SELECT h.term_field, h.term_value, COUNT(DISTINCT h.accession) AS n_gallus_records
FROM base b JOIN hit_term h ON h.accession = b.accession
JOIN terms_ok o ON o.field = h.term_field AND o.value = h.term_value
WHERE lower(trim(b.taxonomy_name)) = 'gallus gallus'
  AND b.pkg = 0 AND b.envo = 0 AND b.tax = 0 AND b.kw = 0
GROUP BY h.term_field, h.term_value ORDER BY n_gallus_records DESC
""").toPandas()
save(gal, "v24_gallus_carrier.csv")
print(gal.to_string(index=False), flush=True)

# ---- suggestion 6: MGnify cohort composition ----
mg = found[found.source == "MGnify"]
comp = (mg.ext_subtype.value_counts().rename_axis("ext_subtype").reset_index(name="n"))
comp["pct_of_mgnify_cohort"] = (100 * comp.n / len(mg)).round(1)
save(comp, "v24_mgnify_composition.csv")
print(comp.to_string(index=False), flush=True)

# ---- suggestion 7: three-class breakdown of the unscreened no-native gain ----
# dominant source of each term's labelled carriers
rows = []
for f in FIELDS:
    v = found[["accession", "source", f]].copy()
    v["value"] = v[f].astype(str).str.lower().str.strip()
    v["field"] = f
    rows.append(v[["accession", "source", "field", "value"]])
carriers = pd.concat(rows, ignore_index=True).merge(
    terms_all[["field", "value"]].drop_duplicates(), on=["field", "value"])
dom = (carriers.groupby(["field", "value", "source"]).accession.nunique()
       .reset_index(name="n").sort_values("n", ascending=False)
       .drop_duplicates(["field", "value"]).rename(columns={"source": "dominant_source"}))
tmeta = (terms_all[["field", "value", "ext_subtype"]]
         .merge(dom[["field", "value", "dominant_source"]], on=["field", "value"], how="left")
         .merge(screen[["field", "value", "verdict", "independent_support"]], on=["field", "value"], how="left"))
DISPUTED = {"agricultural_ww", "industrial_ww"}
tmeta["term_class"] = [
    "1: idiom from a disputed MGnify group" if (r.dominant_source == "MGnify" and r.ext_subtype in DISPUTED)
    else ("3: term the screen keeps" if r.verdict == "accept" else "2: other term the screen rejects")
    for r in tmeta.itertuples()]
chunked_view(spark, tmeta[["field", "value", "term_class", "verdict"]], "tclass")
gain = spark.sql("""
SELECT c.term_class, c.verdict, COUNT(DISTINCT b.accession) AS n_records
FROM base b JOIN hit_term h ON h.accession = b.accession
JOIN tclass c ON c.field = h.term_field AND c.value = h.term_value
WHERE b.pkg = 0 AND b.envo = 0 AND b.tax = 0 AND b.kw = 0
GROUP BY c.term_class, c.verdict ORDER BY n_records DESC
""").toPandas()
save(gain, "v24_gain_classes.csv")
# records attributable to each class alone (a record can carry several terms)
solo = spark.sql("""
WITH r AS (
  SELECT b.accession, collect_set(c.term_class) AS classes
  FROM base b JOIN hit_term h ON h.accession = b.accession
  JOIN tclass c ON c.field = h.term_field AND c.value = h.term_value
  WHERE b.pkg = 0 AND b.envo = 0 AND b.tax = 0 AND b.kw = 0
  GROUP BY b.accession)
SELECT CASE WHEN size(classes) = 1 THEN classes[0] ELSE 'multiple classes' END AS class_resolved,
       COUNT(*) AS n_records FROM r GROUP BY 1 ORDER BY n_records DESC
""").toPandas()
save(solo, "v24_gain_class_totals.csv")
print(gain.to_string(index=False), flush=True)
print(solo.to_string(index=False), flush=True)
print("done", flush=True)
