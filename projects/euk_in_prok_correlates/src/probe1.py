import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session

spark = get_spark_session()

def show(title, sql, n=25):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=60)
    except Exception as e:
        print("ERR:", str(e)[:300])

# 1. Classifier schemas
show("gottcha_gold schema", "DESCRIBE TABLE kbase.nmdc_arkin.gottcha_gold")
show("kraken_gold schema", "DESCRIBE TABLE kbase.nmdc_arkin.kraken_gold")
show("centrifuge_gold schema", "DESCRIBE TABLE kbase.nmdc_arkin.centrifuge_gold")

# 2. What ranks/domains exist? Look for a domain/superkingdom rank and Eukaryota
show("gottcha distinct rank values", "SELECT rank, COUNT(*) c FROM kbase.nmdc_arkin.gottcha_gold GROUP BY rank ORDER BY c DESC")

# 3. Sample rows at coarse rank
show("gottcha sample rows", "SELECT * FROM kbase.nmdc_arkin.gottcha_gold LIMIT 10")

# 4. Bridge table schema + counts
show("omics_files_table schema", "DESCRIBE TABLE kbase.nmdc_arkin.omics_files_table")
show("omics_files workflow_type counts", "SELECT workflow_type, file_type, COUNT(*) c FROM kbase.nmdc_arkin.omics_files_table GROUP BY workflow_type, file_type ORDER BY c DESC")

print("\nDONE")
