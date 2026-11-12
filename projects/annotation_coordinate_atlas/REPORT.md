# Report: Gene and Protein Function Annotations in BERDL, with Coordinates

**Status:** revised for review · **Date:** 2026-10-22 · **Lakehouse read:** 2026-10-22 ·
**SemCat measured:** `globalusers.semantic_catalog` catalog generated 2026-10-21T16:33:03Z
(regenerated 2026-10-21T17:49:36Z), `code_version` 0.32.2, read through Spark. The SemCat CLI
(`/opt/conda/bin/semcat`) used for two `join-keys` checks in NB04 prints no version from inside
the notebook kernel, only a warning that three semcat installs are on the path, so its version
and local catalog are not pinned here. A log kept outside this project
(`semcat-demo-2026-10-22.log`) records the same two `join-keys` results under `semcat --version`
0.33.0.

All four notebooks were executed in order, in one run, against that snapshot. Every number
below comes from a saved notebook output or a file in `data/`.

A census of BERDL tables that assign function to genes and proteins or annotate regions of
genomes, genes and proteins; a test, by query, of whether their coordinates can be used for
collocation; and a graded assessment of SemCat as the instrument for finding them.

---

## Key Findings

### 1. 13 of 23 coordinate-bearing tables can be placed against genes by position, but only 4 of the 14 region-annotation tables can, all in `kescience.mgnify`

![Coordinate frame map](figures/coordinate_frame_map.png)

"Has a start, an end and a strand" and "can answer *which genes sit near this region*" are
different properties, and in BERDL they come apart for region annotations.

**Population.** A census table is *coordinate-bearing* if it has a positional span: a start and
an end, a start and a length, or a packed location string holding them. A sequence reference or
a strand alone does not qualify. By that rule 23 of the 51 census tables are coordinate-bearing
(NB02). `kbase.nmdc_arkin.metatranscriptomics_gold`, which names a scaffold and a strand but has
no start or end, is not.

**Rule.** A table is *joinable to genes by position* when an interval predicate in SQL places its
rows against gene rows on the same nucleotide sequence identifier, and a query in NB04 §5 shows
it doing so. Three routes count:

- **direct**: a region table and a gene table in the same database share the sequence
  identifier, and an interval join (±5 kb) returns genes;
- **self**: the table's rows are themselves genes, so a self-join on a hash sample of whole
  contigs must return neighbouring genes within ±5 kb. This is how a gene table that also
  carries function (BV-BRC, IMG/VR) answers "what is next to this gene";
- **bridged**: the sequence identifier comes from one bridge table that maps each row to exactly
  one sequence, with the 1:1 property checked.

Tables whose coordinates are amino-acid or HMM-model positions are *protein-space only* by rule.
That verdict applies the rule to the census's coordinate-system evidence (NB02), not to a join
query, and is marked as judgement below.

| Verdict | Region tables | Gene tables | Evidence |
|---|---:|---:|---|
| **direct** | **4** | 0 | query: shared contigs + interval join |
| **bridged** | 0 | **1** | query: bounded 1:1 check + self-join through the bridge |
| **self** | 0 | **8** | query: self-join on sampled contigs |
| no gene table | 1 | 0 | query: database listing |
| protein-space only | 9 | 0 | judgement: rule applied to NB02 coordinate system |
| **joinable** | **4 of 14** | **9 of 9** | **13 of 23** |

`refdata.microagrobiome.bgc_catalog`, a BGC table whose only coordinates are latitude and
longitude, is outside the 23 and is shown in the figure for reference.

**The four joinable region tables** are all MGnify, all against `kescience.mgnify.gene` on
`(biome_id, contig_id)`:

| Region table | Region contigs found in `gene` | Regions with a gene within ±5 kb | Median genes |
|---|---:|---:|---:|
| `gene_bgc` | 28,494 / 28,494 | 35,354 / 35,354 | 18 |
| `gene_crispr` | 34,392 / 34,623 | 42,185 / 42,437 | 8 |
| `gene_defense` | 10,864 / 10,864 | 13,734 / 13,739 | 12 |
| `gene_mobilome` | 49,160 / 49,160 | 171,373 / 171,373 | 11 |

SemCat agrees independently. Its `edges` table holds a verified `structural_fk` edge from
`contig_id` in each of the four region tables to `kescience.mgnify.gene.contig_id`, and
`semcat join-keys kescience.mgnify.gene_bgc kescience.mgnify.gene` lists `contig_id` as
VERIFIED (NB04 §5f).

**The bridged gene table** is `kbase.genomes.feature` (1,011,650,903 rows). It has `start`,
`end` and `strand` but no sequence column; `kbase.genomes.contig_x_feature` (also 1,011,650,903
rows) supplies `contig_id`. A full `COUNT(DISTINCT feature_id)` over both tables is avoided.
Instead NB04 takes every `feature_id` in one hash bucket (`pmod(xxhash64(feature_id), 1024) =
0`). Since the bucket is a function of the ID, every copy of an ID falls in the same bucket,
so the test is exact for those IDs. All 987,681 bucket IDs occur once in each table, and the
two ID sets are identical. A self-join through the bridge on a 1/2^20 sample of contigs (34
contigs, 1,241 features) finds a neighbour within ±5 kb for 1,235 features. SemCat lists
`feature_id` between these tables only as an unverified value join, so the bridge rests on the
NB04 check.

**The eight self-joinable gene tables** each return neighbours on every sampled sequence set:
`kescience.mgnify.gene`, `refdata.fungal_db.pombase_gene_coords`,
`kescience.fitnessbrowser.gene`, `globalusers.carbon_source_phenotypes.gene_calls_table`,
`refdata.jgi_mycocosm.features` (end derived as `start + length_bp − 1`; there is no `end`
column), `refdata.jgi_virus.metavr_protein`, `refdata.bvbrc.bvbrc_feature_fact` (positions
are strings, cast to integers), and `kbase.content.c_<genome>_features` (span parsed from the
JSON `location`). The pombase CDS and exon tables also nest inside their genes: 5,134 of 5,134
CDS intervals and 18,025 of 18,026 exon intervals lie inside the gene with the same `gene_id`.

**The negative region cases.** Nine region tables are protein-space only (judgement, above).
`refdata.smag.bgc` has nucleotide BGC intervals and BiG-SCAPE family assignments that MGnify
lacks, but none of the other nine tables in `refdata.smag` has a span column, so nothing in its
database can place genes against those intervals.

*(Notebook: `04_bgc_region_joinability.ipynb` §5; data: `data/bgc_joinability.csv`)*

### 2. Both named queries work in the MGnify frame

The discriminating query passes: **28,494 of 28,494** distinct `gene_bgc` contig identifiers
match a `gene` contig identifier in the `soil` biome, which holds all 35,354 `gene_bgc` rows.

| Measure | Window | Value |
|---|---|---|
| gene–BGC pairs | inside **or within 5 kb** | **754,313** across 35,354 BGCs (21.3 per BGC) |
| genes strictly **inside** the BGC interval | inside only | **13.9 per BGC** |

A BGC typically spans a handful to a few dozen genes, so 13.9 genes inside per BGC is consistent
with a shared coordinate frame rather than coincidental string matches. The 21.3 figure is
larger because the flank admits neighbouring genes by design. A three-table join (BGC region →
gene coordinates → eggNOG function) also runs, so *which functions sit near a BGC* is answerable
end to end.

Multi-domain search separates into two strengths of question:

- **Co-occurrence** ("proteins with domains X and Y") needs only a per-protein domain list.
  6,530 cluster representatives carry both PF00005 and PF00528.
- **Order and spacing** ("X then Y, N residues apart") needs per-domain amino-acid coordinates.
  Counting one protein, one vote (395 proteins, 6%, carry repeat copies), PF00528 precedes
  PF00005 in **6,167 of 6,530 proteins = 94.4%**; pair-level it is 6,578 of 6,963 = 94.5%. That
  is the expected fused ABC-transporter architecture: permease N-terminal, ATPase C-terminal.
  Inter-domain gap median −392 aa (IQR −412 to −371; the sign encodes the order).

That the architecture comes out right is a second check that the amino-acid coordinates mean
what the census says they mean.

*(Notebook: `04_bgc_region_joinability.ipynb` §1–4; data: `data/example_genes_near_bgc.csv`,
`data/example_multidomain_hits.csv`)*

### 3. The census: 51 annotation tables, 23 coordinate-bearing (14 nucleotide, 5 amino-acid, 4 multi-frame)

Full table in `data/annotation_sources.csv`; reproduced in **Results** below. 51 tables survive
adjudication: 20 both assign function *and* annotate a region, 22 assign function without
coordinates, 4 are region-only (3 with a span), 5 are reference vocabularies. A further **13
name-based false positives are excluded and recorded**.

Of the 23 coordinate-bearing tables, **14 are nucleotide**, **5 amino-acid**, and **4 carry
several frames in one row** (amino-acid plus HMM-model or reference-protein positions).

Three facts in the census are recoverable only by reading values, not schemas:

- **`nmdc.results.pfam_annotation_gff`** (2,684,369,000 rows) is named `_gff`, which implies
  genome coordinates. Its `start`/`end` are **amino-acid**: `end − start + 1 == alignment_length`
  on all 26,779 rows of a seeded random sample (NB02 §9). Its `model_start`/`model_end` are
  positions in the Pfam HMM.
- **`kbase.content.c_<genome>_features`** packs `[["NZ_QSIR01000001.1", 1, "+", 855]]`
  (contig, start, strand, length) into a string column called `location`, and SEED Subsystem
  Ontology terms into `ontology_terms`. No column name says start, end, strand, contig, pfam or
  go.
- **`kbase.ke_pangenome.interproscan_domains`** holds 18 distinct `analysis` values: 17
  signature databases (Pfam, 145,825,639 rows; Gene3D, SUPERFAMILY, PANTHER, PRINTS, CDD,
  NCBIfam, ProSiteProfiles, MobiDBLite, SMART, FunFam, ProSitePatterns, Coils, Hamap, PIRSF,
  SFLD, AntiFam) plus a 1-row `Gene3` value that looks like a truncated `Gene3D`.

Two traps found in passing: `refdata.jgi_mycocosm.features` has `start` and `length_bp` but **no
`end`**, and `nmdc.metadata.genome_feature_set` has the best-modelled GFF3 schema in BERDL
(`seqid`/`start`/`end`/`strand`/`phase`/`feature_category_term_id`) and **0 rows**.

*(Notebook: `02_ground_truth_sweep.ipynb`; data: `data/annotation_sources.csv`,
`data/excluded_tables.csv`)*

### 4. SemCat's labels find most census tables, but label few of the relevant columns, and their precision sits at the 0.80 threshold

![SemCat precision and recall](figures/semcat_precision_recall.png)

**Table level.** Of the 51 census tables, a *specific* SemCat label (e.g. `pfam_id`, `ec_number`,
`coordinate`) flags 37; 13 more are flagged only by a generic label (`identifier`,
`annotation_text`, …) that says nothing about gene function; 1 is missed because SemCat does
not index it.

**Column level**, on the pre-registered 200-column audit adjudicated against sampled values and
quoted per `schema_sig` as the plan requires:

| Measure | Value | 95% Wilson interval |
|---|---|---|
| recall (apt label in the right family) | 30/95 = **31.6%** (per column 30/100) | 0.23–0.41 |
| strict precision | 45/56 = **80.4%** (per column 47/58 = 81.0%) | 0.68–0.89 |
| lenient precision (delimited lists count as right) | 49/56 = **87.5%** (per column 51/58) | 0.76–0.94 |

Strict precision by label family (per column): `function_id` 27/36 = 75% (0.59–0.86),
`seqref` 15/16 = 94% (0.72–0.99), `span` 4/5 = 80% (0.38–0.96), `strand` 1/1. Recall by facet
(per column): `function_id` 11/43 = 26%, `span` 17/43 = 40%, `strand` 2/14 = 14%.

| Hypothesis | Criterion | Observed | Standing |
|---|---|---|---|
| H1 sufficient instrument | recall ≥0.80 on every facet **and** coordinate system resolvable | recall 31.6%; the `coordinate` label covers four systems, and 20 of its 78 columns resolve to none | **refuted** |
| H2 high precision, low recall | recall <0.50 **and** precision ≥0.80 | recall 31.6%; strict 80.4%, lenient 87.5% | **supported by the pre-registered point-estimate rule, at the margin**: the strict interval (0.68–0.89) includes values below 0.80 |
| H3 structural not semantic | recall <0.50 **and** precision <0.80 **and** row_count ≥95% | precision 80.4% fails the <0.80 clause on the point estimate; the other clauses hold | **not supported on the point estimate, not excluded at 95%** |
| H0 no value over a name regex | refuted by ≥1 true positive the regex misses | 2 census tables found only by a SemCat-specific label: `globalusers.carbon_source_phenotypes.kofam_annotation_table`, `kbase.nmdc_arkin.metatranscriptomics_gold` | **refuted** |

The audit therefore does not separate H2 from H3 at 95% confidence. The point estimates put
SemCat just on the H2 side, and the `function_id` family alone (75%) sits below 0.80.

**Where SemCat falls short.** `content_type` is NULL on **83.0%** of 92,986 columns (91.8% of
the 66,374 in the audited frame). `concepts` contains **1 molecular label in 101**. The
`coordinate` label spans **four coordinate systems** (geographic, nucleotide, amino-acid, HMM
model) plus 20 columns that type, bounds and sibling names cannot resolve; 32 of its 78 columns
(41%) are geographic.

**Where it is reliable.** `row_count` is exact on **59 of 60** census tables (98.3%). The one
mismatch, `refdata.jgi_virus.metavr_protein`, is 369,281,941 live against 369,281,934 in
SemCat; what caused the 7-row difference was not determined. SemCat also indexes **483 candidate
annotation tables in 13 tenants this account cannot read**.

**Its join layer is populated.** Single-column joins are rows of `edges`: 19,094 rows, of which
**4,004 are verified**, touching 1,872 of the 2,678 indexed tables. `verified_joins` is a
different, much smaller table: its 6 rows are the joins SemCat verified by composite-key
semijoin (four with two-column keys), all within `kescience.fitnessbrowser`. On this project's
own join keys, SemCat holds verified edges for all four MGnify region tables and for the
pombase CDS and exon tables, but not for the `kbase.genomes` bridge (Finding 1).

**Table-level coverage.** 701 of the 864 tables in the account's listing (81.1%) are indexed; 0
indexed tables are gone from the lakehouse and 163 listed tables are absent from SemCat. The
absent tables include all 25 of SemCat's own tables and the 9 tables of
`globalusers.kepangenome_parquet_1`, whose `feature` table has the same column list and row
count (1,011,650,903) as `kbase.genomes.feature`.

*(Notebooks: `01_semcat_discovery.ipynb`, `02_ground_truth_sweep.ipynb`, `03_semcat_grade.ipynb`;
data: `data/semcat_grade.csv`, `data/audit_precision.csv`, `data/audit_recall.csv`,
`data/nb01_summary.json`, `data/nb03_summary.json`)*

---

## Scope of the SemCat verdict: what was and was not tested

Finding 4's precision and recall grade **literal `content_type` lookup**. They are not a verdict
on SemCat's retrieval as a whole.

**Exercised**, of the 25 tables in `globalusers.semantic_catalog`: `catalog_meta`, `tables`
(including `row_count` and `schema_sig`), `columns` (including `content_type`, `role`, bounds,
`ndv`), `concepts`, `verified_joins`, `edges` (counts of verified rows, and the verified edges
on this project's join keys), and `column_embeddings` (row count and vector size only: 92,986
vectors of dimension 384). The SemCat CLI's `join-keys` was run for two table pairs.

**Not exercised:** semantic retrieval over `column_embeddings` (`semcat resolve`,
`resolve-tables`) as a route to the census columns. That is the path most likely to raise
recall on columns that carry no label at all, which is the failure behind the 31.6% recall.
Whether SemCat *as a system* is low-recall remains untested.

---

## Claims

### 13 of 23 coordinate-bearing BERDL annotation tables can be placed against genes by position, but only 4 of the 14 region-annotation tables can, all in kescience.mgnify
- confidence: high
<!-- Nine of the 23 verdicts (protein-space only) apply the stated rule to the census coordinate
     system rather than to a join query; NB04 §5g and data/bgc_joinability.csv mark them. -->
- status: supported
- supports:
  - notebook: notebooks/04_bgc_region_joinability.ipynb#cell-24 [stream: joinability-queries] — "joinable to genes by position: 13 of 23  (region tables 4 of 14; gene tables 9 of 9)"
  - notebook: notebooks/04_bgc_region_joinability.ipynb#cell-21 [stream: joinability-queries] — "each bucket feature_id appears once in contig_x_feature and once in feature, and the two id sets are identical: True"
  - notebook: notebooks/04_bgc_region_joinability.ipynb#cell-23 [stream: semcat-verified-edges] — "verified SemCat edges on these keys: 6"
  - notebook: notebooks/02_ground_truth_sweep.ipynb#cell-15 [stream: census-coordinate-system] — "coordinate-bearing (coords yes or packed): 23"

### BGC regions and gene coordinates in kescience.mgnify share a contig namespace exactly, making "genes near a BGC" a single interval join
- confidence: high
- status: supported
- supports:
  - notebook: notebooks/04_bgc_region_joinability.ipynb#cell-5 [stream: identifier-overlap] — "BGC contigs matched to a gene contig: 28494/28494 = 100.0%"
  - notebook: notebooks/04_bgc_region_joinability.ipynb#cell-11 [stream: biological-plausibility] — "754313            35354        489978           21.3                  13.9"
  - notebook: notebooks/04_bgc_region_joinability.ipynb#cell-23 [stream: semcat-verified-edges] — "kescience.mgnify.gene_bgc.contig_id               kescience.mgnify.gene.contig_id   structural_fk  verified                  1.0000"

### nmdc.results.pfam_annotation_gff uses amino-acid coordinates despite its _gff name, and additionally carries HMM-model coordinates in the same row
- confidence: high
<!-- Single evidence stream by nature: an exact arithmetic identity tested on a seeded random
     sample (N = 26,779 rows, 0 mismatches; data/pfam_coordinate_check.json), not a statistical
     inference. No second independent method was applied, and the claims ledger flags it as
     single-stream. -->
- status: supported
- supports:
  - notebook: notebooks/02_ground_truth_sweep.ipynb#cell-30 — "N tested            : 26,779"

### SemCat's content_type label lookup has low recall, and its precision sits at the 0.80 threshold that separates H2 from H3
- confidence: medium
- status: supported
- supports:
  - notebook: notebooks/03_semcat_grade.ipynb#cell-19 [stream: value-adjudicated-precision] — "strict precision  45/56 = 80.4%"
  - notebook: notebooks/03_semcat_grade.ipynb#cell-18 [stream: label-family-recall] — "per schema_sig  : 30/95 = 31.6%"
  - notebook: notebooks/01_semcat_discovery.ipynb#cell-13 [stream: catalog-completeness] — "content_type_null     77,184 / 92,986 = 83.0%"
- refutes:
  - docs: scope — "Semantic retrieval over column_embeddings (semcat resolve) was not tested; it could raise recall, so this claim covers literal content_type lookup only."

### SemCat's content_type='coordinate' conflates geographic, nucleotide, amino-acid and HMM-model coordinates under one label
- confidence: high
- status: supported
- supports:
  - notebook: notebooks/01_semcat_discovery.ipynb#cell-6 [stream: semcat-metadata-typing] — "distinct coordinate systems sharing the single label 'coordinate': 4 (['amino_acid', 'geographic', 'hmm_model', 'nucleotide']), plus 20 columns resolved to none of them"
  - notebook: notebooks/02_ground_truth_sweep.ipynb#cell-32 [stream: live-census-crosscheck] — "census-confirmed systems under the one label: ['amino_acid', 'hmm_model', 'nucleotide']"

### SemCat's tables.row_count is accurate where verifiable, while its table-level coverage is 81.1% of the account's table listing
- confidence: high
- status: supported
- supports:
  - notebook: notebooks/02_ground_truth_sweep.ipynb#cell-23 [stream: coverage-diff] — "agreement                       : 701/864 = 81%"
  - notebook: notebooks/02_ground_truth_sweep.ipynb#cell-27 [stream: rowcount-verification] — "ACCURACY : 59/60 = 98.3%"

---

## Discoveries

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

## Performance Notes

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

## Results

### Coordinate-bearing tables (23)

| Table | Region type | Coord system | Frame | Span | Strand | Identifier systems | Rows | Joinable to genes (NB04) |
|---|---|---|---|---|---|---|---|---|
| `kbase.ke_pangenome.interproscan_domains` | protein domain/motif | amino_acid | pangenome cluster-representative protein | start..stop | — | InterPro, Pfam, Gene3D, SUPERFAMILY, PANTHER, PRINTS, CDD, NCBIfam, +10 more | 833,303,130 | protein-space only |
| `kbase.ke_pangenome.bakta_pfam_domains` | protein domain | amino_acid | pangenome cluster-representative protein | start..stop | — | Pfam | 18,807,208 | protein-space only |
| `kescience.interpro.protein2ipr` | protein domain/motif | amino_acid | UniProt protein | start..stop | — | InterPro, Pfam, member-DB signatures | 1,175,529,272 | protein-space only |
| `kescience.fitnessbrowser.genedomain` | protein domain | amino_acid | Fitness Browser protein (orgId+locusId) | begin..end | — | Pfam, TIGRFAM, EC (per-row via `domainDb`) | 456,712 | protein-space only |
| `kescience.paperblast.site` | functional residue/site | amino_acid | protein sequence (db+id) | posFrom..posTo | — | PDB, UniProt, ligand IDs, PMIDs | 2,089,192 | protein-space only |
| `nmdc.results.pfam_annotation_gff` | protein domain | **multiple** | gene's protein + Pfam HMM | start..end | — | Pfam | 2,684,369,000 | protein-space only |
| `nmdc.results.annotation_kegg_orthology` | alignment segment | **multiple** | query protein + KO reference protein | q_start..q_end | — | KEGG KO | 1,831,998,811 | protein-space only |
| `nmdc.results.annotation_enzyme_commission` | alignment segment | **multiple** | query protein + EC reference protein | q_start..q_end | — | EC | 1,231,453,377 | protein-space only |
| `kescience.pdb.pdb_uniprot_mapping` | structural segment | **multiple** | PDB author numbering + SEQRES + UniProt | res/sp/pdb beg..end | — | PDB, UniProt | 966,977 | protein-space only |
| `refdata.bvbrc.bvbrc_feature_fact` | gene/CDS | nucleotide | BV-BRC contig (within genome_id) | start_pos..end_pos | strand | EC, KEGG KO, protein families (all JSON-packed) | 1,895,015,043 | **self** |
| `kbase.genomes.feature` | gene/CDS | nucleotide | contig, via `contig_x_feature` | start..end | strand | type, source_database; RAST function via `feature_x_protein`→`protein`→`functional_annotation_rast` (schema-confirmed, join not executed) | 1,011,650,903 | **bridged** |
| `refdata.jgi_virus.metavr_protein` | gene/CDS (viral) | nucleotide | IMG/VR scaffold | start..end | strand | Pfam (array-typed), protein_cluster, product | 369,281,941 | **self** |
| `kescience.mgnify.gene` | gene/CDS | nucleotide | MGnify contig | start..end | strand | via `gene_eggnog` / `gene_amr` / `gene_bgc` | 142,872,191 | **self** |
| `refdata.jgi_mycocosm.features` | gene/CDS/mRNA (fungal) | nucleotide | Mycocosm contig | start + **length_bp (no `end`)** | strand | free-text functions | 17,945,606 | **self** |
| `globalusers.carbon_source_phenotypes.gene_calls_table` | gene call | nucleotide | contig | start..end | strand | KO via `kofam_annotation_table` | 5,111,055 | **self** |
| `kescience.fitnessbrowser.gene` | gene/CDS | nucleotide | Fitness Browser scaffold | begin..end (string) | strand | via `besthitkegg` / `seedannotation` | 228,709 | **self** |
| `refdata.smag.bgc` | **BGC** | nucleotide | SMAG MAG contig (accession_id) | start..end | — | antiSMASH, BiG-SCAPE class/family | 43,169 | no gene table |
| `kescience.mgnify.gene_crispr` | CRISPR array | nucleotide | MGnify contig | crispr_start..crispr_end | `orientation` | repeat/spacer properties | 42,437 | **direct** |
| `kescience.mgnify.gene_bgc` | **BGC** | nucleotide | MGnify contig | start_pos..end_pos | — | antiSMASH, MIBiG | 35,354 | **direct** |
| `kescience.mgnify.gene_mobilome` | mobile element | nucleotide | MGnify contig | start_pos..end_pos | — | element typing | 171,662 | **direct** |
| `kescience.mgnify.gene_defense` | defense system | nucleotide | MGnify contig | system_start..system_end | — | defense typing | 27,858 | **direct** |
| `refdata.fungal_db.pombase_gene_coords` | gene | nucleotide | *S. pombe* chromosome | start..end | strand | PomBase IDs | 12,685 | **self** |
| `kbase.content.c_<genome>_features` | gene/CDS | nucleotide | **packed JSON** | `location[[contig,start,strand,len]]` | in JSON | SEED SSO ontology, free-text function | 3,734 per genome table (5 tables) | **self** |

### Function assignment without coordinates (22)

| Table | # ID systems | Identifier systems | Keyed on | Rows |
|---|---:|---|---|---|
| `kbase.ke_pangenome.eggnog_mapper_annotations` | 9 | eggNOG OGs, COG cat, GO, EC, KEGG ko/Pathway/Module/Reaction/rclass/TC, BRITE, CAZy, BiGG, Pfam | `query_name` | 93,558,330 |
| `kbase.ke_pangenome.bakta_annotations` | 9 | EC, GO, COG, COG cat, KEGG KO, RefSeq, UniParc, UniRef100/90/50 | `gene_cluster_id` | 132,538,155 |
| `kescience.mgnify.gene_eggnog` | 7 | eggNOG OGs, COG cat, GO, EC, KEGG, CAZy, Pfam | `gene_id` | 144,775,367 |
| `kbase.ke_pangenome.interproscan_pathways` | 4 | KEGG, MetaCyc, Reactome, UniPathway | `gene_cluster_id` | 287,228,475 |
| `kescience.pdb.pdb_pfam` | 3 | Pfam, UniProt, PDB | `pdb_id + chain_id` | 990,166 |
| `globalusers.gapmind_pathways.gapmind_pathways` | 2 | GapMind pathway, metabolic_category | `genome_id` *(genome-level)* | 463,729,001 |
| `kbase.nmdc_arkin.proteomics_gold` | 2 | KO, EC | protein identifiers | 345,877 |
| `refdata.merops.uniprot_family_map` | 2 | MEROPS family, UniProt | uniprot accession | 116,733 |
| `refdata.microagrobiome.bgc_catalog` | 2 | BGC identifiers, host/plant metadata | `bgc / anchor / bin` | 139,900 |
| `kbase.ke_pangenome.bakta_amr` | 2 | AMR gene names, reference accession | `gene_cluster_id` | 83,008 |
| `kbase.ke_pangenome.interproscan_go` | 1 | GO | `gene_cluster_id` | 266,317,724 |
| `kbase.ke_pangenome.gapmind_pathways` | 1 | GapMind pathway/step | `gene_cluster_id` | 305,471,280 |
| `refdata.bvbrc.bvbrc_specialty_gene_fact` | 1 | specialty gene family (AMR, virulence, drug target) | `feature_id` | 162,781,795 |
| `refdata.cazy.annotations` | 1 | CAZy family | `protein_accession` | 6,006,576 |
| `globalusers.carbon_source_phenotypes.kofam_annotation_table` | 1 | KEGG KO | `geneid` | 5,235,819 |
| `kescience.fitnessbrowser.besthitkegg` | 1 | KEGG | `orgId + locusId` | 200,074 |
| `kescience.fitnessbrowser.seedannotation` | 1 | SEED subsystem/role | `orgId + locusId` | 177,519 |
| `refdata.fungal_db.sgd_go_annotations` | 1 | GO | SGD gene ID | 138,996 |
| `kescience.fitnessbrowser.besthitmetacyc` | 1 | MetaCyc | `orgId + locusId` | 59,723 |
| `refdata.tcdb.acc_to_tcid` | 1 | TCDB TC number | accession | 24,691 |
| `kescience.mgnify.gene_amr` | 1 | AMRFinder typing | `gene_id` | 8,862 |
| `refdata.smag.cas_proteins` | 1 | Cas protein typing | protein/MAG ids | 8,545 |

### Region table without a span (1)

`kbase.nmdc_arkin.metatranscriptomics_gold` (75,119,498 rows): expression values per feature
with `img_scaffold_oid`, `length` and `strand`, but no start or end.

### Reference vocabularies (5)

`refdata.interpro.entry_xref` (626,311,209) · `refdata.rhea.rhea2uniprot` (397,133) ·
`kescience.interpro.entry` (51,489) · `refdata.interpro.interpro2go` (30,122) ·
`nmdc.ref_data.pfam_terms` (27,481)

### Excluded after inspection (13)

Recorded in `data/excluded_tables.csv`. Notable: `kbase.nmdc_arkin.metabolomics_gold` and
`lipidomics_gold` (mass-spec scan numbers, not genomic spans);
`nmdc.metadata.material_processing_set` (whose `is_stranded` and `stranded_orientation` are
RNA-seq *library* strandedness, and are two of the six columns SemCat labels `strand`);
`refdata.spire.mag_coordinates` (named "coordinates", entirely geographic);
`nmdc.metadata.genome_feature_set` (complete GFF3 schema, 0 rows).

---

## Interpretation

**Coordinate system, not coordinate presence, is the thing to check first** when planning
region-aware work in BERDL. The 23 coordinate-bearing census tables hold about 11.2 billion
rows (the sum of the live counts in `data/annotation_sources.csv` and
`data/row_counts_verified.csv`), in at least four incommensurable frames: nucleotide positions on a contig,
amino-acid positions on a protein, residue numbering in a solved structure, and positions within
an HMM profile. Two tables in one database can disagree. In `kescience.fitnessbrowser`,
`gene.begin/end` are nucleotide positions on a scaffold while `genedomain.begin/end` are
amino-acid positions on the protein. The tables join cleanly on `(orgId, locusId)` and must not
be joined on position.

The joinability result splits along the gene/region line. Every gene-coordinate table in the
census can place genes against each other, which serves "what is next to this gene" wherever
the gene table carries function (BV-BRC with EC/KO, IMG/VR with Pfam). Placing a *region* such
as a BGC, CRISPR array or domain against genes works only in `kescience.mgnify`, where region
tables, a gene table and functional annotation share one frame and one key. The cost there is
coverage: the 35,354 BGCs are all from the soil biome. `refdata.smag.bgc` has richer BGC
semantics (BiG-SCAPE families) but no gene table in its database. That gap needs one table, not
new science.

For multi-domain search, the pangenome domain tables support ordered, spacing-aware queries of
the kind cblaster performs, and `interproscan_domains` bundles 17 signature databases. But they
key on cluster representatives, so "find this domain architecture, then tell me what is next to
it on the chromosome" needs a cluster-member-to-genome mapping that this analysis did not
locate.

On SemCat: its labels flag 37 of the 51 census tables specifically, but they label only about a
third of the relevant columns, and the labels it does apply are right about four times in five.
That is at the H2/H3 boundary, not clearly above it. A user who treats `content_type` as a filter
gets a confident, incomplete answer. The workable pattern is SemCat-as-seed then expand, not
SemCat-as-bound. Two SemCat layers do better than the labels: `row_count` is nearly always exact,
and the verified `edges` cover the MGnify and pombase join keys this project established
independently. Semantic retrieval over the embeddings, which could address the recall gap, was
not tested.

### Literature Context

- The discovery/exploration split in **Paton, Chen & Wu (2023,** *ACM Computing Surveys*,
  doi:10.1145/3626521**)** maps onto what was measured. SemCat's table inventory and row counts
  serve *discovery* (finding candidate tables, including outside a user's grants). Its column
  labels serve *exploration* (what a column means) less well. Its verified edges, which record
  how tables relate, agree with this project's own join checks where both exist.
- **Bianchini et al. (2023,** *Knowl. Inf. Syst.*, doi:10.1007/s10115-023-02014-1**)** describe
  PERSEUS, a semantic metadata catalog over a data lake with the same design posture, and treat
  annotation coverage as a known weak link. The 83% NULL rate found here is consistent with
  that being a general property of the architecture rather than a BERDL-specific defect.
- **Gilchrist et al. (2021,** cblaster, *Bioinformatics Advances*,
  doi:10.1093/bioadv/vbab016**)** state the requirement this census is scored against:
  collocation search needs, per gene, a sequence identifier and a position in a shared frame.
  In BERDL, 13 of 23 coordinate-bearing tables meet it for genes, and 4 of 14 region tables
  meet it for regions.
- **Jørgensen et al. (2024,** *NAR*, doi:10.1093/nar/gkae523**)** show that position carries
  biology in BGC work (core genes central, specialized-metabolite BGCs distal on the
  *Streptomyces* chromosome). That supports treating coordinate-free BGC tables such as
  `refdata.microagrobiome.bgc_catalog` as categorically less useful.
- **van der Hooft et al. (2020,** *Chem. Soc. Rev.*, doi:10.1039/d0cs00162g**)** supply the
  MIBiG/BiG-SCAPE context that `kescience.mgnify.gene_bgc` (`nearest_mibig`) and
  `refdata.smag.bgc` (`big_scape_class`, `gcf_class`) are expressed in, so the two tables answer
  complementary questions.
- **Hurlbert (1984,** *Ecological Monographs*, doi:10.2307/1942661**)** defines
  pseudoreplication. The audit counts cloned staging tables once (per `schema_sig`) and the
  domain-order statistic counts each protein once for that reason.

Prior BERIL work was checked through the knowledge layer. The nearest items,
`gene_function_ecological_agora`'s `Final_Data_Catalog/Sources.md` and
`plant_microbiome_ecotypes`' data manifest, are hand-compiled, project-scoped source lists. They
overlap this census on the pangenome and MGnify tables but record neither coordinate system nor
joinability.

### Novel Contribution

Checked against `references.md` and the knowledge layer only, two things appear not to have been
recorded before:

1. **A coordinate-frame map of BERDL annotation tables**, with joinability tested by query. Prior
   catalogues list tables and purposes; none distinguishes nucleotide from amino-acid from
   HMM-model coordinates or tests which tables can be placed against genes.
2. **A measured baseline for BERDL's semantic catalog.** No prior precision/recall assessment of
   SemCat was found. The value-adjudicated protocol (sample values, validate against the format
   the label claims, separate cardinality errors from vocabulary errors) can be rerun to track
   whether catalog quality changes.

### Scope of the Claim

**The census covers what one account could read on 2026-10-22.** The account's table listing
has 864 tables across 105 databases under 10 tenant prefixes. 840 of them were read; the other
24, all in `ese.ganymede`, are listed but return TABLE_OR_VIEW_NOT_FOUND. SemCat indexes 2,678
tables across 22 tenants; 6 of those tenants are in the account's listing. Everything verified here (coordinate
systems, identifier systems, row counts, joinability) covers that readable slice. Thirteen tenants
outside the account's listing hold 483 SemCat-indexed candidate annotation tables, among them
all 12 operon tables found (`enigma.genome_depot_enigma.browser_operon` and
`browser_operon`/`browser_site_operons` tables in `phagefoundry` and `protect`) and a
polysaccharide-utilization-locus table (`arkinlab.dbcan.dbcan_pul`). These could not be opened.

This is therefore **not** a census of BERDL. The region-annotation picture in particular is
likely understated, because unreadable genome-browser tenants (`enigma`, `phagefoundry`,
`protect`) carry `browser_gene`/`browser_operon`/`browser_site` families of exactly the shape
this project found scarce.

The SemCat grade has the same boundary. Precision and recall are computed over the 655 tables
that are both read by the sweep and indexed. Label quality in `enigma` or `phagefoundry` could
differ and was not sampled.

The BGC demonstration covers one biome (`soil`), because all 35,354 `gene_bgc` rows are soil.
The 13.9-genes-per-BGC figure describes that cohort.

### Limitations

- **Ground truth is a regex plus manual adjudication, and the regex is incomplete.**
  `kbase.content.c_<genome>_features`, which has contig, start, strand and ontology terms, was
  missed by the name-based sweep and found only by reading a column called `location`. Others
  of this kind probably remain, so SemCat's measured recall is against a ground truth that is
  itself a lower bound.
- **The full-frame confusion matrix (`data/semcat_confusion_by_facet.csv`) is biased against
  SemCat** and is not a precision estimate. It treats this project's regex as truth, so a correct
  SemCat label on a column the regex missed counts as a false positive. The value-adjudicated
  audit supersedes it.
- **Precision rests on 56 judgeable `schema_sig` groups**, and its 95% interval (0.68–0.89)
  straddles the 0.80 threshold. Of the 7 `wrong_label` verdicts, two rest on a single failing
  value in 60: `pdb_uniprot_mapping.pdb_end` holds `66A` (a residue number with an insertion
  code) under `coordinate`, and `annotation_hierarchies_unified.term_id` holds `5.3.-.-` (an EC
  class) under `ontology_term_id`. The validators were fixed before the run and were not
  changed after seeing these results.
- **19 of the 100 precision columns carry labels with no validator** (`no_pattern`), including
  `bgc_region_id`, `bgc_class`, `protein_family_id` and `product_prediction`, whose former
  validators accepted any text. Precision covers the 58 columns whose labels assert a checkable
  format.
- The `strand` facet is too small for a stable rate. Across all 840 readable tables there are 18
  genomic-strand columns and SemCat labels 2 of them (2/18, NB02). In the audited frame there are
  14, all in the recall sample, and 2 are found (2/14, NB03).
- Joinability has three limits. Protein-space verdicts (9) apply a rule rather than a query.
  The self-join and bridge checks are samples, of hashed contigs and of a hashed `feature_id`
  bucket. And "no gene table" for `refdata.smag.bgc` covers its own database only; a gene table
  elsewhere in BERDL sharing its contig accessions was not searched for.
- Coordinate systems were determined per table, not per row. A table could mix conventions
  across rows; this was not tested.
- Prior-art claims rest on `references.md` (OpenAlex-derived; PubMed and Semantic Scholar
  returned nothing for these queries when it was compiled) and the knowledge layer. This is not
  an exhaustive literature review.

### What Would Have Changed the Conclusions

- **The pre-registered refutation of the main use case** was an empty contig-ID intersection
  between `gene_bgc` and `gene`. Observed: 28,494 of 28,494 shared. An implausible
  genes-inside-per-BGC value (0.2, or 400) would have flagged a spurious match despite full
  overlap; observed 13.9.
- **H1 had two refutation routes and fails both**: the `coordinate` label cannot be sorted into
  one system from SemCat fields, and recall is 31.6% against a 0.80 bar.
- **H2 versus H3 turns on precision near 0.80.** One more mislabelled `schema_sig` group in 56
  would move strict precision to 78.6% and the point-estimate verdict to H3. The full-frame
  rule-based figures (function_id 0.53, span 0.44, strand 0.50) point the same way but are biased
  for the reason under Limitations.
- **Looked for and not found:** a cluster-member-to-genome mapping that would let the pangenome
  domain tables reach a contig. None was located in the readable catalog.
- **Against completeness:** `kbase.content.c_<genome>_features` shows that at least one class
  of annotation table is invisible to name-based discovery. The census is a floor.
- **Prior movement.** The plan put H3 at MEDIUM-HIGH and H2 at LOW-MEDIUM. The evidence lands
  between them: H2 on the point estimate by 0.4 points, with H3 not excluded. The H3 bookkeeping
  clauses (row_count exact, coverage beyond the account's own listing) hold.

### Corrections history

Each entry changed a reported number or verdict.

1. **Precision adjudication (H3 → H2).** A 12-value sample scored placeholder-only samples and
   delimited lists as mislabels. Moving to 60 values and a four-way adjudication changed the
   verdict; logged in `RESEARCH_PLAN.md` Revision History v2.
2. **Inter-domain gap.** A median taken after `ORDER BY gap_aa … LIMIT 300` reported the tail
   (−680.5 aa). It is now computed over the full join (−392 aa).
3. **Mixed snapshots.** Re-running one notebook alone desynchronised report and notebooks
   (found by `REVIEW_1.md`). The rule since then is to run all four in order.
4. **`schema_sig` deduplication**, pre-registered but not implemented at first (found by
   `REVIEW_1.md`). It is now implemented and quoted.
5. **Cached row counts.** A cell claimed live `COUNT(*)` but read a stale file (found by
   `REVIEW_2.md`). Counts are now computed where they are first used.
6. **A wrong lenient-precision figure** (94.9% against artifacts saying 93.2%), caused by a
   non-deterministic value sample (found by `REVIEW_7.md`).
7. **Deterministic value sampling** (`DISTINCT` + `ORDER BY xxhash64`) fixed the cause of 6.
8. **`kbase.genomes.feature` was called unplaceable.** A reader pointed to the
   `contig_x_feature` bridge, and the table was reclassified as bridged.
9. **2026-10-22 revision, after a pre-publication audit and a Copilot code review.**
   - **Joinability by query.** The verdict list was hand-typed. It is now derived from
     queries under a stated rule applied to all 23 coordinate-bearing tables. That replaces
     "6 of 17 joinable" with 13 of 23, of which 4 of 14 are region tables.
   - **Census rule.** `metatranscriptomics_gold` has no span, so the coordinate-bearing count
     goes from 24 to 23.
   - **Validators.** Three fixes. `src/semcat.py`'s `^mag$`/`^md5$` now match per column.
     Four `r"."` validators were removed. Placeholder filtering is now specific to the
     content type, so `-` and `0` count as valid strand and coordinate values.
   - **SemCat join layer.** The "join layer is unpopulated" reading came from counting
     `verified_joins`. That table holds composite-key joins only; the single-column verified
     joins are in `edges`.
   - **Coordinate systems.** The count of systems no longer includes the "ambiguous" residual.
   - **Rerun.** The chain was rerun against SemCat's 2026-10-21 catalog. Precision now sits at
     the 0.80 threshold, and this report quotes it with an interval.

---

## Data

### Sources

| Collection | Tables Used | Purpose |
|---|---|---|
| `globalusers_semantic_catalog` | `catalog_meta`, `tables`, `columns`, `concepts`, `verified_joins`, `edges`, `column_embeddings` | The instrument under test (7 of its 25 tables) |
| `kbase_ke_pangenome` | `interproscan_domains`, `bakta_pfam_domains`, `bakta_annotations`, `eggnog_mapper_annotations`, `interproscan_go`, `interproscan_pathways`, `gapmind_pathways`, `bakta_amr` | Pangenome domain and function annotation; multi-domain demonstration |
| `kescience_mgnify` | `gene`, `gene_bgc`, `gene_crispr`, `gene_defense`, `gene_mobilome`, `gene_eggnog`, `gene_amr` | BGC/region collocation demonstration; the one frame where region tables join to genes |
| `nmdc_results` | `pfam_annotation_gff`, `annotation_kegg_orthology`, `annotation_enzyme_commission` | Largest annotation tables; coordinate-system value checks |
| `refdata_bvbrc` | `bvbrc_feature_fact`, `bvbrc_specialty_gene_fact` | Largest coordinate+strand feature table |
| `refdata_smag` | all 10 tables (schemas), `bgc`, `cas_proteins` | BGC regions with BiG-SCAPE families; gene-table search |
| `kescience_interpro`, `refdata_interpro` | `protein2ipr`, `entry`, `interpro2go`, `entry_xref` | InterPro domains in protein coordinates |
| `kescience_fitnessbrowser` | `gene`, `genedomain`, `besthitkegg`, `seedannotation`, `besthitmetacyc` | Nucleotide gene table and amino-acid domain table in one database |
| `kescience_pdb`, `kescience_paperblast` | `pdb_uniprot_mapping`, `pdb_pfam`, `site` | Residue-level structural and functional coordinates |
| `refdata_jgi_virus`, `refdata_jgi_mycocosm`, `refdata_fungal_db` | `metavr_protein`, `features`, `pombase_gene/cds/exon_coords` | Viral and fungal feature tables with strand |
| `kbase_genomes`, `kbase_content`, `globalusers_kepangenome_parquet_1` | `feature`, `contig_x_feature`, `functional_annotation_rast` (row count), `c_*_features`, `c_*_cdss`, `feature` | Coordinate tables whose sequence reference is bridged or packed |

### Generated Data

| File | Rows | Description |
|---|---:|---|
| `data/annotation_sources.csv` | 51 | **Primary deliverable**: the census, with category, coordinate system, frame, span, strand, identifier systems, live row count, basis and notes |
| `data/bgc_joinability.csv` | 24 | Per coordinate-bearing table (23, plus `microagrobiome.bgc_catalog` for reference): role, gene partner, verdict, joinable, and whether the verdict rests on a query or on the rule |
| `data/excluded_tables.csv` | 13 | Name-based false positives, with the reason each was excluded |
| `data/semcat_grade.csv` | 51 | Per census table: found by specific label / generic label only / missed |
| `data/ground_truth_columns.csv` | 67,910 | Live schema sweep of the 840 readable tables |
| `data/ground_truth_table_facets.csv` | 840 | Per readable table: which facets its live schema shows |
| `data/sweep_failures.json` | 24 | Listed tables that could not be read (`ese.ganymede`) |
| `data/semcat_candidates.csv` | 2,678 | Frozen SemCat-only answer (recorded before ground truth exists) |
| `data/semcat_coordinate_typing.csv` | 78 | Every `content_type='coordinate'` column with its inferred system and basis |
| `data/semcat_coordinate_crosscheck.csv` | 36 | The `coordinate` columns that fall in census tables: SemCat-inferred system vs census system (NB02 §10) |
| `data/audit_precision.csv` | 100 | Precision stratum, per-column verdict and detail |
| `data/audit_recall.csv` | 100 | Recall stratum, per-column status |
| `data/semcat_confusion_by_facet.csv` | 3 | Full-frame rule-based confusion (biased; see Limitations) |
| `data/row_count_grade.csv` | 60 | SemCat `row_count` vs live `COUNT(*)` |
| `data/row_counts_verified.csv` | 60 | Live row counts for every census table |
| `data/pfam_coordinate_check.json` | 1 | `pfam_annotation_gff` value check: seeded sample (fraction 1e-5, seed 42), N = 26,779, 0 mismatches (NB02 §9) |
| `data/semcat_coverage_diff.json` | 163 | 0 stale + 163 missing tables |
| `data/interproscan_member_dbs.csv` | 18 | `analysis` values inside `interproscan_domains` (17 databases + `Gene3`) |
| `data/example_genes_near_bgc.csv` | 400 | Worked "genes near a BGC" result |
| `data/example_multidomain_hits.csv` | 300 | Worked multi-domain order/spacing result |
| `data/nb01_summary.json` … `nb04_summary.json` | 1 each | Per-notebook summary figures, including SemCat version and wall time |

## Supporting Evidence

### Notebooks

| Notebook | Purpose |
|---|---|
| `01_semcat_discovery.ipynb` | Freezes the SemCat-only answer *before* ground truth exists; coordinate-system sub-test (H1); SemCat join and embedding layers |
| `02_ground_truth_sweep.ipynb` | Live sweep of the readable catalog; strand-recall discriminating query; builds the census; row-count and coverage checks |
| `03_semcat_grade.ipynb` | The 200-column value-adjudicated audit; precision/recall with intervals; found/missed; H0 test |
| `04_bgc_region_joinability.ipynb` | Contig-overlap discriminating query; both demonstration queries; joinability by query for every coordinate-bearing table |

Supporting modules: `src/semcat.py` (shared regexes, the accessible-tenant list, coordinate
classifier), `src/census.py` (curated adjudication with per-row `basis`), `src/validators.py`
(value-based label validators), `q.py` (on-cluster SQL helper).

### Figures

| Figure | Description |
|---|---|
| `figures/coordinate_frame_map.png` | The 23 coordinate-bearing tables plus `microagrobiome.bgc_catalog`, coloured by joinability verdict; verdicts that rest on the rule rather than a join query are marked |
| `figures/semcat_precision_recall.png` | Left: per-facet audited recall and strict precision with 95% Wilson intervals against the 0.80 and 0.50 thresholds. Right: verdict breakdown of the 100-column precision sample. Both panels use the value-adjudicated audit only. |

## Future Directions

1. **Build the cluster-member-to-genome mapping.** It would move `interproscan_domains` (833M
   rows, 17 signature databases) and `bakta_pfam_domains` out of protein space and make
   domain-architecture-plus-neighbourhood queries possible.
2. **Grade SemCat's semantic retrieval** (`semcat resolve` / `resolve-tables` over
   `column_embeddings`) against the census. The 31.6% recall measured here is for literal label
   lookup.
3. **Add a gene-coordinate table to `refdata.smag`**, or document a join path to one, so its
   BiG-SCAPE families can be placed against genes.
4. **Two SemCat fixes with a measured baseline:** split `coordinate` into geographic /
   nucleotide / amino-acid / model, and mark multi-valued columns so that a `kegg_reaction` label
   on a comma-delimited column does not read as a scalar.
5. **Request read access** to `enigma`, `phagefoundry`, `protect` and `arkinlab` and extend the
   census; they hold the operon, genome-browser and PUL tables this slice lacks.
6. **Investigate `nmdc.metadata.genome_feature_set`**, the best feature schema in BERDL, with
   zero rows.
7. **Parse `kbase.content.*_features.location`** into typed columns, and sweep for other
   packed-coordinate columns.

## References

- Paton NW, Chen J, Wu Z (2023). "Dataset Discovery and Exploration: A Survey." *ACM Computing
  Surveys*. doi:10.1145/3626521
- Bianchini D, De Antonellis V, Garda M (2023). "A semantics-enabled approach for personalised
  Data Lake exploration." *Knowledge and Information Systems*. doi:10.1007/s10115-023-02014-1
- Gilchrist CLM, Booth T, van Wersch B, van Grieken L, Medema MH, Chooi Y-H (2021). "cblaster:
  a remote search tool for rapid identification and visualization of homologous gene clusters."
  *Bioinformatics Advances*. doi:10.1093/bioadv/vbab016
- Jørgensen TS, Mohite OS, Sterndorff EB, et al. (2024). "A treasure trove of 1034 actinomycete
  genomes." *Nucleic Acids Research*. doi:10.1093/nar/gkae523
- van der Hooft JJJ, Mohimani H, Bauermeister A, Dorrestein PC, Duncan K, Medema MH (2020).
  "Linking genomics and metabolomics to chart specialized metabolic diversity." *Chemical
  Society Reviews*. doi:10.1039/d0cs00162g
- Hurlbert SH (1984). "Pseudoreplication and the design of ecological field experiments."
  *Ecological Monographs* 54(2):187–211. doi:10.2307/1942661

## Authors

Mark Andrew Miller (Lawrence Berkeley National Laboratory, ORCID 0000-0001-9076-6066)
