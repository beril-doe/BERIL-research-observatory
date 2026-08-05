import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=30):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=60)
    except Exception as e:
        print("ERR:", str(e)[:300])

# Kraken superkingdom names + how euk fraction is stored (percent vs abundance)
show("kraken superkingdom names", """
SELECT name, COUNT(DISTINCT file_id) n_files, ROUND(AVG(percent),2) avg_pct
FROM kbase.nmdc_arkin.kraken_gold WHERE rank='superkingdom'
GROUP BY name ORDER BY n_files DESC""")

# Kraken kingdom-level euk sources
show("kraken kingdom names", """
SELECT name, COUNT(DISTINCT file_id) n_files, ROUND(AVG(percent),3) avg_pct
FROM kbase.nmdc_arkin.kraken_gold WHERE rank='kingdom'
GROUP BY name ORDER BY n_files DESC""")

# Does kraken percent at superkingdom sum ~100 per file? (sanity for fraction)
show("kraken superkingdom percent-sum per file (sample)", """
SELECT file_id, ROUND(SUM(percent),1) sum_pct, COUNT(*) n_sk
FROM kbase.nmdc_arkin.kraken_gold WHERE rank='superkingdom'
GROUP BY file_id ORDER BY file_id LIMIT 8""")

# Euk fraction (kraken) distribution via superkingdom Eukaryota percent
show("kraken euk-fraction buckets", """
WITH e AS (
  SELECT file_id, MAX(CASE WHEN name='Eukaryota' THEN percent ELSE 0 END) euk_pct
  FROM kbase.nmdc_arkin.kraken_gold WHERE rank='superkingdom' GROUP BY file_id)
SELECT CASE WHEN euk_pct=0 THEN '0' WHEN euk_pct<1 THEN '<1%'
            WHEN euk_pct<5 THEN '1-5%' WHEN euk_pct<20 THEN '5-20%' ELSE '>20%' END bucket,
       COUNT(*) n FROM e GROUP BY 1 ORDER BY 1""")

print("\nDONE")
