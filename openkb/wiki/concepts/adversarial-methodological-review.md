---
type: "Concept"
sources: ["summaries/gene_function_ecological_agora__REPORT.md", "summaries/discoveries.md"]
description: "Adversarial review exposes structural and inferential flaws missed by routine review."
---

# Adversarial Review for Structural and Inferential Errors

Adversarial review is an explicit, flaw-seeking evaluation mode for detecting structural and inferential errors that routine review may overlook. It complements, rather than replaces, standard review: routine review is useful for documentation, reproducibility, missing sections, and straightforward statistical problems, while adversarial review examines whether the design, evidence, labels, null models, and decision rules actually support the stated conclusions. [src: discoveries]

## Core principle

High-stakes analyses should be reviewed at the level where claims become load-bearing, not only after notebooks are complete. A paired workflow uses:

1. **Standard review** to identify surface defects, undocumented dependencies, broken figures, and simple analytical mistakes.
2. **Adversarial review** to challenge feature independence, outcome-selection logic, null distributions, sample-size claims, confounder handling, and the correspondence between hypothesis labels and operational tests. [src: discoveries]

This workflow is especially relevant when results inform clinical decisions, experimental design, downstream computational work, or external communication. It strengthens [[concepts/evidence-triangulation]] by testing whether apparently convergent evidence is genuinely independent, and it supports [[concepts/method-concordance]] by distinguishing agreement caused by shared inputs from agreement produced by independent methods.

## Errors adversarial review is designed to catch

### Feature leakage and selection-on-outcome bias

A central failure mode is defining groups or features with the same variables later used to test group differences. In the IBD targeting project, samples were clustered using taxonomic abundances and the same taxa were then tested within clusters. This made within-ecotype associations vulnerable to feature leakage and compositional bias. [src: discoveries]

Repair required leaving out the test species when refitting ecotypes and validating candidates with an independent within-substudy diagnosis contrast. This is a general protection against circularity in stratified analyses and is closely related to [[concepts/phylogenetic-confounding]] and [[concepts/microbiome-ecotype-portability]].

### Missing or inappropriate null distributions

Effect-size thresholds are not self-validating. The reviewed projects contained thresholds such as Jaccard 0.14 and absolute correlation greater than 0.4 without null distributions capable of showing whether those values exceeded chance expectations. A threshold should be interpreted against a prespecified permutation, bootstrap, or other appropriate null rather than treated as intrinsically meaningful. [src: discoveries]

The corrected IBD ecotype analysis showed why this matters: the observed Jaccard value was 0.104 versus a permutation-null mean of 0.785 ± 0.054, with permutation p = 0.000. The divergence signal survived, but the original effect-size framing used the wrong reference statistic. [src: discoveries]

### Hard-coded or non-falsifiable verdict rules

Adversarial review should reconstruct the actual decision rule and ask whether random data could pass it. One IBD pathway test used a rule allowing “at most 3 of 7 categories,” but the null distribution also reached that outcome in 100% of cases, making the test structurally degenerate. A non-significant result was also incorrectly treated as resolving a biological paradox. [src: discoveries]

A structurally degenerate result is therefore a schema or design warning, not a scientific refutation. In the pathway analysis, regex matching on descriptive names hid heme and iron biology, whereas a curator-validated MetaCyc hierarchy identified iron/heme acquisition as the dominant CD-up theme with OR = 8.1 and FDR = 7e-6. [src: discoveries]

### Sample-size and scope overclaims

Review must verify sample sizes and cohort composition from the actual data rather than inherited plan language. The IBD plan overstated one analysis as involving 130 HMP2 subjects, while the relevant test had n = 67 across three sites. Another claimed four viable substudies even though the data supported only three plus a partial case. [src: discoveries]

This check is part of [[concepts/method-concordance]]: agreement across analyses is meaningful only when each analysis has the stated cohort, power, and independence.

### Confounder omission

An analysis can cite the need for confounder adjustment while implementing none. In the IBD review, the absence of confounder adjustment was identified as a critical issue because pooled disease comparisons can reflect cohort, substudy, or compositional differences rather than diagnosis. [src: discoveries]

Independent within-substudy analysis changed the interpretation of candidate species. The original 33-species Tier-A list reduced to three candidates after applying bootstrap-effect, LinDA, and confound-free meta-analytic filters; all 14 E1 candidates passing the first two filters had negative effects in the independent contrast. [src: discoveries]

### Label-versus-data mismatch

Adversarial review checks whether biological labels match the entities and measurements actually used. The IBD plan described a “butyrate-producer” analysis whose named anchors mostly were not butyrate producers. Such mismatches can make a hypothesis appear biologically specific while testing a different construct. [src: discoveries]

### Overinterpretation of predictive metrics

A classifier can perform well on an internal metric while failing the intended translation task. An IBD ecotype classifier achieved macro one-versus-rest AUC = 0.80 in pooled five-fold cross-validation, but agreement with the independent UC Davis metagenomic projection was only 41%. Because `is_ibd` was constant in the held-out cohort, the AUC partly measured healthy-versus-disease separation rather than discrimination among IBD-internal ecotypes. [src: discoveries]

Adversarial review should therefore require evaluation on an independent cohort with dominant cohort-axis variables held fixed. This is a specific application of [[concepts/microbiome-ecotype-portability]].

## Quantified consequence of review

The most direct demonstration comes from the IBD targeting project. Routine review described the work as methodologically sophisticated and recommended proceeding with the existing candidate list. An adversarial review of the same project identified five critical and six important issues, including leakage, incorrect non-significance logic, absent confounder adjustment, missing null distributions, and lack of external replication. [src: discoveries]

After rigor repair, the 33 within-ecotype Tier-A candidates became three independently supported candidates, all in E3: *Mediterraneibacter gnavus*, *Flavonifractor plautii*, and *Blautia wexlerae*. The apparent resolution of the *Clostridioides scindens* paradox was overturned: independent analysis supported CD enrichment with pooled CLR-Δ = +1.18, FDR = 1e-8, and 4/4 sign concordance. [src: discoveries]

The result illustrates that adversarial review is not merely conservative. It can preserve robust findings, redirect invalid interpretations, and identify which downstream claims remain usable. The ecotype framework remained useful for patient stratification, while the original within-ecotype candidate-selection analysis was rejected for intervention targeting. [src: discoveries]

## Scope of review

Adversarial review should occur at two linked stages:

- **Plan revision:** inspect hypotheses, operational definitions, sample-size assumptions, null models, thresholds, data availability, and planned verdict logic before notebooks are run.
- **Notebook or analysis commit:** inspect implemented joins, feature construction, exclusions, statistical tests, figures, and final prose for deviations from the plan. [src: discoveries]

The plan-stage review is cheaper because it can catch structural problems before they propagate across multiple notebooks. In the documented case, a single plan-edit review exposed issues that would otherwise have required repairing seven notebooks. [src: discoveries]

A practical workflow is to run the standard project reviewer, then ask a separate reviewer explicitly to “find flaws, do not be diplomatic,” using the plan, report, failure analysis, and relevant data-mart inspection. The outputs should be reconciled before notebook execution or final synthesis. [src: discoveries]

## Relationship to evidence triangulation

Adversarial review is a prerequisite for credible [[concepts/evidence-triangulation]]. Multiple lines of evidence are not independent merely because they have different names: clustering and downstream testing can share the same features, pathway and metabolite signals can measure different quantities, and several analyses can inherit the same cohort batch effect. Review must therefore ask:

- Does each evidence stream use independent data or only a different transformation?
- Is the null model appropriate for the sampling and feature-construction process?
- Does the result survive confounder adjustment and held-out validation?
- Does the biological label describe the measured entity?
- Are positive and negative findings interpreted symmetrically?

The same principle applies to multi-omics work, where pathway-level differential abundance and metabolite-pool differential abundance measure different biological quantities. Opposite directions need not be contradictions, but they must not be presented as redundant confirmation. [src: discoveries]

## Tensions

Routine review and adversarial review serve different purposes rather than representing mutually exclusive standards. Routine review remains appropriate for ordinary iteration and surface-quality control, while high-stakes or methodologically nuanced projects require the additional adversarial pass. [src: discoveries]

Adversarial review can also expose a tension between transparent methodology revision and multiple-testing interpretation. A documented project may contain many revisions, but revisions are not automatically hypothesis tests. In one case, the actual inferential family contained four pre-registered hypotheses; Bonferroni correction at alpha = 0.0125 left all four supported. Applying FWER correction across all methodology revisions would have treated design changes as tests and constituted a category mistake. [src: discoveries]

## Open Directions

- Develop a `--adversarial` mode for the standard BERDL review workflow that produces paired routine and flaw-seeking reports before analysis execution. [src: discoveries]
- Create a reusable checklist that verifies feature independence, sample counts, null distributions, confounders, label-data alignment, and decision rules for every load-bearing claim. [src: discoveries]
- Add automated checks for cohort-axis variables that are constant in held-out data, same-axis feature leakage, and thresholds lacking empirical null distributions. [src: discoveries]
- Require independent evidence-stream annotations in [[concepts/evidence-triangulation]] workflows so shared inputs and genuinely independent validations are distinguished explicitly. [src: discoveries]
- Benchmark whether adversarial review reduces false-positive candidate lists across clinical, ecological, and functional-genomics projects without suppressing reproducible positive findings. [src: discoveries]

See [[summaries/discoveries]] for the source log of methodological lessons and biological findings.

See also: [[summaries/gene_function_ecological_agora__REPORT]]