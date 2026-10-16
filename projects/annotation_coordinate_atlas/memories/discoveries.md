# Discoveries — annotation_coordinate_atlas

<!-- [annotation_coordinate_atlas] 2026-10-16T16:53:46Z  approved-report extraction (REVIEW: REVIEW_15.md) -->

- A table's name can misstate its coordinate system at scale: `nmdc.results.pfam_annotation_gff`
  (2.68B rows) is named `_gff` but stores amino-acid coordinates — confirmed by
  `end − start + 1 == alignment_length` — plus HMM-model coordinates in the same row.
- "Has coordinates" and "can be joined to genes by position" are distinct table properties. In
  BERDL only 6 of 17 coordinate-bearing region tables satisfy the second — and one of those six
  was initially misjudged as unusable because its bridge table was not looked for.
- `kbase.ke_pangenome.interproscan_domains` carries 18 signature databases in one table,
  discoverable only from `DISTINCT analysis` — no column name enumerates them.
- Coordinates can hide inside a string: `kbase.content.c_<genome>_features.location` holds
  `[[contig, start, strand, length]]` as JSON, with SEED ontology terms in `ontology_terms`.
  No column name discloses either, so both semantic catalogs and name-based regexes miss it.
- Pangenome domain tables (`interproscan_domains`, `bakta_pfam_domains`) key on *cluster
  representatives*, not genome genes, so their protein coordinates cannot reach a contig
  without a cluster-member mapping.
- `nmdc.metadata.genome_feature_set` has the most complete GFF3 schema in BERDL and 0 rows —
  a schema promising data that does not exist.
- Automated catalog labels can be right about vocabulary and wrong about cardinality:
  `bakta_annotations.go` holds `GO:0000287;GO:0008927;…`, so `WHERE go = 'GO:0006064'`
  silently matches nothing despite a correct `go_term` label.
