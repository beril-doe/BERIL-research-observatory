---
type: "Summary"
description: "Pangenome-scale analysis links PHB distribution to variable environments and HGT."
doc_type: short
full_text: "sources/phb_granule_ecology__REPORT.md"
---

# Polyhydroxybutyrate Granule Formation Pathways

## Overview

This report presents a pangenome-scale survey of polyhydroxybutyrate (PHB) biosynthesis across 27,690 GTDB bacterial species. It integrates gene annotations, phylogenetic distribution, environmental metadata, AlphaEarth environmental embeddings, genome size, pangenome core/accessory status, and NMDC metagenomic data to test whether PHB is favored in environmentally variable “feast/famine” habitats. The analysis supports environmental enrichment of PHB pathways, while showing that apparent PHB associations with niche breadth are largely explained by genome size. It also identifies widespread, ongoing horizontal transfer of the committed PHB synthesis gene [[concepts/horizontal-gene-transfer]].

## Key Findings

### PHB pathways are widespread but phylogenetically concentrated

- **21.9% of 27,690 species carry phaC**, the PHA synthase gene and committed step of PHB biosynthesis; **21.7% have a complete pathway** based on phaC plus phaA/phaB.
- The survey identified **118,513 PHB-related gene clusters across 19,496 species** using eggNOG annotations.
- PHB prevalence is highest in **Pseudomonadota (60.9%; 4,544/7,456)**, followed by Myxococcota (52.9%), Halobacteriota (34.4%), Thermoproteota (27.9%), Desulfobacterota (21.9%), and Actinomycetota (18.5%).
- Campylobacterota, Gemmatimonadota, Nanoarchaeota, and Marinisomatota had no detected phaC; Patescibacteria had only 0.4% prevalence.
- The five most enriched phyla contain **85.5% of phaC-positive species while representing 30.4% of total species diversity**, demonstrating strong phylogenetic concentration.
- The apparent abundance of “precursors-only” species (46.5%) is probably inflated because phaA and phaB have broader metabolic roles beyond PHB synthesis. phaR was not detected in the eggNOG annotations, indicating incomplete annotation or gene-assignment limitations.

These results support the broader concept of [[concepts/phylogenetic-confounding]]: pathway presence is not evenly distributed across the bacterial tree, even when the pathway has broad ecological relevance.

### Environmental variability is associated with PHB prevalence

PHB prevalence follows a strong environmental gradient:

| Environment | Species | phaC prevalence |
|---|---:|---:|
| Plant-associated | 625 | 44.0% |
| Soil | 1,484 | 43.6% |
| Wastewater/engineered | 1,124 | 34.5% |
| Freshwater | 3,263 | 25.5% |
| Sediment | 1,020 | 20.1% |
| Marine | 3,010 | 18.7% |
| Human associated | 1,237 | 11.1% |
| Human clinical | 2,472 | 7.4% |
| Animal associated | 3,711 | 3.3% |

A chi-squared test of PHB presence against environmental variability category produced **chi2 = 1,656.36, p ~ 0, dof = 2**. High-variability plant, soil, and wastewater environments therefore contain substantially more PHB-capable species than relatively stable marine, clinical, and host-associated environments. This is the report’s strongest evidence for the [[concepts/feast-famine-selection]] hypothesis at comparative-genomic scale.

The environmental association remains after stratifying species by genome size. High-variability environments have **4.4x, 4.6x, 3.1x, and 1.4x** greater phaC prevalence than low-variability environments in genome-size quartiles Q1 through Q4, respectively; all tests have p-values below 1e-11. This persistence indicates that the environmental signal is not merely a consequence of larger genomes carrying more metabolic genes.

### Niche breadth is largely confounded by genome size

Among 2,008 species with sufficient [[entities/alphaearth-environmental-embeddings]] representation, phaC-positive species had greater environmental embedding variance than phaC-negative species:

- PHB+: median variance **0.3295**, n = 531
- PHB−: median variance **0.2472**, n = 1,477
- Mann–Whitney p = **1.88 × 10^-6**

However, PHB-positive species had much larger median genomes (**4.34 Mbp versus 2.44 Mbp**), and genome size correlated with niche breadth (**rho = 0.302, p = 1.5 × 10^-43**). Controlling for genome size reduced the PHB–niche breadth relationship from **rho = 0.106** to a partial **rho = −0.047 (p = 0.037)**, a 56.3% reduction with a sign reversal.

Thus, the report qualifies rather than confirms the hypothesis that PHB independently promotes broad niche occupation. The raw association is mainly consistent with the relationship between [[concepts/ecological-generalism]] and genome size: larger genomes encode more metabolic functions and tend to occur in broader or more variable habitats. In contrast, the direct enrichment of PHB in variable environments survives genome-size control.

### Subclade enrichment is heterogeneous

Among 248 families tested with Bonferroni-corrected Fisher’s exact tests:

- 41 families were enriched in PHB
- 62 were depleted
- 145 were not significant

Enriched families were concentrated in Pseudomonadota, including Burkholderiaceae, Rhodocyclaceae, Caulobacteraceae, Sphingomonadaceae, Xanthobacteraceae, Rhodanobacteraceae, and Legionellaceae. Additional enriched families occurred in Actinomycetota, Halobacteriota, Thermoproteota, Cyanobacteriota, and Bacillota.

Enriched families skewed toward freshwater and wastewater, whereas depleted families skewed toward marine and host-associated environments. Interpretation is limited because “other_unknown” accounted for 30 of 41 enriched families and 26 of 62 depleted families. The result demonstrates heterogeneous selection within otherwise PHB-rich phyla and motivates [[concepts/metabolic-ecotypes]] and [[concepts/phylogenetic-confounding]].

### PhaC shows a strong horizontal-transfer signal

Phylogenetic discordance analysis identified:

- **311 potential phaC acquisition events** in families with less than 20% phaC prevalence
- **278 potential loss events** in families with more than 80% prevalence

Among discordant phaC-positive species, **60.1% carried phaC as accessory genome**, compared with 32.3% across all phaC-positive species. The elevated accessory fraction is consistent with recent or ongoing horizontal acquisition before fixation in the core genome. Putative recipient families included Lachnospiraceae, Chitinophagaceae, Pelagibacteraceae, Enterobacteriaceae, and Planococcaceae.

Overall, 5,371 species carried phaC as core and 1,959 as accessory, with some species containing both types of copies. The result extends earlier single-species reports of PHA-gene transfer to a broad pangenomic pattern, but direct confirmation requires a phaC gene tree compared with the species tree. This connects the result to [[concepts/core-accessory-resistance]], [[concepts/mobile-genetic-elements]], and [[concepts/pangenome-integration]].

### NMDC metagenomes broadly validate pangenome patterns

A two-tier taxonomy bridge mapped **3,014 of 3,492 NMDC taxon columns (86.3%)** to GTDB genera with known PHB status. PHB inference scores were calculated for **6,365 metagenomic samples**, with a median of 87.2% of taxonomic abundance matched to pangenome genera.

PHB inference scores showed statistically significant but modest correlations with abiotic variables:

- Depth: **rho = −0.119**, p = 1.14 × 10^-21
- Temperature: **rho = +0.088**, p = 1.86 × 10^-12
- Maximum depth: **rho = +0.076**, p = 1.15 × 10^-9
- Minimum depth: **rho = −0.055**, p = 1.05 × 10^-5
- pH: **rho = +0.049**, p = 7.95 × 10^-5
- Ammonium nitrogen: **rho = +0.044**, p = 4.49 × 10^-4

The negative depth association is consistent with greater PHB capacity in shallower, more dynamic environments, but the small effect sizes and point-in-time nature of the environmental measurements limit direct inference about temporal variability. In a genus-level comparison of 693 matched genera, PHB-high genera were more abundant in NMDC samples than PHB-low genera (**Mann–Whitney p = 8.41 × 10^-22**). Frequently abundant PHB-high genera included *Mycobacterium*, *Pseudomonas*, *Cupriavidus*, *Burkholderia*, and *Methylobacterium*.

## Interpretation

The report provides strong comparative evidence that PHB pathway maintenance and acquisition are associated with environments characterized by fluctuating carbon inputs. This supports the [[concepts/feast-famine-selection]] hypothesis, while also indicating that PHB likely has functions beyond carbon storage, including stress resistance, redox balancing, cryoprotection, and responses to osmotic, oxidative, UV, and temperature stress. These functions connect PHB biology to [[concepts/shared-stress-biology]].

The evidence should be separated into two claims:

1. **Environmental selection claim — strongly supported:** PHB prevalence is higher in plant, soil, and wastewater environments than in stable or host-associated environments, and this pattern persists within genome-size quartiles.
2. **Independent niche-breadth claim — weakly supported or unresolved:** PHB-positive species show broader environmental embeddings, but the relationship largely disappears after controlling for genome size.

The report therefore argues that genome size is a major confounding variable in pathway–ecology analyses. Larger genomes are associated with broader metabolic repertoires and environmental breadth, but PHB retains an environment-specific association beyond this general effect. The synthesis connects [[concepts/feast-famine-selection]], [[concepts/latent-metabolic-capabilities]], [[concepts/ecological-generalism]], [[concepts/genome-ecology-validation]], and [[concepts/pangenome-integration]].

## Limitations

- NMDC abiotic correlations are modest, and measurements generally represent snapshots rather than temporal variability.
- NMDC sampling is biased toward terrestrial and soil environments.
- PHA synthase class assignment failed because the analysis expected Pfam accession IDs while eggNOG supplied domain names; all 11,792 phaC clusters were classified as “other_pfam.”
- Environmental metadata are sparse, with 34.9% of species assigned to “other_unknown.”
- AlphaEarth embeddings were available for only 28% of genomes, and the niche analysis covered 2,008 species, or 7.2% of total species diversity.
- phaA and phaB are pleiotropic, making the precursors-only category an imperfect indicator of PHB capacity.
- Phylogenetic structure, genome size, MAG quality, and variable gene-detection rates may affect pathway prevalence estimates.
- HGT events were inferred from phylogenetic discordance and core/accessory status rather than directly demonstrated through gene-tree/species-tree reconciliation.

These limitations exemplify [[concepts/coverage-limited-inference]], [[concepts/annotation-gap]], [[concepts/phylogenetic-confounding]], and [[concepts/phenotype-resolution-matching]].

## Future Directions

1. Map eggNOG domain names to Pfam accessions to classify PHA synthase classes I–IV.
2. Apply phylogenetic logistic regression or phylogenetic independent contrasts to test environmental selection while accounting for shared ancestry.
3. Reconstruct a phaC gene tree and compare it with the species tree to identify transfer events directly.
4. Query the [[entities/fitness-browser]] for phaC mutant phenotypes under feast/famine and stress conditions.
5. Analyze full AlphaEarth vectors rather than only embedding variance to identify environmental axes associated with PHB.
6. Use NMDC ecosystem labels and ENVO terms to improve sample-level environmental classification.

## Data and Supporting Materials

The study used [[entities/berdl]] pangenome tables for eggNOG annotations, gene clusters, taxonomy, environmental metadata, genome size, pangenomes, and AlphaEarth embeddings, together with [[entities/nmdc]] tables for taxonomy, abiotic variables, and metagenomic features. Generated datasets include species-level PHB summaries, taxonomy and environment tables, family enrichment results, core/accessory phaC assignments, NMDC PHB inference scores, abiotic correlations, and pangenome–metagenome comparisons. Analyses were conducted in notebooks `01_phb_gene_discovery.ipynb` through `05_subclade_enrichment.ipynb`.

## Related Concepts
- [[concepts/two-speed-genome]]
- [[concepts/organism-specificity]]

## Entities
- [[entities/random-barcode-transposon-sequencing]]
