import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=60):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=55)
    except Exception as e:
        print("ERR:", str(e)[:400])

# List metadata tables
show("nmdc.metadata tables", "SHOW TABLES IN nmdc.metadata")
show("nmdc_arkin tables (processing/seq/extraction)", "SHOW TABLES IN kbase.nmdc_arkin")

# Euk fraction distribution via gottcha superkingdom abundance
show("gottcha euk-fraction buckets (plastid+euk abundance per file)", """
WITH sk AS (
  SELECT file_id,
         SUM(CASE WHEN label LIKE 'Eukaryota%' THEN abundance ELSE 0 END) euk_ab,
         SUM(abundance) tot_ab
  FROM kbase.nmdc_arkin.gottcha_gold WHERE rank='superkingdom' GROUP BY file_id)
SELECT CASE WHEN euk_ab/tot_ab=0 THEN '0'
            WHEN euk_ab/tot_ab<0.01 THEN '<1%'
            WHEN euk_ab/tot_ab<0.05 THEN '1-5%'
            WHEN euk_ab/tot_ab<0.2 THEN '5-20%'
            ELSE '>20%' END bucket,
       COUNT(*) n_files
FROM sk GROUP BY 1 ORDER BY 1""")

print("\nDONE")
