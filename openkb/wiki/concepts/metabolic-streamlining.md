---
type: "Concept"
sources: ["summaries/pseudomonas_carbon_ecology__REPORT.md"]
description: "Evolutionary loss of metabolic capabilities after specialization to a narrower habitat."
---

# Metabolic Streamlining

## Definition

**Metabolic streamlining** is the evolutionary reduction of metabolic capabilities when a lineage becomes specialized for an environment that supplies a narrower or more predictable set of resources. It differs from simple pathway absence in that the losses are interpreted as adaptive or selectively maintained reductions in unused metabolic functions. [[concepts/latent-metabolic-capabilities]] and [[concepts/pathway-completeness]] are important complementary perspectives because genomic pathway predictions measure inferred capability rather than actual pathway activity. [src: pseudomonas_carbon_ecology]

## Evidence from *Pseudomonas*

The strongest evidence in this corpus comes from a comparison of 12,732 genomes across 433 *Pseudomonas* species clades using 62 GapMind carbon pathways. [src: pseudomonas_carbon_ecology]

The *Pseudomonas* sensu stricto group, dominated by *Pseudomonas aeruginosa*, showed extensive loss of plant-derived sugar and sugar-alcohol pathways relative to the *Pseudomonas_E* group, which includes many *P. fluorescens*, *P. putida*, and *P. syringae* lineages. [src: pseudomonas_carbon_ecology]

Among seven *Pseudomonas* sensu stricto species and 189 *Pseudomonas_E* species with at least five genomes, 43 of 62 pathways differed significantly using Mann–Whitney U tests with Benjamini–Hochberg false-discovery-rate correction. [src: pseudomonas_carbon_ecology] The largest differences were observed for pathways associated with plant-derived substrates: xylose completeness was 0.0% versus 74.4%, arabinose was 0.0% versus 62.6%, myo-inositol was 0.0% versus 58.8%, galacturonate was 28.6% versus 88.4%, ribose was 27.9% versus 92.0%, mannitol was 25.9% versus 77.5%, and sorbitol was 25.9% versus 77.4% in the *P. aeruginosa* and *P. fluorescens* groups, respectively. [src: pseudomonas_carbon_ecology]

The contrast was selective rather than a generalized loss of carbon metabolism. Amino-acid pathways, including arginine, histidine, serine, and glutamate catabolism, and core organic-acid pathways such as citrate, succinate, and pyruvate remained above 99% complete in both groups. [src: pseudomonas_carbon_ecology] This pattern is compatible with specialization toward host environments in which amino acids and organic acids are more relevant than plant-cell-wall sugars, but the ecological mechanism is an interpretation of comparative genomic evidence rather than a direct measurement of in-host flux. [src: pseudomonas_carbon_ecology]

Across species with at least five genomes, free-living and plant-associated species had a median richness of 57 carbon pathways complete in more than half of genomes, compared with 55 in host-associated species. [src: pseudomonas_carbon_ecology] Within *Pseudomonas_E*, mean richness was 56.7 pathways for plant-associated species, 56.1 for free-living species, and 55.2 for host-associated species. [src: pseudomonas_carbon_ecology]

## What the evidence supports

The report assesses the hypothesis of pathway loss in host-associated clades as **strongly supported** because the largest differences involve precisely the plant-associated sugars and sugar alcohols expected to be less useful outside plant-associated habitats. [src: pseudomonas_carbon_ecology] The conservation of amino-acid and central organic-acid metabolism alongside loss of selected sugar pathways provides stronger evidence for targeted streamlining than would an undifferentiated reduction in pathway richness. [src: pseudomonas_carbon_ecology]

The result also illustrates the relationship between [[concepts/metabolic-niche-partitioning]] and [[concepts/host-specific-microbial-adaptation]]: lineages occupying different resource environments can retain different metabolic portfolios, while host adaptation may involve both acquisition of useful functions and loss of functions made unnecessary by the new habitat. [src: pseudomonas_carbon_ecology]

## Boundaries and tensions

The primary axis of pathway variation separated *Pseudomonas* sensu stricto from *Pseudomonas_E*, whereas lifestyle categories overlapped substantially within *Pseudomonas_E*. [src: pseudomonas_carbon_ecology] Consequently, the observed host-associated pattern may reflect lineage history as well as ecological selection, making [[concepts/phylogenetic-confounding]] a central qualification. [src: pseudomonas_carbon_ecology]

The analysis inferred pathway completeness from GapMind predictions rather than directly measuring pathway expression, substrate uptake, growth kinetics, or metabolite flux. [src: pseudomonas_carbon_ecology] The report therefore supports a difference in genomic metabolic potential, while the claim that these losses improve fitness in host environments remains a hypothesis requiring functional validation. [src: pseudomonas_carbon_ecology]

GapMind covers 62 common carbon pathways but omits important aromatic degradation capabilities, including pathways relevant to *P. putida* ecology. [src: pseudomonas_carbon_ecology] This creates an [[concepts/annotation-gap]] and a [[concepts/capability-versus-kinetics]] problem: apparent streamlining may be overstated if the relevant retained functions are absent from the pathway set, and pathway presence alone does not establish effective use under environmental conditions. [src: pseudomonas_carbon_ecology]

## Relation to other metabolic patterns

Streamlining should be distinguished from [[concepts/functional-redundancy]], in which multiple functions can compensate for one another, and from [[concepts/condition-dependent-essentiality]], in which a pathway may be dispensable in one condition but essential in another. [src: pseudomonas_carbon_ecology] It may also coexist with a [[concepts/two-speed-genome]] architecture: conserved losses can occur in the core lineage while niche-specific capabilities remain variable in the accessory genome. [src: pseudomonas_carbon_ecology]

The *P. aeruginosa* result further suggests that lineage-level specialization can precede or parallel the progressive metabolic losses observed during chronic infection. [src: pseudomonas_carbon_ecology] In this interpretation, some apparent metabolic loss during infection may reflect pre-existing lineage-level streamlining rather than only de novo adaptation within individual infections. [src: pseudomonas_carbon_ecology]

## Open Directions

- Add aromatic degradation modules for toluene, benzoate, naphthalene, and related compounds to test whether environmental pathway breadth is underestimated by the 62 GapMind pathways. [src: pseudomonas_carbon_ecology]
- Apply phylogenetic generalized least squares or phylogenetic logistic regression to test whether host-associated pathway losses remain after controlling for the GTDB species tree. [src: pseudomonas_carbon_ecology]
- Analyze within-species variation in *P. fluorescens* and *P. putida* to determine whether metabolic ecotypes are hidden by species-level aggregation. [src: pseudomonas_carbon_ecology]
- Compare pathway predictions with [[entities/random-barcode-transposon-sequencing]] data in the [[entities/fitness-browser]] to test whether retained pathways are functionally important under host- and environmental carbon sources. [src: pseudomonas_carbon_ecology]
- Use genome-level isolation sources and the complete genome-by-pathway matrix to distinguish species-wide streamlining from strain-level metabolic variation. [src: pseudomonas_carbon_ecology]

## Related source

- [[summaries/pseudomonas_carbon_ecology__REPORT]]
