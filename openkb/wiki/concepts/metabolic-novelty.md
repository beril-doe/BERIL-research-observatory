---
type: "Concept"
sources: ["summaries/webofmicrobes_explorer__REPORT.md"]
description: "De novo metabolite production distinguished from amplification of existing compounds"
---

# Metabolic Novelty

## Definition

Metabolic novelty is the fraction of observed metabolite changes that represent de novo production rather than increased abundance of compounds already present in the starting medium. In the Web of Microbes (WoM) data, novelty is operationalized using the ratio `E/(E+I)`, where `E` means an emergent metabolite absent from the starting medium and `I` means an existing metabolite whose level increased. [src: webofmicrobes_explorer]

This distinction connects metabolic capability dependency, [[concepts/metabolic-niche-partitioning]], and [[concepts/pangenome-integration]] by separating biosynthetic output from the amplification or accumulation of available compounds.

## Evidence from Web of Microbes

The 2018 WoM snapshot contains 1,155 organism observations classified as emerged (`E`) and 1,338 classified as increased (`I`). The two action classes are mutually exclusive across all 10,744 observations. [src: webofmicrobes_explorer]

The `E` action indicates that a metabolite was not detected in the starting medium but was detected after organism growth, making it evidence of organism-associated de novo production in this dataset. The `I` action indicates that a metabolite was already present and subsequently increased, representing amplification of an existing metabolite rather than clearly novel synthesis. [src: webofmicrobes_explorer]

Among ENIGMA isolates grown in R2A medium, the reported novelty rates were:

- *Pseudomonas* GW456-L13: 34 emerged and 49 increased; 32.4% novel.
- *Pseudomonas* FW507-14TSA: 33 emerged and 44 increased; 31.4% novel.
- *Pseudomonas* FW300-N2A2: 32 emerged and 26 increased; 30.5% novel.
- *Acidovorax* GW101-3E06: 30 emerged and 48 increased; 28.6% novel.
- *Bacillus* FW507-8R2A: 16 emerged and 39 increased; 15.2% novel.

The observed range, from 15.2% to 32.4%, indicates substantial variation among these isolates, with the highest reported novelty for GW456-L13 and the lowest for FW507-8R2A. [src: webofmicrobes_explorer]

The report presents this variation as a candidate phenotype for comparison with pangenome gene content. Because the analysis includes only a small organism set, the relationship between novelty and genome architecture remains a hypothesis rather than an established general pattern. [src: webofmicrobes_explorer]

## Biological Interpretation

Metabolic novelty can help distinguish two forms of extracellular metabolic behavior: production of compounds not initially available in the medium and increased levels of compounds that were already available. [src: webofmicrobes_explorer] This resolution is useful for interpreting exometabolomic profiles and for prioritizing candidate links between metabolite output and biosynthetic genes. [src: webofmicrobes_explorer]

For example, *Pseudomonas* FW300-N2E3 produced lactate, valine, lysine, thymine, and carnitine with action `E`, while other matched compounds such as alanine, arginine, glycine, proline, phenylalanine, tryptophan, threonine, trehalose, adenine, adenosine, inosine, malate, and nicotinamide were classified as `I`. [src: webofmicrobes_explorer] These products also overlap Fitness Browser tests of carbon or nitrogen sources, creating a route from observed metabolite production to [[concepts/gene-essentiality]] and [[concepts/condition-dependent-essentiality]]. [src: webofmicrobes_explorer]

A high novelty rate may indicate a larger observed biosynthetic output under a particular medium and growth context, but it does not by itself establish broader metabolic capability, pathway completeness, or ecological importance. The report therefore supports using novelty as a comparative phenotype, not as a direct measure of total biosynthetic capacity. [src: webofmicrobes_explorer]

## Tensions and Interpretation Limits

The WoM snapshot contains no organism-level decrease or consumption actions, even though decrease is described as a valid action in the broader WoM schema. All 742 `D` observations in this export belong to the control rather than to organisms. [src: webofmicrobes_explorer] Consequently, the `E/(E+I)` measure describes production-side novelty among observed changes and cannot be balanced against measured uptake or consumption in this snapshot. [src: webofmicrobes_explorer]

The `E` classification is biologically informative but remains dependent on detection limits, medium composition, and the accuracy of starting-medium measurements. The report identifies the action encoding as a key clarification, but does not establish that every `E` observation represents a newly synthesized compound rather than a compound below the initial detection threshold. This is an interpretation limit of the available evidence. [src: webofmicrobes_explorer]

## Relation to the Source Report

The full database exploration and isolate-level counts are documented in [[summaries/webofmicrobes_explorer__REPORT]]. The report identifies metabolic novelty as one of its central contributions and proposes linking novelty rates to pangenome openness, accessory-gene content, and gene fitness effects. [src: webofmicrobes_explorer]

## Open Directions

- Compare `E/(E+I)` rates with accessory-gene fraction and pangenome openness across matched WoM strains to test whether novelty tracks genome flexibility. [src: webofmicrobes_explorer]
- Reanalyze a current WoM or GNPS2 dataset containing organism-level consumption actions to determine whether production-side novelty is coupled to uptake and resource exchange. [src: webofmicrobes_explorer]
- For *Pseudomonas* FW300-N2E3 and GW456-L13, integrate WoM `E` metabolites with Fitness Browser experiments to test whether genes required for utilizing produced compounds are conditionally important. [src: webofmicrobes_explorer]
- Validate representative `E` calls with targeted metabolite measurements and starting-medium detection limits to distinguish true de novo production from initially undetected compounds. [src: webofmicrobes_explorer]