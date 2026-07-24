# Research Plan: Structural Coverage Gap by Biome

## Research Question

Where does experimental (PDB) and high-confidence predicted (AlphaFold) structural coverage of the environmental microbiome fall short, once we account for biome, taxonomy, and function — and which biome × functional-category cells are the largest gaps?

## Background

Two structural resources now live in BERDL:

- **PDB (`kescience_pdb`)** — 250,741 experimental structures with resolution, R-factors, validation metrics, and 966,977 SIFTS chain-to-UniProt mappings. Direct evidence: coordinates you can trust.
- **AlphaFold (`kescience_alphafold`)** — 241M predicted structures keyed by UniProt accession, with per-entry MSA depth as a confidence proxy (MSA depth ≥ 300 correlates with pLDDT > 70 per `docs/structural_biology_memory.md`).

Both join to the BERDL pangenome (`kbase_ke_pangenome.bakta_annotations`) via the UniRef100→UniProt bridge already validated in `alphafold_msa_annotation` (38.8M gene clusters have real UniProt accessions).

The `plant_microbiome_ecotypes` project produced `genome_environment.csv` (293,059 rows) which carries `compartment`, `env_broad_scale`, `host`, and `ncbi_isolation_source` for essentially every genome in the pangenome, plus a curated `is_plant_associated` flag. `ncbi_env_pivot.csv` (279,547 rows) provides a structured EAV pivot of the isolation source text for secondary axis analysis.

Prior work (`alphafold_msa_annotation`) established that MSA depth alone predicts annotation quality (Spearman ρ = 0.756) and identified 415,603 "paradox proteins" — core clusters with msa_depth < 10. That project never distinguished structural *evidence tiers* (predicted vs. experimental) and never stratified by ecological context. This project adds both axes.

## Hypotheses

- **H0 (null):** Structural coverage rate (per gene cluster) is independent of biome once phylum and functional category are controlled.

- **H1:** Soil, subsurface, and extremophile biomes have systematically lower per-cluster PDB coverage than gut- and pathogen-associated biomes, and the gap survives phylum control. Rationale: crystallography priorities historically follow medical/model-organism relevance.

- **H2:** The AF-only-confident subset overstates coverage. Many clusters flagged AF-confident (MSA depth ≥ 300) still have no experimental homolog within 30% identity, and this overstatement is worst in under-studied biomes. Rationale: the AF confidence signal is a function of sequence-database density, which itself correlates with study intensity of the *source* biome, not the *target* biome.

- **H3:** Function predicts coverage more strongly than taxonomy. Central metabolism (glycolysis, TCA, ribosome) is well-covered across every biome; transport, secretion, and defense systems are systematically under-covered. Rationale: functional class predicts experimental difficulty (membrane proteins, large complexes) and community priority.

- **H4 (actionable):** The intersection {is_core within a biome × no PDB hit × AF present but MSA depth < 300 × functional annotation suggesting biome relevance} yields a manageable priority list (~500–1000 clusters) suitable as a crystallography / cryo-EM wishlist.

## Data Sources

| Table / File | Rows | Role |
|---|---|---|
| `kbase_ke_pangenome.gene_cluster` | 132.5M | Cluster identity, core/aux/singleton flags, species clade |
| `kbase_ke_pangenome.bakta_annotations` | 132.5M | UniRef100 bridge, product, hypothetical, EC, KEGG KO |
| `kbase_ke_pangenome.interproscan_domains` | 833M | Domain-based function fallback for un-KEGGed clusters |
| `kescience_pdb.pdb_uniprot_mapping` | 967K | SIFTS: PDB chain → UniProt (identity, coverage) |
| `kescience_pdb.pdb_entries` | 251K | Method, resolution, R-factors for each PDB entry |
| `kescience_alphafold.alphafold_entries` | 241M | AF DB ID per UniProt (presence = AF predicted) |
| `kescience_alphafold.alphafold_msa_depths` | 241M | MSA depth (confidence proxy) |
| `plant_microbiome_ecotypes/data/genome_environment.csv` | 293K | Genome → compartment, env_broad_scale, host, isolation source |
| `plant_microbiome_ecotypes/data/ncbi_env_pivot.csv` | 280K | Structured EAV pivot of isolation source (secondary axis) |
| `plant_microbiome_ecotypes/data/bacdive_isolation.csv` | 24K | Curated cat1/cat2/cat3 + extremophile flags |
| `plant_microbiome_ecotypes/data/marker_gene_clusters.csv` | 588K | Cluster → species → core/accessory/singleton |

## Join Path

```
pdb_entries ─── pdb_uniprot_mapping ───┐
                                       │
alphafold_entries ─── alphafold_msa_depths ──┐
                                             │
                    UniProt accession        │
                             │               │
                             ▼               ▼
bakta_annotations.uniref100 ─── (strip "UniRef100_") ───> UniProt
                             │
                             ▼
                    gene_cluster_id
                             │
                             ▼
                    marker_gene_clusters ─── gtdb_species_clade_id
                                                         │
                                                         ▼
                                              genome_environment ─── compartment,
                                                                     env_broad_scale
```

## Design Decisions (Locked In)

1. **Biome axis:** `compartment` + `env_broad_scale` from `genome_environment.csv` as primary. `ncbi_env_pivot.csv` and `bacdive_isolation.csv` used as secondary sanity check and for extremophile flagging.
2. **PDB hit tiers (two):**
   - **Direct hit:** SIFTS identity ≥ 95% AND coverage ≥ 80% of UniProt length.
   - **Homolog hit:** 30% ≤ identity < 95% (any coverage).
   - **No PDB:** no SIFTS row.
3. **AF confidence tiers (two):**
   - **AF-confident:** entry present AND `msa_depth ≥ 300`.
   - **AF-low-confidence:** entry present AND `msa_depth < 300`.
   - **No AF:** no entry (typically UniParc-only UniRef100).
4. **Phase 3 scope:** Top-100 per biome, each candidate annotated with predicted domain, oligomeric-state guess, MSA depth, core/accessory status, prevalence.

## Phases

### NB01 — Per-cluster coverage extraction (Spark, JupyterHub)

For every gene cluster with a UniProt-linkable UniRef100, assign one PDB tier and one AF tier.

```python
from berdl_notebook_utils.setup_spark_session import get_spark_session
from pyspark.sql.functions import regexp_replace, col, when, lit, max as spark_max

spark = get_spark_session()

# Filter clusters to those with real UniProt bridge (per alphafold_msa_annotation validation)
bakta = (spark.table("kbase_ke_pangenome.bakta_annotations")
    .select("gene_cluster_id", "uniref100", "hypothetical", "ec", "kegg_orthology_id", "product")
    .filter("uniref100 IS NOT NULL AND uniref100 NOT LIKE 'UniRef100_UPI%'")
    .withColumn("uniprot_accession", regexp_replace(col("uniref100"), "UniRef100_", ""))
)

# PDB: aggregate to best identity per UniProt (SIFTS is chain-level; a UniProt may map to many chains)
pdb_map = (spark.table("kescience_pdb.pdb_uniprot_mapping")
    .select("uniprot_accession", "pdb_id", "identity_pct", "coverage_pct")
)
pdb_best = pdb_map.groupBy("uniprot_accession").agg(
    spark_max("identity_pct").alias("best_identity"),
    spark_max("coverage_pct").alias("best_coverage"),
)

# AF confidence
af = (spark.table("kescience_alphafold.alphafold_entries")
    .select("uniprot_accession", "alphafold_id")
    .join(spark.table("kescience_alphafold.alphafold_msa_depths")
              .select("uniprot_accession", "msa_depth"),
          on="uniprot_accession", how="left")
)

# Assign tiers
per_cluster = (bakta
    .join(pdb_best, on="uniprot_accession", how="left")
    .join(af, on="uniprot_accession", how="left")
    .withColumn("pdb_tier",
        when((col("best_identity") >= 95) & (col("best_coverage") >= 80), lit("direct"))
        .when((col("best_identity") >= 30) & (col("best_identity") < 95), lit("homolog"))
        .otherwise(lit("none")))
    .withColumn("af_tier",
        when(col("alphafold_id").isNull(), lit("none"))
        .when(col("msa_depth") >= 300, lit("confident"))
        .otherwise(lit("low_confidence")))
    .select("gene_cluster_id", "uniprot_accession",
            "pdb_tier", "af_tier", "msa_depth",
            "hypothetical", "ec", "kegg_orthology_id", "product")
)

per_cluster.write.mode("overwrite").parquet(
    "s3a://cdm-lake/.../structural_coverage_biome/data/per_cluster_coverage.parquet"
)
```

Expected output: ~38M rows.

### NB02 — Biome stratification & aggregation (Spark, JupyterHub)

Join per-cluster coverage to `marker_gene_clusters` (species) → `genome_environment` (biome), then aggregate to a biome × functional-category matrix.

```python
per_cluster = spark.read.parquet(".../per_cluster_coverage.parquet")

# Species assignment (many clusters ↔ many species; take per species/cluster row)
mgc = spark.read.csv(".../marker_gene_clusters.csv", header=True, inferSchema=True) \
    .select("gene_cluster_id", "gtdb_species_clade_id", "is_core", "is_auxiliary", "is_singleton")

# Genome env — need to pivot from genome to species (majority-vote compartment per species)
genome_env = spark.read.csv(".../genome_environment.csv", header=True, inferSchema=True) \
    .select("genome_id", "gtdb_species_clade_id", "compartment", "env_broad_scale")
# NOTE: apply GTDB prefix normalization here — see pitfalls
species_env = genome_env.groupBy("gtdb_species_clade_id", "compartment").count() \
    .withColumn("rank", ...) \
    .filter("rank = 1").drop("rank", "count")

# Full join
biome_coverage = (per_cluster
    .join(mgc, on="gene_cluster_id", how="inner")
    .join(species_env, on="gtdb_species_clade_id", how="inner")
)

# Aggregate to biome × KEGG-KO-parent (or COG category as fallback)
agg = biome_coverage.groupBy("compartment", "kegg_orthology_id", "is_core") \
    .agg(
        count("*").alias("n_clusters"),
        sum(when(col("pdb_tier") == "direct", 1).otherwise(0)).alias("n_pdb_direct"),
        sum(when(col("pdb_tier") == "homolog", 1).otherwise(0)).alias("n_pdb_homolog"),
        sum(when(col("af_tier") == "confident", 1).otherwise(0)).alias("n_af_confident"),
    )
agg.coalesce(1).write.csv(".../biome_coverage_matrix.csv", header=True, mode="overwrite")
```

### NB03 — Statistical model & visualization (local, from cached CSVs)

- Fisher's exact per biome × function cell for PDB-direct enrichment/depletion vs. global rate
- Logistic regression: `pdb_hit ~ biome + phylum + kegg_module + is_core + log(cluster_size)` with cluster-robust SEs by species (per `plant_microbiome_ecotypes` C1 pattern)
- Heatmap: biome × KEGG-module coverage rate
- Bar plot: biome-level PDB-direct rate with bootstrap 95% CIs
- Model-vs-data plot: fitted coverage rate vs. observed, colored by biome (validate no biome is an outlier the model can't explain)

### NB04 — Prioritized gap list (local, from cached CSVs)

For each biome (compartment × env_broad_scale combination with ≥ 100 genomes):
1. Filter to clusters: is_core = True AND pdb_tier = "none" AND af_tier IN ("confident", "low_confidence") AND biome membership.
2. Score = biome_prevalence × (1 + is_af_low_confidence) × functional_relevance_flag
3. Take top 100.
4. Annotate each with: predicted Pfam domain(s), predicted transmembrane-helix count (if any), oligomeric-state hint from ChEMBL/InterPro, MSA depth, species range.
5. Cross-reference against `alphafold_msa_annotation` paradox protein list — report overlap fraction.

Output: `data/priority_gap_list.csv` with ~500–1000 rows total.

## Performance & Pitfalls Baked In

- **GTDB prefix mismatch** (`DATA_INVENTORY.md` pitfall 4): `genome_environment.csv` uses `RS_GCF_*`/`GB_GCA_*`; some BERDL tables use bare `GCF_*`/`GCA_*`. Add the prefix before joining any tree/pair table.
- **`bakta_pfam_domains` silently drops half of secretion-system Pfams** (pitfall 1): if Phase 3 candidates include secretion/T*SS annotations, cross-check via `interproscan_domains.signature_acc`.
- **Versioned Pfam IDs** (pitfall 2): use `LIKE 'PF00771%'` not equality.
- **SIFTS is chain-level:** collapse to protein (take best identity × coverage across chains) before tier assignment. Done in NB01.
- **Biome-sample imbalance:** gut/human >> soil/subsurface >> marine. Always report per-cluster rates with bootstrapped CIs, not raw counts.
- **UniRef100 UPI-prefixed IDs don't map to AlphaFold** (from `alphafold_msa_annotation`): filter these before joining. ~22.7M rows.
- **Spark cross-database joins fail via REST API** (from `alphafold_msa_annotation`): use Spark tables, not the REST client.
- **Cluster-level vs. protein-level:** MSA depth is per-representative-sequence — within-cluster diversity is invisible. Report this caveat with any AF confidence claim.

## Expected Outcomes

| Hypothesis | If supported | If not supported |
|---|---|---|
| H1 | Soil/subsurface PDB-direct rate < gut PDB-direct rate by >2× after phylum control | PDB coverage tracks taxonomy, not biome |
| H2 | ≥ 30% of AF-confident clusters in under-studied biomes lack a PDB homolog | AF confidence is a good coverage proxy everywhere |
| H3 | Function beats biome in the logistic model (larger coefficient magnitude, higher partial R²) | Biome dominates; function is secondary |
| H4 | Priority list has 500–1500 clusters with defensible biome relevance | Either too few (nothing new) or too many (need tighter filter) |

## Confounders & Limitations

- **Study intensity confounds biome:** Model organisms like *E. coli* and *B. subtilis* skew both toward "gut/host" biomes AND toward high PDB coverage. Phylum control partially addresses this but not fully; discuss in report.
- **AlphaFold DB coverage bias:** 22.7M of 61.5M UniRef100-linked clusters are UPI-only (no AF). If UPI-only skews toward under-sequenced biomes, the AF-tier axis becomes biome-confounded. Sanity check in NB02.
- **`compartment` is plant-centric:** heavily populated for plant biomes, sparser for marine/subsurface. `env_broad_scale` is broader but coarser. Report results for both axes and note where they diverge.
- **Gene cluster ↔ species is many-to-many:** a cluster can be core in one species and singleton in another. Use `marker_gene_clusters.is_core` at the species-cluster pair level, not the cluster level, when computing biome-conditioned core status.

## Revision History

- **v0** (2026-07-24): Initial plan. Design choices locked via interactive review with Justin: compartment+env_broad_scale axis, two-tier PDB hits (95%/30%), top-100 per biome for Phase 3.

## Authors

- Justin Reese | ORCID: 0000-0002-2170-2250 | Lawrence Berkeley National Laboratory
