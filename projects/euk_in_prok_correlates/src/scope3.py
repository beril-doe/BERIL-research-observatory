import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()
def show(title, sql, n=30):
    print("\n===== " + title + " =====")
    try: spark.sql(sql).show(n, truncate=60)
    except Exception as e: print("ERR:", str(e)[:220])
def cols(tbl):
    print("\n-- cols", tbl, "--")
    try: print(" | ".join(r['col_name'] for r in spark.sql("DESCRIBE TABLE "+tbl).collect() if r['col_name'] and not r['col_name'].startswith('#')))
    except Exception as e: print("ERR:", str(e)[:200])

# scale of nmdc.results gottcha2
show("gottcha2 distinct files & superkingdom labels", """
SELECT COUNT(DISTINCT data_object_id) n_files, COUNT(DISTINCT workflow_run_id) n_runs
FROM nmdc.results.gottcha2_classification_report""")
show("gottcha2 superkingdom labels", """
SELECT NAME, COUNT(DISTINCT data_object_id) n_files
FROM nmdc.results.gottcha2_classification_report WHERE LEVEL='superkingdom'
GROUP BY NAME ORDER BY n_files DESC""")

# bridge table
cols("nmdc.metadata.biosample_to_workflow_run")
show("biosample_to_workflow_run sample", "SELECT * FROM nmdc.metadata.biosample_to_workflow_run LIMIT 5")

# how many biosamples & studies does gottcha2 cover via the bridge?
show("gottcha2 coverage via biosample_to_workflow_run", """
WITH runs AS (SELECT DISTINCT workflow_run_id FROM nmdc.results.gottcha2_classification_report)
SELECT COUNT(DISTINCT b.biosample_id) n_biosamples
FROM runs JOIN nmdc.metadata.biosample_to_workflow_run b
  ON b.workflow_run_id = runs.workflow_run_id""")

# studies via biosample -> associated_studies
show("gottcha2 study coverage", """
WITH runs AS (SELECT DISTINCT workflow_run_id FROM nmdc.results.gottcha2_classification_report),
bios AS (SELECT DISTINCT b.biosample_id FROM runs JOIN nmdc.metadata.biosample_to_workflow_run b ON b.workflow_run_id=runs.workflow_run_id)
SELECT COUNT(DISTINCT s.associated_studies) n_studies, COUNT(DISTINCT bios.biosample_id) n_bios
FROM bios JOIN nmdc.metadata.biosample_set_associated_studies s ON s.id = bios.biosample_id""")

# also kraken2 + centrifuge scale
show("kraken2 files & superkingdom euk", """
SELECT COUNT(DISTINCT data_object_id) n_files FROM nmdc.results.kraken2_classification_report""")
print("\nDONE")
