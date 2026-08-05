import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=30):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=60)
    except Exception as e:
        print("ERR:", str(e)[:220])

# --- Full NMDC metadata ceiling ---
show("nmdc.metadata study_set count", "SELECT COUNT(*) n_studies FROM nmdc.metadata.study_set")
show("nmdc.metadata biosample_set: studies & samples", """
SELECT COUNT(*) n_biosamples FROM nmdc.metadata.biosample_set""")
show("biosample_set distinct studies (via associated_studies)", """
SELECT COUNT(DISTINCT associated_studies) n_studies FROM nmdc.metadata.biosample_set_associated_studies""")
show("biosample analysis_type breakdown", """
SELECT analysis_type, COUNT(*) n FROM nmdc.metadata.biosample_set GROUP BY analysis_type ORDER BY n DESC""")

# --- How many studies does the classifier (euk-fraction) data actually cover ---
show("nmdc_arkin study_table count", "SELECT COUNT(*) n FROM kbase.nmdc_arkin.study_table")
show("classifier studies present in omics_files_table", """
SELECT COUNT(DISTINCT study_id) n_studies, COUNT(DISTINCT sample_id) n_samples
FROM kbase.nmdc_arkin.omics_files_table
WHERE file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold)""")
show("omics_files_table ALL studies/samples (any workflow)", """
SELECT COUNT(DISTINCT study_id) n_studies, COUNT(DISTINCT sample_id) n_samples FROM kbase.nmdc_arkin.omics_files_table""")

# --- nmdc.results: does it have per-sample taxonomy across more studies? ---
show("nmdc.results tables", "SHOW TABLES IN nmdc.results")

# --- Other NMDC subsets ---
show("kbase.nmdc_neon tables", "SHOW TABLES IN kbase.nmdc_neon")
show("kbase.nmdc_mags tables", "SHOW TABLES IN kbase.nmdc_mags")
show("nmdc.ncbi_biosamples tables", "SHOW TABLES IN nmdc.ncbi_biosamples")

print("\nDONE")
