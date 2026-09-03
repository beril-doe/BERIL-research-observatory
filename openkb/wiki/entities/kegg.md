---
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/respiratory_chain_wiring__REPORT.md", "summaries/pitfalls.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/paperblast_explorer__REPORT.md", "summaries/nmdc_context_audit__REPORT.md", "summaries/nmdc_community_metabolic_ecology__REPORT.md", "summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/metal_resistance_global_biogeography__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/metal_cross_resistance__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/ibd_phage_targeting__REPORT.md", "summaries/essential_metabolome__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/enigma_contamination_functional_potential__REPORT.md", "summaries/discoveries.md", "summaries/cf_formulation_design__REPORT.md", "summaries/berdl_data_atlas__REPORT.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/bacdive_metal_validation__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md"]
type: "Dataset"
description: "KEGG is a functional annotation and pathway dataset used in genome analyses."
---

# KEGG

## Identity

**KEGG** is a functional annotation and pathway resource used to assign or compare KEGG orthology (KO) annotations for Fitness Browser genes, gene clusters, and pangenome genomes. [src: amr_cofitness_networks, bacdive_metal_validation, pitfalls] In the Fitness Browser schema, KO membership is represented through `keggmember.kgroup`, rather than a single direct `(orgId, locusId) → KO` table. [src: pitfalls]

## Role in the AMR cofitness analysis

The AMR cofitness analysis used Bakta-derived KEGG orthology data from the `kbase_ke_pangenome` collection to characterize AMR cofitness support networks. [src: amr_cofitness_networks] KEGG annotations were also used in the legacy cross-organism conservation analysis, where they provided the comparison with the later InterProScan GO-based analysis. [src: amr_cofitness_networks]

The old KEGG-based analysis produced a mean within-mechanism Jaccard similarity of 0.069 and a mean cross-mechanism similarity of 0.249. [src: amr_cofitness_networks] It did not support the organism-specificity comparison: the cross-mechanism-versus-within-mechanism test had a p-value of 1.0 with old KEGG annotations. [src: amr_cofitness_networks]

By contrast, InterProScan GO annotations produced Jaccard similarities of 0.207 within mechanism and 0.375 across mechanisms, with cross-mechanism similarity significantly higher than within-mechanism similarity (p = 4.3×10⁻¹³). [src: amr_cofitness_networks] This comparison links KEGG to findings on [[concepts/annotation-gap]], [[concepts/cofitness-networks]], and [[concepts/organism-specificity]].

## Role in Fitness Browser KO mapping

A Fitness Browser locus must be mapped to KEGG through two joins. [src: pitfalls] First, `besthitkegg` connects `(orgId, locusId)` to a KEGG organism and gene through `(keggOrg, keggId)`. [src: pitfalls] Second, `keggmember` maps `(keggOrg, keggId)` to the KO group stored in `kgroup`. [src: pitfalls]

```sql
SELECT gf.orgId, gf.locusId, km.kgroup AS KO
FROM kescience.fitnessbrowser.genefitness gf
JOIN kescience.fitnessbrowser.besthitkegg bhk
     ON gf.orgId = bhk.orgId AND gf.locusId = bhk.locusId
JOIN kescience.fitnessbrowser.keggmember km
     ON bhk.keggOrg = km.keggOrg AND bhk.keggId = km.keggId
```

`keggmember` does not contain `orgId` or `locusId`, so attempting to join Fitness Browser loci directly to that table is invalid. [src: pitfalls] The Fitness Browser `kgroupdesc` table uses the column `desc` for KO descriptions, and the numeric-like Fitness Browser fields used alongside these annotations may be stored as strings and require explicit casting before comparisons or arithmetic. [src: pitfalls]

## Role in metal-tolerance prediction

KEGG functional annotations were used to derive the genome-based metal tolerance score in the Metal Fitness Atlas workflow. [src: bacdive_metal_validation] The score was projected onto 27,702 pangenome species using KEGG functional annotations, enabling comparison with BacDive isolation environments. [src: bacdive_metal_validation]

In the BacDive validation, the normalized score was based on metal-associated functional clusters relative to annotated clusters, so KEGG annotation content formed part of the denominator as well as the functional signal. [src: bacdive_metal_validation] This normalization was intended to control for genome size, although the report notes that it may not eliminate confounding because metal-tolerance functions can correlate with total metabolic complexity. [src: bacdive_metal_validation]

Species-level matching linked 42,227 BacDive strains to metal scores across 6,426 GTDB species; the bridge depended on matching BacDive taxonomy to GTDB pangenome species and then using the KEGG-derived scores. [src: bacdive_metal_validation] Bacteria isolated from heavy-metal contamination sites had higher predicted metal-tolerance scores than the environmental baseline (Cohen’s d = +1.00, Mann–Whitney p = 0.006, n = 10), while all contamination isolates showed a smaller but significant effect (Cohen’s d = +0.43, p < 0.0001). [src: bacdive_metal_validation]

This application connects KEGG to [[concepts/environmental-metal-tolerance]], [[concepts/genome-ecology-validation]], and [[concepts/pangenome-integration]]. The result supports the use of KEGG-derived functional content as an ecological predictor, but the small heavy-metal sample and possible annotation and genome-complexity confounding limit how precisely the effect can be estimated. [src: bacdive_metal_validation]

## Interpretation

The AMR analysis treats the KEGG result as evidence that annotation choice and coverage can strongly affect functional interpretation of cofitness networks. [src: amr_cofitness_networks] In that analysis, the InterProScan GO workflow detected organism-specific support-network structure that was not recovered by the older KEGG-based workflow. [src: amr_cofitness_networks]

The BacDive analysis provides a complementary use case: KEGG functional annotations enabled a genome-derived metal-tolerance score that showed significant association with bacterial isolation from contaminated environments. [src: bacdive_metal_validation] However, the report does not establish that KEGG annotations alone explain the ecological signal, because the score also depends on the underlying Fitness Browser data, pangenome projection, species matching, and normalization procedure. [src: bacdive_metal_validation]

Together, these studies do not conclude that KEGG annotations are biologically invalid. [src: amr_cofitness_networks] Instead, they show that KEGG-derived features can be useful for cross-genome ecological prediction while annotation coverage, functional representation, taxonomy matching, and normalization remain important sources of uncertainty. [src: amr_cofitness_networks, bacdive_metal_validation]

The pitfalls documentation further indicates that KEGG-derived results require careful schema inspection and explicit join validation. [src: pitfalls] In particular, a failed direct locus-to-KO join, uncast string-valued measurements, or incomplete annotation coverage can produce apparently clean but incorrect downstream comparisons. [src: pitfalls]

## Related pages

- [[entities/interproscan]]
- [[entities/seed]]
- [[entities/bacdive]]
- [[entities/gtdb]]
- [[entities/metal-fitness-atlas]]
- [[summaries/amr_cofitness_networks__REPORT]]
- [[summaries/bacdive_metal_validation__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/amr_environmental_resistome__REPORT]]
- [[summaries/amr_fitness_cost__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]
- [[summaries/bacdive_phenotype_metal_tolerance__REPORT]]
- [[summaries/berdl_data_atlas__REPORT]]
- [[summaries/cf_formulation_design__REPORT]]
- [[summaries/discoveries]]
- [[summaries/enigma_contamination_functional_potential__REPORT]]
- [[summaries/essential_genome__REPORT]]
- [[summaries/ibd_phage_targeting__REPORT]]
- [[summaries/lanthanide_methylotrophy_atlas__REPORT]]
- [[summaries/metabolic_capability_dependency__REPORT]]
- [[summaries/metal_cross_resistance__REPORT]]
- [[summaries/metal_fitness_atlas__REPORT]]
- [[summaries/metal_resistance_global_biogeography__REPORT]]
- [[summaries/microbeatlas_metal_ecology__REPORT]]
- [[summaries/nmdc_community_metabolic_ecology__REPORT]]
- [[summaries/nmdc_context_audit__REPORT]]
- [[summaries/paperblast_explorer__REPORT]]
- [[summaries/pgp_pangenome_ecology__REPORT]]

## Related Documents
- [[summaries/pitfalls]]


See also: [[summaries/respiratory_chain_wiring__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]