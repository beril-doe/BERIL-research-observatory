import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()
def show(title, sql, n=30):
    print("\n===== " + title + " =====")
    try: spark.sql(sql).show(n, truncate=55)
    except Exception as e: print("ERR:", str(e)[:220])
def cols(tbl):
    print("\n-- cols", tbl, "--")
    try: print(" | ".join(r['col_name'] for r in spark.sql("DESCRIBE TABLE "+tbl).collect() if r['col_name'] and not r['col_name'].startswith('#')))
    except Exception as e: print("ERR:", str(e)[:200])

show("kescience.mgnify tables", "SHOW TABLES IN kescience.mgnify")
print("\nDONE-LIST")
