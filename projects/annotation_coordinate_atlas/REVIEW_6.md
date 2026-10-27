---
reviewer: BERIL Automated Review (Claude, claude-sonnet-5)
date: 2026-10-06
project: annotation_coordinate_atlas
---

# Review: Gene and Protein Function Annotations in BERDL, with Coordinates — and SemCat as the Instrument That Finds Them

## Summary

This is a sixth-round review of a project now five review cycles deep, each of which found and
closed a real (if progressively smaller) defect. I independently re-verified that all three
`REVIEW_5` findings are fixed and consistent everywhere they appear: `REPORT.md`'s Interpretation
section now reads "128" (matching Finding 4, `SCOREBOARD.md`, and `03_semcat_grade.ipynb` cell 24's
`fp=128`) instead of the stale "127"; it reads "119" (matching Finding 4 and `nb01_summary.json`)
instead of the stale pre-registration figure "122"; and Finding 2's gene-near-BGC statistic is now
a two-row table that names the ±5,000 bp flank explicitly and separates the flanked pair count
(754,313, 21.3/BGC) from the strictly-inside biological-plausibility check (489,978 genes, 13.9/BGC)
— a reader computing 754,313 / 35,354 no longer hits an unexplained mismatch. `claims.json`'s
`report_hash` (`d96ca6fe...`) matches a fresh `sha256sum` of `REPORT.md`, and every artifact the
four-notebook chain writes still clusters in the single 21:12–21:21 window on 2026-10-06, with
`REPORT.md`/`SCOREBOARD.md`/`WORKLOG.md`/`claims.json` all at 21:28 — consistent with a post-run
documentation pass and no partial re-run. Hunting past that record for a sixth time, I traced the
multi-domain order-and-spacing demonstration (`04_bgc_region_joinability.ipynb` cell 15, the 94%
PF00528→PF00005 figure) down to its row level and found one new, minor, previously-unflagged item:
the join that produces the 6,963 scored domain pairs is not deduplicated by protein, so a cluster
representative carrying more than one copy of either Pfam domain contributes more than one pair.
A check of the saved 300-row inspection sample (`data/example_multidomain_hits.csv`) found 20 excess
pairs from 16 of 280 distinct cluster IDs (one pair repeated four times); all 36 of those
duplicate-cluster rows happened to agree with the majority `PF00528->PF00005` order, so this does
not change the headline conclusion, but it is exactly the pseudo-replication class the project
otherwise treats carefully (the `schema_sig` dedup built for the SemCat audit exists for this
reason) and it is undisclosed here. Everything else checked this round — both figures re-rendered
and visually inspected, the NB01 coordinate sub-test cell outputs, the NB03 precision/recall and
`schema_sig` dedup cells, and the NB04 collocation and contig-overlap cells — reproduces the
report's numbers to the decimal. This is a well-run, thoroughly self-audited project; round six's
catch is a nice-to-have, not a defect that changes any verdict.

## Methodology

Unchanged from the prior five reviews' assessment. Q1 (the census) is correctly treated as
enumeration; Q2 (SemCat as discovery instrument) carries four competing, falsifiable,
pre-registered hypotheses with a non-circular NB01→NB02 ordering, independently checkable from the
frozen `semcat_candidates.csv` (written at 21:12, before `02_ground_truth_sweep.ipynb` ever runs).

`beril.yaml` records `plan_approval.via: agent-relayed` — recorded by the agent from an
in-conversation confirmation, not witnessed by the CLI at a terminal. As in all five prior reviews,
this is disclosed provenance for a reader weighing the pre-registration claim, not itself a fault.
No `plan_deviations.jsonl` is present. `RESEARCH_PLAN.md`'s Revision History carries one disclosed
v2 entry (the 12→60 value re-sample and two-way→multi-way adjudication taxonomy change), discussed
candidly in both the plan and `REPORT.md`'s "Five corrections" section, with an explicit argument
for why it is non-material (no threshold moved, H1's refutation never depended on it).

**Reproducibility, re-confirmed independently this round.**
```
sha256sum REPORT.md  → d96ca6fe0526c29136f5fda926f00d11ee3233517254e71e91509ee28f776bb2
claims.json report_hash → sha256:d96ca6fe0526c29136f5fda926f00d11ee3233517254e71e91509ee28f776bb2
```
Match. `ls -l --time-style=+%F_%H:%M notebooks/*.ipynb data/*.csv data/*.json figures/*.png` shows
all 28 chain artifacts timestamped 21:12–21:21 on 2026-10-06 in `01→02→03→04` order, with no
stragglers — the staleness-detector pattern from `memories/pitfalls.md` still passes cleanly.
`RESEARCH_PLAN.md` (19:52) and `beril.yaml` (19:57) predate the run, as expected for a frozen plan.
`requirements.txt` is present; the README's Reproduction section states the on-cluster prerequisite,
the `q.py` workaround for the known `run_sql.py` pitfall, runtime (~25 min), and the seeded audit
sample — all still accurate against what the notebooks actually do.

## Code Quality

The `src/` split (`semcat.py`, `census.py`, `validators.py`) continues to do real, load-bearing
work, and I re-traced `validators.py`'s adjudication categories against `figures/semcat_precision_recall.png`'s
right panel this round: correct 51, vacuous 17, wrong_cardinality 5, wrong_label 3, sentinel_only 2,
no_pattern 15, no_data 7 — sums to 100, and strict/lenient precision (51/59, 56/59) follow exactly
from excluding vacuous/sentinel_only/no_pattern/no_data (41 columns) from the denominator. This
matches `03_semcat_grade.ipynb` cell 17's printed `dedup_rate` output to the digit.

**New this round: an undeduplicated join in the multi-domain order demonstration.**
`04_bgc_region_joinability.ipynb` cell 15 computes domain order via
`FROM a JOIN b USING (gene_cluster_id)`, where `a` and `b` are each `SELECT gene_cluster_id, start,
stop FROM interproscan_domains WHERE analysis='Pfam' AND signature_acc = '<PF_A or PF_B>'` — i.e.
every row in `interproscan_domains` matching that signature, not one row per cluster. A cluster
representative with two instances of PF00528 (a repeated domain, which does occur in multi-domain
transporter proteins) produces two output pairs against each PF00005 instance. The cell's own
co-occurrence count one block earlier (cell 14) reports 6,530 *proteins* carrying both domains, but
the order join (cell 15) scores 6,963 *pairs* — a gap of 433 (6.6%) that can only come from repeat
domain instances within a cluster. I confirmed this directly in the saved sample:
`data/example_multidomain_hits.csv` (the unordered 300-row inspection sample cell 15 writes) has
280 distinct `gene_cluster_id` values across 300 rows, with `JAGZGF010000025.1_12` and
`NZ_QURC01000004.1_1568` each appearing 4 times and `CSLW01000253.1_4` (visible in the notebook's
own printed output) appearing twice with two different `b_start`/`b_stop` pairs against the same
`a_start`/`a_stop`. This is not an error in the SQL — it is a legitimate reading of "pairs of
domain instances" — but the report's prose ("PF00528 precedes PF00005 in 6,578 (94%)") reads as a
per-protein architecture statistic, and the pairs are not independent observations once a protein
contributes more than one.

## Evaluation Integrity

This remains descriptive/instrument-evaluation work with no fitted model, so train/test leakage and
baseline selection (`EVALUATION_INTEGRITY.md` items 3–4) are correctly not forced into the write-up.

- **Pseudo-replication in the multi-domain order statistic (item 5 analogue, same family as the
  `schema_sig` dedup the project already applies to the SemCat audit).** Per above: 6,963 scored
  pairs is not the same thing as 6,963 independent proteins, and the gap (433 pairs, 6.6%) traces to
  clusters with repeat domain instances. **Materiality check I ran**: in the 300-row sample, all 36
  rows belonging to a duplicated cluster carried the majority order (`PF00528->PF00005`), so
  deduplicating to one row per cluster would not flip, and likely would not meaningfully move, the
  94% headline — but this is an extrapolation from a 300-row sample of a 6,963-row population, not a
  full-population check, and the notebook does not report the distinct-cluster count for the full
  join the way it does for co-occurrence (6,530). The fix is cheap: dedup to one row per
  `gene_cluster_id` (e.g. nearest instance pair, or `MIN`/first by position) before computing the
  order split, or at minimum report `COUNT(DISTINCT gene_cluster_id)` alongside the 6,963 pair count
  so a reader can see the inflation factor the way they already can for `schema_sig` in the SemCat
  audit.
- **`schema_sig` dedup (item 5, as previously implemented):** re-verified unchanged —
  `recall_sig: 32.3%` (93 groups from 100 columns, 7 collapsed), `precision_sig` unchanged from
  per-column (0 clones in the 59-column judgeable precision sample). Matches `nb03_summary.json` and
  `SCOREBOARD.md`.
- **Selection bias / scope (item 1):** unchanged from prior rounds' correct assessment — "Scope of
  the SemCat verdict" and "Scope of the Claim" remain careful and are not generalized past the
  tested slice.
- **Effect size / small-sample caveats (item 11):** unchanged and still handled well — the binomial
  CI on 51/59 straddling 0.80 is flagged, and the `strand` facet's small n (17 genomic-strand columns
  total) is called out as too small to carry an estimate alone.
- No train/test leakage, baseline-selection, or biology-specific failure mode (items 6–10) applies
  here beyond the pseudo-replication point above — this is a catalog/instrument audit, not a
  cross-genome or cross-sample biological contrast, and the one place a biological check is invoked
  (13.9 genes/BGC as a plausibility check, the ABC-transporter N/C-terminal architecture as a second
  plausibility check) is used correctly, as corroboration rather than as the primary claim.

## Findings Assessment

All headline numbers I independently re-derived from `data/nb0{1,2,3,4}_summary.json` and from
re-executing the notebooks' own printed cell outputs agree with `REPORT.md`/`SCOREBOARD.md` to the
decimal: census 51 entries (24 coordinate-bearing: 15/5/4); collocation 5 direct / 5 protein-only /
2 blocked / 1 impossible out of 18 assessed, 17 coordinate-bearing; SemCat recall 32.3%/30.0%; strict
precision 86.4%, lenient 94.9%; row_count 59/60 = 98.3%; table coverage 80.3% (5 stale, 163 missing);
BGC contig overlap 100% (28,494/28,494); 754,313 gene–BGC pairs at 21.3/BGC flanked, 489,978 genes /
13.9 per BGC strictly inside; multi-domain ordering 6,578/6,963 ≈ 94%, gap median −392 [IQR −412,
−371]; coordinate sub-test 5 distinct systems, 22/78 (28%) unresolvable, 32/78 (41%) geographic;
concepts 1/119 molecular. The pseudo-replication item above is the only new thing this round, and it
does not change any hypothesis verdict (H1/H0 refuted, H2 supported) or the use-case demonstration's
qualitative conclusion (the architecture comes out right, which is the point of citing it). The
project's "What Would Have Changed Our Mind" and "Scope of the Claim" sections remain the strongest
parts of the write-up, and the "Five corrections" narrative plus `WORKLOG.md`'s dedicated entries for
`REVIEW_1`–`REVIEW_5` continue to document the self-correction loop candidly rather than smoothing it
over. (The corrections list is still numbered "Five" rather than folding in the `REVIEW_4`/`REVIEW_5`
fixes as a sixth and seventh entry — a narrative-completeness gap carried over from `REVIEW_5`'s
suggestion 4, still open, still a nice-to-have.)

## Suggestions

1. **(Nice-to-have)** In `04_bgc_region_joinability.ipynb` cell 15, dedup the domain-order join to
   one observation per `gene_cluster_id` before computing the 94% split, or report
   `COUNT(DISTINCT gene_cluster_id)` for the ordered join next to the 6,963 pair count (the way
   cell 14 already reports 6,530 distinct proteins for co-occurrence), so a reader can see how much
   of the 6,963 is repeat-domain inflation. Low priority: the sample check in this review suggests it
   does not change the verdict, but it is the one place in the report where this project's own
   dedup standard (applied rigorously to the SemCat audit) was not applied to a parallel situation.
2. **(Optional, carried over from `REVIEW_5`, still open)** Add the `REVIEW_4` and `REVIEW_5` fixes
   as sixth/seventh entries in `REPORT.md`'s "Five corrections" list, for consistency with how the
   first four review-driven fixes were each logged there.
3. **(Optional, carried over from `REVIEW_3`, still open)** `beril.yaml`'s `artifacts.review` is
   still `false` despite six `REVIEW_N.md` files now existing; confirm this is intentionally set by
   the `submit` skill rather than by review itself.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-sonnet-5)
- **Date**: 2026-10-06
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, WORKLOG.md, SCOREBOARD.md, REVIEW_1.md–REVIEW_5.md, claims.json, beril.yaml, runtime.json, requirements.txt, references.md, q.py, 4 notebooks (cell source and saved outputs inspected, cross-checked against `data/nb0{1,2,3,4}_summary.json`, `audit_precision.csv`, `audit_recall.csv`, `bgc_joinability.csv`, `annotation_sources.csv`, `example_multidomain_hits.csv`, and file mtimes), 3 `src/` modules, 25 data files, 2 figures (opened and visually inspected), project `memories/pitfalls.md`, repository `docs/pitfalls.md`, `euk_in_prok_correlates`/`pathway_based_hygiene` `memories/pitfalls.md` (no cross-project overlap found), `.claude/reviewer/EVALUATION_INTEGRITY.md`
- **Note**: This review was generated by an AI system. It should be treated as advisory input, not a definitive assessment.

<!-- report_hash: sha256:d96ca6fe0526c29136f5fda926f00d11ee3233517254e71e91509ee28f776bb2 -->
