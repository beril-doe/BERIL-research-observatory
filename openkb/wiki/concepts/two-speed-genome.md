---
type: "Concept"
sources: ["summaries/prophage_ecology__REPORT.md", "summaries/prophage_amr_comobilization__REPORT.md", "summaries/phb_granule_ecology__REPORT.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/module_conservation__REPORT.md", "summaries/metal_specificity__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/essential_genome__REPORT.md", "summaries/ecotype_functional_differentiation__REPORT.md", "summaries/cog_analysis__REPORT.md"]
description: "A conserved core and dynamic adaptive genome organize bacterial pangenomes."
---

# Two-Speed Genome Structure

## Definition

The [[concepts/two-speed-genome]] model describes a bacterial pangenome with two functionally distinct components: a conserved core enriched for essential informational and metabolic processes, and a more dynamic novel-gene pool enriched for mobility, defense, ecological adaptation, and poorly characterized functions. The model connects [[concepts/pangenome-integration]] with [[concepts/horizontal-gene-transfer]] by treating gene novelty as functionally structured rather than randomly distributed. [src: cog_analysis]

New evidence refines this model in three ways. First, comparisons among gene-content ecotypes show that the dynamic component differs in functional composition among within-species subpopulations. In a sample of 12 species, every species showed at least one significantly differentiated COG category, and 170 of 257 species-by-COG tests were significant after BH-FDR correction. [src: ecotype_functional_differentiation] Second, cross-organism essentiality data show that the conserved component is not simply the set of genes present across genomes: only 859 of 17,222 ortholog families, or 5.0%, were universally essential across 48 bacteria, while 4,799 families, or 27.9%, were variably essential. [src: essential_genome] Third, analysis of 11,272 species carrying at least one plant-growth-promoting gene found that these genes were generally more core than the genome-wide baseline, with a mean accessory fraction of 29.7% versus 53.2% genome-wide. [src: pgp_pangenome_ecology]

Thus, the two-speed structure includes a deeply conserved functional core, a broad intermediate zone in which indispensability depends on genomic context, and a flexible component that can encode stable ecological specialization rather than only recently acquired traits. [src: essential_genome, pgp_pangenome_ecology]

## Evidence from COG Functional Categories

The original model was evaluated across 357,623 genes from 32 bacterial species spanning 9 phyla. [src: cog_analysis]

- Novel or singleton genes were enriched in COG L, mobile elements, by **+10.88%**, with **100% consistency across species**; this was the strongest reported signal. [src: cog_analysis]
- Novel genes were also enriched in COG V, defense mechanisms, by **+2.83%**, with **100% consistency**, and in COG S, unknown function, by **+1.64%**, with **69% consistency**. [src: cog_analysis]
- Core genes were depleted relative to the overall category distribution in COG J, translation, by **-4.65%**, with **97% consistency**; COG F, nucleotide metabolism, by **-2.09%**, with **100% consistency**; COG H, coenzyme metabolism, by **-2.06%**, with **97% consistency**; COG E, amino acid metabolism, by **-1.81%**, with **81% consistency**; and COG C, energy production, by **-1.75%**, with **88% consistency**. [src: cog_analysis]

Within-species ecotype analysis showed a related but more nuanced pattern. Valid gene-content ecotypes were identified in 12 of 15 sampled species (80%), with 1,820 genomes assigned across the 12 species and an average of 3.7 ecotypes per species, ranging from 2 to 6. [src: ecotype_functional_differentiation] The mean silhouette score was 0.215, indicating overlapping statistical groups rather than sharply separated populations. [src: ecotype_functional_differentiation]

The most frequently differentiated ecotype categories were E, amino acid metabolism (11/12 species; 91.7%); S, unknown function (11/12; 91.7%); V, defense (11/12; 91.7%); and G, carbohydrate metabolism (10/12; 83.3%). [src: ecotype_functional_differentiation] Categories L, replication, recombination, and repair, and S, unknown function, also had the largest mean ecotype effect sizes: 0.0337 and 0.0392, respectively. [src: ecotype_functional_differentiation]

The PGP pangenome analysis provides a complementary example in which ecologically important genes are not concentrated primarily in the accessory genome. Across 13 PGP markers, all genes had significantly higher core fractions than the genome-wide baseline of 46.8%. [src: pgp_pangenome_ecology] Core fractions were 81.5% for pqqC, 78.1% for pqqB, 78.5% for hcnA, 76.5% for ipdC, 70.4% for acdS, 63.8% for nifH, and 55.5% for pqqD. [src: pgp_pangenome_ecology] Pangenome openness correlated negatively with PGP gene richness (Spearman ρ = −0.195, p = 2.0e-97, n = 11,272 species with at least two genomes), suggesting that PGP-rich species tend to have more closed pangenomes. [src: pgp_pangenome_ecology]

The essentiality analysis provides an independent conservation gradient. Across 48 organisms, there were **221,005 genes**, of which **41,059 were essential (18.6%)**, and 2,838,750 bidirectional-best-hit pairs produced 17,222 ortholog groups. [src: essential_genome] Universally essential families were 91.7% core, compared with 88.9% for variably essential families and 81.7% for never-essential families. [src: essential_genome] Orphan essential genes, which had no detectable orthologs in the other Fitness Browser organisms, were only 49.5% core. [src: essential_genome]

Only **15 gene families were essential in all 48 organisms**: ten ribosomal protein families, GroEL, CTP synthase (pyrG), translation elongation factor G (fusA), valyl-tRNA synthetase (valS), and geranyltranstransferase (SelGGPS). [src: essential_genome] This small experimentally defined pan-bacterial essential set identifies a particularly deep layer of the conserved genome, whereas the much larger set of universally essential families captures functions that are indispensable across the sampled organisms but not necessarily every bacterium. [src: essential_genome]

Together, these results support a conserved division between a core cellular “engine” and a flexible adaptive component, while showing that the flexible component can itself be functionally structured within species. [src: cog_analysis, ecotype_functional_differentiation] They also show that essentiality is distributed across the conservation hierarchy rather than mapping perfectly onto core status: 7,084 essential genes were orphans, and 58.7% of those were hypothetical. [src: essential_genome] The PGP results add an important qualification: ecological functions may be stable, lineage-associated components of the core rather than universally mobile accessory traits. [src: pgp_pangenome_ecology]

## Functional Interpretation

Core genes are interpreted as ancient and conserved components supporting translation, energy production, nucleotide metabolism, coenzyme metabolism, and biosynthesis. [src: cog_analysis] The essentiality results directly support this interpretation for a subset of the core: universally essential genes were 91.7% core, and 71% of universally essential families were 100% core across all genomes in their species. [src: essential_genome]

Novel genes are interpreted as more recently acquired or rapidly changing functions that can support ecological adaptation, defense, and niche specialization. [src: cog_analysis] However, the PGP analysis shows that niche specialization need not imply accessory status. The pqqC–acdS combination was strongly associated across species (OR = 7.24, n = 286 co-occurring species, q = 1.2e-83), and acdS and pqqC were enriched in soil or rhizosphere species with odds ratios of 7.02 and 2.90, respectively. [src: pgp_pangenome_ecology] These traits were predominantly core, suggesting the hypothesis that some ecological adaptations become stabilized in specialized lineages rather than remaining primarily HGT-driven. [src: pgp_pangenome_ecology]

The strong COG L enrichment in the core-versus-novel analysis suggests the hypothesis that mobile genetic elements are a major route by which bacterial genomes acquire novel functions. [src: cog_analysis] The ecotype analysis provides convergent functional evidence: category L was significantly differentiated in 9 of 12 species, and category V, defense, was significant in 11 of 12 species. [src: ecotype_functional_differentiation] These findings are consistent with mobility and defense being important features of the dynamic genome, but neither analysis directly demonstrates individual horizontal-transfer events. [src: cog_analysis, ecotype_functional_differentiation]

The essentiality results qualify the idea that the dynamic genome is uniformly dispensable. Variably essential families had a median essentiality penetrance of 33%, with 813 families more than 50% essential and 704 less than 10% essential. [src: essential_genome] This pattern indicates that accessory or variably conserved functions can become indispensable in particular genomic contexts, potentially because of missing alternatives, paralog differences, or compensatory functions. [src: essential_genome] It therefore connects the two-speed model with [[concepts/functional-redundancy]], [[concepts/compensatory-evolution]], and [[concepts/condition-dependent-essentiality]]. The essentiality classification was measured under specific transposon-library conditions, so these context-dependent assignments should not be treated as universal properties of the genes. [src: essential_genome]

The ecotype results further distinguish adaptive shifts from a background of broader genome variation. Adaptive categories V, P, G, E, Q, M, and K had a significance rate of 79.8% (67/84), compared with 68.8% (33/48) for housekeeping categories J, F, H, and C. [src: ecotype_functional_differentiation] Their mean effect size was 0.0136 versus 0.0064 for housekeeping categories, a 2.13-fold difference that was significant by one-sided Mann–Whitney U test (p = 2.53 x 10^-6). [src: ecotype_functional_differentiation] Thus, ecotypes differ in housekeeping functions as well as adaptive functions, but adaptive categories show larger proportional shifts. [src: ecotype_functional_differentiation]

The PGP findings extend this distinction from broad functional categories to an ecological trait system. pqqC was positively associated with hcnC (OR = 1.91) and ipdC (OR = 1.55), while nifH was negatively associated with hcnC (OR = 0.23, q = 5.8e-29) and pqqC (OR = 0.57, q = 2.9e-19). [src: pgp_pangenome_ecology] This suggests that the pqqC–acdS-associated rhizosphere phenotype and the nifH-associated diazotrophic phenotype are distinct ecological configurations within the broader PGP gene space. [src: pgp_pangenome_ecology]

This pattern complements [[concepts/structural-novelty]] and [[concepts/ecological-generalism]]: accessory genes may contribute to ecological and resistance variation, while core genes can encode stable adaptations to specialized environments. [src: cog_analysis, pgp_pangenome_ecology] The negative association between PGP gene richness and pangenome openness further suggests that ecological specialization can coincide with genomic closure, although this is an association rather than proof of causation. [src: pgp_pangenome_ecology]

Ecotype clusters may also reflect within-species phylogenetic or demographic structure; without core-genome phylogenies, the current analysis cannot distinguish ecological specialization from lineage-associated gene-content differences. [src: ecotype_functional_differentiation] Any comparison of core and novel functions should also account for [[concepts/annotation-gap]], because COG annotations covered approximately 70% of genes in the original analysis and approximately 38% of gene clusters in the ecotype study. [src: cog_analysis, ecotype_functional_differentiation]

The orphan-essential result adds a second form of functional darkness to the model. There were 8,297 hypothetical essential genes, including 4,385 orphan genes that could not be predicted by the module-transfer method. [src: essential_genome] For 3,912 hypothetical essential genes with orthologs, transfer from non-essential orthologs in ICA fitness modules generated 1,382 family-backed function predictions. [src: essential_genome] These findings suggest that the dynamic and poorly annotated portion of bacterial genomes is not synonymous with dispensability: some poorly characterized, weakly conserved genes are required under the tested conditions. [src: essential_genome] This observation strengthens the relevance of [[concepts/resource-darkness]] and [[concepts/annotation-gap]] to interpreting the two-speed genome.

## Composite Functional Categories

Composite COG assignments should not automatically be treated as annotation noise. The LV combination, representing mobile and defense functions, showed **+0.34% enrichment** with **76% consistency**, supporting the possibility of multifunctional “mobile defense islands.” [src: cog_analysis]

These composite categories were counted once per gene rather than split among component functions, so their enrichment values describe genes carrying the composite assignment under that counting scheme. [src: cog_analysis]

The ecotype study did not analyze the LV composite category as a separate reported result, but its strong category L signal provides related support for a mobile-element contribution to ecotype differentiation. [src: ecotype_functional_differentiation] This comparison should therefore be treated as convergent category-level evidence rather than as a direct replication of the LV result. [src: cog_analysis, ecotype_functional_differentiation]

The PGP analysis provides a contrasting example of trait co-inheritance without evidence of physical gene linkage. pqqC and acdS were strongly co-occurring and environmentally enriched, but the report did not test whether they were colocated on chromosomes, plasmids, genomic islands, or operons. [src: pgp_pangenome_ecology] Their association therefore supports co-selection or shared lineage ecology, not a demonstrated mobile defense-like island. [src: pgp_pangenome_ecology]

## Scope and Limitations

The original analysis used 32 species and eggNOG v6 annotations, which may differ from original COG assignments. [src: cog_analysis] Unassigned genes may skew category distributions, and counting composite categories once per gene may obscure the contribution of individual component functions. [src: cog_analysis]

The essentiality analysis used 48 Fitness Browser organisms and bidirectional-best-hit orthology. [src: essential_genome] Its essential-gene definition is an upper bound because absent transposon insertions can result from small gene size, AT-rich sequence, or scaffold-edge effects rather than true essentiality. [src: essential_genome] Conservative orthology may miss divergent homologs, paralogs, and gene fusions, so some apparent orphan essentials may have undetected relatives. [src: essential_genome] Connected-component clustering can also over-merge unrelated genes, particularly in multidomain proteins. [src: essential_genome]

The ecotype analysis used a stratified sample of 15 species from 456 eligible species, with valid clusters in 12 species. [src: ecotype_functional_differentiation] KMeans was used after PCA because HDBSCAN was unavailable, and moderate silhouette scores indicate that the resulting ecotypes are statistical tendencies rather than sharply defined populations. [src: ecotype_functional_differentiation] Approximately 38% of gene clusters had COG annotations in the ecotype study, leaving potentially informative unannotated genes outside the functional comparison. [src: ecotype_functional_differentiation]

The PGP analysis relied on exact Bakta gene-name matches, so genes annotated only by product description or variant names may have been missed. [src: pgp_pangenome_ecology] Gene clusters were not functionally validated for truncations, frameshifts, or pseudogenization. [src: pgp_pangenome_ecology] Environmental classification was conservative and limited: only 1,637 species, or 5.9% of species with environmental labels, were classified as soil/rhizosphere dominant. [src: pgp_pangenome_ecology] The reported soil enrichment effects may therefore underestimate true rhizosphere enrichment, while database sampling bias may distort comparisons among environments. [src: pgp_pangenome_ecology]

Essentiality is condition-dependent: RB-TnSeq measurements were obtained under specific library-construction conditions, typically rich media, and may miss genes required during stress or in other environments. [src: essential_genome] The 48 organisms are taxonomically limited and biased toward culturable bacteria, so the 15 pan-essential families should not yet be treated as universal across all bacterial and archaeal diversity. [src: essential_genome]

The combined evidence strongly supports structured functional differences in bacterial pangenomes, but it does not establish that every dynamic-genome difference is adaptive, that every core gene is indispensable, or that every core PGP gene is vertically inherited without HGT. [src: cog_analysis, ecotype_functional_differentiation, essential_genome, pgp_pangenome_ecology] The PGP conclusions are also limited by ipdC rarity, incomplete environmental metadata, and the possibility that pathway completeness reflects overall genome completeness rather than a specific biochemical relationship. [src: pgp_pangenome_ecology]

## Relationship to Other Concepts

- [[concepts/pangenome-integration]] provides the broader framework for combining core, accessory, singleton, and essentiality evidence.
- [[concepts/horizontal-gene-transfer]] offers a mechanism for the mobility-associated enrichment among novel genes.
- [[concepts/annotation-gap]] identifies an important limitation caused by incomplete functional assignment and helps interpret hypothetical orphan essentials.
- [[concepts/core-accessory-resistance]] is relevant to testing whether the dynamic genome component is disproportionately associated with resistance-related functions.
- [[concepts/structural-novelty]] addresses how genomic novelty can be distinguished from merely divergent versions of known genes.
- [[concepts/phylogenetic-confounding]] is central to determining whether ecotype-associated functional differences reflect ecological adaptation or demographic substructure.
- [[concepts/mobile-genetic-elements]] is relevant to the recurrent enrichment and differentiation of category L functions.
- [[concepts/gene-essentiality]] provides the framework for interpreting universally, variably, and orphan-essential gene families.
- [[concepts/functional-redundancy]] and [[concepts/compensatory-evolution]] offer explanations for why homologous families can be essential in some organisms but dispensable in others.
- [[concepts/condition-dependent-essentiality]] is necessary for interpreting essentiality measured under defined RB-TnSeq conditions.
- [[concepts/resource-darkness]] captures the importance of poorly annotated genes, including hypothetical essential genes, within the dynamic genome.
- [[concepts/gene-co-inheritance]] is relevant to testing whether co-occurring PGP traits reflect shared lineage inheritance or physical linkage.
- [[concepts/pathway-completeness]] provides a framework for interpreting the relationship between aromatic amino-acid biosynthesis and ipdC occurrence.

The source analyses and their supporting data are summarized in [[summaries/cog_analysis__REPORT]], [[summaries/ecotype_functional_differentiation__REPORT]], [[summaries/essential_genome__REPORT]], and [[summaries/pgp_pangenome_ecology__REPORT]].

## Open Directions

- Re-run the COG distribution analysis with additional species and explicit phylum-level models to test whether the reported enrichment is universal or taxon-specific. [src: cog_analysis]
- Scale ecotype functional-differentiation tests from the 12-species sample to all 456 eligible species to assess the generality of within-species functional structuring. [src: ecotype_functional_differentiation]
- Separate single-letter and composite COG assignments, then compare gene-level and component-level counting to determine how much LV and other composite signals depend on the counting rule. [src: cog_analysis]
- Overlay core-genome phylogenetic trees on ecotype assignments and use phylogenetically controlled enrichment models to test whether adaptive-category effects persist after demographic structure is accounted for. [src: ecotype_functional_differentiation]
- Compare COG assignments with independent functional annotations to quantify how the approximately 30% unassigned fraction in the original analysis and the approximately 62% unannotated fraction in the ecotype analysis affect the two-speed pattern. [src: cog_analysis, ecotype_functional_differentiation]
- Integrate environmental metadata with ecotype assignments and COG profiles to test whether dynamic-genome functions vary systematically by habitat. [src: ecotype_functional_differentiation]
- Map variably essential families onto pathway-completeness and paralog inventories to test whether alternative metabolism or functional redundancy explains organism-specific essentiality. [src: essential_genome]
- Compare orphan-essential genes with mobile-element annotations, gene-age estimates, and within-species conservation to distinguish recently acquired functions from rapidly evolving ancestral genes. [src: essential_genome]
- Experimentally test the 1,382 module-transfer predictions with CRISPRi or targeted perturbations under the module-associated conditions. [src: essential_genome]
- Expand the essentiality panel taxonomically and compare the resulting pan-essential set with the existing two-speed functional categories to test whether the conserved/dynamic boundary shifts across lineages. [src: essential_genome]
- Test whether pqqC and acdS are physically colocated in operons, genomic islands, or separate loci, distinguishing physical linkage from shared ecological selection. [src: pgp_pangenome_ecology]
- Reanalyze the PGP core/accessory pattern with phylogenetic controls and broader gene-detection methods to determine whether core enrichment persists across lineages and annotation strategies. [src: pgp_pangenome_ecology]
- Stratify nifH-bearing species by aquatic, marine, rhizobial, and free-living soil lifestyles to determine whether nitrogen-fixation traits occupy distinct genome-ecology regimes. [src: pgp_pangenome_ecology]
- Re-test the trp–ipdC relationship while controlling for genome size, total pathway count, and overall metabolic completeness. [src: pgp_pangenome_ecology]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/gene_function_ecological_agora__REPORT]]

See also: [[summaries/metabolic_capability_dependency__REPORT]]

See also: [[summaries/metal_fitness_atlas__REPORT]]

See also: [[summaries/metal_specificity__REPORT]]

See also: [[summaries/module_conservation__REPORT]]

See also: [[summaries/phb_granule_ecology__REPORT]]

See also: [[summaries/prophage_amr_comobilization__REPORT]]

See also: [[summaries/prophage_ecology__REPORT]]