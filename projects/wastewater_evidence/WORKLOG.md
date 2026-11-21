# Worklog — wastewater_evidence

## 2026-10-17 · project scaffolded → open
The author wants to find wastewater and wastewater-related samples across
metadata systems (BioSample, MGnify, NMDC, GOLD so far) and sort them into
subtypes (influent, effluent, sludge, digester, sewer). The question is which
attributes and values in which systems carry the strongest signal, how to
transfer labels from strong-signal systems to weak-signal ones, and how to
validate the transfer without hand-labeling thousands of records. Prior
observations: ~503k keyword hits in ~56M BioSample records, ~39% outside any
wastewater package; ~4.3k MGnify wastewater-biome samples, ~850 with no
wastewater wording in BioSample; substring traps such as "digest" matching
"undigested primary sludge".
→ [README.md](README.md)
→ [beril.yaml](beril.yaml)

## 2026-10-17 · ! Spark client package unavailable; direct Spark Connect used instead
`spark_connect_remote` cannot be installed (its GitHub org no longer resolves), so
`run_sql.py` fails at import. Confirmed on-cluster Spark Connect works with plain
pyspark and the KBase token; wrote `src/berdl_spark.py` and use the cluster conda
Python (`/opt/conda/bin/python`) for every run. Recorded in memories/pitfalls.md.
→ [pitfalls](memories/pitfalls.md)

## 2026-10-17 · schemas and row counts of candidate tables
Inventoried BERDL tables that carry sample descriptions: the NMDC flattening of
NCBI BioSample (`nmdc.ncbi_biosamples`, 51.7M samples, 756M attribute rows, 20.7M
parsed env-triad components with ENVO ids), NMDC `biosample_set` (27k, GOLD
ecosystem path + ENVO triads + INSDC/GOLD ids), AllTheBacteria `biosample_environment`
(2.76M isolates), ENA metadata (8.6M), and the ENVO graph in `kbase.ontology_source`.
`kescience.mgnify.biome` is the genome-catalogue biome list (18 rows), not samples,
so MGnify samples come from the public API instead.
→ [run](runs/20261017T011209Z-schemas/run.json)

## 2026-10-17 · GOLD public export fetched and parsed; MGnify samples fetched
GOLD is not in BERDL and its REST API needs a login, but the public Excel export
(`download?mode=site_excel`, 239 MB) is open. Streamed its XML to parquet: 63.8k
studies, 245k biosamples with 5-level ecosystem paths, 532k organisms, 637k
sequencing projects (these carry `ncbi_biosample_accession`, the bridge to
BioSample). MGnify API paged for all biomes and every sample under lineages that
mention wastewater.
→ [run](runs/20261017T011423Z-gold-parse/run.json)
→ [run](runs/20261017T011424Z-mgnify-fetch/run.json)

## 2026-10-17 · BioSample evidence crosstab
Over all 51.7M BioSample records, flagged four independent evidence channels:
wastewater package, ENVO term in the wastewater subclass closure (seeds found by
label, descendants via `entailed_edge`), metagenome taxonomy name, and keyword
regex over 15 text fields. Wrote aggregates only: crosstab of the four flags,
per-field hit counts with structured overlap, subtype regexes with trap counters
(`digest` vs `undigested`/`digestive`), and the most common values among
keyword-only and structured-only records.
→ [run](runs/20261017T011707Z-biosample-evidence/run.json)

## 2026-10-17 · ! word-boundary regexes were silently broken inside Spark SQL literals
`\b` inside `RLIKE '...'` is a backspace to Spark's literal parser, so the first
AllTheBacteria/ENA probe (`runs/20261017T012405Z-atb-ena-probe`) found 15 hits in
2.76M rows. Added `sql_re()` in `src/ww_flags.py` and re-ran; the superseding
run finds 10.9k AllTheBacteria isolates and ~45k ENA samples with wastewater
wording. Also hit an HTTP 413 from the Spark Connect ingress when uploading the
~10k-row external label table; chunked the upload.
→ [pitfalls](memories/pitfalls.md)
→ [run](runs/20261017T012724Z-atb-ena-probe/run.json)

## 2026-10-17 · ! BioSample crosstab re-run with word-bounded regexes
Re-ran the BioSample evidence crosstab with the shared `ww_flags` patterns and
added trap counters (bounded vs unbounded `septic`, `sewer`; medical `effluent`).
Headline numbers barely moved (keyword hits 568.9k → 556.0k), but the unbounded
patterns had been matching ~2.2k bacterial taxon names (`bronchiseptica`,
`septicum`) and ~350 `sewerzowii` plant records. Supersedes the first run.
→ [run](runs/20261017T012956Z-biosample-evidence/run.json)

## 2026-10-17 · external wastewater labels joined to BioSample
Built the GOLD → NCBI bridge through sequencing projects (5,998 GOLD wastewater
biosamples, 5,391 with an NCBI accession), took the 4,352 MGnify wastewater-biome
samples, and the 201 NMDC biosamples with wastewater ecosystem path or ENVO term.
Joined all 9,390 distinct accessions to BioSample and measured how often each
evidence channel agrees, per source and subtype, plus the most common field
values per external subtype (the transferable vocabulary) and the values seen on
the 1,117 externally labelled samples with no BioSample wastewater signal at all.
→ [run](runs/20261017T013332Z-external-vs-biosample/run.json)

## 2026-10-17 · transfer tested and screened
Mined 242 terms from the externally labelled samples using enrichment against
exact-value background frequencies in `content_pairs_aggregated`. Applied to all
of BioSample they hit 148,289 records, 83,955 with no native signal — but
inspection showed the bulk of that gain is inherited error from MGnify's
mislabelled agricultural and industrial wastewater biomes (16,920 mallard duck
records, 10,343 riverine metagenome). Added a screen on evidence independent of
the term's own text (package, ENVO, BioProject co-membership), which rejects 133
of 242 terms and removes 51,610 of the spurious additions. Cross-source hold-out
showed the honest ceiling: on samples with no native signal, transferred
vocabulary recovers only ~2%.
→ [run](runs/20261017T014030Z-transfer-validate/run.json)
→ [run](runs/20261017T014428Z-term-screen/run.json)

## 2026-10-17 · findings synthesized
Ten findings written up. The headline is negative and worth stating plainly:
simple vocabulary transfer does not solve the hard cases, and unscreened it
amplifies the source system's labelling errors. What does work is a bounded
review of a ranked term table plus three label-free diagnostics (cross-source
hold-out, BioProject coherence against the package reference curve, trap sets).
Discarded the framing that BioSample is merely "thin" relative to the curated
systems: a third of the disagreement is the external label being wrong.
→ [REPORT.md](REPORT.md)
→ [fig](figures/fig_transfer_screen.png) ×4

## 2026-10-17 · review completed
Independent review of REPORT.md via the managed child, run
`e12111a3e4f947bda5dbfa906cc8e1c7`, target harness `claude`. Limitation worth
recording: Codex had no subscription login and OpenCode was not installed, so the
reviewer ran on the same provider as the author session. That is weaker than a
cross-provider review and no substitute target was chosen silently.
The review verified every cited run exited 0, output hashes still match disk, and
no cited number comes from a superseded run. It raised five corrections affecting
stated numbers.
→ [REVIEW_1.md](REVIEW_1.md)

## 2026-10-17 · ! report corrected after review
Verified all five of the review's corrections against the run outputs before
accepting any of them; all five held. Finding 10 mixed denominators (typed
subtypes 211,045 over 685,692 is 30.8%, not the 21% stated against a 601,863
native-only base). Finding 6 blamed GOLD's weak industrial support on acid mine
drainage; the 235 unsupported records are actually 146 unclassified industrial,
35 mine water, 30 hospital, 15 poultry, 9 AMD, and the 79 AMD records belong to
MGnify's Mine water biome instead. "aviary" is an `env_local_scale` value, not
`env_broad_scale`. The hold-out leaked 589 doubly-labelled accessions; clean
numbers are 50.0% and 14.4% overall and 1.2% / 0.5% on no-native-signal samples,
with 0.0% in every GOLD group above three samples — which makes the negative
result cleaner than first written. The screen's ENVO leg is circular for `env_*`
terms: 81 of 109 accepts clear on package support, 26 on ENVO alone (21 of those
`env_*`), 2 on BioProject alone. Also narrowed the MGnify mislabelling claim to
study level with alternative readings, traced the field population counts to a
run, corrected the keyword channel from 17 to 15 fields, and retitled findings 1,
7, 8 and 9 so headings cannot be quoted against the body.
REVIEW_1.md is now stale: REPORT.md changed, so its report hash no longer matches.
→ [run](runs/20261017T020823Z-review-checks/run.json)
→ [REPORT.md](REPORT.md)

## 2026-10-23 · report revised to v2.2
Six requested wording and traceability edits. Re-derived every number they touch
first (`runs/20261023T142719Z-v22-checks`): the 38% riverine share and all nine
per-term support rates quoted in finding 8 were already correct and are
unchanged; the duck-sample field attribution was wrong, since "water trough",
"water line" and "duck cecum" are `env_broad_scale` values while only "barn" and
"aviary" are `env_local_scale`. Renamed the screen's measure from "independent
support" to "corroborating support" everywhere, because the report's own finding
8 said the ENVO leg is circular for `env_*` terms and the old name contradicted
that. Brought three sentences into line with finding 6's position that the
disputed external groups cannot be adjudicated. Defined the previously bare
"50-to-1 amplification" where it is used (338 samples in BioProject PRJEB11269
to 16,920 matched records). Stopped attributing the 729-versus-850 gap to the
wider field set, which nothing measured. Regenerated the figures for the renamed
axis label and a figure title that still said "mislabelled"; no plotted value
changed. Left `src/04b_term_screen.py` untouched so finding 8's run record stays
valid, and said so in the revision entry.
→ [run](runs/20261023T142719Z-v22-checks/run.json)
→ [run](runs/20261023T142939Z-figures/run.json)
→ [REPORT.md](REPORT.md)

## 2026-10-23 · ! report revised to v2.3 after second review
Applied REVIEW_2 suggestions 1-10; skipped 11 on request. Two needed fresh
computation (`runs/20261023T145016Z-v23-checks`). The substantive correction is
that finding 9 misread its own output: the coherence query sums project sizes,
so the "303,334 keyword-flagged samples" were really 303,334 samples in
low-coherence projects of which only 7,106 are flagged. Restated the diagnostic
on flagged samples, where the ranking holds and is cleaner (package 98.2%,
keyword 94.2%, terms 85.4%). Carried finding 6's hedge into findings 7 and 8 and
discovery bullet 2 by rebuilding the propagation argument on target-side
evidence that needs no claim about MGnify's intent. Separated out
`bioreactor metagenome`: it comes from a GOLD group this project chose to
include and the screen accepts it, so ~30k of the apparent gain was this
project's own inclusion decision misattributed to source error. Also found the
Limitations' claim that the lift distortions change no accepted term was
asserted rather than computed, and false: 3 of 242 terms drop under an
accession-based numerator.
→ [run](runs/20261023T145016Z-v23-checks/run.json)
→ [REPORT.md](REPORT.md)

## 2026-10-23 · ! report revised to v2.4 after third review
Applied REVIEW_3 suggestions 1-7; skipped 8 on request. Two of the attributions
I introduced in v2.3 were wrong and are corrected: `biofilter metagenome` is an
MGnify nutrient-removal term the screen rejects, not a GOLD term it keeps, and
the 1,283 chicken records survive screening rather than being rejected, which
inverted the point they were used to make. Replaced finding 7's illustrative
two-way split with a counted three-class breakdown of all 83,955 records
(35,288 disputed-group idiom, 16,668 other rejected terms, 31,789 terms the
screen keeps, 210 mixed). Tracking the chicken records to their carrier turned
the correction into a finding: `env_local_scale = anaerobic`, accepted at 32.4%
support because it is apt in its home nutrient-removal cohort, matches 2,886
BioSample records including all 1,283 chicken-gut samples. That is the screen's
failure mode made concrete, and it now sits in finding 8 and discovery bullet 2
in place of the claim that the screen rejects this material cleanly. The
study-overlap query never excluded the 589 doubly-labelled accessions, so 840
and 835 were upper bounds; the true residual is 31 and 1, and the leak can only
inflate recovery, making the headline figures upper bounds.
→ [run](runs/20261023T150640Z-v24-checks/run.json)
→ [REPORT.md](REPORT.md)

## 2026-10-23 · ! report revised to v2.5 after fourth review
REVIEW_4 was the first by a different model (claude-opus-5) and found that the
v2.4 overlap fix was wrong too. 31 and 1 measured a design never run: the
exclusion of the 589 doubly-labelled accessions was test-side only, while both
term tables were mined from all of their own source's accessions. The residual
that applies is 251 and 246. Both earlier figures are now named as wrong rather
than quietly replaced. The review also caught that `fig_transfer_screen.png`
still carried the title v2.4 existed to retract, which three same-model rounds
had missed; the figure is retitled and all four regenerated with tight bounding
boxes. Applied the other eight suggestions: finding 7's heading now matches its
body, the class table gains its hierarchical-partition and boundary caveats,
class 3 reconciles with finding 8's 51,610, the keyword baseline drops from 14
fields to the ten actually used, finding 4 gains the taxonomy near-tautology
caveat, the mine-water parenthetical no longer relabels a lineage, and the
MGnify cohort is recorded as ~108 short of what the API advertised.
→ [run](runs/20261023T155021Z-figures/run.json)
→ [REPORT.md](REPORT.md)

## 2026-10-23 · ! approved by 0000-0001-9076-6066 → complete
Approved the v2.5 report as complete and cleared it for lakehouse upload.
The project concludes that BioSample's four wastewater evidence channels are
non-nested, that the ENVO closure is the channel that agrees best with the
others, that mined vocabulary recovers essentially no records beyond a generic
keyword regex across studies, that corroborating-support screening removes
most but not all over-generalised idiom, and that subtype assignment should be
multi-label. All ten findings are exploratory; there was no pre-registered
plan. Caveat accepted at approval: REVIEW_5 was a numbers-only verification of
v2.5 by a second model; the last full design review (REVIEW_4) was on v2.4, and
its suggestions were applied in v2.5 without a further full review.
→ [REPORT.md](REPORT.md)
→ [REVIEW.md](REVIEW.md) (copy of [REVIEW_5.md](REVIEW_5.md))
