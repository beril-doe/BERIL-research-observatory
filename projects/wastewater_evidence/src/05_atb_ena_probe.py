"""Bonus sources: AllTheBacteria biosample_environment and ENA metadata.

Aggregates only, to $BERIL_RUN_DIR:
  atb_context_label_counts.csv   AllTheBacteria `context_label` for samples with/without ww wording
  atb_ww_field_values.csv        top values of env fields among ww-keyword isolates
  ena_checklist_counts.csv       ENA checklist among ww-keyword samples vs all
  ena_ww_field_hits.csv          per ENA field: ww keyword hits
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from berdl_spark import get_spark, run_dir  # noqa: E402
from ww_flags import KW_RE_SQL as KW_RE  # noqa: E402  (SQL-escaped: \\b word boundaries)

spark = get_spark("ww-atb-ena")
out = run_dir()
T0 = time.time()


def save(q, name):
    pdf = spark.sql(q).toPandas()
    pdf.to_csv(out / name, index=False)
    print(f"[{time.time()-T0:5.0f}s] {name}: {len(pdf)} rows", flush=True)


ATB_TXT = ["isolation_source", "env_broad_scale", "env_local_scale", "env_medium", "env_package", "context_label"]
atb_kw = " OR ".join(f"lower({c}) RLIKE '{KW_RE}'" for c in ATB_TXT if c != "context_label")
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW atb AS
SELECT *, CASE WHEN {atb_kw} THEN 1 ELSE 0 END AS kw FROM refdata.all_the_bacteria.biosample_environment
""")
save("""SELECT context_label, kw, COUNT(*) n FROM atb GROUP BY context_label, kw ORDER BY n DESC LIMIT 200""",
     "atb_context_label_counts.csv")
rows = []
for c in ["isolation_source", "env_broad_scale", "env_local_scale", "env_medium", "env_package", "context_label"]:
    rows.append(f"(SELECT '{c}' AS field, lower({c}) AS value, COUNT(*) n FROM atb WHERE kw=1 GROUP BY lower({c}) ORDER BY n DESC LIMIT 30)")
save(" UNION ALL ".join(rows), "atb_ww_field_values.csv")
save("SELECT kw, COUNT(*) n, COUNT(DISTINCT biosample_accession) n_acc FROM atb GROUP BY kw", "atb_totals.csv")

ENA_TXT = ["isolation_source", "environment_biome", "environment_feature", "environment_material", "sample_description",
           "sample_title", "study_title", "environmental_medium", "local_environmental_context",
           "broad_scale_environmental_context", "description", "sample_material", "bio_material"]
ena_kw = " OR ".join(f"lower({c}) RLIKE '{KW_RE}'" for c in ENA_TXT)
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW ena AS
SELECT checklist, environmental_sample, library_source, {', '.join(ENA_TXT)},
       CASE WHEN {ena_kw} THEN 1 ELSE 0 END AS kw
FROM refdata.all_the_bacteria.ena_metadata
""")
save("SELECT checklist, kw, COUNT(*) n FROM ena GROUP BY checklist, kw ORDER BY n DESC LIMIT 100", "ena_checklist_counts.csv")
rows = [f"SELECT '{c}' AS field, SUM(CASE WHEN lower({c}) RLIKE '{KW_RE}' THEN 1 ELSE 0 END) n_hits, SUM(CASE WHEN {c} IS NOT NULL AND {c} <> '' THEN 1 ELSE 0 END) n_nonnull FROM ena" for c in ENA_TXT]
save(" UNION ALL ".join(rows) + " ORDER BY n_hits DESC", "ena_ww_field_hits.csv")
print("done", flush=True)
