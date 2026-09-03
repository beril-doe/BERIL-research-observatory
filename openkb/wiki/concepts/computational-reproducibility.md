---
type: "Concept"
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/soil_frontier_genomics__REPORT.md", "summaries/snipe_defense_system__REPORT.md", "summaries/prophage_amr_comobilization__REPORT.md", "summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/pitfalls.md"]
description: "Practices that make BERDL analyses auditable, rerunnable, and trustworthy."
---

# Computational Reproducibility

Computational reproducibility is the preservation of the code, data transformations, execution context, outputs, and provenance needed for another researcher to audit or rerun an analysis. In the BERDL workflow, reproducibility is not achieved merely by committing final TSVs or figures: the notebooks, identifiers, database-resolution logic, intermediate artifacts, and analysis decisions must also be recoverable. [src: pitfalls]

## Core Principle

A result is computationally reproducible when its provenance is executable and inspectable: reviewers can identify which source tables were queried, how records were filtered and joined, which transformations produced each output, and whether the recorded execution actually generated the reported artifacts. This connects computational reproducibility to [[concepts/provenance-aware-data-discovery]], [[concepts/evidence-triangulation]], and [[concepts/adversarial-methodological-review]]. [src: pitfalls]

## BERDL-Specific Requirements

### Resolve data sources at execution time

BERDL collections are migrating from Delta underscore namespaces to dotted Iceberg namespaces. Because migration is ongoing, analysis code should use live, access-aware catalog discovery rather than assuming that either naming convention is universally correct. The resolved table address and tenant should be recorded with the analysis provenance. [src: pitfalls]

Database and schema assumptions also require explicit verification. Important examples include string-typed numeric columns, reserved SQL column names, identifier-prefix differences, EAV-formatted environmental metadata, and multiple rows per genome-pathway pair in GapMind. A reproducible workflow checks these assumptions with schema inspection and validation queries before producing biological results. [src: pitfalls]

### Preserve the executable analysis record

Notebooks referenced in a project README, research plan, or report should exist in Git history alongside the artifacts they generate. In the documented ENIGMA project, NB08, NB09, and NB10 had initially existed only as outputs from interactive sessions; reconstructing them later was possible but more expensive and left a provenance distinction between the interactive original and the reproducible rerun. [src: pitfalls]

Notebook outputs are part of the audit trail. Committing notebooks with empty output cells prevents reviewers from checking reported values without rerunning the analysis. Conversely, `jupyter nbconvert --inplace` may execute successfully while silently leaving zero outputs; writing to a separate executed notebook or capturing standalone script logs is safer. [src: pitfalls]

Programmatic notebook editing also requires structural validation because edited code cells can lack required `outputs` and `execution_count` fields, causing execution or notebook validation to fail. [src: pitfalls]

### Make long analyses restartable

Long BERDL jobs should be designed around checkpoints, intermediate Parquet or TSV outputs, and recovery scripts. JupyterHub kernels may be silently killed after approximately 17–25 minutes without user activity, while large Spark jobs can run for much longer. Converting long notebooks to unbuffered Python scripts, running them with `nohup`, logging stdout/stderr, and saving each completed stage prevents a single interruption from invalidating the entire analysis. [src: pitfalls]

Spark Connect reconnections can also destroy temporary views created earlier in a notebook. Re-registering temporary views immediately before joins, or avoiding temporary-view dependence by using persistent table names and SQL subqueries, makes execution less sensitive to session state. [src: pitfalls]

### Preserve independent analysis modes

Sensitivity analyses must be independently constructed. Copying strict features into a relaxed feature set produces numerically identical downstream results and makes any apparent mapping-mode comparison invalid. A reproducible sensitivity analysis precomputes shared inputs where appropriate but derives each mode independently and records the distinction in the report. [src: pitfalls]

The same principle applies to statistical validation: analyses that cluster on the same taxa later tested for differential abundance require held-out-feature, leave-one-feature-out, or independent-design checks. In the cited ecotype analysis, independent within-substudy evidence reduced a 33-species candidate list to 3 robust candidates, demonstrating why reproducibility includes preserving diagnostic analyses rather than only the preferred final result. [src: pitfalls]

## Data and Identifier Provenance

Cross-database joins should record the identifier normalization and validation rules used. Short ENIGMA strain names produced 12 incorrect genus linkages among 32 pangenome linkages, whereas assembly accession matching is less ambiguous. MetaPhlAn3 cross-cohort integration similarly requires format normalization and a synonymy layer because legacy and modern taxon names can otherwise create artificial abundance contrasts. [src: pitfalls]

A reproducible integration therefore records:

- the original identifier and source table;
- the canonical identifier and any stripped or added prefixes;
- the database or taxonomy version;
- the matching rule and fallback order;
- the number of matched, unmatched, rejected, and ambiguous records; and
- validation checks such as genus consistency or expected key overlap. [src: pitfalls]

These practices support [[concepts/identifier-resolution-and-crosswalks]], [[concepts/pangenome-integration]], and [[concepts/data-currency]]. [src: pitfalls]

## Scale-Aware Reproducibility

Reproducibility must include an execution strategy that can complete within available memory, result-size, and session limits. The pitfalls document recommends keeping filtering, joins, and aggregation in Spark; using `.toPandas()` only for small final results; staging oversized results through MinIO or Parquet; and avoiding row-wise pandas operations, large Cartesian merges, and unnecessary `explode()` calls. [src: pitfalls]

Configuration choices should also be recorded because they can change runtime behavior. Disabling Spark automatic broadcast joins caused a large join to hang even though the small side was suitable for broadcasting. Reproducible performance therefore requires documenting relevant Spark settings, broadcast hints, batching choices, timeouts, and checkpoint locations rather than treating them as incidental environment details. [src: pitfalls]

This operational dimension is part of [[concepts/scalable-spark-data-analysis]] and [[concepts/coverage-limited-inference]]: a result that cannot be rerun because it exceeds driver memory or serialized-result limits is not practically reproducible. [src: pitfalls]

## Reporting and Review

The final report should distinguish interactive exploratory values from values regenerated by committed code, document notebook reconstruction when it occurs, and link outputs to their generating scripts or notebooks. Detailed findings belong in `REPORT.md`, while `README.md` should remain a concise overview linking to the research plan and report. [src: pitfalls]

Reviewers should be able to verify not only the final numbers but also the negative checks: missing tables, access limitations, sparse coverage, orphan records, failed joins, confounding diagnostics, and sensitivity analyses. Suppressing these details can make a project appear more certain or complete than its computational record supports. [src: pitfalls]

## Relationship to Evidence Quality

Computational reproducibility does not guarantee biological validity, but it makes validity claims testable. Reproducible identifier crosswalks expose false matches; preserved leakage checks expose selection bias; explicit coverage counts expose unsupported generalization; and committed notebooks allow reviewers to inspect the exact transformations behind reported statistics. These practices strengthen [[concepts/evidence-triangulation]], [[concepts/coverage-limited-inference]], and [[concepts/phenotype-resolution-matching]]. [src: pitfalls]

## Open Directions

- Build a BERDL provenance template that records resolved namespaces, tenant, table schemas, query text, database versions, identifier mappings, and row-count checks for every analysis stage. This would reduce failures caused by migration, schema drift, and ambiguous joins. [src: pitfalls]
- Add automated pre-submission checks that verify every referenced notebook exists in Git history, executed notebooks contain outputs, and report-linked artifacts are present. This would close the documented gap between claimed and actual reproducibility. [src: pitfalls]
- Develop a reusable checkpoint-and-recovery framework for Spark Connect analyses that detects lost temporary views, session restarts, result-size risks, and JupyterHub idle termination before they invalidate long jobs. [src: pitfalls]
- Add standard validation reports for cross-database joins, including overlap, duplicate-key, rejected-match, and taxonomy-consistency statistics. This would make identifier-resolution uncertainty explicit before downstream biological interpretation. [src: pitfalls]

See [[summaries/pitfalls]] for the complete catalog of BERDL database, statistical-design, scaling, and workflow failure modes.

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]

See also: [[summaries/prophage_amr_comobilization__REPORT]]

See also: [[summaries/snipe_defense_system__REPORT]]

See also: [[summaries/soil_frontier_genomics__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]