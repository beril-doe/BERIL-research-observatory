# Performance Notes — wastewater_evidence

<!-- [wastewater_evidence] 2026-10-23T17:11:01Z  approved-report extraction (REVIEW: REVIEW_5.md) -->

- `kbase.ontology_source.entailed_edge` makes ENVO subclass closure a single
  cheap join; seeding by label and expanding by closure took about 5 seconds
  against the 42.9M-row `statements` table.
- `nmdc.ncbi_biosamples.content_pairs_aggregated` (66.4M rows of
  `harmonized_name` × `content` × `biosample_count`) is the right table for
  exact-value background frequencies. It avoids a full scan of the 51.7M-row
  `biosamples_flattened` per candidate term.
- The Spark Connect ingress returns HTTP 413 for a single large local relation.
  Creating a DataFrame of ~10k rows must be chunked at about 1,000 rows per
  request into separate temp views, then unioned server-side.
