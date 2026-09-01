---
type: "Summary"
description: "Practical BERDL querying, schema, analysis, and workflow pitfalls."
doc_type: short
full_text: "sources/pitfalls.md"
---

# BERDL Database: Common Pitfalls & Gotchas

## Overview

This reference catalogs failure modes and corrective practices for querying BERDL databases, analyzing large microbial datasets, and maintaining reproducible BERIL projects. It emphasizes live catalog discovery, explicit schema and type validation, Spark-first computation, access-aware error handling, and independent validation of analysis design. Relevant cross-cutting topics include [[concepts/computational-reproducibility]], [[concepts/scalable-spark-data-analysis]], [[concepts/identifier-resolution-and-crosswalks]], and [[concepts/adversarial-methodological-review]].

## Database Discovery, Access, and API Reliability

- BERDL is migrating collections from Delta underscore namespaces to Iceberg dotted namespaces. Resolve table addresses through live, access-aware catalog discovery; prefer `catalog.namespace.table` for migrated collections and fall back to the underscore form when necessary.
- Tenant names in `data_lakehouse_ingest` configurations are governance-group names, not necessarily database prefixes. Verify access with `get_group_sql_warehouse()` and inspect namespace locations when uncertain.
- Access failures should be translated into a plain permissions message identifying the table and tenant and directing users to the BERDL Tenant Browser; internal authorization errors should not be exposed to researchers.
- Direct Spark SQL is preferred over REST for large queries, joins, and aggregations. REST endpoints may time out, return transient 503/524 errors, or behave inconsistently; `/schema` is less reliable than `DESCRIBE` through `/query`.
- Tokens may expire during long sessions. On JupyterHub, refresh from `~/.berdl_kbase_session`; the correct environment variable is `KBASE_AUTH_TOKEN`.
- Avoid killing Java processes because Spark Connect runs as a Java service. Concurrent agents should use separate Git worktrees and verify `git branch --show-current` before every commit.

## Schema, Namespace, and Identifier Hazards

- Many BERDL numeric fields are stored as strings, especially in [[entities/fitness-browser]] and genome tables. Cast before comparisons, sorting, arithmetic, or statistical calculations.
- Spark SQL requires backticks around reserved column names such as `order`, `class`, and `select`.
- Never combine `DISTINCT` with aggregates without `GROUP BY`; use grouped aggregation alone.
- Pangenome taxonomy tables must be joined through `genome_id`, not `gtdb_taxonomy_id`, because the latter is stored at different taxonomy depths. `gapmind_pathways.clade_name` uses full `gtdb_species_clade_id` values, not short GTDB species names.
- Species clade IDs contain `--`. This is safe in quoted Spark SQL literals but can be rejected by the REST API; REST users may need local filtering or alternative query construction.
- Pangenome annotation joins use the appropriate level-specific keys: eggNOG `query_name` joins to `gene_cluster_id`, while Bakta and InterProScan annotations also operate at gene-cluster level. Gene clusters are species-specific and must not be compared by ID across species.
- `ncbi_env` is an entity-attribute-value table requiring filtering and pivoting; `genome_ani` uses `genome1_id`, `genome2_id`, and `ANI`; phylogenetic distance tables use bare accessions while other pangenome tables use `RS_`/`GB_` prefixes.
- GapMind requires careful aggregation: multiple rows exist per genome-pathway pair, score categories are categorical, and the best score should be selected before genome- or species-level summaries. In core scope, `score_simplified` is binary (`0.0`/`1.0`), not continuous.
- Web of Microbes action codes are actor-dependent. For organism observations, `I` and `E` encode increased or emerged compounds and define the binary `produced` state; control rows use different meanings. The 2018 snapshot lacks consumption/decreased observations, and many compounds are unidentified.

## Identifier Matching and Cross-Database Integration

Short strain names are unsafe cross-database identifiers. ENIGMA strain names matched to GTDB produced 12 incorrect genus linkages out of 32; genus consistency checks are required, and assembly accessions are preferable. More generally, cross-database joins should use stable accessions, explicit prefix normalization, and validation of expected overlap.

MetaPhlAn3 cross-cohort analyses require a taxonomy synonymy layer, not just string-format normalization. Legacy and modern genus names can create artificial abundance contrasts of approximately 28 log2-fold-change units when the same species is split into separate rows. A robust workflow parses full lineage strings, applies curated synonyms, and ultimately uses an NCBI-taxid-backed, GTDB-version-aware crosswalk.

BacDive and GTDB species concepts differ substantially: exact and suffix-stripped matching together captured 43.4% of strains in one validation, while only 10 of 31 heavy-metal-tagged strains matched species with metal-tolerance scores. Accession-based matching can improve coverage. BacDive utilization must distinguish `+`, `-`, `produced`, and `+/-`; only explicit `+`/`-` records belong in utilization percentages.

## Statistical Design and Interpretation Pitfalls

### Cohort and study confounding

CuratedMetagenomicData healthy and IBD buckets contain disjoint published sub-studies. A pooled `diagnosis + (1 | substudy)` model is structurally unidentifiable because study and diagnosis are collinear. The design-consistent alternative is a within-IBD-substudy CD-versus-nonIBD contrast followed by inverse-variance meta-analysis. Pooled CD-versus-HC results must be labeled as confounded rather than presented as adjusted estimates. This is an instance of [[concepts/batch-confounding]] and [[concepts/phylogenetic-confounding]]-like design dependence in which a nuisance structure is inseparable from the contrast of interest.

### Feature leakage from clustering

Clustering samples on taxon abundances and then testing those same taxa within clusters produces selection-on-outcome bias. In the documented case, held-out-species Jaccard values were 0.230 and 0.064 for two ecotypes, and *C. scindens* changed from nonsignificant to positive in both ecotypes under leave-one-species-out refitting. Independent within-substudy evidence reduced a 33-species candidate list to 3 robust candidates. Recommended safeguards are held-out-feature testing, leave-one-feature-out refitting, or clustering on a genuinely different functional matrix. This is a central concern for [[concepts/metabolic-ecotypes]], [[concepts/microbiome-ecotype-portability]], and [[concepts/adversarial-methodological-review]].

### Other interpretation hazards

- Codon-usage comparisons across species are confounded by GC content; use within-species comparisons or similar-GC organisms.
- PA14 represents less than 5% of CF *P. aeruginosa* virulence genotypes, so PA14 assays require validation in ExoS+ strains despite similar amino-acid catabolism.
- NaCl importance thresholds based on at least one sensitive experiment are biased when organisms have unequal experiment counts; use stricter or mean-effect thresholds and sensitivity analyses.
- Per-genome environment classification from NCBI metadata can leave 52.7% of genomes unknown; species-level majority labels provide approximately 91% coverage in the cited analysis.
- AlphaEarth embeddings cover approximately 28% of genomes and 4.6% of embedding-bearing genomes contain NaNs. Environmental and human-associated samples should be analyzed separately because pooled geographic signal is diluted by human-associated genomes. These limitations relate to [[concepts/coverage-limited-inference]], [[concepts/geospatial-coverage-gaps]], and [[concepts/geographic-distance-decay]].

## Spark, Pandas, and Scale

- Keep filtering, joining, and aggregation in Spark; `.toPandas()` should be reserved for small final outputs. Large Spark Connect results can exceed the 1 GB serialized result cap; stage large results through MinIO or Parquet.
- Do not disable Spark's automatic broadcast joins by default. A forced-shuffle setting caused a large join to hang even though the small side was suitable for broadcasting.
- Avoid pandas spatial Cartesian merges, `iterrows()`, row-wise `.apply()`, and large `explode()` operations. Batch spatial merges, vectorize with joins, and search for algebraic aggregate identities when expansion is quadratic.
- Spark DECIMAL values arrive in pandas as `decimal.Decimal`; cast to `DOUBLE` in SQL or convert pandas columns to float. Spark Connect pandas results may also require conversion to native Python lists before being registered back into Spark.
- PySpark cannot infer NumPy `str_`; cast sampled identifiers to native `str` before `createDataFrame()`.
- After long-running Spark Connect cells, temporary views may disappear following reconnection; re-register them immediately before use.
- Replace zero-valued missing measurements in NMDC abiotic data with NaN, and use the actual `_has_numeric_value` column names.
- Large jobs can outlive JupyterHub's roughly 17–25 minute idle timeout. Convert them to unbuffered scripts run with `nohup`, save intermediate checkpoints, and provide recovery/finalization scripts.
- Avoid `nbconvert --inplace` when outputs matter; it can silently leave executed notebooks with no outputs. Write to a separate output file or capture standalone script logs.

## Database-Specific Highlights

### Pangenome

The pangenome contains billion-row `gene` and junction tables, a roughly 421-million-row ANI table, a roughly 93-million-row eggNOG table, and other very large collections. Always filter by genome or species before joining. Use left joins for the 12 pangenome records whose species clades are absent from `gtdb_species_clade`, and account for 141 orphan genes. AlphaEarth, NCBI coordinates, and environmental metadata are sparse. Several referenced tables remain unavailable, including `pangenome_build_protocol`, `genomad_mobile_elements`, and `IMG_env`. These constraints shape [[concepts/pangenome-integration]], [[concepts/coverage-limited-inference]], and [[concepts/provenance-aware-data-discovery]].

### Fitness Browser

All columns are strings; `orgId` is case-sensitive; `genefitness` has approximately 27 million rows and requires organism filters. KO mapping is a two-hop join through `besthitkegg` and `keggmember`; `experiment` uses `expName`, `expGroup`, and `condition_1`; and `seedannotationtoroles` joins by `seed_desc`. Essential genes are absent from `genefitness`, so fitness-only analyses miss approximately 14.3% of protein-coding genes. ICA components should remain at or below 40% of experiment count, cosine distances should be clipped to `[0, 1]`, and ortholog extraction must cover every organism in the intended analysis. These issues affect analyses of [[concepts/fitness-conservation]], [[concepts/gene-essentiality]], [[concepts/condition-dependent-essentiality]], and [[concepts/cofitness-networks]].

### NMDC and Planet Microbe

NMDC classifier and metabolomics tables use `file_id`, but their file namespaces do not overlap. Bridge them through `omics_files_table` and `sample_id`. `taxonomy_features` is a wide matrix with numeric taxon-ID columns, not a tidy table. NMDC and Planet Microbe abundance tables use species-level names, so genus abundance requires a species-to-genus rollup before filtering. Planet Microbe `project` and `library` tables are empty, and curated and raw databases should be selected explicitly. These integration constraints are relevant to [[concepts/multi-omics-integration]], [[concepts/identifier-resolution-and-crosswalks]], and [[concepts/phenotype-resolution-matching]].

### BacDive, PhageFoundry, and GenomeDepot

BacDive joins may require explicit INT-to-STRING casts, and taxonomy columns use `tax_class` and `tax_order`. PhageFoundry separates GenomeDepot browser databases from the strain-modelling database, which contains experimental phage-host data; the strain-modelling gene table lacks functional annotations. GenomeDepot schemas contain naming differences such as `cog_class_id`, and `protect_genomedepot` uses sampled table variants. These distinctions matter for [[entities/bacdive]], [[entities/phagefoundry]], and [[concepts/genome-ecology-validation]].

### Other database notes

AlphaFold joins require removing the `UniRef100_` prefix, and roughly 9% of entries have MSA depth below 30. PDB quality fields are method-dependent and nullable. PaperBlast years and protein lengths are strings, gene identifiers span namespaces, and raw snippets require cleaning. `kbase_genomes` uses CDM UUIDs and billion-row junctions. UniRef50/90/100 collections are partial datasets and must not be treated as complete releases.

## Reproducibility and Project Workflow

- Commit notebooks alongside figures and tables. Verify that every notebook referenced in a plan or report exists in Git history; reconstruct missing notebooks from artifacts and document the reconstruction.
- Keep computed outputs flat in project `data/` rather than creating nonstandard `data/results/` directories.
- Detailed synthesis belongs in `REPORT.md`; `README.md` should remain a concise project overview linking to the report and research plan.
- Execute notebooks before committing so outputs remain available for review. Validate notebook JSON after programmatic edits because missing `outputs` or `execution_count` fields can invalidate execution.
- Preserve independent strict and relaxed analysis modes; copying one feature set into the other invalidates sensitivity analyses.
- Apply FDR correction to all actual p-value columns, including nonstandard names, and use moderate, seeded bootstrap sizes for practical runtimes.
- Treat keyword gene annotation as provisional and validate it against co-fitness or other independent evidence.
- Confirm reviewer output paths after subprocess execution and run Codex reviewers with network-enabled permissions and compact prompts referencing on-disk instructions.

## Quick Checklist

Before querying or interpreting BERDL data:

- Discover the current namespace and verify tenant access.
- Inspect schemas and confirm exact table, column, and join-key names.
- Cast string numerics and quote reserved identifiers.
- Filter billion-row tables before joins or collection.
- Normalize identifiers and validate overlap, genus, species, and accession consistency.
- Check coverage, missingness, orphan records, and duplicate grain.
- Keep large operations in Spark and stage oversized results through Parquet or MinIO.
- Test for study confounding, feature leakage, unequal experiment counts, and taxonomy synonymy.
- Use independent evidence streams before promoting exploratory findings.
- Commit executable notebooks, outputs, checkpoints, and complete reports.

## Related Concepts
- [[concepts/annotation-gap]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/resource-darkness]]
- [[concepts/shared-dispensability]]
- [[concepts/spatial-sampling-effort]]

## Entities
- [[entities/kegg]]
- [[entities/eggnog]]
- [[entities/amrfinderplus]]
- [[entities/average-nucleotide-identity]]
- [[entities/diamond]]
- [[entities/modelseed]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/uniprot]]
