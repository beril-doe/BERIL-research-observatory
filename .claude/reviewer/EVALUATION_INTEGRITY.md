# Evaluation Integrity checklist

The single source of truth for the silent failures that make a result look better
than it is. Referenced by the project reviewer (`SYSTEM_PROMPT.md`), the plan
reviewer (`PLAN_REVIEW_PROMPT.md`), and the refutation pass (`REFUTATION_PROMPT.md`)
so the criteria live in **one** place.

Anchored to the leakage taxonomy of Kapoor & Narayanan, *"Leakage and the
reproducibility crisis in machine-learning-based science"* (Patterns, 2023), and
the **REFORMS** reporting checklist (Kapoor et al., 2024). These failures hide in
the **numbers**, not the prose — inspect the cell `outputs` (split sizes, class
balances, the exact metric computed), name the cell/query, and state the check
that would rule each relevant failure in or out.

## Universal — apply even to plain descriptive SQL

1. **Selection bias** — non-representative subsetting, survivorship filtering, or
   dropping rows in a way that flatters the result.
2. **Metric misuse** — a metric mismatched to the question, accuracy on an
   imbalanced target, or no multiple-comparison correction / p-hacking.

## Conditional — only when the analysis trains or tunes a model or threshold

3. **Train/test leakage** — target, feature, look-ahead/temporal, or group leakage
   (related rows — same genome, taxon, or sample — straddling the split); or
   reporting performance on the same data a model/threshold was tuned on.
4. **Benchmark/baseline selection** — a cherry-picked or missing comparator, or no
   held-out set.

Most BERDL analyses are descriptive SQL with no model — **don't force a train/test
leakage hunt where nothing was fit.** If none is evident, say so briefly.

## Conditional — biology / bioinformatics analyses

Comparative-genomics / pangenome / microbiome / fitness findings have field-specific failure modes. When a finding is one of these, the single most decisive disconfirming check is usually here:

5. **Phylogenetic non-independence** (cross-genome / cross-species claim) — genomes and species are not independent samples, so a correlation or enrichment across taxa can be shared descent or one oversampled clade. Collapse to one genome per species/genus (or add a clade covariate / re-run as PGLS) and confirm the effect isn't carried by a single clade. [Felsenstein 1985, doi:10.1086/284325]
6. **Database ascertainment bias** (claim generalized to "bacteria" / "the pangenome") — sequenced genomes over-represent pathogens, model organisms, and culturable taxa. Report the taxonomic composition of the input set and re-test on a taxonomically balanced subsample (cap N per species).
7. **Annotation transfer error & circularity** (function / pathway claim) — most functional annotations are homology-propagated and a large fraction are mis-annotated; using a predicted function as evidence for that same function is circular, and paralogs get counted as orthologs. Separate experimental from inferred (IEA) annotations, restrict to well-characterized families, and confirm orthology (reciprocal-best-hit) rather than raw KO/EC membership. [Schnoes et al. 2009, doi:10.1371/journal.pcbi.1000605]
8. **Compositional artifact** (correlation / differential abundance on proportions or gene fractions) — the constant-sum constraint manufactures spurious (often negative) correlations. Recompute with a log-ratio method (CLR / ALDEx2 / ANCOM-BC) before trusting it. [Gloor et al. 2017, doi:10.3389/fmicb.2017.02224]
9. **MAG contamination / incompleteness** (gene presence/absence or low-biomass signal) — a "missing" gene may be an assembly gap and a signal may be a contaminant. Restrict to CheckM-passing genomes (>90% complete, <5% contamination) and inspect negative/blank controls. [Parks et al. 2015, doi:10.1101/gr.186072.114; Davis et al. 2018, doi:10.1186/s40168-018-0605-2]
10. **Batch confounding** (finding pooled across collections / studies) — cross-study "biology" can be a batch artifact confounded with the contrast. Re-test the effect within each collection (add study / host covariates), not just across them. [Leek et al. 2010, doi:10.1038/nrg2825]
11. **Effect size, not just significance** (any "highly significant" result at lakehouse N) — huge N makes trivial differences "significant." Require an effect magnitude + interval against a biologically meaningful threshold. [Wasserstein & Lazar 2016, doi:10.1080/00031305.2016.1154108]

The **group-leakage** subtype (item 3) most relevant to genomics is non-independent genomes or paralogs counted as independent. Multiple-testing / FDR (item 2) and held-out replication in an independent collection (item 4) apply here too.

If `projects/<id>/claims.json` is present, read it: each claim's computed
resolved artifact support and **confidence_mismatch** show where written confidence may outrun
its evidence. Corroborate against the actual cell outputs.
