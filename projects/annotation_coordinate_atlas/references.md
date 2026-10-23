# References — annotation_coordinate_atlas

Two literatures bear on this project: dataset-discovery/metadata-quality (for the
SemCat assessment) and biosynthetic gene cluster mining (for the downstream use
case that motivates the coordinate requirement).

## Dataset discovery and semantic metadata catalogs

- **Paton NW, Chen J, Wu Z (2023). Dataset Discovery and Exploration: A Survey.**
  *ACM Computing Surveys*. doi:10.1145/3626521 — 46 citations.
  The directly relevant framing. Surveys dataset search, data navigation, data
  annotation and **schema inference**, and names the dimensions along which such
  systems are compared. It supplies the standard vocabulary for grading SemCat:
  discovery (finding candidate tables) vs exploration (understanding their
  properties and relationships) are separate capabilities that can succeed or
  fail independently.

- **Bianchini D, De Antonellis V, Garda M (2023). A semantics-enabled approach for
  personalised Data Lake exploration.** *Knowledge and Information Systems*.
  doi:10.1007/s10115-023-02014-1.
  PERSEUS builds a semantic metadata catalog over a data lake, with explicit
  "tools and metrics to ease the annotation of Data Lake metadata". Same design
  posture as SemCat. Useful for the point that annotation coverage is a known
  weak link in these architectures, not a BERDL-specific defect.

- **Masmoudi M et al. (2024). Semantic Data Integration and Querying: A Survey and
  Challenges.** *ACM Computing Surveys*. doi:10.1145/3653317.
  Background on join discovery as part of semantic data integration. Not cited in
  REPORT.md. (SemCat records verified single-column joins in its `edges` table and
  composite-key joins in `verified_joins`; REPORT.md gives the counts for the catalog
  version measured.)

## Biosynthetic gene clusters — why coordinates matter

- **Gilchrist CLM et al. (2021). cblaster: a remote search tool for rapid
  identification and visualization of homologous gene clusters.**
  *Bioinformatics Advances*. doi:10.1093/bioadv/vbab016 — 306 citations.
  The best statement of the downstream use case the user named. cblaster's whole
  premise is detecting **collocated** genes — which requires, per gene, a
  sequence/contig identifier and a position in a shared coordinate frame. This is
  the functional requirement the census tests each table against: a table
  with Pfam hits but no genome coordinates cannot support a cblaster-style query,
  however rich its annotations.

- **Jørgensen TS et al. (2024). A treasure trove of 1034 actinomycete genomes.**
  *Nucleic Acids Research*. doi:10.1093/nar/gkae523.
  Demonstrates why *complete* assemblies and synteny matter for BGC work —
  documents the structured chromosomal location of core genes vs the distal
  location of specialized-metabolite BGCs in *Streptomyces*. Positional
  information carries biology; a coordinate-free annotation table discards it.

- **van der Hooft JJJ et al. (2020). Linking genomics and metabolomics to chart
  specialized metabolic diversity.** *Chemical Society Reviews*.
  doi:10.1039/d0cs00162g — 232 citations.
  Background on BGC/natural-product mining at scale and the MIBiG reference set.
  Relevant because `kescience.mgnify.gene_bgc` carries `nearest_mibig` and
  `nearest_mibig_class`, and `refdata.smag.bgc` carries BiG-SCAPE classes
  (`big_scape_class`, `gcf_class`) — so both tables are expressed in this
  literature's vocabulary.

- **Shi Y-M et al. (2022). Global analysis of biosynthetic gene clusters reveals
  conserved and unique natural products in entomopathogenic nematode-symbiotic
  bacteria.** *Nature Chemistry*. doi:10.1038/s41557-022-00923-2.
  Example of the pangenome + BGC sequence-similarity-network analysis that the
  `refdata.smag.bgc` family-number/GCF columns are designed to support. Background
  only; not cited in REPORT.md.

- **Hurlbert SH (1984). Pseudoreplication and the design of ecological field
  experiments.** *Ecological Monographs* 54(2):187–211. doi:10.2307/1942661.
  The standard statement of pseudoreplication: treating non-independent observations
  as independent inflates *n*. Cited in REPORT.md for counting cloned staging tables
  once (per `schema_sig`) and repeat-domain proteins once.

## Note on search coverage

Searched OpenAlex, Semantic Scholar, arXiv, and PubMed via `paper-search-mcp`.
PubMed and Semantic Scholar returned 0 results for both queries in this session
(the arXiv results for the metadata query were off-topic false matches — Byzantine
SGD, remote sensing — and are excluded). So this list is OpenAlex-derived and is
not an exhaustive review; it is sufficient framing for a data-census project,
where the primary evidence is the lakehouse itself rather than the literature.
