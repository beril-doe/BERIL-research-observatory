---
type: "Summary"
description: "Pangenome-scale analysis identifies distinct PGP ecological guilds and inheritance patterns"
doc_type: short
full_text: "sources/pgp_pangenome_ecology__REPORT.md"
---

# PGP Gene Distribution Across Environments & Pangenomes

## Overview

This report analyzes plant growth-promoting (PGP) gene distribution, co-occurrence, environmental enrichment, pangenome location, and metabolic associations across the BERDL pangenome. It covers 27,702 species and identifies 11,272 species carrying at least one of 13 PGP markers, using 32,736 PGP gene clusters and data from 291,279 genomes. [src: pgp_pangenome_ecology]

The central conclusion is that a non-diazotrophic plant-growth-promotion module centered on [[entities/pqqC]] and [[entities/acdS]] is strongly associated with soil and rhizosphere environments, whereas [[entities/nifH]]-bearing nitrogen fixers form a more ecologically distinct guild. PGP genes are predominantly core genes rather than accessory genes, supporting [[concepts/gene-co-inheritance]] over a dominant [[concepts/horizontal-gene-transfer]] model. [src: pgp_pangenome_ecology]

## Key Findings

### PGP traits form a structured syndrome

Across five focal genes, 8 of 10 pairwise associations were significant after Benjamini–Hochberg FDR correction. The strongest positive association was between [[entities/pqqC]] and [[entities/acdS]] (OR = 7.24, n = 286 co-occurring species, q = 1.2e-83). [[entities/pqqC]] also co-occurred positively with [[entities/hcnA-hcnC]] (OR = 1.91) and [[entities/ipdC]] (OR = 1.55), suggesting a rhizosphere-effectiveness module involving phosphate solubilization, ACC deaminase activity, hydrogen cyanide production, and indole-3-acetic-acid-related metabolism. [src: pgp_pangenome_ecology]

By contrast, [[entities/nifH]] was negatively associated with [[entities/hcnA-hcnC]] (OR = 0.23, q = 5.8e-29) and [[entities/pqqC]] (OR = 0.57, q = 2.9e-19), and was not significantly associated with [[entities/ipdC]] (OR = 1.13, q = 0.54). This supports ecological separation between diazotrophs and the primarily non-diazotrophic pqqC/acdS-associated PGP phenotype. [src: pgp_pangenome_ecology]

Only 157 species (1.4%) carried at least three focal traits. The most common multi-trait combination was pqqC + acdS (153 species), while nifH + pqqC occurred in 225 species despite their negative overall association. [src: pgp_pangenome_ecology]

### Soil and rhizosphere selection favors acdS and pqqC

In an environmental comparison of 1,039 soil/rhizosphere species with 10,233 species from other environments, **acdS**, **pqqC**, and **hcnC** were significantly enriched in soil. Their reported odds ratios were 7.02, 2.90, and 1.85, respectively. **acdS** prevalence was 15.8% in soil versus 2.6% elsewhere and remained strongly enriched after phylum-level controls (logistic-regression OR = 6.98, p = 4.8e-61). A rhizosphere-only sensitivity analysis gave an acdS OR of 10.6 (q = 7.6e-38). [src: pgp_pangenome_ecology]

**nifH** was depleted in soil-classified species (OR = 0.60, q = 5.5e-08), while **ipdC** showed no raw enrichment (OR = 0.79, q = 0.47) and was soil-depleted in a phylum-controlled model (OR = 0.56, p = 0.027). Bacillota_A was an exception, with soil-enriched nifH (OR = ∞, q = 2.5e-4). [src: pgp_pangenome_ecology]

The report cautions that only 1,637 species, or 5.9% of species with environmental labels, were classified as soil/rhizosphere dominant; the analysis is therefore conservative and likely underestimates true rhizosphere enrichment because of broad or noisy isolation-source labels. This limitation illustrates [[concepts/coverage-limited-inference]] and [[concepts/cultivation-bias]]. [src: pgp_pangenome_ecology]

### PGP genes are predominantly core

The hypothesis that PGP genes are mainly accessory and horizontally transferred was rejected. All 13 PGP genes had significantly higher core fractions than the genome-wide baseline of 46.8%. Core fractions included 81.5% for **pqqC**, 78.1% for **pqqB**, 78.5% for **hcnA**, 76.5% for **ipdC**, 70.4% for **acdS**, 63.8% for **nifH**, and 55.5% for **pqqD**. [src: pgp_pangenome_ecology]

The mean accessory fraction across PGP genes was 29.7%, compared with 53.2% genome-wide. Pangenome openness also correlated negatively with PGP gene richness (Spearman ρ = −0.195, p = 2.0e-97, n = 11,272 species with at least two genomes). These results support [[concepts/core-accessory-resistance]] and [[concepts/pangenome-integration]], in which PGP traits are associated with stable, specialized ecological niches rather than primarily with recent HGT-driven acquisition. [src: pgp_pangenome_ecology]

**pqqD** was an important outlier: it had the lowest core fraction (55.5%) and highest singleton fraction (27.5%), consistent with occasional horizontal spread as a standalone gene. The functional pqqB–pqqC module was nevertheless predominantly core. [src: pgp_pangenome_ecology]

### The trp–ipdC relationship is context dependent

Complete tryptophan biosynthesis predicted **ipdC** presence: ipdC prevalence was 2.5% in species with complete trp pathways versus 0.9% in trp-incomplete species (Fisher OR = 2.81, p = 6.3e-10; logistic OR = 2.81, 95% CI 1.97–4.01). The association persisted after adding a soil covariate (OR = 2.87, p = 7.0e-09). [src: pgp_pangenome_ecology]

However, tyrosine pathway completeness was also associated with ipdC (OR = 3.62, p = 2.3e-11), weakening a tryptophan-specific interpretation. The report links this result to regulation by the TyrR transcription factor: TyrR regulation of ipdC in *Enterobacter cloacae* responds to tryptophan, tyrosine, and phenylalanine. This finding is relevant to [[entities/tyrR]] and [[concepts/pathway-completeness]]. [src: pgp_pangenome_ecology]

The association reversed in soil/rhizosphere species (OR = 0.30, p = 0.02) but remained positive in non-soil species (OR = 3.56, p = 7.7e-13). This pattern suggests the hypothesis that soil-associated PGP bacteria may obtain aromatic amino acids from plant exudates, reducing selection for autonomous biosynthesis while retaining ipdC. Because ipdC occurred in only 214 species (1.9%), the soil-specific reversal is hypothesis-generating rather than conclusive. [src: pgp_pangenome_ecology]

## Interpretation

The report proposes that the canonical agricultural PGPB phenotype is better represented by a co-selected **pqqC–acdS** module than by nitrogen fixation. The module is tightly associated, enriched in the rhizosphere, and mostly core, making it a candidate marker of stable plant-associated specialization. This interpretation connects [[concepts/gene-co-inheritance]], [[concepts/metabolic-ecotypes]], and [[concepts/genome-ecology-validation]]. [src: pgp_pangenome_ecology]

Nitrogen fixation appears to represent a separate ecological guild. The observed nifH depletion in soil likely reflects the strong representation of aquatic and marine diazotrophs and host-associated nitrogen fixers in the database, although finer separation of marine, rhizobial, and free-living soil diazotrophs is needed. [src: pgp_pangenome_ecology]

## Limitations

- Environmental labels are incomplete and biased toward clinical and host-associated sampling; soil/rhizosphere coverage is limited. [src: pgp_pangenome_ecology]
- PGP detection relied on exact Bakta gene-name matches, potentially missing product-only annotations and naming variants. [src: pgp_pangenome_ecology]
- Gene presence was not functionally validated, and pseudogenes or truncated clusters may be included. [src: pgp_pangenome_ecology]
- The rarity of ipdC limits power for stratified analyses. [src: pgp_pangenome_ecology]
- GapMind trp and tyr completeness may proxy for overall genome or metabolic completeness; genome size and total pathway count were not controlled. [src: pgp_pangenome_ecology]

## Follow-up Directions

1. Test whether pqqC and acdS are physically linked in operons, genomic islands, or separate loci using [[concepts/gene-neighborhood-inference]].
2. Stratify nifH-bearing species by marine, aquatic, rhizobial, and free-living soil lifestyles.
3. Re-test trp–ipdC coupling while controlling for genome size, pathway count, and overall metabolic completeness.
4. Analyze hcnA–hcnC phylogeny and its relationship to rhizosphere biocontrol phenotypes.
5. Compare pqqC + acdS + hcnC genomes with commercial inoculant strains to evaluate predictive agronomic signatures.

## Source Materials

The report is supported by notebooks covering data extraction, PGP co-occurrence, environmental selection, core/accessory status, and trp–ipdC analysis. Generated datasets include species-level PGP matrices, environmental labels, pangenome statistics, GapMind completeness scores, pairwise co-occurrence results, enrichment models, and stratified trp–ipdC tests. [src: pgp_pangenome_ecology]

## Related Concepts
- [[concepts/two-speed-genome]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/annotation-gap]]
- [[concepts/evidence-triangulation]]
- [[concepts/organism-specificity]]

## Entities
- [[entities/bakta]]
- [[entities/berdl]]
- [[entities/kegg]]
- [[entities/fitness-browser]]
- [[entities/modelseed]]
- [[entities/uniprot]]
