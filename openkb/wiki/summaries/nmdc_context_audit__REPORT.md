---
type: "Summary"
description: "Audit showing NMDC labels conceal provenance, scale, currency, and tenant differences."
doc_type: short
full_text: "sources/nmdc_context_audit__REPORT.md"
---

# NMDC Context Audit

## Summary

This audit examines BERDL resources whose names contain `nmdc` and finds that the label is systematically overloaded across **three tenants** and **six provenance classes**. Of 20 matching database names, only **7 are real, maintained resources**; they include genuine NMDC data, external NCBI and Pfam re-hosts, Arkin Lab derivatives, NMDC-derived KBase resources, and a NEON namesake collision. The findings establish [[concepts/provenance-aware-data-discovery]] as a necessary discovery principle: a shared substring does not establish common provenance, scope, authority, or currency.

## Key findings

- Genuine NMDC resources are [[entities/nmdc-metadata]] and [[entities/nmdc-results]]; [[entities/nmdc-ncbi-biosamples]] is an NCBI BioSample mirror, and [[entities/nmdc-ref-data]] contains Pfam terms.
- NMDC-related resources are split across the `nmdc` and `kbase` tenants. `kbase.nmdc_arkin`, `kbase.nmdc_mags`, and `kbase.nmdc_neon` are therefore missed by searches limited to the `nmdc` tenant.
- The genuine NMDC biosample universe contains **16,640 samples**, whereas the co-hosted NCBI mirror contains **51,711,888 biosamples** and **756,112,544 attribute rows**—a roughly 3,000× scale trap with no naming cue.
- [[entities/nmdc-mags]] is the freshest NMDC-related resource and contains **62,346 MAGs**, while [[entities/nmdc-neon]] refers to the NSF [[entities/national-ecological-observatory-network]], not the [[entities/national-microbiome-data-collaborative]].
- Iceberg snapshot ages range from **2026-07-02** to **2026-03-09**, making [[concepts/data-currency]] important for resource selection. Snapshot `committed_at` is the only available currency signal.
- Catalog tables have no comments and databases have empty properties; static documentation lacks a valid NMDC schema entry point, and the `berdl` skill contains no NMDC-specific guidance. Inventory tooling groups by catalog prefix and does not connect `kbase.nmdc_*` resources back to NMDC.

## Interpretation

The audit infers that overloaded naming contributes to suboptimal resource selection, although it does not directly observe users making incorrect choices. Likely failures include selecting the NCBI mirror when NMDC-curated metadata is intended, overlooking the freshest MAG catalog, or attributing NEON data to NMDC. These errors can increase computational cost, waste analyst time, and weaken attribution. The evidence supports [[concepts/context-rich-catalogs]] and data provenance as safeguards.

The report does not recommend removing or relabeling co-hosted resources. NCBI data gains value from BERDL attribute harmonization, and Arkin-derived products add embeddings and traits. The proposed solution is to expose provenance, authority, scope, value added, and currency together during discovery.

## Operational details

- Iceberg metadata makes row counts cheap, including the **1.83B-row** `nmdc.results.annotation_kegg_orthology` table.
- `DESCRIBE DATABASE EXTENDED` may be forbidden even when table reads and counts succeed, demonstrating different access surfaces for metadata and data.
- `get_databases()` returns both dotted Iceberg aliases and underscore Hive aliases; inventory code must deduplicate these forms.
- The audit supplies a seven-resource landscape table, naming-cruft inventory, provenance probes, figures, and a 15-file knowledge base with a decision guide.

## Recommendations and open directions

The proposed fixes are to repair the missing NMDC schema link, add an NMDC module to the `berdl` skill, cross-link the two tenant homes, expose snapshot currency in inventory output, correct provenance-blur labels, mention NMDC in top-level documentation, and remove or repair broken aliases and test databases.

Future work should measure whether these changes improve resource selection, extend provenance auditing to other overloaded BERDL labels, and compare BERDL snapshots with live upstream counts to quantify completeness lag. A broader next analysis is to combine inventory metadata with project usage patterns to test whether provenance-aware discovery changes selection behavior.

## Related Concepts
- [[concepts/coverage-limited-inference]]
- [[concepts/evidence-triangulation]]
- [[concepts/cultivation-bias]]

## Entities
- [[entities/fitness-browser]]
- [[entities/gtdb]]
- [[entities/kegg]]
