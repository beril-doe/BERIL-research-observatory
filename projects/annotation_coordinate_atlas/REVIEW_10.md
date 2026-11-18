---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-10-06
project: annotation_coordinate_atlas
---

# Review: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Summary

This is a tenth-round review of a mature project that has already absorbed nine rounds of
independent scrutiny, each of which found and closed a real defect. I re-verified the project
from raw artifacts rather than trusting the prior reviews' say-so: recomputed `sha256sum
REPORT.md` and confirmed it matches `claims.json`'s recorded `report_hash`
(`16fb00ff63a0ab167280c60c3e200b8b1ccfb53e343fd09bcc73f3cd5687011b`) — the exact mismatch
`REVIEW_9.md` flagged as its one new finding has since been fixed (`WORKLOG.md`'s 2026-10-06
entry documents the rebuild, and `REPORT.md`/`claims.json` now share one mtime, 22:07:14);
checked every notebook/data/figure mtime across the four-notebook chain and confirmed all fall
within one 10-minute execution window (21:33–21:43), so Correction 3's "mixed snapshot" failure
mode is not recurring; cross-checked all four `data/nb0N_summary.json` files against
`REPORT.md`'s and `SCOREBOARD.md`'s headline numbers (precision 86.4%/93.2%, recall 32.3%/30.0%,
table agreement 80.3%, row-count accuracy 98.3%) and found exact agreement; and reconstructed
the 18-row `data/bgc_joinability.csv` collocation breakdown by hand (5 direct + 5 protein-space
only + 2 blocked + 1 impossible + 3 self-contained variants + 1 cross-frame + 1 needs-parsing =
18, of which 17 carry coordinates), which matches Key Finding 1's table exactly. I found **no new
substantive defect in the analysis content**. The one thing worth a sentence is a minor internal
inconsistency in `data/nb04_summary.json` (noted under Code Quality) that does not propagate into
anything `REPORT.md` or `SCOREBOARD.md` actually states. The project is sound, its hypotheses are
resolved with stable verdicts across five re-runs and two SemCat versions, and at this point the
main remaining question is not "is this correct" but "has review converged" — and on the evidence
available, it has.

## Methodology

Unchanged from all nine prior rounds and still accurate. Q1 (the census) is correctly treated as
enumeration rather than hypothesis; Q2 carries four falsifiable, pre-registered hypotheses
(H0–H3) with thresholds fixed before the stratified audit ran, and a decision rule that includes
an explicit "mixed evidence" exit (clause 5) rather than forcing a verdict. `beril.yaml` records
`plan_approval.via: agent-relayed` — disclosed provenance for a reader weighing the
pre-registration claim, not itself a fault. No `plan_deviations.jsonl` is present in the project
directory. `RESEARCH_PLAN.md`'s Revision History now runs to four entries (v1–v4); all are
disclosed, argued as non-material against the frozen thresholds, and consistent with the
artifacts I rebuilt independently this round.

One recurring process note, carried from `REVIEW_9.md` and still true: `README.md`'s `## Status`
line reads "Reviewed — REVIEW_9.md drafted; awaiting `submit`." That forward-reference is now one
round stale — this is REVIEW_10 — for the same reason REVIEW_9 noted about its own placeholder:
the status line is scaffolding stamped by the review-invocation tooling, not a claim made by the
project's author, so I am not treating it as a project defect. It is nonetheless the kind of
drift this project is otherwise unusually careful to catch (see Corrections 3/5 in `REPORT.md`),
and a human reading `README.md` right now would see a stale number.

## Code Quality

No new issues in `src/semcat.py`, `src/census.py`, or `src/validators.py` since `REVIEW_6`/
`REVIEW_8` last inspected them; I spot-checked that the `float('nan')` guard documented in
`memories/pitfalls.md`'s last entry is actually present in `src/validators.py` (it is — the
`f != f` NaN test appears there). `memories/pitfalls.md` documents eight traps with cheap
detection commands; nothing in this round's artifacts suggests a ninth.

**One minor, non-propagating inconsistency, worth a mention but not a fix-before-submit.**
`data/nb04_summary.json` records `"collocation_blocked": 3`, but the 18-row CSV it summarizes
(`data/bgc_joinability.csv`) has exactly 2 rows whose `collocation` field is the literal string
`blocked` (`refdata.smag.bgc`, `kbase.genomes.feature`) — the third unit evidently gets folded in
from the 1 row marked `impossible` (`refdata.microagrobiome.bgc_catalog`), under a coarser
3-bucket taxonomy (`direct`/`protein_only`/`blocked`) that the JSON uses internally and that sums
to 13, not 18 (the other 5 rows — 3 self-contained variants, 1 cross-frame, 1 needs-parsing —
aren't represented in any of the three JSON buckets at all). This matters only because
`REPORT.md`'s own Key Finding 1 table is more careful: it reports `blocked: 2` and
`no coordinates at all: 1` as separate rows, which is what the CSV actually shows, and never
quotes the JSON's `collocation_blocked` field directly. So no number a reader would cite is
wrong — but the summary JSON's taxonomy doesn't document itself, and a future reader regenerating
a dashboard from `nb04_summary.json` alone, rather than from `REPORT.md`'s prose, could report "3
blocked" and be off by one against the finer-grained CSV. Worth a one-line comment in the notebook
cell that emits this JSON, nothing more.

## Evaluation Integrity

This remains descriptive/instrument-evaluation work with no fitted model or tuned threshold, so
`EVALUATION_INTEGRITY.md` items 3–4 (train/test leakage, baseline selection) are correctly absent,
as all nine prior rounds also found.

- **Selection bias / scope (item 1) — still careful, re-verified this round.** "Scope of the
  SemCat verdict" and "Scope of the Claim" state plainly that only 5 of SemCat's 25 tables and no
  CLI path were tested, that the grade covers readable tenants only (826 of the account's tables
  against SemCat's 2,509-table index), and that the BGC demonstration is scoped to one biome
  (`soil`, because `gene_bgc`'s 35,354 rows are entirely soil — confirmed in
  `data/nb04_summary.json`: `bgcs_in_biome: 35354` equals `bgcs_with_genes: 35354`). The Key
  Finding *headings* stay scoped in their own wording ("Only 5 of 17 coordinate-bearing region
  tables...", "SemCat is high-precision and low-recall (H2), **on the subset tested**") rather
  than generalizing to "SemCat" or "BERDL" unqualified — the exact failure this checklist (item 6,
  the database-ascertainment-bias analogue) asks a reviewer to catch on the author's side. It is
  not present here.
- **Metric-reporting integrity — independently re-derived this round, not re-read.** I recomputed
  precision (`audit_correct`, `audit_wrong_cardinality`, `audit_wrong_label`,
  `audit_sentinel_only` from `data/nb03_summary.json`: 51+4+4+2=61 of which 59 are judgeable per
  the strict/lenient split) and recall (`audit_found`/`audit_recall_sample` = 30/93 schema_sig
  groups) directly from the summary JSON this round, and both reproduce `REPORT.md`'s 86.4% /
  93.2% / 32.3% exactly. This is the same reconciliation that caught the 56/59 vs 55/59 error in
  `REVIEW_7.md`; it finds no new instance here.
- **The claims-ledger integrity check — re-verified closed.** `REVIEW_9.md`'s one finding was that
  `claims.json`'s `report_hash` no longer matched a live `sha256sum REPORT.md`. I recomputed that
  hash independently this round: both files now read `16fb00ff…` and share an identical mtime
  (22:07:14), so the ledger-rebuild step `REVIEW_9.md` recommended was carried out and is
  confirmed current as of this review.
- **Pseudo-replication** — both pre-registered corrections (per-`schema_sig` dedup for the SemCat
  audit; per-protein dedup for the domain-order statistic) remain implemented and immaterial, as
  `data/nb03_summary.json` (`audited_recall` 0.3226 vs `audited_recall_per_column` 0.3) and
  `data/nb04_summary.json` (`multidomain_protein_b_then_a` 6167/6530 = 94.4% vs
  `multidomain_b_then_a` 6578/6963 = 94.5%) both confirm directly.

No biology-specific failure mode (items 5–10) applies beyond what prior rounds already assessed —
this is a catalog/instrument audit, not a comparative-genomics claim, and the one
biological-plausibility check used (13.9 genes/BGC; the ABC-transporter N/C-terminal
architecture) continues to function as corroboration of a join rather than as a headline claim on
its own.

## Findings Assessment

Conclusions are supported by the numbers in the cell outputs — independently reconfirmed this
round against the raw summary JSONs and the full `bgc_joinability.csv`, not assumed from a prior
review's tally. Limitations remain unusually well acknowledged: recall is stated as a probable
lower bound (because the regex-built ground truth itself missed a whole class of annotation
table, `kbase.content.c_<genome>_features`), the full-frame confusion matrix is explicitly flagged
as biased against SemCat and superseded by the value-adjudicated audit, the audit's binomial CI is
noted as straddling the 0.80 decision threshold, and the value-sample's run-to-run non-determinism
is quantified (lenient precision ranged 93.2%–94.9% across five full-chain re-runs) rather than
hidden. `### What Would Have Changed Our Mind` gives concrete, pre-registered refutation routes
for both the headline use-case finding (an empty contig-ID intersection, which did not occur:
28,494/28,494) and H1 (either coordinate-system resolvability or ≥0.80 recall; both failed), plus
a result that argues against the census being complete and a reader-facing acknowledgment that
the unbiased full-frame figures would support H3 if the audit's bias correction is rejected.
Nothing is left as "to be filled." `claims.json`'s two `confidence_mismatch` flags
(single-stream evidence on the `pfam_annotation_gff` coordinate-identity claim and the
`coordinate`-label-conflation claim) are both acknowledged explicitly in `REPORT.md`'s claims-
ledger note, correctly characterized as exact enumerations/arithmetic identities rather than
statistical estimates that happen to lack a second corroborating stream.

## Suggestions

1. **(Nice-to-have, not blocking)** Add a one-line comment in the `04_bgc_region_joinability.ipynb`
   cell that emits `collocation_blocked` in `nb04_summary.json`, documenting that this field folds
   the CSV's `blocked` and `impossible` verdicts together and does not account for all 18 rows.
   Nothing downstream currently cites this field directly, so this is cosmetic, but it would
   prevent a future reader from quoting "3 blocked" against the finer-grained and already-correct
   `bgc_joinability.csv`/`REPORT.md` figure of 2.
2. **(Process, cosmetic)** Update `README.md`'s `## Status` line, which still reads "awaiting
   `submit`" with a reference to `REVIEW_9.md`; it now trails this review by one round. Low
   priority since it is tooling-stamped scaffolding, not an author claim, but easy to fix in the
   same pass as submission.
3. **(Carried over, now resolved — no action needed)** `REVIEW_9.md`'s claims-ledger hash mismatch
   is fixed; `REVIEW_1.md`'s `schema_sig` dedup and chain-coherence findings remain closed;
   `REVIEW_7.md`'s lenient-precision figure remains corrected everywhere I checked
   (`REPORT.md`, `SCOREBOARD.md`, `claims.json`, `nb03_summary.json` all agree at 93.2%). None of
   these need to be raised again.
4. **(Unchanged from prior rounds, genuine but low-priority)** Future Direction 2 — re-running the
   SemCat grade against `column_embeddings`/`edges`/the `semcat resolve`/`semcat joins` CLI paths
   — remains the single most consequential open question about whether the H2 verdict generalizes
   beyond literal label lookup. This is appropriately scoped as future work rather than something
   this project's own grant or timeline required.

Given the volume of independent, convergent verification this project has now accumulated across
ten review rounds — with every prior finding closed and this round surfacing nothing beyond one
cosmetic data-file nit and one stale status line — I see no remaining obstacle to `submit` on
technical grounds.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-10-06
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, WORKLOG.md, SCOREBOARD.md, REVIEW_1.md–REVIEW_9.md, claims.json, beril.yaml, runtime.json, memories/pitfalls.md, repository docs/pitfalls.md, src/validators.py, src/semcat.py, src/census.py, requirements.txt, all four notebooks (cell sources and outputs), data/nb01_summary.json–nb04_summary.json (full field-level reconciliation), data/bgc_joinability.csv (full 18-row reconstruction), figures/ (existence and size check), independent `sha256sum REPORT.md` cross-checked against claims.json's recorded report_hash, full artifact-mtime sweep of notebooks/data/figures/REPORT.md/claims.json
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive assessment.

<!-- report_hash: sha256:16fb00ff63a0ab167280c60c3e200b8b1ccfb53e343fd09bcc73f3cd5687011b -->
