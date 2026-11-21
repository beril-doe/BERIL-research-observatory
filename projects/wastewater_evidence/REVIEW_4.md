---
reviewer: BERIL Automated Review (Claude, claude-opus-5)
date: 2026-10-23
project: wastewater_evidence
---

# Review: Wastewater Evidence Across Sample-Metadata Systems

## Summary

This is a careful, unusually well-traced report, and the v2.4 edits are the best
round so far. I re-derived every table and nearly every inline count against the
run outputs. All 123 recorded output files still match their `run.json` hashes,
every run the report cites exited 0, and no cited number comes from either
superseded run. The four figures in `figures/` are byte-identical to the outputs
of the run the report credits. Both v2.4 attribution corrections (priority 1) are
correct, Finding 7's four-row class table reproduces exactly and its
classification code re-derives cleanly (priority 2), and Finding 8's 1,283-record
claim and 32.4% support rate are right (priority 3).

Two substantive problems remain, and one of them follows the pattern of the
previous rounds: a fix introduced a new error. First, the new study-overlap
residual of **31 and 1 is wrong for the figures it qualifies** — the term tables
were never re-mined, so the 589 doubly-labelled accessions still sit on the
*training* side, and the residual that applies is 251 and 246, derivable by
subtraction from this project's own run output. Second,
`fig_transfer_screen.png` is still titled "screening removes the ones inherited
from disputed source groups", which is precisely the claim v2.4 retracted. Beyond
those, Finding 7's heading, body, restatement and the What-Would-Have-Changed-
Our-Mind bullet do not all speak at the same strength, and the class table's row
3 does not reconcile with Finding 8's "51,610 are dropped".

## Methodology

The research question is clearly stated and is genuinely testable at the level it
operates: which fields and values assert wastewater, not which samples are
wastewater. The report is disciplined about that distinction, and the Scope
section is the strongest part of the document.

**Pre-registration status is correctly represented.** There is no
`RESEARCH_PLAN.md`, no `plan_approval` in `beril.yaml`, and no
`plan_deviations.jsonl`. The report says so at the top and tags every one of the
ten findings `basis: exploratory`. Nothing is presented as confirmatory. This is
correct and needs no change.

**Priority 4 — the study-overlap residual is understated.** The v2.4 query does
exclude what it says it excludes. `src/10_v24_checks.py:76-93` builds `gold_proj`
and `mg_proj` from accessions `NOT IN (SELECT accession FROM dual)` and also
excludes duals from the counted side, so "31 MGnify accessions and 1 GOLD
accession still share a BioProject with an accession labelled solely by the other
source" is literally true. The direction-of-effect statement is also right: a leak
can only inflate recovery, so the reported rates are upper bounds.

The problem is that this is not the residual that applies to the numbers it is
attached to. `src/07_review_checks.py:95` filters only the *test* set:

```python
te_cl = te_all[~te_all.accession.isin(both_gm)]
```

The term tables it applies, `terms_g` and `terms_m`, are read unchanged from
`04_transfer_validate.py`, which built them from *all* GOLD-labelled and *all*
MGnify-labelled accessions — the 589 duals included. Each dual therefore still
contributes vocabulary to the other direction's table. A non-dual test accession
that shares a BioProject with a dual is leaked just as surely as one sharing with
a single-source accession, and the v2.4 query does not count it.

The correct residual is already in the run output, by subtraction. All 589 duals
have a BioProject link, so:

| Quantity | Value |
|---|---:|
| MGnify accessions sharing a project with any GOLD-labelled accession | 840 |
| of which doubly labelled | 589 |
| **non-dual MGnify test accessions still leaked** | **251** |
| GOLD accessions sharing a project with any MGnify-labelled accession | 835 |
| **non-dual GOLD test accessions still leaked** | **246** |

So the sentence "Excluding the 589 doubly-labelled accessions removes nearly all
of it" is wrong — the exclusion was test-side only, and it removed the duals'
self-recovery, not their training contribution. The headline conclusion survives
unharmed, because the leak inflates and observed no-native recovery is already
1.2% and 0.5%. But the stated residual is off by roughly an order of magnitude,
and 840/835 was not simply an upper bound replaced by a true value: it was one
wrong number replaced by another.

Note that **31 and 1 would be correct** under a design where the term tables are
re-mined with the 589 excluded. The cheapest honest fix is to say which design
was run.

**The MGnify cohort is slightly less complete than stated.** The fetch log shows
two lineages returning fewer samples than the API advertised: `Water and sludge`
859 against 958 expected, and `Biological phosphorus removal:Activated sludge` 8
against 17. The report says "all 4,352 MGnify wastewater-biome samples". About
108 advertised samples were not collected, and nothing says so.

**Reproducibility is otherwise excellent.** Every cited run has a `run.json` with
exit code 0 and a script hash that still matches the file on disk. The ten
script-hash mismatches I found are all on superseded or failed runs whose scripts
were later edited, which is expected. `requirements.txt` is present, the README
carries a real Reproduction section naming the cluster Python and the Spark
dependency, and `memories/pitfalls.md` records three real traps including the
`\b`-in-`RLIKE` bug that invalidated the two superseded runs. There are no
notebooks, so the notebook-output check does not apply.

**README gaps.** `src/10_v24_checks.py` is absent from the Reproduction block,
although v2.3 added the then-three verification scripts and the report cites the
v2.4 run in both Finding 7 and Finding 8. `REVIEW_3.md` is missing from Quick
Links. The Worklog link is duplicated on consecutive lines.

## Code Quality

The SQL is correct where I could check it, and the shared-regex module is the
right structure. `sql_re` doubling backslashes before embedding in `RLIKE` is the
fix for a bug that silently nulled an earlier run, and it is applied
consistently. `TAX_STRICT_RE` is anchored (`^...$`) over exactly 8 metagenome
taxa, matching the Recommended scheme's claim. The mining thresholds in
`04_transfer_validate.py:51-53` are `MIN_COUNT = 3`, `MIN_LIFT = 50.0`,
`MIN_PURITY = 0.70`, exactly as Finding 7 describes.

**Priority 2 — the classification logic is sound and the table is right.** I
re-derived `src/10_v24_checks.py:144-171` independently in pandas and reproduced
the term assignment exactly: 29 class-1 terms, 112 class-2, 101 class-3, with no
NaN in either the dominant-source or the verdict merge. The record counts match
`v24_gain_class_totals.csv` exactly, and the four rows sum to 83,955 as claimed
(35,288 + 16,668 + 31,789 + 210).

Two things about the class definitions should be stated rather than left implied.

**The partition is hierarchical, and row 3's label is not what row 3 contains.**
Class 1 pre-empts the verdict split, so 8 accepted class-1 terms covering 411
records are kept by the screen but counted under class 1. Combined with part of
the 210 multi-class row, this is why class 3 reads 31,789 while Finding 8's
"51,610 are dropped" implies 32,345 survivors (83,955 − 51,610). Both numbers are
correct; nothing reconciles them, and a reader who subtracts will think one of
them is wrong.

**"Disputed" was applied to MGnify-dominant terms only, and Finding 6 disputes
more than that.** The class-1 test requires `dominant_source == "MGnify"`. Thirty-
two terms carry `ext_subtype = industrial_ww` but are GOLD-dominant — `mine
tailing pool`, `animal house`, `conventional feedlot`, `abattoir waste`,
`organic dairy farm` and others — and they fall into classes 2 and 3. Finding 6
says GOLD's `industrial_ww` group is only 52% supported, so GOLD's industrial
group is in dispute too. The narrower boundary is a defensible choice; it is not
a stated one.

**Class 1 is not uniformly idiom.** Of its 29 terms, 8 are accepted, including
`acid mine drainage`, `anaerobic reactor` and `small river`. Describing the whole
35,288-record class as "Idiom from the disputed MGnify groups" over-claims for
that fraction. The "rejects almost all" column captures the screen's behaviour
but not the characterisation.

## Evaluation Integrity

Most of this project is descriptive SQL over metadata, and no classifier is
trained, so there is no train/test leakage hunt to run across most of it. Two
objects are fitted and both deserve scrutiny.

**The term table is the fitted object, and its hold-out does leak.** This is the
priority-4 finding above, and it is an evaluation-integrity issue rather than a
bookkeeping one: the design that produced 50.0%, 14.4%, 1.2% and 0.5% keeps the
589 doubly-labelled accessions in the training vocabulary while removing them
from the test set, and the reported residual does not measure that. The check
that settles it is to re-run `build_terms` on source-exclusive cohorts and
recompute; the check that bounds it without re-running is the 840 − 589 = 251 and
835 − 589 = 246 subtraction above.

**The screen's circularity is disclosed and quantified correctly.** I verified
`chk_screen_basis.csv` row by row: 81 accepted terms clear on package support
(54 + 11 + 5 + 5 + 3 + 2 + 1), 26 on ENVO alone (21 from `env_*` fields covering
2,588 records, 5 others), and 2 on BioProject co-membership alone covering 592
records, totalling 109. `chk_screen_envo_dropped.csv` confirms the counterfactual
drops exactly 21 accepts. Finding 8 reports all of this accurately and does not
claim more independence than it has.

**One near-tautology is not flagged.** Finding 4 reports that `taxonomy_name` is
"almost never the sole evidence (12 of 369,048 hits stand alone)". But the
crosstab's taxonomy channel is a regex over `taxonomy_name` itself, and
`keyword_by_field.csv` shows 368,903 of those 369,048 keyword hits also fire the
taxon channel. The two channels read the same string, so the result is mechanical,
not a measure of the field's informativeness. Finding 1 makes exactly this
independence caveat for ENVO and keyword. It should extend to this row.

**Thresholds are acknowledged as arbitrary.** The 10% support cut is stated as
untuned and the accept/reject counts are said to move with it. The 3/50/0.70
mining filters are reported in the text and verified in code. No baseline
selection or metric substitution problems found.

**Ascertainment is handled better than in most reports I review.** The Scope
section gives the realized cohort as 9,390 accessions, about 0.018% of BioSample,
says the cohort is study-clustered, names the dominating BioProjects on both
sides, and states plainly that nothing here observes the physical matrix. Finding
2's warning that the package channel is 67% one COVID-era surveillance package is
the same discipline applied to the strongest channel.

## Findings Assessment

Everything below was checked against the run outputs, not the prose.

**Priority 1 — both v2.4 corrections are right.** `biofilter metagenome` appears
in `term_table_mgnify_only.csv` with `built_from = MGnify` and `ext_subtype =
nutrient_removal_bioreactor`, which is not a disputed group, and `term_screen.csv`
gives it support 0.009668 with verdict `reject`. That is 0.97%, exactly as
reported. `env_local_scale = anaerobic` is likewise MGnify-only and
nutrient-removal, accepted at 0.32432, matching 2,886 BioSample records, and
`v24_gallus_carrier.csv` shows it is the single accepted term carrying all 1,283
*Gallus gallus* no-native records. The contrast term `bioreactor metagenome` is
GOLD-only from `bioreactor_anaerobic_sludge`, accepted at 10.6%, with 25,859
no-native records in `applied_new_examples.csv`. Every one of these checks out.

The "chicken-gut" characterisation is supported, though indirectly: the same
screen-survivor file lists `env_medium = cecal content` at exactly 1,283. That is
a co-occurring count rather than a join, and one clause could say so.

**Priority 3 — Finding 8 draws the right conclusion.** The term has real support
in its home domain and over-matches badly outside it, and that is genuinely what
corroborating support cannot detect, because the measure is computed over the
term's own carriers without reference to where the term came from. The finding is
well reasoned and the counterexample is the right one to lead with.

**Priority 5 — heading, body, restatement and the mind-changing bullet do not
agree in strength.** Four separate mismatches:

1. *Heading versus body on the mechanism.* The heading's second clause says
   "unscreened, it generalises study idiom at scale", locating the problem in the
   unscreened state. The body's own emphasis is the opposite: "Class 3 is the one
   that matters, because the screen does not remove it". Class 3 is 31,789
   records, larger than class 2, and survives screening. The heading also calls
   the content study idiom, where the body attributes class 3 to this project's
   decision to include a GOLD bioreactor group.
2. *Body versus restatement on the MGnify direction.* The body says "The
   MGnify-direction result is therefore ambiguous, and only the GOLD direction
   (n=381) supports the headline." The restatement then offers "2 of 381 GOLD
   records and 9 of 722 MGnify ones" as jointly showing the residual is
   essentially zero, quietly recruiting the direction it just set aside.
3. *Body versus the What Would Have Changed Our Mind bullet.* That bullet reports
   "1.2% and 0.5%" symmetrically as refutation, with no trace of the MGnify
   ambiguity and no mention that the figures are upper bounds. A limitation
   stated in the body is dropped in the section most likely to be quoted.
4. *The restatement mislabels the keyword baseline.* It says the mined table
   "reaches roughly the records a generic keyword regex over 14 fields already
   reaches". The 83,955 and 148,289 results come from a **10-field** concat in
   `src/04_transfer_validate.py:187` and `src/04b_term_screen.py:83`. The 14-field
   definition belongs only to the hold-out columns, through
   `labelled_samples.parquet`. The report's own Finding 1 and Limitations flag the
   15/14/10 split, so this is a slip — but it attaches the stricter baseline to
   the weaker computation, which overstates what the keyword regex already covers.

**Priority 6 — everything else traces, with two small gaps.** I matched Finding 1's
seven-row channel table, Finding 2's package table and its "all remaining" row of
2,339, Finding 3's 24 closure terms and three leading term counts, Finding 4's
field-population table and both sole-evidence ratios, Finding 5's digest and
septic counts, Finding 6's full per-source table and the duck-field attributions,
Finding 7's hold-out table and per-group breakdown, Finding 8's nine per-term
support rates and three accept-basis counts, Finding 9's coherence and trap
tables, and Finding 10's six subtype counts and 30.8%. The Limitations numbers
check too: 4 of 758 unresolved background values in the transfer log, exactly 3
terms dropped by an accession-based numerator in `v23_lift_recheck.csv` (each on
2 accessions counted as 4 rows, failing the count filter and not the lift
threshold), 747 multiply-labelled accessions, 5,391 of 5,998 on the GOLD bridge,
and 180 columns / 756M attribute rows / 810 harmonized names / 42.9M statements /
66.4M content pairs from the schemas run.

The 62.7% riverine figure for the `Industrial wastewater` lineage, added in v2.3
and not written to any CSV, is correct: 192 of 306 samples in that exact lineage,
and all 192 riverine records do sit there.

The two gaps are presentational. The same term carries two different bases in
adjacent findings — `riverine metagenome` is 10,343 in Finding 7 (the no-native
subset) and 11,376 in Finding 8 (all carriers) — with nothing saying they measure
different things. And `trap_check.csv` has a fifth row, `river_discharge` with 3
records, that Finding 9's trap table silently drops.

**Figures.** All four match the cited run byte-for-byte, which is better
traceability than most projects achieve. But `fig_transfer_screen.png`'s left
panel is titled **"Transfer adds records; screening removes the ones inherited
from disputed source groups"**, and v2.4 exists to retract exactly that. Eight
class-1 terms are accepted, the 1,283 chicken records survive, and the single
largest component of the gain survives. The title also mis-describes the other
direction, since most of the 51,610 removed records are class-2 material not from
a disputed group. The Revision History closes "No figure changed", and this is
the one figure a reader consults for Finding 8. Separately, three of the four
figure titles are clipped at the canvas edge.

**One residual attribution error.** Finding 6's parenthetical says "The 79
acid-mine-drainage records belong to MGnify's `Mine water` biome, not to GOLD."
The MGnify lineage is `Industrial wastewater:Mine water` with 79 samples;
nothing establishes those samples are acid mine drainage. The sentence was added
to correct an earlier confusion and re-labels mine water as acid mine drainage in
the process.

**No overstated causal or novelty language found.** The report consistently says
"asserts wastewater" rather than "is wastewater", declines to adjudicate MGnify's
intent, and states repeatedly that no channel's precision was measured. Finding 9
says outright that the coherence diagnostic "ranks channels; it does not score
them". The Limitations section is honest and the negative results are reported
rather than buried.

## Suggestions

1. **Replace the 31 and 1 residual, or state the design that makes it right.**
   Either re-mine the two term tables from source-exclusive cohorts and recompute
   the hold-out, in which case 31 and 1 stand, or report 251 and 246 and say the
   exclusion was test-side only. As written the sentence "Excluding the 589
   doubly-labelled accessions removes nearly all of it" is false for the figures
   it qualifies. Both residuals are already derivable from
   `v24_overlap_residual.csv` by subtracting the 589.

2. **Regenerate `fig_transfer_screen.png` with a title v2.4 supports.** Something
   like "Transfer adds records; screening removes about three fifths of them,
   including most but not all disputed-group idiom". `src/06_figures.py:84` is the
   line. Note in the Revision History that a figure did change.

3. **Reconcile Finding 7's class 3 with Finding 8's 51,610.** One sentence: the
   screen keeps 32,345 of the 83,955, of which 31,789 are matched only by class-3
   terms and the rest by accepted class-1 terms or a mix.

4. **Bring Finding 7's heading in line with its body.** The body's load-bearing
   claim is that the largest component of the apparent gain survives screening and
   traces to this project's own inclusion decision. The heading currently blames
   the unscreened state, which the body contradicts.

5. **Carry the MGnify-direction ambiguity into the restatement and the mind-
   changing bullet.** Both currently present 1.2% and 0.5% symmetrically. The
   bullet should also say the figures are upper bounds, since the report
   establishes that two paragraphs earlier.

6. **Fix "over 14 fields" in the restatement.** The 83,955 and 148,289 results use
   10 fields. Either say 10 or drop the number.

7. **State the class-1 boundary.** Say that "disputed" was applied to
   MGnify-dominant terms only, that 32 GOLD-dominant `industrial_ww` terms fall
   outside it, and that 8 of the 29 class-1 terms are accepted and include
   plausible wastewater vocabulary such as `acid mine drainage`.

8. **Add the taxonomy independence caveat to Finding 4.** The 12-of-369,048 result
   is mechanical, because the taxon channel reads the same string as the keyword
   channel on that field.

9. **Correct the mine-water parenthetical in Finding 6**, and note in Finding 4 or
   Scope that the MGnify fetch returned 859 of 958 advertised `Water and sludge`
   samples and 8 of 17 for one nutrient-removal lineage, so "all 4,352" means all
   that were retrievable.

10. **Housekeeping.** Add `src/10_v24_checks.py` to the README Reproduction block
    and `REVIEW_3.md` to Quick Links; remove the duplicated Worklog line. Add the
    `river_discharge` row to Finding 9's trap table or say it was dropped. Say
    that Finding 7's 10,343 and Finding 8's 11,376 are different bases for the
    same term. Note that Finding 3's "8 accessions" sums per-field counts and is
    an upper bound. Pass `bbox_inches="tight"` when saving figures, since three of
    four titles are clipped.

## Review Metadata
- **Reviewer**: BERIL Automated Review (Claude, claude-opus-5)
- **Date**: 2026-10-23
- **Scope**: REPORT.md, README.md, beril.yaml, references.md, 25 runs (123 output
  files hash-verified, 13 cited runs read in full), 14 analysis scripts, 0
  notebooks, 6 generated data files, 4 figures (all four viewed and compared to
  their source CSVs and to the cited run's hashes). Checks performed included
  independent re-derivation of Finding 1's crosstab rollup, Finding 7's term
  classification, Finding 8's accept-basis counts, and the labelled-cohort
  accession and source-overlap counts from `labelled_samples.parquet`. The
  BERDL lakehouse was not queried; all verification was against recorded run
  outputs on disk, so claims resting on a fresh Spark query could not be
  independently recomputed.
- **Note**: This review was generated by an AI system. It should be treated as
  advisory input, not a definitive assessment.

<!-- report_hash: sha256:7f9829816675f97ea7ec93ce00b996b5dab61d80b0dc9d4e12a1d6b17dbad87b -->
