---
type: "Summary"
description: "Synthesizes how gene fitness effects shape bacterial genome conservation."
doc_type: short
full_text: "sources/conservation_fitness_synthesis__REPORT.md"
---

# Gene Conservation, Fitness, and the Architecture of Bacterial Genomes

## Overview

This synthesis examines the relationship between gene conservation across bacterial pangenomes and experimentally measured fitness effects. It integrates RB-TnSeq fitness data for 194,216 protein-coding genes from 43 diverse bacteria, conservation data from 27,690 species, and 1,116 ICA-derived fitness modules across 32 organisms. The central conclusion is that the [[concepts/core-accessory-resistance|core genome]] is not an inert collection of housekeeping genes: it is the most functionally active and environmentally constrained part of the genome.

## Key Findings

### Conservation–fitness gradient

Gene conservation declines gradually with decreasing importance. Essential genes are 82% core, whereas genes that are neutral in every experiment are still 66% core. Thus, fitness importance predicts conservation, but only modestly, and even experimentally neutral genes are frequently conserved. This result extends the [[concepts/gene-essentiality]] and [[concepts/pangenome-integration]] perspectives across diverse bacteria.

### The core-genome burden paradox

Core genes are more likely than accessory genes to impose measurable costs under laboratory conditions:

- 24.4% of core genes show positive fitness when deleted, compared with 19.9% of accessory genes.
- Genes with strong condition-specific effects are 1.78 times more likely to be core.
- Genes that are both important and burdensome in different conditions are 1.29 times more likely to be core.

These results challenge the expectation that conserved genes are uniformly beneficial or metabolically inexpensive. They support a [[concepts/condition-dependent-essentiality]] view in which conserved genes can be costly in some environments while remaining valuable across the broader range of conditions encountered in nature.

### Environmental selection as a resolution

The report proposes that laboratory conditions are an impoverished proxy for natural environments such as soil, biofilms, and host tissues. A gene that improves growth when deleted in rich medium may nevertheless support survival under natural conditions. The strongest signature of this proposed selection process is the set of 28,017 genes that are both costly in the laboratory and conserved in the pangenome: these genes are consistent with purifying selection maintaining functions despite their costs. By contrast, 5,526 genes are both costly and dispensable, making them candidates for ongoing gene loss.

This interpretation is a cross-environment hypothesis rather than a direct measurement of fitness in nature; environmental data and experiments are needed to test it. The proposed connection between laboratory phenotypes, pangenome conservation, and environmental context relates to [[concepts/genome-ecology-validation]].

## Functional architecture

The core genome is organized into coordinated functional units rather than isolated essential genes. ICA identified 1,116 co-regulated fitness modules. These modules contain 86% core genes versus an 81.5% baseline, with an odds ratio of 1.46 and p=1.6e-87; 59% of modules are composed of more than 90% core genes.

The burden pattern varies by function. Motility and chemotaxis show a +7.8 percentage-point core-burden excess, RNA metabolism +12.9 percentage points, and protein metabolism +6.2 percentage points. Cell-wall functions show the opposite pattern: non-core cell-wall genes are more burdensome. The report interprets this as consistent with energetically expensive functions such as flagellar motility being retained because they are valuable in natural environments, while ribosomal and related components support rapid growth responses despite their costs. These coordinated functional patterns connect to [[concepts/cofitness-networks]] and [[concepts/gene-co-inheritance]].

## Negative findings

- Module family breadth does not predict conservation: the correlation between the number of organisms represented and core fraction is rho=-0.01, p=0.91.
- Accessory genes are not systematically more burdensome; they are less costly on average than core genes, contrary to a [[concepts/core-accessory-resistance]] expectation of genome streamlining.
- Condition-specific fitness effects do not identify niche-specific accessory genes. Such genes are more likely to be core, suggesting that core genes have more detectable context-dependent effects.

## Open questions

1. Characterize the 5,526 costly and dispensable genes to determine whether they are mobile elements, recently acquired genes, or genes undergoing loss.
2. Link fitness and conservation patterns to [[entities/alphaearth-environmental-embeddings|AlphaEarth environmental data]] to test whether organisms from variable environments retain more trade-off genes in their core genomes.
3. Identify universally essential gene families shared across all 43 organisms.
4. Determine which co-regulated functions are represented by the 48 accessory modules.

## Data and provenance

The synthesis uses Fitness Browser RB-TnSeq measurements, KBase pangenome conservation data, upstream per-gene fitness statistics, and ICA fitness modules. Figures and analyses are documented in `notebooks/01_summary_figures.ipynb` and the associated selection-signature, fitness-conservation-gradient, and core-genome-architecture figures. The primary resources include [[entities/fitness-browser|Fitness Browser]], [[entities/random-barcode-transposon-sequencing|RB-TnSeq]], [[entities/kbase-ke-pangenome|KBase pangenome]], and [[entities/independent-component-analysis|ICA]].

## Related Concepts
- [[concepts/shared-dispensability]]
- [[concepts/organism-specificity]]
- [[concepts/cultivation-bias]]
