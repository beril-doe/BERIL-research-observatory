---
type: "Summary"
description: "Prioritizes experimentally testable functions across 57,011 bacterial dark genes."
doc_type: short
full_text: "sources/functional_dark_matter__REPORT.md"
---

# Functional Dark Matter — Summary

## Overview

This report builds a unified catalog of functionally dark genes across 48 Fitness Browser organisms and converts it into experimentally actionable priorities. It integrates fitness phenotypes, essentiality, pangenome conservation, co-regulation, gene neighborhoods, cross-organism concordance, environmental metadata, GapMind pathway gaps, and Bakta reannotation. Two complementary prioritization strategies are developed: an evidence-weighted route for genes with converging, testable hypotheses and a conservation-weighted route for broadly conserved genes that remain poorly understood. [src: functional_dark_matter]

The report frames [[concepts/resource-darkness]] as a tractable experimental problem rather than a single undifferentiated annotation deficit. It proposes [[entities/random-barcode-transposon-sequencing|RB-TnSeq]], [[entities/crispri|CRISPRi]], broad phenotypic screens, and expansion of the organism collection as the main routes to characterization. [src: functional_dark_matter]

## Scale and structure of the dark-gene catalog

- The catalog contains **57,011 dark genes** among **228,709 genes** from 48 organisms, representing **24.9%** of the total.
- **17,344** dark genes are experimentally actionable: **7,787** have strong fitness effects (`|fitness| ≥ 2`) and **9,557** are essential because viable transposon mutants were not recovered.
- **39,532** dark genes have links to the pangenome, while **6,142** belong to ICA fitness modules that provide co-regulation-based function hypotheses.
- **511** genes are both accessory and strongly fitness-active, making them especially relevant to biogeographic and niche-adaptation analyses.
- Dark-gene prevalence varies substantially among organisms, suggesting that annotation depth contributes to the observed differences rather than differences in true functional content alone. [src: functional_dark_matter]

The report introduces a five-level darkness spectrum based on six evidence flags: domain annotation, ortholog assignment, function prediction, co-fitness partner, fitness or essentiality phenotype, and pangenome context.

| Tier | Name | Genes | Interpretation |
|---|---|---:|---|
| T1 | Void | 4,273 | No evidence lines |
| T2 | Twilight | 12,282 | One clue |
| T3 | Dusk | 16,103 | Two converging hints |
| T4 | Penumbra | 22,500 | Substantial, testable evidence |
| T5 | Dawn | 1,853 | Nearly characterized |

Only 4,273 genes are in the zero-evidence T1 category; most dark genes have at least one clue, and T4 genes constitute the largest group. This supports a tiered strategy in which T1 genes receive broad screens, T4 genes receive targeted experiments, and T5 genes receive confirmatory validation. [src: functional_dark_matter]

## Major evidence layers

### Fitness phenotypes and cross-organism concordance

Fitness profiling supplies direct experimental evidence that many dark genes affect growth under defined conditions. Among dark-gene ortholog groups represented in at least three organisms, **65 groups** show measurable fitness concordance across condition classes. Concordant families include candidates associated with carbon utilization, stress response, nitrogen metabolism, motility, and chemotaxis-related functions. [src: functional_dark_matter]

Examples include OG11386, a DUF5064-containing group with carbon-source concordance across eight organisms; OG05812, a stress-associated group with a Peptidase_M50 domain; and OG10455, a motility-associated group with mechanosensitive-channel domains. The report treats these as conserved phenotype signals, not definitive functional assignments. [src: functional_dark_matter]

A dark-versus-annotated null comparison found no significant difference in cross-organism concordance: the Mann–Whitney test gave **p = 0.17**, with both groups having a median concordance of 1.0. This supports the hypothesis that dark genes with orthologs behave like real functional genes rather than random annotation noise. [src: functional_dark_matter]

### Metabolic gap context

[[entities/gapmind|GapMind]] analysis found **1,256 organism–pathway pairs** in 44 Fitness Browser-linked species where nearly complete pathways co-occur with dark genes. Frequently represented gaps include fucose, rhamnose, sorbitol, myoinositol, and gluconate utilization, as well as asparagine biosynthesis. [src: functional_dark_matter]

These are organism-level co-occurrences, not direct gene-to-enzyme matches. A supplementary domain-matching analysis narrowed the candidates to **42,239 gene–pathway hits** involving **3,186 dark genes**: 5,398 high-confidence EC-prefix matches, 4,687 medium-confidence PFam matches, and 32,154 low-confidence keyword matches. Direct gene-to-step assignments still require structure prediction, EC-level validation, or enzymology. This motivates [[concepts/metabolic-model-gapfilling]] as a potential cross-document theme. [src: functional_dark_matter]

### Pangenome conservation

Initial Fitness Browser-scale breadth analysis was poorly discriminating: **99.9%** of 30,756 dark-gene clusters mapped to “universal” root-level eggNOG groups. A species-count variant improved resolution, with counts ranging from 1 to 33 species; its rankings correlated strongly with the original rankings (**Spearman ρ = 0.982**) but had only 62% top-50 and 58% top-100 overlap. [src: functional_dark_matter]

The expanded analysis queried the full GTDB r214 pangenome of **27,690 species**. Across 11,774 dark-gene root OGs, species counts ranged from 1 to 27,482, with a median of 135 and a mean of 2,128. OG propagation added pangenome assignments for **5,206** dark genes, increasing pangenome coverage from 32,791 genes (57.5%) to 37,997 (66.6%). [src: functional_dark_matter]

At the OG level, **55.9%** were kingdom-level, occurring across multiple phyla; 6.5% were classified as mobile, and the remaining groups were distributed across class, family, genus, phylum, order, and species tiers. Independently, genes were classified as strong testable hypotheses (6.0%), weak leads (52.5%), or true knowledge gaps (41.5%). The highest-priority gaps combine broad conservation with little or no functional evidence. COG0468, COG0443, and COG0491 are highlighted as pan-bacterial knowledge gaps. [src: functional_dark_matter]

This motivates [[concepts/pangenome-integration]] and [[concepts/evidence-triangulation]].

### Gene neighborhoods, synteny, and co-fitness

A positional neighborhood analysis found that 30,190 dark genes (52.9%) share a predicted operon with an annotated gene. However, the report cautions that simply having an annotated neighbor is weak evidence: 97.2% of dark genes have at least one annotated gene within a five-gene window, a rate expected given the overall 75% annotation rate. Dark genes have a mean annotated-neighbor fraction of 63.6%, below the genome-wide baseline, suggesting that dark genes may cluster with other dark genes. [src: functional_dark_matter]

Cross-species synteny strengthened this evidence. Of 21,011 dark-gene/partner pairs, 17,058 showed neighborhood conservation in at least one other organism and 10,150 were conserved in at least three organisms. Independent co-fitness testing of 32,075 non-essential operon pairs identified 2,899 pairs with co-fitness evidence, including 1,129 mutual top-five pairs. **998 pairs** were validated by both conserved synteny and strong co-fitness. [src: functional_dark_matter]

These results support [[concepts/gene-neighborhood-inference]] and [[concepts/cofitness-networks]] while emphasizing that neighborhood-based assignments are hypotheses requiring experimental confirmation.

## Environmental relevance of laboratory phenotypes

Within-species carrier-versus-non-carrier comparisons tested 151 accessory dark-gene clusters across 31 species. Ten clusters showed significant environmental enrichment at FDR < 0.05, including *Pseudomonas putida* genes enriched in human-associated or clinical isolates and *Pseudomonas syringae* genes enriched in plant-associated genomes. The top candidate, *P. putida* N2C3 AO356_11255, was associated with freshwater and soil carriers and had a nitrogen-utilization phenotype. [src: functional_dark_matter]

Across 47 testable lab-to-field comparisons, **29 (61.7%)** showed concordant directions. The one-sided binomial test was marginal against a 0.5 null (**p = 0.072**), whereas Fisher’s combined probability across the individual tests was **p = 0.031**. NMDC validation independently confirmed all **4/4 pre-registered abiotic predictions**:

- Nitrogen-source phenotypes correlated positively with total nitrogen and ammonium nitrogen.
- pH-associated carriers correlated positively with sample pH.
- Anaerobic-associated carriers correlated negatively with dissolved oxygen.

A separate NMDC trait analysis confirmed all seven pre-registered trait-condition predictions, but the report treats these correlations cautiously because carrier abundance and community trait scores can be compositionally coupled. Exploratory tests had a very high significance rate, likely reflecting the dominance of ubiquitous genera such as *Pseudomonas*, *Klebsiella*, and *Bacteroides*. These findings support [[concepts/genome-ecology-validation]] but do not establish causal gene–environment relationships. [src: functional_dark_matter]

## Prioritized candidates and experimental routes

### Route A: evidence-weighted prioritization

A six-axis score combines fitness importance, conservation, inference quality, pangenome distribution, biogeographic evidence, and tractability. The top 100 candidates span 22 organisms; 82% have high-confidence hypotheses supported by at least three evidence types, 85 have module-based predictions, and 97 have domain annotations. [src: functional_dark_matter]

The leading candidate is *P. putida* N2C3 AO356_11255, with a predicted D-alanyl-D-alanine carboxypeptidase function, an EamA domain, a nitrogen fitness effect of 3.4, and the strongest reported lab–field signal (OR = 44). Other leading candidates include MR-1 genes 202463, 199738, 203545, and 202450. The latter three are K03306-associated paralogs with nitrogen phenotypes and should be compared through single- and double-mutant experiments. [src: functional_dark_matter]

### Essential dark genes

Essential genes are underrepresented in fitness-centric rankings because they lack viable transposon mutants and therefore lack ordinary fitness profiles. A separate five-axis score prioritizes 9,557 essential dark genes using neighborhood context, conservation, phylogenetic breadth, domains, and CRISPRi tractability. [src: functional_dark_matter]

The leading candidates include *E. coli* Keio gene 14796, with a YbeY domain and an ion-transport hypothesis; MR-1 gene 200382, associated with RimP_N/DUF150_C domains and a predicted ribosome-assembly role; and *Klebsiella oxytoca* BWI76_RS08540, associated with OmpA/TIGR02802 domains and a cell-division hypothesis. The report recommends CRISPRi knockdown rather than transposon disruption for these genes. [src: functional_dark_matter]

### Route B: conservation-weighted discovery

The second route ranks genes and OGs by conservation multiplied by ignorance. It favors broadly conserved true knowledge gaps rather than genes with the strongest existing condition-specific evidence. Its first-ranked OGs include COG0468, COG0443, and COG0491, each occurring across tens of thousands of species or nearly so while lacking functional hypotheses. [src: functional_dark_matter]

The two routes are complementary: Route A is suited to targeted experiments with predicted conditions, whereas Route B is suited to broad screens seeking fundamentally new functions. Their organism sets share 39 organisms but differ in ordering and in a small number of selected organisms.

## Organism-level experimental coverage

A greedy evidence-weighted set-cover algorithm selected **42 organisms from 28 genera**, covering 95% of composite priority. MR-1 ranks first because it combines 121 historically profiled conditions, 587 scored dark genes, and strong fitness effects. Three MR-1 experiments—stress, nitrogen-source, and carbon-source screens—cover 111 top-500 candidates, or 20.8%.

The conservation-weighted set also selects 42 organisms and covers **95.6%** of importance-weighted priority. *Sinorhizobium meliloti* ranks first with 1,630 OGs and 195 kingdom-level gaps, followed by *P. putida*, MR-1, *Bacteroides thetaiotaomicron*, and *Klebsiella michiganensis*. [src: functional_dark_matter]

An extended pool of 73 organisms, including 25 non-Fitness Browser organisms, produces a 50-organism set covering **98.7%** of OGs across six phyla. This adds representatives from Bacillota, Actinomycetota, and Campylobacterota, including [[entities/bacillus-subtilis|*Bacillus subtilis*]], [[entities/mycobacterium-tuberculosis|*Mycobacterium tuberculosis*]], and [[entities/campylobacter-jejuni|*Campylobacter jejuni*]]. The extension addresses the major taxonomic bias of the original collection: 37 of 48 Fitness Browser organisms are Pseudomonadota. [src: functional_dark_matter]

## Recommended campaign

1. **MR-1 stress RB-TnSeq:** test oxidative, osmotic, metal, heat, and pH stress, prioritizing gene 202463 and related PF01145 candidates.
2. **MR-1 nitrogen RB-TnSeq:** test nitrogen limitation and amino-acid supplementation, including the K03306 paralog trio 199738/203545/202450.
3. ***E. coli* CRISPRi:** knock down the top essential dark genes, beginning with Keio:14796.
4. ***P. putida* N2C3 validation:** test AO356_11255 under nitrogen limitation and compare its phenotype with carrier-environment distributions.
5. **Broad discovery screens:** use diverse condition panels for T1 Void and T2 Twilight genes lacking condition predictions.
6. **Non-Fitness Browser expansion:** construct or deploy TnSeq/CRISPRi resources in missing phyla to test whether conserved unknowns retain functions across native genomic contexts.

## Main limitations and tensions

- The dark-gene count likely overestimates true unknowns because many genes labeled hypothetical in the Fitness Browser have newer annotations elsewhere.
- Fitness Browser condition coverage is uneven, favoring organisms such as MR-1 with deep experimental profiling.
- GapMind results are organism-level co-occurrences rather than direct gene-to-pathway assignments.
- Module, neighborhood, synteny, and co-fitness predictions are indirect evidence, not functional proof.
- NMDC validation is mostly genus-level and vulnerable to compositional coupling; only four pre-registered abiotic predictions were formally testable.
- The stress-versus-carbon/nitrogen accessory hypothesis was rejected in the opposite direction: stress dark genes were 23.0% accessory versus 25.5% for carbon/nitrogen genes (**p = 0.013**). This is a substantive tension with the simple expectation that stress functions should be more accessory, and motivates further analysis of [[concepts/core-accessory-resistance]] and condition-specific conservation.
- Ranking is robust in overall correlation but sensitive at the top of the list: alternative weight schemes retain **ρ > 0.93** overall, while specific top-50 lists can retain only 64% of candidates. [src: functional_dark_matter]

## Core contribution

The report’s central contribution is an integrated, experimentally grounded framework for bacterial functional dark matter. It shows that many unknown genes already have measurable phenotypes, conserved genomic context, pangenome links, or environmental signals, and it turns those evidence layers into ranked genes, organism covering sets, and concrete RB-TnSeq or CRISPRi experiments. The resulting framework connects [[concepts/resource-darkness]], [[concepts/fitness-conservation]], [[concepts/experimental-functional-prioritization]], [[concepts/pangenome-integration]], [[concepts/gene-neighborhood-inference]], and [[concepts/genome-ecology-validation]].

## Open Directions

- Apply AlphaFold-based structure prediction and enzymology to the 42,239 GapMind domain-compatible candidates, prioritizing the 5,398 EC-prefix matches.
- Run permutation or sample-label-shuffling null tests on raw NMDC matrices to quantify compositional inflation in abiotic and trait correlations.
- Recalculate conservation-weighted coverage using species-level rather than genus-level assignments for non-Fitness Browser organisms.
- Compare the top conserved knowledge gaps across Gram-negative, Gram-positive, Actinobacterial, and Campylobacterial hosts.
- Use robust-rank indicators to select candidates that remain in the top tier across alternative scoring weights.
- Integrate NMDC proteomics and metabolomics with carrier abundance to seek evidence more directly connected to gene function. [src: functional_dark_matter]

## Related Concepts
- [[concepts/shared-stress-biology]]
- [[concepts/functional-redundancy]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/cultivation-bias]]
- [[concepts/two-speed-genome]]
- [[concepts/mobile-genetic-elements]]
- [[concepts/multi-omics-integration]]

## Entities
- [[entities/bakta]]
- [[entities/marinobacter]]
- [[entities/pseudomonas-aeruginosa]]
- [[entities/staphylococcus-aureus]]
- [[entities/streptococcus-pneumoniae]]
- [[entities/acinetobacter-baumannii]]
- [[entities/amrfinderplus]]
- [[entities/uniprot]]
- [[entities/interproscan]]
- [[entities/modelseed]]
- [[entities/berdl]]
