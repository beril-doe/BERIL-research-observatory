---
type: "Summary"
description: "Genome-scale analysis reveals compartment shifts, core PGP functions, and pervasive microbial duality."
doc_type: short
full_text: "sources/plant_microbiome_ecotypes__REPORT.md"
---

# Plant Microbiome Ecotypes — Summary

## Scope

This report analyzes plant-associated microbial functional guilds and their genetic architecture across 293,059 GTDB genomes, including 1,136 plant-associated species and 25,375 known non-plant species. It integrates pangenome annotations, environmental metadata, NMDC community data, MGnify genomes, BacDive phenotypes, and within-species phylogenetic analyses. The report's main themes are [[concepts/plant-compartment-filtering]], [[concepts/dual-nature-microbial-lifestyles]], [[concepts/core-accessory-resistance]], [[concepts/horizontal-gene-transfer]], [[concepts/functional-redundancy]], and [[concepts/phylogenetic-confounding]].

## Main Findings

### Compartment effects are real but small

Plant compartments impose statistically significant functional differences, but the original large effect was an artifact of marker choice and a few genome-rich species. On 607 root, rhizosphere, and phyllosphere species using the refined 17-marker panel, PERMANOVA estimated a total compartment effect of R² = 0.071 (pseudo-F = 23.2, p = 0.001). db-RDA attributed R² = 0.060 to location-only centroid shifts, approximately 84% of the PERMANOVA effect. PERMDISP was also significant (F = 15.6, p = 0.001): roots were least dispersed, phyllosphere communities were intermediate, and rhizospheres were most variable. Thus, compartment identity is a weak but genuine functional filter, rather than a determinant of most community variance.

The earlier Phase 1 estimate of R² = 0.527 fell to 0.072 after exclusion of the three dominant species per compartment, demonstrating strong sensitivity to taxonomic sampling. Per-marker enrichments remained directional, including root enrichment for ACC deaminase, T3SS, nitrogen fixation, and quorum sensing, but should not be interpreted as a community-wide multivariate effect of the original magnitude.

### Beneficial functions are more core-encoded than pathogenic functions

Beneficial plant-growth-promoting gene clusters were 64.6% core, compared with 45.2% for pathogenic clusters and 46.8% for the genome-wide baseline. The beneficial-versus-pathogenic difference was highly significant (Mann–Whitney U = 83,567,419, p = 3.38e-125), with a bootstrap 95% confidence interval of [0.089, 0.106]. Biofilm, IAA biosynthesis, nitrogen fixation, and phosphate solubilization had especially high core fractions, whereas T4SS, coronatine toxin, and effectors were more accessory or singleton-enriched. This supports a model in which acquired beneficial functions can become stabilized, while pathogenic functions remain more evolutionarily dynamic.

### HGT evidence is mixed and scale-dependent

Marker clusters that were singletons were 15.95 times more likely to co-occur with transposase/integrase singletons (Fisher's exact p = 8.8e-20), supporting frequent mobility-associated acquisition. However, markers as a class had a lower singleton enrichment ratio than the genomic average (0.78), suggesting purifying selection after acquisition. MGnify independently found higher mobilome burdens in plant-associated genera than in non-plant genera (median 3.7 versus 2.8 mobile elements per genome, p = 1.49×10⁻⁵), while prior genome-level studies report mobile-element depletion in plant microbiota. The report interprets this tension as potentially scale-dependent: genus-level diversity can be HGT-rich even when stabilized individual genomes carry fewer mobile elements. This links the findings to [[concepts/mobile-genetic-elements]] and [[concepts/two-speed-genome]].

### Co-occurring genera are slightly redundant rather than complementary

The initial Cohen's d = −7.54 was invalid because it used the standard deviation of permutation means rather than the raw pair-level standard deviation. Correcting the formula reduced the effect to approximately −0.43; prevalence-weighted aggregation reduced it further to −0.39, with permutation p < 0.001. Co-occurring genera were therefore slightly less complementary than random pairs, consistent with [[concepts/functional-redundancy]] and environmental filtering. The direction was robust, but the effect is small. A PGP–pathogen C-score analysis was structurally underpowered because 66 of 69 NMDC genera were dual or mixed rather than PGP-only.

### Plant-associated gene families retain enrichment after broad phylogenetic control

Of 5,671 eggNOG ortholog groups tested, 5,341 were significant in raw plant-versus-non-plant comparisons and 3,840 had OR > 2. This near-saturation indicates substantial taxonomic compositional bias. A controlled subset of 50 enriched gene families remained significant after phylum-level correction; for example, COG3569 declined from OR = 8.92 to 6.01 but remained strongly associated with plant status. A real per-species regression incorporating phylum and log10 genome size found that 48 of 50 retained positive, significant plant-association coefficients at BH-FDR q < 0.05. The two failed fits were singular-matrix cases rather than biological rejections.

All 50 families had functional annotations. Major themes included electron transport, high-affinity cytochrome c oxidases, iron–sulfur cluster biosynthesis, inorganic ion transport, and carbohydrate or secondary metabolism. Their core fractions ranged from 60.1% to 83.1%, above the 46.8% baseline. These results suggest enhanced metabolic competitiveness in microaerobic, nutrient-limited plant environments, while leaving the precise plant-interaction mechanisms unresolved.

### Dual-nature classification is widespread but weakly discriminative

The refined 17-marker panel used KEGG module completeness thresholds to reduce false-positive T3SS and nitrogen-fixation calls. Despite removing ubiquitous categories, 878 of 1,115 plant-associated species (78.7%) remained dual-nature. Most plant-associated species carry both PGP and pathogenic markers, but the categorical label does not distinguish biological phenotype: all 14 experimentally characterized beneficial or pathogenic validation species were assigned to the dual-nature class, and all four neutral controls were misclassified.

The continuous pathogenicity ratio, defined as n_pathogen / (n_pgp + n_pathogen), provided the only observed discrimination: known beneficial species had median ratio 0.50 versus 0.60 for known pathogens (Mann–Whitney U = 9, p = 0.027; n = 7 versus 7). Cohort labels should therefore be treated as a coarse screen, while continuous marker balance and experimental context are more informative. Genome size contributes substantially: dual-nature prevalence was 54% in the smallest genome-size quartile versus 87% in the remaining quartiles. This supports the broader [[concepts/dual-nature-microbial-lifestyles]] view that shared molecular machinery can underlie different ecological outcomes.

### Only some marker signals survive strict phylogenetic tests

A cluster-robust GLM with genus clustering and phylum fixed effects found 8 of 14 markers significant after BH-FDR correction, including ACC deaminase (OR = 8.01), T3SS (OR = 2.71), nitrogen fixation (OR = 2.71), phenazine, cellulase, phosphate solubilization, pectinase, and effectors. However, within-genus label shuffling retained only three markers: nitrogen fixation, ACC deaminase, and T3SS. The report consequently distinguishes three evidence tiers:

- **Species-level robust:** nitrogen fixation, ACC deaminase, and T3SS.
- **Genus- or cassette-level:** phenazine, cellulases, pectinases, phosphate solubilization, and effectors.
- **Not robust:** DAPG biocontrol, T4SS, hydrogen cyanide, IAA biosynthesis, siderophore, and acetoin/butanediol.

This analysis weakens species-level interpretations of broad marker enrichments while preserving a meaningful genus-scale association between plant lineages and functional cassettes. It also illustrates [[concepts/phylogenetic-confounding]] and [[concepts/phenotype-resolution-matching]]: the strength of an ecological conclusion depends on whether the statistical and biological resolution match.

### MGnify cross-validation supports rhizosphere associations but shows low concordance

MGnify contained 20,473 species across soil and three crop-rhizosphere biomes. T3SS prevalence was approximately twice as high in tomato, maize, and barley rhizospheres as in bulk soil: 24.0%, 21.6%, and 22.3% versus 12.3%. Seventeen genera occurred across all three crop rhizospheres, including *Pseudomonas_E*, *Streptomyces*, *Variovorax*, *Telluria*, and *Acidovorax*. Host-specific genera provide candidates for crop-specific biocontrol.

Agreement between pangenome isolation metadata and MGnify rhizosphere detection was only 11.7% by Jaccard overlap. This likely reflects differences between cultivation metadata and metagenomic detection, as well as sampling and database biases, so MGnify provides partial rather than definitive validation. The result is consistent with [[concepts/cultivation-bias]], [[concepts/method-concordance]], and [[concepts/coverage-limited-inference]].

### Within-species plant adaptation is concentrated in a minority of taxa

Phylogenetic-tree coverage was limited: only 18 of 65 plant-associated species with at least 20 genomes had distance data, leaving 47 candidates untestable. Of 17 species meeting the remaining sample criteria, five passed Bonferroni-corrected Fisher tests for subclade-by-plant-association segregation: *Xanthomonas vasicola*, *Mesorhizobium* sp002294985, *Agrobacterium pusense*, *Pseudomonas_E avellanae*, and *Xanthomonas campestris*. Three also satisfied Cochran-valid chi-square assumptions.

Host-specific subclade structure was strongest for two expected pathovar–host associations. *X. campestris* segregated toward Brassica hosts, with 46/47 genomes in one subclade, while *X. vasicola* segregated toward *Zea mays*, with 47/52 genomes in one subclade. These findings support a mixed model: plant adaptation is often accessory-genome-mediated and not aligned with core phylogeny, but in some taxa—especially *Xanthomonas*—host-specialized accessory cassettes have become phylogenetically structured. This is an example of [[concepts/host-specific-microbial-adaptation]] and [[concepts/microbial-arms-race]].

## Methodological Corrections and Limitations

- The original genus-level validation was circular because cohorts were defined from the same marker presence being validated.
- The original Cohen's d was inflated by a denominator error; the corrected effect is approximately −0.4.
- The original PERMANOVA magnitude was dominated by a small number of genome-rich species and conflated location with dispersion.
- `bakta_pfam_domains` uses versioned Pfam identifiers and lacks 12 of 22 queried marker Pfams that are present in InterProScan, especially secretion-system domains. The refined pipeline used InterProScan and is therefore unaffected.
- Genome-size adjustment supports the 50 enriched gene-family associations but does not remove the genome-size gradient in dual-nature classification.
- The cluster-robust GLM is a practical genus-level analogue to a phylogenetic GLMM, not a full tree-based model.
- Plant assignment depends mainly on isolation-source metadata; only 7,995 of 293,059 genomes had plant-associated annotations.
- MGnify mobilome and BGC data were available primarily for soil, limiting direct rhizosphere-versus-soil comparisons.

These limitations emphasize [[concepts/adversarial-methodological-review]], [[concepts/annotation-gap]], [[concepts/provenance-aware-data-discovery]], and [[concepts/computational-reproducibility]] as important safeguards for large comparative-genomics studies.

## Overall Interpretation

The report supports a multi-scale view of plant-associated bacterial ecology. Plant compartments exert small functional filters; beneficial functions are comparatively stable in core genomes; HGT and mobilome patterns depend on analytical scale; and co-occurring taxa show weak redundancy rather than strong division of labor. Broad PGP/pathogen categories are poor species-level classifiers because marker repertoires are widely shared and often genus-confounded. The strongest species-level signals involve nitrogen fixation, ACC deaminase, T3SS, and a limited number of host-specialized subclades. Future work should prioritize full tree-based models, accessory-gene trees, transcriptomic validation of dual-nature organisms, direct mobile-element annotation, finer-grained metabolic complementarity, and experimental testing of electron-transport and iron–sulfur functions in plant-associated niches. These priorities connect to [[concepts/dna-rna-functional-response]], [[concepts/experimental-functional-prioritization]], [[concepts/pathway-completeness]], and [[concepts/metabolic-competitive-exclusion]].

## Key Data and Analysis Outputs

- `data/h1_dbrda_results.csv`: PERMANOVA, PERMDISP, and db-RDA decomposition.
- `data/c1_cluster_robust.csv`: genus-clustered GLM marker tests.
- `data/genome_size_control.csv`: per-species OG regressions with genome-size control.
- `data/subclade_full_scan.csv`: corrected 65-species subclade scan.
- `data/h6_host_subclade_full.csv`: host-by-subclade associations.
- `data/pfam_bakta_ips_audit.csv`: Bakta versus InterProScan Pfam coverage audit.
- `data/genus_dossiers_v2.csv`: integrated dossiers for 30 plant-associated genera.

## Related Concepts
- [[concepts/organism-specificity]]
- [[concepts/metabolic-support-networks]]
- [[concepts/scalable-spark-data-analysis]]
- [[concepts/resource-darkness]]

- [[concepts/plant-compartment-filtering]]
- [[concepts/dual-nature-microbial-lifestyles]]
- [[concepts/core-accessory-resistance]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/mobile-genetic-elements]]
- [[concepts/functional-redundancy]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/host-specific-microbial-adaptation]]
- [[concepts/method-concordance]]
- [[concepts/cultivation-bias]]
- [[concepts/coverage-limited-inference]]
- [[concepts/pathway-completeness]]

## Entities
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/average-nucleotide-identity]]
- [[entities/flux-balance-analysis]]
- [[entities/modelseed]]
- [[entities/uniprot]]
