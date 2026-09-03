---
type: "Concept"
sources: ["summaries/soil_metal_functional_genomics__REPORT.md", "summaries/soil_frontier_genomics__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/pitfalls.md"]
description: "Patterns for reliable, efficient Spark-based analysis of large BERDL datasets."
---

# Scalable Spark Data Analysis

Scalable Spark data analysis is the practice of keeping large-data operations distributed, minimizing driver-side collection, and adapting queries and workflows to BERDL’s table sizes, storage layout, and Spark Connect behavior. It is closely related to [[concepts/scalable-spark-data-analysis]], [[concepts/computational-reproducibility]], [[concepts/provenance-aware-data-discovery]], and [[concepts/identifier-resolution-and-crosswalks]].

## Core Principle: Compute Near the Data

Filtering, joining, and aggregation should occur in Spark before data are collected into pandas. Calling `.toPandas()` transfers the complete result to the driver and can be slow or cause out-of-memory failures, whereas Spark DataFrame operations keep intermediate computation distributed. [src: pitfalls]

For large pangenome tables, queries should apply restrictive filters such as `genome_id`, species, or organism before joining. The `gene` and `gene_genecluster_junction` tables each contain approximately 1 billion rows, while other large tables include `genome_ani` at approximately 421 million rows, `eggnog_mapper_annotations` at approximately 93 million rows, and `gapmind_pathways` at approximately 305 million rows. [src: pitfalls]

The REST API is suitable for small one-off queries, but direct `spark.sql()` is preferred for queries involving more than 1 million rows, large joins, or large aggregations because REST requests can time out or return transient failures. [src: pitfalls] This operational distinction supports [[concepts/provenance-aware-data-discovery]] because query reliability and access context affect whether an analysis can be reproduced.

## Query Planning and Join Strategy

Spark’s optimizer should generally be allowed to choose broadcast joins. Setting `spark.sql.autoBroadcastJoinThreshold = -1` can be harmful: in one documented job, disabling automatic broadcasting caused a 13.7-million-row by 18,000-row join to wait on an unnecessary shuffle for more than 17 minutes. [src: pitfalls]

Small filter tables can be registered as temporary views and explicitly broadcast with SQL hints when automatic detection is insufficient. Broadcast hints improved a billion-row pangenome junction workflow by approximately 8% in the documented profiling, although the underlying unpartitioned tables still required full scans. [src: pitfalls]

The main performance bottleneck in some genome-by-gene-cluster workflows is storage layout rather than pandas conversion: the `gene` and `gene_genecluster_junction` tables are not partitioned by the most useful filtering keys, so each species query can require a large scan. [src: pitfalls] Extracted matrices should therefore be cached as files and reused rather than rebuilt for every downstream analysis. [src: pitfalls]

## Avoiding Driver and Pandas Bottlenecks

Spark Connect has a serialized result-size limit of 1 GB in the documented environment. Raising `spark.driver.maxResultSize` with a runtime `SET` command cannot change this limit after the session has started. [src: pitfalls] A practical workaround is to write the distributed result to MinIO or Parquet and read it back through Spark, rather than collecting the large result directly through Spark Connect. [src: pitfalls]

Pandas spatial merges can create a Cartesian product before a distance filter is applied. In one gene-neighborhood workflow, an intermediate merge reached approximately 24 million rows and required roughly 9 GB of working memory, exceeding a 16 GB driver. [src: pitfalls] Recommended alternatives are batching focal features, pushing range predicates into Spark, or reducing the analysis scope. [src: pitfalls]

Row-wise pandas operations do not scale well. A documented `iterrows()` workflow over 27,000 focal features ran for more than 30 minutes, whereas a vectorized merge and boolean filter completed in approximately 10 seconds. [src: pitfalls] Similarly, filtering a 961,000-row DataFrame with row-wise `.apply()` was much slower than an equivalent merge on key columns. [src: pitfalls]

Exploding records can also create avoidable quadratic growth. A tree-based donor-inference workflow would have expanded 6.3 million events into approximately 126 million rows and an estimated 19 GB DataFrame; an algebraic reformulation using total recipient events minus recipient events for each candidate genus avoided the expansion and completed in 142 seconds. [src: pitfalls] This illustrates a general optimization strategy: reformulate aggregate calculations so that bounded combinations are summarized rather than explicitly enumerated.

## Type and Schema Discipline

Spark SQL frequently exposes data types that differ from pandas or Python expectations. DECIMAL columns arrive in pandas as `decimal.Decimal`, and arithmetic with floats can fail; casting to `DOUBLE` in SQL is preferred. [src: pitfalls] Aggregates such as `AVG()` over integer or decimal literals should also be explicitly cast to `DOUBLE`. [src: pitfalls]

Numeric fields in several BERDL databases are stored as strings, so comparisons, sorting, and arithmetic require explicit casts. This applies broadly to the Fitness Browser and also affects coordinates, lengths, and other fields in genome collections. [src: pitfalls]

NumPy string scalars produced by `np.random.choice()` cannot always be inferred by PySpark. Converting sampled identifiers to native Python `str` values before calling `createDataFrame()` prevents schema-inference failures. [src: pitfalls]

Pandas-to-Spark round trips can fail after `.toPandas()` on a Spark Connect DataFrame because columns may be backed by PyArrow `ChunkedArray` objects. The preferred solution is to perform filtering and joins directly in Spark SQL; for small unavoidable round trips, convert columns to native Python lists first. [src: pitfalls]

## Session Reliability and Checkpointing

Spark Connect temporary views can disappear when the server reconnects during a long-running cell. A Python variable may remain available while the server-side view is gone, so temporary views should be re-registered immediately before cells that use them in joins. [src: pitfalls]

JupyterHub kernels can be silently killed after approximately 17–25 minutes without user activity. Long-running analyses should be converted to standalone Python scripts, launched with unbuffered logging, and structured to write intermediate Parquet or other checkpoints. [src: pitfalls]

Notebook execution itself requires care. On the documented JupyterHub environment, `jupyter nbconvert --inplace` may exit successfully while leaving an executed notebook with zero cell outputs. Writing to a separate output notebook or running the equivalent Python script with redirected logs preserves an audit trail. [src: pitfalls] These practices directly support [[concepts/computational-reproducibility]] and [[concepts/adversarial-methodological-review]].

## Scale-Aware Statistical Workflows

Large data volume does not remove the need for design validation. Pooled case-control microbiome analyses can be structurally confounded when study membership is perfectly aligned with diagnosis; in that setting, a random-effects model cannot identify an independent diagnosis effect. [src: pitfalls] Within-study contrasts and meta-analysis are more defensible alternatives, connecting scalable computation with [[concepts/batch-confounding]] and [[concepts/phylogenetic-confounding]].

Clustering and differential-abundance analysis must also be separated by feature space or validated with held-out features. Clustering samples on taxa and testing those same taxa within clusters creates feature leakage, so a computationally efficient pipeline can still produce biased biological conclusions. [src: pitfalls] This is an application of [[concepts/adversarial-methodological-review]] and [[concepts/evidence-triangulation]].

## Practical Workflow

1. Discover the current BERDL namespace and verify access before constructing queries. [src: pitfalls]
2. Inspect schemas and confirm data types, identifier formats, table grain, and join keys. [src: pitfalls]
3. Filter large tables as early as possible, preferably on partition-aligned keys such as species, genome, or organism. [src: pitfalls]
4. Keep joins, aggregations, and type conversions in Spark; collect only compact final summaries. [src: pitfalls]
5. Use broadcast hints for genuinely small sides of large joins, but do not disable the optimizer globally. [src: pitfalls]
6. Replace row-wise pandas operations, large Cartesian merges, and unnecessary `explode()` calls with vectorized, batched, or algebraic alternatives. [src: pitfalls]
7. Write checkpoints for long jobs and retain executable notebooks or scripts with logs. [src: pitfalls]
8. Validate coverage, missingness, identifier overlap, confounding, and leakage before interpreting results. [src: pitfalls]

## Open Directions

- Benchmark partitioning or materialized filtered tables for the largest pangenome joins to determine which keys most reduce repeated scans. [src: pitfalls]
- Compare MinIO-staged Parquet workflows with direct Spark Connect collection across result sizes to establish practical collection thresholds. [src: pitfalls]
- Develop reusable BERDL utilities that detect string numerics, DECIMAL outputs, identifier-prefix mismatches, and temporary-view loss before downstream analysis. [src: pitfalls]
- Extend automated pipeline checks to flag study-diagnosis collinearity and same-feature clustering/testing before statistical results are produced. [src: pitfalls]

See [[summaries/pitfalls]] for the complete catalog of BERDL querying, analysis, and workflow failure modes.

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]

See also: [[summaries/soil_frontier_genomics__REPORT]]

See also: [[summaries/soil_metal_functional_genomics__REPORT]]