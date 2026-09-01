---
sources: ["summaries/discoveries.md", "summaries/amr_cofitness_networks__REPORT.md"]
type: "Gene_Or_Pathway"
description: "Flagellar motility enables bacterial movement and was enriched in AMR cofitness networks."
---

# Flagellar Motility

## Identity

- **Type:** Gene or pathway
- **Related terms:** flagellum-dependent cell motility, flagellum assembly, bacterial-type flagellum, and flagellum-dependent swarming. [src: amr_cofitness_networks]
- **Related entity:** [[entities/flagellar-motility]]

## Role in the AMR cofitness analysis

Flagellar-motility functions were among the strongest functional enrichments detected in antimicrobial-resistance (AMR) gene cofitness support networks. [src: amr_cofitness_networks] Using InterProScan Gene Ontology annotations, flagellum-dependent cell motility and flagellum assembly were each significantly enriched in five organisms, with mean odds ratios of 4.7 and 5.3, respectively. [src: amr_cofitness_networks] Bacterial-type flagellum was enriched in four organisms with a mean odds ratio of 4.9, while flagellum-dependent swarming was enriched in four organisms with a mean odds ratio of 5.0. [src: amr_cofitness_networks]

Across AMR mechanisms, flagellar-motility terms occurred in 53–61% of organisms, placing them below the more consistently conserved core of transmembrane transport, signal transduction, transcription regulation, and phosphorelay signaling. [src: amr_cofitness_networks]

## Interpretation and caveat

The association between flagellar motility and AMR cofitness may reflect genuine co-regulation involving resistance, motility, and signaling pathways, but the report does not establish direct regulatory linkage. [src: amr_cofitness_networks] A competing explanation is [[concepts/shared-dispensability]]: flagellar genes may be dispensable in the Fitness Browser’s shaken liquid-culture experiments because those conditions provide little opportunity for swimming or chemotaxis. [src: amr_cofitness_networks]

The same cofitness signal could therefore arise because AMR genes and flagellar genes respond similarly to laboratory conditions, rather than because they are controlled by a shared regulatory program. [src: amr_cofitness_networks] Pearson correlation removes each gene’s mean fitness before correlation, but condition-responsive similarity among genes that are broadly dispensable can still produce cofitness. [src: amr_cofitness_networks]

## Evidence status

The flagellar-motility enrichment is a significant observation, but its biological mechanism remains unresolved. [src: amr_cofitness_networks] The key proposed test is a fitness-matched permutation that compares AMR support networks with random non-AMR genes having the same mean-fitness distribution. [src: amr_cofitness_networks] Persistence of flagellar enrichment after matching would support a co-regulatory interpretation; disappearance would support shared dispensability as the primary explanation. [src: amr_cofitness_networks]

## Related pages

- [[concepts/cofitness-networks]]
- [[concepts/shared-dispensability]]
- [[concepts/condition-dependent-essentiality]]
- [[entities/fitness-browser]]
- [[entities/interproscan]]
- [[summaries/amr_cofitness_networks__REPORT]]

See also: [[summaries/discoveries]]