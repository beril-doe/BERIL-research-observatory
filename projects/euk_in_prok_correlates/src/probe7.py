import warnings
warnings.filterwarnings("ignore")
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()

def show(title, sql, n=30):
    print("\n===== " + title + " =====")
    try:
        spark.sql(sql).show(n, truncate=55)
    except Exception as e:
        print("ERR:", str(e)[:300])

CLASSIFIED = """(SELECT DISTINCT o.sample_id FROM kbase.nmdc_arkin.omics_files_table o
  WHERE o.file_id IN (SELECT DISTINCT file_id FROM kbase.nmdc_arkin.gottcha_gold))"""

show("data_generation instrument coverage", f"""
WITH s AS {CLASSIFIED}
SELECT COUNT(DISTINCT s.sample_id) classified,
       COUNT(DISTINCT hi.has_input) with_datagen,
       COUNT(DISTINCT CASE WHEN iu.instrument_used IS NOT NULL THEN hi.has_input END) with_instrument
FROM s
LEFT JOIN nmdc.metadata.data_generation_set_has_input hi ON hi.has_input = s.sample_id
LEFT JOIN nmdc.metadata.data_generation_set_instrument_used iu ON iu.parent_id = hi.parent_id""")

show("instrument models used (classified samples)", f"""
WITH s AS {CLASSIFIED}
SELECT COALESCE(ins.model, ins.name, ins.vendor, '(null)') model, COUNT(DISTINCT s.sample_id) n
FROM s
JOIN nmdc.metadata.data_generation_set_has_input hi ON hi.has_input = s.sample_id
JOIN nmdc.metadata.data_generation_set_instrument_used iu ON iu.parent_id = hi.parent_id
JOIN nmdc.metadata.instrument_set ins ON ins.id = iu.instrument_used
GROUP BY 1 ORDER BY 2 DESC""")

# material processing (extraction/library) coverage via has_input
show("material_processing has_input schema", "DESCRIBE TABLE nmdc.metadata.material_processing_set_has_input")
show("library_prep_kit / extraction coverage", f"""
WITH s AS {CLASSIFIED}
SELECT COUNT(DISTINCT s.sample_id) classified,
   COUNT(DISTINCT CASE WHEN mp.library_preparation_kit IS NOT NULL THEN hi.has_input END) with_libkit,
   COUNT(DISTINCT CASE WHEN mp.library_type IS NOT NULL THEN hi.has_input END) with_libtype,
   COUNT(DISTINCT CASE WHEN mp.extraction_targets IS NOT NULL THEN hi.has_input END) with_extract
FROM s
LEFT JOIN nmdc.metadata.material_processing_set_has_input hi ON hi.has_input = s.sample_id
LEFT JOIN nmdc.metadata.material_processing_set mp ON mp.id = hi.parent_id""")

print("\nDONE")
