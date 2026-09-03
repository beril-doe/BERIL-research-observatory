---
sources: ["summaries/amr_cofitness_networks__REPORT.md"]
type: "Gene_Or_Pathway"
description: "A biosynthetic pathway enriched in AMR cofitness support networks"
---

# Histidine Biosynthesis

## Identity

Histidine biosynthesis is represented in this corpus by GO:0000105 and is treated as a gene or pathway entity. [src: amr_cofitness_networks]

## Evidence from AMR cofitness networks

Histidine biosynthesis was among the top functional categories enriched in AMR gene cofitness neighborhoods based on InterProScan GO annotations. [src: amr_cofitness_networks]

The term was significantly enriched in three organisms, with a mean odds ratio of 5.3. [src: amr_cofitness_networks] Efflux-resistance networks showed the strongest reported association, with histidine biosynthesis enriched in six organisms in the mechanism-specific analysis. [src: amr_cofitness_networks]

Histidine biosynthesis showed a possible mechanism-specific difference between efflux and metal-resistance networks: it occurred in 68% of efflux organisms versus 30% of metal-resistance organisms (uncorrected p = 0.013; FDR-adjusted q = 0.18). Because the association did not remain significant after FDR correction, the report treats this as a hint rather than an established mechanism-specific effect. [src: amr_cofitness_networks]

## Interpretation and caveat

The enrichment may indicate co-regulation linking AMR genes with amino-acid metabolism, but it may also reflect [[concepts/shared-dispensability]] under Fitness Browser laboratory conditions, where supplemented media can make biosynthetic genes redundant. [src: amr_cofitness_networks]

The report identifies a fitness-matched permutation as the key test: random non-AMR genes should be matched to AMR genes by mean fitness distribution to determine whether histidine-biosynthesis enrichment is specific to AMR neighborhoods or is a general property of slightly positive-fitness, conditionally dispensable genes. [src: amr_cofitness_networks]

## Related pages

- [[concepts/cofitness-networks]]
- [[concepts/condition-dependent-essentiality]]
- [[entities/tryptophan-biosynthesis]]
- [[entities/flagellar-motility]]
- [[summaries/amr_cofitness_networks__REPORT]]