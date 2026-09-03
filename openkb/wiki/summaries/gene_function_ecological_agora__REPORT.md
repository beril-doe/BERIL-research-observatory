---
type: "Summary"
description: "GTDB-scale atlas links microbial gene innovation, acquisition depth, ecology, and phenotype."
doc_type: short
full_text: "sources/gene_function_ecological_agora__REPORT.md"
---

# Gene Function Ecological Agora

## Summary

This report presents a GTDB-r214-scale atlas of bacterial gene innovation and acquisition. It analyzes 18,989 species representatives and 13,062 KOs using a per-rank **Producer × Participation** framework, Sankoff parsimony, M22 acquisition-depth attribution, ecological metadata, BacDive phenotypes, AlphaEarth environmental embeddings, and mobile-genetic-element (MGE) context. The project closes four phases plus synthesis with 13.7 million rank–clade–KO atlas scores and 17.1 million inferred gain events.

The central methodological contribution is a tree-aware framework for distinguishing clade-specific paralog expansion from cross-clade acquisition. It classifies tuples as **Innovator-Isolated**, **Innovator-Exchange**, **Sink/Broker-Exchange**, or **Stable**, while reporting acquisition depth from recent genus-level gains to ancient phylum-level gains. The framework also introduces annotation-density residualization, [[concepts/leaf-consistency]] as a within-clade uncertainty measure, and exploratory tree-based donor inference at genus rank.

## Main findings

- **Mycobacteriaceae and mycolic-acid functions:** The pre-registered Innovator-Isolated hypothesis is supported at family rank, with producer Cohen’s *d* = +0.31 and consumer *d* = −0.19. The signal is strongest in a mycolate-positive sub-clade of 10 of 13 genera, where producer *d* rises to +0.394, while consumer evidence weakens at genus rank. [[entities/mycobacteriaceae]] is enriched 7.88× in host-pathogen-associated environments (*p* < 10⁻⁴⁵), and BacDive profiles show aerobic, rod-shaped, largely non-motile, catalase-associated phenotypes.

- **Cyanobacteriia and photosystem II (PSII):** The PSII Innovator-Exchange hypothesis is supported specifically at class rank, with producer *d* = +1.50 and consumer *d* = +0.70. Finer ranks are stable because PSII is broadly shared within Cyanobacteria rather than repeatedly innovated within individual genera. Cyanobacteriia is enriched 2.77× in photic aquatic environments (*p* < 10⁻⁵²), and PSII has a high leaf-consistency value of 0.88, consistent with a class-defining innovation and a Cyanobacteria-associated donor-origin signal.

- **Bacteroidota and polysaccharide-utilization loci (PULs):** The original absolute-zero Innovator-Exchange criterion is falsified at UniRef50 resolution. A Sankoff diagnostic nevertheless recovers a small HGT-direction signal (*d* ≈ 0.15), and Bacteroidota CAZymes are modestly less clumped than housekeeping controls. Ecology and phenotype are consistent with the functional context: [[entities/bacteroidota]] is enriched 1.40× in gut/rumen environments (*p* < 10⁻³⁵), with saccharolytic and glycoside-hydrolase-rich BacDive profiles. The result supports a qualified, resolution-dependent interpretation rather than the original strong hypothesis.

- **Regulatory versus metabolic functions:** The strong-form asymmetry hypothesis is not supported: effects remain below *d* = 0.3. Regulatory KOs are more phylogenetically clumped than metabolic KOs (consumer *d* = −0.211), matching the direction predicted by the complexity hypothesis of Jain et al. and independently supported by Burch et al. The strongest exchange enrichment occurs instead in mixed regulatory–metabolic KOs, whose Innovator-Exchange rate is 0.57%, approximately twice that of pure regulatory or metabolic KOs.

- **Acquisition-depth signatures:** Recent-to-ancient gain ratios distinguish function classes. CRISPR-Cas has a 24.5× ratio, TCS histidine kinases 10.3×, β-lactamases 9.0×, and tRNA synthetases 2.3×. Strict housekeeping classes show high leaf consistency, whereas HGT-associated classes are patchier and more recent-skewed. These results motivate [[concepts/acquisition-depth-signatures]] and connect the atlas to [[concepts/horizontal-gene-transfer]].

- **Architectural promiscuity:** Mixed-category KOs show a median of 46 Pfam architectures per KO, compared with 15 for TCS histidine kinases, 5 for mycolic-acid KOs, and 1 for PSII. This exploratory result suggests that structural modularity may facilitate cross-clade exchange, connecting the atlas to [[concepts/structural-novelty]]. KO-to-architecture concordance is mixed: consumer-side correlation is *r* = 0.67, while producer-side correlation is only *r* = 0.09.

- **MGE context:** Pre-registered PSII, PUL, and mycolic-acid KOs are not themselves enriched in MGE machinery. Their MGE-machinery fractions are 0%, 0%, and 0.57%, respectively, versus an atlas baseline of 1.37%. PSII gene-neighborhood analysis finds 10.91% of focal features adjacent to MGE machinery, essentially equal to the 10.6% Poisson baseline. PUL and mycolic gene-neighborhood scans were deferred because of scale-related memory failures, so the non-cargo conclusion is strongest for PSII and machinery-level evidence. This result contributes to [[concepts/mobile-genetic-elements]] and [[concepts/gene-neighborhood-inference]].

- **Pangenome openness:** P4-D4 finds no atlas-wide relationship between within-species pangenome openness and M22 recent gains (Spearman *r* = −0.011 across 894 genera). This informative null separates within-species strain diversity from between-species lineage-level acquisition, establishing a distinction relevant to [[concepts/pangenome-integration]].

- **Alm 2006 reproduction:** The reported *r* ≈ 0.74 relationship between histidine-kinase abundance and recent lineage-specific expansion is not reproduced at full GTDB scale. Four framings yield *r* = 0.10–0.29 across 18,989 species. The qualitative recent-skew and consumer-side architectural relationship persist, but the quantitative point estimate does not. The report attributes dilution to taxonomic breadth, differences between per-genome paralog counts and Sankoff gains, and rank granularity.

## Bias control and statistical discipline

D2 annotation-density residualization finds no producer-side association with nuisance covariates (R² = 0.000) and only a small consumer-side association (R² = 0.053). All major hypothesis directions and verdicts survive residualization. A later multiple-testing pass finds that 14 of 16 formal tests survive family-wise Bonferroni correction; the two failures are already-reported null results: Mycobacteriaceae–soil enrichment and the NB11 producer comparison. Leaf consistency and M26 donor labels are treated as descriptive or exploratory rather than hypothesis tests.

The project documents repeated diagnostic corrections rather than treating every methodology revision as a new hypothesis test. Key lessons include: audit annotation substrates before analysis; calibrate thresholds against biological controls; close-read foundational papers; use cheap targeted diagnostics before changing methodology; and distinguish descriptive atlas patterns from pre-registered hypothesis tests. These practices connect with [[concepts/annotation-gap]], [[concepts/method-concordance]], and [[concepts/evidence-triangulation]].

## Limitations

The atlas does not identify donors at deep ranks, perform full DTL reconciliation, or provide cross-phase error propagation. Composition-based donor inference was unavailable because per-CDS sequence data were not queryable. M26 tree-based donor labels are exploratory and algebraically favor Open-Innovator classifications. PSII evidence is class-rank-specific and based on 21 PSII KOs at that rank; Cyanobacteria phenotype coverage is too thin for a strong BacDive anchor. PUL and mycolic gene-neighborhood analyses remain scale-bounded, and ecological enrichment demonstrates association with expected environments rather than causation. These constraints reflect [[concepts/coverage-limited-inference]] and [[concepts/phylogenetic-confounding]].

## Reusable concepts

- [[concepts/producer-participation-framework]] — Direction-agnostic Innovator-Isolated, Innovator-Exchange, Sink/Broker, and Stable classifications.
- [[concepts/acquisition-depth-signatures]] — Function-class differences in recent versus ancient Sankoff gains.
- [[concepts/leaf-consistency]] — Within-clade prevalence as an uncertainty and heterogeneity measure.
- [[concepts/horizontal-gene-transfer]] — Tree-aware inference and function-class patterns of gene acquisition.
- [[concepts/evidence-triangulation]] — Combining atlas effects, ecological consistency, and phenotype anchors.
- [[concepts/genome-ecology-validation]] — Testing whether genomic patterns align with environmental and phenotypic distributions.
- [[concepts/mobile-genetic-elements]] — MGE-machinery and cargo-context analysis for transferred functions.
- [[concepts/gene-neighborhood-inference]] — Genome-context analysis of possible MGE cargo.
- [[concepts/annotation-gap]] — Annotation-related bias and the need to audit functional substrates.
- [[concepts/method-concordance]] — Agreement and disagreement across UniRef, KO, Pfam, and tree-based measurements.
- [[concepts/structural-novelty]] — The exploratory relationship between Pfam architectural diversity and exchange propensity.
- [[concepts/pangenome-integration]] — Distinguishing within-species pangenome diversity from between-species acquisition.

## Key project artifacts

- `data/p4_deep_rank_pp_atlas.parquet` — 13.74M rank–clade–KO Producer × Participation records.
- `data/p4_per_event_uncertainty.parquet` — 17.07M gain events with acquisition depth and leaf consistency.
- `data/p4d5_residualized_atlas.parquet` — Atlas scores after D2 residualization.
- `data/p4_genus_rank_quadrants_tree_proxy.tsv` — Exploratory M26 genus-level donor-proxy classifications.
- `data/p4_multiple_testing_correction_summary.tsv` — Formal test-family correction results.

Overall, the report concludes that the atlas is methodologically defensible and biologically interpretable when claims are kept resolution-specific. Two major hypotheses are supported, the Bacteroidota claim is qualified rather than accepted in its original form, the regulatory/metabolic claim is reframed toward the complexity hypothesis, and the Alm 2006 numerical reproduction is honestly rejected while its qualitative methodological influence remains.

## Related Concepts
- [[concepts/two-speed-genome]]
- [[concepts/organism-specificity]]
- [[concepts/cultivation-bias]]
- [[concepts/adversarial-methodological-review]]
- [[concepts/prevalence-ceiling]]

## Entities
- [[entities/mycobacterium-tuberculosis]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/eggnog]]
- [[entities/uniprot]]
- [[entities/average-nucleotide-identity]]
