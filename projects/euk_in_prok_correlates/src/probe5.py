import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=40):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=55)
    except Exception as e:
        print("ERR:", str(e)[:400])

# Distinct sample_ids behind the classifier files
show("classified samples & bsm namespace", """
SELECT SUBSTRING(sample_id,1,10) ns, COUNT(DISTINCT sample_id) n_samples
FROM kbase.nmdc_arkin.omics_files_table o
WHERE o.file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold)
GROUP BY 1 ORDER BY 2 DESC""")

# Does classifier sample_id join to biosample_set.id at all?
show("join classified samples -> biosample_set", """
WITH s AS (
  SELECT DISTINCT o.sample_id FROM kbase.nmdc_arkin.omics_files_table o
  WHERE o.file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold))
SELECT COUNT(*) total_classified_samples,
       SUM(CASE WHEN b.id IS NOT NULL THEN 1 ELSE 0 END) joined_to_biosample
FROM s LEFT JOIN nmdc.metadata.biosample_set b ON s.sample_id = b.id""")

# Predictor coverage among joined biosamples
show("predictor non-null coverage (joined biosamples)", """
WITH s AS (
  SELECT DISTINCT o.sample_id FROM kbase.nmdc_arkin.omics_files_table o
  WHERE o.file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold))
SELECT
  COUNT(*) n,
  SUM(CASE WHEN b.env_medium_term_name IS NOT NULL THEN 1 ELSE 0 END) env_medium,
  SUM(CASE WHEN b.ecosystem_category IS NOT NULL THEN 1 ELSE 0 END) ecosystem_cat,
  SUM(CASE WHEN b.host_taxid_term_name IS NOT NULL OR b.host_name IS NOT NULL THEN 1 ELSE 0 END) host,
  SUM(CASE WHEN b.depth_has_numeric_value IS NOT NULL THEN 1 ELSE 0 END) depth,
  SUM(CASE WHEN b.size_frac_has_raw_value IS NOT NULL OR b.filter_pore_size_has_numeric_value IS NOT NULL THEN 1 ELSE 0 END) sizefrac_filter,
  SUM(CASE WHEN b.samp_collec_device IS NOT NULL THEN 1 ELSE 0 END) collec_device
FROM s JOIN nmdc.metadata.biosample_set b ON s.sample_id = b.id""")

# ecosystem_category breakdown of classified samples (the strongest predictor)
show("ecosystem_category of classified samples", """
WITH s AS (
  SELECT DISTINCT o.sample_id FROM kbase.nmdc_arkin.omics_files_table o
  WHERE o.file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold))
SELECT COALESCE(b.ecosystem_category,'(null)') ecosystem_category, COUNT(*) n
FROM s JOIN nmdc.metadata.biosample_set b ON s.sample_id=b.id
GROUP BY 1 ORDER BY 2 DESC""")

print("\nDONE")
