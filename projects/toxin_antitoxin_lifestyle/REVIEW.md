---
reviewer: BERIL Automated Review
date: 2026-07-02
project: toxin_antitoxin_lifestyle
---

# Review: Toxin-Antitoxin Systems Across Bacterial Lifestyles

## Summary

This is a well-scoped, well-documented, and technically careful mechanistic follow-up
to the `lifestyle_cog` project. Three pre-registered hypotheses are stated crisply,
tested with appropriate non-parametric statistics, controlled for the two most
plausible confounders (genome size and phylum), and reported honestly — including a
directional rejection of H2. The three-file structure (README / RESEARCH_PLAN /
REPORT) is followed, notebook outputs are populated across all three notebooks
(34/37 code cells have outputs), and the two most important known BERDL pitfalls for
this analysis (Pfam-NAMES-not-accessions in `PFAMs`, and `genome_size` living on
`gtdb_metadata` rather than `genome`) are both correctly handled and cited to
`docs/pitfalls.md`. The main areas for improvement are (a) a subtle family
attribution ambiguity where the Pfam name `RelE` is shared by RelBE and YoeB-YefM
but attributed only to RelBE, which the code comments on but the REPORT does not
disclose; (b) minor internal inconsistencies (the README references a file name
that no longer exists); and (c) the family-composition analysis stops short of the
pre-registered "toxin+antitoxin co-localization" sensitivity check.

## Methodology

**Research question**: Clearly stated in both README.md and RESEARCH_PLAN.md as a
mechanistic drill-down inside COG-V (the coarse defense category) from the
lifestyle_cog project.

**Hypotheses**: Three hypotheses (H1 accessory-enrichment, H2 host-lower per Mb, H3
family composition asymmetry) each get an H0, a rationale, and a pre-registered
effect-size threshold (|r| ≥ 0.15 or 0.2). This is unusually rigorous for
observatory work.

**Data sources**: Named explicitly with row counts and filter strategy in a table
(RESEARCH_PLAN §Data Sources). The reuse of the lifestyle_cog cohort is called out
as a strict extension rather than new lifestyle classification work — appropriate
scoping.

**Reproducibility**:
- `requirements.txt` is present and lists the seven packages actually used.
- The README `## Reproduction` block gives the three-command `jupyter nbconvert`
  recipe with clear Spark-vs-local separation (NB01 is Spark, NB02/NB03 are
  local). REPORT.md repeats the same recipe with explicit `--timeout` values.
- NB01 uses BROADCAST-free batched IN-clauses (batch size 500) for per-species
  aggregations, which is a reasonable pattern for 25K species.
- Intermediate TSVs are all persisted so NB02/NB03 do not require Spark. The
  large `ta_hits_by_gene_cluster.tsv` (46 MB) is gitignored but regenerable
  from NB01. This is the right trade-off.
- The `src/build_nb0*.py` authoring scripts are a nice touch — they make the
  notebook contents diff-friendly at review time.

**Small documentation gap**: The README (line 29) refers to
`projects/lifestyle_cog/data/species_lifestyle.tsv`, but the code in both NB02 and
NB03 reads `projects/lifestyle_cog/data/species_lifestyle_classification.csv`,
which is what actually exists on disk. Either the README or the file name is stale
— since the CSV is the file that exists, update the README to match.

## Code Quality

**SQL / BERDL patterns**:
- The token-safe four-way `LIKE` matching on the comma-delimited `PFAMs` column
  (NB01 §3, `token_where` helper) is exactly the pattern recommended in
  `docs/pitfalls.md` for this table. Substring matches like `LIKE '%RelE%'` are
  correctly avoided.
- Genome size is joined via `gtdb_metadata.accession = genome.genome_id`
  (NB01 §9), consistent with the pitfalls guidance that `genome_size` is on
  `gtdb_metadata`, not `genome`.
- Batched `IN (...)` clauses of size 500 keep the SQL under practical query-size
  limits and avoid a huge cross-join through the full 132M-row `gene_cluster`
  table.

**Statistical methods**:
- **H1**: Paired Wilcoxon signed-rank of per-species non-core fractions (TA vs
  baseline), plus a pooled chi-square. The rank-biserial r is computed manually
  from `(pos − neg) / total` on the paired sign-rank statistic — correct.
- **H2**: Mann-Whitney U two-sided with rank-biserial r via
  `1 − 2U/(n1·n2)`. Genome-size confound is checked directly with Spearman on
  raw and per-Mb rates (report shows the per-Mb rate has ρ = +0.013 — the
  normalization does its job).
- **H3**: Per-family Mann-Whitney with Benjamini-Hochberg FDR across the 10
  detectable families. The Shannon-entropy family-diversity measure is a
  sensible operationalization of "broader repertoire."
- Phylum stratification uses ≥20 species per phylum plus ≥5 species per
  lifestyle for the H2 sub-test — reasonable thresholds.

**Subtle issue: RelE attribution is family-collapsed to RelBE**. In
`ta_families_seed.tsv`, the Pfam name `RelE` is listed as the toxin for BOTH
RelBE (row 1) and YoeB-YefM (row 4). The build script uses `setdefault` when
constructing `family_map` (see `build_nb01.py` §6), which means every RelE
domain hit is attributed to RelBE (first-seen), never to YoeB-YefM. YoeB-YefM
is therefore counted essentially only via its antitoxin partner
`PhdYeFM_antitox`. The comment in code acknowledges the ambiguity, but:

1. The REPORT's headline finding **RelBE host-enriched (r = −0.408, LARGE)**
   likely conflates RelBE and YoeB-YefM toxin hits, since ~8,468 `RelE`
   annotations (per `ta_panel_coverage.tsv`) all map to RelBE.
2. The REPORT should either (a) disclose that "RelBE" here means the
   RelE-superfamily ribonuclease pool as a whole, or (b) rebuild the
   attribution to split RelE hits between families based on which antitoxin
   is co-annotated on the same gene cluster.

This does not invalidate the big-picture direction (host-enriched
translation-arresting ribonucleases) but it complicates the family-specific
claim.

**Related sensitivity check that was pre-registered but not executed**:
RESEARCH_PLAN §Sensitivity Checks item 4 promises a "toxin-only vs
toxin+antitoxin" analysis restricted to co-localized T–AT pairs (within
500 bp). This is exactly the check that would resolve the RelE attribution
ambiguity above. Neither notebook implements it. Add it, or explicitly retract
the sensitivity item and explain why.

**Pfam family definition sensitivity (Sensitivity Check #5)** — the promised
"strict-TADB vs expanded" comparison is also not implemented. The report
acknowledges panel size is 12 families rather than 40, but does not rerun H3
under a different panel definition.

**Pitfall awareness**: Two pitfalls in `docs/pitfalls.md` are explicitly tagged
`[toxin_antitoxin_lifestyle]` — the PFAM-names issue and the
`gtdb_metadata.genome_size` join. Both are correctly handled in NB01. A third
tag (Spark Connect restart requiring `get_credentials()` first) reflects
infrastructure work done during the project — good documentation practice.

**Notebook organization**: Each notebook has clean setup → load → analyze →
visualize → persist structure with markdown section headers. Output cells are
populated (14/15 in NB01, 11/12 in NB02, 9/10 in NB03). This is a strong
positive versus projects that commit code-only notebooks.

## Findings Assessment

**Are conclusions supported by the data shown?**

- **H1 STRONGLY SUPPORTED**: The paired Wilcoxon (p = 2×10⁻¹⁵⁵, r = +0.625) and
  the pooled chi-square (χ² = 1.47×10⁴) both point the same direction, and 10/11
  phyla preserve it. The pooled 3×3 observed-vs-expected table in REPORT.md is
  the clearest single piece of evidence: accessory bucket is +15,004 above the
  baseline expectation while core is −5,065 and singleton is −9,939. Well
  supported.

- **H2 REJECTED (direction opposite)**: The report treats this correctly — the
  a priori sign was wrong and this is stated up front rather than buried.
  Median per-Mb densities (host 6.80, free 5.21) and the −0.133 rank-biserial
  are reported with the appropriate qualifier that the effect size is small.
  The accessory-only variant is slightly larger (−0.198). Genome-size
  sensitivity (Spearman ρ = +0.013 after per-Mb normalization) is convincing.
  The Cyanobacteriota inversion (free carries 25.3 vs 4.4 TA/Mb) is flagged
  as biologically real and traceable to literature.

- **H3 SUPPORTED, with the RelBE attribution caveat above**: 10/10 families
  significant at BH-FDR < 0.05 is a strong outcome. The interpretation
  paragraph (VapBC free-enriched via soil actinomycetes; RelBE host-enriched;
  HipBA persister-cell selection) is careful and cites specific prior work.

**Limitations acknowledged?**
- The report mentions the Cyanobacteriota inversion and the two zero-hit Pfam
  names (HicA, HigA) up front. Good.
- The report does not disclose the RelE→RelBE family collapse (see above).
- The report does not disclose that the family panel is 12 rather than the
  ~40-family TADB target — this is a scope reduction from the plan.
- The `n=1660 host / 743 free` cohort loses 45+81=126 species with lifestyle
  labels but zero TA hits. The report handles this correctly (they're
  explicitly noted as "itself evidence against H2") but the H2 Mann-Whitney is
  computed on the `ta_per_mb` values only for species with ≥1 TA hit AND a
  known genome size — verify from the notebook output. From cell 11 output:
  "Species dropped for missing genome-size: 126" — this matches the number of
  zero-TA species, suggesting these are one and the same set. That is fine and
  is documented, but a one-line note in REPORT.md clarifying that H2's
  1660+743 = 2,403 is the intersection (TA-carrying × lifestyle-labeled ×
  genome-sized) would remove any ambiguity.

**Visualizations**:
- Only 2 figures for 3 notebooks — but each figure is a well-composed 2-panel
  overview (H1+H2 for NB02, family+phylum for NB03). NB01 does not need a
  figure because it is pure ETL.
- Figures cover the headline results but no phylum-stratified H1 forest plot
  and no family-composition per-species distribution plot. Nice-to-have, not
  critical.

**Comparison to prior BERDL projects**: REPORT.md includes an explicit
`| Project | What it showed | This project extends |` table cross-referencing
`lifestyle_cog`, `functional_dark_matter`, and `snipe_defense_system`. This is
the right kind of scholarship for the observatory.

## Suggestions

1. **(Priority: medium)** Disclose the RelE family attribution in REPORT.md.
   Either (a) add a sentence noting that "RelBE" in the family results includes
   all RelE-superfamily ribonuclease hits, since RelE is also the YoeB toxin
   Pfam name; or (b) rework the family attribution in NB01 to split RelE hits
   between RelBE and YoeB-YefM based on co-annotated antitoxin (RelB → RelBE,
   PhdYeFM_antitox → YoeB-YefM). This is a real methodological question, not
   a cosmetic one.

2. **(Priority: medium)** Execute or explicitly retract the two pre-registered
   sensitivity checks that were not run: toxin+antitoxin co-localization (§4)
   and expanded-panel sensitivity (§5). If they are out of scope for this
   round, add a "deferred sensitivity checks" note to REPORT.md with a
   one-sentence justification.

3. **(Priority: low)** Fix the README file-name inconsistency: line 29
   references `projects/lifestyle_cog/data/species_lifestyle.tsv`, but the
   actual file (and the code) is
   `projects/lifestyle_cog/data/species_lifestyle_classification.csv`.

4. **(Priority: low)** Add a one-line note to REPORT §Cohort clarifying that
   the H2 n=1660/743 cohort is the intersection (TA-carrying ∩
   lifestyle-labeled ∩ genome-sized), and that the 126 dropped species are
   the same set that had zero TA hits (this appears to be true from the
   notebook but is not explicit in the report).

5. **(Priority: low)** Consider a small additional figure for the
   phylum-stratified H1 result — a forest plot of per-phylum accessory-
   enrichment Δ or rank-biserial. It would make the "10/11 phyla preserve
   direction" claim visually obvious.

6. **(Priority: low)** The panel table in RESEARCH_PLAN.md lists ~14 candidate
   families with ~35+ candidate Pfams, but the executed panel is 12 families /
   17 Pfam names. Either update the plan table to match the executed panel or
   add a note to REPORT.md explaining the reduction (e.g., "families with
   unstable/ambiguous eggNOG naming were dropped").

7. **(Priority: nice-to-have)** The build_nb0*.py authoring scripts are a
   nice pattern — consider linking to them from README.md so a reviewer can
   find them without digging into `src/`.

## Review Metadata

- **Reviewer**: BERIL Automated Review
- **Date**: 2026-07-02
- **Scope**: README.md, RESEARCH_PLAN.md, REPORT.md, references.md,
  requirements.txt, 3 notebooks (NB01–NB03), 3 `src/build_nb0*.py` authoring
  scripts, 8 data files, 2 figures, and `docs/pitfalls.md`.
- **Note**: This review was generated by an AI system. It should be treated as
  advisory input, not a definitive assessment.
