---
type: "Concept"
sources: ["summaries/ecotype_env_reanalysis__REPORT.md", "summaries/bacdive_metal_validation__REPORT.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md"]
description: "How ecological niche shapes AMR abundance, composition, inheritance, and strain variation"
---

# Environmental Structuring of the Resistome

## Definition

Environmental structuring of the resistome is the association between ecological niche and the abundance, composition, and evolutionary organization of antimicrobial-resistance (AMR) genes across bacterial species. In the BERIL analyses, environment is associated not only with how much AMR a species carries, but also with whether resistance is core or accessory, which mechanisms predominate, and how AMR repertoires vary among strains. [src: amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation]

## Evidence across the pangenome

The combined analyses examined AMR across 14,723 species carrying 82,908 distinct AMR clusters; the environmental-resistome analysis included 280,337 genomes. [src: amr_environmental_resistome, amr_pangenome_atlas] Clinical-source species had a median of 5 AMR gene clusters, compared with 2 in soil, aquatic, and host-associated species; human-gut species also had a median of 5. [src: amr_environmental_resistome] The environment effect was significant (Kruskal–Wallis H = 781.9, p = 9.4×10⁻¹⁶⁷, η² = 0.056) and remained detectable across majority-vote classification thresholds from 50% to 90%. [src: amr_environmental_resistome]

Using a different species-level aggregation and classification, the pan-bacterial atlas found that Human/Clinical species averaged 10.6 AMR clusters per species, compared with 4.6 for Soil/Terrestrial, 3.9 for Aquatic, and 3.0 for Animal species (Kruskal–Wallis H = 440, p = 7.0e-93). [src: amr_pangenome_atlas] These values are not directly interchangeable with the medians above because the analyses use different environment groupings and summary procedures. [src: amr_environmental_resistome, amr_pangenome_atlas]

The strain-variation analysis provides a complementary scale of evidence: across 1,305 species and 180,025 genomes, 51.3% of AMR gene-species occurrences were rare, 41.3% variable, and 7.5% fixed. [src: amr_strain_variation] Host-associated species carried more AMR genes per genome than terrestrial or aquatic species in both rule-based and NCBI keyword-based classifications, with human-clinical isolates showing the highest burden (Kruskal–Wallis, p < 0.05). [src: amr_strain_variation] The NCBI classifier assigned environments to 1,190 of 1,307 species (91%), whereas the BacDive approximation classified 459 (35%). [src: amr_strain_variation]

These results extend the ecology-based resistome pattern reported by Gibson et al. from approximately 6,000 genomes to 14,723 species across 293K genomes. [src: amr_environmental_resistome] The finding is supported at substantially greater genomic and species scale, although uneven public-genome sampling—especially the overrepresentation of clinical isolates—may contribute to the observed difference. [src: amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation]

## Core and accessory resistance

Environmental differences are especially clear in the [[concepts/core-accessory-resistance]] composition of AMR. Clinical species averaged 32.4% core and 67.6% accessory AMR, whereas soil species averaged 57.1% core and 42.9% accessory AMR. [src: amr_environmental_resistome] Human-gut species had the largest accessory fraction, at 80.3%, while aquatic species averaged 54.4% core and 45.6% accessory AMR. [src: amr_environmental_resistome]

The atlas independently found that AMR genes were depleted from the core genome overall: 30.3% were core versus 46.8% for the pangenome baseline (OR=0.49, chi-squared=23,117, p≈0), with the auxiliary genome 2.2x enriched for AMR (33.6% versus 15.3%). [src: amr_pangenome_atlas] In a paired test of 4,252 species, 63.7% showed AMR less core than their species baseline (Wilcoxon p=1.1e-130; mean difference -0.102). [src: amr_pangenome_atlas]

The environment effect on core AMR percentage was significant (Kruskal–Wallis H = 506.0, p = 4×10⁻¹⁰⁷, η² = 0.036). [src: amr_environmental_resistome] The atlas similarly reported that clinical AMR was less core than soil AMR (30.8% versus 58.1%) and plant AMR (63.1%). [src: amr_pangenome_atlas] Together, these findings support a gradient in which soil and aquatic species retain proportionally more broadly maintained resistance, whereas clinical and gut species accumulate a larger accessory component. [src: amr_environmental_resistome, amr_pangenome_atlas]

The strain-resolution analysis confirms that the conservation classes correspond to real prevalence differences within species: 77.3% of atlas-defined Core AMR genes were fixed, 57.3% of Auxiliary genes were variable, and 78.7% of Singleton genes were rare. [src: amr_strain_variation] Thus, the environmental core/accessory gradient is consistent with substantial strain-level heterogeneity rather than only between-species differences. [src: amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation]

The reports interpret core resistance as primarily intrinsic or chromosomally encoded and accessory resistance as more likely acquired through horizontal gene transfer. [src: amr_environmental_resistome, amr_pangenome_atlas] This is an evidence-supported evolutionary interpretation, not a direct determination of genomic location or acquisition history, because the analyses use prevalence-based core definitions and do not uniformly measure mobility. [src: amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation]

The atlas further resolves this pattern by mechanism. Beta-lactamases were 54.9% core, while regulatory genes were only 6.5% core; named mobile examples including blaTEM, tet(C), and ant(2'')-Ia were 0% core. Intrinsic efflux systems such as emhABC were reported as greater than 95% core, whereas acquired efflux genes were accessory. [src: amr_pangenome_atlas] This supports the hypothesis that environmental differences partly reflect different mixtures of conserved intrinsic defenses and recently acquired, mobile resistance. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Mechanism-by-environment differences

Resistance mechanism composition is strongly environment-dependent. [src: amr_environmental_resistome] Metal resistance comprised 45.0% of classified AMR in aquatic species and 44.0% in soil species, but 6.1% in human-gut species; its environment effect was the largest measured (η² = 0.107). [src: amr_environmental_resistome] Target modification comprised 43.6% of human-gut AMR and 27.5% of clinical AMR, compared with 6.2% of aquatic AMR, with η² = 0.100. [src: amr_environmental_resistome]

Enzymatic inactivation was more evenly distributed, ranging from 24.1% in human-gut species to 44.1% in host-associated species, while efflux ranged from 1.1% in aquatic species to 7.0% in human-gut species. [src: amr_environmental_resistome] All four tested mechanisms showed significant environment-dependent composition after BH-FDR correction. [src: amr_environmental_resistome]

At strain resolution, resistance islands provide an additional mechanism-level explanation for structured variation. The analysis detected 1,517 islands across 705 species, with a mean size of 6.2 genes, a median of 4, a maximum of 43, and a mean phi coefficient of 0.827. [src: amr_strain_variation] Of these islands, 88% contained genes from multiple resistance mechanisms; efflux occurred in 954 islands and enzymatic inactivation in 698. [src: amr_strain_variation] These results support [[concepts/resistance-islands]] as a possible route by which environmental or clinical selection can shape coordinated AMR repertoires, but co-occurrence does not prove co-selection or functional synergy. [src: amr_strain_variation]

The atlas provides functional support for this ecological separation: COG V (Defense mechanisms) was 7.05x enriched in AMR genes (14.9% versus 2.1%), COG P (Inorganic ion transport) was 1.93x enriched (10.7% versus 5.6%), and COG J (Translation) was 1.50x enriched. [src: amr_pangenome_atlas] The ion-transport enrichment was associated with abundant mercury-resistance families, including merA and merP, and arsenic-resistance families such as arsD. [src: amr_pangenome_atlas]

The pattern suggests the hypothesis that natural environments select for resistance profiles strongly shaped by metal exposure, while clinical and gut environments favor antibiotic-associated strategies such as target modification and efflux. [src: amr_environmental_resistome] This interpretation is mechanistically plausible but remains an ecological inference rather than a direct causal test because exposure histories were not experimentally measured and the AMRFinderPlus Reference Gene Catalog includes stress-response genes alongside classical antibiotic-resistance determinants. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Within-species evidence

The relationship is not limited to differences between species. Among 823 species represented by genomes from at least two environments, the fraction of genomes from clinical sources correlated with total AMR cluster count (Spearman rho = 0.465, p = 2.2×10⁻⁴⁵). [src: amr_environmental_resistome] Species dominated by clinical genomes carried a mean of 72.9 AMR clusters, compared with 16.4 in environmentally dominated species, and the difference was significant by Mann–Whitney U testing (p = 2.0×10⁻¹⁸). [src: amr_environmental_resistome]

Clinical-dominated species also had a higher grouped accessory fraction than environmentally dominated species (93.6% versus 81.7%, p = 0.004), although the continuous correlation between clinical-genome fraction and accessory percentage was borderline (rho = 0.065, p = 0.064). [src: amr_environmental_resistome] The analysis is explicitly a species-level proxy, not a true per-genome within-species comparison. [src: amr_environmental_resistome]

The strongest example is [[entities/klebsiella-pneumoniae]], with 1,115 AMR clusters, of which only 7 were core and 1,108 were accessory; 80% of its genomes were classified as clinical. [src: amr_environmental_resistome] Comparable clinical-dominated patterns were reported for [[entities/staphylococcus-aureus]], [[entities/streptococcus-pneumoniae]], and [[entities/mycobacterium-tuberculosis]], while [[entities/salmonella-enterica]] was classified as predominantly host-associated. [src: amr_environmental_resistome]

The broader strain-variation analysis found that 190 of 974 species with sufficient genome counts formed at least two distinct AMR ecotypes using UMAP and DBSCAN, with a median silhouette score of 0.620. [src: amr_strain_variation] Environmental association tests were possible for only 2 species because 52.7% of genomes lacked a classifiable isolation source and strict expected-frequency criteria were applied. [src: amr_strain_variation] Case-study plots for [[entities/klebsiella-pneumoniae]], [[entities/staphylococcus-aureus]], and [[entities/salmonella-enterica]] showed visible environmental structuring, but the statistical evidence is underpowered and does not establish that environment causes the ecotypes. [src: amr_strain_variation]

## Independence from phylogeny

Environment-AMR associations persisted after stratification by broad taxonomic groups. [src: amr_environmental_resistome] Five of six tested phyla showed significant within-phylum environment effects, with Bacteroidota showing the largest effect (η² = 0.130); only Chloroflexota was non-significant. [src: amr_environmental_resistome] At the family level, 20 of 141 testable families showed significant effects after FDR correction, including Enterobacteriaceae (q = 3×10⁻²¹), Bacteroidaceae (q = 1.3×10⁻¹⁷), Lachnospiraceae (q = 2.5×10⁻¹²), and Pseudomonadaceae (q = 3.9×10⁻¹²). [src: amr_environmental_resistome]

The atlas likewise found strong phylogenetic structure: Gammaproteobacteria contained 45% of all AMR clusters (37,752/83,008), and Klebsiella, Salmonella, Citrobacter, and Enterobacter were the leading genera by AMR clusters per species. [src: amr_pangenome_atlas] Within phyla, pangenome openness correlated positively with AMR count in 8/10 tested phyla, but the overall correlation was near zero (rho=0.006), indicating that phylogeny dominates the aggregate openness signal. [src: amr_pangenome_atlas]

The strain-level analysis independently found phylogenetic structure in 1,261 species: 701 (55.6%) had significant Mantel signal after FDR correction, the median Mantel r was 0.247, and 87.8% showed positive correlations between ANI distance and AMR Jaccard distance. [src: amr_strain_variation] Non-core AMR had a stronger median signal than core AMR (0.222 versus 0.117; paired t-test p = 7.0e-16, n = 489), suggesting that acquired genes can become lineage-associated after acquisition. [src: amr_strain_variation] This result strengthens [[concepts/phylogenetic-amr-structure]], while also requiring caution because near-universal core genes have little Jaccard variation and therefore can show artificially suppressed distance-based correlations. [src: amr_strain_variation]

These results weaken the interpretation that the environmental pattern is merely a consequence of different environments containing different bacterial lineages. [src: amr_environmental_resistome] However, only 14% of tested families showed significant within-family effects, and many families did not span enough environments for reliable testing. [src: amr_environmental_resistome]

## Continuous environmental evidence

AlphaEarth environmental embeddings provided supplementary support for the discrete environment classifications. [src: amr_environmental_resistome] Among 2,659 species with both AMR data and embeddings, 52 of 64 dimensions correlated with AMR diversity after FDR correction, with the strongest correlation at dimension A34 (rho = +0.24). [src: amr_environmental_resistome] A Mantel test found that environmental distance predicted AMR mechanism-profile distance (r = 0.098, p = 0.001). [src: amr_environmental_resistome]

The environmental-AMR coupling was strongest in clinical species (r = 0.177), intermediate in soil species (r = 0.129), and weakest in aquatic species (r = 0.061). [src: amr_environmental_resistome] Because the embedding dimensions have limited biological interpretability and covered only 28% of genome data, this evidence confirms the broad pattern without identifying specific environmental drivers. [src: amr_environmental_resistome]

A separate atlas analysis of 2,684 species with at least three genomes and embeddings found that environmental diversity predicted AMR count (Spearman rho=0.466, p=1.6e-144), while environmental diversity was negatively associated with AMR core fraction (rho=-0.173, p=1.8e-19). [src: amr_pangenome_atlas] The agreement between the discrete-environment and continuous-embedding analyses strengthens the association, but does not establish that environmental diversity itself causes AMR accumulation. [src: amr_environmental_resistome, amr_pangenome_atlas]

## Tensions

### Ecological signal versus sampling bias

The reports find substantially greater AMR abundance in clinical species, but clinical isolates are massively overrepresented in NCBI and are more likely to be sequenced because of their resistance phenotypes. [src: amr_environmental_resistome] Environmental AMR may therefore be underestimated, particularly when novel resistance genes are missed by annotations focused on known determinants. [src: amr_environmental_resistome] The atlas also notes that 7,838 of 14,723 AMR-carrying species (53.2%) received a non-Other/Unknown environment classification, leaving 46.8% in the large unknown bin. [src: amr_pangenome_atlas] The strain-variation analysis similarly reported that 52.7% of genomes lacked a classifiable isolation source for ecotype testing. [src: amr_strain_variation]

### Core/accessory status versus acquisition history

The analyses treat core AMR as a proxy for intrinsic resistance and accessory AMR as a proxy for acquired resistance, consistent with prior resistome observations. [src: amr_environmental_resistome, amr_pangenome_atlas] Nevertheless, prevalence-based core/accessory labels do not directly establish chromosomal location, mobility, or the historical route of acquisition. [src: amr_environmental_resistome, amr_strain_variation] The strain-level finding that non-core genes have stronger phylogenetic signal than core genes further suggests lineage-restricted maintenance, but does not by itself distinguish vertical inheritance from repeated transfer among close relatives. [src: amr_strain_variation]

### Association versus causation

The observed clinical enrichment could reflect antibiotic selection in clinical environments, but the data cannot distinguish this explanation from reverse causality, in which resistant or virulent organisms are preferentially sampled from clinical settings. [src: amr_environmental_resistome] The positive association between environmental diversity and AMR count similarly supports a hypothesis about niche breadth and horizontal acquisition rather than a demonstrated causal mechanism. [src: amr_pangenome_atlas] Likewise, visible environment-associated AMR ecotypes are not supported by adequately powered statistical tests for most species. [src: amr_strain_variation]

### Annotation scope and mechanism classification

The atlas contains 83,008 AMRFinderPlus hits spanning 1,939 AMR gene families, but the catalog includes mercury, arsenic, and other stress-response genes in addition to classical antibiotic-resistance genes. [src: amr_pangenome_atlas] Its mechanism labels were generated by keyword matching, leaving 22.2% in an Other/Unclassified category; therefore, comparisons among mechanism classes may be sensitive to annotation ontology and classification rules. [src: amr_pangenome_atlas] The strain-variation analysis likewise relies on AMRFinderPlus, so resistance mechanisms absent from that database are missed. [src: amr_strain_variation]

### Temporal trends remain unresolved

A separate strain-level analysis found no significant temporal trend in AMR gene count after multiple-testing correction in any of 513 species with at least 20 genomes spanning at least 3 post-1990 years. [src: amr_strain_variation] Slopes were roughly balanced between positive and negative values (251 versus 262), but sparse collection dates—only 70% of genomes had parseable dates—make this a data-quality null rather than evidence against temporal environmental selection. [src: amr_strain_variation]

## Open Directions

- Compare specific AMR clusters shared by soil, aquatic, gut, and clinical species to test for cross-niche gene exchange; this would directly evaluate the inference about recent horizontal transfer. [src: amr_environmental_resistome]
- Use time-stamped genomes of [[entities/klebsiella-pneumoniae]] and [[entities/staphylococcus-aureus]] to test whether accessory AMR increases over sampling decades, using curated dates to address the unresolved temporal result. [src: amr_environmental_resistome, amr_strain_variation]
- Link environmental profiles to mobile-element annotations to determine whether clinical accessory clusters are enriched on plasmids, transposons, or integrative elements. [src: amr_environmental_resistome, amr_pangenome_atlas, amr_strain_variation]
- Validate species-level predictions against environmental metagenomes to assess whether the pangenome signal transfers to real communities. [src: amr_environmental_resistome, amr_pangenome_atlas]
- Apply environment-specific gene identification and PERMANOVA/ordination to determine which clusters, rather than aggregate counts alone, drive ecological separation. [src: amr_environmental_resistome]
- Improve ecotype testing by expanding isolation-source metadata and testing whether AMR clusters, resistance islands, and environmental variables jointly explain strain-level structure. [src: amr_strain_variation]
- Map Bakta cross-references to the CARD Antibiotic Resistance Ontology to replace keyword mechanism classes and reduce the 22.2% Other/Unclassified category. [src: amr_pangenome_atlas]
- Estimate AMR gene gain and loss rates from phylogenetic distances and compare intrinsic with acquired resistance dynamics. [src: amr_pangenome_atlas, amr_strain_variation]
- Test fitness effects of mobile resistance in clinical organisms and under antibiotic-stress conditions, extending beyond the predominantly environmental Fitness Browser coverage. [src: amr_pangenome_atlas]

## Source

See [[summaries/amr_environmental_resistome__REPORT]] for the complete environmental-resistome project summary, data tables, notebooks, limitations, and analyses.

See [[summaries/amr_pangenome_atlas__REPORT]] for the pan-bacterial AMR census, conservation, taxonomy, functional, environmental, and fitness analyses.

See [[summaries/amr_strain_variation__REPORT]] for the within-species variation, resistance-island, phylogenetic-signal, ecotype, temporal, and environment-burden analyses.

See also: [[summaries/amr_fitness_cost__REPORT]]

See also: [[summaries/bacdive_metal_validation__REPORT]]

See also: [[summaries/ecotype_env_reanalysis__REPORT]]