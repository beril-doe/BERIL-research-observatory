# References

## Prior BERIL projects (direct dependencies / distinctions)

- `projects/alphafold_msa_annotation/` — Established the UniRef100→UniProt→AlphaFold bridge and produced the "paradox protein" list (415K core clusters with msa_depth < 10). This project reuses the bridge and cross-references the paradox list in Phase 3 (NB04).
- `projects/plant_microbiome_ecotypes/` — Source of `genome_environment.csv`, `ncbi_env_pivot.csv`, `bacdive_isolation.csv`, `marker_gene_clusters.csv`. Documented most of the pitfalls we bake into NB01–NB02.
- `projects/truly_dark_genes/` — Complementary lens: they characterize hypothetical proteins by annotation depth; we characterize by structural evidence tier.
- `projects/functional_dark_matter/` — Has some biogeographic profiles for dark genes but no PDB/AF cross-link. We fill that gap.

## Data collections

- `data/alphafold_collection/README.md` — AlphaFold ingestion (241M entries, model_version=6)
- `data/pdb_collection/README.md` — PDB ingestion (250K entries + 967K SIFTS UniProt mappings + validation metrics)
- `data/structural_biology/README.md` — Structure-determination project schema + Phenix skill

## External resources

- **SIFTS** — https://www.ebi.ac.uk/pdbe/docs/sifts/ — PDB-to-UniProt residue-level mapping used as our PDB tier source.
- **AlphaFold Protein Structure Database** — https://alphafold.ebi.ac.uk/ — 241M predicted structures, keyed by UniProt.
- **PDB RCSB** — https://data.rcsb.org/ — GraphQL API used to populate `kescience_pdb.pdb_entries` and `pdb_validation`.
- **ENVO ontology** — http://www.obofoundry.org/ontology/envo.html — reference for biome vocabulary; `ncbi_env_pivot.csv` is ENVO-adjacent.

## Structural biology literature

- Jumper et al. 2021 — "Highly accurate protein structure prediction with AlphaFold." *Nature* 596:583. Establishes pLDDT + MSA depth as confidence signals.
- Terwilliger et al. 2023 — "AlphaFold predictions are valuable hypotheses..." *Nat. Methods*. Argues AF models complement but don't replace experimental structures. Motivates our two-tier separation.
- Bordin et al. 2023 — "AlphaFold2 reveals commonalities and novelties in protein structure space." Systematic AF vs. PDB comparison at family level.
- Varadi et al. 2022 — "AlphaFold Protein Structure Database." *NAR* 50:D439. AlphaFold DB release paper.

## Ecological / pangenome context

- Almeida et al. 2019 — "A new genomic blueprint of the human gut microbiota." Establishes the gut PDB overrepresentation this project quantifies.
- Nayfach et al. 2021 — "A genomic catalog of Earth's microbiomes." Environmental genome scale-up that motivates the coverage-gap question.
