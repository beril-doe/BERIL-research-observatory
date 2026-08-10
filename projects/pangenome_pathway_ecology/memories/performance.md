# Performance Notes — pangenome_pathway_ecology

<!-- [pangenome_pathway_ecology] 2026-08-10T16:57:32Z  approved-report extraction (REVIEW: REVIEW_3.md) -->

- The integrated species dataset (27,690 rows, 22 columns) was assembled by joining `pangenome`, `gapmind_pathways`, `genome`, `gtdb_species_clade`, and environment metadata from `ncbi_env`. All joins used `gtdb_species_clade_id` or `genome_id` as keys.
- Filtering to species with ≥10 genomes (2,812 species) was necessary for meaningful within-species pathway statistics.
- Statistical analysis (NB04) runs from cached CSVs without Spark in ~1 minute.
