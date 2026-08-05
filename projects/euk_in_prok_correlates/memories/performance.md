# Performance Notes — euk_in_prok_correlates

<!-- [euk_in_prok_correlates] 2026-07-10T16:07:02Z  approved-report extraction (REVIEW: REVIEW_3.md) -->

- The read-based taxonomy tables are large (`kraken2_classification_report` ~29M rows). Aggregate each
  classifier to one row per `workflow_run_id` **before** joining to metadata; never scan them unfiltered.
- Analyse at the **`workflow_run_id`** level, not biosample level: NMDC pools many biosamples into one
  ReadbasedAnalysis run (1,067/2,759 runs are pooled), so biosample-level joins inflate n via pseudo-replication.
- The native `nmdc.results` tables are keyed by `data_object_id` / `workflow_run_id`; bridge to biosample/study
  via `nmdc.metadata.biosample_to_workflow_run` (join on `workflow_run_id`), then
  `biosample_set_associated_studies` (child tables key on `parent_id`). This links 99%+ of classified runs.
