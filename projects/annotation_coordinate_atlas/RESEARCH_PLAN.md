# Research Plan: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Research Question

Two coupled questions, one descriptive and one evaluative.

**Q1 (census).** Across all BERDL tenants, which tables assign a function to a
gene or protein, and which annotate a *region* of a genome, gene, or protein
(domain, motif, BGC, operon, CRISPR array, defense system, mobile element)? For
each: does it carry coordinates (sequence/contig reference, start, end, strand);
is the coordinate system **nucleotide** (genome/contig), **amino-acid**
(protein/residue), or **model** (HMM profile position); which identifier systems
appear (Pfam, KO, EC, GO, InterPro, COG, antiSMASH/MIBiG, UniProt, …); and how
many rows does it have?

**Q2 (instrument, FINER/PICO-framed).**
*Population* — the 788 tables in the 8 BERDL tenants this account can read.
*Intervention* — discovering the Q1 answer using SemCat
(`globalusers.semantic_catalog`): its `concepts`, `columns.content_type`,
`tables.row_count`, and `verified_joins` layers.
*Comparator* — discovering the same answer by exhaustive live `DESCRIBE` of all
788 tables plus manual inspection, which is the ground truth.
*Outcome* — per-facet precision and recall of SemCat against that ground truth,
plus a per-table verdict of **found / missed / wrong**.

The deliverable the user asked for: a table of annotation sources; a note on
which could support BGC-adjacent searches (genes near a BGC region; multi-domain
searches); and an assessment of SemCat's usefulness.

### Scope assumptions (stated, not confirmed)

These two were put to the user and the question timed out. The plan proceeds on
the recommended defaults; both are cheap to reverse at the checkpoint.

1. **Inaccessible tenants are reported, separately.** SemCat indexes 21 tenants;
   this account reads 8. The main results table covers only tables whose
   properties were *verified* against live data. A second, clearly-labelled
   table reports SemCat's assertions for the ~1,750 tables in the 13
   unreadable tenants (enigma 866, phagefoundry 283, protect 160,
   kbaseincubator 91, arkinlab 83, usgs 70, …), marked unverifiable. Dropping
   them would hide the only operon-region and PUL tables found
   (`enigma.genome_depot_enigma.browser_operon`, `arkinlab.dbcan.dbcan_pul`),
   which bear directly on the stated use case.
2. **Triage is exhaustive, not sampled.** All 788 accessible tables get a live
   schema pull. Justified by measurement, not optimism: a timed sweep of the
   `kescience` tenant did 158 tables / 1,017 columns in 19.6 s (0.12 s/table),
   so the full sweep costs ~95 s.

## Competing Hypotheses

About SemCat as the discovery instrument for molecular-annotation tables. (Q1,
the census, is enumeration — it has an answer, not a hypothesis. Q2 is where the
genuine uncertainty lives, and it is what makes this project falsifiable.)

- **H0** (null): SemCat's semantic layer adds nothing over a naive column-name
  regex. Anything `content_type` finds, `RLIKE` on `column_name` finds too, and
  SemCat contributes no table and no correct label that the regex misses.
- **H1**: SemCat is a sufficient discovery instrument. Its semantic labels have
  both high recall (≥80% of ground-truth annotation/coordinate columns carry an
  appropriate `content_type`) and correct coordinate-system typing, so a
  SemCat-only workflow answers Q1.
- **H2** (rival): SemCat is **high-precision, low-recall** — a good seed, a bad
  bound. The labels it applies are mostly correct (≥80% precision) but it labels
  a minority of the relevant columns (<50% recall). Correct workflow: start from
  SemCat, then expand.
- **H3** (rival): SemCat's value is **structural, not semantic**. Its reliable
  contributions are *coverage* (2,599 tables across 21 tenants, including many
  invisible to a given user's inventory) and *bookkeeping* (`row_count`,
  `n_columns`, `description`), while its interpretive layers (`concepts`,
  `content_type`) are unreliable in **both** directions — missing most relevant
  columns *and* mislabelling some it does annotate. Workflow consequence: use
  SemCat to enumerate what exists, never to decide what a column means.

H2 and H3 are not the same claim and the data separates them: they differ on
**precision**. H2 says applied labels can be trusted; H3 says they cannot.

### Per-hypothesis predictions, falsification & decision criteria

Unit of analysis throughout: **one column of one table** (`node` in
`semantic_catalog.columns`), restricted to the 8 readable tenants. Columns are
the right unit because labelling is applied per column. They are *not* fully
independent — columns within a table, and tables cloned across staging databases
(`nmdc.nmdc_metadata_staging_20260820/0824/0908/0923` all carry
`genome_feature_set`), share a labelling fate. Correction: compute every rate
twice, once per column and once per **distinct `schema_sig`** (SemCat's own
schema fingerprint), and report both. Where they disagree, the schema_sig figure
is the one quoted, since replicated staging copies otherwise inflate n without
adding evidence — the metadata analogue of Felsenstein's (1985) phylogenetic
pseudo-replication.

| Hypothesis | Prediction (what we'd observe if true) | Falsification test (result that rejects it) | Unit of analysis (what one row is; why independent) | Decision criterion (threshold/comparison) |
|---|---|---|---|---|
| **H1** — sufficient instrument | Ground-truth annotation/coordinate columns almost all carry an apt `content_type`; `coordinate`-labelled columns separate nucleotide from amino-acid; the SemCat-only candidate list ≈ the ground-truth list | Any facet shows recall <80%, **or** the `coordinate` label provably conflates coordinate systems | One column, deduplicated by `schema_sig` | Recall ≥0.80 on *every* facet (function-id, span, strand, seq-ref) AND coordinate-system typing resolvable from SemCat fields alone AND ≤10% of ground-truth tables missed |
| **H2** — high precision, low recall | Recall <0.50, but labels that *are* applied are right: a Pfam-labelled column really holds Pfam accessions, a strand-labelled column really holds genomic strand | Precision <0.80 on the audited facets — i.e. applied labels are themselves untrustworthy | One column, deduplicated by `schema_sig` | Recall <0.50 AND precision ≥0.80, both on the hand-audited facet set |
| **H3** — structural not semantic | Recall <0.50 **and** precision <0.80 (both directions bad), while `row_count` is exact and table-level coverage exceeds the user's own inventory | `row_count` disagrees with live `COUNT(*)` beyond staleness, **or** precision ≥0.80 (which would make it H2), **or** SemCat's table list adds nothing beyond the accessible inventory | One column (rates); one table (`row_count` accuracy, coverage) | Recall <0.50 AND precision <0.80 AND `row_count` exact on ≥95% of verifiable tables AND SemCat surfaces ≥1 relevant table absent from the user's accessible inventory |
| **H0** — no added value | The SemCat-driven candidate set is a subset of the regex-driven set, with no correct label the regex could not infer from the name | SemCat contributes ≥1 relevant table or ≥1 correct, name-unguessable label | One column / one table | Rejected if SemCat yields any true positive a name regex misses (e.g. a correctly typed column whose name is uninformative) |

H0 is adjudicated by rejection, per the decision rule below.

### Prior evidence already in hand (exploration, logged in WORKLOG.md)

Recorded here because it makes the prior honest, and because a reviewer should
know the plan is not blind. It is **not** the pre-registered test — the frozen
tests above are run over the full 788-table ground truth, not these spot checks.

- `concepts`: all 122 labels are environmental/geochemical; zero molecular
  concepts. Already fatal to any concepts-based route.
- `content_type` is NULL on 78,730 of 93,617 columns (84%).
- Strand facet: SemCat labels **6** columns; a name regex over SemCat's own
  `columns` finds **58** (~10% recall). 2 of the 6 are wrong
  (`material_processing_set.is_stranded` is RNA-seq library strandedness), and
  true strand columns are labelled `annotation_text`.
- `content_type='coordinate'` (78 columns) mixes lat/lon, nucleotide spans, and
  residue spans under one label.
- `row_count` was exact against live `COUNT(*)` on 4 tables spanning 35K–2.68B rows.
- `verified_joins` has 6 rows for 2,599 tables.

This points at **H3**. The pre-registered job is to test it properly rather than
to confirm it, and the H3 row above carries the conditions that would break it.

## Discrimination Strategy

One 2×2 settles H1/H2/H3, built from a hand-audited facet set:

Draw a stratified audit sample of **200 columns** — 100 that SemCat labelled with
an annotation- or coordinate-relevant `content_type` (measures **precision**:
how many deserve that label?) and 100 drawn from ground-truth annotation/
coordinate columns regardless of label (measures **recall**: how many got
labelled?). Stratify across tenant and facet; adjudicate each by reading the
column's actual values, not its name.

- high recall → **H1**
- low recall, high precision → **H2**
- low recall, low precision → **H3**
- SemCat's set ⊆ regex's set with nothing added → **H0**

The coordinate-system sub-test is the sharpest single discriminator and is run
first, because it is the one facet where the *user's actual question* and
SemCat's representation are known to diverge: take every column SemCat labels
`coordinate`, and ask whether SemCat's own fields (`type`, `lower`, `upper`,
sibling columns) suffice to sort it into geographic / nucleotide / amino-acid /
HMM-model. If they do not, H1 dies regardless of the recall numbers, since
coordinate system is explicitly requested per table.

## Confidence Prior

**H3: MEDIUM-HIGH.** **H2: LOW-MEDIUM.** **H1: LOW.** **H0: VERY LOW.**

Reason for the H3 lean: the exploration evidence above is already consistent with
it on four independent facets, and 84% NULL coverage caps achievable recall far
below H1's threshold. Not HIGH, because precision has only been spot-checked on
one facet (strand, 2/6 wrong) — a single facet is weak evidence for the
precision half of the claim, and strand may be unusually hard (the English word
is genuinely ambiguous between genomic strand and library strandedness, so it may
be SemCat's worst case rather than a typical one). H0 is very low because SemCat
demonstrably indexes tenants absent from this account's inventory, which a regex
over accessible tables cannot reach by construction.

Literature support is for the *framing*, not the prior: Paton et al. (2023)
treat discovery and exploration as separately-failing capabilities, which is
precisely the H3 split. No prior BERDL-specific benchmark exists — this would be
the first.

## Literature Context

See `references.md`. Two threads:

**Metadata quality / dataset discovery.** Paton, Chen & Wu (2023, *ACM CSUR*)
survey dataset discovery and exploration and supply the vocabulary for grading
SemCat; their discovery-vs-exploration distinction is the H3 hypothesis in
general form. Bianchini et al. (2023) describe PERSEUS, a semantic metadata
catalog over a data lake with the same design posture as SemCat, and treat
annotation coverage as a known weak link — so a low-recall finding here is a
general property of the architecture, not a BERDL defect. Masmoudi et al. (2024)
frame the join-discovery problem, relevant because SemCat's `verified_joins` is
effectively unpopulated (6 rows / 2,599 tables).

**Why coordinates are the right thing to ask about.** Gilchrist et al. (2021,
cblaster, 306 citations) is the canonical tool for exactly the query the user
named — finding **collocated** genes. Its requirement is per-gene sequence ID +
position in a shared frame, which is the functional test each table in the census
is scored against. Jørgensen et al. (2024, *NAR*) show positional information
carries biology in BGC work (core genes central, specialized-metabolite BGCs
distal on the *Streptomyces* chromosome), so a coordinate-free annotation table
discards real signal. van der Hooft et al. (2020) supply the MIBiG/BiG-SCAPE
background that `kescience.mgnify.gene_bgc` (`nearest_mibig`,
`nearest_mibig_class`) and `refdata.smag.bgc` (`big_scape_class`, `gcf_class`)
are expressed in.

**Gap.** No published assessment of BERDL's semantic catalog, and no inventory of
BERDL annotation tables by coordinate system. The nearest prior art is internal:
the knowledge layer surfaced `gene_function_ecological_agora`'s
`Final_Data_Catalog/Sources.md` and `plant_microbiome_ecotypes`' data manifest,
both partial, project-scoped source lists compiled by hand — which is itself
evidence that this census is repeatedly needed and has never been done once.

## Feasibility

- **Verdict**: **partial** — and the word is doing real work here, in two
  distinct ways.

- **Attrition, Q1 (census).** Nominal: 2,599 tables SemCat indexes. Readable by
  this account: 788 tables / 8 tenants / 84 databases (**30%** of SemCat's
  universe). SemCat ∩ readable ≈ 847 tables by SemCat's own count across
  kbase/kescience/nmdc/refdata — the two figures differ because `bervodata`
  (5 DBs) and `culturebotai` are readable but un-indexed, while SemCat's snapshot
  is from 2026-09-29 and the inventory from 2026-10-02. Candidate annotation
  tables within the readable set: ~164 (123 with function identifiers, 41
  coordinate-only), of which an expected 60–100 survive triage as genuine. So the
  census will be **complete for 8 tenants and metadata-only for 13** — that is
  the sense in which Q1 is partial, and it is a *grant* limitation, not a data
  limitation. It cannot be fixed by more compute.

- **Attrition, Q2 (instrument grade).** The precision/recall estimate is
  computed over readable tables only, so it is an estimate of SemCat's quality
  **on this account's slice**, generalized to the rest only by assumption. The
  13 unreadable tenants include SemCat's largest (enigma, 866 tables) and could
  have systematically different label quality. This must be stated as a scope
  limit in the report, not smoothed over.

- **Verified cheap.** Live `DESCRIBE`: 0.12 s/table measured (158 tables in
  19.6 s on `kescience`) → ~95 s for all 788. Iceberg `COUNT(*)` returns in
  seconds even at 2.68B rows, so every row count can be verified rather than
  trusted. Read access confirmed on `refdata.smag.bgc` (43,169),
  `kescience.mgnify.gene_bgc` (35,354), `nmdc.results.pfam_annotation_gff`
  (2,684,369,000), `kbase.ke_pangenome.interproscan_domains` (833,303,130).
  Denied on `enigma.genome_depot_enigma.browser_gene`,
  `arkinlab.dbcan.dbcan_pul`, `phagefoundry.phages_genomedepot.browser_gene`.

- **Limiting factor on identifier enumeration.** "Which identifier systems does
  this table use" sometimes requires reading *values*, not columns:
  `kbase.ke_pangenome.interproscan_domains.analysis` holds the member-database
  name (Pfam / TIGRFAM / PANTHER / …), so one table spans many identifier
  systems. At 833M rows a `DISTINCT` is affordable on a low-cardinality column
  but must be bounded; use SemCat's `ndv` to decide before running, and sample
  where `ndv` is large.

- **Known trap, already hit.** `$BERIL_CORE/scripts/run_sql.py` fails on-cluster
  (`No module named 'spark_connect_remote'`) — it is the off-cluster tool. This
  project uses `q.py`, a thin wrapper over
  `berdl_notebook_utils.setup_spark_session.get_spark_session`. See
  `memories/pitfalls.md`.

## Query Strategy

### Tables Required

| Table | Purpose | Estimated Rows | Filter Strategy |
|---|---|---|---|
| `globalusers.semantic_catalog.columns` | SemCat's labels — the thing under test | 93,617 | Filter `tenant IN (readable 8)` for the graded set; keep all for coverage claims |
| `globalusers.semantic_catalog.tables` | SemCat `row_count`/`description`/`provenance_class`; coverage comparison | 2,599 | None (small) |
| `globalusers.semantic_catalog.concepts`, `verified_joins` | Assess the concept and join layers | 122 / 6 | None (tiny) |
| Live `SHOW DATABASES`/`SHOW TABLES`/`DESCRIBE` over 8 readable tenants | **Ground truth**, independent of SemCat | 788 tables, ~5K columns | Full sweep; ~95 s measured |
| `nmdc.results.pfam_annotation_gff` | Pfam per gene; has both sequence span *and* HMM `model_start`/`model_end` | 2,684,369,000 | `COUNT(*)` from Iceberg metadata; `LIMIT` for value sampling |
| `nmdc.results.annotation_kegg_orthology`, `annotation_enzyme_commission` | KO and EC assignment at scale | 1.83B / 1.23B | Metadata count; sample for coordinate check |
| `refdata.bvbrc.bvbrc_feature_fact` | Genome features **with strand**; `family_ids_json` | 1,895,015,043 | Metadata count; sample |
| `kescience.interpro.protein2ipr`, `interpro.entry` | InterPro domains in protein coordinates | 1.18B | Metadata count; sample |
| `kbase.ke_pangenome.interproscan_domains` | Multi-member-DB domains on cluster representatives; `analysis` enumerates ID systems | 833,303,130 | `DISTINCT analysis` (low ndv); sample |
| `kbase.ke_pangenome.bakta_pfam_domains` | Pfam domains, pangenome | 18,807,208 | Full scan affordable |
| `refdata.jgi_virus.metavr_protein`, `refdata.jgi_mycocosm.features` | Viral / fungal features **with strand** | 369M / 17.9M | Metadata count; sample |
| `refdata.smag.bgc` | **BGC regions**: `bgc_region`, start/end, `product_prediction`, `big_scape_class`, `gcf_class` | 43,169 | Full scan |
| `kescience.mgnify.gene_bgc` | **BGC regions with `contig_id`** + `nearest_mibig` | 35,354 | Full scan; partitioned by `biome_id` |
| `kescience.mgnify.gene`, `gene_crispr`, `gene_defense`, `gene_mobilome` | Genes and other region classes in genome coordinates — the join partners for "genes near a BGC" | gene ~large; others small | Partition-aware; `contig_id` join |
| `kescience.pdb.pdb_uniprot_mapping`, `kescience.paperblast.site` | Residue-level protein coordinates | 966,977 / — | Full scan |
| `kescience.fitnessbrowser.gene`, `genedomain`, `besthitmetacyc` | Domains + gene coords (string-typed — CAST) | 456,712 | Full scan |
| `kbase.genomes.feature`, `nmdc.metadata.genome_feature_set` | Core feature tables with strand that SemCat under-labels | TBD live | Metadata count |

### Performance Plan

- **Tier**: on-cluster JupyterHub Spark SQL (`berdl_env.py --check` → on-cluster,
  direct access, no proxy). Via `q.py` in notebooks.
- **Estimated complexity**: **moderate**. No heavy joins or aggregations over the
  billion-row tables — those are touched only for metadata counts, schema, and
  bounded samples. The expensive-looking step (788 `DESCRIBE`s) is measured at
  ~95 s. The real cost is adjudication effort on the 200-column audit, which is
  judgment, not compute.
- **Known pitfalls**: four already recorded in `memories/pitfalls.md` —
  `run_sql.py` is off-cluster-only; `content_type='coordinate'` is not a genomic
  coordinate; `content_type` recall ~10% on some facets and `concepts` has no
  molecular vocabulary; SemCat indexes tables you cannot read and misses tables
  you can. Plus two from the shared universal list that bite here: string-typed
  numeric columns (`fitnessbrowser.gene.begin/end` are `string` — CAST before any
  comparison) and gene-cluster IDs being species/cluster-scoped
  (`interproscan_domains` keys on `gene_cluster_id`, a cluster representative,
  **not** a genome gene — so its protein coordinates are in a different frame
  from any genome contig and cannot be joined to one without going through a
  cluster-member mapping).

## Analysis Plan

### Notebook `01_semcat_discovery.ipynb` — what SemCat alone would tell you
- **Goal**: Record the SemCat-only answer to Q1, frozen before ground truth is
  built, so the comparison cannot be contaminated by hindsight. This ordering is
  the methodological point of the notebook.
- **Discriminating/refuting query (run first)**: the coordinate-system
  sub-test — every `content_type='coordinate'` column with its `type`,
  `lower`/`upper`, and sibling columns, classified into geographic / nucleotide /
  amino-acid / HMM-model **using SemCat fields only**. Separates **H1 from
  H2+H3**: if SemCat cannot resolve coordinate system, H1 is dead immediately.
- **Expected output**: `data/semcat_candidates.csv` (SemCat-only candidate
  tables + facets), `data/semcat_coordinate_typing.csv`.

### Notebook `02_ground_truth_sweep.ipynb` — the independent census
- **Goal**: Build ground truth without SemCat: live sweep of all 788 readable
  tables, classify every column by name+type, then hand-adjudicate each candidate
  table by reading schema and sampling values. Determine per table: region vs
  point annotation, coordinate system, sequence-reference column, identifier
  systems (including value-level enumeration where one column spans several, e.g.
  `interproscan_domains.analysis`), and live row count.
- **Discriminating/refuting query (run first)**: the strand-facet recall test at
  full scale — all ground-truth strand columns vs the 6 SemCat labels. Separates
  **H1 from H2/H3** on recall and, by auditing the 6, starts the **H2 vs H3**
  precision split.
- **Expected output**: `data/ground_truth_columns.csv`,
  `data/annotation_sources.csv` (**the user's primary deliverable**),
  `data/row_counts_verified.csv`.

### Notebook `03_semcat_grade.ipynb` — found / missed / wrong
- **Goal**: Adjudicate Q2. Join notebook 1's SemCat answer to notebook 2's ground
  truth; compute per-facet precision and recall, both per column and per distinct
  `schema_sig`; label every table in the census **found / missed / wrong**; verify
  `row_count` against live counts; assess `concepts` and `verified_joins`; and
  quantify what SemCat adds that a name regex cannot (the H0 test).
- **Discriminating/refuting query (run first)**: the stratified 200-column audit
  (100 SemCat-labelled → precision; 100 ground-truth → recall), adjudicated on
  values. This is **the** H2-vs-H3 test.
- **Expected output**: `data/semcat_grade.csv`,
  `data/semcat_confusion_by_facet.csv`, `figures/semcat_precision_recall.png`.

### Notebook `04_bgc_region_joinability.ipynb` — can the stated use case be served?
- **Goal**: Move from "has coordinates" to "is actually usable". For each
  region-annotation table, test whether its coordinates can be joined to a gene
  table in a **shared** frame: do the sequence identifiers literally match
  (`mgnify.gene_bgc.contig_id` vs `mgnify.gene.contig_id`), or is a mapping
  needed (`refdata.smag.bgc.accession_id`/`mag`)? Then demonstrate both named
  queries end-to-end: (a) genes within/near a BGC region; (b) a multi-domain
  protein search.
- **Discriminating/refuting query (run first)**: an identifier-overlap check —
  `COUNT(DISTINCT contig_id)` intersection between `gene_bgc` and `gene`. If the
  intersection is empty the coordinates are useless for collocation regardless of
  being present, which would be the most consequential negative result in the
  project and must be found early rather than assumed away.
- **Expected output**: `data/bgc_joinability.csv`, `data/example_genes_near_bgc.csv`,
  `data/example_multidomain_hits.csv`, `figures/coordinate_frame_map.png`.

## Pre-registered Decision Rule

Evaluated on the stratified audit (precision, recall) with the per-`schema_sig`
figures quoted where the two units disagree:

1. Recall ≥0.80 on every facet **and** coordinate system resolvable from SemCat
   alone **and** ≤10% of ground-truth tables missed → **H1 supported**.
2. Recall <0.50 **and** precision ≥0.80 → **H2 supported**. SemCat is a seed.
3. Recall <0.50 **and** precision <0.80 **and** `row_count` exact on ≥95% of
   verifiable tables **and** ≥1 relevant table surfaced that the accessible
   inventory lacks → **H3 supported**. SemCat is an inventory, not a classifier.
4. SemCat's candidate set ⊆ the name-regex set with no correct, name-unguessable
   label and no extra table → **H0 not rejected**.
5. Recall in [0.50, 0.80), or precision and recall pointing opposite ways, or
   facets disagreeing materially among themselves → **mixed evidence**, reported
   plainly as such, per-facet, with no single headline verdict. A facet-dependent
   answer is a legitimate result for a question about a heterogeneous catalog, and
   will not be collapsed into a grade to look decisive.

The Q1 census is reported regardless of which hypothesis wins — it is the
user's primary deliverable and does not depend on the verdict.

## Expected Outcomes

- **If H1 supported**: SemCat can be the front door for molecular data discovery
  in BERDL. Recommend building `content_type`-driven search into the BERIL skills
  so future projects skip hand-sweeping. Would also mean the exploration spot
  checks were unrepresentative — worth reporting as a caution against small-sample
  instrument judgments.
- **If H2 supported**: SemCat is a legitimate starting point but never a stopping
  point. Concrete recommendation: a two-stage discovery pattern (SemCat seed →
  name/type expansion → live confirm) codified in the `berdl-discover` skill.
- **If H3 supported** (the leaning outcome): the actionable split is to **use
  `tables` and ignore `concepts`**. SemCat is the best available answer to "what
  tables exist, how big, in which tenant" — including tenants a user cannot see,
  which is genuinely valuable and unobtainable elsewhere — and is unsafe for
  "what does this column mean". The highest-leverage fix is not better NLP but
  filling `content_type` where it is NULL (84%) and splitting the `coordinate`
  label into geographic / nucleotide / amino-acid / model. Both are concrete,
  cheap, high-value catalog improvements this project can hand back to SemCat's
  maintainers with a measured baseline attached.
- **If H0 not rejected**: SemCat's semantic layer is not yet earning its keep for
  molecular questions, and a documented regex would serve users better today.
  Report it plainly; it is a useful finding, not a hostile one.
- **Independent of the verdict**: the census stands as the deliverable, and the
  coordinate-frame map from notebook 4 is likely the most reusable artifact —
  several annotation tables are expected to have coordinates in frames that
  cannot be joined to each other (cluster-representative protein coordinates in
  `interproscan_domains` vs contig coordinates in `mgnify.gene`), which is
  exactly the trap a researcher attempting a BGC-neighborhood query would
  otherwise hit after writing the query.

## Revision History
- **v1** (2026-10-02): Initial plan
- **v2** (2026-10-06): Minor deviation, logged under execute-plan's Revision Loop; no
  re-approval sought. NB03 §2a was re-run after a first pass, changing two things the plan
  left unspecified: values sampled per audited column (12 -> 60) and the adjudication
  taxonomy (two-way correct/wrong -> four-way `correct` / `wrong_cardinality` /
  `wrong_label` / `sentinel_only`, the last excluded from the denominator). Measured strict
  precision moved 77.8% -> 83.9% and the verdict H3 -> H2.
  **Why this is not material:** no hypothesis was added or dropped; no decision threshold
  moved (precision 0.80, recall 0.50, row_count 0.95 all stand as written); the
  discrimination strategy is unchanged (still a 100+100 stratified, value-adjudicated
  audit); and what would refute H1 is unchanged — recall was 32% under both passes, so H1's
  refutation never depended on this. The plan required adjudication "by reading the column's
  actual values": a 12-value sample that returned only placeholders (`-`, `nan`, `None`) was
  not reading actual values, so the re-run increased compliance with the pre-registered
  method rather than departing from it.
  **Recorded against it:** the revision followed seeing a result, and it moved the verdict.
  The strict/lenient precision pair is a post-hoc analytic choice the plan did not
  anticipate; it is non-decisive here only because H2 holds under both figures (83.9% and
  91.9%). Had they straddled 0.80, the Decision Rule's clause 5 ("mixed evidence") would
  apply and the H2/H3 question would be reported unresolved. Both passes' numbers are kept
  visible in `SCOREBOARD.md` and `REPORT.md`.
- **v3** (2026-10-06): Compliance record, not a deviation. The plan's unit-of-analysis section
  commits to computing every rate twice — per column and per distinct `schema_sig` — so that
  cloned staging tables cannot inflate *n*. **The first execution of NB03 omitted this
  entirely.** The omission was not self-detected; `REVIEW_1.md` found a staging-database clone
  sitting in the audit sample as an independent observation. Now implemented in
  `03_semcat_grade.ipynb` §2b-bis: a `schema_sig` group scores as one observation, all-must-pass
  within the group (the conservative direction). Effect: the precision sample contained no
  clones (59 columns → 59 groups, figures unchanged); the recall sample collapsed 100 columns
  into 93 groups, moving recall from 30.0% per column to **32.3%** per `schema_sig`. Per the
  plan, the `schema_sig` figure is the one quoted; both are reported. The correction slightly
  favours SemCat and moves no verdict. Recorded here because the plan made a methodological
  commitment that the analysis initially failed to honour, and that gap is part of the project's
  record whether or not it changed an outcome.
- **v4** (2026-10-06): Scope note, no change to the pre-registered contract. The Q2 intervention
  is specified as "SemCat ... its `concepts`, `columns.content_type`, `tables.row_count`, and
  `verified_joins` layers" — 5 of the catalog's 25 tables. The executed analysis matches that
  specification exactly. Recording it explicitly because the resulting verdict is easily
  over-read: `column_embeddings` (vector search) and `edges` (15,490 rows) were never queried,
  and no `semcat` CLI exists on this host, so `semcat resolve` / `semcat joins` were not
  exercised. The measured 32.3% recall is therefore a property of **literal label lookup**, not
  of SemCat as a retrieval system. `REPORT.md` carries this as its own section rather than a
  limitation bullet.

## Authors
Mark Andrew Miller, Lawrence Berkeley National Laboratory, ORCID 0000-0001-9076-6066
