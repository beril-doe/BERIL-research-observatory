---
type: "Concept"
sources: ["summaries/t4ss_cazy_environmental_hgt__REPORT.md", "summaries/pseudomonas_carbon_ecology__REPORT.md", "summaries/pitfalls.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/lignin_community_enrichment__REPORT.md", "summaries/genotype_to_phenotype_enigma__REPORT.md", "summaries/field_vs_lab_fitness__REPORT.md", "summaries/enigma_carbon_census_1__REPORT.md"]
description: "Environmental presence suggests opportunity, but activity requires pathway and process evidence."
---

# Environmental Occupancy versus Catabolic Activity

## Core Idea

Environmental occurrence and abundance show where organisms are detected, but they do not establish that those organisms degrade a particular compound, express the relevant genes, or contribute measurable catabolic flux. The distinction is central to interpreting genome-based utilization predictions alongside environmental surveys. [src: enigma_carbon_census_1]

The lignin-enrichment experiment reinforces this distinction from the opposite direction: taxa that became dominant under lignin or lignin-plus-labile-carbon conditions are plausible participants in the enrichment response, but 16S abundance alone does not prove lignin degradation, pathway expression, or carbon assimilation. [src: lignin_community_enrichment]

This is an instance of [[concepts/evidence-triangulation]]: a defensible claim about environmental catabolism requires agreement among pathway or gene evidence, organism-level linkage, and environment-specific activity measurements. Taxonomic abundance alone supplies only ecological context. [src: enigma_carbon_census_1]

## Evidence Layers

The ENIGMA Carbon Census connected compounds to pathway annotations, ENIGMA-isolate utilizer predictions, SSO field occurrence, and global biome abundance. These layers answer different questions: pathway and genome evidence address potential utilization; field occurrence addresses whether implicated genera are observed locally; and metagenomic abundance addresses where those genera occur globally. [src: enigma_carbon_census_1]

The local SSO atlas detected 62 implicated utilizer genera in the field, while the global NMDC atlas detected 83 of 86 implicated genera in 1719 metagenomes out of 3825 taxonomy-bearing metagenomes. These observations establish environmental occupancy of the taxa, not degradation of the census compounds. [src: enigma_carbon_census_1]

The census explicitly treated the global atlas as a biome-abundance proxy because no environmental dataset measured the census compounds. Thus, a genus enriched in soil, freshwater, or periphyton cannot on this evidence be said to degrade a target compound in that environment. [src: enigma_carbon_census_1]

The lignin study adds an experimental selection layer. After one lignin passage, Pseudomonas reached 39.3% and Acinetobacter 25.2% of bacterial 16S reads, while the base community contained less than 0.1% of each genus. The shift was associated with a 90% reduction in observed OTUs, from 1,594 to 163, and treatment explained 97.9% of bacterial community variance (R²=0.979, p=0.001). [src: lignin_community_enrichment]

These results show that an enrichment condition can select for taxa associated with a substrate, but they still measure community composition rather than compound turnover or catabolic flux. The report therefore treats pathway assignments and known genus-level capabilities as biological context and hypothesis-generating evidence, not as direct proof of activity. [src: lignin_community_enrichment]

## Environmental Patterns in the Census

Periphyton, defined in the report as freshwater biofilm environments such as epilithon, epipsammon, and epiphyton, emerged as a reservoir for implicated Burkholderiales and Comamonadaceae. Several genera reached approximately 96–97% prevalence in periphyton samples, with mean relative abundances around 0.005–0.009. [src: enigma_carbon_census_1]

Label-free outlier analysis found large genus-by-sample abundance spikes in periphyton and soil, including Nocardioides at 0.43 in epipsammon, Hydrogenophaga at 0.28 in epiphyton, and Mycobacterium at 0.22 in soil. These are useful signals for locating candidate habitats or inocula, but they remain occupancy signals without compound-resolved activity measurements. [src: enigma_carbon_census_1]

The marine comparison further illustrated the distinction. In 302 Planet Microbe runs, all 68 listed genera showed positive abundance, but most terrestrial or freshwater-associated genera occurred at approximately 1e-3 to 1e-4 abundance in open ocean. Alteromonas was a notable marine-associated genus, occurring at 0.048 in 240/302 runs with prevalence 0.79. None of these abundance patterns demonstrates degradation of a census compound. [src: enigma_carbon_census_1]

The lignin experiment provides a complementary controlled example of condition-dependent occupancy. Flavobacterium increased from 0.1% in the base community to 14.1% under lignin-only enrichment but declined to 1.4% when labile carbon was co-supplemented. Comamonas reached 3.6–5.1% in Round 2 groups, Aminobacter appeared at 7.6% in L-L and 6.4% in LC-L, and Rhodococcus was highest in lignin-only enrichment at 0.67%. [src: lignin_community_enrichment]

These patterns support hypotheses about substrate-associated selection, including a possible specialist response by Flavobacterium to lignin-derived aromatics, but the study did not directly measure degradation rates, pathway expression, or isotope incorporation. Conversely, Sphingomonas was more abundant in the base community (1.74%) than in enriched conditions, showing that a genus known for aromatic catabolism need not be selected by every lignin enrichment. [src: lignin_community_enrichment]

## What Occupancy Can and Cannot Support

Environmental occupancy can support:

- selecting inoculum sources for enrichment experiments;
- identifying habitats in which candidate utilizers are present;
- distinguishing broad biome associations among predicted utilizer genera;
- generating hypotheses about whether local or global environments may contain relevant organisms;
- identifying taxa that reproducibly respond to a substrate-associated enrichment condition, when the experiment includes suitable treatment comparisons. [src: enigma_carbon_census_1, lignin_community_enrichment]

Occupancy cannot by itself support:

- compound-specific degradation;
- expression of catabolic genes;
- pathway completeness in the sampled organisms;
- transport, uptake, or substrate bioavailability;
- degradation rates, carbon assimilation, or catabolic flux;
- the conclusion that persistence or enrichment of a taxon reflects direct substrate use rather than cross-feeding, tolerance, or indirect ecological effects. [src: enigma_carbon_census_1, lignin_community_enrichment]

The distinction also applies in reverse: failure to detect a genus in an environmental dataset does not prove that it cannot degrade the compound, because detection depends on sampling, sequencing depth, taxonomic resolution, and database representation. This limitation connects environmental interpretation to [[concepts/cultivation-bias]], [[concepts/prevalence-ceiling]], and [[concepts/annotation-gap]]. [src: enigma_carbon_census_1]

The lignin study illustrates an additional caution: strong treatment separation does not automatically identify the mechanism of selection. Labile carbon shifted the community toward Acinetobacter, Aeromonas, and Enterobacter, while reducing Pseudomonas and Flavobacterium under the reported conditions; these changes are consistent with a copiotrophic shift but do not by themselves establish which taxa degraded lignin or its aromatic products. [src: lignin_community_enrichment]

## Statistical and Technical Constraints

The census's soil-versus-freshwater comparisons were exploratory. Treating thousands of metagenomes as independent observations in rank tests ignores study dependence and compositional, zero-inflated abundance structure; the report therefore considers contrast direction and rank more reliable than the resulting p-values. [src: enigma_carbon_census_1]

Accurate occupancy estimates also required species-to-genus aggregation before abundance calculations. Filtering directly on bare genus names produced near-zero matches and initially caused the marine analysis to report zero positive genera. The NMDC denominator likewise had to be restricted to the 3825 covstats files carrying taxonomy rather than the approximately 6700 rows in the sample-file lookup. [src: enigma_carbon_census_1]

These technical requirements show that even the weaker occupancy claim depends on careful taxonomic rollup and denominator definition. They do not, however, transform abundance into activity. [src: enigma_carbon_census_1]

The enrichment study had a different but related limitation: with n=3 per group, pairwise Mann–Whitney tests had a minimum achievable p-value of 0.10, preventing FDR-corrected significance for individual OTUs. Effect sizes, including CLR differences and PERMANOVA R² values, remained interpretable, but biological attribution was limited. [src: lignin_community_enrichment]

The bacterial Round 2 history effect was statistically supported, with Round 1 history explaining 58.9% of variance (F=14.31, R²=0.589, p=0.002), while the current carbon source explained 32.7% (F=4.85, R²=0.327, p=0.018). However, significant PERMDISP results for 16S (p=0.0004) and ITS (p=0.0001) indicate that dispersion differences contributed to PERMANOVA separation. [src: lignin_community_enrichment]

Fungal occupancy patterns were especially difficult to interpret as activity evidence. ITS replicate Bray–Curtis distances reached 0.99–1.00 for several Round 2 groups, and the ITS Round 2 history effect was not statistically detectable (p=0.090). Low diversity, uneven sequencing depth, exclusion of sample LL_1, and incomplete environmental reference coverage were reported as possible contributors. [src: lignin_community_enrichment]

## Recommended Evidence Chain

A compound-specific environmental catabolism claim should combine:

1. a structurally resolved compound identity;
2. a plausible catabolic pathway or reaction signature;
3. a genome or metagenome carrying the relevant genes, ideally with pathway-completeness evidence;
4. environmental detection of the carrier organism or genes in the target habitat;
5. transcript, protein, metabolite, isotope-tracing, or growth evidence showing activity under relevant conditions. [src: enigma_carbon_census_1]

For enrichment experiments, the chain should additionally include substrate disappearance, product formation, growth attribution, and ideally genome-resolved or isotope-linked evidence connecting the process to specific organisms. The lignin study measured community restructuring and historical persistence but did not include these direct process measurements. [src: lignin_community_enrichment]

The Carbon Census reaches the first four layers unevenly for its callable compounds but lacks environmental measurements of compound degradation. Its 74 organism-dark compounds therefore remain resource-dark discovery targets rather than evidence that the compounds are biologically inaccessible or unused. [src: enigma_carbon_census_1]

## Implications for Enrichment Design

The atlas is most valuable as a siting tool. The strong periphyton signal suggests freshwater-biofilm inocula for enrichments targeting aromatic-utilizer communities, while the broader dark set requires enrichment and metagenomic discovery rather than inference from taxon abundance alone. [src: enigma_carbon_census_1]

For the callable aromatic compounds, the concentration of predicted utilizers in Burkholderiales provides a plausible source-selection hypothesis, but enrichment outcomes should be evaluated with compound disappearance, growth, metabolite products, and genetic evidence. Such measurements would test whether environmental occupancy corresponds to realized catabolic activity. [src: enigma_carbon_census_1]

The lignin passaging experiment suggests that enrichment design must account for sequence and history effects. Communities with lignin histories remained Pseudomonas-dominated in Round 2, whereas communities with lignin-plus-labile-carbon histories remained more Acinetobacter- and Enterobacter-associated; Round 1 history explained more Round 2 bacterial variance than the current carbon source. [src: lignin_community_enrichment]

Accordingly, matched current conditions alone may not produce equivalent communities or equivalent functional outcomes. Parallel passage histories, direct chemistry, metagenomics, and activity assays are needed to determine whether observed ecological memory reflects persistent catabolic capacity, priority effects, cross-feeding, or physiological carryover. [src: lignin_community_enrichment]

## Open Directions

- Pair SSO and periphyton samples with compound-resolved incubations, metabolomics, and stable-isotope probing to test whether abundant predicted genera actively assimilate target aromatics. [src: enigma_carbon_census_1]
- Reanalyze NMDC soil/freshwater contrasts using study-aware mixed models or sample-level permutations to separate robust occupancy structure from study and compositional effects. [src: enigma_carbon_census_1]
- Search metagenomes from high-occupancy habitats for the specific catabolic genes and pathway completeness associated with each callable compound, then compare gene presence with compound turnover. [src: enigma_carbon_census_1]
- Use metatranscriptomics or proteomics during enrichment to determine whether predicted pathways are expressed rather than merely encoded. [src: enigma_carbon_census_1]
- Apply the same occupancy-to-activity framework to the 74 resource-dark compounds after targeted literature mining and enrichment-based genome recovery. [src: enigma_carbon_census_1]
- Repeat lignin enrichments with n>=5 per group and measure lignin disappearance, aromatic intermediates, growth, and isotope incorporation to test whether the dominant taxa directly perform the inferred catabolism. [src: lignin_community_enrichment]
- Compare identical Round 2 conditions across multiple independently generated Round 1 histories using metagenomics and time-resolved metabolomics to identify the mechanism and persistence of [[concepts/ecological-memory]]. [src: lignin_community_enrichment]
- Test whether Flavobacterium, Comamonas, Pseudomonas, or Acinetobacter carry complete aromatic-catabolism pathways and express them during lignin enrichment, rather than inferring function from genus-level abundance. [src: lignin_community_enrichment]

## Related Source

See [[summaries/enigma_carbon_census_1__REPORT]] for the complete census, atlas results, limitations, and proposed enrichment strategy.

See also: [[summaries/field_vs_lab_fitness__REPORT]]

See also: [[summaries/genotype_to_phenotype_enigma__REPORT]]

See also: [[summaries/lignin_community_enrichment__REPORT]]

See also: [[summaries/metabolic_capability_dependency__REPORT]]

See also: [[summaries/pgp_pangenome_ecology__REPORT]]

See also: [[summaries/pitfalls]]

See also: [[summaries/pseudomonas_carbon_ecology__REPORT]]

See also: [[summaries/t4ss_cazy_environmental_hgt__REPORT]]