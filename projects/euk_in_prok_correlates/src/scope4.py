import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()
def show(title, sql, n=40):
    print("\n===== " + title + " =====")
    try: spark.sql(sql).show(n, truncate=60)
    except Exception as e: print("ERR:", str(e)[:220])

# STUDY coverage of nmdc.results gottcha2 (fix: child table keys on parent_id)
show("nmdc.results gottcha2 STUDY + biosample coverage", """
WITH runs AS (SELECT DISTINCT workflow_run_id FROM nmdc.results.gottcha2_classification_report),
bios AS (SELECT DISTINCT b.biosample_id FROM runs
         JOIN nmdc.metadata.biosample_to_workflow_run b ON b.workflow_run_id=runs.workflow_run_id)
SELECT COUNT(DISTINCT a.associated_studies) n_studies, COUNT(DISTINCT bios.biosample_id) n_bios
FROM bios JOIN nmdc.metadata.biosample_set_associated_studies a ON a.parent_id = bios.biosample_id""")

# per-study sample counts (concentration check)
show("nmdc.results gottcha2 samples per study (top 25)", """
WITH runs AS (SELECT DISTINCT workflow_run_id FROM nmdc.results.gottcha2_classification_report),
bios AS (SELECT DISTINCT b.biosample_id FROM runs
         JOIN nmdc.metadata.biosample_to_workflow_run b ON b.workflow_run_id=runs.workflow_run_id)
SELECT a.associated_studies study, COUNT(DISTINCT bios.biosample_id) n_bios
FROM bios JOIN nmdc.metadata.biosample_set_associated_studies a ON a.parent_id=bios.biosample_id
GROUP BY a.associated_studies ORDER BY n_bios DESC""", 25)

# processing-flag coverage on the classified set (potential H1d-lite predictors)
show("processing-flag distribution among gottcha2-classified biosamples", """
WITH runs AS (SELECT DISTINCT workflow_run_id FROM nmdc.results.gottcha2_classification_report)
SELECT b.has_filtration, b.has_extraction, b.has_pooling, b.has_subsampling, COUNT(DISTINCT b.biosample_id) n
FROM runs JOIN nmdc.metadata.biosample_to_workflow_run b ON b.workflow_run_id=runs.workflow_run_id
GROUP BY 1,2,3,4 ORDER BY n DESC""", 20)

# compare: nmdc_arkin study count (what we used)
show("nmdc_arkin classifier study count (current analysis)", """
SELECT COUNT(DISTINCT study_id) n_studies FROM kbase.nmdc_arkin.omics_files_table
WHERE file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold)""")
print("\nDONE")
