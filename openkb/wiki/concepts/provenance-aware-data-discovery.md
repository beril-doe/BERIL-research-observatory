---
type: "Concept"
sources: ["summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/paperblast_explorer__REPORT.md", "summaries/nmdc_context_audit__REPORT.md"]
description: "Discovering data by provenance, authority, scope, and currency—not name alone."
---

# Provenance-Aware Data Discovery

## Definition

Provenance-aware data discovery treats resource provenance, authority, scope, scale, currency, and value added as first-class discovery metadata rather than inferring meaning from names or tenant placement. It complements [[concepts/context-rich-catalogs]] and [[concepts/evidence-triangulation]] by making resource identity and evidence context explicit before analysis begins.

## Why it matters

The NMDC Context Audit found that the `nmdc` label spans three tenants and six provenance classes, so a shared substring does not establish common provenance, scope, scale, or currency. Of 20 database names containing `nmdc`, only seven were real, maintained resources. [src: nmdc_context_audit]

The seven resources include genuine NMDC resources, external re-hosts from NCBI and Pfam, an Arkin Lab derivative, NMDC-derived KBase resources, and a namesake collision belonging to the National Ecological Observatory Network. [src: nmdc_context_audit] This means that name-based discovery can cause both analytical mis-scoping and incorrect attribution, connecting this concept to [[concepts/coverage-limited-inference]] and [[concepts/resource-darkness]].

## NMDC audit evidence

The `nmdc` tenant is neither exclusively NMDC nor a complete view of NMDC-related data. `nmdc.metadata` and `nmdc.results` are genuine NMDC resources, while `nmdc.ncbi_biosamples` is an NCBI BioSample harvest and `nmdc.ref_data` contains Pfam terms. [src: nmdc_context_audit] Conversely, `kbase.nmdc_arkin`, `kbase.nmdc_mags`, and `kbase.nmdc_neon` are NMDC-related or namesake resources outside the `nmdc` tenant. [src: nmdc_context_audit]

A major scale hazard is the contrast between the genuine NMDC biosample universe of **16,640 samples** and the co-hosted NCBI mirror containing **51,711,888 biosamples** and **756,112,544 attribute rows**. [src: nmdc_context_audit] Selecting by name alone could therefore place an analysis on a dataset roughly 3,000 times larger than intended, with no naming convention that signals the difference. [src: nmdc_context_audit]

The audit also identified an acronym collision: `kbase.nmdc_neon` is associated with the NSF National Ecological Observatory Network, not the DOE-BER National Microbiome Data Collaborative. [src: nmdc_context_audit] Provenance-aware discovery must therefore expose the responsible program or authority, not merely the database name.

## Currency is part of provenance context

Resource currency is another discovery dimension. The latest Iceberg snapshot dates ranged from **2026-07-02** for `kbase.nmdc_mags` and `kbase.nmdc_neon` to **2026-03-09** for `nmdc.ncbi_biosamples`; the genuine NMDC resources had last commits on **2026-05-20**. [src: nmdc_context_audit] The audit identifies Iceberg `.snapshots.committed_at` as the only available data-currency signal and recommends exposing it in inventory output. [src: nmdc_context_audit]

Currency should be shown alongside provenance rather than treated as an implicit property of a catalog. A resource can be authoritative but stale, recent but externally re-hosted, or derived and current while differing substantially from its upstream source. The NMDC audit does not resolve these distinctions by ranking resources universally; it argues that users need the context to choose appropriately. [src: nmdc_context_audit]

## Catalog and tooling gaps

The audit found no human-readable context in the lakehouse catalog: tables had no `Comment` values and databases had empty `Properties`. [src: nmdc_context_audit] Static documentation also lacked a working NMDC schema entry point, while the `berdl` skill contained no NMDC-specific guidance. [src: nmdc_context_audit]

The inventory tool grouped resources by catalog prefix, leaving `kbase.nmdc_*` resources unlinked to NMDC and failing to distinguish `kbase.nmdc_neon` from NMDC. [src: nmdc_context_audit] In addition, `get_databases()` returned both dotted Iceberg aliases and underscore Hive aliases, requiring deduplication before inventory iteration. [src: nmdc_context_audit]

These failures show that provenance-aware discovery must operate at multiple layers: catalog metadata, documentation, dynamic inventory, and user-facing decision guides. The audit’s proposed remedies are to add an NMDC documentation and tooling module, cross-link split tenant homes, surface snapshot currency, correct provenance-blur labels, and clean up broken or phantom aliases. [src: nmdc_context_audit]

## Design principles

1. **Separate name from provenance.** A matching substring should trigger investigation, not classification. [src: nmdc_context_audit]
2. **Display authority and steward.** Users should be able to distinguish NMDC, NCBI, Pfam, Arkin Lab, KBase, and NEON resources. [src: nmdc_context_audit]
3. **Expose scope and scale.** Record representative row counts and biological coverage so that similarly named resources cannot be confused silently. [src: nmdc_context_audit]
4. **Link across tenant boundaries.** Inventory views should connect related resources even when catalog prefixes differ. [src: nmdc_context_audit]
5. **Show currency at discovery time.** Iceberg snapshot commit times should be surfaced as a freshness indicator. [src: nmdc_context_audit]
6. **Describe value added without erasing origin.** Harmonization, flattening, embeddings, and other transformations should be documented while preserving upstream authority. [src: nmdc_context_audit]
7. **Make selection goal-oriented.** A decision guide should map analytical goals to resources and explicitly state join and attribution risks. [src: nmdc_context_audit]

## Tensions

### Co-hosting versus provenance clarity

Co-hosting external and derived resources with genuine NMDC data can be analytically valuable: the NCBI mirror receives attribute harmonization, and the Arkin derivative adds embeddings and traits. [src: nmdc_context_audit] However, the same arrangement becomes hazardous when catalog names and tenant browsing do not expose origin, transformation, or authority. [src: nmdc_context_audit] The appropriate resolution is not removal or blanket relabeling, but explicit provenance and value-added metadata. [src: nmdc_context_audit]

### Inferred behavior versus directly observed misuse

The audit concludes that overloaded naming is consistent with suboptimal resource selection, but the wrong choices were inferred from gap analysis and prior-project usage skew rather than directly observed user behavior. [src: nmdc_context_audit] Any claim that provenance-aware discovery reduces errors therefore remains a testable hypothesis rather than an established outcome. [src: nmdc_context_audit]

## Open Directions

- Add provenance, authority, representative scale, tenant relationships, and `committed_at` to `berdl` inventory output, then test whether users select different resources for the same analytical goals. [src: nmdc_context_audit]
- Compare project queries before and after an NMDC decision guide is deployed to measure whether users reach the intended resource faster and with fewer cross-tenant omissions. [src: nmdc_context_audit]
- Extend the seven-resource audit method to other overloaded BERDL labels and test whether the same provenance classes recur. [src: nmdc_context_audit]
- Diff `nmdc.metadata` and `nmdc.ncbi_biosamples` against their live upstream authorities to distinguish snapshot staleness from genuine completeness differences. [src: nmdc_context_audit]

## Related pages

- [[summaries/nmdc_context_audit__REPORT]]
- [[concepts/context-rich-catalogs]]
- [[concepts/data-currency]]
- [[concepts/evidence-triangulation]]
- [[entities/national-microbiome-data-collaborative]]
- [[entities/ncbi-biosample]]
- [[entities/pfam]]
- [[entities/national-ecological-observatory-network]]
- [[entities/berdl]]

See also: [[summaries/paperblast_explorer__REPORT]]

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]