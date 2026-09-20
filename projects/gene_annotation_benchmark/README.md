# Gene Annotation Benchmark

## Research Question

Can the Price/Fitness Browser reannotation set be converted into a balanced
gene-function benchmark that includes both successful human reannotations and
strong-fitness genes where evidence was not sufficient for a useful improved
annotation?

## Status

Active. The source-of-truth benchmark plan and schema live in:

```text
KBaseIncubator/gene-annotation-benchmark
```

This BERIL project entry records lakehouse collections, backend-compatibility
checks, and SQL pitfalls discovered while constructing the candidate sets.

## Data Sources

- `kescience_fitnessbrowser` - Fitness Browser genes, RB-TnSeq phenotypes,
  cofitness, conserved cofitness, orthologs, neighborhoods, and reported
  reannotations
- `kescience_paperblast` - curated sequence-to-paper links and literature
  snippets/summaries
- `kescience_interpro` - sequence-to-InterPro and GO mappings
- `kbase_ke_pangenome` - pangenome gene clusters, conservation, Bakta, eggNOG,
  Pfam, and InterProScan annotations

## Current Implementation Repos

- `KBaseIncubator/gene-annotation-benchmark`
- `KBaseIncubator/gene-annotation-agent`
- `KBaseIncubator/gene-agent-data-viz`
- `KBaseIncubator/BERIL-research-observatory`

## First Lakehouse Milestone

BERDL infrastructure may have migrated from the older MinIO/Delta/Spark path
to an Iceberg-backed catalog or a different gateway. The first live milestone
is backend discovery:

1. authenticate to the current BERDL query endpoint;
2. list visible catalogs and namespaces;
3. rediscover the Fitness Browser, PaperBLAST, InterPro, and pangenome table
   identifiers;
4. validate the logical keys needed by the benchmark:
   - Fitness Browser `(orgId, locusId)`
   - PaperBLAST duplicate-sequence mapping
   - InterPro sequence accessions
   - pangenome `gene_cluster_id`

Only after those checks should candidate-set SQL be run.
