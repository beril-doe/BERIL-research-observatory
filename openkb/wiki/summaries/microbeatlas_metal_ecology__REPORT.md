---
type: "Summary"
description: "Global PGLS links metal-resistance breadth to bacterial niche breadth."
doc_type: short
full_text: "sources/microbeatlas_metal_ecology__REPORT.md"
---

# Metal Resistance Ecology — Summary

## Contribution

This study tests whether bacterial genera with broader metal-resistance repertoires occupy broader ecological niches. It integrates [[entities/amrfinderplus]] pangenome annotations for 6,789 GTDB species with niche breadth inferred from 98,919 OTUs across 463,972 [[entities/microbeatlas]] samples, using [[entities/pagels-lambda]] and [[entities/phylogenetic-generalized-least-squares]] (PGLS). The central result is a positive association between the number of metal types resisted and bacterial niche breadth after controlling for phylogeny, genome size, and sampling depth. [src: microbeatlas_metal_ecology]

Relevant cross-document themes include [[concepts/metal-resistance-breadth]], [[entities/levins-niche-breadth]], [[concepts/phylogenetic-amr-structure]], [[concepts/horizontal-gene-transfer]], [[concepts/ecological-generalism]], and [[concepts/phylogenetic-confounding]].

## Main findings

- Bacterial niche breadth is strongly phylogenetically conserved: Levins’ standardized niche breadth had Pagel’s λ = 0.787 across 1,264 genera, while habitat-category range had λ = 0.909. [src: microbeatlas_metal_ecology]
- In the 606-genus PGLS subset, metal type diversity was the only primary metal-AMR predictor that survived Bonferroni correction. Its coefficient was β = +0.021, SE = 0.0056, p = 1.5×10⁻⁴; the threshold for six confirmatory models was p < 0.0083. [src: microbeatlas_metal_ecology]
- Total AMR cluster count and core AMR fraction were not significant predictors of Levins’ B_std. The result therefore supports a breadth-over-depth pattern: coverage of multiple metal types, rather than many resistance genes for a narrow set of metals, is associated with ecological generalism. [src: microbeatlas_metal_ecology]
- The association persisted in a multi-predictor PGLS containing all three AMR metrics: metal types β = +0.023, p = 5.5×10⁻⁴, while AMR cluster count and core fraction remained non-significant. [src: microbeatlas_metal_ecology]

## Phylogenetic structure and evolutionary interpretation

Metal AMR traits showed intermediate phylogenetic signal: λ = 0.260 for total AMR clusters, λ = 0.441 for core AMR fraction, and λ = 0.335 for metal type diversity. Niche breadth was more conserved than AMR traits, while nitrification showed near-maximal signal in both bacteria and archaea. [src: microbeatlas_metal_ecology]

This gradient is consistent with a mixed evolutionary model in which core resistance traits are more vertically inherited, whereas accessory gene accumulation and expansion across metal types are more labile and potentially shaped by [[concepts/horizontal-gene-transfer]], [[concepts/mobile-genetic-elements]], and local metal exposure. This is an interpretation rather than a direct demonstration of HGT causality. [src: microbeatlas_metal_ecology]

The standalone bacterial niche-breadth λ of 0.787 exceeded the PGLS residual λ of 0.708 because including metal type diversity removes some phylogenetically structured variance. The study interprets this as evidence that metal resistance breadth explains part, but not all, of the phylogenetic covariance in niche breadth. [src: microbeatlas_metal_ecology]

## Robustness and sensitivity

The principal positive association was stable across several controls:

- Adding pangenome species count as a PGLS covariate gave β = +0.0204, p = 3.4×10⁻⁴.
- Rarefying to one species per genus across 200 iterations produced a median β = +0.0147, median p = 0.0054, and a positive effect in all iterations; 89.5% were nominally significant and 57.5% passed the Bonferroni threshold.
- Adding log genome size gave metal types β = +0.0218, p = 3.6×10⁻⁴, with ΔAIC = 10.8 favoring inclusion of metal types. Genome size was independently positive.
- A three-covariate PGLS controlling simultaneously for metal types, log species count, and log genome size retained the metal-type effect: β = +0.0218, p = 3.5×10⁻⁴. Genome size remained significant, while log species count did not.
- Adding within-genus variation in metal type counts left the mean effect significant (β = +0.0189, p = 0.0016); within-genus SD was not significant (p = 0.181).
- Excluding each of the seven primary metals preserved a positive coefficient, although none of the leave-one-metal-out models remained significant. This supports a distributed signal but does not distinguish distributed biological contributions from loss of predictor variance.
- Excluding each of the 13 environment categories preserved a positive association; the weakest was after excluding aquatic samples (β = +0.0085, p = 0.031).
- Filtering out OTUs with mean relative abundance below 0.01% reduced bacterial niche-breadth λ only from 0.763 to 0.750 in the matched subset, and the signal remained highly significant (p = 2.8×10⁻⁴⁰).

The strict 5% within-environment prevalence analysis reduced the PGLS sample from 606 to 379 genera and produced β = +0.0166, p = 0.092. The direction and approximate magnitude persisted, but statistical power fell substantially. [src: microbeatlas_metal_ecology]

## Independent validation analyses

### Groundwater prevalence

Among 767 genera detected in 1,624 groundwater samples and having metal AMR data, metal type diversity correlated positively with groundwater prevalence (Spearman ρ = +0.112, p = 0.0019). Top-quartile metal-diverse genera had median prevalence of 0.81%, versus 0.62% for bottom-quartile genera; the Mann–Whitney comparison gave p = 0.007. [src: microbeatlas_metal_ecology]

However, metal type diversity did not correlate significantly with groundwater fold enrichment relative to non-groundwater samples (ρ = +0.042, p = 0.242). Thus, the analysis supports a prevalence association but does not establish groundwater-specific enrichment or the proposed metal-contamination mechanism. [src: microbeatlas_metal_ecology]

### ENIGMA ORFRC time series

A separate amplicon analysis processed all 133 samples from [[entities/prjna1084851]], generating 24,295 OTUs. Community-weighted mean metal-type diversity ranged from 1.01 to 1.83 and differed across eight groundwater wells (Kruskal–Wallis H = 29.10, p = 0.0001). Wells FW215 and FW216, located in the U/NO₃ contamination plume, had the highest median values: 1.37 and 1.36, respectively. [src: microbeatlas_metal_ecology]

Community-weighted metal-type diversity increased over time after carbon amendment (Spearman ρ = +0.383, p < 0.0001; FW216 alone, ρ = +0.576, p = 0.0001). This is consistent with ecological selection during geochemical change, but the analysis is observational and only 16.8% of reads were joinable to genus-level AMR data. *Sulfurimonas* declined over time (ρ = −0.323, p = 0.0002), illustrating that groundwater abundance can also be driven by electron-acceptor availability rather than metal resistance. [src: microbeatlas_metal_ecology]

## Archaeal results

Archaeal niche breadth showed significant phylogenetic signal for B_std (λ = 0.197, p = 1.1×10⁻⁵) and environment count (λ = 0.898, p = 4.6×10⁻¹⁴). The archaeal AMR analysis was severely underpowered, with only 48 genera. Metal type diversity had the same positive direction as in bacteria but was non-significant: β = +0.0145, SE = 0.0198, p = 0.467. Formal power analysis estimated that at least 702 genera would be needed for 80% power at α = 0.05, or 1,084 under the Bonferroni threshold. The result should not be interpreted as evidence for no archaeal association. [src: microbeatlas_metal_ecology]

## Causal interpretation

The PGLS coefficient is a phylogenetically adjusted association, not a causal estimate. Three explanations remain compatible with the data:

1. Diverse metal tolerance may help taxa colonize chemically varied environments.
2. Broad-niche taxa may encounter more environments, HGT donors, and metal exposures, increasing acquisition of metal-resistance genes.
3. A shared factor such as genome size, metabolic versatility, or biofilm capacity may promote both traits.

Genome-size controls weaken the third explanation as a sole account, but they do not establish directionality. Time-series genomic data, controlled metal-enrichment experiments, or natural experiments would be required to distinguish these scenarios. [src: microbeatlas_metal_ecology]

## Experimental framework

The report proposes experimental testing using 435 candidate OTUs: 215 in the top 10% for both niche breadth and metal diversity, plus 220 nitrifier positive controls. An eight-OTU shortlist includes *Klebsiella*, *Enterococcus*, *Citrobacter*, *Franconibacter*, *Noviherbaspirillum*, *Serratia*, *Aeromonas*, and *Pseudomonas*, with metal-specific stresses selected from their inferred resistance profiles.

The proposed test is that a candidate OTU should increase by at least two-fold under its assigned metal stress after 7–14 days relative to metal-free controls. Recommended design parameters are 4–6 stress treatments, five replicates, and 7- and 14-day time points. A pre-treatment sequencing screen at ≥50,000 reads per sample should restrict experiments to the 3–5 candidates detectable at ≥0.1% abundance. [src: microbeatlas_metal_ecology]

## Limitations and open directions

Major limitations include reliance on sequencing-effort-sensitive niche proxies, primer and geographic sampling bias, broad and heterogeneous environment categories, uneven pangenome coverage, genus-level aggregation, limited archaeal representation, lack of alternative phylogenetic-tree testing, and incomplete validation of [[entities/amrfinderplus]] metal annotations. The Gaussian PGLS treatment of the integer metal-type predictor is acknowledged as an approximation, especially for standalone Pagel’s λ analyses. [src: microbeatlas_metal_ecology]

Priority next steps are to:

- split aquatic samples into finer environmental categories;
- test alternative phylogenetic trees and taxonomic aggregation schemes;
- quantify AMRFinderPlus false-positive rates by manual validation of 100 clusters;
- estimate pangenome openness and HGT burden as additional predictors;
- test specific metal co-resistance combinations rather than only total type count;
- expand archaeal AMR coverage with environmental MAGs;
- use phylogenetic mixed models for reverse-direction count analyses; and
- archive derived data and workflows in a public Zenodo repository.

## Overall assessment

The study provides strong comparative evidence that bacterial genera with broader inferred metal-resistance type repertoires tend to have broader inferred ecological niches, independently of phylogeny, genome size, and several measures of sampling depth. The effect is statistically robust in the main bacterial analysis and directionally supported by groundwater and ENIGMA observations, but remains correlational and dependent on ecological and genomic proxies rather than direct physiological measurements. [src: microbeatlas_metal_ecology]

## Related Concepts
- [[concepts/annotation-gap]]
- [[concepts/cultivation-bias]]
- [[concepts/experimental-functional-prioritization]]
- [[concepts/method-concordance]]
- [[concepts/organism-specificity]]
- [[concepts/phenotype-resolution-matching]]
- [[concepts/spatial-sampling-effort]]

## Entities
- [[entities/bakta]]
- [[entities/fitness-browser]]
- [[entities/bacdive]]
- [[entities/metal-fitness-atlas]]
- [[entities/kegg]]
- [[entities/random-barcode-transposon-sequencing]]
