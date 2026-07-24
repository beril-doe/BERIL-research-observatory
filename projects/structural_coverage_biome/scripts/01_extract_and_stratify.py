"""Full biome × Pfam-coverage stratification (v2: local CSV via toPandas)."""
import os
import pandas as pd
from berdl_notebook_utils.setup_spark_session import get_spark_session
from pyspark.sql.functions import (
    col, when, lit, count, countDistinct, sum as spark_sum, row_number,
    regexp_replace, lower, desc,
)
from pyspark.sql.window import Window

OUT = "/home/justaddcoffee/BERIL-research-observatory/projects/structural_coverage_biome/data"
os.makedirs(OUT, exist_ok=True)

spark = get_spark_session()

# ============================================================================
# STEP 1 — Biome classification per genome
# ============================================================================
biome_rules = [
    ("host_gut",           r"\b(gut|feces|stool|faecal|fecal|cecum|caecum|cecal|caecal|rumen|colon|rectum|rectal|gastrointestinal|gi tract|intestin|colonic|coprolite|mucosa)\b"),
    ("host_respiratory",   r"\b(lung|sputum|nasopharyn|oropharyn|respiratory|oral|saliva|tongue|throat|bronch|tonsil|dental|plaque|tooth|teeth|nasal)\b"),
    ("host_urogenital",    r"\b(urin|urethra|vagina|cervi|urogenital|bladder|prostate|semen|penile)\b"),
    ("host_blood_tissue",  r"\b(blood|serum|plasma|csf|cerebrospinal|wound|abscess|pus|tissue|biopsy|liver|kidney|spleen|lymph|joint|synovial|bone marrow)\b"),
    ("host_skin",          r"\b(skin|dermal|epidermis|scalp|sebaceous|axilla|forearm|dermat)\b"),
    ("host_other",         r"\b(human|patient|clinical|hospital|host|homo sapiens|infant|neonate|elderly)\b"),
    ("plant_associated",   r"\b(plant|phyllosphere|endosphere|endophyte|rhizosphere|rhizoplane|root|leaf|leaves|shoot|stem|seed|flower|fruit|nodul|arabidopsis|maize|wheat|rice|soybean|tomato|potato|barley|sorghum)\b"),
    ("soil",               r"\b(soil|permafrost|subsoil|topsoil|paddy|farmland|arable|dryland|grassland|tundra|desert|rhizosphere soil)\b"),
    ("sediment",           r"\b(sediment|mud|slime|silt|riverbed|lakebed|seabed|estuar)\b"),
    ("marine",             r"\b(marine|seawater|sea water|ocean|coastal|saline water|halocline|reef|coral|sponge|kelp|algae|deep-sea|planktonic|zooplankton|hypoxic seawater)\b"),
    ("freshwater",         r"\b(lake water|lake|river|stream|freshwater|pond|reservoir|groundwater|spring water|aquifer|surface water|water sample|water \(|wetland)\b"),
    ("subsurface_extreme", r"\b(subsurface|borehole|deep subsurface|deep-sea vent|hydrothermal|hot spring|geyser|acid mine|acidic|thermophil|hyperthermophil|psychrophil|halophil|cave|mine drainage|underground)\b"),
    ("built_environment",  r"\b(sewage|wastewater|activated sludge|bioreactor|biofilm|hospital surface|air sample|indoor|shower|toilet|cooling tower|drink water|drinking water)\b"),
    ("food_industrial",    r"\b(food|dairy|milk|cheese|yogurt|fermented|sourdough|kimchi|sauerkraut|beer|wine|kombucha|sausage|meat|fish product|kefir|salami|cured)\b"),
    ("agricultural_animal",r"\b(cattle|bovine|chicken|pig|swine|poultry|sheep|goat|horse|equine|canine|dog|feline|cat|silage|feedlot|dairy cow|calf|piglet)\b"),
    ("insect_invertebrate",r"\b(insect|bee|honeybee|ant|termite|larva|larvae|beetle|wasp|butterfly|nematode|worm|drosophila|caterpillar|gut of|midgut|hindgut)\b"),
]

gt = (spark.table("kbase_ke_pangenome.gtdb_metadata")
    .select(col("accession").alias("genome_id"), "ncbi_isolation_source")
    .filter("ncbi_isolation_source IS NOT NULL AND ncbi_isolation_source NOT IN ('none','not known','not provided','not applicable','missing','unknown','Unknown','N/A','NA')")
)
src = lower(col("ncbi_isolation_source"))
case_expr = None
for label, pattern in biome_rules:
    cond = src.rlike(pattern)
    case_expr = when(cond, lit(label)) if case_expr is None else case_expr.when(cond, lit(label))
case_expr = case_expr.otherwise(lit("other"))
genome_biome = gt.withColumn("biome", case_expr).cache()

genome = spark.table("kbase_ke_pangenome.genome").select("genome_id", "gtdb_species_clade_id")
species_biome_counts = (genome
    .join(genome_biome, on="genome_id", how="inner")
    .groupBy("gtdb_species_clade_id", "biome")
    .agg(count("*").alias("n_genomes")))
w = Window.partitionBy("gtdb_species_clade_id").orderBy(desc("n_genomes"))
species_biome = (species_biome_counts
    .withColumn("rk", row_number().over(w)).filter(col("rk") == 1).drop("rk")
    .select("gtdb_species_clade_id", "biome", col("n_genomes").alias("majority_biome_n_genomes"))
    .cache())

# STEP 3 — Pfam tier
pdb_pfams = spark.table("kescience_pdb.pdb_pfam").select("pfam_id").distinct().cache()
ips_pfam = (spark.table("kbase_ke_pangenome.interproscan_domains")
    .filter("analysis = 'Pfam'")
    .select("gene_cluster_id",
            regexp_replace(col("signature_acc"), r"\.\d+$", "").alias("pfam_id"))
    .distinct()
    .cache())

per_cluster_pfam = ips_pfam.groupBy("gene_cluster_id").agg(countDistinct("pfam_id").alias("n_pfam"))
bakta_covered = (ips_pfam.join(pdb_pfams, on="pfam_id", how="inner")
    .groupBy("gene_cluster_id").agg(countDistinct("pfam_id").alias("n_covered_pfam")))
per_cluster_tier = (per_cluster_pfam
    .join(bakta_covered, on="gene_cluster_id", how="left")
    .withColumn("n_covered_pfam", when(col("n_covered_pfam").isNull(), 0).otherwise(col("n_covered_pfam")))
    .withColumn("pfam_tier",
        when(col("n_covered_pfam") == 0, lit("pfam_no_covered"))
        .when(col("n_covered_pfam") == col("n_pfam"), lit("pfam_all_covered"))
        .otherwise(lit("pfam_partial_covered"))))

gc = spark.table("kbase_ke_pangenome.gene_cluster").select(
    "gene_cluster_id", "gtdb_species_clade_id",
    "is_core", "is_auxiliary", "is_singleton")

cluster_full = (gc
    .join(per_cluster_tier.select("gene_cluster_id", "n_pfam", "n_covered_pfam", "pfam_tier"),
          on="gene_cluster_id", how="left")
    .withColumn("pfam_tier",
        when(col("pfam_tier").isNull(), lit("no_pfam_annotation")).otherwise(col("pfam_tier")))
    .withColumn("n_pfam", when(col("n_pfam").isNull(), lit(0)).otherwise(col("n_pfam")))
    .withColumn("n_covered_pfam", when(col("n_covered_pfam").isNull(), lit(0)).otherwise(col("n_covered_pfam")))
    .join(species_biome.select("gtdb_species_clade_id", "biome"),
          on="gtdb_species_clade_id", how="left")
    .withColumn("biome", when(col("biome").isNull(), lit("unassigned")).otherwise(col("biome"))))

# ============================================================================
# COLLECT ALL AGGREGATES LOCALLY
# ============================================================================
print(">>> matrix (biome × pfam_tier × is_core) ...", flush=True)
matrix_pd = (cluster_full.groupBy("biome", "pfam_tier", "is_core")
    .agg(count("*").alias("n_clusters"))
    .toPandas())
matrix_pd.to_csv(f"{OUT}/biome_pfam_matrix.csv", index=False)
print(f"  matrix rows: {len(matrix_pd)}")

print(">>> summary per biome ...", flush=True)
summary_pd = (cluster_full.groupBy("biome").agg(
    count("*").alias("n_clusters_total"),
    spark_sum(when(col("pfam_tier") == "no_pfam_annotation", 1).otherwise(0)).alias("n_no_pfam"),
    spark_sum(when(col("pfam_tier") == "pfam_no_covered", 1).otherwise(0)).alias("n_pfam_no_covered"),
    spark_sum(when(col("pfam_tier") == "pfam_partial_covered", 1).otherwise(0)).alias("n_pfam_partial"),
    spark_sum(when(col("pfam_tier") == "pfam_all_covered", 1).otherwise(0)).alias("n_pfam_all_covered"),
    spark_sum(when(col("is_core") == True, 1).otherwise(0)).alias("n_core"),
).toPandas())
for c in ["n_no_pfam", "n_pfam_no_covered", "n_pfam_partial", "n_pfam_all_covered", "n_core"]:
    summary_pd[c.replace("n_", "pct_")] = 100 * summary_pd[c] / summary_pd["n_clusters_total"]
summary_pd = summary_pd.sort_values("n_clusters_total", ascending=False)
summary_pd.to_csv(f"{OUT}/biome_summary.csv", index=False)
print(summary_pd.round(2).to_string())

print("\n>>> genome-biome map ...", flush=True)
gb_pd = genome_biome.toPandas()
gb_pd.to_csv(f"{OUT}/genome_biome.csv", index=False)
print(f"  {len(gb_pd):,} genomes")

print(">>> species-biome map ...", flush=True)
sb_pd = species_biome.toPandas()
sb_pd.to_csv(f"{OUT}/species_biome.csv", index=False)
print(f"  {len(sb_pd):,} species")

print("\n>>> top uncovered Pfams per biome ...", flush=True)
cluster_pfam_biome = (ips_pfam
    .join(gc.select("gene_cluster_id", "gtdb_species_clade_id"), on="gene_cluster_id", how="inner")
    .join(species_biome.select("gtdb_species_clade_id", "biome"), on="gtdb_species_clade_id", how="inner")
    .join(pdb_pfams.withColumn("in_pdb", lit(True)), on="pfam_id", how="left")
    .withColumn("in_pdb", when(col("in_pdb").isNull(), lit(False)).otherwise(col("in_pdb"))))
uncovered_by_biome = (cluster_pfam_biome.filter(~col("in_pdb"))
    .groupBy("biome", "pfam_id")
    .agg(countDistinct("gene_cluster_id").alias("n_clusters")))
w2 = Window.partitionBy("biome").orderBy(desc("n_clusters"))
top_uncovered_pd = (uncovered_by_biome
    .withColumn("rk", row_number().over(w2))
    .filter(col("rk") <= 20).drop("rk")).toPandas()
top_uncovered_pd.to_csv(f"{OUT}/biome_top_uncovered.csv", index=False)
print(f"  top uncovered rows: {len(top_uncovered_pd)}")

spark.stop()
print("\nALL DONE")
