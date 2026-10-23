# Discoveries — wastewater_evidence

<!-- [wastewater_evidence] 2026-10-23T17:11:01Z  approved-report extraction (REVIEW: REVIEW_5.md) -->

- In NCBI BioSample, the wastewater package is 67% a single COVID-era sewage
  surveillance package (`SARS-CoV-2.wwsurv.1.0`), so using the package as ground
  truth silently restricts training data to influent and raw sewage.
- Mining vocabulary from an externally labelled sample set and filtering on
  enrichment plus subtype purity does **not** stop one study's idiom being applied
  far beyond it: a homogeneous source group produces terms that are rare and pure
  and still wrong outside that group, whether or not the group's own label is.
  Corroborating-support screening catches most of this but not all: a term with
  genuine support in its home domain can over-match badly elsewhere, as
  `env_local_scale = anaerobic` does in reaching 1,283 chicken-gut records. Screening candidate terms on corroborating support catches it, but the legs of
  that measure are not equally independent: only the submitter-chosen package is
  independent of the term's text. Ontology
  annotations parsed from the same strings are circular for terms mined from
  those fields, and BioProject co-membership is independent of text but not of
  study structure.
- Within-BioProject coherence is a usable label-free **ranking** diagnostic for
  any sample-level flag over NCBI data: 98.2% of the submitter-asserted package
  channel's flagged samples sit in projects where it fires on at least 80% of
  samples, against 94.2% for a keyword channel and 85.4% for mined terms, each
  taken over that channel's own flagged samples in projects where it fired. It is a comparison, not a score, because the package reference
  is near-tautological and large mixed studies confound all three curves.
- `\b` inside a Spark SQL `RLIKE` string literal is parsed as a backspace, not a
  word boundary, so word-bounded regexes silently match almost nothing.
