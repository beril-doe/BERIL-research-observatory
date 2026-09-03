---
type: "Summary"
description: "Maps prophage modules, TerL lineages, and environmental patterns across bacterial diversity."
doc_type: short
full_text: "sources/prophage_ecology__REPORT.md"
---

# Prophage Gene Modules and Terminase-Defined Lineages Across Bacterial Phylogeny and Environmental Gradients

## Overview

This report presents a large-scale analysis of prophage-associated gene modules across 27,702 bacterial species in the BERDL pangenome, combining eggNOG annotations, host phylogeny, environmental metadata, TerL sequence clustering, gene co-occurrence analysis, and NMDC metagenomic data. It distinguishes near-universal prophage-associated functions from structurally variable modules and tests whether prophage composition is shaped by genome size, host phylogeny, or environment.

The central conclusion is that prophage ecology is modular: environmental signals are strongest for structural and anti-defense functions, whereas lineage-level distributions largely track host phylogeny. The results also support a two-tier organization consisting of a physically linked core backbone and more mobile or scattered accessory functions, connecting [[concepts/prophage-genome-modularity]] with [[concepts/module-versus-lineage-ecology]].

## Key Findings

### Prophage modules are widespread but unevenly complete

All 27,702 analyzed species carried at least one prophage-associated gene cluster, totaling 4,005,537 clusters. Three modules were nearly universal:

- Packaging (A): 100.0% of species
- Lysogenic regulation (F): 100.0%
- Lysis (D): 99.9%

The more structurally variable modules were:

- Head morphogenesis (B): 56.1%
- Tail (C): 55.6%
- Anti-defense (G): 64.3%
- Integration (E): 99.1%

Only 34.9% of species carried all seven modules. The near-universal core modules may include many domesticated or defective prophage remnants, while modules B, C, and G are more informative indicators of structurally complete prophage elements. This supports a distinction between prophage domestication and intact prophage architecture, with the former related to [[concepts/mobile-genetic-elements]].

### Genome size and environment explain more variation than phylogeny

PERMANOVA of prophage module composition identified significant effects for genome size quartile, environment, and host family phylogeny, all with p=0.01. Their F-statistics were:

| Predictor | F-statistic |
|---|---:|
| Genome size quartile | 212.99 |
| Environment | 30.04 |
| Phylogeny (family) | 6.17 |

Genome size was the strongest predictor and correlated with prophage cluster count at rho=0.717. However, environmental effects remained significant within every genome-size quartile, with all Kruskal-Wallis tests yielding p < 6.5e-78. AlphaEarth analyses also detected a partial correlation between environmental niche breadth and prophage module count after controlling for genome size (partial Spearman rho=0.468, p=8.41e-110).

These results reject the hypothesis that phylogeny alone explains prophage distribution, while emphasizing genome-size confounding and [[concepts/phylogenetic-confounding]] as major considerations in comparative pangenome analyses.

### Human-associated environments are enriched for structural and anti-defense functions

Constrained permutations preserving host family and genome-size strata identified eight significant module-by-environment associations after FDR correction. Human-associated environments showed strong enrichment for:

- Tail: log2(OR)=2.21, Z=10.86
- Head morphogenesis: log2(OR)=1.98, Z=10.00
- Anti-defense: log2(OR)=1.70, Z=8.76

Human-clinical environments also enriched anti-defense (log2(OR)=0.14, Z=5.14), tail (0.77, 3.90), and head morphogenesis (0.70, 3.59). Anti-defense was depleted in freshwater (log2(OR)=-0.74, Z=-4.74) and animal-associated environments (-0.24, -8.77).

The pattern suggests the hypothesis that human-associated niches impose stronger or more persistent phage–host arms-race pressures, favoring retention of complete structural machinery and counter-defense functions. It is consistent with [[concepts/microbial-arms-race]] and the Piggyback-the-Winner framework, but the annotation-based design does not establish causality.

### TerL lineages are phylogenetically constrained and ecologically heterogeneous

Clustering 38,085 TerL proteins from 11,789 species at 70% amino acid identity with [[entities/mmseqs2]] produced 10,991 lineages. The distribution was highly skewed: 6,921 lineages (63%) were singletons, while the largest lineage contained 1,094 members across 869 species. Threshold sensitivity yielded 4,001 lineages at 50% AAI and 16,283 at 80% AAI.

No individual lineage showed significant environment-specific enrichment after FDR correction across 500 tests. However, among 824 lineages with at least five species:

- 325 were classified as specialists, with Shannon entropy <1.0 or a dominant environment accounting for >80% of members.
- 499 were generalists distributed across at least three environments.

Specialists were concentrated in animal-associated, freshwater, and marine settings. Thus, [[concepts/module-versus-lineage-ecology]] differs between module-level and whole-TerL-defined lineage ecology: modules show environmental associations beyond phylogenetic expectation, whereas whole lineages do not.

### NMDC data independently supports environmental effects

Taxonomy-based prophage burden scores were inferred for 6,365 [[entities/nmdc]] metagenomic samples, with 87.2% median matching coverage. The analysis detected 57 significant module–abiotic-variable correlations after FDR correction. Strongest associations included:

| Module or burden | Variable | Spearman rho |
|---|---|---:|
| Packaging | pH | 0.519 |
| All modules | pH | 0.474 |
| All modules | Temperature | 0.399 |
| All modules | Depth | 0.361 |
| All modules | Total nitrogen | 0.333 |

Head morphogenesis, tail, and anti-defense were significant in both pangenome enrichment and NMDC correlation analyses. Packaging, lysis, integration, and lysogenic regulation were NMDC-significant but not pangenome-enriched beyond phylogenetic expectation, likely because their near-universal prevalence leaves little presence/absence variation. The NMDC findings strengthen the case for environmental effects on prophage burden, while remaining indirect because burden was inferred from taxonomy rather than directly detected in each metagenome. This is an example of [[concepts/evidence-triangulation]] combined with [[concepts/coverage-limited-inference]].

## Prophage Module Organization

Co-occurrence tests across 15 phylogenetically stratified species provided partial support for modular prophage organization. Of 95 module–species tests, 44 (46.3%) showed significantly greater within-module gene co-occurrence than expected by chance.

- Packaging (A): 11/15 significant; mean co-localization 0.986
- Lysis (D): 13/15 significant; mean co-localization 0.901
- Lysogenic regulation (F): 10/15 significant; mean co-localization 1.000
- Tail (C): 5/12 significant; mean co-localization 0.752
- Head morphogenesis (B): 1/6 significant; mean co-localization 0.474
- Integration (E): 1/15 significant; mean co-localization 0.420
- Anti-defense (G): 3/11 significant; mean co-localization 0.281

The core modules A, D, and F behave as physically linked prophage units. Integration genes are distributed across genomic insertion sites, while anti-defense genes are weakly co-localized with one another and may occur in defense islands separate from the prophage backbone. These results support [[concepts/prophage-genome-modularity]] and [[concepts/gene-neighborhood-inference]], but the limited sampling of 15 species and sparse representation of some modules constrain generalization.

## Hypothesis Outcomes

- **H0, phylogeny alone explains prophage distribution:** Rejected. Environment had a stronger PERMANOVA effect than phylogeny and remained significant after genome-size stratification.
- **H1a, module prevalence varies by environment:** Supported, especially for tail, head morphogenesis, and anti-defense modules.
- **H1b, TerL lineages show environment-specific enrichment:** Not supported at the individual-lineage level after FDR correction, although specialist and generalist breadths differed.
- **H1c, module genes co-occur:** Partially supported. Core modules co-occur strongly; integration and anti-defense do not.
- **H1d, NMDC prophage burden correlates with abiotic variables:** Supported by 57 significant correlations, with pH and temperature among the strongest predictors.

## Important Caveats

1. Prophage identification relied on [[entities/eggnog]] functional annotations rather than dedicated tools such as geNomad or VIBRANT, so prevalence may include bacterial homologs and domesticated remnants.
2. Genome size is a dominant burden predictor, and residual confounding may remain despite stratification and partial correlation.
3. Environment categories were derived from sparse and inconsistent isolation-source metadata; 9,659 species (35%) were assigned to `other_unknown`.
4. NMDC burden estimates rely on genus-level conservation and have not been independently validated for prophage genes.
5. Co-occurrence analysis covered one species per phylum and used 200 null permutations, limiting within-lineage replication and precision.
6. AlphaEarth embeddings covered only 28% of genomes and may overrepresent clinically and environmentally well-sampled lineages.

## Future Directions

- Compare annotation-based calls with geNomad or VIBRANT on representative genomes to estimate false-positive and false-negative rates.
- Use partial or sequential PERMANOVA to quantify the unique environmental variance after simultaneously controlling for phylogeny and genome size.
- Separate analyses of the core backbone (A, D, F) from accessory functions (B, C, E, G).
- Test whether anti-defense genes co-localize with host defense systems in defense islands.
- Link enriched modules to SOS, pH, and temperature induction mechanisms.
- Analyze longitudinal NMDC samples to distinguish temporal change from cross-sectional association.

## Related Concepts
- [[concepts/horizontal-gene-transfer]]
- [[concepts/organism-specificity]]
- [[concepts/annotation-gap]]
- [[concepts/method-concordance]]
- [[concepts/two-speed-genome]]

- [[concepts/prophage-genome-modularity]]
- [[concepts/module-versus-lineage-ecology]]
- [[concepts/mobile-genetic-elements]]
- [[concepts/microbial-arms-race]]
- [[concepts/gene-neighborhood-inference]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/evidence-triangulation]]
- [[concepts/coverage-limited-inference]]

## Entities
- [[entities/berdl]]
- [[entities/fitness-browser]]
- [[entities/random-barcode-transposon-sequencing]]
