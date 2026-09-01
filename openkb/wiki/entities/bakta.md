---
sources: ["summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/cf_formulation_design__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md"]
type: "Method"
description: "Bacterial genome annotation method used for PGP, AMR, and metabolic analyses"
---

# Bakta

Bakta is a bacterial genome annotation method that provides standardized product, enzyme-classification, and cross-reference annotations for AMR identification, pangenome analysis, PGP-gene distribution studies, fitness-effect studies, and metabolic annotation-gap resolution. [src: amr_fitness_cost, amr_pangenome_atlas, annotation_gap_discovery, pgp_pangenome_ecology]

## Role in AMR fitness-cost studies

The AMR fitness-cost study used the `bakta_amr` and `bakta_annotations` tables from `kbase_ke_pangenome` to assemble AMR-gene annotations. [src: amr_fitness_cost]

The study identified **1,352 AMR genes** across 43 organisms, comprising **178 Tier 1 genes** and **1,174 Tier 2 genes**. Tier 1 was based on `bakta_amr` results, while Tier 2 expanded the set through keyword matching in Bakta annotations. [src: amr_fitness_cost]

Tier 2 genes represented 86% of the AMR set. Their fitness distribution was not distinguishable from the Tier 1 distribution, with a Kolmogorov–Smirnov test p = 0.17. This supported the conclusion that annotation-based expansion did not materially dilute or bias the observed AMR fitness-cost signal. [src: amr_fitness_cost]

## Role in the pan-bacterial AMR atlas

The pan-bacterial AMR analysis used Bakta annotations alongside [[entities/amrfinderplus]] calls to characterize **83,008 AMRFinderPlus hits** on gene-cluster representatives across 14,723 species. Bakta product annotations and eggNOG hits were both available for 93.0% of AMR clusters. [src: amr_pangenome_atlas]

Bakta annotations supported functional-context analysis, including comparison of AMR clusters with a pangenome baseline across COG categories. AMR clusters were enriched for defense mechanisms and inorganic ion transport, with the latter reflecting mercury- and arsenic-resistance families included in the broad AMRFinderPlus reference catalog. [src: amr_pangenome_atlas]

The atlas also used Bakta product descriptions for keyword-based mechanism classification. The resulting categories included enzymatic inactivation, efflux, beta-lactamase, target modification, oxidoreductase, cell-wall modification, and regulatory mechanisms. However, 22.2% of hits remained Other/Unclassified because their product descriptions did not match the keyword sets. [src: amr_pangenome_atlas]

The report recommends mapping Bakta database cross-references (`bakta_db_xrefs`) to CARD Antibiotic Resistance Ontology terms as a more systematic alternative to keyword classification. [src: amr_pangenome_atlas]

## Role in PGP gene-distribution analysis

The PGP pangenome study used Bakta `gene` annotations in the `kbase_ke_pangenome` collection to extract clusters matching 13 plant-growth-promotion markers, including [[entities/acdS]], [[entities/pqqC]], [[entities/hcnA-hcnC]], [[entities/ipdC]], and [[entities/nifH]]. The analysis included **32,736 PGP gene clusters** across **11,272 species** carrying at least one marker. [src: pgp_pangenome_ecology]

Bakta annotations enabled species-level PGP presence matrices and core/accessory/singleton classification. The study found that all 13 PGP genes had significantly higher core fractions than the 46.8% genome-wide core baseline; reported core fractions included 81.5% for pqqC, 70.4% for acdS, 63.8% for nifH, and 55.5% for pqqD. [src: pgp_pangenome_ecology]

The PGP study used Bakta-derived gene calls to identify a strong pqqC–acdS co-occurrence association (OR = 7.24, n = 286 co-occurring species, q = 1.2e-83) and to quantify environmental enrichment. Soil/rhizosphere species showed enrichment for acdS (OR = 7.02), pqqC (OR = 2.90), and hcnC (OR = 1.85), while nifH was depleted (OR = 0.60). [src: pgp_pangenome_ecology]

Bakta-based PGP detection therefore contributed to the proposed [[concepts/gene-co-inheritance]] interpretation that the pqqC–acdS module is a stable, rhizosphere-associated phenotype rather than primarily a recently acquired accessory package. This interpretation is based on annotation-derived gene presence and pangenome status; the study did not independently validate gene functionality or expression. [src: pgp_pangenome_ecology]

## Role in metabolic annotation-gap discovery

The annotation-gap discovery study queried Bakta annotations in the `kbase_ke_pangenome` collection for alternative EC numbers and product-name matches, particularly for gapfilled reactions lacking ModelSEED EC assignments. [src: annotation_gap_discovery]

Bakta-based evidence contributed **22 newly resolved reaction–organism pairs**, corresponding to **10.9%** of the 201 gapfilled enzymatic pairs evaluated in that study. The Bakta search produced **1,459 candidate entries** for alternative EC or product-name evidence. [src: annotation_gap_discovery]

Bakta was used as one component of a broader [[concepts/evidence-triangulation]] pipeline combining gapfilling, Fitness Browser fitness evidence, pangenome conservation, GapMind pathway predictions, and BLAST homology. The complete pipeline resolved 96 of 201 pairs (47.8%), whereas Bakta evidence alone resolved 22 pairs (10.9%). [src: annotation_gap_discovery]

Bakta-derived alternatives were especially relevant to “dark reactions,” defined in the study as 50 gapfilled reactions without ModelSEED EC numbers. Only 8 of these 50 reactions (16%) were resolved, compared with 88 of 151 reactions with known EC numbers (58.3%), indicating that product-name and alternative-annotation evidence did not eliminate the difficulty of classifying EC-less reactions. [src: annotation_gap_discovery]

These results connect Bakta-derived annotation to [[concepts/annotation-gap]], [[concepts/evidence-triangulation]], and [[concepts/pangenome-integration]]. [src: annotation_gap_discovery]

## Role in functional dark-matter reannotation

The functional dark-matter project used **Bakta v1.12.0 with database v6.0** to reannotate or cross-reference **132.5 million pangenome cluster representatives**. Among **39,532 dark genes** with pangenome links, **33,105 (83.7%)** received a Bakta product description rather than remaining classified as hypothetical; this corresponds to **58.1% of all 57,011 dark genes** in the catalog. [src: functional_dark_matter]

Bakta descriptions changed the interpretation of the prioritized catalog: **all 100 top-ranked dark-gene candidates** received product descriptions. Examples included homogentisate 1,2-dioxygenase HmgA, cell-division proteins ZapE and ZapC, N-acetylglucosamine kinase, and the BolA-family iron-metabolism protein IbaG. These descriptions provide independent annotation support, but they do not by themselves establish that the reported product assignment is experimentally correct in the studied strain or condition. [src: functional_dark_matter]

Bakta’s AMRFinderPlus integration identified **5 dark genes with AMR annotations**, including mercury-resistance transport protein MerF in Marinobacter, a yersiniabactin transporter in *Klebsiella oxytoca*, an acid-resistance protein in *K. oxytoca*, a heat-resistance membrane protein in *Pseudomonas stutzeri*, and an S8-family peptidase in PV4. [src: functional_dark_matter]

Of the **6,427 genes** that remained hypothetical in both the Fitness Browser annotation and Bakta, 79.4% gained UniRef50 links, 69.1% gained UniParc/UniRef100 links, and 62.4% gained RefSeq links. Thus, Bakta did not resolve every dark gene but supplied cross-reference paths for literature and homology-based follow-up. [src: functional_dark_matter]

Adding Bakta annotation as a seventh evidence flag changed the darkness tier of **18,019 genes**, with the largest movement occurring from T4 Penumbra to T5 Dawn when Bakta supplied the final missing evidence line. [src: functional_dark_matter]

The reannotation demonstrates that the Fitness Browser’s hypothetical-gene label can reflect annotation vintage rather than complete functional ignorance. Bakta therefore functions both as an annotation-improvement method and as an evidence layer in [[concepts/resource-darkness]], [[concepts/annotation-gap]], and [[concepts/evidence-triangulation]]. [src: functional_dark_matter]

## Annotation limitations

PGP detection relied on Bakta `gene` annotations matching exact marker names, including nifH, acdS, pqqC, and related names. Genes annotated only by product description or under variant names were missed, particularly for less-characterized PGP genes. [src: pgp_pangenome_ecology]

The PGP study also did not filter detected clusters for truncations, frameshifts, or pseudogenization. Consequently, a Bakta annotation matching a PGP gene name does not necessarily demonstrate that the gene is intact or functional. [src: pgp_pangenome_ecology]

Keyword-based Tier 2 annotation could include some non-AMR genes, including general efflux transporters. The report treated this as an annotation-noise limitation but found that the Tier 1 sensitivity analysis produced consistent results. [src: amr_fitness_cost]

The product classifier used in the AMR fitness-cost study did not handle fosfomycin-resistance or tellurite-resistance annotations, leaving approximately 25 genes in the unknown-mechanism category. [src: amr_fitness_cost]

In the pan-bacterial AMR atlas, zero AMR clusters had Pfam domain hits in the `bakta_pfam_domains` table. The report interpreted this as evidence that the AMRFinderPlus and Pfam scans targeted non-overlapping sequence space, although it may also indicate an annotation-coverage limitation requiring investigation. [src: amr_pangenome_atlas]

In the annotation-gap discovery study, Bakta product-name and alternative-EC matching provided partial evidence but did not independently resolve most gaps. The study therefore treated Bakta as a complementary annotation stream rather than a sufficient basis for gene–reaction assignment. [src: annotation_gap_discovery]

The functional dark-matter reannotation shows that Bakta product descriptions should not be treated as experimental validation. A Bakta annotation can expose a plausible product for a gene previously labeled hypothetical, but functional prioritization still relies on independent evidence such as fitness effects, conservation, gene neighborhoods, co-fitness, or environmental concordance. [src: functional_dark_matter]

The residual set of **6,427 genes** that remained hypothetical after both Fitness Browser and Bakta annotation demonstrates that reannotation does not eliminate the functional dark-matter problem. [src: functional_dark_matter]

These limitations connect Bakta-derived annotation to the broader [[concepts/annotation-gap]], [[concepts/pangenome-integration]], and [[concepts/coverage-limited-inference]] challenges in comparative microbial genomics. [src: amr_fitness_cost, amr_pangenome_atlas, annotation_gap_discovery, functional_dark_matter, pgp_pangenome_ecology]

## Related resources

- [[entities/amrfinderplus]] — related AMR identification resource used with Bakta annotations. [src: amr_fitness_cost, amr_pangenome_atlas]
- [[entities/gtdb]] — taxonomy resource used for taxonomic analysis in the pan-bacterial AMR atlas. [src: amr_pangenome_atlas]
- [[entities/gapmind]] — pathway-completeness resource used alongside Bakta in annotation-gap and PGP analyses. [src: annotation_gap_discovery, pgp_pangenome_ecology]
- [[entities/kbase-ke-pangenome]] — source collection containing Bakta annotations and PGP gene-cluster data. [src: annotation_gap_discovery, pgp_pangenome_ecology]
- [[concepts/evidence-triangulation]] — framework in which Bakta evidence was combined with fitness, pangenome, GapMind, and homology evidence. [src: annotation_gap_discovery, functional_dark_matter]
- [[concepts/resource-darkness]] — evidence-tier framework applied to dark genes after Bakta reannotation. [src: functional_dark_matter]
- [[summaries/amr_fitness_cost__REPORT]] — source report on AMR fitness costs.
- [[summaries/amr_pangenome_atlas__REPORT]] — source report on pan-bacterial AMR conservation, distribution, and functional context.
- [[summaries/annotation_gap_discovery__REPORT]] — source report on integrated metabolic annotation-gap discovery.
- [[summaries/functional_dark_matter__REPORT]] — source report on experimentally prioritized bacterial functional dark matter.
- [[summaries/pgp_pangenome_ecology__REPORT]] — source report on PGP gene distribution across environments and pangenomes.

See also: [[summaries/cf_formulation_design__REPORT]]

See also: [[summaries/fitness_modules__REPORT]]

See also: [[summaries/microbeatlas_metal_ecology__REPORT]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]