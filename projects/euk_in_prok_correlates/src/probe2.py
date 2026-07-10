import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=40):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=70)
    except Exception as e:
        print("ERR:", str(e)[:400])

# --- Is there Eukaryota signal? ---
# gottcha superkingdom labels
show("gottcha superkingdom labels", """
SELECT label, COUNT(DISTINCT file_id) n_files, COUNT(*) rows
FROM kbase.nmdc_arkin.gottcha_gold WHERE rank='superkingdom'
GROUP BY label ORDER BY n_files DESC""")

# kraken domain-level distinct rank codes then domain names
show("kraken rank codes", "SELECT rank, COUNT(*) c FROM kbase.nmdc_arkin.kraken_gold GROUP BY rank ORDER BY c DESC")
show("kraken domain names (rank D)", """
SELECT name, COUNT(DISTINCT file_id) n_files, ROUND(AVG(percent),2) avg_pct
FROM kbase.nmdc_arkin.kraken_gold WHERE rank='D'
GROUP BY name ORDER BY n_files DESC""")

# centrifuge domain-level
show("centrifuge rank codes", "SELECT rank, COUNT(*) c FROM kbase.nmdc_arkin.centrifuge_gold GROUP BY rank ORDER BY c DESC")

# How many metagenome files total, and euk-fraction distribution via kraken domain
show("n distinct files per classifier", """
SELECT 'gottcha' src, COUNT(DISTINCT file_id) n FROM kbase.nmdc_arkin.gottcha_gold
UNION ALL SELECT 'kraken', COUNT(DISTINCT file_id) FROM kbase.nmdc_arkin.kraken_gold
UNION ALL SELECT 'centrifuge', COUNT(DISTINCT file_id) FROM kbase.nmdc_arkin.centrifuge_gold""")

print("\nDONE")
