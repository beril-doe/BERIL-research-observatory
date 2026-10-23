"""Re-derive the numbers the v2.2 edits touch, from the recorded run outputs.

Covers:
  edit 3  which BioSample field holds 'water trough', 'duck cecum' and 'aviary'
          for the MGnify agricultural_ww samples
  edit 6a the '38% riverine metagenome' share for MGnify's industrial_ww group
  edit 6b every per-term support rate quoted in finding 8
  edit 5  the amplification ratio (one source BioProject -> BioSample records)

Outputs ($BERIL_RUN_DIR):
  v22_duck_fields.csv        per term, which env_* field carries it, among those samples
  v22_industrial_share.csv   riverine/stream composition of MGnify industrial_ww
  v22_finding8_terms.csv     the quoted terms with their recorded support rates
  v22_amplification.csv      source-record to BioSample-record ratio for the duck terms
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
ENV_FIELDS = ["env_broad_scale", "env_local_scale", "env_medium", "isolation_source"]


def latest(p):
    return sorted(glob.glob(str(PROJ / p)))[-1]


def save(df, name):
    df.to_csv(out / name, index=False)
    print(f"[{time.time()-T0:5.0f}s] {name}: {len(df)} rows", flush=True)


lab = pd.read_parquet(latest("runs/*-external-vs-biosample/out/labelled_samples.parquet"))
found = lab[lab.found == 1]

# ---- edit 3: which field carries each duck term, among the agricultural_ww samples ----
ag = found[(found.source == "MGnify") & (found.ext_subtype == "agricultural_ww")]
rows = []
for term in ["water trough", "duck cecum", "aviary", "water line", "barn"]:
    for f in ENV_FIELDS:
        n = int((ag[f].astype(str).str.lower().str.strip() == term).sum())
        if n:
            rows.append({"term": term, "field": f, "n_samples_in_group": n,
                         "group_size": len(ag)})
save(pd.DataFrame(rows).sort_values(["term", "n_samples_in_group"], ascending=[True, False]),
     "v22_duck_fields.csv")

# ---- edit 6a: composition of MGnify industrial_ww ----
ind = found[(found.source == "MGnify") & (found.ext_subtype == "industrial_ww")]
ind_ns = ind[ind.any_signal == 0]
rows = []
for tag, df in [("all found", ind), ("no-signal subset", ind_ns)]:
    vc_tax = df.taxonomy_name.astype(str).str.lower().value_counts()
    vc_med = df.env_medium.astype(str).str.lower().value_counts()
    rows.append({
        "cohort": tag, "n": len(df),
        "riverine_metagenome": int(vc_tax.get("riverine metagenome", 0)),
        "pct_riverine": round(100 * vc_tax.get("riverine metagenome", 0) / len(df), 1),
        "env_medium_stream_water": int(vc_med.get("stream water", 0)),
        "pct_stream_water": round(100 * vc_med.get("stream water", 0) / len(df), 1),
        "top_taxonomy": vc_tax.index[0] if len(vc_tax) else None,
        "top_taxonomy_n": int(vc_tax.iloc[0]) if len(vc_tax) else 0,
    })
save(pd.DataFrame(rows), "v22_industrial_share.csv")

# ---- edit 6b: the per-term support rates quoted in finding 8 ----
sc = pd.read_csv(latest("runs/*-term-screen/out/term_screen.csv"))
QUOTED = [
    ("taxonomy_name", "anas platyrhynchos"), ("taxonomy_name", "riverine metagenome"),
    ("env_medium", "cecal contents"), ("env_medium", "stream water"),
    ("env_local_scale", "animal house"), ("isolation_source", "sewage"),
    ("isolation_source", "anaerobic digester"), ("taxonomy_name", "bioreactor metagenome"),
    ("env_local_scale", "water"),
]
rows = []
for f, v in QUOTED:
    m = sc[(sc.field == f) & (sc.value == v)]
    if m.empty:
        # the term may have been mined from a different field; report where it is
        alt = sc[sc.value == v]
        rows.append({"field_quoted": f, "value": v, "found_in_field": ";".join(alt.field) or "ABSENT",
                     "n_records": int(alt.n_records.sum()) if len(alt) else 0,
                     "independent_support": round(float(alt.independent_support.max()), 4) if len(alt) else None,
                     "verdict": ";".join(alt.verdict) if len(alt) else None, "match": "field mismatch"})
    else:
        r = m.iloc[0]
        rows.append({"field_quoted": f, "value": v, "found_in_field": f,
                     "n_records": int(r.n_records),
                     "independent_support": round(float(r.independent_support), 4),
                     "support_pkg": round(float(r.support_pkg), 4),
                     "support_envo": round(float(r.support_envo), 4),
                     "support_proj": round(float(r.support_proj), 4),
                     "verdict": r.verdict, "match": "ok"})
save(pd.DataFrame(rows), "v22_finding8_terms.csv")

# ---- edit 5: amplification ratio ----
spark = get_spark("ww-v22")
ag_acc = ag.accession.tolist()
spark.createDataFrame([(a,) for a in ag_acc[:1000]], schema=["accession"]).createOrReplaceTempView("ag_c0")
for i in range(1000, len(ag_acc), 1000):
    spark.createDataFrame([(a,) for a in ag_acc[i:i + 1000]],
                          schema=["accession"]).createOrReplaceTempView(f"ag_c{i//1000}")
parts = " UNION ALL ".join(f"SELECT * FROM ag_c{j}" for j in range((len(ag_acc) + 999) // 1000))
spark.sql(f"CACHE TABLE ag AS {parts}")
amp = spark.sql("""
WITH src AS (
  SELECT s.bioproject_accession AS proj, COUNT(DISTINCT a.accession) AS n_src
  FROM ag a JOIN nmdc.ncbi_biosamples.sra_biosamples_bioprojects s
    ON s.biosample_accession = a.accession
  GROUP BY s.bioproject_accession ORDER BY n_src DESC LIMIT 1),
tgt AS (
  SELECT COUNT(*) AS n_tgt FROM nmdc.ncbi_biosamples.biosamples_flattened
  WHERE lower(trim(taxonomy_name)) = 'anas platyrhynchos')
SELECT src.proj AS largest_source_bioproject, src.n_src AS source_records,
       tgt.n_tgt AS biosample_records_matched,
       ROUND(tgt.n_tgt / src.n_src, 1) AS amplification
FROM src CROSS JOIN tgt
""").toPandas()
save(amp, "v22_amplification.csv")
print(amp.to_string(index=False), flush=True)
print("done", flush=True)
