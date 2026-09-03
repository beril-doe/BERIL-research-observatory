---
type: "Concept"
sources: ["summaries/nmdc_context_audit__REPORT.md"]
description: "Data currency is the recency of a resource’s latest committed snapshot."
---

# Data Currency and Snapshot Freshness

## Definition

**Data currency** is the recency of a dataset’s latest committed snapshot. In the BERDL NMDC context audit, Iceberg’s `.snapshots.committed_at` timestamp is the only available signal of when a table or resource was most recently updated. [src: nmdc_context_audit] Currency is therefore a core component of [[concepts/context-rich-catalogs]] and [[concepts/provenance-aware-data-discovery]]: users need to evaluate recency alongside provenance, authority, scope, and scale rather than treating a shared resource name as sufficient context.

## Evidence from the NMDC context audit

Snapshot ages varied by approximately four months across resources labeled `nmdc`. [src: nmdc_context_audit] The freshest resources were `kbase.nmdc_mags` and `kbase.nmdc_neon`, both last committed on **2026-07-02**. [src: nmdc_context_audit] `kbase.nmdc_arkin` was last committed on **2026-05-27**, while `nmdc.metadata`, `nmdc.results`, and `nmdc.ref_data` were last committed on **2026-05-20**. [src: nmdc_context_audit] `nmdc.ncbi_biosamples` was the stalest resource, with a last commit of **2026-03-09** and an age of approximately four months at audit time. [src: nmdc_context_audit]

The audit shows why freshness cannot be inferred from tenant or name. `kbase.nmdc_mags` was the freshest NMDC-related resource even though it lived in the `kbase` tenant, outside the primary `nmdc` tenant. [src: nmdc_context_audit] Conversely, resources in the `nmdc` tenant were not uniformly current or even NMDC-produced: that tenant included the substantially older NCBI BioSample re-host. [src: nmdc_context_audit]

## Discovery implication

Freshness is invisible in the current discovery experience. Tables have no human-readable comments, databases have empty properties, and the inventory does not expose snapshot currency to users selecting a resource. [src: nmdc_context_audit] A catalog entry that reports `max(committed_at)` or equivalent latest-snapshot metadata would make currency available at discovery time. [src: nmdc_context_audit]

The audit identifies Iceberg snapshot metadata as cheap to query: row counts, including the **1.83B-row** `nmdc.results.annotation_kegg_orthology` table, return through Iceberg metadata without requiring expensive full-table scans. [src: nmdc_context_audit] This supports routinely adding scale and freshness indicators to inventory output rather than omitting them for performance reasons. [src: nmdc_context_audit]

## Interpretation and limitations

Snapshot freshness measures the recency of the BERDL-hosted resource, not necessarily its completeness relative to a live upstream authority. [src: nmdc_context_audit] The audit assessed completeness relative to snapshot timestamps and did not compare the resources with current upstream NMDC or NCBI record counts. [src: nmdc_context_audit] A recent snapshot may still lag upstream, while an older snapshot may remain appropriate for a reproducible analysis if its version is explicitly recorded.

Currency should therefore be interpreted together with provenance and authority. The audit distinguishes genuine NMDC resources from the NCBI BioSample mirror, Pfam reference data, Arkin-derived products, and the NEON namesake resource; their snapshot dates describe different products and update processes. [src: nmdc_context_audit] This is an instance of [[concepts/evidence-triangulation]]: selection should combine timestamp evidence with resource identity, provenance, and intended analytical goal.

## Open Directions

- Add the latest Iceberg `committed_at` value and snapshot age to `berdl` inventory output, then test whether users choose resources more appropriately. [src: nmdc_context_audit]
- Compare `nmdc.metadata` and `nmdc.ncbi_biosamples` snapshots with live upstream record counts to quantify completeness lag, which the audit left unresolved. [src: nmdc_context_audit]
- Record the selected snapshot identifier and timestamp in downstream analyses so results remain reproducible when resources are refreshed. [src: nmdc_context_audit]

## Related Documents
- [[summaries/nmdc_context_audit__REPORT]]
