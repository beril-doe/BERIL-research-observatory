"""Discover schemas and row counts of candidate sample-metadata tables.

Writes schemas.md and schemas.json to $BERIL_RUN_DIR.
"""
# %%
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from berdl_spark import get_spark, run_dir  # noqa: E402

TABLES = [
    # NCBI BioSample (NMDC-curated flattening)
    *[f"nmdc.ncbi_biosamples.{t}" for t in [
        "biosamples_flattened", "biosamples_attributes", "biosamples_ids",
        "biosamples_links", "ncbi_packages_flattened", "ncbi_attributes_flattened",
        "env_triads_flattened", "attribute_harmonized_pairings",
        "harmonized_name_usage_stats", "harmonized_name_dimensional_stats",
        "content_pairs_aggregated", "mixed_content_counts", "bioprojects_flattened",
        "sra_biosamples_bioprojects", "measurement_evidence_percentages",
        "measurement_results_skip_filtered", "unit_assertion_counts",
    ]],
    # NMDC
    "nmdc.metadata.biosample_set", "nmdc.metadata.study_set",
    "nmdc.metadata.field_research_site_set",
    "kbase.nmdc_mags.biosample_metadata", "kbase.nmdc_mags.study_sample",
    "kbase.nmdc_arkin.study_table", "kbase.nmdc_arkin.kraken_gold",
    "kbase.nmdc_arkin.sample_tokens_v1", "kbase.nmdc_arkin.vocab_registry_v1",
    # MGnify
    "kescience.mgnify.biome", "kescience.mgnify.genome", "kescience.mgnify.species",
    # Other sample-bearing refdata
    "refdata.all_the_bacteria.biosample_environment",
    "refdata.all_the_bacteria.ena_metadata",
    "refdata.all_the_bacteria.assembly_biosample_metadata",
    "refdata.agmicrobiome.sample_environment",
    "refdata.agmicrobiome.sample_metadata",
    "refdata.microagrobiome.bgc_environment",
    # Ontology
    "kbase.ontology_source.statements", "kbase.ontology_source.prefix",
]

# %%
spark = get_spark("ww-schemas")
out = run_dir()
result = {}
lines = ["# Candidate table schemas\n"]
for t in TABLES:
    t0 = time.time()
    try:
        cols = spark.sql(f"DESCRIBE {t}").toPandas()
        cols = cols[~cols["col_name"].str.startswith("#") & (cols["col_name"] != "")]
        try:
            n = spark.sql(f"SELECT COUNT(*) AS n FROM {t}").toPandas()["n"].iloc[0]
        except Exception as e:  # noqa: BLE001
            n = f"count failed: {type(e).__name__}"
        result[t] = {"rows": int(n) if isinstance(n, (int,)) or hasattr(n, "item") else n,
                     "columns": cols[["col_name", "data_type"]].values.tolist()}
        lines.append(f"\n## {t}  (rows: {n:,})\n" if not isinstance(n, str) else f"\n## {t}  ({n})\n")
        lines.append("| column | type |\n|---|---|")
        for c, d in result[t]["columns"]:
            lines.append(f"| `{c}` | {d} |")
        print(f"{t}: {n} rows, {len(cols)} cols, {time.time()-t0:.1f}s", flush=True)
    except Exception as e:  # noqa: BLE001
        result[t] = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
        lines.append(f"\n## {t}\n\nERROR: {result[t]['error']}\n")
        print(f"{t}: ERROR {type(e).__name__}: {str(e)[:200]}", flush=True)

(out / "schemas.md").write_text("\n".join(lines) + "\n")
(out / "schemas.json").write_text(json.dumps(result, indent=1, default=str))
print("wrote", out / "schemas.md")
