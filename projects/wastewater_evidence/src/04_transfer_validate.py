"""Transfer wastewater labels from strong-signal systems to BioSample, and validate without hand labels.

Construction
------------
1. Mine candidate terms from externally labelled samples (GOLD paths, MGnify biomes):
   for each (field, value) seen on labelled samples, compute enrichment against the
   background frequency of that exact value across all 51.7M BioSample records
   (`content_pairs_aggregated` for harmonized attributes, a direct count for taxonomy_name).
   Keep terms that are both enriched and subtype-pure.
2. Hold-out transfer: build the table from GOLD only, apply to MGnify-labelled samples
   (and the reverse). Neither source saw the other's vocabulary.
3. Apply the combined table to all of BioSample and compare with the four native channels.

Validation without hand labels
------------------------------
a. Cross-source hold-out (above): does vocabulary learned in one system recover the
   other system's samples?
b. BioProject coherence: samples in a BioProject are usually one study of one matrix.
   A good flag is near-0 or near-1 within a project; mass in the middle means the rule
   fires inconsistently. The wastewater *package* channel gives the reference curve.
c. Trap set: records matching near-miss wording (digestive tract, dialysis effluent,
   septicaemia organisms, undigested sludge feedstock) must stay unflagged.

Outputs ($BERIL_RUN_DIR):
  term_table.csv, term_table_gold_only.csv, term_table_mgnify_only.csv
  holdout_transfer.csv        cross-source recall of the held-out source's samples
  applied_channel_compare.csv transferred flag vs package / ENVO / taxon / keyword over all BioSample
  applied_new_examples.csv    records the term table finds that no native channel flags
  bioproject_coherence.csv    binned within-project flagged fraction, per channel
  trap_check.csv              near-miss wording: how many the term table flags
  subtype_assignment.csv      subtype counts from the term table, over all BioSample
"""
# %%
import glob
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from berdl_spark import get_spark, run_dir  # noqa: E402
from ww_flags import KW_RE_SQL, PKG_RE, SUBTYPE_RE, TAX_STRICT_RE_SQL, envo_views_sql, sql_re  # noqa: E402

PROJ = Path(__file__).resolve().parent.parent
out = run_dir()
T0 = time.time()
N_BIOSAMPLE = 51_711_888          # nmdc.ncbi_biosamples.biosamples_flattened, run 20261017T011209Z-schemas
HARMONIZED = ["isolation_source", "env_medium", "env_local_scale", "env_broad_scale"]
FIELDS = HARMONIZED + ["taxonomy_name"]
MIN_COUNT = 3                     # a term must be seen on at least this many labelled samples
MIN_LIFT = 50.0                   # ... and be this much commoner among them than in BioSample at large
MIN_PURITY = 0.70                 # ... and point to one subtype this consistently


def log(m):
    print(f"[{time.time()-T0:6.0f}s] {m}", flush=True)


def save(df, name):
    df.to_csv(out / name, index=False)
    log(f"{name}: {len(df)} rows")


def chunked_view(spark, df, name, ch=1000):
    """Spark Connect ingress rejects one large local relation (HTTP 413); send it in pieces."""
    df = df.astype(object).where(df.notna(), None)
    rows = [tuple(r) for r in df.itertuples(index=False)]
    parts = []
    for i in range(0, len(rows), ch):
        p = f"{name}_c{i // ch}"
        spark.createDataFrame(rows[i:i + ch], schema=list(df.columns)).createOrReplaceTempView(p)
        parts.append(p)
    spark.sql(f"CACHE TABLE {name} AS " + " UNION ALL ".join(f"SELECT * FROM {p}" for p in parts))


spark = get_spark("ww-transfer")
for s in envo_views_sql():
    spark.sql(s)

lab = pd.read_parquet(sorted(glob.glob(str(PROJ / "runs/*-external-vs-biosample/out/labelled_samples.parquet")))[-1])
lab = lab[lab.found == 1].copy()
log(f"labelled samples: {len(lab)} ({lab.source.value_counts().to_dict()})")

# %% ---- candidate (field, value) pairs from labelled samples ----
cand = []
for f in FIELDS:
    v = lab[["source", "ext_subtype", f]].copy()
    v["value"] = v[f].astype(str).str.lower().str.strip()
    v = v[~v.value.isin(["", "nan", "none", "missing", "not applicable", "not collected", "na", "-", "unknown"])]
    v["field"] = f
    cand.append(v[["source", "ext_subtype", "field", "value"]])
cand = pd.concat(cand, ignore_index=True)
log(f"candidate rows: {len(cand)}, distinct (field,value): {cand.groupby(['field','value']).ngroups}")

# %% ---- background frequency of each candidate value across all of BioSample ----
pairs = cand[["field", "value"]].drop_duplicates()
chunked_view(spark, pairs, "cand_pairs")
bg_h = spark.sql("""
SELECT p.field, p.value, SUM(c.biosample_count) AS bg_count
FROM cand_pairs p JOIN nmdc.ncbi_biosamples.content_pairs_aggregated c
  ON c.harmonized_name = p.field AND lower(trim(c.content)) = p.value
WHERE p.field <> 'taxonomy_name'
GROUP BY p.field, p.value
""").toPandas()
bg_t = spark.sql("""
SELECT 'taxonomy_name' AS field, lower(trim(b.taxonomy_name)) AS value, COUNT(*) AS bg_count
FROM nmdc.ncbi_biosamples.biosamples_flattened b
JOIN (SELECT value FROM cand_pairs WHERE field='taxonomy_name') p
  ON lower(trim(b.taxonomy_name)) = p.value
GROUP BY lower(trim(b.taxonomy_name))
""").toPandas()
bg = pd.concat([bg_h, bg_t], ignore_index=True)
log(f"background counts resolved for {len(bg)} of {len(pairs)} (field,value) pairs")


def build_terms(sub: pd.DataFrame, n_samples: int, tag: str) -> pd.DataFrame:
    c = sub.groupby(["field", "value", "ext_subtype"]).size().reset_index(name="n")
    tot = c.groupby(["field", "value"])["n"].sum().reset_index(name="n_total")
    top = c.sort_values("n", ascending=False).drop_duplicates(["field", "value"])
    t = top.merge(tot, on=["field", "value"]).merge(bg, on=["field", "value"], how="left")
    t["purity"] = t["n"] / t["n_total"]
    t["bg_count"] = t["bg_count"].fillna(t["n_total"])          # unseen in background: assume all occurrences are ours
    # share of labelled samples carrying this value, against its share of all BioSample records
    t["lift"] = (t["n_total"] / n_samples) / (t["bg_count"] / N_BIOSAMPLE)
    keep = t[(t.n_total >= MIN_COUNT) & (t.lift >= MIN_LIFT) & (t.purity >= MIN_PURITY)].copy()
    keep["built_from"] = tag
    return keep.sort_values(["field", "n_total"], ascending=[True, False])[
        ["field", "value", "ext_subtype", "n_total", "bg_count", "lift", "purity", "built_from"]]


terms_all = build_terms(cand, lab.accession.nunique(), "GOLD+MGnify+NMDC")
terms_gold = build_terms(cand[cand.source == "GOLD"],
                         lab[lab.source == "GOLD"].accession.nunique(), "GOLD")
terms_mg = build_terms(cand[cand.source == "MGnify"],
                       lab[lab.source == "MGnify"].accession.nunique(), "MGnify")
save(terms_all, "term_table.csv")
save(terms_gold, "term_table_gold_only.csv")
save(terms_mg, "term_table_mgnify_only.csv")

# %% ---- (a) cross-source hold-out ----
def apply_terms(df: pd.DataFrame, terms: pd.DataFrame) -> pd.Series:
    hit = pd.Series(False, index=df.index)
    for f in FIELDS:
        tf = terms[terms.field == f]
        if tf.empty:
            continue
        vals = set(tf.value)
        hit |= df[f].astype(str).str.lower().str.strip().isin(vals)
    return hit


rows = []
for train, test in [("GOLD", "MGnify"), ("MGnify", "GOLD")]:
    tt = {"GOLD": terms_gold, "MGnify": terms_mg}[train]
    te = lab[lab.source == test]
    hit = apply_terms(te, tt)
    rows.append({"trained_on": train, "tested_on": test, "n_test": len(te),
                 "n_terms": len(tt), "pct_recovered": round(100 * hit.mean(), 1),
                 "pct_recovered_among_no_native_signal": round(
                     100 * hit[te.any_signal == 0].mean(), 1) if (te.any_signal == 0).any() else None,
                 "n_no_native_signal": int((te.any_signal == 0).sum())})
save(pd.DataFrame(rows), "holdout_transfer.csv")

# %% ---- apply the combined table to all of BioSample ----
chunked_view(spark, terms_all[["field", "value", "ext_subtype"]], "terms")
subtype_case = "CASE " + " ".join(
    f"WHEN lower(concat_ws(' ', b.isolation_source, b.env_medium, b.env_local_scale, b.env_broad_scale, b.description_title, b.taxonomy_name)) RLIKE '{sql_re(rx)}' THEN '{st}'"
    for st, rx in SUBTYPE_RE.items() if st != "sludge_generic") + " WHEN lower(concat_ws(' ', b.isolation_source, b.env_medium, b.env_local_scale, b.env_broad_scale, b.description_title, b.taxonomy_name)) RLIKE '" + sql_re(SUBTYPE_RE['sludge_generic']) + "' THEN 'sludge_generic' ELSE 'unspecified' END"

join_terms = " OR ".join(
    f"(t.field='{f}' AND lower(trim(b.{f})) = t.value)" for f in FIELDS)
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW term_hits AS
SELECT DISTINCT b.accession, t.ext_subtype AS term_subtype
FROM nmdc.ncbi_biosamples.biosamples_flattened b JOIN terms t ON {join_terms}
""")
spark.sql("CACHE TABLE term_hits_c AS SELECT accession, min(term_subtype) AS term_subtype FROM term_hits GROUP BY accession")
log(f"term-table hits over all BioSample: {spark.sql('SELECT COUNT(*) n FROM term_hits_c').toPandas()['n'].iloc[0]:,}")

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW chan AS
SELECT b.accession,
  CASE WHEN lower(b.package_content) RLIKE '{PKG_RE}' THEN 1 ELSE 0 END AS pkg,
  CASE WHEN e.accession IS NOT NULL THEN 1 ELSE 0 END AS envo,
  CASE WHEN lower(b.taxonomy_name) RLIKE '{TAX_STRICT_RE_SQL}' THEN 1 ELSE 0 END AS tax,
  CASE WHEN lower(concat_ws(' ', b.isolation_source, b.env_broad_scale, b.env_local_scale, b.env_medium,
                            b.sample_type, b.description_title, b.description_comment, b.project_name,
                            b.env_package, b.host)) RLIKE '{KW_RE_SQL}' THEN 1 ELSE 0 END AS kw,
  CASE WHEN h.accession IS NOT NULL THEN 1 ELSE 0 END AS term,
  {subtype_case} AS subtype
FROM nmdc.ncbi_biosamples.biosamples_flattened b
LEFT JOIN envo_hits e ON e.accession = b.accession
LEFT JOIN term_hits_c h ON h.accession = b.accession
""")
spark.sql("CACHE TABLE chanc AS SELECT * FROM chan")
save(spark.sql("SELECT pkg, envo, tax, kw, term, COUNT(*) AS n_acc FROM chanc GROUP BY pkg, envo, tax, kw, term ORDER BY n_acc DESC").toPandas(),
     "applied_channel_compare.csv")
save(spark.sql("""
SELECT c.subtype, c.term, COUNT(*) AS n_acc
FROM chanc c WHERE c.pkg+c.envo+c.tax+c.kw+c.term > 0 GROUP BY c.subtype, c.term ORDER BY n_acc DESC
""").toPandas(), "subtype_assignment.csv")

# what does the term table find that nothing native flags?
rows = []
for f in ["isolation_source", "env_medium", "env_broad_scale", "taxonomy_name", "package_content", "description_title"]:
    rows.append(f"""(SELECT '{f}' AS field, lower(b.{f}) AS value, COUNT(*) AS n
      FROM nmdc.ncbi_biosamples.biosamples_flattened b JOIN chanc c ON c.accession=b.accession
      WHERE c.term=1 AND c.pkg=0 AND c.envo=0 AND c.tax=0 AND c.kw=0
      GROUP BY lower(b.{f}) ORDER BY n DESC LIMIT 25)""")
save(spark.sql(" UNION ALL ".join(rows)).toPandas(), "applied_new_examples.csv")

# %% ---- (b) BioProject coherence ----
coh = spark.sql("""
WITH proj AS (
  SELECT s.bioproject_accession AS proj, c.accession, c.pkg, c.term, c.kw
  FROM nmdc.ncbi_biosamples.sra_biosamples_bioprojects s JOIN chanc c ON c.accession = s.biosample_accession),
agg AS (
  SELECT proj, COUNT(*) AS n,
         AVG(CAST(pkg AS DOUBLE)) AS f_pkg, AVG(CAST(term AS DOUBLE)) AS f_term, AVG(CAST(kw AS DOUBLE)) AS f_kw,
         MAX(pkg) AS any_pkg, MAX(term) AS any_term, MAX(kw) AS any_kw
  FROM proj GROUP BY proj)
SELECT channel, bin, COUNT(*) AS n_projects, SUM(n) AS n_samples FROM (
  SELECT 'package' AS channel, FLOOR(LEAST(f_pkg,0.999)*5)/5 AS bin, n FROM agg WHERE any_pkg=1 AND n>=5
  UNION ALL SELECT 'term_table', FLOOR(LEAST(f_term,0.999)*5)/5, n FROM agg WHERE any_term=1 AND n>=5
  UNION ALL SELECT 'keyword', FLOOR(LEAST(f_kw,0.999)*5)/5, n FROM agg WHERE any_kw=1 AND n>=5
) GROUP BY channel, bin ORDER BY channel, bin
""").toPandas()
save(coh, "bioproject_coherence.csv")

# %% ---- (c) trap set ----
TRAPS = {
    "digestive_tract": r"digestive (tract|system)|gastrointestinal|gastric|in vitro digest",
    "undigested_feedstock": r"undigested",
    "dialysis_effluent": r"(dialysis|peritoneal|hematoma|wound) [a-z ]{0,20}effluent",
    "septicaemia_organism": r"bronchiseptica|meningoseptica|septicum|atroseptica|gallisepticum|anguilliseptica",
    "river_discharge": r"river discharge|discharge (rate|volume)|glacial discharge",
}
rows = []
for name, rx in TRAPS.items():
    rows.append(f"""SELECT '{name}' AS trap,
      COUNT(*) AS n_matching,
      SUM(c.term) AS n_flagged_by_terms, SUM(c.kw) AS n_flagged_by_keyword,
      SUM(c.pkg) AS n_in_ww_package, SUM(c.envo) AS n_with_envo
    FROM nmdc.ncbi_biosamples.biosamples_flattened b JOIN chanc c ON c.accession=b.accession
    WHERE lower(concat_ws(' ', b.isolation_source, b.env_medium, b.env_local_scale, b.env_broad_scale,
          b.description_title, b.taxonomy_name, b.organism_name)) RLIKE '{sql_re(rx)}'""")
save(spark.sql(" UNION ALL ".join(rows)).toPandas(), "trap_check.csv")
print("done", flush=True)
