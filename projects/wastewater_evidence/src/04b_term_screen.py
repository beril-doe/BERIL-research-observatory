"""Screen transferred terms against independent BioSample evidence, without hand labels.

Why
---
`04_transfer_validate.py` mines vocabulary from externally labelled samples and keeps
terms that are rare in BioSample at large (high lift) and point to one subtype (high
purity). Both filters pass for vocabulary inherited from a *mislabelled* external
group: a biome that wrongly contains duck-cecum samples yields terms that are rare,
pure, and wrong. Purity inside a homogeneous cluster says nothing about whether the
cluster was labelled correctly.

The screen
----------
For every candidate term, look at all BioSample records that carry it and ask how often
they independently show wastewater evidence that does **not** come from the same text:

  support_pkg   submitter chose a wastewater BioSample package
  support_envo  the record's env triad was annotated with a wastewater ENVO term
  support_proj  the record's BioProject also contains package-flagged samples

Terms from the free-text environment fields are screened on all three. Terms from
`taxonomy_name` are screened on package and ENVO only (BioProject support is weak for
a taxon that spans whole studies). No hand labels are used anywhere.

Outputs ($BERIL_RUN_DIR):
  term_screen.csv         every term with its independent-support rates and verdict
  screen_effect.csv       records recovered before and after screening, by channel overlap
  screen_examples.csv     top values among records recovered by the screened table alone
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
MIN_SUPPORT = 0.10     # at least this fraction of the term's records must show independent evidence


def log(m):
    print(f"[{time.time()-T0:6.0f}s] {m}", flush=True)


def save(df, name):
    df.to_csv(out / name, index=False)
    log(f"{name}: {len(df)} rows")


def chunked_view(spark, df, name, ch=1000):
    df = df.astype(object).where(df.notna(), None)
    rows = [tuple(r) for r in df.itertuples(index=False)]
    parts = []
    for i in range(0, len(rows), ch):
        p = f"{name}_c{i // ch}"
        spark.createDataFrame(rows[i:i + ch], schema=list(df.columns)).createOrReplaceTempView(p)
        parts.append(p)
    spark.sql(f"CACHE TABLE {name} AS " + " UNION ALL ".join(f"SELECT * FROM {p}" for p in parts))


spark = get_spark("ww-screen")
for s in envo_views_sql():
    spark.sql(s)

terms = pd.read_csv(sorted(glob.glob(str(PROJ / "runs/*-transfer-validate/out/term_table.csv")))[-1])
log(f"terms to screen: {len(terms)}")
chunked_view(spark, terms[["field", "value", "ext_subtype"]], "terms")

# per-record channels, independent of the free-text fields where possible
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW base AS
SELECT b.accession, b.isolation_source, b.env_medium, b.env_local_scale, b.env_broad_scale, b.taxonomy_name,
  CASE WHEN lower(b.package_content) RLIKE '{PKG_RE}' THEN 1 ELSE 0 END AS pkg,
  CASE WHEN e.accession IS NOT NULL THEN 1 ELSE 0 END AS envo,
  CASE WHEN lower(b.taxonomy_name) RLIKE '{TAX_STRICT_RE_SQL}' THEN 1 ELSE 0 END AS tax,
  CASE WHEN lower(concat_ws(' ', b.isolation_source, b.env_broad_scale, b.env_local_scale, b.env_medium,
       b.sample_type, b.description_title, b.description_comment, b.project_name, b.env_package, b.host))
       RLIKE '{KW_RE_SQL}' THEN 1 ELSE 0 END AS kw
FROM nmdc.ncbi_biosamples.biosamples_flattened b LEFT JOIN envo_hits e ON e.accession = b.accession
""")
spark.sql("CACHE TABLE basec AS SELECT * FROM base")

# BioProjects that contain at least one wastewater-package sample
spark.sql("""
CACHE TABLE ww_projects AS
SELECT DISTINCT s.bioproject_accession AS proj
FROM nmdc.ncbi_biosamples.sra_biosamples_bioprojects s JOIN basec c ON c.accession = s.biosample_accession
WHERE c.pkg = 1
""")
spark.sql("""
CACHE TABLE acc_proj AS
SELECT s.biosample_accession AS accession, MAX(CASE WHEN p.proj IS NOT NULL THEN 1 ELSE 0 END) AS in_ww_project
FROM nmdc.ncbi_biosamples.sra_biosamples_bioprojects s LEFT JOIN ww_projects p ON p.proj = s.bioproject_accession
GROUP BY s.biosample_accession
""")

join_terms = " OR ".join(f"(t.field='{f}' AND lower(trim(b.{f})) = t.value)" for f in FIELDS)
screen = spark.sql(f"""
SELECT t.field, t.value, t.ext_subtype,
       COUNT(*) AS n_records,
       AVG(CAST(b.pkg AS DOUBLE)) AS support_pkg,
       AVG(CAST(b.envo AS DOUBLE)) AS support_envo,
       AVG(CAST(COALESCE(p.in_ww_project, 0) AS DOUBLE)) AS support_proj,
       AVG(CAST(b.tax AS DOUBLE)) AS rate_tax,
       AVG(CAST(b.kw AS DOUBLE)) AS rate_kw
FROM terms t JOIN basec b ON {join_terms}
LEFT JOIN acc_proj p ON p.accession = b.accession
GROUP BY t.field, t.value, t.ext_subtype
""").toPandas()
log(f"screened {len(screen)} terms over BioSample")

screen["independent_support"] = screen[["support_pkg", "support_envo"]].max(axis=1)
# taxonomy terms span whole studies, so BioProject co-membership is not independent evidence for them
mask_txt = screen.field != "taxonomy_name"
screen.loc[mask_txt, "independent_support"] = screen.loc[mask_txt, ["support_pkg", "support_envo", "support_proj"]].max(axis=1)
screen["verdict"] = (screen.independent_support >= MIN_SUPPORT).map({True: "accept", False: "reject"})
screen = screen.sort_values(["verdict", "n_records"], ascending=[True, False])
save(screen, "term_screen.csv")
log(f"accepted {int((screen.verdict=='accept').sum())} / rejected {int((screen.verdict=='reject').sum())} terms")

acc = screen[screen.verdict == "accept"][["field", "value", "ext_subtype"]]
chunked_view(spark, acc, "terms_ok")
join_ok = " OR ".join(f"(t.field='{f}' AND lower(trim(b.{f})) = t.value)" for f in FIELDS)
spark.sql(f"""
CACHE TABLE hits_ok AS
SELECT DISTINCT b.accession FROM basec b JOIN terms_ok t ON {join_ok}
""")
spark.sql(f"""
CACHE TABLE hits_all AS
SELECT DISTINCT b.accession FROM basec b JOIN terms t ON {join_terms}
""")
save(spark.sql("""
SELECT CASE WHEN ha.accession IS NULL THEN 0 ELSE 1 END AS term_unscreened,
       CASE WHEN ho.accession IS NULL THEN 0 ELSE 1 END AS term_screened,
       CASE WHEN b.pkg+b.envo+b.tax+b.kw > 0 THEN 1 ELSE 0 END AS any_native,
       COUNT(*) AS n_acc
FROM basec b LEFT JOIN hits_all ha ON ha.accession=b.accession LEFT JOIN hits_ok ho ON ho.accession=b.accession
GROUP BY 1,2,3 ORDER BY n_acc DESC
""").toPandas(), "screen_effect.csv")

rows = []
for f in ["isolation_source", "env_medium", "taxonomy_name", "package_content"]:
    rows.append(f"""(SELECT '{f}' AS field, lower(b2.{f}) AS value, COUNT(*) AS n
      FROM nmdc.ncbi_biosamples.biosamples_flattened b2 JOIN basec b ON b.accession=b2.accession
      JOIN hits_ok ho ON ho.accession=b.accession
      WHERE b.pkg=0 AND b.envo=0 AND b.tax=0 AND b.kw=0
      GROUP BY lower(b2.{f}) ORDER BY n DESC LIMIT 20)""")
save(spark.sql(" UNION ALL ".join(rows)).toPandas(), "screen_examples.csv")
print("done", flush=True)
