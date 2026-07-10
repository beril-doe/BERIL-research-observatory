"""Build the per-sample analysis table for euk_in_prok_correlates.

Response variable: GOTTCHA relative eukaryotic abundance (primary), with
plastid (plant) and non-plastid (protist/fungal) split, plus Kraken (Metazoa/host)
and Centrifuge euk fractions for source attribution + robustness.
Predictors: matrix/env/ecosystem/collection-device/platform/depth + study_id.

Run on-cluster:  python src/build_analysis_table.py
Writes:          data/euk_fraction_per_file.csv, data/analysis_table.csv
"""
import warnings, os
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session

OUT = os.path.join(os.path.dirname(__file__), "..", "data")
spark = get_spark_session()

# ---------------------------------------------------------------------------
# 1. Per-SAMPLE eukaryotic fractions from each classifier. Each classifier
#    writes its own file_id; they share only sample_id (via omics_files_table),
#    so aggregate each classifier through the bridge to sample level, then merge.
#    Fraction = abundance-based, relative within classified reads at superkingdom.
# ---------------------------------------------------------------------------
gottcha = spark.sql("""
WITH pf AS (
  SELECT file_id,
    SUM(CASE WHEN label LIKE 'Eukaryota%'       THEN abundance ELSE 0 END)/SUM(abundance) euk,
    SUM(CASE WHEN label = 'Eukaryota (plastid)' THEN abundance ELSE 0 END)/SUM(abundance) plastid,
    SUM(CASE WHEN label = 'Eukaryota'           THEN abundance ELSE 0 END)/SUM(abundance) euk_np
  FROM kbase.nmdc_arkin.gottcha_gold WHERE rank='superkingdom' GROUP BY file_id)
SELECT o.sample_id, MAX(o.study_id) study_id, COUNT(*) n_gott_files,
       AVG(pf.euk) gott_euk_frac, AVG(pf.plastid) gott_plastid_frac, AVG(pf.euk_np) gott_euk_nonplastid_frac
FROM pf JOIN kbase.nmdc_arkin.omics_files_table o ON o.file_id = pf.file_id
GROUP BY o.sample_id
""")

kraken = spark.sql("""
WITH pf AS (
  SELECT file_id,
    SUM(CASE WHEN name='Eukaryota' THEN abundance ELSE 0 END)/SUM(abundance) euk
  FROM kbase.nmdc_arkin.kraken_gold WHERE rank='superkingdom' GROUP BY file_id)
SELECT o.sample_id, AVG(pf.euk) krak_euk_frac
FROM pf JOIN kbase.nmdc_arkin.omics_files_table o ON o.file_id = pf.file_id
GROUP BY o.sample_id
""")

centrifuge = spark.sql("""
WITH pf AS (
  SELECT file_id,
    SUM(CASE WHEN label='Eukaryota' THEN abundance ELSE 0 END)/SUM(abundance) euk
  FROM kbase.nmdc_arkin.centrifuge_gold WHERE rank='superkingdom' GROUP BY file_id)
SELECT o.sample_id, AVG(pf.euk) cent_euk_frac
FROM pf JOIN kbase.nmdc_arkin.omics_files_table o ON o.file_id = pf.file_id
GROUP BY o.sample_id
""")

gottcha.createOrReplaceTempView("g")
kraken.createOrReplaceTempView("k")
centrifuge.createOrReplaceTempView("c")

per_sample = spark.sql("""
SELECT g.sample_id, g.study_id, g.n_gott_files,
       g.gott_euk_frac, g.gott_plastid_frac, g.gott_euk_nonplastid_frac,
       k.krak_euk_frac, c.cent_euk_frac
FROM g LEFT JOIN k ON k.sample_id=g.sample_id LEFT JOIN c ON c.sample_id=g.sample_id
""")
per_sample.createOrReplaceTempView("per_sample")
ps = per_sample.toPandas()
ps.to_csv(os.path.join(OUT, "euk_fraction_per_file.csv"), index=False)
print(f"[per_sample classifiers] {len(ps)} samples")
print(ps[["gott_euk_frac","gott_plastid_frac","krak_euk_frac","cent_euk_frac"]].describe().round(4).to_string())

# ---------------------------------------------------------------------------
# 3. Join biosample predictors (select only needed columns from wide table).
# ---------------------------------------------------------------------------
bs = spark.sql("""
SELECT id,
       env_medium_term_name, env_broad_scale_term_name, env_local_scale_term_name,
       ecosystem, ecosystem_category, ecosystem_type, ecosystem_subtype,
       samp_collec_device,
       depth_has_numeric_value AS depth_m,
       host_taxid_term_name, host_name, geo_loc_name_has_raw_value AS geo_loc,
       collection_date_has_raw_value AS collection_date
FROM nmdc.metadata.biosample_set
""")
bs.createOrReplaceTempView("bs")

# ---------------------------------------------------------------------------
# 4. Sequencing platform (subset) via data_generation chain.
# ---------------------------------------------------------------------------
plat = spark.sql("""
SELECT hi.has_input AS sample_id, COALESCE(ins.model, ins.name) AS platform
FROM nmdc.metadata.data_generation_set_has_input hi
JOIN nmdc.metadata.data_generation_set_instrument_used iu ON iu.parent_id = hi.parent_id
JOIN nmdc.metadata.instrument_set ins ON ins.id = iu.instrument_used
""").dropDuplicates(["sample_id"])
plat.createOrReplaceTempView("plat")

analysis = spark.sql("""
SELECT s.*,
       bs.env_medium_term_name, bs.env_broad_scale_term_name, bs.env_local_scale_term_name,
       bs.ecosystem, bs.ecosystem_category, bs.ecosystem_type, bs.ecosystem_subtype,
       bs.samp_collec_device, bs.depth_m, bs.host_taxid_term_name, bs.host_name,
       bs.geo_loc, bs.collection_date, plat.platform
FROM per_sample s
LEFT JOIN bs ON bs.id = s.sample_id
LEFT JOIN plat ON plat.sample_id = s.sample_id
""")
at = analysis.toPandas()
at.to_csv(os.path.join(OUT, "analysis_table.csv"), index=False)
print(f"\n[analysis_table] {len(at)} samples")
print("coverage:")
for col in ["ecosystem_category","ecosystem_type","env_medium_term_name","samp_collec_device","platform","depth_m","gott_euk_frac"]:
    print(f"  {col:28s} {at[col].notna().sum():5d} ({100*at[col].notna().mean():.0f}%)")
print("\nDONE")
