"""NCBI BioSample: which structured and free-text evidence marks wastewater?

Reads nmdc.ncbi_biosamples.* and kbase.ontology_source.* via Spark Connect.
All outputs are aggregates (no per-sample dumps) written to $BERIL_RUN_DIR:

  envo_terms.csv              wastewater-related ENVO terms (seeds + subclass closure)
  envo_evidence_by_term.csv   accessions per ENVO term x env attribute, top raw strings
  package_counts.csv          accessions per wastewater-related BioSample package
  taxonomy_counts.csv         accessions per wastewater-like metagenome taxonomy_name
  keyword_by_field.csv        per text field: keyword hits, and overlap with package/ENVO/taxon
  subtype_by_field.csv        per text field x subtype regex: hits, package overlap, traps
  evidence_crosstab.csv       PKG x ENVO x TAX x KW agreement over all 51.7M records
  kw_only_examples.csv        most common field values among KW-only (no structured) hits
"""
# %%
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from berdl_spark import get_spark, run_dir  # noqa: E402

spark = get_spark("ww-biosample-evidence")
out = run_dir()
T0 = time.time()


def save(df, name):
    pdf = df.toPandas()
    pdf.to_csv(out / name, index=False)
    print(f"[{time.time()-T0:6.0f}s] {name}: {len(pdf)} rows", flush=True)
    return pdf


# %% 1. ENVO term set: seeds by id + label pattern, then subclass closure (descendants)
SEED_LABEL_RE = (r"waste ?water|sewage|sludge|biosolid|anaerobic digest|digester|digestor|sewer|"
                 r"effluent|influent|septic|wastewater")
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW envo_seed AS
SELECT DISTINCT subject AS id FROM kbase.ontology_source.statements
WHERE predicate='rdfs:label' AND subject LIKE 'ENVO:%' AND lower(value) RLIKE '{SEED_LABEL_RE}'
  AND NOT lower(value) RLIKE 'digestive|oil sludge|marine sludge'
""")
spark.sql("""
CREATE OR REPLACE TEMP VIEW envo_ww AS
SELECT id, 'seed' AS how FROM envo_seed
UNION
SELECT e.subject AS id, 'descendant' AS how
FROM kbase.ontology_source.entailed_edge e JOIN envo_seed s ON e.object = s.id
WHERE e.predicate='rdfs:subClassOf' AND e.subject LIKE 'ENVO:%'
""")
spark.sql("""
CREATE OR REPLACE TEMP VIEW envo_ww_lab AS
SELECT w.id, min(w.how) AS how, max(l.value) AS label
FROM envo_ww w LEFT JOIN kbase.ontology_source.statements l
  ON l.subject = w.id AND l.predicate='rdfs:label'
GROUP BY w.id
""")
save(spark.sql("SELECT * FROM envo_ww_lab ORDER BY how, id"), "envo_terms.csv")

# %% 2. ENVO evidence in BioSample env triads
spark.sql("""
CREATE OR REPLACE TEMP VIEW envo_hits AS
SELECT t.accession, t.attribute, t.id, t.raw_original
FROM nmdc.ncbi_biosamples.env_triads_flattened t JOIN envo_ww w ON t.id = w.id
""")
save(spark.sql("""
WITH agg AS (
  SELECT id, attribute, COUNT(DISTINCT accession) AS n_acc FROM envo_hits GROUP BY id, attribute),
raws AS (
  SELECT id, attribute, raw_original, COUNT(*) AS n,
         ROW_NUMBER() OVER (PARTITION BY id, attribute ORDER BY COUNT(*) DESC) AS rk
  FROM envo_hits GROUP BY id, attribute, raw_original)
SELECT a.id, l.label, a.attribute, a.n_acc,
       concat_ws(' | ', collect_list(concat(r.raw_original, ' (', r.n, ')'))) AS top_raw
FROM agg a JOIN envo_ww_lab l ON a.id=l.id
LEFT JOIN raws r ON r.id=a.id AND r.attribute=a.attribute AND r.rk<=4
GROUP BY a.id, l.label, a.attribute, a.n_acc ORDER BY n_acc DESC
"""), "envo_evidence_by_term.csv")

# %% 3. Packages and taxonomy names
spark.sql("""
CREATE OR REPLACE TEMP VIEW ww_pkg AS
SELECT name FROM nmdc.ncbi_biosamples.ncbi_packages_flattened
WHERE lower(name) LIKE '%wastewater%' OR lower(name) LIKE '%wwsurv%' OR lower(env_package) LIKE '%waste%'
""")
save(spark.sql("""
SELECT b.package_content, COUNT(*) AS n_acc
FROM nmdc.ncbi_biosamples.biosamples_flattened b
WHERE lower(b.package_content) LIKE '%wastewater%' OR lower(b.package_content) LIKE '%wwsurv%'
   OR lower(b.package_content) LIKE '%sludge%'
GROUP BY b.package_content ORDER BY n_acc DESC
"""), "package_counts.csv")

TAX_RE = r"waste ?water|sewage|sludge|digester|bioreactor|biofilter|biogas|sewer|effluent|influent|septic|biosolid"
save(spark.sql(f"""
SELECT taxonomy_name, taxonomy_id, COUNT(*) AS n_acc,
       SUM(CASE WHEN lower(package_content) RLIKE 'wastewater|wwsurv' THEN 1 ELSE 0 END) AS n_in_ww_pkg
FROM nmdc.ncbi_biosamples.biosamples_flattened
WHERE lower(taxonomy_name) RLIKE '{TAX_RE}'
GROUP BY taxonomy_name, taxonomy_id ORDER BY n_acc DESC
"""), "taxonomy_counts.csv")

# %% 4. Per-record evidence flags over the whole table
# Regexes come from ww_flags (word-bounded, SQL-escaped). The first run of this
# script (runs/20261017T011707Z-biosample-evidence) used unbounded patterns and
# so counted e.g. Bordetella bronchi*septic*a and *sewer*zowii as hits.
from ww_flags import KW_RE_SQL as KW_RE, TAX_STRICT_RE_SQL as TAX_STRICT_RE, SUBTYPE_RE_SQL, sql_re  # noqa: E402

TEXT_FIELDS = ["isolation_source", "env_broad_scale", "env_local_scale", "env_medium", "sample_type",
               "source_name", "description_title", "description_comment", "description", "project_name",
               "study_name", "samp_mat_process", "sample_name", "organism_name", "taxonomy_name",
               "env_package", "host"]
kw_cols = ",\n  ".join(f"CASE WHEN lower({c}) RLIKE '{KW_RE}' THEN 1 ELSE 0 END AS kw_{c}" for c in TEXT_FIELDS)
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW flags AS
SELECT b.accession,
  CASE WHEN lower(b.package_content) RLIKE 'wastewater|wwsurv' THEN 1 ELSE 0 END AS pkg,
  CASE WHEN e.accession IS NOT NULL THEN 1 ELSE 0 END AS envo,
  CASE WHEN lower(b.taxonomy_name) RLIKE '{TAX_STRICT_RE}' THEN 1 ELSE 0 END AS tax,
  {kw_cols}
FROM nmdc.ncbi_biosamples.biosamples_flattened b
LEFT JOIN (SELECT DISTINCT accession FROM envo_hits) e ON e.accession = b.accession
""")
kw_any = " + ".join(f"kw_{c}" for c in TEXT_FIELDS if c not in ("taxonomy_name", "organism_name"))
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW flags2 AS
SELECT *, CASE WHEN ({kw_any}) > 0 THEN 1 ELSE 0 END AS kw FROM flags
""")
spark.sql("CACHE TABLE flags2")

save(spark.sql("""
SELECT pkg, envo, tax, kw, COUNT(*) AS n_acc FROM flags2 GROUP BY pkg, envo, tax, kw ORDER BY n_acc DESC
"""), "evidence_crosstab.csv")

# per-field keyword hits and how often a structured signal co-occurs
rows = []
for c in TEXT_FIELDS:
    rows.append(f"""SELECT '{c}' AS field, SUM(kw_{c}) AS n_hits,
      SUM(kw_{c}*pkg) AS n_with_pkg, SUM(kw_{c}*envo) AS n_with_envo, SUM(kw_{c}*tax) AS n_with_tax,
      SUM(kw_{c}*(CASE WHEN pkg+envo+tax>0 THEN 1 ELSE 0 END)) AS n_with_any_structured,
      SUM(kw_{c}*(CASE WHEN pkg+envo+tax=0 THEN 1 ELSE 0 END)) AS n_kw_only
      FROM flags2""")
save(spark.sql(" UNION ALL ".join(rows) + " ORDER BY n_hits DESC"), "keyword_by_field.csv")

# %% 5. Subtype regexes per field, with trap counters
SUBTYPES = dict(SUBTYPE_RE_SQL)
SUBTYPES.update({
    "trap_digest_substring": r"digest",
    "trap_undigested": r"undigested",
    "trap_digestive": r"digestive|digestion of|in vitro digest|gastric",
    "trap_septic_unbounded": r"septic",
    "trap_septic_bounded": sql_re(r"\bseptic\b"),
    "trap_sewer_unbounded": r"sewer",
    "trap_sewer_bounded": sql_re(r"\bsewers?\b"),
    "trap_effluent_medical": sql_re(r"(dialysis|peritoneal|hematoma|wound|bronchoalveolar)[^.]{0,40}\beffluent"),
})
rows = []
for c in TEXT_FIELDS:
    for st, rx in SUBTYPES.items():
        rows.append(f"""SELECT '{c}' AS field, '{st}' AS subtype,
          SUM(CASE WHEN lower({c}) RLIKE '{rx}' THEN 1 ELSE 0 END) AS n_hits,
          SUM(CASE WHEN lower({c}) RLIKE '{rx}' AND lower(package_content) RLIKE 'wastewater|wwsurv' THEN 1 ELSE 0 END) AS n_with_pkg
          FROM nmdc.ncbi_biosamples.biosamples_flattened""")
save(spark.sql(" UNION ALL ".join(rows) + " ORDER BY subtype, n_hits DESC"), "subtype_by_field.csv")

# %% 6. What do KW-only records look like? Top values per field (bounded)
rows = []
for c in ["isolation_source", "env_medium", "env_local_scale", "env_broad_scale", "sample_type", "source_name", "taxonomy_name", "package_content"]:
    rows.append(f"""(SELECT '{c}' AS field, lower(b.{c}) AS value, COUNT(*) AS n
       FROM nmdc.ncbi_biosamples.biosamples_flattened b JOIN flags2 f ON f.accession=b.accession
       WHERE f.kw=1 AND f.pkg=0 AND f.envo=0 AND f.tax=0
       GROUP BY lower(b.{c}) ORDER BY n DESC LIMIT 40)""")
save(spark.sql(" UNION ALL ".join(rows)), "kw_only_examples.csv")

# %% 7. And the reverse: structured-positive but no keyword anywhere — what text do they carry?
rows = []
for c in ["isolation_source", "env_medium", "env_local_scale", "env_broad_scale", "sample_type", "taxonomy_name", "package_content"]:
    rows.append(f"""(SELECT '{c}' AS field, lower(b.{c}) AS value, COUNT(*) AS n
       FROM nmdc.ncbi_biosamples.biosamples_flattened b JOIN flags2 f ON f.accession=b.accession
       WHERE f.kw=0 AND (f.pkg=1 OR f.envo=1)
       GROUP BY lower(b.{c}) ORDER BY n DESC LIMIT 40)""")
save(spark.sql(" UNION ALL ".join(rows)), "structured_only_examples.csv")
print("done", flush=True)
