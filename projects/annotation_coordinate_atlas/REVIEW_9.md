---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-10-06
project: annotation_coordinate_atlas
---

# Review: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Summary

This is a ninth-round review of a project whose prior eight rounds found and closed a real (if
shrinking) defect each time, and whose eighth round explicitly concluded the reconciliation-style
checks had converged and recommended `submit`. I independently re-verified the core numbers again
from raw artifacts rather than trusting prose — recomputing the precision/recall tally directly
from `data/audit_precision.csv` (`correct=51, wrong_cardinality=4, wrong_label=4, sentinel_only=2,
vacuous=17, no_pattern=15, no_data=7` → strict `51/59=86.44%`, lenient `55/59=93.22%`), cross-checking
`data/nb03_summary.json` and `data/nb04_summary.json` against `REPORT.md`/`SCOREBOARD.md`, and
reconstructing the 18-row collocation breakdown row-by-row from `data/bgc_joinability.csv` (5
direct + 5 protein-only + 3 self-contained-variants + 1 cross-frame + 1 needs-parsing + 2 blocked +
1 no-coordinates = 18, of which 17 carry coordinates) — and every one of these reproduces
`REPORT.md`'s stated figures exactly. No new defect in the analysis content itself.

But this round does find one new, concrete, and ironic issue: **`claims.json`'s own integrity
check is currently broken.** `claims.json` records `report_hash:
sha256:f237c16905377953b5aef479ea0c7a0fd23d6331f724d41ec5a83d8f15917084`, the same hash
`REVIEW_8.md`'s footer recorded as verified. A fresh `sha256sum REPORT.md` right now returns
`a825fcebb0de1be45549f161923efde6a32d352d1ea0dbc07551a6530e8307a8` — a different file. Filesystem
timestamps explain why: `REPORT.md`'s mtime is `21:59:34`, twenty seconds *after* `REVIEW_8.md` was
written (`21:59:14`) and four minutes after `claims.json` was last built (`21:55:50`). `WORKLOG.md`'s
own entry confirms the cause — after `REVIEW_8` closed, its two open suggestions were acted on:
`REPORT.md`'s corrections section was extended from "Five corrections" to "Six corrections" (the
full text for Corrections 3–6 is now present, matching `SCOREBOARD.md`), and `beril.yaml`'s
`artifacts.review` was flipped `false → true`. Both edits are genuine improvements and I verified
the *substance* of `claims.json` — its six claims' locators, cell references (`cell-13`, `cell-9`,
`cell-3`, `cell-8`, `cell-7`/`cell-11`/`cell-9`, `cell-16`/`cell-19`), and `confidence_mismatch`
flags (true on 2 of 6: the `pfam_annotation_gff` coordinate claim and the `coordinate`-label
conflation claim) — all still match the current `REPORT.md` word-for-word, because the edit touched
only the Corrections section, not the Claims section. So nothing a reader would cite is actually
wrong. But the hash binding that is supposed to let a submitter *trust* that is now false, and this
is precisely the "cached value silently carrying stale state" failure class this project's own
`memories/pitfalls.md` and Corrections 3/5 document — recurring one layer up, at the
report↔claims-ledger binding rather than the notebook chain. The fix is mechanical: re-run the
claims build before `submit`.

## Methodology

Unchanged from all eight prior rounds, and still accurate: Q1 (the census) is correctly treated as
enumeration, not hypothesis; Q2 carries four falsifiable, pre-registered hypotheses with thresholds
fixed before the audit ran. `beril.yaml` records `plan_approval.via: agent-relayed` — disclosed
provenance for a reader weighing the pre-registration claim, not itself a fault, as in all eight
prior reviews. No `plan_deviations.jsonl` is present in the project directory. The one disclosed
plan revision (`RESEARCH_PLAN.md` Revision History v2, the 12→60 value re-sample and the
two-way→four-way adjudication taxonomy change) remains candidly argued as non-material and is
consistent with what `data/audit_precision.csv`'s seven-category tally actually shows — I rebuilt
that tally myself this round rather than re-reading the prior review's claim about it.

One small, separate process note: the README's `## Status` line already reads "Reviewed —
REVIEW_9.md drafted; awaiting `submit`" and this very file's placeholder was stamped before I wrote
it. That is scaffolding written by the review-invocation tooling at session start, not a claim made
by the project's author, and I am not treating it as a project defect — but a human reading the
README before this file exists would see a forward-reference to a document that does not yet say
anything. Worth noting only because it is the kind of premature-status pattern this project is
otherwise careful about.

## Code Quality

No new issues. The `src/` split (`semcat.py`, `census.py`, `validators.py`) is unchanged since
`REVIEW_6`/`REVIEW_8` last inspected it. `memories/pitfalls.md` now documents eight traps (four
SemCat-specific, two tooling/Python, two of the project's own reproducibility bugs), each with a
cheap detection command; the newest (`float('nan')` defeating an `is not None` guard) was checked
against `src/validators.py` by `REVIEW_8` and I have no reason to revisit that. `docs/pitfalls.md`
(the repository-level historical archive) raises nothing this project's own notes do not already
cover.

## Evaluation Integrity

This remains descriptive/instrument-evaluation work with no fitted model or tuned threshold, so
`EVALUATION_INTEGRITY.md` items 3–4 (train/test leakage, baseline selection) are correctly absent
from the write-up — forcing them in would misclassify the analysis type, as all eight prior rounds
also found.

- **Selection bias / scope (item 1) — still careful.** "Scope of the SemCat verdict" and "Scope of
  the Claim" state plainly that only 5 of SemCat's 25 tables and no CLI path were tested, that the
  grade covers readable tenants only, and that the census is a slice (now stated as 826 of the
  account's tables against SemCat's 2,509-table index). The Key Finding headings stay scoped in
  their own wording ("Only 5 of 17 coordinate-bearing region tables...", "SemCat is high-precision
  and low-recall (H2), on the subset tested") rather than generalizing to "SemCat" or "BERDL"
  unqualified — the exact failure mode item 6 warns about, and the one this checklist asks a
  reviewer to catch on the author's side. It is not present here, as in all eight prior rounds.
- **Metric-reporting integrity — independently re-derived, not re-read.** I rebuilt the
  precision/recall arithmetic from `data/audit_precision.csv` row-by-row myself this round (see
  Summary) rather than trusting `REVIEW_8`'s prior tally, and it reproduces `REPORT.md`'s
  86.4%/93.2%/32.3% to the decimal. This is the same check that caught the `56/59` error in
  `REVIEW_7`; this round it confirms no new instance.
- **The claims-ledger integrity check itself — the one new finding this round.** `claims.json`'s
  `report_hash` no longer matches the live `REPORT.md` (see Summary for the exact hashes and
  timeline). This is not a finding about the *claims* — I checked each claim's locators and
  `confidence_mismatch` flags against the current report text and all six still match exactly — it
  is a finding about the *mechanism* meant to prove that correspondence. A submitter who trusts the
  recorded hash without recomputing it would be trusting a check that is currently false.
- **Pseudo-replication:** both pre-registered corrections (per-`schema_sig` dedup for the SemCat
  audit; per-protein dedup for the domain-order statistic) remain implemented, and both are
  reconfirmed immaterial by the numbers I recomputed this round (30.0%→32.3% recall; 94.5%→94.4%
  domain order).

No biology-specific failure mode (items 5–10) applies beyond what prior rounds already assessed —
this is a catalog/instrument audit, and the one biological-plausibility check used (13.9 genes/BGC;
the ABC-transporter N/C-terminal architecture) continues to function as corroboration of a join,
not as a headline claim in itself.

## Findings Assessment

Conclusions are supported by the numbers in the cell outputs, independently reconfirmed this round
rather than assumed from the prior review's say-so (see Summary for the full recomputation).
Limitations remain unusually well acknowledged — recall stated as a probable lower bound, the
full-frame confusion matrix explicitly flagged as biased against SemCat, the audit's binomial CI
noted as straddling the 0.80 decision threshold, and the value-sample non-determinism quantified
with an observed run-to-run range. `### What Would Have Changed Our Mind` still gives concrete
pre-registered refutation routes for both the headline use-case finding and H1, both of which I
re-traced against `data/bgc_joinability.csv` and `nb04_summary.json` this round and found
accurately described. Nothing is left as "to be filled." Discoveries and Performance Notes each tie
to a specific notebook/figure/data file, as in all prior rounds.

## Suggestions

1. **(New, primary, mechanical — do before `submit`)** Re-run the claims build (`beril claims
   build` or equivalent) so `claims.json`'s `report_hash` matches the current `REPORT.md`
   (`a825fcebb0de1be45549f161923efde6a32d352d1ea0dbc07551a6530e8307a8`). The claim content itself
   does not need to change — I verified it still matches the report — but the recorded hash is
   currently a false signal of that correspondence, and `submit` should not inherit it uncorrected.
2. **(Not a project defect, a process observation)** Nine rounds in, the reconciliation-style checks
   (numeric cross-checks between report, notebooks, and data files) have twice now caught drift
   introduced by the review-and-fix cycle itself rather than by the original analysis: first the
   notebook-chain desync (Corrections 3/5), now the claims-ledger hash (this round). That is a
   useful signal in its own right — it suggests that whatever closes out a review round should
   itself re-run the claims build and the artifact-timestamp check from `memories/pitfalls.md`
   before considering the round closed, since "fix the report, rebuild the ledger" is currently two
   manual steps and only the first one reliably happens.
3. **(Carried over, now resolved — no action needed)** `REVIEW_3`/`REVIEW_7`/`REVIEW_8` flagged
   `beril.yaml`'s `artifacts.review` as `false` despite `REVIEW_N.md` files existing; it now reads
   `true`. `REVIEW_5`/`REVIEW_6`/`REVIEW_7`/`REVIEW_8` flagged the corrections section as stopping
   at five instead of six; `REPORT.md` and `SCOREBOARD.md` now both carry all six. Both are closed
   and do not need to be raised again.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-10-06
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, WORKLOG.md, SCOREBOARD.md, REVIEW_1.md–REVIEW_8.md, claims.json, beril.yaml, memories/pitfalls.md, repository docs/pitfalls.md, data/audit_precision.csv (full row-level recomputation), data/nb03_summary.json, data/nb04_summary.json, data/bgc_joinability.csv (full row-level reconstruction of the 18-table collocation breakdown), file mtimes/stat for REPORT.md, claims.json and REVIEW_8.md, independent sha256sum of REPORT.md cross-checked against claims.json's recorded report_hash and REVIEW_8.md's footer hash
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive assessment.

<!-- report_hash: sha256:a825fcebb0de1be45549f161923efde6a32d352d1ea0dbc07551a6530e8307a8 -->
