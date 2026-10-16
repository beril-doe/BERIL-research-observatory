# Worklog — annotation_coordinate_atlas

## 2026-10-02 — project scaffolded → exploration

Created `projects/annotation_coordinate_atlas/` in the `~/beril-fresh` science
checkout. The session's own cwd (`~/.beril`) has no `projects/` tree and four
candidate checkouts exist on this machine; the user chose `~/beril-fresh/projects/`
(80 projects, the largest, and where the related `berdl_data_atlas` and
`annotation_disagreement_between_sources` projects live).

**What the user came in wanting to find out.** Two things, and they are different
kinds of question:

1. *A census.* Which BERDL tables, across any tenant (explicitly including NMDC,
   KBase reference data, and the pangenome tables), assign a function to a gene
   or a protein — and separately, which annotate a *region* of a genome, gene, or
   protein (domains, motifs, BGC regions, operons). Per table: coordinates
   present or not (sequence/contig ID, start, end, strand), the coordinate system
   those coordinates live in (nucleotide/genome vs amino-acid/protein),
   identifier systems used (Pfam, KO, EC, GO, InterPro, antiSMASH, …), and row
   counts.

2. *An instrument evaluation.* Use SemCat to do the finding, then grade SemCat:
   for each table in the final answer, did SemCat find it, miss it, or get it
   wrong? This makes SemCat the object of study as much as the tool, which means
   the census has to be established by a route independent of SemCat or the
   grade is circular.

The stated downstream motivation is region-aware search — "genes near a BGC
region", "multi-domain searches" — so the deliverable has to say not just
*whether* coordinates exist but whether they are joinable across tables into a
shared frame.

**Environment.** `berdl_env.py --check` reports **on-cluster** with direct Spark
access; no proxy needed. Live inventory (cached 2026-10-02 16:28 UTC): 8 tenants,
84 databases, 788 tables across `bervodata`, `culturebotai`, `kbase`, `kescience`,
`mamillerpa`, `my`, `nmdc`, `refdata`.

**SemCat located.** Not referenced anywhere in the BERIL corpus under that name —
found by scanning the inventory cache for `sem*`. It is the database
`globalusers.semantic_catalog`, 25 tables: `tables`, `columns`, `concepts`,
`column_embeddings`, `verified_joins`, `edges`, `database_edges`, `derivations`,
`ontology_hierarchy`, `l4_curation`, `catalog_detectors`, `catalog_meta`,
plus compound/taxon dictionary and membership families. Worth noting for the
instrument assessment: `globalusers` is not one of the 8 tenants the inventory
reported for this user, so SemCat sits outside the tenant inventory it describes.

Status set to `exploration`. Next: probe the SemCat schema, then run the census
twice — once SemCat-driven, once by independent sweep — so the two can be
compared.

## 2026-10-02 — exploration: SemCat probed, census scoped

Wrote `q.py`, a small on-cluster SQL helper. The corpus's `scripts/run_sql.py`
targets off-cluster Spark Connect and fails here with
`No module named 'spark_connect_remote'` — that module is not in the JH conda env.
`q.py` uses `berdl_notebook_utils.setup_spark_session.get_spark_session` instead.
(Captured as a pitfall.)

### SemCat's shape

`globalusers.semantic_catalog`, generated 2026-09-29T04:51Z, code_version 0.19.28.
Indexes **2,599 tables / 154 databases / 21 tenants / 93,617 columns**, with
15,490 edges, 122 concepts, and only **6** rows in `verified_joins`.

The useful tables for this question are `tables` (fq, tenant, database,
table_name, row_count, description, provenance_class) and `columns` (role,
content_type, concept_label, facet_layer, facet_confidence, ndv, null_fraction,
lower/upper bounds).

### Four findings that shape the plan

**1. SemCat's scope and my read access are different sets, in both directions.**
SemCat indexes 21 tenants; my inventory shows 8 with membership. Spot-checked
reads: `refdata.smag.bgc` ✓, `kescience.mgnify.gene_bgc` ✓,
`nmdc.results.pfam_annotation_gff` ✓, `kbase.ke_pangenome.interproscan_domains` ✓;
`enigma.genome_depot_enigma.browser_gene` ✗, `arkinlab.dbcan.dbcan_pul` ✗,
`phagefoundry.phages_genomedepot.browser_gene` ✗ (all denied). Conversely
`bervodata` (5 DBs: bervo, chess, fao_soils, hwsd2, watershed_sfa_soil_moisture)
and `culturebotai` are readable by me but **absent from SemCat entirely**.
Consequence: for ~13 tenants SemCat metadata is the *only* available evidence,
and it cannot be verified. The report must separate verified rows from
SemCat-asserted-only rows rather than blending them.

**2. `concepts` is useless for this question.** All 122 concept labels are
environmental/geochemical — temperature, microplate, water, conductivity,
nitrate, depth, salinity, metals. Not one concerns gene function, Pfam, KO, EC,
GO, domains, or BGCs. The single near-miss is cluster 3341 "annotations"
(2 columns). Discovery must be driven by `columns.content_type`, not `concepts`.

**3. `content_type` has the right vocabulary but poor recall.** It does carry
`pfam_id`, `ko_term`, `ec_number`, `go_term`, `interpro_id`, `cog_id`,
`uniprot_accession`, `bgc_region_id`, `bgc_class`, `operon_id`, `domain_id`,
`contig_id`, `locus_tag`, `strand` — exactly the facets asked about. But
**78,730 of 93,617 columns (84%) have `content_type = NULL`**. The recall test
that settles it: SemCat labels **6** columns `strand`; a plain name regex over
SemCat's *own* `columns` table finds **58**. That is ~10% recall. Worse, 2 of
the 6 are wrong — `nmdc.metadata.material_processing_set.is_stranded` and
`.stranded_orientation` are RNA-seq library strandedness, not genomic strand —
and genuine strand columns are mislabeled `annotation_text`
(`kescience.fitnessbrowser.gene.strand`, `refdata.bvbrc.bvbrc_feature_fact.strand`).

**4. `content_type='coordinate'` conflates geography with genomics.** Its 78
columns mix lat/lon (`usgs.ngwmn.wells`, `nmdc.metadata.biosample_set`,
`kbase.ke_pangenome.alphaearth_embeddings_all_years`) with genomic spans
(`kescience.mgnify.gene_bgc.start_pos/end_pos`, `refdata.smag.bgc.start/end`)
and protein/residue spans (`kescience.pdb.pdb_uniprot_mapping.res_beg/res_end`,
`kescience.interpro.protein2ipr.start/stop`). Since the *coordinate system* —
nucleotide vs amino-acid — is precisely what the user asked for per table,
SemCat's single `coordinate` label cannot answer it. This is a "got it wrong"
case, not a "missed it" case.

**5. `row_count` is trustworthy.** SemCat's counts matched live `COUNT(*)`
exactly on all four tables checked: pfam_annotation_gff 2,684,369,000;
interproscan_domains 833,303,130; smag.bgc 43,169; mgnify.gene_bgc 35,354.
Iceberg metadata counts return in seconds even at billion-row scale, so
verifying every row count live is cheap and should be done.

### Census size

Within the 4 accessible SemCat-indexed tenants (kbase, kescience, nmdc, refdata;
847 tables), a name-based sweep classifies: 123 tables with function-identifier
columns (19 of which also carry start/end, 3 of those also strand), plus 41 more
with start/end but no function column (candidate coordinate tables that *join*
to function). ~164 tables to triage — feasible. Name matching also produces
false positives (`biosample_set`, `nmdc_arkin.metabolomics_gold`), so manual
triage of each candidate is required, not optional.

Highest-value candidates found so far, with SemCat row counts:
`nmdc.results.pfam_annotation_gff` (2.68B, has HMM model_start/model_end *and*
sequence start/end), `refdata.bvbrc.bvbrc_feature_fact` (1.90B, +strand),
`nmdc.results.annotation_kegg_orthology` (1.83B),
`nmdc.results.annotation_enzyme_commission` (1.23B),
`kescience.interpro.protein2ipr` (1.18B), `kbase.ke_pangenome.interproscan_domains`
(833M), `refdata.jgi_virus.metavr_protein` (369M, +strand),
`kbase.ke_pangenome.bakta_pfam_domains` (18.8M), `refdata.jgi_mycocosm.features`
(17.9M, +strand), `kescience.pdb.pdb_uniprot_mapping` (967K),
`kescience.fitnessbrowser.genedomain` (457K), `refdata.smag.bgc` (43K, with
`bgc_region`/`big_scape_class`/`product_prediction`), `kescience.mgnify.gene_bgc`
(35K). The mgnify family also has `gene`, `gene_crispr`, `gene_defense`,
`gene_mobilome` — region annotations in genome coordinates.

Next: write RESEARCH_PLAN.md. The hypothesis-bearing part of this project is not
the census (that is enumeration) but SemCat's adequacy as the discovery
instrument — which is genuinely uncertain and already showing a split verdict
(good row counts and vocabulary, bad recall and bad coordinate-system typing).

## 2026-10-02 — plan written → proposed

`RESEARCH_PLAN.md` frozen at v1. Status set to `proposed`.

**Transition not event-logged.** The skill prescribes
`uv run beril status <id> --set proposed`, but neither `beril` on this machine has
a `status` subcommand — the workbench CLI (v2.0.0,
`/home/mamillerpa/beril-workbench/.venv/bin/beril`) offers
`doctor|setup|start|user|claims|approve|login|logout|ov|runtime-snapshot`, and the
older `beril-fresh` CLI the same. Took the skill's documented fallback and edited
`status:` in `beril.yaml` directly, so this transition has no row in
`events.jsonl`. `beril approve` *does* exist and supports `--relayed`, so the
plan-approval record will be properly written when the checkpoint is answered.

Side note worth recording: `uv run beril ...` from inside `beril-fresh` rebuilt
`beril-cli` from that repo into the *active* `VIRTUAL_ENV`, which is the
workbench venv. Verified afterwards that the workbench venv's `beril_cli` still
resolves to `beril-workbench/packages/cli/beril_cli/__init__.py` and reports
v2.0.0, so nothing is broken — but `uv run` inside a second checkout while a
different venv is active is a way to clobber a CLI, and plain `python`/absolute
paths are safer here.

### Why this framing, and what was rejected

The user's request reads as pure enumeration — list the tables, list their
properties. Writing it that way would have produced a plan with no hypothesis and
nothing to be wrong about. But the request has a second half ("say for each
answer whether SemCat found it, missed it, or got it wrong"; "an assessment of how
useful SemCat was") that *is* an empirical claim about an instrument, and that is
where the uncertainty actually lives. So the plan keeps the census as the
deliverable (Q1, reported regardless of outcome) and puts the competing
hypotheses on SemCat (Q2). That is the honest allocation: enumeration gets
enumerated, and the thing that could come out either way gets pre-registered
tests.

**The circularity trap, and the fix.** Grading SemCat using SemCat-derived
candidates would be worthless. So notebook 1 freezes the SemCat-only answer
*before* notebook 2 builds ground truth by an independent live `DESCRIBE` sweep of
all 788 readable tables. Notebook ordering is load-bearing here, not cosmetic. A
timed probe (158 tables in 19.6 s = 0.12 s/table) showed the independent sweep
costs ~95 s, which is what made the non-circular design affordable rather than
aspirational — worth stating plainly, because the cheap-but-circular design would
have been tempting if the sweep had looked expensive.

**Hypotheses considered and rejected as strawmen.** "SemCat is useless" was
rejected: it demonstrably indexes 21 tenants against this account's 8, which is
real and otherwise-unobtainable value, and its `row_count` was exact on every
table checked. "SemCat is broken because it's incomplete" was rejected as
unfalsifiable — every catalog is incomplete. What survived is the
precision/recall split: H2 (trust the labels it applies, distrust its coverage)
versus H3 (distrust both, trust the bookkeeping). Those differ on a measurable
quantity — precision on applied labels — and the exploration evidence (2 of 6
`strand` labels wrong) leans H3 without settling it, since one facet is thin
evidence and `strand` may be SemCat's hardest case rather than a typical one.
H0 (no value over a name regex) is retained at a very low prior mostly to keep
the comparator explicit.

**Unit-of-analysis decision.** One column, but rates computed twice — per column
and per distinct `schema_sig` — because NMDC keeps four dated staging copies of
`genome_feature_set`, and counting cloned schemas as independent observations
would inflate n without adding evidence. The per-`schema_sig` figure is the one
quoted where they disagree.

**Feasibility verdict: `partial`, deliberately, with numbers.** 788 of SemCat's
2,599 tables are readable (30%). The census is therefore complete for 8 tenants
and metadata-only for 13 — including SemCat's largest, `enigma` (866 tables). The
instrument grade is likewise computed on this account's slice and generalizes to
the rest only by assumption. Both limits are grants limits, unfixable by compute,
and the plan requires them stated in the report rather than smoothed over. Chose
`partial` over `answerable` precisely because the surviving set looks clean —
which is the condition under which the verdict is easiest to inflate.

**One addition the user did not ask for, and why.** Notebook 4 tests whether
coordinates are *joinable*, not merely *present* — do `mgnify.gene_bgc.contig_id`
values actually intersect `mgnify.gene.contig_id`? This is inside the stated
scope, not beyond it: the user's reason for wanting coordinates is "genes near a
BGC region", and a table can satisfy "has contig, start, end, strand" while
living in a coordinate frame nothing else shares.
`kbase.ke_pangenome.interproscan_domains` is the concrete worry — it keys on
`gene_cluster_id`, a cluster *representative*, so its protein coordinates cannot
be joined to a genome contig without a cluster-member mapping. Finding that after
writing the query is the expensive way to learn it.

Next: plan-review checkpoint. Not starting notebooks until approval is on disk.

## 2026-10-02 — analysis started → active; NB01 and NB02 run

Approval recorded (`via: agent-relayed`, plan_hash `939a7492…`, verified present
in `beril.yaml` before any analysis code was written). Status set to `active` by
hand, since this `beril` CLI has no `status` subcommand.

Built `q.py` (ad-hoc CLI queries) and `src/semcat.py` (shared regexes and the
coordinate-system classifier, so four notebooks cannot drift on what "ground
truth" means).

### NB01 — the frozen SemCat-only answer

**The discriminating query failed H1 outright, as the plan said it would if
SemCat could not resolve coordinate system.** SemCat's 78 `content_type='coordinate'`
columns span **five** distinct systems: geographic 32, nucleotide 16, amino-acid
10, HMM-model 2, and 18 that remain **ambiguous even after** bringing in type,
numeric bounds, and sibling column names. 41% geographic means a user filtering
on this label to find genome features gets mostly latitude and longitude. Every
successful classification was decided by type/bounds/siblings — the label itself
contributed nothing. H1 is dead on its own pre-registered terms.

Supporting structural facts: `content_type` is NULL on 84.1% of 93,617 columns;
exactly **1** of 122 `concepts` contains any molecular term; `verified_joins` has
**6** rows for 2,599 tables.

**A refinement made before ground truth existed**, so it cannot have been tuned
to the answer: Route A (semantic labels) initially appeared to find *more* tables
(1,958) than a plain name regex (758). That is an artifact — `identifier` labels
columns in 1,691 of 2,599 tables (65%) and `annotation_text` in 1,242 (48%), so
including them makes "SemCat found an annotation table" nearly vacuous. Splitting
specific from generic labels: Route A-specific = 649 tables, and the generic
labels inflate by 1,309. NB01 was re-run with the split so the frozen artifact
carries it.

The H0 comparator came out interesting rather than foregone: SemCat's **specific**
labels flagged **373 tables the name regex missed**, and the regex flagged 20 that
SemCat missed. Whether those 373 are true positives is NB03's job.

### NB02 — the independent census

Live sweep: **883 tables / 108 databases / 69,601 columns in ~113 s**, 13
failures (all one cause — a stale `s3a://cdm-lake/users-sql` location under
`mamillerpa`/`my`). Two pitfalls cost re-runs and are recorded: `get_db_structure()`
returns a JSON *string* (and iterating it yields characters, failing silently),
and `fn` was shadowed across cells, which published a DataFrame where an integer
metric belonged.

**Discriminating query — strand recall at full scale.** Ground truth: **18**
genomic-strand columns in accessible tables, adjudicated explicitly because the
word is ambiguous (genomic strand vs RNA-seq library strandedness vs reading
frame/phase). SemCat labels 6 columns `strand` overall, 4 in accessible tenants,
of which **2 are correct**. So **recall 2/18 = 11.1%**, **precision 2/4 = 50%**.
The two false positives are `nmdc.metadata.material_processing_set.is_stranded`
and `.stranded_orientation` — library protocol fields, not genomic strand. Real
strand columns sit mislabelled as `annotation_text`. Recall fails H1's ≥80%;
precision fails H2's ≥80%; both conditions of H3 hold on this facet. The
pre-registered 200-column audit in NB03 is what decides whether that generalizes.

**The census: 51 tables**, 24 of them coordinate-bearing — nucleotide 15,
amino-acid 5, multiple-frames 4 — plus **13 excluded false positives** recorded
explicitly, because what a name-based rule gets wrong is part of the answer.
Curated in `src/census.py` with a per-row `basis` field saying whether a schema
read or a value check settled it. Three value checks did real work:

- `nmdc.results.pfam_annotation_gff` (2,684,369,000 rows — the largest):
  `end-start+1 == alignment_length` exactly, so start/end are **amino-acid**,
  not nucleotide, *despite `_gff` in the name*. `model_start`/`model_end` are HMM
  profile positions — a third kind of coordinate that is not a sequence position.
- `nmdc.results.annotation_kegg_orthology`: `q_end-q_start+1 == aln_len`, so
  amino-acid, and `s_start`/`s_end` are on a *different* protein (the KO reference).
- `kbase.content.c_<genome>_features`: `location` = `[["NZ_QSIR01000001.1",1,"+",855]]`
  = `[contig, start, strand, length]`, and `ontology_terms` = `{"SSO":{...}}`.
  **Full genomic coordinates plus ontology function assignment, and not one column
  name says start, end, strand, contig, pfam, or go.** SemCat misses it; so does
  the name regex that built this census's own ground truth. Found only by reading
  values of a column called `location`. This is the honest limit on my ground
  truth, not just on SemCat's, and the report must say so.

Other findings worth keeping: `kbase.ke_pangenome.interproscan_domains` carries
**18 signature databases in one table** (Pfam 145,825,639 rows, Gene3D,
SUPERFAMILY, PANTHER, …), enumerable only from `DISTINCT analysis`;
`refdata.jgi_mycocosm.features` has `start` and `length_bp` but **no `end`**;
`refdata.bvbrc.bvbrc_feature_fact` (1,895,015,043 rows) has contig+start+end+strand
*and* EC/KO/family identifiers, but every coordinate is string-typed and every
identifier is JSON-packed; `nmdc.metadata.genome_feature_set` has the single
best-modelled GFF3 schema in BERDL and **0 rows**, in both the canonical and the
staging copy.

**SemCat bookkeeping, graded.** `row_count` exact on **65/66** verifiable tables
(98.5%) — the one miss is `refdata.jgi_virus.metavr_protein`, off by 7 rows from
growth since the 2026-09-29 snapshot. That clears H3's ≥95% bar. But table-level
*coverage* is weaker than expected: within accessible tenants, 159 SemCat tables
are **gone** from the lakehouse (three deleted NMDC staging databases, 53 tables
each) and 185 live tables are **absent** from SemCat — including all 25 of
SemCat's own tables and `globalusers.kepangenome_parquet_1`, which holds a
1,011,650,903-row gene-coordinate table. Table-level agreement: 79%.

Next: NB03 (the 200-column stratified audit → the H2/H3 decision) and NB04
(coordinate-frame joinability, which is what decides whether the BGC use case
is actually servable).

## 2026-10-02 — NB03 run, and a verdict that changed under a better method

**The pre-registered 200-column audit.** 100 SemCat-labelled columns (precision) and 100
ground-truth annotation/coordinate columns (recall), stratified and seeded, adjudicated
against **sampled values** rather than column names — judging a `pfam_id` label by whether
the column is *called* something Pfam-ish would have re-imported the assumption under test.

**First pass said H3. It was wrong, and the reason was method, not data.** That pass sampled
12 values per column and scored each label simply correct-or-wrong. Two problems surfaced on
inspection of the 14 failures:

1. Seven were columns whose 12 sampled values were *all* placeholders — `'-'`, `'nan'`,
   `'None'`. That is a limitation of a `LIMIT 12` sample, not evidence that SemCat mislabelled
   anything; the label may be perfectly right for populated rows. Scoring those against SemCat
   is simply an error.
2. Two were multi-valued columns — `bakta_annotations.go` holding
   `GO:0000287;GO:0008927;…`, `proteomics_gold.COG` holding `COG2885,COG3637`. The vocabulary
   is right; the cardinality is not. That is a real and consequential defect (a user writing
   `WHERE go = 'GO:0006064'` silently gets nothing) but it is a *different* defect from naming
   the wrong vocabulary, and lumping the two overstates the case.

Re-ran with 60 values per column and a four-way adjudication — `correct` /
`wrong_cardinality` / `wrong_label` / `sentinel_only`, the last excluded from the denominator
as an audit limitation. Result: **strict precision 52/62 = 83.9%**, lenient 57/62 = 91.9%,
recall unchanged at **32%**. Both precision figures clear H2's 0.80 bar, so the verdict moved
**H3 → H2**. The superseded numbers are kept in `SCOREBOARD.md`; the change came from fixing
the instrument, not from preferring the answer.

**So: H2 supported — SemCat is high-precision and low-recall.** H1 was already refuted twice
over (coordinate sub-test, recall 32%). H3 is refuted *on its precision clause only*: its
other claims are independently true (row_count exact 65/66 = 98.5%; 439 candidate tables in
tenants this account cannot read). H0 is refuted.

The five genuine `wrong_label` cases are worth naming, because they are a type:
`refdata.interpro.interpro2go.interpro_name` labelled `interpro_id` (a name is not an id);
`kbase.nmdc_arkin.cog_hierarchy_flat.cog_id` labelled `cog_id` while holding category letters
`J`, `A`, `K` — here the *column* is misnamed and SemCat trusted it;
`kescience.mgnify.genome_cog.cog_category` labelled `cog_id`, where SemCat overrode a column
name that was already correct; `kbase.all_the_bacteria.file_index.project_id` labelled
`ec_number` while holding `zxfmy`, which is flagrant.

Precision is strongly facet-dependent: `seqref` 16/16 = 100%, `span` 5/5 = 100%,
`function_id` 31/41 = 76%. The `strand` facet (recall 14%, precision 50%) is the worst in the
catalog but too small to carry an estimate alone.

**A cross-check I had to argue myself out of.** The full-frame, rule-based confusion matrix
reports much harsher precision (function_id 0.54, span 0.44). It is biased: it treats this
project's own name regex as truth, and the audit demonstrated that regex is incomplete — so
SemCat is charged a false positive every time it labels a column the regex failed to
recognise, which is SemCat *succeeding*. 127 of the 274 `function_id` labels fall outside the
regex's reach. The value-adjudicated audit is the pre-registered test and supersedes it; the
full-frame numbers are reported as a biased lower bound and labelled as such.

## 2026-10-02 — NB04 run: the use case is servable, but only in some frames

**Discriminating query passed decisively.** Every one of the 28,494 distinct `gene_bgc`
contig ids in the `soil` biome matches a `gene` contig id — **100% overlap**, same namespace,
no mapping table needed. (The whole of `gene_bgc`, all 35,354 rows, turns out to be the soil
biome.) The interval join yields 754,313 gene–BGC pairs and **13.9 genes inside per BGC** —
a biologically sensible BGC size, which is the real check: it shows the join operates in a
genuinely shared coordinate frame rather than matching strings by coincidence. The
three-table extension (BGC region → gene coordinates → eggNOG function) also runs, so "which
functions sit near a BGC" is answerable end to end.

**Multi-domain search works, and order queries work where coordinates exist.** 6,530 cluster
representatives carry both PF00005 and PF00528; over the full 6,963-pair join PF00528
precedes PF00005 in **94%** — permease N-terminal, ATPase C-terminal, the expected fused ABC
transporter architecture. That the architecture comes out right is a second validation that
the amino-acid coordinates mean what the census says they mean.

**Correction.** I first reported the inter-domain gap as median −680.5 aa, computed from a
300-row sample taken *after* `ORDER BY gap_aa` — the extreme tail rather than the
distribution. Recomputed with `percentile_approx` over the full join: median −392 aa, IQR
−412 to −371. The ordering-then-limiting pattern is an easy way to publish a biased statistic
and it nearly happened here.

**The negative result is the more useful half.** Of 18 coordinate-bearing region tables, only
**5** support a region-to-gene positional join with no mapping step (the MGnify family plus
PomBase). **5** are protein-space only — `interproscan_domains` and `bakta_pfam_domains` live
on pangenome *cluster representatives*, `protein2ipr` on UniProt accessions, and both NMDC
`results` tables on a gene's protein with no contig column anywhere in that database. They
answer domain questions well and cannot reach a genome contig at all. **3** are blocked or
impossible: `refdata.smag.bgc` has clean BGC intervals but SMAG ships no gene-coordinate
table, so nothing can be placed against them inside BERDL; `kbase.genomes.feature` has
1,011,650,903 rows of start/end/strand and **no sequence column**, so the coordinates cannot
be located; `refdata.microagrobiome.bgc_catalog` has no sequence coordinates whatsoever, only
latitude and longitude.

Written to `figures/coordinate_frame_map.png` and `data/bgc_joinability.csv`. This is probably
the most reusable artifact in the project: "has coordinates" and "can be joined to genes" are
different properties, and the gap between them is where a researcher would otherwise lose an
afternoon.

All four notebooks executed with outputs saved, zero errors. Next: results-review checkpoint.

## 2026-10-06 — findings synthesized → analysis

`REPORT.md` written; status `active` → `analysis`; `artifacts.report: true`.

**Materiality ruling, asked for before synthesis.** The user asked whether the NB03 §2a rerun
(12→60 values, two-way→four-way adjudication, verdict H3→H2) was a material change under
execute-plan's Revision Loop. Determination: **not material**. No hypothesis was added or
dropped; no decision threshold moved (precision 0.80, recall 0.50, row_count 0.95 all stand);
the discrimination strategy is unchanged (still a 100+100 stratified, value-adjudicated
audit); and what refutes H1 is unchanged — recall was 32% under both passes. The Revision
Loop's own qualifier ("a changed cutoff is material only when that value appears in a decision
criterion") does not catch values-per-column, which appears in no criterion. The plan
*required* adjudication "by reading the column's actual values"; a 12-value sample returning
only placeholders was not reading actual values, so the rerun increased compliance rather than
departing from it. Logged as Revision History **v2**, and verified with `beril`'s own
`plan_digest`: computed hash equals the recorded `plan_hash` exactly, so the approval stands —
the tool agrees the append is non-material.

What I recorded against myself: the revision followed seeing a result and moved a verdict, and
the strict/lenient precision pair is a post-hoc choice. It is non-decisive only because H2
holds under both figures (83.9%, 91.9%). Had they straddled 0.80 the Decision Rule's clause 5
would apply and H2-vs-H3 would be reported unresolved.

**What the synthesis had to reconcile.** Three things did not simply fall out of the numbers:

1. *Two precision estimates that disagree.* The value-adjudicated audit says 83.9%; the
   full-frame rule-based matrix says 0.44–0.54 and would support H3. The latter is biased —
   it treats this project's own regex as truth, so SemCat is charged a false positive whenever
   it labels a column the regex missed, which is SemCat succeeding (127 `function_id` columns
   fall in that gap). The audit supersedes it, but the conflict is stated in the report under
   "What Would Have Changed Our Mind" rather than buried, because a reader who rejects the
   bias argument should land on "unresolved", not on 83.9%.
2. *The scope of the SemCat verdict.* On the user's instruction, the report now states
   explicitly that only **5 of SemCat's 25 tables** were exercised (`catalog_meta`, `tables`,
   `columns`, `concepts`, `verified_joins`) and that no `semcat` CLI was used — there is none
   on this machine's PATH, so neither `semcat resolve` nor `semcat joins` was tested. This
   matters more than a normal caveat: `column_embeddings` and the 15,490-row `edges` table are
   exactly the components that could compensate for sparse `content_type`, so the 32% recall
   is a measurement of *literal label lookup*, not of SemCat as a system. Written as its own
   section, not a limitation bullet.
3. *A reproducibility hole found during the claims build.* The headline "row_count exact on
   65/66" had been computed in an ad-hoc shell script with no notebook provenance — it would
   have gone into the report as an unreproducible number. Added §6a to NB02 to recompute it
   and re-ran the notebook; the claim now points at `02_ground_truth_sweep.ipynb#cell-19`. [2026-10-16: now `#cell-27` after the one-based citation repoint; see the last entry of this log.]
   This is precisely what the claims ledger is for, and it earned its keep.

**What was discarded.** An earlier framing led with the SemCat verdict. The report now leads
with joinability (5 of 18), per the user's instruction and on the merits: the census and the
instrument grade are both in service of whether region-aware queries are possible, and that is
the answer a reader needs first.

Claims ledger: 6 claims, 4 multiple-stream, **2 single-stream with confidence mismatch** left
standing and explained rather than relabelled — both rest on one measurement by nature (an
exact arithmetic identity; a complete enumeration). Both corrections remain visible in
`REPORT.md` and `SCOREBOARD.md`.

Next: `berdl-review`. Submission deferred to the user.

## 2026-10-06 — REVIEW_1 found two real defects; both fixed, all notebooks re-run

`bash $BERIL_CORE/tools/review.sh annotation_coordinate_atlas` → `REVIEW_1.md` (claude,
claude-sonnet-5). It judged the design sound — non-circular census/instrument split,
pre-registered falsification, discriminating queries first — and then found two things I had
missed. Both were real. Neither was self-detected.

**1. Mixed snapshots, and it was my doing.** To fix a provenance gap (the 65/66 row_count
figure had been computed in an ad-hoc shell script with no notebook behind it) I added §6a to
`02_ground_truth_sweep.ipynb` and re-executed *that notebook only* — on 2026-10-06, four days
after 01/03/04 ran. Both NB01 and NB02 read live catalog state top-to-bottom, so this
desynchronised the repository from its own report: REPORT quoted 883 accessible tables /
69,601 columns / 13 sweep failures / 159 stale / 185 missing, while the saved notebooks
produced 826 / 67,575 / 0 / 5 / 163. NB03's saved outputs were additionally stale against the
`ground_truth_columns.csv` it reads. The reviewer caught this by cross-checking file
timestamps and cell outputs against the prose — exactly the check I should have run after
touching one notebook in a chain.

Fixed by re-executing **all four in order** against one 2026-10-06 snapshot and restating
every affected figure in `REPORT.md` and `SCOREBOARD.md`. One bug surfaced during the re-run:
`classify_coordinate_system` crashed with `cannot convert float NaN to integer`, because
SemCat 0.24.2 returns NaN for bounds where 0.19.28 returned strings, and my `num()` helper
returned `float('nan')` rather than `None` — which passes an `is not None` guard and then dies
in `format(int(...))`. Fixed in `src/semcat.py`.

Two things worth keeping from the re-run:

- **SemCat is a fast-moving target.** `code_version` went 0.19.28 (09-29) → 0.21.6 (10-06
  04:12) → **0.24.2** (10-06 19:38) — three regenerations in eight days, two inside one working
  day. Indexed tables 2,599 → 2,509; columns 93,617 → 91,246. Any grade of this catalog is a
  grade of one version of it, so the report header now pins the exact snapshot and the README
  warns about drift.
- **Most of the apparent staleness improvement was SemCat catching up, not the lakehouse
  changing.** The three dated NMDC staging databases responsible for 159 stale tables on 10-02
  had been dropped from SemCat's index by 10-06, taking the figure to 5.

**2. A pre-registered correction I never implemented.** `RESEARCH_PLAN.md` commits to computing
every rate twice — per column and per distinct `schema_sig` — so cloned staging tables cannot
inflate *n*. I wrote that into the plan, cited Felsenstein for it, and then did not do it. The
reviewer found a staging-database clone sitting in the audit sample as an independent row.
Implemented in `03_semcat_grade.ipynb` §2b-bis: a `schema_sig` group scores as one observation,
all-must-pass. The precision sample had no clones (59 columns → 59 groups); the recall sample
collapsed 100 → 93, moving recall 30.0% → **32.3%**. Per the plan, the `schema_sig` figure is
now the one quoted. It slightly favours SemCat and changes no verdict.

**Net effect on conclusions: none.** Across two independent snapshots, two adjudication
policies and two units of analysis, H1 and H0 are refuted, H2 is supported, the census holds at
51 entries / 24 coordinate-bearing, and 5 of 18 region tables join directly. Final figures:
recall 32.3%, strict precision 86.4% (51/59), lenient 94.9%, row_count 65/66, agreement 80.3%.
The numbers moved; the findings did not. That stability is worth more than the original numbers
were.

`REPORT.md` now carries four corrections — two self-detected, two from review, labelled as
such. Claims ledger rebuilt: 6 claims, 4 multiple-stream, 2 single-stream-by-nature. Next:
re-review against the corrected report.

## 2026-10-06 — REVIEW_2: the same bug, one layer deeper

Ran the review again against the corrected report. It independently re-verified both
`REVIEW_1.md` findings as genuinely fixed — rather than taking my word for it — and then found
a third instance of the *same* defect in a place the first fix had not reached.

**§6a claimed to be live and was not.** The cell I added to give the row-count figure notebook
provenance said it checked "against live Iceberg `COUNT(*)`", and then read
`data/row_counts_verified.json` — a file dated 2026-10-02 that no cell or script regenerates.
It fed the census's `row_count` column, the H3 ≥95% decision clause, and a Performance Note.
So the fix for Correction 3 had itself shipped a stale cache. Not self-detected; found by the
reviewer comparing the cell's prose to its code and the file's mtime.

Rewritten so §6a issues the `COUNT(*)` queries itself and re-emits `annotation_sources.csv`,
`row_counts_verified.json/csv` and `row_count_grade.csv` from that live result — the number and
the file now cannot diverge. Live measurement: **59 of 60 exact = 98.3%**; the target set is
now exactly the census tables, hence 60 rather than the previous 66. H3's clause still passes
with margin. One ordering trap hit on the way: §6a runs *after* the census emit cell, so
attaching `counts_live` there raised `NameError`; §6a now re-emits the census itself.

Two smaller items from the same review, both fixed: a Limitations bullet still said "thirteen
tables failed the sweep" when the current run has **0** (those scratch tables were removed from
the lakehouse), and a "14 ground-truth strand columns" figure matched neither artifact — the
real numbers are **17** across all accessible tables and **13** inside the audited frame. Both
were leftovers from the pre-re-run snapshot that my own sweep for stale figures missed.

**Re-ran the entire chain again** rather than just the downstream notebooks, which is the
lesson from Correction 3 applied rather than merely written down. All four notebooks now carry
one timestamp window and one SemCat version (0.24.2).

**Conclusions unchanged across three full-chain re-runs and two SemCat versions**: H1 and H0
refuted, H2 supported (recall 32.3%, strict precision 86.4%, lenient 94.9%), census stable at
51 entries / 24 coordinate-bearing, 5 of 18 region tables directly joinable, BGC contig overlap
100%, 13.9 genes per BGC. That the verdicts survived every correction is now the strongest
evidence in the project — stronger than any single figure in it.

`REPORT.md` carries five corrections: two self-detected, three from review. Corrections 3 and 5
are the same defect surviving its own first fix, and that recurrence is flagged in the report
as the more useful finding than either instance. Three pitfalls recorded for the chain-staleness
class, SemCat version volatility, and the `float('nan')` guard failure. Next: third review.

## 2026-10-06 — REVIEW_3 and REVIEW_4: diminishing findings, two more fixed

**REVIEW_3** independently re-verified every headline figure against all four summary JSONs,
confirmed `claims.json`'s `report_hash` matches `REPORT.md`, and traced §6a's actual cell code
(not my description of it) to confirm the live-count fix was real. It found three leftovers,
all fixed:

- `03_semcat_grade.ipynb` still carried a comment citing the pre-Correction-5 figure
  (`65/66 = 98.5%`) next to a hardcoded `rc_ok = True`. Harmless to the computation, but a
  fourth instance of this project's signature bug, so worth closing.
- Two unreferenced scratch CSVs from the 2026-10-02 exploration
  (`ground_truth_columns_raw.csv`, `_gt_table_facets.csv`). Checked first that both were
  genuinely superseded — same schema, current equivalents present from today's run — then
  removed.
- The staleness-detection command in `memories/pitfalls.md` globbed only `*_summary.json`,
  which would not have caught the very cached file that caused Correction 5. Widened to all of
  `data/*.csv`, `data/*.json` and `figures/*.png`, with a note to grep for `json.load`/
  `read_csv` inside cells whose prose claims to compute something "live".

**REVIEW_4** found a real inconsistency I had carried from the start, and a cosmetic one:

1. **The headline denominator was wrong.** "5 of 18 coordinate-bearing region tables" counted
   `refdata.microagrobiome.bgc_catalog` as coordinate-bearing, while the census in the same
   report tags it `coords=no` and notes it would "badly mislead" a coordinate search. Verified
   against `bgc_joinability.csv` joined to `annotation_sources.csv`: of the 18 tables assessed,
   **16 are `coords=yes`, 1 is `packed`, 1 is `no`** — so 17 are coordinate-bearing, not 18.
   Corrected throughout to "5 of 17", with the eighteenth kept in the assessed set and labelled
   as the one table with no coordinates at all, since a researcher hunting BGC tables *would*
   reach for it and should be told why it cannot work. The headline table now separates
   "blocked" (2) from "no coordinates at all" (1) rather than lumping them as 3.
2. **The figure had 2026-10-02 baked into its title** after a full 10-06 re-execution — the
   same stale-snapshot class, in pixels. Now read from `nb01_summary.json` at plot time, so the
   title carries the snapshot date and SemCat version and cannot go stale again.

Re-ran the whole chain after each source edit rather than making an exception for "it's only a
comment" or "it's only the figure" — that exception is precisely what caused Correction 3.
All artifacts now sit in one 21:12–21:21 window, SemCat 0.24.2, verdict unchanged
(H2 supported, recall 32.3%, strict precision 86.4%).

**Four review rounds, each finding less.** REVIEW_1: two substantive defects (mixed snapshots,
unimplemented pre-registered dedup). REVIEW_2: one substantive (a "live" cell reading a cached
file) plus two stale figures. REVIEW_3: three cosmetic/hygiene items. REVIEW_4: one real
denominator error, one cosmetic. Three of the seven findings were the same defect class —
a cached or hardcoded value silently carrying an old snapshot — which survived two of its own
fixes. The WORKLOG above is left as written at each stage rather than retro-edited; the "5 of
18" phrasing in earlier entries is what I believed then, and this entry is the correction.

Verdicts have now survived five full-chain re-runs, two SemCat versions (0.19.28, 0.24.2), two
adjudication policies and two units of analysis without moving.

## 2026-10-06 — REVIEW_5: three prose/number inconsistencies, all fixed

No computation bugs this round; all three findings were drafting errors where the prose had
drifted from the notebooks. Reviews 1–4 had not caught any of them.

1. **127 vs 128.** The Interpretation section quoted 127 `function_id` columns outside the
   regex's reach while Finding 4 and `SCOREBOARD.md` said 128. The notebook is authoritative
   (`semcat_confusion_by_facet.csv`, `fp=128`); the 127 was a leftover from the pre-re-run
   snapshot. Corrected.
2. **122 vs 119 concepts.** Same shape: Interpretation still carried the pre-registration
   figure of 122 concepts from `RESEARCH_PLAN.md` while the current snapshot has 119.
   Corrected, along with an adjacent "84%" that should have been 83.6%.
3. **A conflation in the headline use-case finding, and the one that mattered.** Finding 2 read
   "754,313 gene–BGC pairs across all 35,354 BGCs, at 13.9 genes inside per BGC" — two
   different populations in one sentence. 754,313 counts pairs within a **±5,000 bp flank**;
   13.9 counts genes strictly *inside* the BGC interval. A reader doing the obvious arithmetic
   gets 754,313 / 35,354 = 21.3 and cannot reconcile it with 13.9. Worse, **the flank was
   never mentioned in any prose document** — it existed only as `FLANK = 5000` in the notebook,
   so the discrepancy was unresolvable without reading the source. Rewritten as a two-row table
   that names the window for each figure and says which one carries the biological check (13.9,
   the inside-count) and why the other is larger by design.

Finding 3 is the most useful of the five rounds for the report's readers: the other findings
were wrong numbers, this one was a number that was right but unverifiable from the text.

Verdicts untouched. No notebook source changed this round, so no re-run was needed — the
artifacts remain the single 21:12–21:21 chain.

## 2026-10-06 — REVIEW_6: domain-order pseudo-replication, fixed

Sixth round verified every prior fix still holds — 28 chain artifacts in one run window,
`claims.json` hash matching, all notebook numbers reproducing to the decimal, both figures
visually checked against the reported values — and found one new item, rated nice-to-have.

**The 94% domain-order statistic was pair-level, not protein-level.** A cluster carrying
repeat copies of PF00005 or PF00528 contributes several pairs to the join, so each such
protein voted more than once. This is precisely the pseudo-replication class the project
handles carefully elsewhere (per-`schema_sig` dedup in NB03, with Felsenstein cited in the
plan for it) — and I had not applied the same care to NB04. The reviewer checked materiality
before flagging it and found the duplicate rows all agreed with the majority order, so it was
disclosed as cosmetic rather than a defect.

Fixed anyway, because the project's own standard requires it. NB04 now computes a
protein-level statistic — one cluster, one vote, by majority of its pairs — alongside the
pair-level one: **6,167 of 6,530 proteins = 94.4%**, against 6,578 of 6,963 pairs = 94.5%.
**395 proteins (6%) carry repeat domains.** The correction is immaterial, which is worth
stating plainly: it confirms the finding rather than qualifying it. Both figures are now in
`REPORT.md` with the deduplicated one quoted, and a Limitations bullet records where
pseudo-replication was checked and that neither check happened until review asked for it.

Six rounds, with severity falling monotonically: two substantive defects → one substantive
plus two stale figures → three hygiene items → one denominator error plus one cosmetic →
three prose/number drifts → one immaterial statistical refinement. Verdicts unchanged
throughout: H1 and H0 refuted, H2 supported, recall 32.3%, strict precision 86.4%, census 51
entries, 5 of 17 coordinate-bearing region tables directly joinable.

## 2026-10-06 — REVIEW_7: a wrong number in the deliverable, and its root cause

Seventh round re-derived every headline figure from the raw artifacts rather than the prose,
and found an error six prior rounds had missed.

**Lenient precision was wrong in three places.** `REPORT.md` (×3), `SCOREBOARD.md` and
`claims.json` all said **56/59 = 94.9%**. The notebook's printed output,
`data/audit_precision.csv`, `data/nb03_summary.json` and the figure's own title all said
**55/59 = 93.2%**. Verified directly: the current run has `wrong_cardinality=4` and
`wrong_label=4`, so lenient = 51+4 = 55. The 94.9% was true of an earlier run where the split
was 5/3. Corrected everywhere. Strict precision (86.4%) and recall (32.3%) were right
throughout, and the H2 verdict keys off strict precision, so no verdict moved.

**The root cause is the more useful finding, and it undercuts a claim I had made.** `03`
samples values with `SELECT col ... WHERE col IS NOT NULL LIMIT 60` — and `LIMIT` without
`ORDER BY` has no row-order guarantee across separate Spark/Iceberg executions. So repeated
full-chain re-runs can adjudicate a *different* 60 values per column, which is exactly how one
column migrated between `wrong_cardinality` and `wrong_label` between runs. The README had
claimed the audit was "seeded and reproducible"; the seed fixes which **columns** are audited,
not which **values** within them. That claim was overstated and is now corrected to say
precisely what is and is not reproducible, with the observed ±2-point range on lenient
precision stated.

**Fix considered and deliberately not applied.** `SELECT DISTINCT col ... ORDER BY
xxhash64(CAST(col AS STRING)) LIMIT 60` is deterministic and samples distinct values, which is
what format-checking actually wants. Measured on the worst cases: ~20 s for a low-cardinality
column on a 2.68B-row table, ~101 s for a high-cardinality one — roughly 1–2 h for the full
200-column audit, plus a full chain re-run. I did not adopt it, for a reason worth recording:
changing the notebook source without re-running would reintroduce the source-≠-outputs defect
that Corrections 3 and 5 were about, and spending 1–2 h of cluster time on a change that moves
no verdict is the user's call, not mine. Logged as Future Direction 7 with the measured costs
attached so the decision can be made on numbers.

Also tested and rejected `ORDER BY col` (deterministic but returns the 60 *smallest* values —
biased, and would have made the audit worse) and `ORDER BY xxhash64(col)` without `DISTINCT`
(deterministic but groups identical values, so a 60-row sample can be one repeated value).

Seven rounds. Severity has fallen throughout but has not reached zero, and this round produced
a genuine factual error in the primary deliverable — which argues the reviews are still
earning their cost rather than that the project is finished.

## 2026-10-06 — REVIEW_8: converged; status → reviewed

Eighth round found **no new substantive defect**. It independently recomputed precision and
recall from `data/audit_precision.csv`'s raw verdict tally (`correct=51, wrong_cardinality=4,
wrong_label=4, sentinel_only=2` → 51/59 strict, 55/59 lenient) and reproduced both to the
decimal; confirmed `claims.json`'s hash matches `REPORT.md`; confirmed all 28 chain artifacts
sit in one execution window; and spot-checked NB04's protein-level dedup in source. Its two
remaining items were cosmetic carryovers, both now closed: the corrections section had not been
extended to cover `REVIEW_7`'s finding (now Correction 6, in both `REPORT.md` and
`SCOREBOARD.md`), and `beril.yaml.artifacts.review` was still `false`.

Status set to `reviewed`.

**On stopping.** `REVIEW_8` made a process observation worth recording: this reconciliation-style
review has converged, and further rounds of the same checks have low expected yield. The
productive next target is the dimension this project never tested at all — SemCat's
`column_embeddings`, `edges`, and the `semcat resolve` / `semcat joins` CLI paths, which are
the components most likely to change the recall verdict. That is Future Direction 2, not a
review round.

Eight rounds produced: two substantive defects (R1), one substantive plus two stale figures
(R2), three hygiene items (R3), one denominator error plus one cosmetic (R4), three prose/number
drifts (R5), one immaterial statistical refinement (R6), one real factual error with a
reproducibility root cause (R7), none (R8). Four of the eleven findings were a single defect
class — a cached, hardcoded or stale value silently carrying an old snapshot — which survived
two of its own fixes before the detector in `memories/pitfalls.md` was widened enough to catch
it. **No verdict moved in any round.** H1 and H0 refuted, H2 supported, census 51 entries /
24 coordinate-bearing, 5 of 17 coordinate-bearing region tables directly joinable.

Not submitting; that decision is the user's.

## 2026-10-06 — REVIEW_9: stale claims hash, fixed; all three hashes aligned

No new defect in the analysis — the reviewer re-derived the precision/recall tally, the
18-table collocation breakdown and both summary JSONs, and all reproduced the report exactly.

It did find that `claims.json`'s `report_hash` had gone stale: I extended the corrections
section in response to `REVIEW_8` and never rebuilt the ledger, so the binding meant to prove
ledger-matches-report was false. The substance was fine — every locator and flag still matched
word-for-word — but the proof was not. **Fourth distinct recurrence of this project's signature
defect**, this time one layer above the data: an artifact that caches a hash rather than a
number. Rebuilt; `REPORT.md`, `claims.json` and `REVIEW_9.md`'s footer now all read
`a825fceb…`.

The pattern is worth stating once more plainly, because it is the most transferable thing this
project produced: **every derived artifact that records a value computed elsewhere — a cached
CSV, a hardcoded figure title, a prose number, a content hash — is a snapshot that will
desynchronise unless something regenerates it in the same pass.** It recurred here after being
diagnosed, documented in `memories/pitfalls.md`, and fixed twice. The staleness-detection
command in that file now globs `data/*`, `figures/*` and the notebooks; it should arguably also
check `claims.json`'s hash against `REPORT.md`, and `submit` does exactly that check, which is
how this one would have been caught anyway.

Project left at `status: reviewed` with nine reviews on record. Not submitting — the user's call.

## 2026-10-06 — REVIEW_1 suggestions 1–3 re-audited on request

Asked to address `REVIEW_1.md` suggestions 1–3. All three had already been closed during
rounds 1–9, so this pass was verification rather than new work. Verified each against artifacts
rather than against my own prior claims:

1. **Chain coherence.** All four notebooks execute in order within one window
   (01 → 21:33, 02 → 21:35, 03 → 21:39, 04 → 21:43), every `data/` and `figures/` artifact falls
   in 21:33–21:43, and `claims.json`'s `report_hash` matches `REPORT.md`. Closed by the
   full-chain re-runs logged on 10-06.
2. **Sweep failures.** `data/sweep_failures.json` holds 0 entries; `REPORT.md` says "the sweep
   completed with **0 failures**", with the earlier 13 recorded as a dated historical note.
3. **`schema_sig` dedup.** Implemented in `03_semcat_grade.ipynb` §2b-bis; both rates reported
   (recall 32.3% per `schema_sig`, 30.0% per column).

**One real leak found during the reconciliation audit.** A systematic diff of every headline
figure in `REPORT.md`/`SCOREBOARD.md` against the four summary JSONs turned up a claim
*heading* still reading "table-level coverage is 79% against the live catalog" while the
claim's own evidence line underneath it said `agreement 0.803`. A heading contradicting its own
evidence is worse than a stale body number, because the heading is what gets quoted. Corrected
to 80.3% and the ledger rebuilt; `REPORT.md` and `claims.json` now both hash to `16fb00ff…`.

The same audit flagged ten other apparently-stale values; all ten were inside the Corrections
narrative, where they are historically accurate by design (e.g. "`REPORT.md` quoted 883
accessible tables ... while the notebooks produced 826"). One near-miss worth noting: the
scoreboard's `function_id 30/38 = 79%` matched the stale-value pattern but is current and
correct — a reminder that a string search for old numbers produces false positives and the
context has to be read.

**Revision History extended** with two entries, neither a deviation:
- **v3** records that the pre-registered `schema_sig` dedup was *initially omitted* and only
  implemented after `REVIEW_1.md` caught a staging clone in the audit sample. The plan made a
  methodological commitment the first execution failed to honour; that belongs in the record
  even though implementing it moved no verdict (recall 30.0% → 32.3%).
- **v4** records the Q2 scope explicitly: the executed analysis matches the plan's stated
  intervention (5 of 25 SemCat tables) exactly, but the resulting verdict is easy to over-read,
  so the untested surface (`column_embeddings`, `edges`, the absent `semcat` CLI) is named in
  the plan as well as the report.

`beril`'s own `plan_digest` re-verified after both appends: `939a7492…`, matching the recorded
`plan_hash`. The approval remains valid — Revision History sits below the hashed region by
design.

No hypothesis verdict moved. Suggestions 4 and 5 from `REVIEW_1.md` were not actioned: 4 is
moot (it asked for a note explaining that notebooks reflected two different snapshots; they no
longer do), and 5 (a census summary chart) remains open as a genuine nice-to-have.

## 2026-10-06 — REVIEW_10: prior findings closed; one nit fixed, one declined with reason

Tenth round re-derived the core numbers from raw artifacts and confirmed every prior finding
closed, including `REVIEW_9`'s hash mismatch (`REPORT.md` and `claims.json` now both
`16fb00ff…`). Two cosmetic items:

**Fixed.** `README.md`'s Status line hardcoded "REVIEW_9.md" and went stale the moment
`REVIEW_10.md` landed — a miniature of this project's signature defect. Rewritten to reference
"the highest-numbered `REVIEW_N.md`" so it cannot go stale again, rather than bumping the
number and reintroducing the same problem next round.

**Declined, with reason.** `data/nb04_summary.json` records `collocation_blocked: 3`, which
sums the CSV's `blocked` (2) and `impossible` (1) rows under one coarser label. The field is
arithmetically correct but ambiguously named. I checked: **nothing in `REPORT.md` or
`SCOREBOARD.md` cites it** — both quote the finer breakdown directly from
`bgc_joinability.csv` — so no published number is affected.

Renaming it would mean editing NB04 source, which under this project's own rule (Corrections
3 and 5) obliges a full-chain re-run. That re-run carries a non-trivial cost it would be
dishonest to ignore: the audit's value sample is not order-stable (`LIMIT` without `ORDER BY`,
diagnosed in Correction 6), so each full re-run can shift lenient precision by ~2 points and
force another reconciliation pass across `REPORT.md`, `SCOREBOARD.md` and `claims.json`.
Trading a real risk of churn in a published figure for a cosmetic rename in an uncited JSON
field is a bad exchange. Recorded here so the decision is visible rather than silent; it is a
one-line fix for whoever next re-runs the chain for an independent reason.

Ten rounds. Every substantive finding closed; the two open items are this JSON field name and
`REVIEW_1` suggestion 5 (a census summary chart), both cosmetic.

## 2026-10-07 — deterministic value sampling implemented; chain re-run; documents reconciled

Asked to close Correction 6's root cause. Replaced NB03's value sampler and re-ran all four
notebooks in order (18:46 → 19:01 UTC).

**Design, with the rejected alternatives measured rather than assumed.** Three properties were
needed — deterministic, diverse, affordable — and no single cheap trick gives all three:

| design | determ. | diverse | worst-column cost | outcome |
|---|---|---|---|---|
| `LIMIT 60`, no `ORDER BY` | ✗ | ✓ | ~1 s | the original defect |
| `ORDER BY col LIMIT 60` | ✓ | ✗ | ~10 s | rejected: `-` sorts below every alphanumeric, so placeholder-heavy columns return nothing but sentinels |
| `ORDER BY xxhash64(col) LIMIT 60` | ✓ | ✗ | ~67 s | rejected: identical values hash identically; `gene_id` on a 2.68B-row table returned the same id repeatedly |
| `DISTINCT` + `ORDER BY xxhash64` | ✓ | ✓ | ~101 s | adopted |

The hash-bucket prefilter (`pmod(abs(xxhash64(...)), 256) = 0`) is applied only where SemCat
reports `ndv > 100,000`, cutting the `DISTINCT` aggregation ~256× (101 s → 67 s) while staying
a pure function of the value. It is skipped for low-cardinality columns, where bucketing could
leave fewer than 60 distinct values. Using SemCat's own `ndv` to pick the strategy is a small
irony worth noting: the catalog under evaluation is load-bearing for the evaluation's cost.

**A prediction made before the run, and it held.** Recall adjudicates by label-family matching
and never reads sampled values, so it should not move. It did not: 32.3% per `schema_sig`,
30.0% per column, identical to the prior run. Only precision depends on the sample.

**What changed (11 summary fields).** Seven from the sampler, two from live drift, one new
metadata field:

| field | before | after | cause |
|---|---|---|---|
| `audit_checkable` | 59 | 60 | sampler |
| `audit_sentinel_only` | 2 | 1 | sampler |
| `audit_wrong_cardinality` | 4 | 5 | sampler |
| `audited_precision_strict` | 86.4% | **85.0%** | sampler |
| `audited_precision_lenient` | 93.2% | **93.3%** | sampler |
| `schema_sig_groups_precision` | 59 | 60 | sampler |
| `columns_swept` | 67,575 | 67,582 | live lakehouse drift |
| `semcat_code_version` | 0.24.2 | 0.26.1 | SemCat code bump |
| `value_sampling` | — | new | provenance field |

The mechanism is specific: `kbase.nmdc_arkin.biochemical_features_metadata.EC_Number` had
returned only `nan` placeholders under a plain `LIMIT`, so it scored `sentinel_only` and was
excluded from the denominator. `DISTINCT` surfaces the non-placeholder minority, so it now
adjudicates — as `wrong_cardinality`. Judgeable grew by one while `correct` stayed at 51,
which is why strict precision *fell* slightly even though the audit got better. That is the
right direction: a column that was previously unjudgeable is now judged, and judged against
SemCat.

**Note on the SemCat version bump.** `code_version` moved 0.24.2 → 0.26.1 but
`generated_at` did not (still 2026-10-06T19:38:26Z) and `n_tables`/`n_columns`/`n_concepts` are
unchanged — the code was upgraded without regenerating the catalog. The report header now says
so explicitly rather than implying a content change.

**No verdict moved.** H1 and H0 refuted, H2 supported, H3 refuted on its precision clause.
Both precision figures still clear 0.80 comfortably.

**Reconciliation.** 14 live figures updated across `REPORT.md` and `SCOREBOARD.md`; the
Corrections narrative was deliberately left alone, since those passages describe past states
accurately and rewriting them would erase the record. A scripted audit confirmed no stale value
survives in any live section. `README.md`'s reproducibility paragraph — which previously had to
hedge about ±2-point drift — now documents the deterministic query instead. Future Direction 7
struck through as done; the obsolete Limitations bullet rewritten to past tense. Claims ledger
rebuilt: `REPORT.md` and `claims.json` both hash to `0dbd0ae1…`.

The project's headline reproducibility property has changed in kind, not just degree: the audit
figures were previously *approximately stable*, and are now *exactly reproducible* against a
fixed catalog snapshot.

## 2026-10-07 — REVIEW_11; header dates corrected

Eleventh review found **no new substantive defect**. It went beyond re-reading prior reviews
and issued three fresh live Spark queries against the lakehouse, independently confirming
`n_columns = 91,246`, `n_tables = 2,509` and `gene_bgc = 35,354` against the report's stated
figures, and recomputed `sha256sum REPORT.md` against `claims.json`.

Two notes from it, handled differently:

- It observed that `REVIEW_10` had attributed the `float('nan')` guard to `src/validators.py`
  when it lives in `src/semcat.py`. Checked my own files: `memories/pitfalls.md` names no file
  for that entry, so the misattribution was internal to that review and there was nothing in
  the project to correct. Recorded rather than silently passed over, because "a prior review
  was wrong" is itself worth being able to trace.
- SemCat's `code_version` had drifted again, 0.26.1 → **0.27.0**, with `generated_at` and
  `n_columns` unchanged — the fourth instance of a code bump without catalog regeneration.

**One real staleness found while checking that second point.** The report header still read
`Date: 2026-10-06 · Lakehouse snapshot: 2026-10-06` when the deterministic-sampling chain
actually ran on **2026-10-07**. Corrected, and the header rewritten to separate the two things
that had been conflated: the catalog *content* is pinned by `generated_at`
(2026-10-06T19:38:26Z, stable across four version stamps), while `code_version` records only
what this run happened to read. `Status:` in the header also still said `analysis`; it is
`reviewed` in `beril.yaml` and now says so.

**`REVIEW_11.md` is consequently one edit stale** — its footer records `0dbd0ae1…`, the report
is now `c10081e9…`. `claims.json` was rebuilt and matches the current report. The brief was to
run the review once, so I have not triggered a twelfth; a current review is required before
`submit`, and that is a one-command step whenever wanted.

## 2026-10-07 — REVIEW_12: current review in place; REPORT.md untouched

Ran one more review so the latest one covers the current `REPORT.md`, per instruction, and made
no edits to `REPORT.md` afterwards.

**No new substantive defect.** The reviewer did its own verification rather than restating
prior rounds: recomputed `sha256sum REPORT.md` against `claims.json`, confirmed the header
dates now read 2026-10-07, programmatically scanned all four notebooks for code cells missing
saved output (only the same two inert import/setup cells earlier rounds identified), and
re-parsed six primary CSVs with Python's `csv` module rather than `wc -l` — catching that
`wc -l` miscounts one file because a quoted field contains an embedded newline. Every row count
matched the report.

That last detail is worth keeping: a line count is not a row count for CSVs with quoted
multi-line fields, and `data/annotation_sources.csv` has exactly that shape because the census
`notes` column carries prose. Any future check of these artifacts should parse rather than
count lines.

**Hash state, verified after the run:**

| artifact | sha256 (first 16) |
|---|---|
| `REPORT.md` | `c10081e9b05ca966` |
| `REVIEW_12.md` footer | `c10081e9b05ca966` |
| `claims.json` `report_hash` | `c10081e9b05ca966` |

All three agree, `REPORT.md` is byte-identical to its state before the review, and
`REVIEW_12.md` carries exactly one footer. The stale-review condition flagged at the end of the
previous entry is cleared.

Twelve rounds. The last four found only process-level items — a stale date, a misattribution
inside a prior review, a cosmetic JSON field name — rather than anything analytical. Project
remains at `status: reviewed`. Not submitting.

## 2026-10-07 — Correction 8: `kbase.genomes.feature` was not unusable after all

A reader pointed out that the `gene_function_ecological_agora` project already joins
`kbase_genomes.feature` to `contig_x_feature` to place features on contigs — a join this
census had declared impossible. Checked live; they were right.

**What I had done wrong.** The census read `kbase.genomes.feature` in isolation, saw
`start`/`end`/`strand` and no sequence column, and recorded 1,011,650,903 rows of coordinates
as unplaceable. I never looked at the other 17 tables in `kbase.genomes`. One of them is
`contig_x_feature(contig_id, feature_id)`.

**Verified by execution:** 1,011,650,903 rows, 1,011,650,903 distinct `feature_id` — an exact
1:1 placement — across 32,868,698 contigs. The join returns `contig_id` + `start` + `end` +
`strand` + `type`, and a self-join on a single contig returns 14–15 CDS neighbours within
±5 kb, which is plausible gene density. Reclassified `blocked` → `bridged (1:1)`:
**positionally joinable 5 → 6**, blocked 2 → 1.

**Not verified, and labelled as such.** The same database carries `feature_x_protein`,
`protein` (with `hash`) and `functional_annotation_rast` (253,173,194 rows of RAST free-text
function on `protein_hash`), so coordinates and function look reachable in one database. The
five-way join **exceeded a 400 s timeout** and I did not retry it, so it is recorded as
schema-confirmed only and `kbase.genomes` gets no verified function-assignment credit in the
census. An earlier `DESCRIBE` in this session also hung once and succeeded on one retry — the
cluster is intermittently slow on this database, which is itself worth knowing.

**After the correction I re-ran the same check against the other negative case.**
`refdata.smag` has no feature or gene table of any kind, so `refdata.smag.bgc` stays `blocked`.
Making one correction is not evidence the rest of the category is right; checking was cheap.

**Two lessons, the second more uncomfortable than the first.**

1. *Method.* Joinability is a property of a table's **database**, not of its own column list.
   The census classified on column lists, so it was structurally unable to see bridge tables.
   That is a design flaw in how I built ground truth, not a slip on one row.
2. *Detection.* **Twelve independent review rounds did not find this.** Every one of them verified
   the report against the project's own artifacts — and the artifact was itself wrong. Internal
   consistency checking cannot surface an error of omission in the underlying survey; it can
   only confirm that the write-up faithfully reports whatever the survey found. It took a
   reader who knew a different project's query. The twelve reviews were not wasted — they
   caught seven real defects — but their blind spot is now demonstrated rather than theoretical,
   and that is worth more than another round of the same checks.

No hypothesis verdict is affected: this is a census/use-case finding, not an instrument one.
H1 and H0 remain refuted, H2 supported, recall 32.3%, strict precision 85.0%.

Chain re-run in order (all four), `REPORT.md`/`SCOREBOARD.md`/`README.md` reconciled, claims
rebuilt — report and ledger both hash to `3ce22132…`. Also picked up two live drifts in the
same run: `columns_swept` 67,582 → 67,587 and SemCat `code_version` 0.26.1 → 0.27.0
(`generated_at` and column count unchanged — the fourth code bump without regeneration).

## 2026-10-07 — REVIEW_13: covers the corrected report; two documentation nits left unfixed

`REVIEW_13.md` is the first review of the post-Correction-8 state. Hash check after the run:
`REPORT.md`, `REVIEW_13.md`'s footer and `claims.json` all read `3ce22132…`, and `REPORT.md` is
byte-identical to its state before the review — no edits were made to it afterwards, per
instruction.

It verified the correction independently rather than taking the worklog's word for it:
re-parsed `bgc_joinability.csv` with Python's `csv` module and confirmed exactly 5 `direct` +
1 `bridged (1:1)` = 6, matching Finding 1; re-derived the precision tally
(51 correct / 5 wrong_cardinality / 4 wrong_label / 1 sentinel_only) to the reported 85.0%
strict and 93.3% lenient over a 60-column denominator; confirmed recall 30/100 per column; and
ran this project's own mtime staleness check against the chain.

**It found a factual error in my own prose, and it is right.** Correction 8 says "ten
independent review rounds did not find this." The true count is **twelve** — `REVIEW_12.md`
completed immediately before Correction 8. `WORKLOG.md` compounds it by saying "ten" and then
"eleven" two sentences later. The error appears in `REPORT.md`, `SCOREBOARD.md` and this log.

**Deliberately not fixed.** The instruction for this pass was to run the review once and make
no edits to `REPORT.md` afterwards. The claim spans `REPORT.md` and `SCOREBOARD.md`, so
correcting it in one and not the other would leave them contradicting each other — worse than
both being consistently wrong in a way that is now documented here. This entry is the
correction of record: **the count is twelve, not ten**, and the point it supports is
strengthened rather than weakened by the larger number.

Also carried forward and unfixed, first raised in `REVIEW_8`: `README.md` describes
`memories/pitfalls.md` as "four SemCat traps and one tooling trap" when it now holds ten
entries. Left alone for the same reason — this pass was scoped to the joinability correction
and one review.

Both are one-line fixes available whenever the report is next opened. Project remains at
`status: reviewed`. Not submitted.

## 2026-10-16 — REVIEW_13 nits fixed

Applied both low-priority items from `REVIEW_13.md`. The Correction 8 review count now reads
**twelve** in `REPORT.md`, `SCOREBOARD.md` and the Correction 8 entry above, which also fixes
that entry's ten/eleven self-contradiction. `README.md`'s Quick Links now describe
`memories/pitfalls.md` as holding ten traps. No numbers, figures or verdicts changed. Because
`REPORT.md` changed, `REVIEW_13.md` no longer matches the current report hash, so the project
needs a fresh `/berdl-review` before `/submit`.

## 2026-10-16 — Claims ledger: pfam value check executed, conflation claim gets a second stream

- **pfam value check, now executed.** The `end - start + 1 == alignment_length` check behind the
  `pfam_annotation_gff` claim had only been recorded in prose (`src/census.py`, NB02 §5). NB02
  §9 (cell 29) now runs it on a seeded Bernoulli sample (fraction 1e-5, seed 42): **N = 26,779,
  0 mismatches, 0 NULL rows**, max `end` 3,625. Saved to `data/pfam_coordinate_check.json`.
  Claim wording and confidence unchanged; still single-stream, still flagged.
- **Conflation claim, second stream.** NB02 §10 (cell 31) checks NB01's SemCat-metadata typing
  of the 78 `coordinate` columns against this census: 36 overlap, **0 contradictions**.
  Saved to `data/semcat_coordinate_crosscheck.csv`. Ledger mismatch count 2 → 1.
- **Citations corrected:** joinability claim's census support nb02 cell 9 → 14; conflation
  claim nb01 cell 3 (markdown) → 6. Both new cells were appended to the end of NB02, so no
  existing cell index moved. Both ran in a fresh kernel with only NB02's setup cell before them;
  the rest of the chain was not re-run.
- **Open, not fixed:** a quote check of every claim citation shows most of the *other* locators
  also point at the wrong cell. The quoted values exist in the notebooks but at different
  indices, probably left over from earlier restructuring. `beril claims build` marks them
  "resolved" because it checks only that the cell exists, not its content.

## 2026-10-16 — Claims citations: all 12 repointed (one-based)

**Correction to the entry above.** `beril claims` reads `#cell-N` as the **one-based** ordinal in
the notebook's `cells` array (`beril_cli/claims_cmd.py`, `resolve_evidence_pointer`). The entry
above counted from 0, so its cell numbers are one too low: the pfam check is **cell 30** and the
census cross-check is **cell 32**.

A one-based quote check (every number in each quoted support must appear in the cited cell's
source or output) found **0 of 12** citations matching. Three were my off-by-one errors. Nine
predated today and pointed at the wrong cell under either numbering, probably left over from
earlier restructuring. Three of those nine were paraphrases whose exact figures were never
printed (`0.803`, `5,000`, `18 region tables`); their quotes are now verbatim excerpts of the
cited output. All 12 were repointed, the ledger rebuilt, and the check re-run: **12/12 match**,
12 resolved. Claim wording, confidence and status unchanged; confidence mismatch still 1 (pfam,
single-stream by nature).

Also verified: `nb04_summary.json`'s `collocation_blocked: 2` counts `blocked` + `impossible`,
consistent with the claim's "1 blocked, 1 with no coordinates". Not a discrepancy.

## 2026-10-16 — review completed → reviewed (REVIEW_14)

[`REVIEW_14.md`](REVIEW_14.md), reviewer Claude (`claude-sonnet-5`), on `REPORT.md`
`sha256:7e7088ed…`. Assessment: no critical or important issues. Both REVIEW_13 nits confirmed
fixed, the two new NB02 cells confirmed as real computations, and the NB02 mtime gap traced and
judged benign (appended cells over pinned inputs, no re-sweep). Two low-priority items raised:
`REPORT.md`'s Generated Data table omits `pfam_coordinate_check.json`,
`semcat_coordinate_crosscheck.csv` and `ground_truth_table_facets.csv`; and the earlier entry
today saying the new cells ran with "only NB02's setup cell before them" leaves out that `cen`
was also built from `CENSUS` in that kernel. Status stays `reviewed`.

## 2026-10-16 — REVIEW_14 suggestions fixed

- `REPORT.md` Generated Data table now lists `pfam_coordinate_check.json`,
  `semcat_coordinate_crosscheck.csv` and `ground_truth_table_facets.csv`.
- **Correction to the "pfam value check executed" entry above:** it says the two new NB02
  cells ran "in a fresh kernel with only NB02's setup cell before them". That is incomplete. The
  kernel ran NB02's setup cell (cell 2), then `cen = pd.DataFrame(CENSUS)`, which is the first
  line of NB02 cell 15 and builds the census frame from the curated, pinned `src/census.py`, and
  then the two new cells. No sweep, live listing or other chain cell ran.

## 2026-10-16 — review completed → reviewed (REVIEW_15)

[`REVIEW_15.md`](REVIEW_15.md), reviewer Claude (`claude-sonnet-5`), on `REPORT.md`
`sha256:a172f57e…`. The `claims.json` rebuild in the REVIEW_14-fix pass recorded the same hash.
Assessment: no critical or important issues. Both REVIEW_14 suggestions confirmed applied, and
all 12 claim citations independently re-verified. Raised only trivial, optional items: the
per-notebook summary JSONs, `sweep_failures.json` and `row_counts_verified.json` are not in the
Generated Data table (judged a defensible editorial choice); and several quotes I called
"verbatim excerpts" are lightly reformatted (fragments joined with `;`, whitespace collapsed)
rather than byte-literal, though every value checks out. Status stays `reviewed`.

## 2026-10-16 — Session provenance note

From 2026-10-16, most of the author's prompts in this session were drafted by another Claude
session reading this session's output, and then submitted by the author. See
<https://github.com/beril-doe/coscientist-bench/issues/20>.

## 2026-10-16 — approved by 0000-0001-9076-6066 → complete

Approved on [`REPORT.md`](REPORT.md) `sha256:a172f57e…` with [`REVIEW.md`](REVIEW.md) (a copy of
`REVIEW_15.md`). Concluded: BERDL holds 51 gene/protein annotation tables, but of 17
coordinate-bearing region tables only 6 join to genes by position. SemCat's `content_type`
label lookup is high-precision (85% strict) and low-recall (30%), so it is an unreliable way to
find them. Caveats accepted at approval: one claim (`pfam_annotation_gff` coordinate system)
stays high-confidence on a single evidence stream, and Future Direction 2, grading SemCat's
embedding and edge retrieval paths, remains open.
