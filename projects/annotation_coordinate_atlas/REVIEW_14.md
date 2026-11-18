---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-10-16
project: annotation_coordinate_atlas
---

# Review: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Summary

This is the fourteenth review of this project, and the work since `REVIEW_13.md` (2026-10-09)
is modest and, on inspection, sound: the two low-priority documentation nits `REVIEW_13.md`
raised (the "ten"/"eleven" review-count self-contradiction and the stale `memories/pitfalls.md`
description in `README.md`) were fixed exactly as recommended, and a follow-up session added two
new evidence-stream cells to `02_ground_truth_sweep.ipynb` that execute, for the first time, a
value check that had previously only been described in prose (the `pfam_annotation_gff`
amino-acid-coordinate identity) and a cross-check of NB01's SemCat-metadata coordinate typing
against this project's own census. Both are genuine, disclosed, live computations — not restated
numbers — and both are correctly reflected in `claims.json`, which now shows the conflation claim
promoted to `multiple-streams` and overall `confidence_mismatch` reduced from 2 to 1 (the
remaining one, the `pfam_annotation_gff` claim, is correctly self-flagged as single-stream by
nature, as `REPORT.md`'s "note on the claims ledger" explains). I independently recomputed
`sha256sum REPORT.md` and it matches `claims.json`'s `report_hash` exactly, and I spot-checked 9
of the ledger's 12 evidence citations directly against the one-based notebook cells they point to
(across all four notebooks) — every one I checked reproduces the exact quoted string. I also ran
the project's own prescribed staleness check (file mtimes across the chain) and found a real,
but ultimately benign, anomaly: `02_ground_truth_sweep.ipynb` and two new data files it writes
carry a 2026-10-16 timestamp while the other three notebooks and all other artifacts are frozen
at 2026-10-09. Tracing this down, it matches the `WORKLOG.md` account exactly — two cells were
appended to the end of NB02 and run in a fresh kernel, not a full chain re-run — and the inputs
those cells depend on (`CENSUS`, a curated static artifact, and `row_counts_verified.json`, a
frozen file from the 2026-10-09 run) are pinned rather than live, so no desynchronization of the
kind Corrections 3/5 describe actually occurred. The one new, independently-found issue is a
small documentation gap: the "Generated Data" table in `REPORT.md` still does not list either of
the two new output files, nor a pre-existing one (`data/ground_truth_table_facets.csv`) that has
apparently never appeared there across all 14 review rounds. None of this touches a hypothesis,
a figure, or a conclusion.

## Methodology

Unchanged in substance from `REVIEW_13.md`'s assessment and still sound: Q1 (the census) is
reported as enumeration independent of the Q2 verdict, per the plan; Q2's four hypotheses carry
pre-registered thresholds with an explicit "mixed evidence" exit, and the decision rule is
applied without having been bent to fit the data. `beril.yaml`'s `plan_approval.via:
agent-relayed` — the approval was a conversational grant the agent recorded, not one a human
typed at a terminal; this is disclosed provenance, not a fault. No `plan_deviations.jsonl` is
present in the project directory.

I verified the two new NB02 cells are genuine additions, not restatements: cell 29 (one-based
30) issues a fresh, seeded (`fraction=1e-5, seed=42`) Bernoulli sample directly against
`nmdc.results.pfam_annotation_gff` via `spark.table(...).sample(...)` — a live query, not a
cached read — and finds `N tested: 26,779; mismatches: 0`. Cell 31 (one-based 32) merges NB01's
`data/semcat_coordinate_typing.csv` against the census `cen` DataFrame and finds 36 overlapping
columns with 0 contradictions, writing `data/semcat_coordinate_crosscheck.csv`. Both match the
corresponding `claims.json` entries verbatim.

`WORKLOG.md`'s account of this session states the two cells "ran in a fresh kernel with only
NB02's setup cell before them." That is slightly imprecise: cell 31's merge requires `cen`
(the census DataFrame), which is built at cell 14 from `pd.DataFrame(CENSUS)` — so cell 14 must
also have executed in that session, not just the setup cell. This is harmless in practice
because both of cell 14's inputs (`CENSUS`, a hand-curated Python structure in `src/census.py`,
and `data/row_counts_verified.json`, frozen since the 2026-10-09 full-chain run) are static
artifacts rather than live queries — re-running cell 14 at any later date reproduces the same
`cen` — but it is a small factual imprecision in a project whose own history (Correction 8) makes
a point of catching exactly this kind of self-description slip.

## Code Quality

No new issues in `src/semcat.py`, `src/census.py`, or `src/validators.py`. The two new NB02
cells are well-commented (cell 29 explains why a `sample()` is used instead of `LIMIT`, to avoid
reading only the first files) and follow the project's established conventions (seeded sampling,
NULL-exclusion counted separately, writing the artifact path in the printed output).

**New, independently found — the Generated Data table is incomplete.** `REPORT.md`'s "Generated
Data" table (Supporting Evidence section) lists 15 files but omits three that exist in `data/`
and are legitimately part of the record:
- `data/semcat_coordinate_crosscheck.csv` — backs the `live-census-crosscheck` evidence stream
  cited in `claims.json` for the conflation claim (cell-32). This is the file created in the very
  session that raised the ledger's `multiple-streams` count, so its absence from the table is a
  fresh gap, not a carried-over one.
- `data/pfam_coordinate_check.json` — is named in `REPORT.md`'s claims-ledger note (line 239)
  but not in the Generated Data table itself.
- `data/ground_truth_table_facets.csv` — produced by NB02 (`tf.to_csv(...)`, confirmed by grep)
  but never mentioned anywhere in `REPORT.md`'s prose or tables; this one predates the current
  session and appears to have been missed by all 13 prior reviews as well.

None of these affects a reported figure — all three are legitimately present on disk and their
contents (where cited) check out — but a reader using the Generated Data table as a manifest of
`data/` would not find three of the files that are actually there.

## Evaluation Integrity

Still descriptive/instrument-evaluation work with no fitted model or tuned threshold, so
train/test leakage and baseline selection (`EVALUATION_INTEGRITY.md` items 3–4) correctly don't
apply, as every prior round also found. The two new cells don't change this: one is an exact
arithmetic identity check on sampled rows (not an estimate that could leak), the other is a
label-agreement cross-check between two already-computed, non-overlapping-construction artifacts
(NB01's SemCat-only typing, frozen before ground truth existed, vs. NB02's independent census).

- **Selection bias / scope (item 6, database-ascertainment analogue)** — unchanged and still
  careful. `### Scope of the Claim` and `### Scope of the SemCat verdict` state the realized
  cohort precisely, and Key Finding headings stay scoped ("Only 6 of 17...", "on the subset
  tested") rather than generalizing to unqualified "BERDL" or "SemCat."
- **Metric-reporting integrity** — `claims.json`'s six claims now resolve to `multiple-streams`
  (5) or correctly self-flagged `single-stream` (1, explained in `REPORT.md` as an exact
  arithmetic identity rather than an under-evidenced estimate, consistent with the update
  described above). No `unresolved` or `invalid` evidence entries; the one `not-checked` entry
  (the scope-note "refutes" pointer) is a documentation cross-reference, not a computed
  artifact, and is correctly marked as such.
- **Report/ledger hash integrity** — independently recomputed this round; `REPORT.md`'s
  `sha256sum` matches `claims.json`'s `report_hash` exactly.
- **Citation integrity** — spot-checked 9 of 12 evidence locators directly against notebook
  cells (both newly-added and pre-existing ones, across all four notebooks); all matched the
  quoted strings exactly, consistent with `WORKLOG.md`'s account of a full one-based citation
  repoint that achieved 12/12.

No biology-specific failure mode (`EVALUATION_INTEGRITY.md` items 5, 7–11) applies — this
remains a catalog/instrument audit, not a comparative-genomics claim, and the project makes that
distinction correctly throughout.

## Findings Assessment

Conclusions remain supported by the numbers in the cell outputs. The two new evidence streams
strengthen, rather than alter, existing claims: the pfam identity check now has a reproducible,
seeded execution behind it (previously only described as having been run once, interactively,
unsaved), and the coordinate-conflation claim gained a second, independent evidence stream that
agrees with the first (0 contradictions across 36 overlapping columns). No hypothesis verdict,
headline figure, or Key Finding changed. `### What Would Have Changed Our Mind` and the
Limitations section remain unusually thorough and are unaffected by this session's additions.
Nothing is left as "to be filled." No `Discoveries`/`Performance Notes` entry appears
unsupported or overgeneralized on inspection.

## Suggestions

1. **(Low priority, documentation)** Add `data/semcat_coordinate_crosscheck.csv` and
   `data/pfam_coordinate_check.json` to `REPORT.md`'s Generated Data table — both now back cited
   claims and are otherwise absent from the one table meant to enumerate `data/`'s contents.
   While fixing this, also add the pre-existing `data/ground_truth_table_facets.csv`, which has
   apparently never appeared there.
2. **(Trivial, self-description precision)** `WORKLOG.md`'s 2026-10-16 entry describing the new
   NB02 cells as having run "in a fresh kernel with only NB02's setup cell before them" should
   note that cell 14 (which builds `cen` from the curated `CENSUS` artifact) also ran — harmless
   given `cen`'s inputs are pinned, but worth getting right given this project's own demonstrated
   sensitivity to exactly this class of self-reported-process error (Correction 8).
3. **(Unchanged, genuine, low priority)** Future Direction 2 — grading SemCat's
   `column_embeddings`/`edges`/CLI retrieval paths rather than literal `content_type` lookup —
   remains the single most consequential open question about whether the H2 verdict
   generalizes. Correctly scoped as future work, not a gap in the current report.
4. **(Carried over, confirmed closed)** Both low-priority items from `REVIEW_13.md` (the
   "ten"/"eleven"/"twelve" review-count correction and the stale `README.md` pitfalls-count
   description) are fixed exactly as recommended, consistently across `REPORT.md`,
   `SCOREBOARD.md`, `WORKLOG.md`, and `README.md`.

Fourteen review rounds in, the only outstanding items are documentation completeness nits that
touch no hypothesis, figure, or conclusion. On technical grounds I see no remaining obstacle to
`submit`.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-10-16
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, WORKLOG.md, SCOREBOARD.md, claims.json,
  beril.yaml, runtime.json, memories/pitfalls.md, docs/pitfalls.md, requirements.txt, all four
  notebooks (direct inspection of the two newly-added cells in `02_ground_truth_sweep.ipynb` and
  spot-checks of 9 of 12 claims.json evidence citations against one-based cell contents across
  all four notebooks), data/ artifacts (existence and cross-reference check against REPORT.md's
  Generated Data table), figures/ (existence check, unchanged since 2026-10-09), an independently
  recomputed `sha256sum REPORT.md` cross-checked against claims.json's recorded report_hash, and
  a file-mtime staleness check per the project's own documented detection command (which
  surfaced and resolved the NB02-only timestamp anomaly discussed above). REVIEW_1.md through
  REVIEW_13.md were read for prior-finding context but their conclusions were independently
  re-verified against the current artifacts rather than taken on trust.
- **Note**: This review was generated by an AI system. It should be treated as advisory input,
  not a definitive assessment.

<!-- report_hash: sha256:7e7088ed4aab0157a16729e85881ca2185013228c8412534aa59cce2376f4f0e -->
