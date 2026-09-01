---
type: "Concept"
sources: ["summaries/phb_granule_ecology__REPORT.md"]
description: "Environmental variability selects for PHB storage pathways in microbial genomes."
---

# Feast–Famine Selection

## Definition

The feast–famine selection hypothesis proposes that microbial carbon-storage pathways are favored when organisms experience alternating periods of resource abundance and scarcity. In the PHB context, carbon accumulated during a resource-rich interval can be stored as intracellular polyhydroxybutyrate and subsequently mobilized during carbon limitation. The hypothesis therefore predicts that PHB biosynthesis should be enriched in habitats with fluctuating carbon inputs rather than uniformly distributed across environments. [src: phb_granule_ecology]

This ecological mechanism connects [[entities/polyhydroxybutyrate]] storage with [[concepts/shared-stress-biology]], because PHB granules may also contribute to resistance against osmotic, oxidative, UV, temperature, and freezing stresses. [src: phb_granule_ecology]

## Evidence from the PHB pangenome survey

The report tested this hypothesis across 27,690 GTDB species by using phaC, the committed PHA synthase step, as the primary marker of PHB capacity. Overall, 21.9% of species carried phaC and 21.7% had a complete phaC + phaA/phaB pathway. [src: phb_granule_ecology]

PHB prevalence followed the predicted environmental gradient:

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

[src: phb_granule_ecology]

The association between PHB presence and environmental variability was highly significant (**chi2 = 1,656.36, p ~ 0, dof = 2**). Plant-associated, soil, and wastewater environments—classified as relatively variable—had substantially higher PHB prevalence than marine, clinical, and animal-associated environments, which were classified as relatively stable. This is strong comparative evidence supporting the feast–famine prediction, although environmental categories are proxies rather than direct measurements of temporal carbon fluctuation. [src: phb_granule_ecology]

## Independence from genome size

A major qualification is that PHB-positive species had larger genomes than PHB-negative species, with median genome sizes of **4.34 Mbp** and **2.44 Mbp**, respectively. Genome size also correlated with AlphaEarth-derived environmental niche breadth (**rho = 0.302, p = 1.5 × 10^-43**). [src: phb_granule_ecology]

PHB-positive species initially appeared to have broader environmental distributions: median AlphaEarth embedding variance was **0.3295** for PHB-positive species and **0.2472** for PHB-negative species (**Mann–Whitney p = 1.88 × 10^-6**). After controlling for genome size, however, the association largely disappeared, changing from a raw **rho = 0.106** to a partial **rho = −0.047 (p = 0.037)**. The effect size fell by 56.3% and reversed sign. [src: phb_granule_ecology]

This distinction is important for [[concepts/phylogenetic-confounding]] and [[concepts/ecological-generalism]]: PHB presence is not independent evidence that the pathway itself causes broad niche occupation. Larger genomes may encode more metabolic capabilities generally, making both PHB presence and apparent niche breadth downstream correlates of genome architecture. [src: phb_granule_ecology]

The environmental PHB signal was nevertheless retained within every genome-size quartile. High-variability environments had 4.4-fold, 4.6-fold, 3.1-fold, and 1.4-fold greater phaC prevalence than low-variability environments in quartiles Q1 through Q4, respectively; each comparison had p < 1 × 10^-11. The persistence of this pattern provides stronger evidence that environmental selection for PHB is not simply a by-product of larger genomes. [src: phb_granule_ecology]

## Phylogenetic structure and gene mobility

Feast–famine selection operates within a strongly phylogenetically structured distribution. Pseudomonadota had 60.9% phaC prevalence, Myxococcota had 52.9%, and Halobacteriota had 34.4%, whereas several major phyla had no detected phaC. Within 248 tested families, 41 were enriched and 62 were depleted after Bonferroni correction. Enriched families skewed toward freshwater and wastewater, while depleted families skewed toward marine and host-associated environments. [src: phb_granule_ecology]

The pathway is also evolutionarily mobile. The analysis identified **311 potential phaC acquisition events** and **278 potential loss events** from phylogenetically discordant distributions. Among discordant phaC-positive species, **60.1%** carried phaC as accessory genome, compared with **32.3%** across all phaC-positive species. This elevated accessory fraction is consistent with ongoing [[concepts/horizontal-gene-transfer]], but the events remain putative because they were inferred from family-level discordance and core/accessory status rather than a direct phaC gene-tree/species-tree reconciliation. [src: phb_granule_ecology]

## Metagenomic cross-validation

NMDC metagenomic data provided an independent, though indirect, test. Pangenome-derived phaC prevalence was mapped to 3,014 of 3,492 NMDC taxon columns, and PHB inference scores were calculated for 6,365 samples with a median 87.2% of taxonomic abundance matched to pangenome genera. [src: phb_granule_ecology]

The inferred PHB score correlated negatively with depth (**rho = −0.119, p = 1.14 × 10^-21**) and positively with temperature (**rho = +0.088, p = 1.86 × 10^-12**). These directions are compatible with greater PHB capacity in shallower, warmer, and potentially more dynamic carbon environments, but all reported effect sizes were modest (**|rho| < 0.12**). [src: phb_granule_ecology]

In a genus-level comparison, PHB-high genera were more abundant in NMDC samples than PHB-low genera (**Mann–Whitney p = 8.41 × 10^-22**). This provides [[concepts/evidence-triangulation]] across pangenomic prevalence and metagenomic community composition, while not demonstrating that PHB is actively synthesized in the sampled communities. [src: phb_granule_ecology]

## Evidence grade and interpretation

**Strongly supported:** PHB biosynthetic capacity is enriched in broad environmental categories expected to experience greater resource variability, and the enrichment persists after genome-size stratification. [src: phb_granule_ecology]

**Qualified:** PHB-positive species show greater apparent environmental breadth in raw analyses, but genome size largely explains this association. The report does not establish that PHB itself causes ecological generalism. [src: phb_granule_ecology]

**Consistent but indirect:** NMDC associations with depth, temperature, and genus abundance support the pangenome pattern, but point-in-time abiotic measurements do not directly quantify temporal feast–famine dynamics. [src: phb_granule_ecology]

**Mechanistically plausible but not isolated:** PHB may be selected not only for carbon buffering but also for stress protection, redox balance, cryoprotection, and other functions. Consequently, feast–famine selection is supported as an important selective force but is not demonstrated to be the sole driver of PHB distribution. [src: phb_granule_ecology]

## Tensions

### Environmental selection versus genome-size effects

The raw association between PHB and niche breadth suggests that PHB-positive species occupy broader environmental spaces, but controlling for genome size nearly eliminates the relationship and reverses its sign. In contrast, PHB enrichment by environmental variability remains within all genome-size quartiles. Thus, genome size weakens the claim that PHB independently promotes generalism but does not remove the more direct environment-type association. [src: phb_granule_ecology]

### Temporal variability versus environmental proxies

The environmental categories used in the pangenome analysis classify habitats as expected to differ in variability, but they do not measure temporal carbon fluctuations directly. NMDC abiotic variables provide independent context, yet they are mostly point-in-time observations and show modest correlations. The feast–famine interpretation is therefore well supported as a cross-environment pattern but remains less directly tested at the level of measured temporal resource dynamics. [src: phb_granule_ecology]

### PHB capacity versus PHB activity

The primary evidence measures gene presence or inferred taxonomic capacity rather than PHB granule formation or expression in situ. The report’s metagenomic inference therefore establishes potential community capacity, not active PHB synthesis under a particular feast–famine regime. [src: phb_granule_ecology]

## Open Directions

- Apply phylogenetic logistic regression to the species-by-environment table to test whether the high-variability enrichment remains after jointly controlling for shared ancestry and genome size. [src: phb_granule_ecology]
- Link NMDC ecosystem labels and ENVO terms to repeated abiotic measurements to test whether phaC prevalence or inferred PHB capacity tracks directly measured temporal carbon variability. [src: phb_granule_ecology]
- Use Fitness Browser phaC mutant phenotypes under alternating carbon-rich and carbon-limited conditions to test whether the pathway provides a direct feast–famine fitness advantage. [src: phb_granule_ecology]
- Reconstruct a phaC gene tree and reconcile it with the species tree to distinguish environmental acquisition from phylogenetic inheritance and quantify the role of [[concepts/horizontal-gene-transfer]]. [src: phb_granule_ecology]
- Combine PHB gene presence with transcriptomic, proteomic, metabolomic, or direct granule measurements to separate [[concepts/latent-metabolic-capabilities]] from active PHB storage. [src: phb_granule_ecology]

## Source

- [[summaries/phb_granule_ecology__REPORT]]