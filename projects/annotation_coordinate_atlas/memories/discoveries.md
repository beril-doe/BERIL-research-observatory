# Discoveries — annotation_coordinate_atlas

<!-- [annotation_coordinate_atlas] 2026-10-23T13:24:35Z  approved-report extraction (REVIEW: REVIEW_16.md) -->

- A table's name can misstate its coordinate system at scale: `nmdc.results.pfam_annotation_gff`
  (2.68 billion rows) is named `_gff` but stores amino-acid coordinates, confirmed by
  `end − start + 1 == alignment_length`, plus HMM-model coordinates in the same row.
- "Has coordinates" and "can be joined to genes by position" are distinct table properties. In
  BERDL 13 of 23 coordinate-bearing annotation tables satisfy the second, but only 4 of the 14
  region-annotation tables do, all in `kescience.mgnify`. The other region tables are in protein
  coordinates (9) or have no gene table in their database (`refdata.smag.bgc`).
- A table's joinability depends on its database, not only its own columns:
  `kbase.genomes.feature` has no sequence column, and `kbase.genomes.contig_x_feature` places
  each of its 1,011,650,903 features on a contig.
- `kbase.ke_pangenome.interproscan_domains` carries 17 signature databases in one table,
  discoverable only from `DISTINCT analysis`; no column name enumerates them.
- Coordinates can hide inside a string: `kbase.content.c_<genome>_features.location` holds
  `[[contig, start, strand, length]]` as JSON, with SEED ontology terms in `ontology_terms`.
  No column name discloses either, so both semantic catalogs and name-based regexes miss it.
- Pangenome domain tables (`interproscan_domains`, `bakta_pfam_domains`) key on *cluster
  representatives*, not genome genes, so their protein coordinates cannot reach a contig
  without a cluster-member mapping.
- `nmdc.metadata.genome_feature_set` has the most complete GFF3 schema in BERDL and 0 rows.
- Automated catalog labels can be right about vocabulary and wrong about cardinality:
  `eggnog_mapper_annotations.KEGG_Reaction` holds `R01505,R04533,…`, so an equality predicate on
  one reaction silently matches nothing despite a correct `kegg_reaction` label.
