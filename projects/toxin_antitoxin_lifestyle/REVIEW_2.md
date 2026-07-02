---
reviewer: BERIL Automated Review
date: 2026-07-02
project: toxin_antitoxin_lifestyle
---

# Review: Toxin-Antitoxin Systems Across Bacterial Lifestyles (Round 2)

## Summary

This is a strong second pass on a mechanistic follow-up to `lifestyle_cog`. The
project responds directly and substantively to REVIEW_1: the RelE attribution
ambiguity is now audited in a dedicated notebook (NB04), the paired-Pfam
sensitivity check has been executed and returns a genuinely informative negative
result (0.02% co-annotation rate, correctly attributed to eggNOG's per-gene
scope), the stale filename reference in the README is fixed, the H2 cohort
intersection is now spelled out in REPORT §Cohort, and the `src/build_nb0*.py`
authoring pattern is now discoverable from the README. Three pre-registered
hypotheses remain crisply stated and honestly reported, including the direction-
reversed H2 rejection and a corrected-and-slightly-stronger RelBE finding
(r = −0.439 vs −0.408). Remaining gaps are minor and mostly documentation
polish: the RESEARCH_PLAN panel table (14 candidates) has not been reconciled
against the executed 10-family panel, a small numerical inconsistency exists
in REPORT (12- vs 10-family seed), and the phylum-stratified H1 forest plot
suggested in REVIEW_1 was not added. None of these affect the correctness of
the reported science.

## Methodology

**Response to REVIEW_1 §RelE attribution (medium priority #1)** — Fully
resolved. NB04 rebuilds attribution by inspecting each RelE-carrying gene
cluster's full comma-delimited PFAMs string for co-annotated antitoxin
partners (`RelB` for RelBE, `PhdYeFM_antitox` for YoeB-YefM). The finding is
important on its own: 8,431/8,431 RelE-carrying gene clusters are
`RelE_solo` — none co-annotate either antitoxin on the same eggNOG record.
Redefining RelBE from `RelB`-indicator only actually *strengthens* the
host-enrichment signal (r = −0.439 LARGE vs original −0.408 LARGE), because
the ambiguous RelE_solo hits (which are lifestyle-neutral, r = +0.006, n.s.)
diluted the original attribution. The correction is transparent, the direction
of the headline finding survives, and both old and new numbers are reported
side-by-side.

**Response to REVIEW_1 §Sensitivity checks (medium priority #2)** — Partially
resolved with an informative negative result. The pre-registered check #4
(toxin+antitoxin co-annotation) is executed in NB04 §4. Only 85 of 407,118
TA-Pfam-carrying gene clusters (0.02%) carry both a toxin-side and
antitoxin-side name on the same PFAMs string. NB04 correctly diagnoses the
root cause (eggNOG annotates each gene individually; toxin and antitoxin sit
on separate adjacent genes) and correctly concludes that the pre-registered
"within 500 bp" version of the check requires chromosomal-neighborhood
analysis on `bakta_annotations` + coordinates, deferred to future work. This
is a legitimate scoping decision, well-documented. Check #5 (expanded-panel
sensitivity) is explicitly deferred with a one-paragraph justification in
NB04 §5 and REPORT §RelE Attribution. Acceptable resolution.

**Response to REVIEW_1 §README filename (low priority #3)** — Fixed.
README.md line 29 now references
`projects/lifestyle_cog/data/species_lifestyle_classification.csv`, matching
the file the notebooks actually read.

**Response to REVIEW_1 §Cohort intersection (low priority #4)** — Fixed.
REPORT §Cohort now includes the explicit sentence: "2,403 species used for
H1–H3 — the intersection (species with TA hits ∩ lifestyle label ∩
genome_size in gtdb_metadata)" and verifies from NB02 output that the
126 "zero-TA" species and the 126 "dropped-for-missing-genome-size" species
are the same set.

**Response to REVIEW_1 §Forest plot (low priority #5)** — Not addressed. The
figures directory still contains 2 PNGs (nb02_h1_h2_overview.png,
nb03_family_and_phylum.png). Nice-to-have, not blocking.

**Response to REVIEW_1 §Panel-table reconciliation (low priority #6)** —
Partially addressed. REPORT now clearly notes the executed panel is 10
detectable Type II families and that HicA/HigA hit zero, but
RESEARCH_PLAN.md §TA Family Panel still shows the original 14-family
candidate table. Since RESEARCH_PLAN is meant to be the pre-registered
scope, a one-line addendum noting the executed subset would be enough.

**Response to REVIEW_1 §Link build scripts (nice-to-have #7)** — Fixed.
README.md now explicitly notes "The `src/build_nb0*.py` scripts are
diff-friendly authoring source for the notebook JSON."

## Code Quality

**NB04 implementation is clean.** It reloads the long-form
`ta_hits_by_gene_cluster.tsv`, deduplicates to gene-cluster level, and applies
the same token-safe `has_token` matcher used elsewhere. The RelE binning
logic (RelBE if RelB is co-annotated; YoeB-YefM if PhdYeFM_antitox is
co-annotated; RelE_solo otherwise; RelBE_ambig if both — with count 0 in
practice) is straightforward and auditable. All output cells in NB04 are
populated.

**Subtle methodological consideration on the NB04 RelBE_new definition** —
The re-attribution operationally defines `RelBE_new = has_RelB` (regardless
of whether `RelE` is also present). This is defensible because RelB is
specific to the RelBE family, while RelE is shared, so `has_RelB` is the
cleaner indicator. The trade-off is that gene clusters annotated with RelE
alone (the RelE_solo bin) are now not counted as RelBE at all — the report
handles this correctly by reporting all three bins in the same table. A
tiny addition would be to state explicitly in the notebook that
`RelBE_new` is defined as "presence of the RelB antitoxin, with or without
a co-annotated RelE toxin" so that readers do not have to reverse-engineer
it from the binning function.

**Paired-Pfam finding is a legitimate new pitfall observation.** The 0.02%
co-annotation rate (85/407,118) is a strong argument that any future TA
project relying on eggNOG PFAMs alone cannot enforce toxin+antitoxin
pairing. This would be a useful addition to `docs/pitfalls.md` under
`[toxin_antitoxin_lifestyle]` for future reference.

**Pitfall awareness (unchanged from REVIEW_1)** — Still solid. Both
`PFAMs`-are-names and `genome_size`-lives-on-`gtdb_metadata` pitfalls are
correctly handled and tagged in `docs/pitfalls.md`.

**Notebook organization** — All four notebooks follow the setup → load →
analyze → visualize → persist pattern. Outputs are populated across NB01
(14 code cells), NB02 (11), NB03 (9), NB04 (9). This is above-average
audit trail quality for the observatory.

## Findings Assessment

**Are conclusions supported by the data shown?** All three headline
verdicts remain well-supported and the RelE re-audit slightly strengthens
the H3 story:

- **H1 STRONGLY SUPPORTED**: Unchanged. Paired Wilcoxon p = 2 × 10⁻¹⁵⁵,
  r = +0.625 (LARGE), 10/11 phyla preserve direction. Pooled 3×3 observed-
  vs-baseline table in REPORT §H1 shows accessory bucket +15,004 above
  expectation.
- **H2 REJECTED (direction opposite)**: Unchanged. Host 6.80 vs free 5.21
  TA/Mb (r = −0.133 small); accessory-only variant r = −0.198 slightly
  stronger; Spearman ρ = +0.013 confirms no residual size confound after
  per-Mb normalization; 7/9 testable phyla preserve host-higher direction.
- **H3 SUPPORTED, with corrected attribution**: 10/10 families still BH-FDR
  significant. RelBE host-enriched (r = −0.439 LARGE under corrected
  attribution, up from −0.408); VapBC free-enriched (r = +0.318 LARGE);
  HipBA host-enriched (r = −0.135 small-to-medium). The correction is
  reported honestly and the direction-and-magnitude story is unchanged.

**Limitations acknowledged?** The updated REPORT now explicitly documents:
- The RelE ambiguity and its correction (§RelE Attribution)
- The paired-Pfam 0.02% rate and why pre-registration check #4 could not
  be executed in its intended form
- The panel scope of 10 executed families vs the broader TADB target
- The 126-species drop and its overlap with zero-TA species (§Cohort)

The one remaining honesty item is the small "12-family seed" mention in
REPORT §Cohort. The actual `ta_families_seed.tsv` contains 10 families and
17 Pfam names — the "12-family" language appears twice in REPORT
(§Cohort, §Panel scope) and is not consistent with the seed file or with
"Loaded 10 TA families" in NB01 output. This is a documentation-polish
issue, not a correctness issue.

**Visualizations** — Still 2 figures for 4 notebooks. NB04 is a pure
diagnostic notebook without a plot, which is defensible. A forest plot of
per-phylum H1 or H2 rank-biserial (REVIEW_1 §5) would still add value but
is not blocking.

**Small numeric inconsistency**: REPORT §Key Findings reports "407,884 gene
clusters carry at least one Type II TA-family Pfam signature," but NB01
output shows "Gene clusters with at least one TA Pfam hit: 407,921" and
NB04 shows "Distinct gene clusters carrying any TA Pfam: 407,118" (after
inner-join to `gene_cluster` — the smaller number is post-join). The 407,884
in REPORT does not match either number in the notebooks. Pick one canonical
number and cite the notebook cell it comes from.

## Suggestions

1. **(Priority: low)** Reconcile the "12-family seed" language in REPORT
   §Cohort and §Panel scope with the actual 10-family
   `ta_families_seed.tsv`. If the plan started with 12 and dropped 2 for
   nomenclature/dedup reasons, add one sentence explaining that; otherwise
   just say "10-family seed."

2. **(Priority: low)** Fix the 407,884 → 407,118 (post-join) or 407,921
   (pre-join) number in REPORT §Key Findings so the headline count matches
   the notebook it is derived from.

3. **(Priority: low)** Add a one-line addendum to RESEARCH_PLAN.md §TA
   Family Panel noting that the executed panel was reduced to 10
   detectable families and pointing readers to REPORT §Cohort for the
   full rationale. This closes the loop between plan and report.

4. **(Priority: low)** In NB04 §2, add a one-sentence comment clarifying
   that `RelBE_new` is defined as "presence of the `RelB` antitoxin token,
   with or without a co-annotated `RelE` toxin token" — the current
   `relbe_indicator` lambda buries this behind a one-line function.

5. **(Priority: nice-to-have)** Add the 0.02% eggNOG per-gene co-annotation
   observation to `docs/pitfalls.md` under `[toxin_antitoxin_lifestyle]`.
   Anyone else trying to enforce toxin+antitoxin pairing purely from the
   `PFAMs` column will hit the same wall, and the diagnosis in NB04 §4 is
   good reference material.

6. **(Priority: nice-to-have)** The REVIEW_1 §5 phylum-stratified H1
   forest plot suggestion still stands — a small addition to NB03 that
   would make the "10/11 phyla preserve direction" claim visually
   obvious without re-running the pipeline.

## Review Metadata

- **Reviewer**: BERIL Automated Review
- **Date**: 2026-07-02
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, REVIEW_1.md,
  references.md, requirements.txt, 4 notebooks (NB01–NB04), 4
  `src/build_nb0*.py` authoring scripts, 12 data files, 2 figures, and
  `docs/pitfalls.md`.
- **Note**: This review was generated by an AI system. It should be treated
  as advisory input, not a definitive assessment.
