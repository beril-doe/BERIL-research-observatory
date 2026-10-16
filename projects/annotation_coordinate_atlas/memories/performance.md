# Performance Notes — annotation_coordinate_atlas

<!-- [annotation_coordinate_atlas] 2026-10-16T16:53:46Z  approved-report extraction (REVIEW: REVIEW_15.md) -->

- Live `DESCRIBE` across the whole accessible catalog is cheap: 826 tables / 67,587 columns in
  ~110 s (0.13 s/table). Building an independent schema ground truth is affordable; there is
  no need to trust a catalog's column list for this purpose.
- Iceberg `COUNT(*)` is metadata-served and returns in seconds even at 2.68B rows — 60 tables
  counted in under 30 s. Compute row counts in the notebook that reports them; caching them to
  a file is how a chain goes stale (see Correction 5).
- Value sampling for label adjudication should use `SELECT col ... WHERE col IS NOT NULL LIMIT
  n` (limit pushdown, no shuffle). Avoid `DISTINCT`, which forces a shuffle on billion-row
  tables.
- A 12-value sample is too small for format adjudication: placeholder-heavy columns (`-`,
  `nan`, `None`) return all-sentinel samples and produce false "mislabelled" verdicts. 60
  values reduced sentinel-only outcomes from 7 to 1.
- `kescience.mgnify.gene_bgc` and friends are partitioned by `biome_id`; filter on it. The
  whole of `gene_bgc` (35,354 rows) is the `soil` biome.

---
