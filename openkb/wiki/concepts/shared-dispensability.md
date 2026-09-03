---
type: "Concept"
sources: ["summaries/pitfalls.md", "summaries/genotype_to_phenotype_enigma__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/conservation_fitness_synthesis__REPORT.md", "summaries/cofitness_coinheritance__REPORT.md", "summaries/caulobacter_fur_lipida_loss__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md"]
description: "Shared laboratory dispensability can mimic biological cofitness or co-regulation."
---

# Shared Dispensability as a Cofitness Confound

## Definition

**Shared dispensability** is the possibility that genes show correlated fitness profiles because they are similarly unnecessary under the assay conditions, rather than because they are directly co-regulated or mechanistically coupled. In [[concepts/cofitness-networks]], this creates a confound between shared condition-dependent fitness responses and genuine biological support relationships. [src: amr_cofitness_networks]

## Why the confound matters

Cofitness measures similarity in gene-fitness profiles across experiments; it does not, by itself, establish direct transcriptional regulation or physical interaction. Genes can covary because the same environmental axis changes their value, even when they do not share a regulator. [src: amr_cofitness_networks]

This issue is especially important for Fitness Browser data because experiments generally use shaken liquid culture, where flagellar motility and chemotaxis may provide little benefit, and often use rich or supplemented media, where amino-acid biosynthesis can be redundant. AMR genes are also frequently dispensable in experiments performed without antibiotics. Consequently, AMR, motility, and biosynthetic genes may occupy a common “dispensable under laboratory conditions” class. [src: amr_cofitness_networks]

The resulting correlations could reflect condition-dependent essentiality rather than AMR-specific regulatory biology. This links the confound to [[concepts/condition-dependent-essentiality]] and [[concepts/gene-essentiality]]. [src: amr_cofitness_networks]

## Evidence from AMR support networks

The AMR cofitness analysis across 28 organisms found enrichment for flagellum-dependent cell motility, flagellum assembly, bacterial-type flagellum, flagellum-dependent swarming, histidine biosynthesis, and tryptophan biosynthesis. These terms were significantly enriched in three to five organisms, with mean odds ratios between 4.7 and 5.3. [src: amr_cofitness_networks]

The enriched functions are also those most plausibly rendered dispensable by standard assay conditions: motility in shaken liquid culture and biosynthesis in supplemented media. Energy metabolism was not enriched in the conservation-matched permutation analysis, consistent with energy metabolism remaining useful under laboratory growth conditions. This pattern supports shared dispensability as a plausible alternative explanation, but does not prove that it is the cause of the observed AMR cofitness signal. [src: amr_cofitness_networks]

The report’s key unresolved distinction is:

- **Co-regulation hypothesis:** AMR genes are genuinely integrated with motility, signaling, and biosynthetic programs through shared regulators or cellular pathways.
- **Shared-dispensability hypothesis:** these gene classes show similar fitness responses because they are all burdens or are unnecessary in the tested environments, without requiring a direct regulatory relationship. [src: amr_cofitness_networks]

## What correlation does and does not remove

Pearson correlation subtracts each gene’s mean fitness before calculating covariation. Therefore, two genes that are uniformly slightly beneficial when knocked out should not correlate merely because both have positive average fitness. [src: amr_cofitness_networks]

However, shared dispensability can still produce condition-specific covariation. For example, two genes may both become more dispensable in nutrient-rich conditions and less dispensable during starvation. Their profiles can therefore correlate through a common environmental response even if they have no direct regulatory connection. [src: amr_cofitness_networks]

Thus, cofitness should be interpreted as shared fitness behavior, not automatically as co-regulation. This is a central qualification for [[concepts/cofitness-networks]] and for functional inference based on high-throughput mutant-fitness data. [src: amr_cofitness_networks]

## Relationship to robust findings

The shared-dispensability explanation weakens the interpretation of the specific flagellar and amino-acid enrichment as an AMR-specific mechanism. It does not eliminate the report’s organism-specificity result: different AMR mechanisms within the same organism shared more GO support terms than the same mechanism across organisms, with mean Jaccard values of 0.375 and 0.207, respectively (MWU p = 4.3×10⁻¹³). [src: amr_cofitness_networks]

The report argues that this relative network structure remains informative even if the correlated genes are co-varying because of shared assay-context responses. It indicates that each organism has a characteristic regulatory, metabolic, and signaling architecture shaping its support networks. This connects the confound to [[concepts/organism-specificity]] without reducing organism-specificity to direct co-regulation. [src: amr_cofitness_networks]

Similarly, AMR-containing ICA modules were larger than non-AMR modules, with median sizes of 46 versus 27 genes (MWU p = 1.7×10⁻⁸), and 208 of 209 AMR gene–module assignments were in cross-organism conserved module families. The report treats this module result as more robust because ICA modules capture condition-specific structure beyond shared mean fitness. [src: amr_cofitness_networks]

## Required resolving analysis

The most important follow-up is a **fitness-matched permutation**. Random non-AMR genes should be selected within organisms while matching the mean-fitness distribution of AMR genes, particularly the approximately −0.05 to +0.05 range proposed in the report. Their cofitness neighborhoods should then be tested for the same flagellar and biosynthetic enrichments. [src: amr_cofitness_networks]

- If fitness-matched random genes show comparable enrichment, the AMR signal is consistent with shared dispensability.
- If AMR neighborhoods remain selectively enriched after matching, the result would support a more specific co-regulatory or mechanistic interpretation. [src: amr_cofitness_networks]

Additional discriminating analyses include computing cofitness separately under antibiotic stress and standard growth, directly testing the mean fitness of flagellar-gene knockouts, and comparing AMR genes with other conditionally dispensable classes such as phage-defense or secondary-metabolite genes. [src: amr_cofitness_networks]

## Methodological implications

Functional enrichment from cofitness networks should be conditioned on assay context, gene mean fitness, and the availability of nutrients or stresses relevant to the tested phenotype. High-coverage annotation can reveal signals missed by legacy annotations, but improved annotation does not resolve whether an enriched category reflects regulation or shared dispensability. [src: amr_cofitness_networks]

The confound therefore motivates combining cofitness with independent evidence, such as condition-specific experiments, regulatory data, or [[concepts/multi-omics-integration]]. It also reinforces the importance of [[concepts/annotation-gap]]: annotation quality affects signal detection, while experimental context affects signal interpretation. [src: amr_cofitness_networks]

## Open Directions

1. Use organism-stratified, mean-fitness-matched permutations to test whether flagellar and amino-acid enrichments are AMR-specific. [src: amr_cofitness_networks]
2. Compare antibiotic-stress and antibiotic-free cofitness profiles to determine whether AMR–motility associations depend on resistance-relevant conditions. [src: amr_cofitness_networks]
3. Quantify the mean fitness distribution of flagellar, chemotaxis, and biosynthetic knockouts across Fitness Browser experiments. [src: amr_cofitness_networks]
4. Test whether other conditionally dispensable gene classes reproduce the same support-network enrichment pattern. [src: amr_cofitness_networks]
5. Validate candidate co-regulatory links with independent regulatory or multi-omics measurements rather than cofitness alone. [src: amr_cofitness_networks]

## Source

See [[summaries/amr_cofitness_networks__REPORT]].

See also: [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/caulobacter_fur_lipida_loss__REPORT]]

See also: [[summaries/cofitness_coinheritance__REPORT]]

See also: [[summaries/conservation_fitness_synthesis__REPORT]]

See also: [[summaries/essential_genome__REPORT]]

See also: [[summaries/genotype_to_phenotype_enigma__REPORT]]

See also: [[summaries/pitfalls]]