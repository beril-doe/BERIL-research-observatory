"""Build the per-run analysis table for euk_in_prok_correlates (v2, nmdc.results source).

Unit of analysis = workflow_run_id (one NMDC ReadbasedAnalysis run; the three classifiers
share it). This avoids pooling pseudo-replication (many biosamples -> one pooled run).

Response: GOTTCHA2 relative eukaryotic abundance (primary) + plastid(plant)/non-plastid split;
Kraken2 Eukaryota (host/Metazoa) at domain rank; Centrifuge Eukaryota (robustness).
Predictors: matrix/env/ecosystem (+within-study env_local_scale, ecosystem_subtype, geo) + platform + pooling.

Run on-cluster:  python src/build_analysis_table.py
Writes:          data/analysis_table.csv
"""
import warnings, os
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
spark = get_spark_session()

# --- per workflow_run eukaryotic fractions from each classifier ---
gottcha = spark.sql("""
SELECT workflow_run_id,
  SUM(CASE WHEN NAME LIKE 'Eukaryota%'       THEN REL_ABUNDANCE ELSE 0 END)/SUM(REL_ABUNDANCE) gott_euk_frac,
  SUM(CASE WHEN NAME = 'Eukaryota (plastid)' THEN REL_ABUNDANCE ELSE 0 END)/SUM(REL_ABUNDANCE) gott_plastid_frac,
  SUM(CASE WHEN NAME = 'Eukaryota'           THEN REL_ABUNDANCE ELSE 0 END)/SUM(REL_ABUNDANCE) gott_euk_nonplastid_frac
FROM nmdc.results.gottcha2_classification_report WHERE LEVEL='superkingdom' AND workflow_run_id IS NOT NULL GROUP BY workflow_run_id
""")
kraken = spark.sql("""
SELECT workflow_run_id,
  SUM(CASE WHEN name='Eukaryota' THEN clade_reads ELSE 0 END)/SUM(clade_reads) krak_euk_frac
FROM nmdc.results.kraken2_classification_report WHERE rank='D' AND workflow_run_id IS NOT NULL GROUP BY workflow_run_id
""")
centrifuge = spark.sql("""
SELECT workflow_run_id,
  SUM(CASE WHEN name='Eukaryota' THEN abundance ELSE 0 END)/NULLIF(SUM(abundance),0) cent_euk_frac
FROM nmdc.results.centrifuge_output_report_file WHERE taxRank='superkingdom' AND workflow_run_id IS NOT NULL GROUP BY workflow_run_id
""")
for df,nm in [(gottcha,'g'),(kraken,'k'),(centrifuge,'c')]:
    df.createOrReplaceTempView(nm)

# --- run -> one biosample (min id) + study, via bridge ---
run_bios = spark.sql("""
WITH rb AS (
  SELECT workflow_run_id, MIN(biosample_id) biosample_id, MAX(CAST(has_pooling AS INT)) has_pooling,
         MAX(CAST(has_extraction AS INT)) has_extraction
  FROM nmdc.metadata.biosample_to_workflow_run GROUP BY workflow_run_id)
SELECT rb.*, a.associated_studies study_id
FROM rb LEFT JOIN nmdc.metadata.biosample_set_associated_studies a ON a.parent_id = rb.biosample_id
""")
run_bios.createOrReplaceTempView("rb")

bs = spark.sql("""
SELECT id,
  env_medium_term_name, env_broad_scale_term_name, env_local_scale_term_name,
  ecosystem, ecosystem_category, ecosystem_type, ecosystem_subtype,
  samp_collec_device, depth_has_numeric_value AS depth_m,
  host_taxid_term_name, host_name, geo_loc_name_has_raw_value AS geo_loc
FROM nmdc.metadata.biosample_set
""")
bs.createOrReplaceTempView("bs")

plat = spark.sql("""
SELECT hi.has_input AS biosample_id, COALESCE(ins.model, ins.name) platform
FROM nmdc.metadata.data_generation_set_has_input hi
JOIN nmdc.metadata.data_generation_set_instrument_used iu ON iu.parent_id = hi.parent_id
JOIN nmdc.metadata.instrument_set ins ON ins.id = iu.instrument_used
""").dropDuplicates(["biosample_id"])
plat.createOrReplaceTempView("plat")

analysis = spark.sql("""
SELECT g.workflow_run_id AS sample_id, rb.biosample_id, rb.study_id,
       rb.has_pooling, rb.has_extraction,
       g.gott_euk_frac, g.gott_plastid_frac, g.gott_euk_nonplastid_frac,
       k.krak_euk_frac, c.cent_euk_frac,
       bs.env_medium_term_name, bs.env_broad_scale_term_name, bs.env_local_scale_term_name,
       bs.ecosystem, bs.ecosystem_category, bs.ecosystem_type, bs.ecosystem_subtype,
       bs.samp_collec_device, bs.depth_m, bs.host_taxid_term_name, bs.host_name, bs.geo_loc,
       plat.platform
FROM g
LEFT JOIN k  ON k.workflow_run_id = g.workflow_run_id
LEFT JOIN c  ON c.workflow_run_id = g.workflow_run_id
LEFT JOIN rb ON rb.workflow_run_id = g.workflow_run_id
LEFT JOIN bs ON bs.id = rb.biosample_id
LEFT JOIN plat ON plat.biosample_id = rb.biosample_id
""")
at = analysis.toPandas()
at.to_csv(os.path.join(OUT, "analysis_table.csv"), index=False)
print(f"[analysis_table v2] {len(at)} runs, {at.study_id.nunique()} studies")
print(at[["gott_euk_frac","gott_plastid_frac","krak_euk_frac","cent_euk_frac"]].describe().round(4).to_string())
print("\nstudy sizes:")
print(at.study_id.value_counts().head(12).to_string())
print("\ncoverage:")
for col in ["ecosystem_category","ecosystem_type","env_medium_term_name","env_local_scale_term_name","platform","study_id"]:
    print(f"  {col:28s} {at[col].notna().sum():5d} ({100*at[col].notna().mean():.0f}%)")
print("\nDONE")
