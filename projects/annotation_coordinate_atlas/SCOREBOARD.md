# Scoreboard — Gene and Protein Function Annotations in BERDL, with Coordinates
<!-- plan_hash: sha256:939a7492a268a47c8c514afb7b792b67248128a08a2336e750697af188f4c332 -->  **4 of 4 notebooks run**

**Snapshot:** all four notebooks re-executed in order **2026-10-07** against SemCat catalog
generated 2026-10-06T19:38:26Z (`code_version` 0.27.0) and the live lakehouse of 2026-10-07.
NB03's value sampling is now deterministic (Correction 7). Figures below are
from that single run. Rates are quoted **per distinct `schema_sig`**, as `RESEARCH_PLAN.md`
requires; per-column figures are given where they differ.

| Hypothesis | Standing | Criterion | Observed (unit, n) | Where |
|---|---|---|---|---|
| H1 (SemCat sufficient) | refuted | recall ≥0.80 on every facet AND coordinate system resolvable from SemCat fields alone | coordinate sub-test failed: 5 distinct systems share the one `coordinate` label, 22/78 unresolvable even with type+bounds+siblings; recall 30/93 = 32.3% (schema_sig; 30/100 = 30.0% per column) | `01_semcat_discovery.ipynb` §1; `03_semcat_grade.ipynb` §2b |
| H2 (high precision, low recall) | supported | recall <0.50 AND precision ≥0.80 | recall 32.3% ✓; strict precision 51/60 = 85.0% ✓, lenient 56/60 = 93.3% ✓ (schema_sig = per-column here; no clones in the precision sample) — holds under both adjudication policies | `03_semcat_grade.ipynb` §2a, §2b-bis, §2c |
| H3 (structural not semantic) | refuted on its precision clause | recall <0.50 AND precision <0.80 AND row_count ≥95% AND ≥1 table beyond own inventory | precision 85.0% ✗ (needed <0.80). Other clauses hold: row_count exact 59/60 = 98.3% ✓ (table, n=60, computed live in-notebook); 493 candidate tables in unreadable tenants ✓ | `03_semcat_grade.ipynb` §2c; `02_ground_truth_sweep.ipynb` §6a |
| H0 (no value over name regex) | refuted | rejected if SemCat yields ≥1 true positive a name regex misses | SemCat's specific labels found 2 census tables the regex missed; at column level it labelled 128 `function_id` columns outside the regex's reach, with only 3 outright mislabels in 59 judged (table, n=51 census; column, n=275 labelled) | `03_semcat_grade.ipynb` §3, §4 |

## Use-case feasibility (NB04 — a direct test of the deliverable, not a hypothesis)

| Claim | Standing | Observed |
|---|---|---|
| BGC regions and genes share a contig namespace | supported | 28,494/28,494 = **100%** of `gene_bgc` contigs match a `gene` contig (soil biome); **13.9 genes strictly inside per BGC** — the biologically expected magnitude, which validates the join rather than merely counting string matches; separately, 754,313 gene–BGC pairs at a ±5,000 bp flank (21.3 per BGC, larger by design because the flank admits neighbours) |
| Multi-domain *order* search is possible | supported | 6,963 PF00005/PF00528 pairs on shared cluster representatives; PF00528 precedes PF00005 in **6,167/6,530 proteins = 94.4%** (one protein, one vote; 395 proteins carry repeat domains). Undeduplicated pair-level: 6,578/6,963 = 94.5% — pseudo-replication immaterial here. Expected ABC-transporter architecture; gap IQR −412 to −371 aa |
| Collocation is possible everywhere coordinates exist | **refuted** | of 18 region tables assessed (**17 coordinate-bearing**): **6 positionally joinable** (5 direct + 1 bridged via a 1:1 table), 5 protein-space only, 1 blocked, 1 with no coordinates at all |

## Facet dependence

Strict precision by facet: `seqref` 16/16 = 100%, `span` 5/5 = 100%, `function_id` 30/39 = 77%.
Recall by facet: `span` 17/43, `function_id` 11/44, `strand` 2/13. The `strand` facet is the
worst on every measure (full-frame recall 2/13 = 15%, precision 2/4 = 50%) and is too small to
carry an estimate alone.

**A cross-check that must not be over-read.** The full-frame, rule-based confusion matrix
(`data/semcat_confusion_by_facet.csv`) is much harsher — function_id precision 0.53, span 0.44,
strand 0.50 — because it treats this project's own name regex as truth. The audit showed that
regex is itself incomplete, so SemCat is charged a false positive every time it labels a column
the regex failed to recognise, which is SemCat succeeding. The value-adjudicated audit is the
pre-registered test and supersedes it.

## Corrections (kept visible)

1. **Precision adjudication, H3 → H2.** A first pass sampled 12 values per column and scored
   labels correct-or-wrong, giving strict precision 77.8% and "H3 supported". That pass scored
   placeholder-only samples (`-`, `nan`, `None`) against SemCat — a limit of the *sample*, not
   of SemCat — and treated multi-valued columns identically to genuine mislabels. Re-run with
   60 values and a four-way adjudication: precision 83.9% on that snapshot, 86.4% on the final
   one; verdict H2. Recall was ~32% throughout, so H1's refutation never depended on it. Logged
   as `RESEARCH_PLAN.md` Revision History v2; `beril`'s own `plan_digest` confirms the approval
   remains valid.
2. **Inter-domain gap.** First reported as median −680.5 aa from a 300-row sample taken *after*
   `ORDER BY gap_aa` — the extreme tail, not the distribution. Recomputed with
   `percentile_approx` over the full join: median **−392 aa**.
3. **Mixed snapshots — found by `REVIEW_1.md`, not self-detected.** Re-running only
   `02_ground_truth_sweep.ipynb` on 2026-10-06 desynchronised the report from the repo
   (REPORT said 883 tables / 159 stale; notebooks produced 826 / 5). Fixed by re-executing all
   four notebooks in order at one snapshot. SemCat itself moved 0.19.28 → 0.21.6 → 0.24.2 → 0.26.1 → 0.27.0 in
   nine days, which is why the snapshot is now pinned in the report header.
4. **Pre-registered `schema_sig` dedup was never implemented — also found by `REVIEW_1.md`.**
   Now in `03_semcat_grade.ipynb` §2b-bis. No clones in the precision sample (59 → 59); the
   recall sample collapsed 100 columns → 93 groups, moving recall 30.0% → 32.3%. Changes no
   verdict, and slightly favours SemCat.

5. **The same staleness bug one layer deeper — found by `REVIEW_2.md`.** After Correction 3,
   §6a still claimed to check "live Iceberg `COUNT(*)`" while reading a 2026-10-02 JSON that
   nothing regenerated, feeding the census `row_count` column and the H3 ≥95% clause. §6a now
   issues the counts itself and re-emits every dependent file. Live: **59/60 = 98.3%** exact
   (target set is now exactly the census tables, hence 60 not 66). Clause still passes.
   Corrections 3 and 5 are one defect that survived its own first fix.

6. **Lenient precision stated as 56/59 = 94.9% against artifacts saying 55/59 = 93.2% — found
   by `REVIEW_7.md`.** Corrected. Root cause: the audit's value sample uses `LIMIT` without
   `ORDER BY`, so re-runs can adjudicate a slightly different 60 values per column, moving one
   column between `wrong_cardinality` and `wrong_label`. The README's "seeded and reproducible"
   claim has been narrowed accordingly — the seed fixes which *columns* are audited, not which
   *values*. Strict precision, recall and all verdicts were stable throughout.

7. **The non-determinism behind Correction 6 fixed at source.** NB03's sampler is now
   `SELECT DISTINCT col ... ORDER BY xxhash64(CAST(col AS STRING)) LIMIT 60`, with a hash-bucket
   prefilter where SemCat reports `ndv > 100,000`. Two cheaper designs were measured and
   rejected: `ORDER BY col` surfaces only sentinels (`-` sorts below every alphanumeric), and
   `ORDER BY xxhash64(col)` without `DISTINCT` groups identical values (one value returned 60×).
   Effect: one placeholder-only column resolved to real values, so judgeable went 59 → 60,
   `sentinel_only` 2 → 1, **strict precision 86.4% → 85.0%**, **lenient 93.2% → 93.3%**.
   **Recall unchanged at 32.3%** — it matches label families and never reads sampled values.
   The audit now reproduces exactly instead of drifting ~±2 points per run.

8. **`kbase.genomes.feature` wrongly classified as unusable — found by a human reader.** The
   census read the table in isolation, saw no sequence column, and called 1,011,650,903 rows of
   coordinates unplaceable. `kbase.genomes.contig_x_feature` places every feature on a contig
   with an exact 1:1 mapping (1,011,650,903 rows / 1,011,650,903 distinct features /
   32,868,698 contigs); a self-join on one contig returns 14–15 CDS within ±5 kb. Reclassified
   `blocked` → `bridged (1:1)`: **positionally joinable 5 → 6**, blocked 2 → 1. No hypothesis
   verdict affected. Twelve prior review rounds missed it because each checked the report against
   the project's own artifacts, and the artifact was wrong.

**Hypothesis verdicts are stable across seven full-chain re-runs, four SemCat version stamps,
two adjudication policies and two units of analysis.** The use-case count moved once, in
Correction 8.
