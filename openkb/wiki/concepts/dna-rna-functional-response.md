---
type: "Concept"
sources: ["summaries/harvard_forest_warming__REPORT.md"]
description: "Chronic warming can produce comparable DNA and RNA functional shifts."
---

# DNA and RNA Functional Responses to Chronic Warming

## Core Idea

DNA and RNA provide complementary views of microbial functional response: DNA reflects the distribution and persistence of functional gene content, whereas RNA reflects the composition of the actively represented transcript pool. The Harvard Forest long-term warming study tested whether RNA would respond more strongly than DNA to chronic +5°C soil warming and found comparable treatment-associated variation after accounting for a horizon-by-incubation confound. [src: harvard_forest_warming]

This result concerns the [[concepts/multi-omics-integration]] of functional gene pools rather than a direct comparison of quantitative gene expression. The RNA data were based on contig-level KO annotation counts, so they represent transcript-pool composition and not TPM-quantified expression. [src: harvard_forest_warming]

## Evidence from Harvard Forest

The study analyzed 42 biosamples from the [[entities/harvard-forest-long-term-warming-study]] at [[entities/harvard-forest-barre-woods]], including control and heated soils from organic and mineral horizons. The DNA cohort contained 28 samples and the RNA cohort contained 39 samples. [src: harvard_forest_warming]

In a paired subset of 25 samples, treatment appeared stronger in DNA than RNA: DNA had PERMANOVA R²=11.9% with p=0.020, while RNA had R²=3.2% with p=0.60. However, every organic sample in this paired comparison was incubated and every mineral sample was direct, confounding horizon with incubation. [src: harvard_forest_warming]

A direct-sample sensitivity analysis reduced this confounding. Treatment R² was 12.7% for DNA in mineral soil (n=14, p=0.081), 11.4% for RNA in mineral soil (n=11, p=0.254), and 10.0% for RNA in organic soil (n=14, p=0.190). The comparable 10–13% R² values do not support the hypothesis that RNA is more warming-sensitive than DNA in this multi-decadal dataset. [src: harvard_forest_warming]

## Functional Signals

The DNA pool showed significant enrichment of heated-up carbon-cycling KOs in organic soil: 5 of 57 curated carbon-cycling hits occurred among 433 heated-up KOs, with Fisher OR=2.78 and one-sided p=0.042. No analogous FDR-significant enrichment was found in DNA mineral, RNA organic, or RNA mineral comparisons. [src: harvard_forest_warming]

The RNA pool nevertheless contained directional carbon-cycle signals. Particulate methane monooxygenase genes pmoA and pmoB, represented by [[entities/particulate-methane-monooxygenase]], increased under warming in both horizons: pmoA log2 fold changes were +0.730 in organic soil and +0.743 in mineral soil, while pmoB changes were +0.669 and +0.880, respectively. These signals had nominal p-values from 0.009 to 0.054 and did not survive correction across approximately 14,000 KOs. [src: harvard_forest_warming]

In heated mineral soil, the paired glyoxylate-cycle genes isocitrate lyase and malate synthase increased, with log2 fold changes of +0.460 and +0.268 and p=0.037 for each. The [[entities/glyoxylate-cycle]] signal is consistent with altered C2-substrate use or stress metabolism, but the report treats it as biologically directional rather than a definitive genome-wide discovery because of multiple-testing limitations. [src: harvard_forest_warming]

## Why DNA and RNA May Converge

Several explanations are consistent with the observed convergence:

1. **Long-term compositional equilibration:** After approximately 25 years of warming, genome-content turnover may have caught up with regulatory responses, reducing the expected RNA-over-DNA asymmetry. [src: harvard_forest_warming]
2. **Single-timepoint transcript variability:** RNA was sampled on one date, so short-term moisture, substrate, root-exudate, diurnal, and microspatial effects may add noise unrelated to chronic warming. [src: harvard_forest_warming]
3. **Compositional dilution:** The metatranscriptome contained 14,302 distinct KOs compared with 12,863 in the metagenome; a richer rare-organism repertoire can increase per-KO variance under relative-abundance analysis. [src: harvard_forest_warming]
4. **Broad activity suppression:** Warming-associated substrate depletion could reduce activity across many transcript categories rather than redirecting activity toward a small number of treatment-responsive functions. This interpretation connects the result to [[concepts/chronic-warming-substrate-depletion]]. [src: harvard_forest_warming]

These explanations remain hypotheses rather than independently established mechanisms in this dataset. [src: harvard_forest_warming]

## Tensions

The report's comparable DNA and RNA treatment R² values contrast with the published precedent it discusses, in which treatment had a larger effect on KEGG transcripts than on CAZyme or genome-level signals. The comparison is unresolved because the studies used different sampling timepoints, replication, and analytical pipelines. [src: harvard_forest_warming]

The apparent strength of DNA relative to RNA in the paired analysis also conflicts with the original RNA-leading hypothesis, but the report attributes that pattern primarily to the horizon × incubation confound rather than treating it as evidence that RNA is intrinsically less responsive. [src: harvard_forest_warming]

## Boundaries of Inference

The study supports comparable functional-pool separation under chronic warming, not equivalence of DNA abundance and RNA expression. The unbalanced design prevents incubation from being fully factored out of the DNA organic-horizon analysis. [src: harvard_forest_warming]

Because the experiment has one sampling date, limited replication for high-dimensional KO tests, and no quantitative metabolomics, proteomics, or in-lakehouse soil chemistry, it cannot determine whether the observed functional shifts are seasonally stable, quantitatively transcriptional, or directly caused by substrate depletion. [src: harvard_forest_warming]

## Open Directions

- Add quantitative metabolomics, NOM, and proteomics to test whether DNA/RNA convergence accompanies substrate depletion or altered protein production. [src: harvard_forest_warming]
- Repeat DNA–RNA comparisons across seasons and matched direct samples to separate chronic warming from timepoint and incubation effects. [src: harvard_forest_warming]
- Use MAG-linked annotations to identify which organisms carry the pmoA/pmoB response and test whether it reflects lineage replacement or within-lineage activity change. [src: harvard_forest_warming]
- Compare the pmoA/pmoB and glyoxylate-cycle signals across additional warming datasets to test whether they are portable responses or site-specific signatures. [src: harvard_forest_warming]

See [[summaries/harvard_forest_warming__REPORT]] for the complete project summary.