# NMDC Context Audit

## Research Question
Across the BERDL lakehouse, the label "NMDC" is attached to tenants, databases, and
tables whose provenance, depth, breadth, completeness, and added value vary widely.
Does this labeling confuse BERIL users about what each resource actually contains — and
can a linked knowledge base clarify the context so users select the optimal NMDC data
earlier in their sessions (stronger conclusions, less time, less cost)?

## Status
Analysis — report drafted, awaiting `/berdl-review` and `/submit`.

## Data Collections
Audited collections: `nmdc_metadata`, `nmdc_results`, `nmdc_ncbi_biosamples`,
`nmdc_ref_data`, `kbase_nmdc_arkin`, `kbase_nmdc_mags`, `kbase_nmdc_neon`.

## Overview
An audit of every "NMDC"-labeled resource in BERDL: which are genuinely National
Microbiome Data Collaborative outputs vs. external data (NCBI, NEON, Pfam) or
other-group derivations (e.g. Arkin lab); where NMDC data is duplicated across tenants;
whether each copy is complete and current; and what value BERDL has added over
upstream NMDC. Findings are captured as a directory of Open-Knowledge-Format markdown
files (`knowledge/`) — YAML front matter, descriptive filenames, and cross-links — plus
recommendations to improve the static docs and dynamic discovery tooling.

## Quick Links
- [Research Plan](RESEARCH_PLAN.md) — hypothesis, approach, audit strategy *(TBD)*
- [Report](REPORT.md) — findings and recommendations *(TBD)*
- [Knowledge base](knowledge/) — Open-Knowledge-Format context files *(deliverable, TBD)*

## Reproduction
*TBD — add prerequisites and step-by-step instructions after the audit is complete.*

## Authors
Mark Andrew Miller — LBL — ORCID [0000-0001-9076-6066](https://orcid.org/0000-0001-9076-6066)
