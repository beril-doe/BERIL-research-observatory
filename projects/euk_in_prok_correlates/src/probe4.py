import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=80):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=48)
    except Exception as e:
        print("ERR:", str(e)[:400])

def cols(tbl):
    print("\n----- columns: " + tbl + " -----")
    try:
        for r in spark.sql("DESCRIBE TABLE " + tbl).collect():
            cn = r['col_name']
            if cn and not cn.startswith('#'):
                print(cn, end=" | ")
        print()
    except Exception as e:
        print("ERR:", str(e)[:300])

cols("nmdc.metadata.biosample_set")
cols("nmdc.metadata.data_generation_set")
cols("nmdc.metadata.instrument_set")
cols("nmdc.metadata.material_processing_set")

# id column check on biosample_set
show("biosample_set id sample", "SELECT id FROM nmdc.metadata.biosample_set LIMIT 3")
# omics bridge sample_id namespace vs biosample id
show("omics_files sample_id sample", "SELECT DISTINCT sample_id FROM kbase.nmdc_arkin.omics_files_table WHERE sample_id IS NOT NULL LIMIT 3")

print("\nDONE")
