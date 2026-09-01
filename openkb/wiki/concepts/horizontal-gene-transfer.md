---
type: "Concept"
sources: ["summaries/t4ss_cazy_environmental_hgt__REPORT.md", "summaries/snipe_defense_system__REPORT.md", "summaries/prophage_ecology__REPORT.md", "summaries/prophage_amr_comobilization__REPORT.md", "summaries/phb_granule_ecology__REPORT.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/pathway_capability_dependency__REPORT.md", "summaries/pangenome_openness__REPORT.md", "summaries/module_conservation__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/field_vs_lab_fitness__REPORT.md", "summaries/ecotype_analysis__REPORT.md", "summaries/costly_dispensable_genes__REPORT.md"]
description: "Evidence for HGT, mobile-element transfer, and limits of accessory-genome inference"
---

# Horizontal Gene Transfer and Accessory Genome Dynamics

## Overview

[[concepts/horizontal-gene-transfer]] can expand bacterial accessory genomes by introducing genes absent from much of the surrounding pangenome. The costly+dispensable genes report identifies a subset of this accessory DNA that imposes a measurable laboratory fitness burden while lacking broad conservation. [src: costly_dispensable_genes]

The central interpretation is that these genes are disproportionately associated with mobile genetic elements and other recently acquired sequences, rather than representing poorly maintained core metabolic genes. This connects accessory-genome structure to acquisition, persistence, and loss. [src: costly_dispensable_genes]

New T4SS–CAZy evidence extends this framework from mobile-element annotation and pangenome structure to environmental loci and gene-tree incongruence. Among 30,497 high-quality environmental MAGs, 6,652 (21.8%) carried T4SS or conjugative machinery under a multi-marker definition. Ninety-two CAZy families showed elevated co-occurrence with T4SS loci at distances of ≤10 kb, with GT2 glycosyltransferases the top hit. [src: t4ss_cazy_environmental_hgt]

The T4SS analysis found enrichment in marine sediment (OR=5.5, q<10⁻⁹⁸), barley rhizosphere (OR=10.4), and maize rhizosphere (OR=4.1). A GT2 gene tree contained 77 detected HGT events, including 32 high-confidence normalized cross-phylum events; the strongest, Node_4915, spanned eight phyla at maximum divergence of 4.843. [src: t4ss_cazy_environmental_hgt]

The same study did not find CAZy genes on plasmids in its ICEfinder analysis: only 12 IMEs appeared among the top 100 accumulators. T4SS-positive genomes had 10× higher MGE density (p<0.001), which is consistent with chromosomal or integrative transfer through IMEs or ICEs rather than plasmid mobilization. These are observational results and do not establish that T4SS machinery directly mediates the transfers. [src: t4ss_cazy_environmental_hgt]

New prophage–AMR evidence likewise strengthens the association between horizontal transfer and accessory-genome structure, while separating species-level association from local evidence of mobilization. Across 27,702 species, 14,669 (52.9%) carried both AMR and prophage markers. Among AMR instances in 1,953 genomes from 100 highly AMR-burdened species, 55.7% were on contigs carrying strict prophage markers and 10.4% were within 10 genes of a prophage marker. [src: prophage_amr_comobilization]

At species level, prophage density predicted AMR repertoire breadth across 4,770 species (Spearman rho=0.572, p<10^-300). The association remained after controlling for genome count (partial Spearman rho=0.464, p=1.0×10^-253) and was significant across five major phyla. This supports prophage density as a marker of gene-acquisition potential or shared mobile-element ecology, but does not prove phage-mediated AMR transfer. [src: prophage_amr_comobilization]

A complementary PHB pangenome analysis provides direct evidence that horizontal transfer can introduce a metabolic pathway into otherwise depleted lineages. Among 311 species identified as potential phaC acquisitions because they carried the gene despite belonging to families with less than 20% phaC prevalence, 60.1% carried phaC as accessory genome, compared with 32.3% across all phaC-carrying species. These remain putative events without gene-tree/species-tree reconciliation. [src: phb_granule_ecology]

The PGP pangenome analysis provides an important counterweight: PGP genes were predominantly core across 11,272 species, with core fractions above the 46.8% genome-wide baseline for all 13 analyzed genes. A functionally important gene is therefore not necessarily a recent horizontal acquisition. [src: pgp_pangenome_ecology]

Pangenome openness also did not significantly predict whether gene-content variation was associated more strongly with environment or phylogeny. Openness had a Spearman rho of -0.05 with environment effects (p=0.54) and 0.03 with phylogeny effects (p=0.73). An open pangenome should therefore not automatically be interpreted as evidence of environment-driven acquisition or adaptation. [src: pangenome_openness]

## Evidence for Mobile-Element-Driven Accessory DNA

Among 142,190 genes from 43 bacteria, 5,526 were classified as both costly and dispensable. These genes were 7.45 times more likely than costly+conserved genes to contain mobile-element keywords such as transposase, integrase, phage, insertion sequence, recombinase, or prophage (OR=7.45, p=4.6e-71). The SEED category “Phages, Prophages, Transposable elements, Plasmids” was 11.7-fold enriched (FDR=1.3e-17), while “Virulence” was 26.7-fold enriched (FDR=5.6e-14), although the latter used small counts of 21 versus 4 genes. [src: costly_dispensable_genes]

Together, these results provide strong direct support for an association between costly accessory genes and [[concepts/mobile-genetic-elements]]. They also support a [[concepts/two-speed-genome]] view in which relatively stable core regions coexist with more rapidly changing accessory regions. [src: costly_dispensable_genes]

The T4SS–CAZy study supplies an independent environmental example of mobile-element-associated transfer potential. T4SS/conjugative machinery was present in 21.8% of the surveyed MAGs, and T4SS loci co-occurred with 92 elevated CAZy families within the tested ≤10 kb threshold. GT2 glycosyltransferases occurred in 767 genomes, with an average distance of 5,041 bp. [src: t4ss_cazy_environmental_hgt]

The T4SS result is mechanistically suggestive but does not reduce to plasmid transfer. ICEfinder identified no plasmid-borne CAZy genes in the reported analysis, whereas T4SS-positive genomes had 10× higher MGE density (p<0.001). This pattern is consistent with chromosomal or integrative transfer, including IME/ICE-mediated mobilization, but threshold validation and direct experimental evidence are still required. [src: t4ss_cazy_environmental_hgt]

The prophage–AMR atlas provides a second, much larger mobile-element association. Across the full pangenome, it identified 83,008 AMR gene clusters, 1,261,929 strict prophage-marker clusters, and 3,465,244 broad prophage-marker clusters. AMR clusters were 69.7% accessory, whereas prophage-marker clusters were 83.8% accessory; prophage markers were also more often singletons than AMR genes (53.8% versus 36.1%). [src: prophage_amr_comobilization]

Gene-level proximity was weaker than the overall co-occurrence signal. Of 36,041 AMR instances, 20,073 (55.7%) were on prophage-bearing contigs, 12,026 (33.4%) were within 50 genes, 7,137 (19.8%) within 20 genes, 3,731 (10.4%) within 10 genes, and 1,991 (5.5%) within 5 genes of a prophage marker. [src: prophage_amr_comobilization]

The PHB analysis extends the mobile-gene pattern beyond defense and mobile-element annotations. Across 27,690 GTDB species, 6,067 carried phaC, and 1,959 carried it as accessory genome while 5,371 carried it as core; some species had both core and accessory copies. The accessory fraction was especially high in SAR324, Bacillota_A, and Eremiobacterota, suggesting that these lineages may be active recipients of phaC, although this remains an inference from pangenome structure. [src: phb_granule_ecology]

The PGP results show that the mobile-gene pattern is not universal. Across the BERDL pangenome, pqqC was 81.5% core, acdS was 70.4% core, nifH was 63.8% core, and pqqD was 55.5% core. The mean accessory fraction across PGP genes was 29.7%, compared with 53.2% genome-wide. [src: pgp_pangenome_ecology]

The pangenome-openness result indicates that mobile-element-associated accessory structure does not necessarily map onto measured environmental or phylogenetic effect sizes. Its null correlations are compatible with multiple acquisition processes but do not identify the mechanism generating the lack of association. [src: pangenome_openness]

## Signatures of Recent Acquisition

Costly+dispensable genes have several features expected of recently acquired or weakly established DNA:

- SEED annotation was present for 50.8%, compared with 74.9% of costly+conserved genes.
- KEGG annotation was present for 20.0%, compared with 42.7% of costly+conserved genes.
- 44.5% were orphan genes with no ortholog group, compared with 13.1% of costly+conserved genes.
- Median ortholog breadth was 15 organisms, compared with 31 for costly+conserved genes (Mann–Whitney p=4.0e-99; rank-biserial r=0.233).
- 24.2% were singletons found in one genome, while no costly+conserved genes were singletons.
- Median length was 615 bp, compared with 765 bp for costly+conserved genes (p=4.2e-75; rank-biserial r=0.170).

These patterns are consistent with recent acquisition, sequence fragmentation, and limited residence time in the broader pangenome. The interpretation remains inferential for individual genes because ortholog assignment covered only 48 organisms and Fitness Browser genes were linked to pangenome clusters at a 90% identity threshold. [src: costly_dispensable_genes]

The annotation deficit also links accessory-genome dynamics to [[concepts/annotation-gap]]: poorly characterized genes are disproportionately represented among sequences with the narrowest observed distributions. [src: costly_dispensable_genes]

The T4SS–CAZy analysis provides a stronger phylogenetic signature for a defined gene family. Of 77 GT2-tree events, 65 spanned two phyla and 12 spanned at least three phyla (15.6%). Node_4915 contained 35 genes, 82.9% synteny, representatives from eight phyla, and Max_Divergence=4.843. Across events, divergence and synteny were negatively correlated (Spearman rho=-0.615, p<0.001), consistent with sequence divergence after transfer. [src: t4ss_cazy_environmental_hgt]

GT2-neighbourhood analysis further supports local functional coupling: among 376 genomes, T4SS occurred in 503 neighbourhood entries and GT2 in 495. GH23, a murein lytic transglycosylase, occurred 106 times and was the second most common CAZy family in GT2 neighbourhoods, suggesting that cell-wall-remodelling functions cluster with GT2–T4SS loci. [src: t4ss_cazy_environmental_hgt]

The T4SS study also identified a metal-resistance association. GT2-neighbourhood MAGs (n=376) had a mean of 0.045 metal-resistance types versus 0.004 in non-GT2 MAGs (n=260,276; Mann–Whitney p=8.6e-27); the report describes genomes with GT2 in T4SS-proximal neighbourhoods as carrying 11× more metal-resistance genes. This supports a possible relationship between HGT hubs and [[concepts/metal-resistance-breadth]], but it is an observational association. [src: t4ss_cazy_environmental_hgt]

The PHB results provide a second acquisition signature: in phylogenetically discordant phaC-positive species, the accessory rate reached 60.1% versus 32.3% across all phaC-carrying species. The strongest putative recipient families included Lachnospiraceae (38 acquisitions; 3.1% family prevalence), Chitinophagaceae (22; 12.4%), Pelagibacteraceae (13; 5.3%), Enterobacteriaceae (11; 2.3%), and Planococcaceae (10; 12.8%). [src: phb_granule_ecology]

The prophage–AMR results complicate local proximity as a recent-acquisition signature. AMR genes within 10 genes of prophage markers were only slightly more accessory than distal AMR genes (67.6% versus 65.5%; OR=1.10, p=0.005; bootstrap 95% CI [1.024, 1.185]). The effect was absent or reversed at 3–5 genes and strengthened at broader thresholds, reaching OR=1.28 at 50 genes. Only 33 of 74 testable species had OR>1, with a median species-level OR of 0.85. [src: prophage_amr_comobilization]

This threshold sensitivity suggests that immediate neighbours of phage structural genes may be core phage components, whereas broader intervals may capture genomic islands containing prophage remnants and laterally transferred genes. Because the study used ordinal gene positions and keyword/Pfam prophage calls rather than dedicated prediction tools, this interpretation remains a hypothesis. [src: prophage_amr_comobilization]

The PGP results show that narrow distribution and accessory status must be interpreted alongside gene function and lineage. PGP-rich species had more closed, not more open, pangenomes: PGP gene richness correlated negatively with singleton fraction (Spearman rho=-0.195, p=2.0e-97, n=11,272 species with at least two genomes). This is consistent with stable ecological specialization but does not prove vertical inheritance or exclude transfer. [src: pgp_pangenome_ecology]

Pangenome openness remains a coarse summary metric. Because it was not associated with environment or phylogeny effects, auxiliary fraction, Heap’s law alpha, and pangenome fluidity may be more informative for testing whether particular dimensions of accessory structure track ecological or evolutionary drivers. [src: pangenome_openness]

## Cost, Persistence, and Gene Loss

Costly+dispensable genes were defined using `max_fit > 1` in at least one experiment, meaning that deletion improved fitness under at least one tested condition. This indicates burden under measured laboratory conditions, not universal cost across environments. [src: costly_dispensable_genes]

Fourteen SEED top-level categories—including Protein Metabolism, Respiration, Carbohydrates, Amino Acids, Cofactors/Vitamins, Motility, Stress Response, and RNA Metabolism—were significantly depleted among costly+dispensable genes at FDR<0.05. [src: costly_dispensable_genes]

Many costly+dispensable genes may therefore be candidates for ongoing gene loss: they may have entered through HGT, impose a host burden, and lack sufficient broad benefit for maintenance across the pangenome. This is an evolutionary hypothesis rather than a directly observed temporal trajectory. [src: costly_dispensable_genes]

Persistence is not necessarily evidence of neutrality. A total of 14.1% of costly+dispensable genes had condition-specific phenotypes, compared with 16.7% of costly+conserved genes and 2.7% of neutral+dispensable genes. Accessory status can therefore coexist with conditional value, connecting this result to [[concepts/condition-dependent-essentiality]] and [[concepts/core-accessory-resistance]]. [src: costly_dispensable_genes]

The prophage–AMR atlas adds a species-level persistence model. Species with higher prophage-marker density carried broader AMR repertoires, with a log-log regression slope of 0.823 (SE=0.018; R²=0.30). The association persisted after controlling for genome count and across five major phyla, but the analysis could not determine whether prophages directly mobilize AMR genes or whether both are favoured in species with broader acquisition capacity. [src: prophage_amr_comobilization]

The PHB study adds a pathway-specific persistence model. PhaC prevalence was 44.0% in plant-associated species, 43.6% in soil, and 34.5% in wastewater/engineered environments, compared with 18.7% in marine, 7.4% in human clinical, and 3.3% in animal-associated species. Within every genome-size quartile, high-variability environments had higher phaC prevalence than low-variability environments, with fold enrichments from 1.4x to 4.6x and all p-values below 1e-11. These results suggest that transfer and retention of phaC may be favoured by recurrent carbon fluctuation, without establishing the timing or direction of individual transfers. [src: phb_granule_ecology]

The PGP findings provide a contrasting persistence model. The pqqC–acdS combination was strongly associated across species (OR=7.24), enriched in soil/rhizosphere species, and composed largely of core genes. This suggests the hypothesis that some transferable traits can become stably retained and vertically inherited after ecological specialization. [src: pgp_pangenome_ecology]

## Organism-Specific Dynamics

*Pseudomonas stutzeri* RCH2 was an outlier, with 21.5% of its genes classified as costly+dispensable, compared with 14.0% in the next organism, *Bacteroides thetaiotaomicron*. Possible explanations include recent phage invasion, insertion-sequence expansion, or genomic-island acquisition, but the cause was not resolved. [src: costly_dispensable_genes]

This outlier emphasizes organism- and strain-specific accessory-genome dynamics, related to [[concepts/organism-specificity]]. [src: costly_dispensable_genes]

The prophage–AMR study likewise found substantial species heterogeneity: only 33 of 74 testable species showed an accessory-enrichment odds ratio above 1 for AMR genes within 10 genes of prophage markers, and the median species-level OR was 0.85. Aggregate co-localization is therefore not a universal organism-level mechanism. [src: prophage_amr_comobilization]

The T4SS–CAZy associations were also biome-specific, with distinct enrichment in marine sediment, barley rhizosphere, and maize rhizosphere. This indicates that environmental context may shape the distribution of candidate transfer hubs, although biome-level enrichment does not establish transfer direction or mechanism. [src: t4ss_cazy_environmental_hgt]

The PHB analysis identified lineage-specific acquisition patterns in families with low phaC prevalence, while the PGP analysis found gene-specific conservation. In particular, pqqD had the lowest core fraction among the analyzed PGP genes (55.5%) and the highest singleton fraction (27.5%), suggesting that it may sometimes spread horizontally as a standalone gene even though the pqqB–pqqC module is predominantly core. [src: pgp_pangenome_ecology]

## Relationship to Community Evolution

The mobile-element accumulation described here should be distinguished from [[concepts/black-queen-dynamics]]. Costly+dispensable genes were predominantly associated with selfish elements rather than metabolic functions, so their loss should not automatically be interpreted as adaptive outsourcing of a public-good pathway. [src: costly_dispensable_genes]

A subset could nevertheless participate in community dependency if gene loss removes functions supplied by neighbouring organisms. Testing this possibility requires combining gene presence and absence with community composition and metabolic-support data, linking the question to [[concepts/metabolic-support-networks]]. [src: costly_dispensable_genes]

The PGP analysis provides a contrasting community-relevant trait architecture. The pqqC–acdS module was associated with soil/rhizosphere specialization, whereas nifH was negatively associated with pqqC and hcnC and depleted in soil-classified species. These distributions could reflect transfer, differential loss, niche filtering, or database sampling structure. [src: pgp_pangenome_ecology]

The PHB study similarly connects gene distribution to ecological selection without demonstrating community dependency. PHB inference scores from NMDC were negatively correlated with depth (rho=-0.119, p=1.14 x 10^-21) and positively correlated with temperature (rho=0.088, p=1.86 x 10^-12). [src: phb_granule_ecology]

The T4SS–CAZy study adds a possible connection between transfer hubs and metal-resistance ecology: GT2-neighbourhood MAGs carried 11× more metal-resistance genes than non-GT2 MAGs in the reported comparison. This supports a testable link to [[concepts/environmental-metal-tolerance]] and [[concepts/metal-resistance-breadth]], but does not distinguish co-selection from shared habitat or transfer mechanism. [src: t4ss_cazy_environmental_hgt]

The null association between openness and environment effects does not rule out community-level or gene-function-specific ecological selection. It indicates only that the aggregate openness metric did not predict the available environment-effect estimates in the analyzed species set. [src: pangenome_openness]

## Tensions

The costly+dispensable profile is consistent with genomic debris from HGT, but the same genes can show condition-specific phenotypes. “Costly” and “dispensable” should therefore not be treated as synonymous with useless or destined for immediate deletion. [src: costly_dispensable_genes]

The T4SS–CAZy findings create a related tension between locus co-localization and demonstrated mechanism. GT2 loci were co-localized with T4SS machinery, and GT2 phylogenetic incongruence provided evidence for 32 cross-phylum events, but the ≤10 kb threshold remains pending validation, Node_4915 requires BLAST validation, and no experiment demonstrated T4SS-mediated transfer. The absence of plasmid-borne CAZy genes redirects attention toward chromosomal or integrative mechanisms without proving that interpretation. [src: t4ss_cazy_environmental_hgt]

The prophage–AMR association creates a tension between co-occurrence and mechanism. Prophage markers occurred on the same contigs as 55.7% of AMR instances, and prophage density predicted AMR breadth strongly, but local proximity predicted accessory status only weakly and heterogeneously. [src: prophage_amr_comobilization]

The recent-acquisition signal is limited by incomplete annotation, binary core/accessory definitions, ortholog searches restricted to 48 organisms, and the 90% identity linking threshold. The prophage analysis additionally used keyword/Pfam calls, ordinal gene positions, and a sample of 20 genomes per species rather than all 293,000 genomes. [src: costly_dispensable_genes, prophage_amr_comobilization]

The PHB HGT signal is also inferential: 311 acquisitions and 278 losses were defined from family-level prevalence discordance, while the 60.1% accessory rate provided supporting evidence. Gene-tree/species-tree reconciliation and genomic-context analysis are needed to resolve the events. [src: phb_granule_ecology]

The PGP pangenome analysis rejects a general HGT-centred model for its focal genes: all 13 PGP genes had core fractions above the 46.8% genome-wide baseline, although pqqD retained a comparatively high singleton fraction of 27.5%. Core status is not proof that historical transfer never occurred, and exact-name annotation can miss divergent homologues. [src: pgp_pangenome_ecology]

These acquisition and stable-inheritance signals apply to different gene sets and should not be collapsed into one genome-wide rule. Mobile-element-associated costly genes, prophage-associated AMR patterns, T4SS-proximal GT2 loci, and discordant phaC copies can show acquisition signatures, whereas ecologically specialized PGP genes can be predominantly core. [src: costly_dispensable_genes, prophage_amr_comobilization, t4ss_cazy_environmental_hgt, phb_granule_ecology, pgp_pangenome_ecology]

## Open Directions

- Validate the T4SS–CAZy synteny threshold with a permutation test using unfiltered Spark data, and test whether the discovery/validation replication persists under alternative distance thresholds. [src: t4ss_cazy_environmental_hgt]
- Validate Node_4915 with BLAST against NCBI nr and compare GT2 gene and species trees to distinguish cross-phylum transfer from contamination, paralogy, or misannotation. [src: t4ss_cazy_environmental_hgt]
- Establish a housekeeping-gene null baseline and factorize biome enrichment using θ = OR(T4SS-CAZy) / [OR(T4SS) × OR(CAZy)]. [src: t4ss_cazy_environmental_hgt]
- Map GT2 and CAZy loci to contigs, IMEs, ICEs, plasmids, and chromosomal islands to test whether the observed 10× MGE-density difference reflects integrative transfer. [src: t4ss_cazy_environmental_hgt]
- Test whether the GT2–metal-resistance association survives controls for biome, phylogeny, genome quality, and MGE density, and determine whether resistance genes share physical neighbourhoods with GT2–T4SS loci. [src: t4ss_cazy_environmental_hgt]
- Apply geNomad or PHASTER to BERDL genomes and test whether AMR–prophage co-localization and prophage-density/AMR-breadth relationships survive validated prophage calls. [src: prophage_amr_comobilization]
- Use contig sequences to calculate base-pair distances and determine whether the reversal at 3–5 genes reflects phage structural neighbourhoods or an ordinal-position artefact. [src: prophage_amr_comobilization]
- Partition prophage, plasmid, and integrative-conjugative-element contributions to AMR co-localization and test whether each element class predicts AMR breadth independently. [src: prophage_amr_comobilization]
- Analyze *P. stutzeri* RCH2 for phage regions, insertion-sequence expansions, plasmids, and genomic islands to distinguish explanations for its 21.5% costly+dispensable fraction. [src: costly_dispensable_genes]
- Test whether costly+dispensable genes cluster near tRNA genes, genomic-island boundaries, or scaffold edges, and compare closely related strains to determine whether they are being lost over evolutionary time. [src: costly_dispensable_genes]
- Reanalyze pangenome openness by functional category and compare auxiliary fraction, Heap’s law alpha, and pangenome fluidity against environment and phylogeny effects. [src: pangenome_openness]
- Reconstruct phaC gene and species trees, and map phaC copies to genomic neighbourhoods and mobile-element contexts to distinguish true transfer from incomplete sampling. [src: phb_granule_ecology]
- Map pqqC and acdS to genomic neighbourhoods and mobile-element contexts, and reconstruct gene and genome phylogenies for pqqC, acdS, nifH, and pqqD to distinguish vertical inheritance, lineage-specific loss, and recurrent transfer. [src: pgp_pangenome_ecology]

## Related Documents

- [[summaries/t4ss_cazy_environmental_hgt__REPORT]]
- [[summaries/pangenome_openness__REPORT]]
- [[summaries/pathway_capability_dependency__REPORT]]
- [[summaries/pgp_pangenome_ecology__REPORT]]
- [[summaries/phb_granule_ecology__REPORT]]
- [[summaries/prophage_amr_comobilization__REPORT]]
- [[summaries/prophage_ecology__REPORT]]
- [[summaries/snipe_defense_system__REPORT]]
- [[summaries/ecotype_analysis__REPORT]]
- [[summaries/field_vs_lab_fitness__REPORT]]
- [[summaries/metabolic_capability_dependency__REPORT]]
- [[summaries/module_conservation__REPORT]]