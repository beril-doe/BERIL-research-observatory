---
type: "Concept"
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/truly_dark_genes__REPORT.md", "summaries/snipe_defense_system__REPORT.md", "summaries/prophage_amr_comobilization__REPORT.md", "summaries/pathway_capability_dependency__REPORT.md", "summaries/module_conservation__REPORT.md", "summaries/metal_specificity__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/metal_cross_resistance__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/fitness_effects_conservation__REPORT.md", "summaries/field_vs_lab_fitness__REPORT.md"]
description: "Fitness importance correlates modestly with pangenome conservation, but context matters."
---

# Fitness Importance and Pangenome Conservation

## Overview

[[concepts/fitness-conservation]] describes the relationship between measured gene fitness effects and the likelihood that a gene is retained across genomes. Across approximately 194,000 genes from 43 bacteria, stronger or broader fitness effects were associated with greater pangenome conservation, but the association was modest. [src: fitness_effects_conservation]

The field-versus-lab analysis found that fitness importance was associated with conservation, while ecological condition type was a weak discriminator. Genes with strong defects in field-stress and field-core experiments were enriched in the core genome, but lab-nutrient genes showed comparable enrichment, and field-specific genes were not significantly more conserved than lab-specific genes. [src: field_vs_lab_fitness]

The module-conservation analysis extends this comparison from individual genes to co-regulated functional units. ICA module genes were 86.0% core, compared with 81.5% for all genes, an enrichment of 4.5 percentage points (OR=1.46, p=1.6e-87). Among 974 modules with at least three mapped genes, 577 (59%) were >90% core, 349 (36%) were mixed, and 48 (5%) were <50% core; the median module was 93.4% core. [src: module_conservation] Thus, many fitness-response units are embedded in the conserved genome, although this result describes genes with measurable fitness variation and does not include essential genes that lack transposon insertion data. [src: module_conservation]

Metal studies refine this relationship rather than producing a single conservation value. The metal cross-resistance analysis found a gradient from general-stress genes to metal-shared genes to metal-specific genes, with progressively lower conservation. [src: metal_cross_resistance] The Pan-Bacterial Metal Fitness Atlas nevertheless found that the complete set of metal-important genes was strongly core-enriched: 12,838 records were 87.4% core versus 76.9% for baseline genes (OR=2.08, p=4.3e-162). [src: metal_fitness_atlas]

The metal-specificity analysis separates these effects more directly. Among 7,609 metal-important records from 24 organisms, 4,177 (54.9%) were metal-specific, 2,888 (38.0%) were generally sick across conditions, and 544 (7.2%) were both metal- and stress-sensitive. Metal-specific genes remained core-enriched, but their pooled core fraction was 84.8% and organism-mean fraction was 88.0%, compared with 90.2% for general sick genes; the difference was significant across organisms (CMH p=0.011). [src: metal_specificity]

Taken together, the corpus supports a general relationship between functional importance and conservation while cautioning that fitness alone is a weak standalone classifier of core status. Gene architecture, experimental coverage, phylogenetic history, ecological context, module organization, and whether a function is broadly stress-related or chemically specialized must be considered alongside fitness measurements. [src: fitness_effects_conservation, field_vs_lab_fitness, module_conservation, metal_cross_resistance, metal_fitness_atlas, metal_specificity]

## Evidence from *Desulfovibrio vulgaris* Hildenborough

The field-versus-lab analysis classified 757 *Desulfovibrio vulgaris* Hildenborough experiments into six condition classes: lab-nutrient (237), field-core (204), lab-other (140), field-stress (78), heavy-metals (55), and lab-antibiotic (43). The broad classification contained 337 field-related and 420 laboratory-related experiments. [src: field_vs_lab_fitness]

Among 2,725 non-essential genes with both fitness measurements and pangenome links, 76.3% were classified as core. A further 678 essential genes lacked fitness data because transposon mutants were not recovered; 80.1% of these genes were core and they were excluded from condition-class comparisons. [src: field_vs_lab_fitness]

Using fitness < -2 to define strong importance, conservation varied by condition class. [src: field_vs_lab_fitness]

| Condition class | Important genes | Core fraction | Odds ratio vs baseline | FDR q |
|---|---:|---:|---:|---:|
| Field-stress | 298 | 83.6% | 1.58 | 0.026 |
| Field-core | 376 | 82.4% | 1.46 | 0.026 |
| Lab-other | 292 | 81.5% | 1.37 | 0.073 |
| Lab-nutrient | 452 | 81.4% | 1.36 | 0.037 |
| Lab-antibiotic | 109 | 73.4% | 0.86 | 0.49 |
| Heavy-metals | 198 | 71.2% | 0.77 | 0.14 |

Field-stress, field-core, and lab-nutrient genes were significantly enriched in the core genome after Benjamini–Hochberg correction. [src: field_vs_lab_fitness] This pattern supports a connection between [[concepts/condition-dependent-essentiality]] and conservation, but does not establish that field relevance itself causes greater conservation. [src: field_vs_lab_fitness]

The heavy-metal value of 71.2% core is important when interpreting the newer atlas and specificity analyses. It came from a *D. vulgaris* analysis of condition-specific heavy-metal genes, whereas the atlas included all genes with a metal fitness defect across organisms and the specificity study separated metal-specific from broadly sick genes. [src: field_vs_lab_fitness, metal_fitness_atlas, metal_specificity] These analyses address different biological sets and should not be treated as interchangeable estimates of metal-gene conservation. [src: field_vs_lab_fitness, metal_fitness_atlas, metal_specificity]

## Fitness magnitude versus ecological context

The broader cross-organism analysis showed a conservation gradient across fitness categories. Essential genes with no viable mutants were 82% core (27,693 genes), compared with 78% of genes often sick in more than 10% of experiments (15,989), 70% of mixed genes (20,739), 72% of sometimes-sick genes (25,201), 66% of always-neutral genes (94,889), and 70% of sometimes-beneficial genes (9,705). When binned by strongest fitness effect, essential genes were 82.2% core, genes with `min_fit < -3` were 77.7% core, and genes with `min_fit -1 to 0` were 66.4% core. [src: fitness_effects_conservation]

Fitness breadth showed the same direction: essential genes were 82% core, genes affecting fitness in 20 or more experiments were 79% core, genes affecting 6–20 experiments were 73% core, genes affecting 1–5 experiments were 71% core, and genes with no recorded experiments were 66% core. The association was statistically significant but small (Spearman rho = 0.086, p = 8.1e-230). [src: fitness_effects_conservation]

Specificity analysis in the *D. vulgaris* dataset found 50 lab-specific genes with fitness defects only in laboratory conditions, of which 96.0% were core, compared with 52 field-specific genes, of which 88.5% were core. The difference was not statistically significant (Fisher exact odds ratio = 0.32, p = 0.27). [src: field_vs_lab_fitness]

The strongest contrast in that analysis was between universally important and neutral genes: 352 universally important genes were 79.8% core, whereas 2,083 neutral genes were 74.5% core; this comparison was significant (odds ratio = 1.35, p = 0.033). [src: field_vs_lab_fitness] Together with the broader cross-organism gradient, this supports the interpretation that the magnitude or breadth of fitness importance may matter more for conservation than whether an experiment is labeled field or laboratory. [src: fitness_effects_conservation, field_vs_lab_fitness]

However, fitness effects were weak predictors of binary core status in cross-validated logistic regression. The field-only model had a CV-AUC of 0.517, the lab-only model 0.531, and the combined field-plus-lab model 0.548. A full model adding gene length reached 0.645, making gene length a substantially stronger predictor than either fitness dimension alone. [src: field_vs_lab_fitness] These results motivate combining fitness data with broader [[concepts/pangenome-integration]] rather than treating fitness as a standalone conservation classifier. [src: field_vs_lab_fitness]

The broader analysis also challenges a simple burden model. Core genes were more likely than auxiliary genes to show positive fitness effects when deleted: 24.4% of core genes were ever beneficial versus 19.9% of auxiliary genes, corresponding to an odds ratio of 0.77 for auxiliary versus core genes. Core and auxiliary genes had distinct fitness distributions, with core genes showing heavier tails in both negative and positive directions. This suggests the hypothesis that core genes are more deeply embedded in critical pathways and therefore can be harmful in some conditions but burdensome in others, rather than being uniformly advantageous to retain. [src: fitness_effects_conservation]

Genes tagged with strong condition-specific effects in the `specificphenotype` table were 77.3% core, compared with 70.3% for genes without specific phenotypes (OR = 1.78, p = 1.8e-97). In addition, 4,450 genes (2.7%) fit an “ephemeral niche gene” pattern: neutral overall but critical in one condition. These genes were more common among core genes (3.0%) than auxiliary genes (1.7%) or singleton genes (1.6%). [src: fitness_effects_conservation] These results suggest that condition-specific effects are not necessarily accessory and may be especially detectable in core genes with multiple functional roles. [src: fitness_effects_conservation]

Novel singleton genes showed near-zero mean fitness in the tested assays, suggesting that they were largely invisible under laboratory conditions rather than systematically detrimental. This remains a hypothesis because singleton genes may have poor transposon coverage rather than genuinely neutral effects. [src: fitness_effects_conservation]

## Module-level conservation

The module-conservation analysis provides a direct test of whether fitness-response units follow the conservation pattern observed for individual genes. Across 1,116 ICA modules from 32 organisms, 974 modules had at least three genes mapped to pangenome conservation data. The mapped module genes were 86.0% core compared with 81.5% for all genes, with OR=1.46 and p=1.6e-87. [src: module_conservation]

Most modules were predominantly core: 577 of 974 (59%) were >90% core, 349 (36%) were 50–90% core, and 48 (5%) were <50% core. The median module was 93.4% core. These results strengthen the view that co-regulated fitness response units are often embedded in the conserved genome, but the absolute enrichment remains modest because the baseline core rate is already high. [src: module_conservation]

Module-family breadth did not predict conservation. Families spanning more organisms did not have higher core fractions (Spearman rho=-0.01, p=0.914), suggesting that conservation is more likely to be a property of individual genes or specific functional units than a simple consequence of a module family’s cross-organism scope. The high baseline core rate of approximately 82% also leaves little room for a breadth-related gradient. [src: module_conservation]

Accessory module families nevertheless exist: 38 families had <50% core genes. They may represent horizontally transferred functional units or niche-specific operons, but this interpretation is a hypothesis requiring direct tests of gene mobility, neighborhood structure, and ecological distribution. [src: module_conservation]

No essential genes appeared in any ICA module. This is expected from the experimental design: ICA modules require fitness measurements, while essential genes lack recoverable transposon mutants and therefore have no measured fitness variation. Module conservation should consequently be interpreted as conservation among the non-essential, fitness-measurable genome fraction, not as evidence that essential functions are absent from conserved regulatory systems. [src: module_conservation]

At the level of 52 ICA fitness modules in the *D. vulgaris* field-versus-lab analysis, the mean core fraction was 0.886 and the median was 1.000. Module conservation was not significantly correlated with field activity (Spearman rho = 0.071, p = 0.62). [src: field_vs_lab_fitness] Using the mean core fraction as the classification threshold yielded 21 ecological modules with mean core fraction 0.980, 17 conserved-quiet modules with mean core fraction 0.983, five field-variable modules with mean core fraction 0.829, and nine lab modules with mean core fraction 0.516. [src: field_vs_lab_fitness]

The metal atlas found 183 metal-responsive modules with conservation data, with a mean core fraction of 0.826 and a median of 0.929. [src: metal_fitness_atlas] Both analyses therefore place many environmentally responsive modules in the core genome, but neither establishes that module activity alone predicts conservation. [src: field_vs_lab_fitness, metal_fitness_atlas]

The newer metal-specificity module analysis was inconclusive: per-module z-normalization produced maximum absolute z-scores below 2.0 for most metal experiments because metals represented a small fraction of experiments per organism. The report recommends using the precomputed z-scores from the atlas directly. [src: metal_specificity]

## Metal-specificity and the conservation gradient

The metal-specificity analysis classified 6,504 experiments, including 559 metal experiments (8.6%) and 5,945 non-metal experiments (91.4%). At a 5% non-metal sick-rate threshold, 54.9% of analyzed metal-important genes were metal-specific, 38.0% were general sick, and 7.2% were metal+stress. The classification was qualitatively stable across thresholds, although the exact fraction changed from approximately 41% at a 2% threshold to approximately 67% at 10%. [src: metal_specificity]

Across 22 organisms with pangenome links, metal-specific genes had a pooled core fraction of 84.8% (2,969/3,500) and an organism-mean core fraction of 88.0%. General sick genes were 90.2% core by both the reported pooled and organism-mean summaries, while the baseline was 79.8% pooled and 81.1% organism-mean. Metal+stress genes were 94.3% pooled and 93.6% organism-mean. [src: metal_specificity]

All three categories were core-enriched above baseline, but the Cochran-Mantel-Haenszel test showed that metal-specific genes were less core-enriched than general sick genes across organisms (p=0.011). [src: metal_specificity] This is consistent with a modest [[concepts/core-accessory-resistance]] effect: specialized resistance mechanisms may be somewhat more likely to occur in the accessory genome, while general stress and cellular functions are more deeply conserved. [src: metal_specificity]

The estimate is conservative because approximately 14% of protein-coding genes, about 82% of them core, were putatively essential and absent from fitness data. [src: metal_specificity] The specificity study also excluded seven of 31 metal-tested organisms—ANA3, Dino, Keio, MR1, Miya, PV4, and SB2B—because locus identifiers did not match fitness-matrix index formats; the 24 included organisms accounted for 7,609 of 12,838 atlas records (59.3%). [src: metal_specificity]

Metal-specific genes were 1.64 times more likely than general sick genes to match metal-resistance keywords (12.2% versus 7.8%; Fisher exact OR=1.64, p=2.4e-8). This functional enrichment supports the interpretation that the specificity classification captures biologically meaningful specialized resistance rather than simply general stress sensitivity. [src: metal_specificity]

The strongest novel candidate families were UCP030820 (2/3 metal-specific, 67%), YebC (7/12, 58%), and DUF1043/YhcB (3/6, 50%). UCP030820 was associated with seven metals, YebC with six metals across 11 organisms, and DUF1043/YhcB with five metals across six organisms. [src: metal_specificity] YebC is a plausible mechanistic hypothesis because its reported role in resolving ribosome stalling at proline-rich motifs could become important when metal stress increases demand for proline-rich transporters or chaperones, but this mechanism has not been tested in the reported fitness data. [src: metal_specificity]

YfdZ and the Mla/Yrb system were more pleiotropic, while DUF39 had 0/2 metal-specific records and a mean sick rate of 0.637. These observations make them less suitable as narrowly defined metal-resistance candidates. [src: metal_specificity] Across all 149 novel metal candidate families, 45.6% had a dominant metal-specific classification, compared with 58.2% of annotated families (Fisher exact OR=0.60, p=0.003). [src: metal_specificity]

## The pan-bacterial metal fitness atlas

The Pan-Bacterial Metal Fitness Atlas analyzed 559 metal-related experiments across 31 organisms and 16 metals, including 383,349 gene × metal fitness records from 24 organisms with fitness matrices. Of these records, 12,838 (3.3%) were broadly metal-important and 5,667 (1.5%) met a stricter definition. [src: metal_fitness_atlas]

Metal-important genes were 87.4% core versus 76.9% for baseline genes (OR=2.08, p=4.3e-162), with 21 of 22 organisms showing positive core-enrichment deltas and 14 significant at p<0.05. Essential metal tolerance genes had a mean core-fraction delta of +0.148, nearly twice the +0.081 mean delta for toxic metals (Mann-Whitney U=39, p=0.015, one-sided). [src: metal_fitness_atlas]

The strongest metal-specific enrichments were manganese (+0.198; all 30 important genes core), zinc (+0.151), molybdenum (+0.148), tungsten (+0.145), and iron (+0.116). Twelve of 14 metals were individually significant at p<0.05; cadmium and uranium were not significant, with deltas of -0.010 (p=0.92) and +0.035 (p=0.34), respectively. [src: metal_fitness_atlas]

The atlas identified 2,891 ortholog groups with metal phenotypes, of which 1,182 were conserved across at least two organisms and 601 across at least three. It also identified 149 candidate metal-biology families with conserved phenotypes but incomplete annotation. [src: metal_fitness_atlas] These candidates connect conservation analysis to [[concepts/annotation-gap]] and [[concepts/experimental-functional-prioritization]].

At the module level, 600 metal-responsive ICA module records were identified among 19,453 module × metal-experiment records using per-organism z-scored profiles and a |z| > 2.0 threshold. The 183 responsive modules with conservation data had a mean core fraction of 0.826 and a median of 0.929. [src: metal_fitness_atlas]

A signature of 1,286 KEGG KO terms was used to score 27,702 pangenome species. After genome-size normalization, *Leptospirillum* ranked at the 91st percentile, *Acidithiobacillus* at the 77th, *Marinobacter* at the 75th, and *Sulfobacillus* at the 71st. Bioleaching genera were not significantly enriched as a group after normalization (Mann-Whitney p=0.17), suggesting that metal-associated functions are broadly distributed rather than restricted to specialists. [src: metal_fitness_atlas]

The pangenome result did not validate simple gene repertoire presence/absence as a predictor of metal tolerance. Without normalization, organisms with large open pangenomes dominated rankings, reflecting genome size rather than metal biology. [src: metal_fitness_atlas] This supports integrating gene presence with phenotype and kinetics rather than treating repertoire size as a direct tolerance measure. [src: metal_fitness_atlas]

## Metal cross-resistance adds a conservation gradient

The metal cross-resistance study analyzed 452 metal experiments across 37 organisms and 14 metals, extracting fitness data for 119,561 genes in 28 organisms with at least three metals. It found 317 organism–metal-pair observations across 85 unique metal pairs, with 98.1% of gene-level correlations positive and 99.1% statistically significant at p < 0.05. [src: metal_cross_resistance]

| Gene tier | Genes | Share of metal-important genes | Mean core fraction | Fully core (≥95%) |
|---|---:|---:|---:|---:|
| General stress | 1,484 | 18.2% | 92.0% | 57.2% |
| Metal-shared | 2,306 | 28.3% | 91.0% | 50.4% |
| Metal-specific | 4,372 | 53.6% | 89.8% | 45.7% |

The 11.5 percentage point decline in the fully core fraction from general-stress to metal-specific genes supports a layered evolutionary model: broadly pleiotropic stress defense is deepest in the core, shared metal defense is intermediate, and specialized metal resistance is more variable. [src: metal_cross_resistance]

The cross-resistance tiers and the newer specificity analysis are directionally consistent, although their exact fractions differ because they use different organism sets, thresholds, and definitions. [src: metal_cross_resistance, metal_specificity] Functional keyword analysis similarly found general-stress genes enriched for energy, respiration, and cell-envelope functions, while metal-specific genes were enriched for transporters, efflux, and iron/metal-related functions. [src: metal_cross_resistance]

The metal cross-resistance data identified 318 conserved ortholog groups that were metal-shared in at least two organisms. These families span up to 14 organisms and include cell-envelope, energy-metabolism, DNA-repair, and ion-homeostasis functions. [src: metal_cross_resistance]

## Resistance functions as a contrasting pattern

Lab-antibiotic and heavy-metal fitness-important genes in *D. vulgaris* had the lowest core fractions, at 73.4% and 71.2%, respectively, below the 76.3% baseline. [src: field_vs_lab_fitness] This pattern is consistent with [[concepts/core-accessory-resistance]], in which resistance functions can occupy variable portions of the genome.

The atlas qualifies rather than overturns this interpretation. Its 87.4% core estimate includes genes involved in core cell-envelope, DNA-repair, protein-quality-control, and central-metabolism functions that are vulnerable to metal disruption. [src: metal_fitness_atlas] The specificity analysis shows that even the more narrowly defined metal-specific set remains 88.0% core by organism mean, although it is significantly less core-enriched than general sick genes. [src: metal_specificity]

The low conservation of some resistance categories remains provisional because existing analyses did not directly test genomic mobility, physical linkage, or recent acquisition. Such analyses would connect this concept to [[concepts/mobile-genetic-elements]] and [[concepts/two-speed-genome]]. [src: field_vs_lab_fitness]

The cross-resistance data further show that resistance functions are not uniformly accessory. Across organisms, Co–Ni had a mean gene-fitness correlation of r = 0.56 across 28 organisms, Fe–Zn reached r = 0.61 across six organisms, and Cu–U reached r = 0.51 across five organisms. Aluminum was the most independent metal by mean correlation (r = 0.34), consistent with a distinct toxicity mechanism. [src: metal_cross_resistance]

The low conservation of some metal categories is also sensitive to sampling and definition. The atlas excluded nine organisms lacking Fitness Browser–pangenome links, while the specificity study excluded seven organisms because of locus-ID mismatches. [src: metal_fitness_atlas, metal_specificity] These coverage gaps limit inference about whether specialized metal resistance is consistently more accessory across bacteria. [src: metal_fitness_atlas, metal_specificity]

## Robustness and scope

The rank ordering in the *D. vulgaris* analysis was broadly robust across fitness thresholds from -1 to -3: field-stress genes consistently had the highest conservation, while heavy-metal genes were consistently among the least conserved. [src: field_vs_lab_fitness]

The broader cross-organism results are statistically strong but describe a modest gradient: essential genes were 82% core and always-neutral genes 66% core across approximately 194,000 genes and 43 bacteria. [src: fitness_effects_conservation] The metal atlas reports a stronger aggregate enrichment, but its conservation analysis covers 22 of 31 metal-tested organisms and excludes nine organisms lacking Fitness Browser–pangenome links. [src: metal_fitness_atlas]

The module-conservation study covers 1,116 ICA modules across 32 organisms, but only 29 of 32 organisms had pangenome links; Cola, Kang, and SB2B lacked links because their species had too few genomes in GTDB for pangenome construction. [src: module_conservation] Its module classifications also depend on an upstream membership rule of |Pearson r| >= 0.3 with a maximum of 50 genes per module, while the 90% and 50% core cutoffs are convenient rather than biologically motivated. [src: module_conservation]

The specificity analysis covers 24 organisms and 7,609 of 12,838 metal-important records because of locus-ID incompatibilities. The excluded set includes Keio (*E. coli*), MR1 (*Shewanella*), and ANA3, so the missing records may alter estimates of metal-specificity or conservation. [src: metal_specificity]

The metal atlas has uneven coverage. Cobalt and nickel were tested in 27 and 26 organisms, respectively, while uranium, chromium, mercury, cadmium, selenium, and manganese had only one or two organisms of coverage. [src: metal_fitness_atlas] Metal concentrations varied among organisms, and no dose-response normalization relative to organism-specific tolerance thresholds was performed. [src: metal_fitness_atlas]

The Fitness Browser is concentrated primarily in Proteobacteria, laboratory conditions underrepresent ecological niches, single-gene knockouts do not capture epistasis, and singleton neutrality may reflect poor transposon coverage. [src: fitness_effects_conservation] The metal analyses add phylogenetic non-independence, unequal experiment counts, concentration differences, and incomplete non-metal stress controls as limitations. [src: metal_cross_resistance, metal_fitness_atlas, metal_specificity]

The *D. vulgaris* findings are limited to one organism with a relatively high core fraction and comparatively coarse core/auxiliary classification. [src: field_vs_lab_fitness] The analysis also excludes essential genes without recoverable transposon mutants, depends on manually assigned condition labels, and compares small field-specific and lab-specific sets of 50–52 genes. [src: field_vs_lab_fitness]

The metal BacDive validation was inconclusive: after correcting organism matching and collapsing strains to species-level entries, the effective sample size was 20 independent species, with a multi-metal tolerance correlation of approximately Spearman rho = -0.02 and p > 0.8. [src: metal_cross_resistance] This is a coverage- and power-limited test rather than evidence that gene-level cross-resistance fails to predict environmental metal tolerance. [src: metal_cross_resistance]

## Tensions

The condition-class results support field-stress and field-core genes as significantly conserved, while field-specific genes were not significantly more conserved than lab-specific genes. [src: field_vs_lab_fitness] Module-level analysis likewise found no significant relationship between field activity and conservation, despite identifying highly conserved ecological modules and low-conservation lab modules. [src: field_vs_lab_fitness]

The broader dataset reinforces the general importance–conservation relationship but complicates its interpretation: core genes are more likely to be essential, yet they are also more likely to show beneficial deletion effects and strong condition-specific phenotypes. [src: fitness_effects_conservation]

The module analysis adds a related qualification: module genes are more core than average, but module-family breadth is unrelated to core fraction (rho=-0.01, p=0.914). [src: module_conservation] Thus, conservation of a co-regulated unit does not appear to increase simply because that unit is represented in more organisms. [src: module_conservation]

The metal evidence contains a scope-dependent tension. The *D. vulgaris* heavy-metal condition-specific set was 71.2% core and below baseline, whereas the pan-bacterial atlas found that the full set of metal-important genes was 87.4% core and above baseline. [src: field_vs_lab_fitness, metal_fitness_atlas] The specificity analysis resolves part of this tension by showing that narrowly metal-specific genes are 88.0% core by organism mean but less core-enriched than general sick genes. [src: metal_specificity] The evidence therefore supports different functional tiers rather than a single universal conservation value.

The metal data also introduce a tension between universal direction and variable magnitude. Nearly all metal fitness correlations were positive, but metal-pair strengths differed, from Fe–Zn at r = 0.61 and Co–Ni at r = 0.56 to Al–Co at r = 0.30. [src: metal_cross_resistance] Shared stress biology coexists with chemistry-specific and organism-specific components that remain only moderately predictable. [src: metal_cross_resistance]

The most consistent interpretation is that fitness importance can coincide with conservation, but conservation is not uniquely ecological. It may reflect general functional integration, shared stress biology, gene architecture, module organization, measurement coverage, phylogenetic history, and genome dynamics. [src: fitness_effects_conservation, field_vs_lab_fitness, module_conservation, metal_cross_resistance, metal_fitness_atlas, metal_specificity]

## Open Directions

- Resolve locus-ID mismatches for ANA3, Dino, Keio, MR1, Miya, PV4, and SB2B to recover the remaining 40.7% of metal-important records and test whether specificity estimates generalize. [src: metal_specificity]
- Incorporate the three module organisms without pangenome links and determine whether their omission changes the 86.0% module-gene core fraction or the distribution of core, mixed, and accessory modules. [src: module_conservation]
- Reanalyze module conservation with continuous gene-cluster prevalence rather than the arbitrary 90% and 50% thresholds. [src: module_conservation]
- Test whether module-family breadth remains unrelated to conservation after controlling for organism count, gene-family size, phylogeny, and the high baseline core rate. [src: module_conservation]
- Validate metal-specificity calls against the Fitness Browser `specificphenotype` table and repeat the osmotic comparison using the exact threshold from the counter-ion analysis. [src: metal_specificity]
- Reanalyze metal-responsive modules using the atlas's precomputed z-scores rather than per-module normalization. [src: metal_specificity, metal_fitness_atlas]
- Replace binary core/auxiliary labels with quantitative gene-cluster prevalence across genomes to test whether continuous conservation measures strengthen the relationship with fitness magnitude. [src: field_vs_lab_fitness]
- Refit predictive models using continuous fitness scores, gene length, experimental coverage, fitness breadth, and module membership to determine whether fitness predicts conservation after measurement biases are controlled. [src: fitness_effects_conservation, field_vs_lab_fitness, module_conservation]
- Test whether the positive and negative fitness tails of core genes reflect trade-offs, condition-dependent essentiality, or epistatic network structure using matched multi-condition perturbation data. [src: fitness_effects_conservation]
- Map heavy-metal and antibiotic fitness-important genes and accessory module families to mobile elements and resistance islands to test whether low conservation reflects horizontal transfer or other accessory-genome processes. [src: field_vs_lab_fitness, module_conservation]
- Use phylogenetic independent contrasts on metal cross-resistance matrices to distinguish shared ancestry from conserved response architecture. [src: metal_cross_resistance]
- Normalize metal fitness effects by concentration relative to MIC and test whether dose normalization changes pairwise cross-resistance magnitudes. [src: metal_cross_resistance, metal_fitness_atlas]
- Functionally characterize the 149 atlas candidates and prioritize replicated families, especially UCP030820, YebC, and DUF1043/YhcB, for structural and experimental validation. [src: metal_fitness_atlas, metal_specificity]
- Test YebC's proposed proline-rich translation-bottleneck mechanism under metal exposure using expression, ribosome-stalling, and targeted fitness assays. [src: metal_specificity]
- Evaluate singleton genes and excluded organisms with improved transposon coverage and environmental assays to distinguish true neutrality or specificity from [[concepts/coverage-limited-inference]]. [src: fitness_effects_conservation, metal_specificity]
- Expand matched fitness and pangenome data to additional organisms and rare metals to evaluate [[concepts/organism-specificity]] and [[concepts/coverage-limited-inference]]. [src: metal_fitness_atlas, metal_specificity]

## Related Documents

- [[summaries/fitness_effects_conservation__REPORT]]
- [[summaries/field_vs_lab_fitness__REPORT]]
- [[summaries/metal_cross_resistance__REPORT]]
- [[summaries/metal_fitness_atlas__REPORT]]
- [[summaries/metal_specificity__REPORT]]
- [[summaries/module_conservation__REPORT]]
- [[summaries/fitness_modules__REPORT]]

See also: [[summaries/pathway_capability_dependency__REPORT]]

See also: [[summaries/prophage_amr_comobilization__REPORT]]

See also: [[summaries/snipe_defense_system__REPORT]]

See also: [[summaries/truly_dark_genes__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]