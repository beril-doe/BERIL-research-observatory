import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=40):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=55)
    except Exception as e:
        print("ERR:", str(e)[:300])

CLASSIFIED = """(SELECT DISTINCT o.sample_id FROM kbase.nmdc_arkin.omics_files_table o
  WHERE o.file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold))"""

# Biosample predictor coverage (fixed columns)
show("biosample predictor coverage", f"""
WITH s AS {CLASSIFIED}
SELECT COUNT(*) n,
  SUM(CASE WHEN b.env_medium_term_name IS NOT NULL THEN 1 ELSE 0 END) env_medium,
  SUM(CASE WHEN b.env_broad_scale_term_name IS NOT NULL THEN 1 ELSE 0 END) env_broad,
  SUM(CASE WHEN b.ecosystem_type IS NOT NULL THEN 1 ELSE 0 END) ecosystem_type,
  SUM(CASE WHEN b.host_taxid_term_name IS NOT NULL OR b.host_name IS NOT NULL THEN 1 ELSE 0 END) host,
  SUM(CASE WHEN b.depth_has_numeric_value IS NOT NULL THEN 1 ELSE 0 END) depth,
  SUM(CASE WHEN b.size_frac_has_raw_value IS NOT NULL THEN 1 ELSE 0 END) size_frac,
  SUM(CASE WHEN b.samp_size_has_numeric_value IS NOT NULL THEN 1 ELSE 0 END) samp_size,
  SUM(CASE WHEN b.samp_collec_device IS NOT NULL THEN 1 ELSE 0 END) collec_device,
  SUM(CASE WHEN b.samp_mat_process_term_name IS NOT NULL THEN 1 ELSE 0 END) mat_process
FROM s JOIN nmdc.metadata.biosample_set b ON s.sample_id = b.id""")

# Sequencing instrument coverage: data_generation_set linked to biosample via has_input
show("data_generation_set_has_input schema", "DESCRIBE TABLE nmdc.metadata.data_generation_set_has_input")
show("data_generation instrument coverage for classified samples", f"""
WITH s AS {CLASSIFIED}
SELECT COUNT(DISTINCT s.sample_id) classified,
       COUNT(DISTINCT hi.has_input) with_datagen,
       COUNT(DISTINCT CASE WHEN dg.instrument_used IS NOT NULL THEN hi.has_input END) with_instrument
FROM s
LEFT JOIN nmdc.metadata.data_generation_set_has_input hi ON hi.has_input = s.sample_id
LEFT JOIN nmdc.metadata.data_generation_set dg ON dg.id = hi.id""")

# instrument model distribution
show("instrument models used (classified samples)", f"""
WITH s AS {CLASSIFIED}
SELECT COALESCE(ins.model, ins.name, '(null)') model, COUNT(DISTINCT s.sample_id) n
FROM s
JOIN nmdc.metadata.data_generation_set_has_input hi ON hi.has_input = s.sample_id
JOIN nmdc.metadata.data_generation_set_instrument_used iu ON iu.id = hi.id
JOIN nmdc.metadata.instrument_set ins ON ins.id = iu.instrument_used
GROUP BY 1 ORDER BY 2 DESC""")

print("\nDONE")
