# Research Plan: Price/Fitness Browser Gene Annotation Benchmark

## Goal

Build a benchmark package for the KBase gene annotation agent that contains:

- genes with trusted Price/Fitness Browser improved annotations;
- genes with strong RB-TnSeq evidence but no reported improved annotation;
- blinded human curation outcomes that decide whether the frozen evidence
  supports a specific function, a general function, weak family/fold evidence,
  no useful hypothesis, the existing annotation, or an artifact call.

## Why BERIL

The benchmark denominator should be computed from BERDL rather than by
re-running large local all-vs-all searches whenever possible. BERDL is expected
to provide:

| Collection | Role |
| --- | --- |
| `kescience_fitnessbrowser` | reported positives, strong-fitness denominator, cofitness, neighborhoods |
| `kescience_paperblast` | paper evidence for each candidate |
| `kescience_interpro` | InterPro and GO evidence |
| `kbase_ke_pangenome` | pangenome conservation and cluster-level annotations |

## Backend-Compatibility Gate

The historical local workflow used Spark SQL against BERDL collections whose
storage path was backed by MinIO/Delta. Because the lakehouse infrastructure is
expected to have changed, the first notebook or script must be a smoke test
that answers:

1. Does authentication work?
2. Which SQL catalogs are visible?
3. Which namespace contains each required collection?
4. Did table names or key columns change?
5. Are numeric Fitness Browser fields typed as strings or numerics now?

Do not tune candidate SQL until table discovery succeeds on the current
backend.

## Candidate Sets

1. `price_reported_positive`: union of frozen local Price positives and live
   Fitness Browser `reannotation` / `reannotationec` tables.
2. `fitness_strong_gene`: all Fitness Browser genes that pass the current
   multi-condition RB-TnSeq effect threshold.
3. `unreported_strong_fitness`: anti-join of strong-fitness genes against
   reported positives.
4. `pilot_120`: blinded sample with positives, rich-evidence unreported
   candidates, and sparse/conflicting unreported candidates.

## Label Semantics

Absence from a reannotation table is not a no-call label.

The candidate table should preserve a Price/Fitness Browser provenance field:

```text
reported_positive
not_reported
price_reviewed_no_update
unknown
```

The training/evaluation target should come from a separate blinded project
curation field:

```text
specific_function
general_function
weak_family_or_fold
still_unresolved
keep_existing_annotation
artifact_or_bad_candidate
```

`price_reviewed_no_update` requires an explicit Morgan Price audit trail for a
specific locus. `not_reported` by itself is only an anti-join result.

## First Deliverables

1. BERDL smoke-test results with current table identifiers.
2. A first `price_reported_positive` import.
3. The strong-fitness denominator SQL.
4. SQLite candidate and curation tables in `gene-annotation-agent`.
5. A blinded Candidate Queue in `gene-agent-data-viz`.
6. A 120-gene pilot manifest ready for curation.
