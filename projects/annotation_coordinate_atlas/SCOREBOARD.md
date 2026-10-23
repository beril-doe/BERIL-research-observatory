# Scoreboard — Gene and Protein Function Annotations in BERDL, with Coordinates
<!-- plan_hash: sha256:939a7492a268a47c8c514afb7b792b67248128a08a2336e750697af188f4c332 -->  **4 of 4 notebooks run**

**Snapshot:** all four notebooks executed in order on **2026-10-22**, in one run, against SemCat
catalog generated 2026-10-21T16:33:03Z (`code_version` 0.32.2, read through Spark) and the live
lakehouse of 2026-10-22. Rates are quoted **per distinct `schema_sig`**, as `RESEARCH_PLAN.md`
requires, with per-column figures alongside and 95% Wilson intervals.

| Hypothesis | Standing | Criterion | Observed (unit, n) | Where |
|---|---|---|---|---|
| H1 (SemCat sufficient) | refuted | recall ≥0.80 on every facet AND coordinate system resolvable from SemCat fields alone | the `coordinate` label covers 4 systems, 20/78 columns resolve to none; recall 30/95 = 31.6% (schema_sig; 30/100 per column) | `01_semcat_discovery.ipynb` §1; `03_semcat_grade.ipynb` §2b |
| H2 (high precision, low recall) | supported by the point-estimate rule, at the margin | recall <0.50 AND precision ≥0.80 | recall 31.6% ✓; strict precision 45/56 = 80.4% (0.68–0.89) ✓ on the point estimate; lenient 49/56 = 87.5% (0.76–0.94) ✓. The strict interval includes values below 0.80. | `03_semcat_grade.ipynb` §2a, §2b-bis, §2c |
| H3 (structural not semantic) | not supported on the point estimate, not excluded at 95% | recall <0.50 AND precision <0.80 AND row_count ≥95% AND ≥1 table beyond own inventory | precision 80.4% ✗ (needed <0.80) on the point estimate. Other clauses hold: row_count exact 59/60 = 98.3% ✓ (table, n=60); 483 candidate tables in tenants outside the account's listing ✓ | `03_semcat_grade.ipynb` §2c; `02_ground_truth_sweep.ipynb` §6a |
| H0 (no value over name regex) | refuted | rejected if SemCat yields ≥1 true positive a name regex misses | 2 census tables flagged only by a SemCat-specific label (`kofam_annotation_table`, `metatranscriptomics_gold`) | `03_semcat_grade.ipynb` §3 |

## Use-case feasibility (NB04, a direct test of the deliverable)

| Claim | Standing | Observed |
|---|---|---|
| BGC regions and genes share a contig namespace | supported | 28,494/28,494 `gene_bgc` contigs match a `gene` contig (soil biome); 13.9 genes strictly inside per BGC; 754,313 gene–BGC pairs at ±5 kb (21.3 per BGC) |
| Multi-domain *order* search is possible | supported | PF00528 precedes PF00005 in 6,167/6,530 proteins = 94.4% (one protein, one vote; pair level 6,578/6,963 = 94.5%); gap IQR −412 to −371 aa |
| Collocation is possible wherever coordinates exist | **refuted for region tables** | of 23 coordinate-bearing tables, 13 are joinable to genes by position: 4 of 14 region tables (all MGnify, direct), 9 of 9 gene tables (8 self, 1 bridged). 9 region tables are protein-space only (rule-based verdict), 1 has no gene table in its database |

## Facet dependence

Strict precision by label family (per column): `function_id` 27/36 = 75% (0.59–0.86),
`seqref` 15/16 = 94%, `span` 4/5 = 80%, `strand` 1/1. Recall by facet (per column):
`function_id` 11/43, `span` 17/43, `strand` 2/14. Strand recall is 2/14 in the audited frame
(tables both live and indexed) and 2/18 across all 840 readable tables (NB02 §3). Both counts
are too small for a stable rate.

**A cross-check that must not be over-read.** The full-frame, rule-based confusion matrix
(`data/semcat_confusion_by_facet.csv`) gives function_id precision 0.53, span 0.44, strand 0.50,
because it treats this project's own name regex as truth and so charges SemCat a false positive
for every correct label on a column the regex missed. The value-adjudicated audit is the
pre-registered test and supersedes it.

## Corrections (history)

1. Precision adjudication moved from a 12-value correct/wrong scoring to 60 values and a
   four-way verdict; the verdict moved H3 → H2 (`RESEARCH_PLAN.md` Revision History v2).
2. Inter-domain gap: a tail median (−680.5 aa) replaced by the full-join median (−392 aa).
3. Mixed snapshots from re-running one notebook alone (found by `REVIEW_1.md`); all four now
   run in order.
4. Pre-registered `schema_sig` deduplication implemented (found by `REVIEW_1.md`).
5. Row counts read from a stale cached file (found by `REVIEW_2.md`); now computed live.
6. Wrong lenient-precision figure from a non-deterministic value sample (found by `REVIEW_7.md`).
7. Deterministic value sampling (`DISTINCT` + `ORDER BY xxhash64`) fixed the cause of 6.
8. `kbase.genomes.feature` reclassified from unplaceable to bridged after a reader pointed to
   `contig_x_feature`.
9. 2026-10-22 revision:
   - Joinability is now derived from queries for all 23 coordinate-bearing tables.
   - `metatranscriptomics_gold` is no longer coordinate-bearing (it has no span).
   - Copilot's three validator and classifier fixes are applied.
   - SemCat's verified joins are read from `edges`, not from the composite-key
     `verified_joins`.
   - The full chain was rerun against SemCat's 2026-10-21 catalog. Strict precision moved
     from 85.0% to 80.4%, at the threshold.
