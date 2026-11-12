# Performance Notes — annotation_coordinate_atlas

<!-- [annotation_coordinate_atlas] 2026-10-23T13:24:35Z  approved-report extraction (REVIEW: REVIEW_16.md) -->

- A live `DESCRIBE` sweep of the accessible catalog is cheap: 840 tables and 67,910 columns in
  49 s. An independent schema ground truth is affordable, so there is no need to trust a
  catalog's column list for this purpose.
- Iceberg `COUNT(*)` is metadata-served: 60 census tables, up to 2.68 billion rows, are counted
  in 10 s. Compute row counts in the notebook that reports them rather than caching them in a
  file, which is how a chain goes stale.
- Value sampling: `SELECT col ... WHERE col IS NOT NULL LIMIT n` is the cheapest query but has no
  row-order guarantee, so repeated runs adjudicate different values. The audit instead uses
  `SELECT DISTINCT col ... ORDER BY xxhash64(col) LIMIT 60`, which is deterministic and diverse.
  `DISTINCT` forces an aggregation, so on columns where SemCat reports `ndv > 100,000` a
  hash-bucket prefilter (`pmod(xxhash64(col), 256) = 0`) bounds its cost. NB03 runs in 394 s.
- Uniqueness on a billion-row key can be tested exactly on a subset by hashing the key:
  every copy of a `feature_id` lands in the same `pmod(xxhash64(feature_id), 1024)` bucket. The
  bucket check over both 1,011,650,903-row `kbase.genomes` tables takes 449 s.
- Self-join checks sample whole contigs by hashing the contig ID, so every gene on a sampled
  contig is present. The 1,895,015,043-row `bvbrc_feature_fact` takes 302 s at a 1/2^20
  sample.
- `kescience.mgnify.gene_bgc` and its sibling tables are partitioned by `biome_id`; filter on it.
  All 35,354 `gene_bgc` rows are in the `soil` biome.

---
