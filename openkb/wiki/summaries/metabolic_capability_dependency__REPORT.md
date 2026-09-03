---
type: "Summary"
description: "Quantifies latent metabolic pathways, pangenome links, and within-species ecotypes."
doc_type: short
full_text: "sources/metabolic_capability_dependency__REPORT.md"
---

# Metabolic Capability vs. Metabolic Dependency

## Overview

This report integrates GapMind pathway-completeness predictions with Fitness Browser gene-fitness data to distinguish pathways that are genomically complete from those that are functionally important under tested conditions. It evaluates 1,695 pathway–organism pairs across 48 organisms, tests links between pathway dependency and pangenome openness, and characterizes within-species [[concepts/metabolic-ecotypes]] in 10 species.

## Key Findings

### Latent capabilities are common and pathway-dependent

- 15.8% of genomically complete pathways were classified as **latent capabilities**: they showed no detectable fitness importance, with mean absolute t-score < 1.0 and fewer than 5% essential genes.
- 32.3% were intermediate and 51.9% were active dependencies.
- Dependency class varied strongly by pathway category (χ²=163.6, df=4, p=2.5×10⁻³⁴).
- Carbon source utilization pathways were most often latent: 24.3% latent and 39.8% active.
- Amino acid biosynthesis pathways were predominantly active: 63.5% active and 6.5% latent.
- The latent fraction varied among organisms from 0–31.6%, with high values in [[entities/pseudomonas-syringae]] strains and [[entities/klebsiella-michiganensis]].
- Threshold sensitivity produced latent fractions from 4.7% to 21.1%, but the qualitative conclusion that a substantial fraction of complete pathways are fitness-neutral remained stable.

These findings support [[concepts/latent-metabolic-capabilities]] as a distinction from [[concepts/pathway-completeness]]: a pathway may be encoded yet unnecessary under a particular environment or laboratory medium. They also illustrate [[concepts/condition-dependent-essentiality]], in which functional importance depends on the tested conditions.

### Black Queen predictions received mixed support

Pathway-level conservation did not distinguish latent capabilities from active dependencies. Mean conservation was 0.829 for active pathways, 0.907 for intermediate pathways, and 0.869 for latent pathways; the active-versus-latent comparison was not significant (Mann–Whitney U, p=0.94; rank-biserial r=0.052).

At the clade level, however, latent capability rate was positively correlated with pangenome openness across 22 unique species clades (Spearman ρ=0.69, p=0.0004). Clades with more fitness-neutral complete pathways tended to have more dynamic pangenomes. This supports a qualified Black Queen hypothesis interpretation in which genome dynamics and community context may reveal dependency patterns more clearly than pathway-level conservation rates. The result connects to [[concepts/pangenome-integration]] and [[concepts/fitness-conservation]].

The report identifies several reasons why pathway conservation may have missed gene-loss signals: pathway-level measures cannot detect partial erosion, fitness-tested organisms represent only a subset of species-clade genomes, SEED-based pathway mapping introduces proxy noise, and evolutionary loss may not yet be visible in current sampling.

### Metabolic ecotypes are widespread

All 10 target species showed meaningful metabolic clustering, with silhouette scores above 0.2. Scores ranged from 0.349 in PALSA-747 sp. to 0.894 in [[entities/salmonella-enterica]].

- *Salmonella enterica* formed six clusters from 11,396 genomes and had the strongest separation (silhouette=0.894).
- *Stutzerimonas stutzeri* and *Alteromonas macleodii* formed two clusters with silhouettes of 0.780 and 0.738, respectively.
- Other species included *Acetatifactor intestinalis*, *Ruminococcus* E sp., [[entities/phenylobacterium]] sp., *Limivicinus* sp., [[entities/pelagibacter]] sp., [[entities/prochlorococcus]] A sp., and PALSA-747 sp.

Cluster membership was associated with isolation environment in *S. enterica* (χ²=1570.2, df=25, p<0.0001) and *Phenylobacterium* sp. (χ²=12.2, df=1, p=0.0005), but not in the tested marine organisms. The report frames these results as evidence for widespread [[concepts/metabolic-ecotypes]], while noting that observational clustering cannot establish ecological causation and that marine metadata may lack sufficient resolution. The latter limitations relate to [[concepts/phenotype-resolution-matching]], [[concepts/cultivation-bias]], and [[concepts/phylogenetic-confounding]].

The most heterogeneous pathways were valine/leucine biosynthesis (heterogeneity=0.60), tryptophan biosynthesis (0.51), and lysine/threonine biosynthesis (0.49), indicating population-level variation in biosynthetic independence.

## Methods and Data

Pathway completeness was obtained from [[entities/kbase-ke-pangenome]].gapmind_pathways, while gene fitness, essentiality, and SEED subsystem annotations came from [[entities/fitness-browser]]. GapMind pathways were mapped to fitness data through SEED subsystem proxies.

Dependency thresholds were:

- **Active dependency:** mean absolute t-score > 2.0 or >20% essential genes.
- **Latent capability:** mean absolute t-score < 1.0 and <5% essential genes.
- **Intermediate:** values between these thresholds.

The analysis generated per-genome and per-species pathway summaries, pathway fitness metrics and classifications, conservation and pangenome-openness tables, pathway heterogeneity scores, ecotype assignments, and pathway cluster signatures. Hierarchical clustering and PCA were used for ecotype detection.

Two GapMind pathways, deoxyribonate and myoinositol, lacked matching SEED subsystem roles and were excluded. Phenylalanine and tyrosine were retained through `phe` and `tyr` abbreviation matches. Alanine was excluded because too few SEED-annotated genes met the coverage requirement.

## Interpretation and Limitations

The report proposes that carbon utilization pathways are especially condition-dependent: they may be ecologically useful but neutral in the tested medium. Amino acid biosynthesis pathways appear more strongly retained under the experimental conditions. The observed 3.7-fold difference in latent rates between carbon utilization and amino acid biosynthesis (24.3% versus 6.5%) is presented as a testable prediction about differential gene loss.

Important limitations include laboratory-condition bias, proxy-based pathway mapping, pathway-level rather than gene-level conservation, limited fitness coverage across 48 organisms, and possible confounding between ecotype clusters and phylogeny. An attempted organism-to-clade linkage using NCBI taxonomy identifiers failed because the relevant metadata column contained boolean strings rather than numeric taxids; downstream clade analyses therefore rely on organism-level fitness aggregates without an explicit taxonomic linkage.

## Future Directions

1. Replace pathway-level conservation with gene-level presence/absence and phylogenetic dN/dS analyses.
2. Use direct GapMind per-step gene assignments instead of SEED proxies.
3. Search for recent gene-loss events in pathways classified as latent.
4. Enrich isolation metadata with BacDive, GTDB, and other environmental trait datasets.
5. Test whether high-latency organisms encode public-goods pathways or occur with cross-feeding partners in community datasets, connecting the analysis to [[concepts/metabolic-support-networks]].

## Related Concepts
- [[concepts/capability-versus-kinetics]]
- [[concepts/evidence-triangulation]]
- [[concepts/coverage-limited-inference]]
- [[concepts/annotation-gap]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/functional-redundancy]]
- [[concepts/horizontal-gene-transfer]]
- [[concepts/two-speed-genome]]

- [[concepts/latent-metabolic-capabilities]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/metabolic-ecotypes]]
- [[concepts/pangenome-integration]]
- [[concepts/pathway-completeness]]
- [[concepts/metabolic-support-networks]]
- [[concepts/fitness-conservation]]
- [[concepts/phylogenetic-confounding]]

## Entities
- [[entities/gtdb]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/modelseed]]
- [[entities/kegg]]
- [[entities/acinetobacter-baylyi-adp1]]
- [[entities/escherichia-coli]]
