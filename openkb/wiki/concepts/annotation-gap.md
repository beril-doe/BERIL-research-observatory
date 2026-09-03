---
type: "Concept"
sources: ["summaries/truly_dark_genes__REPORT.md", "summaries/respiratory_chain_wiring__REPORT.md", "summaries/prophage_ecology__REPORT.md", "summaries/pitfalls.md", "summaries/phage_defense_arsenal__REPORT.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/pathway_capability_dependency__REPORT.md", "summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md", "summaries/lanthanide_methylotrophy_atlas__REPORT.md", "summaries/gene_function_ecological_agora__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/env_embedding_explorer__REPORT.md", "summaries/enigma_sso_asv_ecology__REPORT.md", "summaries/ecotype_functional_differentiation__REPORT.md", "summaries/counter_ion_effects__REPORT.md", "summaries/conservation_vs_fitness__REPORT.md", "summaries/berdl_data_atlas__REPORT.md", "summaries/bacillota_b_subsurface_accessory__REPORT.md", "summaries/bacdive_phenotype_metal_tolerance__REPORT.md", "summaries/bacdive_metal_validation__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_strain_variation__REPORT.md", "summaries/amr_pangenome_atlas__REPORT.md", "summaries/amr_fitness_cost__REPORT.md", "summaries/amr_environmental_resistome__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md"]
description: "Annotation gaps reflect uneven sequence coverage, functional knowledge, ecological sampling, and method validity."
---

# Bacterial Annotation Gap

The bacterial annotation gap is the uneven distribution of functional and structural knowledge across bacterial proteins, genomes, and ecological contexts. It is not adequately measured by counting hypothetical proteins: annotation status depends on pangenome class, sequence representation, database currency, marker validity, ecological sampling, experimental coverage, and the resolution of the inference method. Evidence from AlphaFold MSA depth, Fitness Browser dark genes, AMR cofitness, environmental resistome profiling, metabolic-model gapfilling, deep-subsurface comparisons, ecotype differentiation, fitness-module analysis, and lanthanide-methylotrophy surveys shows that different layers of the gap require different evidence. [src: alphafold_msa_annotation, amr_cofitness_networks, amr_environmental_resistome, amr_pangenome_atlas, annotation_gap_discovery, bacillota_b_subsurface_accessory, conservation_vs_fitness, ecotype_functional_differentiation, fitness_modules, lanthanide_methylotrophy_atlas, truly_dark_genes]

The [[summaries/truly_dark_genes__REPORT]] provides the clearest decomposition of annotation lag from genuine novelty. Among 57,011 Fitness Browser dark genes, 39,532 had pangenome links and could be reannotated with Bakta v1.12.0. Bakta reclassified 33,105 genes (83.7%) as annotation-lag genes, while 6,427 (16.3%) remained hypothetical in both pipelines and were designated truly dark. A further 17,479 dark genes lacked pangenome links and could not be assessed. [src: truly_dark_genes]

The truly dark genes were shorter, less conserved, more taxonomically restricted, and lower in GC content than annotation-lag genes: median length was 121 versus 194 amino acids, core-genome fraction was 43.1% versus 72.7%, essential fraction was 18.0% versus 13.4%, mean GC content was 0.542 versus 0.584, ortholog presence was 29.3% versus 63.7%, and median ortholog breadth was 1 versus 4 organisms. These effects support the interpretation that at least part of the assessed set represents genuine biological novelty rather than merely outdated annotation, although short genes are also intrinsically harder to annotate and measure by transposon insertion. [src: truly_dark_genes]

Truly dark genes also expose a distinction between sequence recognition and functional understanding. Although 79.4% had UniRef50 links and 84.7% had database cross-references, only 4.0% had Pfam hits and 4.6% had KEGG KOs. Only 246 genes (3.8%) had no annotation clues at all; 96.2% had some combination of sequence identifiers, eggNOG evidence, orthologs, module membership, or fitness phenotypes. [src: truly_dark_genes]

This distinction links [[concepts/resource-darkness]], [[concepts/structural-novelty]], [[concepts/pangenome-integration]], [[concepts/evidence-triangulation]], and [[concepts/experimental-functional-prioritization]]. The strongest practical conclusion is that annotation gaps should be represented as evidence profiles rather than binary known-versus-unknown labels. [src: truly_dark_genes]

The conservation-versus-fitness study provides direct evidence that essentiality is associated with, but does not determine, pangenome conservation. Across 33 organisms, essential genes were modestly enriched in core clusters, while essential auxiliary and unmapped genes remained disproportionately hypothetical. Essential-core genes numbered 22,751 and were 87% functionally annotated; essential-auxiliary genes numbered 3,683 and were 38.2% hypothetical; essential-unmapped genes numbered 1,259 and were 44.7% hypothetical. [src: conservation_vs_fitness]

The ecotype functional-differentiation study adds a complementary result: even among auxiliary gene-content subpopulations within species, functional categories are not random. Across 12 bacterial species, 170 of 257 species-by-COG tests were significant after correction, and adaptive categories had mean effect sizes 2.13 times those of housekeeping categories. However, substantial differentiation in housekeeping categories and moderate cluster separation mean that enrichment does not by itself establish ecological adaptation. [src: ecotype_functional_differentiation]

The metabolic annotation study shows that some gaps can be resolved by triangulating model predictions with fitness, pangenome, alternative-annotation, and sequence-homology evidence, but more than half of evaluated reaction-organism pairs remained unresolved. The deep-subsurface study adds a related warning: incorrect marker identities can create biologically misleading interpretations, as occurred in an initial iron-reduction analysis. [src: annotation_gap_discovery, bacillota_b_subsurface_accessory]

The fitness-module study adds a process-level dimension. [[entities/independent-component-analysis]] applied to RB-TnSeq fitness profiles recovered biologically coherent groups of co-regulated genes, but these groups were poor predictors of exact gene-level functions. Module-level evidence can reduce uncertainty about biological process context without closing the molecular-function annotation gap. [src: fitness_modules]

The lanthanide methylotrophy atlas demonstrates the same distinction at pangenome scale. Across 293,059 GTDB-r214 genomes, xoxF was annotated in 3,690 genomes whereas mxaF occurred in 195, producing an xoxF:mxaF ratio of 18.92:1. Marker presence did not establish pathway activity, pathway intactness, or substrate use, and Bakta and eggNOG calls disagreed substantially for some markers. [src: lanthanide_methylotrophy_atlas]

## Evidence from AlphaFold MSA depth

In the analysed BER pangenome, 132,531,501 gene clusters were available, but only 38,051,842 (28.7%) successfully bridged to AlphaFold MSA-depth records through a real UniProt accession. The bridged subset is biased toward better-characterised organisms, so the unrepresented 70.7% may contain an even larger annotation gap. [src: alphafold_msa_annotation]

MSA depth provides a measurable axis for this gap. Core clusters had a median MSA depth of 15,308, compared with 5,527 for auxiliary non-singletons and 5,299 for auxiliary-plus-singleton clusters. At the 10th percentile, core depth was 334, whereas the two accessory categories had depths of 32 and 25. [src: alphafold_msa_annotation]

Across 38,051,842 gene-cluster–UniProt pairs, MSA depth correlated with domain-hit count at Spearman rho = 0.7563. Mean domain hits increased from 0.59 for proteins with MSA depth below 10 to 10.83 for proteins with depth at least 10,000; mean distinct InterPro families increased from 0.059 to 4.601. This supports [[concepts/msa-depth]] as a proxy for representation in existing functional knowledge, although the correlation does not establish that MSA depth causes better annotation. [src: alphafold_msa_annotation]

The relationship held within core and accessory pangenome classes, and core genes had slightly higher domain richness at equivalent MSA depths. However, MSA depth was measured for representative sequences, so within-cluster sequence diversity was not assessed. [src: alphafold_msa_annotation]

The broader low-depth core subset makes the central point that conservation does not guarantee annotation. There were 415,603 core clusters with MSA depth below 10; 286,439 (68.9%) were hypothetical, only 137 (0.033%) had EC annotations, and 346 (0.083%) were mapped to KEGG. These proteins occurred across 14,768 species clades and had mean and median MSA depths of 4.57 and 4.0. They are candidates for structural and functional investigation, but conservation alone does not demonstrate essentiality or biochemical importance. [src: alphafold_msa_annotation]

The truly dark-gene analysis identifies a related but not identical population. Truly dark genes were 4.2 times less likely to have cross-organism orthologs (OR = 0.236), and their orthologs had a median breadth of 1 rather than 4 organisms. Their mean absolute GC deviation was 0.047 versus 0.038 for annotation-lag genes (d = 0.247, p = 1.3e-43), 9.2% had strong GC deviation compared with 4.0% of annotation-lag genes, and 12.0% were within two genes of a mobile element. These findings support a [[concepts/horizontal-gene-transfer]] hypothesis for some truly dark genes, but GC deviation is an imperfect HGT proxy. [src: truly_dark_genes]

The conservation-versus-fitness analysis identifies complementary conserved but under-described genes. Essentiality was associated with core membership, but the median odds ratio was only 1.56, and essential auxiliary and unmapped genes had higher hypothetical fractions than essential-core genes. The appropriate interpretation is that conservation, essentiality, and annotation status are correlated but non-interchangeable axes. [src: conservation_vs_fitness]

The ecotype study adds a second route by which poorly annotated genes can shape interpretation. Approximately 38% of gene clusters had COG annotations, leaving 62% outside the tested COG vocabulary. Because unannotated genes may include ecotype-specific adaptive functions, observed enrichment toward annotated categories may underestimate functional differentiation. [src: ecotype_functional_differentiation]

The fitness-module results provide a way to investigate poorly annotated proteins through phenotype rather than sequence similarity. Across 32 organisms, Module-ICA produced 1,116 stable modules, and 94.2% had significantly elevated within-module cofitness. This identifies genes that respond similarly across experimental conditions even when their individual molecular functions remain unknown. [src: fitness_modules]

## Annotation quality as a second axis of the gap

The AMR cofitness analysis demonstrates that the annotation resource can change the apparent biological result. On the same cofitness data, legacy SEED/KEGG annotations produced 0 significant enrichment results in 280 tests, whereas InterProScan GO annotations produced 35 significant results among 3,193 tests. InterProScan GO coverage was reported as 68%, compared with 40–80% per organism and more variable coverage for older annotations. [src: amr_cofitness_networks]

The improved annotations revealed enrichment for flagellar motility, flagellum assembly, bacterial-type flagella, flagellum-dependent swarming, histidine biosynthesis, and tryptophan biosynthesis. These terms were enriched in three to five organisms, with mean odds ratios from 4.7 to 5.3. The result does not show that the functions are AMR-specific or directly co-regulated: [[concepts/shared-dispensability]] remains an alternative explanation, and fitness-matched permutation is needed. [src: amr_cofitness_networks]

The fitness-module study reaches a related conclusion. Adding PFam domains and lowering the enrichment overlap threshold from 3 to 2 increased module annotation from 8% to 80%, covering 890 rather than 92 modules and unlocking 7.6-fold more function predictions. PFam provided the broadest coverage, while KEGG KOs were too gene-specific for reliable module-level enrichment. Broader annotation is not necessarily more accurate: domain-level evidence may overcount associations, and a pathway or domain label may indicate process participation rather than a specific catalytic activity. [src: fitness_modules]

Benchmarking makes this resolution limit explicit. Ortholog transfer achieved 95.8% strict precision, 91.2% coverage, and F1 = 0.934 in held-out KO prediction, whereas Module-ICA had below-1% strict KO precision and 23.3% coverage. Cofitness voting also had below-1% strict KO precision despite 73.0% coverage. Module evidence is therefore best used for process-level hypotheses, not exact KO assignment. [src: fitness_modules]

The annotation-gap discovery study provides direct evidence that combining resources can resolve otherwise ambiguous metabolic functions. Among 201 gapfilled enzymatic reaction-organism pairs from 14 Fitness Browser organisms and 18 carbon sources, 96 (47.8%) received candidate genes: 44 high-confidence pairs (21.9%), 19 medium-confidence pairs (9.5%), and 33 low-confidence pairs (16.4%). The remaining 105 pairs (52.2%) were unresolved. [src: annotation_gap_discovery]

The integrated pipeline combined EC matching, Bakta alternative annotations, pangenome conservation, fitness profiles, GapMind pathway evidence, and BLAST homology. EC matching alone resolved 51/201 pairs (25.4%), Bakta contributed 22 newly resolved pairs (10.9%), and BLAST alone resolved 70/201 pairs (34.8%). The full pipeline resolved 96 pairs, 13 percentage points above BLAST alone. Excluding NB03 reduced resolution to 86 pairs (42.8%), excluding NB04 to 80 (39.8%), and excluding BLAST to 73 (36.3%). These results support [[concepts/evidence-triangulation]] rather than replacement of one method by another. [src: annotation_gap_discovery]

The same study found that 50 of 201 gapfilled reactions (24.9%) had no EC number. Only 8/50 dark reactions (16%) were resolved, compared with 88/151 reactions with known EC numbers (58.3%). Stoichiometrically defined dark reactions are therefore less accessible to sequence-homology and functional cross-referencing approaches. [src: annotation_gap_discovery]

The deep-subsurface Bacillota_B report shows why biological validation of markers is essential. An earlier analysis used K07811, K17324, and K17323 as iron-reduction markers, but these corresponded to TMAO reductase, glycerol ABC ATP-binding, and glycerol permease functions rather than canonical multi-heme iron-reduction markers. Corrected analysis used PFAM PF02085, PFAM PF22678, and a CXXCH heme-binding motif count of at least 4. [src: bacillota_b_subsurface_accessory]

The correction changed the apparent result from shallow clay at 50.0% versus deep clay at 11.1% to corrected rates of 40.0% versus 55.6%. Pairwise Fisher tests were not significant after correction, with all reported p values at least 0.46. The sulfur-reduction signal was unaffected, with 5/9 deep-clay genomes positive versus a reported Mitzscherling rock-attached null rate of 0.2% and binomial p = 4 x 10^-12. [src: bacillota_b_subsurface_accessory]

The lanthanide atlas gives a second marker-calibration example. Bakta `product='Lanmodulin'` identified 62 genomes, all in three canonical alpha-Proteobacterial methylotroph families, whereas eggNOG `Preferred_name='lanM'` produced 505 likely false positives concentrated in unrelated gut Bacillota. For xoxF and mxaF, eggNOG K00114 and K14028 were retained as primary sources; Bakta was used as a union source where appropriate. Annotation source must therefore be calibrated per marker. [src: lanthanide_methylotrophy_atlas]

The lanthanide analysis also shows that missing annotations can be asymmetric across complementary pathways. Of 2,185 xoxF-bearing genomes lacking eggNOG PQQ annotations, 1,288 (59%) had at least one Bakta PQQ product. However, 897 genomes (24.3% of the complete xoxF set) had no PQQ evidence from either source, leaving assembly incompleteness, pseudogenization, and community-acquired PQQ as unresolved hypotheses. [src: lanthanide_methylotrophy_atlas]

## Ecological sampling as an annotation and interpretation gap

The environmental resistome analysis shows that database composition shapes apparent functional differences between bacterial groups. Across 14,723 species and 280,337 genomes, clinical-source species had a median of 5 AMR gene clusters, compared with 2 in soil, aquatic, and host-associated species; the environment effect was significant (Kruskal–Wallis H = 781.9, p = 9.4 x 10^-167, eta-squared = 0.056). [src: amr_environmental_resistome]

The pan-bacterial AMR atlas similarly found 10.6 AMR clusters per Human/Clinical species, compared with 4.6 for Soil/Terrestrial, 3.9 for Aquatic, and 3.0 for Animal species. This comparison included 7,838 species with non-unknown environment classifications, or 53.2% of the 14,723 AMR-carrying species. [src: amr_pangenome_atlas]

Clinical and human-gut species also had larger accessory AMR fractions than natural-environment species. Clinical species averaged 67.6% accessory AMR, compared with 42.9% in soil and 45.6% in aquatic species; human-gut species averaged 80.3% accessory AMR. These are dataset-dependent estimates rather than universal environmental constants. [src: amr_environmental_resistome, amr_pangenome_atlas]

Resistance mechanism composition was environment-dependent. Metal resistance represented 44.0% of soil AMR and 45.0% of aquatic AMR but 6.1% of human-gut AMR, whereas target modification represented 43.6% of human-gut AMR and 27.5% of clinical AMR but 6.2% of aquatic AMR. These categories require caution because the AMR atlas included approximately 15,000 mercury-resistance hits and another approximately 6,000 arsenic-resistance hits alongside classical antibiotic-resistance determinants. [src: amr_environmental_resistome, amr_pangenome_atlas]

Known clinical resistance genes may be easier to recognize than novel environmental resistance determinants, and environment-specific false-negative rates were not directly measured. This remains a hypothesis rather than an established correction. [src: amr_environmental_resistome, amr_pangenome_atlas]

The environmental signal was not explained entirely by taxonomy: 5 of 6 tested phyla showed significant within-phylum environment effects, while 20 of 141 testable families showed significant effects after FDR correction. Environment and phylogeny remain deeply entangled, and many families do not span enough environments for reliable testing. [src: amr_environmental_resistome]

Continuous environmental embeddings provide an additional but limited view. Among 2,659 species with AMR data and AlphaEarth embeddings, 52 of 64 dimensions correlated with AMR diversity after FDR correction, and a Mantel test relating environmental distance to AMR-profile distance gave r = 0.098 and p = 0.001. The embeddings covered only 28% of genomes and their dimensions had limited interpretability. [src: amr_environmental_resistome]

The lanthanide atlas provides a contrasting environmental example. Among 293,059 genomes, soil/sediment had the strongest broad-class xoxF enrichment: 6.84% of 13,779 genomes carried xoxF, with OR = 1.92 versus generic environmental samples and p_BH = 6.1 x 10^-39. Marine samples were also enriched (4.76%; OR = 1.31; p_BH = 7.8 x 10^-7). REE-impacted samples showed a descriptive elevation of 10.81% among only 37 genomes (OR = 3.51), but p_BH = 0.082 did not meet the FDR threshold. Host-associated genomes were strongly depleted (0.22%; OR = 0.058; p_BH = 0). [src: lanthanide_methylotrophy_atlas]

The REE-acid-mine-drainage case demonstrates why environmental presence should not be equated with activity. Only 4/37 REE-AMD MAGs carried xoxF, and 0/37 carried Bakta-validated lanmodulin or xoxJ. The community was instead dominated by acidophilic, metal-tolerant, DNA-repair, acid-resistance, and oxidative-stress functions. The sample was too small and geographically narrow to determine whether REE exposure selects for lanthanide-dependent methylotrophy. [src: lanthanide_methylotrophy_atlas]

The subsurface Bacillota_B comparison illustrates a parallel sampling problem. Its deep-clay anchor contained only 10 genomes, largely from borehole and porewater contexts, compared with 62 soil-baseline genomes. Deep-clay Bacillota_B were larger rather than streamlined: mean genome size was 4,110,038 bp versus 3,046,124 bp, and mean eggNOG OG counts were 2,630 versus 2,106. [src: bacillota_b_subsurface_accessory]

The metabolic annotation study found resolution rates from 20% in *Bacteroides thetaiotaomicron* to 71.4% in *Klebsiella michiganensis* across the six organisms reported in its organism-level breakdown. Better-annotated reference genomes and stronger Fitness Browser coverage were associated with higher resolution, while the divergent Bacteroidetes organism had the lowest rate. This suggests, but does not establish, that phylogenetic distance and uneven experimental coverage affect recoverability of annotation gaps. [src: annotation_gap_discovery]

## Two layers of the gap

### Pangenome-class layer

The overall hypothetical-protein rate was 3.8% among core clusters, compared with 11.6% among auxiliary non-singletons and 13.8% among auxiliary-plus-singleton clusters. Chi-square tests gave chi-squared > 500,000 with p approximately 0, and the odds ratios for core versus auxiliary-plus-singleton and core versus auxiliary non-singleton clusters were 0.25 and 0.31. [src: alphafold_msa_annotation]

This pattern is consistent with a [[concepts/core-accessory-resistance]] distinction in which broadly distributed core genes have more sequence representation and annotation, whereas accessory genes may be taxonomically restricted, rapidly evolving, or horizontally transferred. These evolutionary explanations were not directly tested in the MSA-depth report. [src: alphafold_msa_annotation]

The truly dark-gene results strengthen the accessory-novelty interpretation. Truly dark genes had a core fraction of 43.1% versus 72.7% among annotation-lag genes, only 29.3% had orthologs, and the median ortholog breadth was 1 versus 4. In ICA organisms, 41% of neighboring genes were also hypothetical, forming genomic dark islands; 12.0% of truly dark genes were within two genes of a mobile element, and 25.9% showed operon-like cofitness with adjacent genes. [src: truly_dark_genes]

The AMR atlas strengthens the connection between pangenome class and resistance interpretation. Across 14,723 species, only 30.3% of AMR genes were core versus 46.8% for the pangenome baseline, and the auxiliary genome was 2.2x enriched for AMR. In a paired test of 4,252 species, 63.7% showed AMR less core than their species baseline. [src: amr_pangenome_atlas]

The conservation-versus-fitness analysis shows that essentiality shifts, but does not erase, this distinction. Essential genes were 86.1% core versus 81.2% for non-essential genes, with a median odds ratio of 1.56. Essential auxiliary genes were 38.2% hypothetical and essential-unmapped genes were 44.7% hypothetical. [src: conservation_vs_fitness]

The ecotype study shows that accessory differentiation is functionally structured within species. Frequently differentiated categories included amino acid metabolism E (11/12 species), defense V (11/12), carbohydrate metabolism G (10/12), cell wall M (9/12), inorganic ion transport P (9/12), and secondary metabolism Q (9/12). Housekeeping categories also differentiated frequently, so accessory functional enrichment does not by itself prove ecological adaptation. [src: ecotype_functional_differentiation]

Fitness modules add a process-level form of conservation. Cross-organism alignment identified 156 module families spanning at least two organisms, including 28 spanning 5+, 7 spanning 10+, and one spanning 21 organisms. Of the 156 families, 145 had consensus functional labels. These families suggest conserved co-regulation programs, but conservation of a module does not imply that every member has the same molecular function. [src: fitness_modules]

### MSA-depth layer

The class-level pattern conceals a severe annotation gap within a subset of core genes. The 415,603 core clusters with MSA depth below 10 were mostly hypothetical despite their pangenome conservation. The available reports do not establish whether their low MSA depth reflects unprecedented folds, extreme sequence divergence, database sampling bias, or limitations of representative-sequence lookup. This uncertainty is central to [[concepts/structural-novelty]]. [src: alphafold_msa_annotation]

The truly dark set provides a complementary candidate population enriched for narrow taxonomic distribution, short sequences, lower GC content, and possible HGT signals. These genes are not simply equivalent to low-depth core proteins: the former are defined by agreement between two hypothetical annotations, while the latter are defined by low structural-database representation. [src: truly_dark_genes, alphafold_msa_annotation]

The fitness-module data provide a phenotype-based prioritisation route for both populations. Module membership can be assessed from correlated fitness profiles even when sequence-based transfer is unavailable, but the benchmark shows that membership should be interpreted as process context rather than as evidence for a specific KEGG KO. [src: fitness_modules]

The environmental resistome provides a parallel warning about apparent novelty: 18.7% of AMR clusters, or 15,550 clusters, could not be classified into four resistance mechanisms from gene names or product annotations. The atlas reported 22.2% of 83,008 AMR hits as Other/Unclassified under a different dataset and classification procedure. These values should not be averaged or treated as a single estimate. [src: amr_environmental_resistome, amr_pangenome_atlas]

The subsurface report shows that generic residual categories can hide interpretable biology. Of 547 enriched OGs, 462 were assigned to an other/unannotated bucket by the keyword scanner, while manual review recovered molybdopterin-cofactor metabolism, DsrE/DsrF/DsrH-like sulfite handling, anaerobic ferredoxin oxidoreductase activity, and transporter signals. [src: bacillota_b_subsurface_accessory]

## Tension: core conservation versus annotation status

Core genes are better annotated overall than accessory genes, yet 68.9% of the low-MSA-depth core subset is hypothetical. Essential genes are enriched in core clusters, but the enrichment is modest, and essential auxiliary and unmapped groups have higher hypothetical fractions than essential-core genes. Conservation and essentiality are therefore correlated dimensions rather than interchangeable measures of functional knowledge. [src: alphafold_msa_annotation, conservation_vs_fitness]

The ecotype results add a related tension. Adaptive COG categories had larger effects than housekeeping categories, but housekeeping functions also differentiated in most species tested. Functional differentiation is consistent with selection acting on gene-content variation, but it may also include drift, phylogenetic structure, and ongoing gene gain and loss. [src: ecotype_functional_differentiation]

The fitness-module results introduce a resolution tension. Module-ICA recovered strong biological structure—94.2% of modules showed significant cofitness enrichment, mean within-module absolute correlation was 0.34 versus 0.12 in the background, and genomic adjacency was enriched 22.7-fold—yet exact KO prediction had below-1% precision. Strong process-level evidence therefore does not entail strong gene-level annotation. [src: fitness_modules]

The lanthanide marker results show the same tension between detection and interpretation. XoxF strongly outnumbered mxaF, but xoxF presence alone does not prove methanol oxidation. Bakta detected lanmodulin in 62 genomes while eggNOG produced 505 likely false positives, demonstrating that marker counts are meaningful only after source calibration. [src: lanthanide_methylotrophy_atlas]

These results are not contradictory because they condition on different subsets and measurements. Together they indicate several separable dimensions of the annotation gap: pangenome distribution, sequence and structural representation, functional-vocabulary coverage, ecological sampling, experimental coverage, marker validity, and the distinction between process association and molecular-function identity. [src: alphafold_msa_annotation, amr_cofitness_networks, amr_environmental_resistome, conservation_vs_fitness, ecotype_functional_differentiation, fitness_modules, lanthanide_methylotrophy_atlas, truly_dark_genes]

The annotation-gap discovery results add an operational distinction: a reaction may be required by a metabolic model while its responsible gene remains unknown. Gapfilling added 219 reactions to address 38 false-negative growth cases, but only 96 of 201 enzymatic reaction-organism pairs received candidate genes. Model-level plausibility and gene-level annotation are related but non-equivalent evidence. [src: annotation_gap_discovery]

The subsurface correction illustrates how a strong ecological interpretation can be robust for one marker family and invalid for another. The deep-clay sulfur-reduction signal remained supported after review, whereas the apparent shallow-clay iron-reduction enrichment disappeared when appropriate multi-heme-cytochrome signals replaced mismatched KOs. [src: bacillota_b_subsurface_accessory]

## Scope and limitations

InterProScan annotations reached 111,035,431 clusters (83.8% of all clusters), substantially beyond the 29.3% UniProt bridge coverage used for the AlphaFold analysis. MSA-depth results therefore describe a selected, better-characterised portion of bacterial diversity. The genome collection was taxonomically imbalanced, common taxa such as Pseudomonas and *Escherichia coli* were over-represented, and the analysis used a static version-6 AlphaFold snapshot. [src: alphafold_msa_annotation]

The MSA-depth correlation was computed over the full dataset without subgroup stratification by pangenome class or organism-level annotation bias. Its magnitude should not be treated as universal for every bacterial lineage or protein family. [src: alphafold_msa_annotation]

The truly dark-gene census has a 17,479-gene pangenome-linkage gap, and Bakta may produce false negatives. Ortholog coverage included only 32 of 48 Fitness Browser organisms, while short genes are difficult both to annotate and to measure by transposon fitness. Strong phenotypes may also reflect polar effects on downstream genes. [src: truly_dark_genes]

The conservation-versus-fitness analysis used 33 organisms after coverage filtering. Essentiality is an upper-bound classification because absent transposon insertions can reflect short genes, low-complexity regions, scaffold edges, or other technical factors. It was measured under particular library-construction and growth contexts and may miss stress-specific essentiality. Four organisms were unmatched because their species had too few GTDB genomes; the principal *E. coli* clade was absent because it contained too many genomes; and some identifier mismatches reduced coverage. [src: conservation_vs_fitness]

The AMR annotation comparison is not a direct benchmark of correctness. InterProScan increased coverage and detected enrichment that SEED/KEGG missed, but results remained sensitive to GO-term granularity, organism composition, the null model, and shared experimental dispensability. The environmental resistome is vulnerable to NCBI sampling bias, with clinical isolates over-represented and soil and aquatic species undersampled. Species-level majority-vote environments collapse within-species variation, and core/accessory labels depend on genome count and a 95% prevalence threshold. [src: amr_cofitness_networks, amr_environmental_resistome]

The pan-bacterial AMR atlas classified only 7,838 of 14,723 AMR-carrying species with non-unknown environments, and its AlphaEarth analysis covered 2,684 species. Its mechanism classes were generated by keyword matching against AMRFinderPlus product descriptions rather than CARD ontology mapping; 22.2% of 83,008 AMR hits were assigned to Other/Unclassified. [src: amr_pangenome_atlas]

The Bacillota_B comparison used 10 deep-clay genomes versus 62 baseline genomes, with a borehole- and porewater-dominated anchor. Genus-level phylogenetic confounding was only partly mitigated, and keyword-based functional labels left substantial residual ambiguity. [src: bacillota_b_subsurface_accessory]

The metabolic study used automated RAST annotations and achieved 42.5% baseline FBA accuracy across 574 organism-carbon-source combinations, with 86.5% recall and 42.5% precision. ModelSEED gapfilling was non-unique and did not guarantee biological optimality. The study was also phylogenetically biased, with 12 of 14 organisms belonging to Proteobacteria. [src: annotation_gap_discovery]

The lanthanide atlas used text-mined environmental classification; AlphaEarth coordinates covered only 1,457/3,690 xoxF genomes (39.5%); the REE-AMD anchor contained only 37 MAGs from one bioproject; and marker calls were affected by source disagreement. Sequence-level screening for truncated ORFs, pseudogenes, and assembly fragmentation was out of scope. [src: lanthanide_methylotrophy_atlas]

The ecotype study sampled only 15 species from 456 eligible species, with 12 valid analyses spanning six phyla. It used KMeans rather than HDBSCAN, did not control for within-species phylogeny, and obtained a moderate mean silhouette score of 0.215. Since approximately 62% of gene clusters lacked COG annotations, detected functional differentiation may be incomplete. [src: ecotype_functional_differentiation]

The fitness-module study used a 40% component cap to avoid FastICA convergence failures, and organisms with limited experiment counts produced weaker modules. Cross-organism families were based on BBH-derived ortholog fingerprints, so family recovery depends on ortholog detection and organism inclusion. [src: fitness_modules]

## Implications

The annotation gap is not adequately described by counting hypothetical proteins. Combining pangenome class with [[concepts/msa-depth]] distinguishes broadly distributed proteins with substantial sequence support from conserved proteins isolated from known sequence space. Comparing annotation pipelines distinguishes biological novelty from information that is present in the data but inaccessible to lower-coverage or inconsistent systems. Ecological metadata is necessary to determine whether apparent functional absences reflect biology, environment-specific gene content, or uneven database representation. [src: alphafold_msa_annotation, amr_cofitness_networks, amr_environmental_resistome, truly_dark_genes]

The truly dark-gene report provides an operational prioritisation framework. Its multi-criteria ranking identified 100 candidates across 19 organisms, including 34 essential genes, 53 operon-associated genes, and 30 genes in ICA fitness modules. Top candidates combined strong phenotypes with genomic or partial-annotation clues, such as PV4/5210953 with a motility phenotype and TatC operon association, ANA3/7026383 with a nitrogen-source phenotype and ABC-transporter operon, and Methanococcus_S2/MMP_RS06570 with DUF190, COG-T, and fluoride-efflux operon evidence. [src: truly_dark_genes]

Essentiality, pangenome conservation, MSA depth, annotation coverage, phenotype, genomic context, and structural prediction should therefore be treated as complementary prioritisation axes. A strong candidate is not necessarily a gene with the largest phenotype or the lowest annotation score; it is a gene supported by independent evidence that narrows a testable hypothesis. [src: conservation_vs_fitness, truly_dark_genes]

The ecotype analysis adds functional structure within the accessory genome, but its large S-category signal makes uncharacterised proteins a priority for follow-up rather than a basis for definitive ecological claims. [src: ecotype_functional_differentiation]

Fitness modules are most defensible as statements that a protein may participate in a biological process, especially when module membership is supported by cross-organism conservation or multiple annotation sources. They should not be presented as exact molecular-function assignments because ortholog transfer was far more precise in held-out KO prediction. [src: fitness_modules]

The metabolic results show that [[concepts/metabolic-model-gapfilling]] can generate useful hypotheses, but gapfilling is not equivalent to gene annotation. High-confidence assignments are stronger follow-up priorities than low-confidence assignments, but all require validation. [src: annotation_gap_discovery]

The AMR atlas shows that core/accessory status is biologically informative but insufficient. AMR was accessory-enriched overall, while intrinsic beta-lactamases were 54.9% core and regulatory genes were 6.5% core. Clinical AMR was both more abundant and less core than soil or plant AMR, supporting an intrinsic-versus-acquired distinction while leaving annotation and sampling bias unresolved. [src: amr_pangenome_atlas]

The corrected clay analysis demonstrates the value of biologically specific markers. Combining PFAM evidence with CXXCH motif scanning improved marker specificity where KEGG lacked a canonical KO, but the approach does not alone establish extracellular electron transfer, iron reduction in situ, or ecological causality. [src: bacillota_b_subsurface_accessory]

The lanthanide atlas adds a practical rule for pangenome annotation: use marker-specific source calibration, report union-of-source evidence separately from primary calls, and distinguish absence of an annotation from absence of a pathway. Its xoxF/mxaF and lanmodulin results show that large-scale prevalence can be robust while functional claims remain conditional on pathway completeness, sequence integrity, and ecological validation. [src: lanthanide_methylotrophy_atlas]

## Open Directions

- Recalculate the MSA-depth/domain-richness association separately for core, auxiliary non-singleton, and singleton groups, and compare representative-sequence results with all members of selected clusters. [src: alphafold_msa_annotation]
- Compare AlphaFold MSA depth with ESMFold confidence and Foldseek matches to distinguish sequence-space novelty from structural predictability without homologous sequences. [src: alphafold_msa_annotation, truly_dark_genes]
- Map the 415,603 low-depth core clusters and the 6,427 truly dark genes onto GTDB phylogeny to identify lineages enriched for conserved or lineage-restricted unknown proteins. [src: alphafold_msa_annotation, truly_dark_genes]
- Join low-depth core and truly dark proteins with Fitness Browser measurements and [[concepts/condition-dependent-essentiality]] analyses. [src: alphafold_msa_annotation, conservation_vs_fitness, truly_dark_genes]
- Extend pangenome linkage to the 17,479 unlinked dark genes, then rerun Bakta, clue-matrix construction, and candidate prioritisation. [src: truly_dark_genes]
- Compare essential-core, essential-auxiliary, and essential-unmapped genes across MSA depth, domain counts, independent databases, and experimentally validated essentiality. [src: conservation_vs_fitness]
- Repeat AMR cofitness enrichment with fitness-matched non-AMR genes and benchmark annotation pipelines on identical gene sets. [src: amr_cofitness_networks]
- Map AMRFinderPlus and Bakta cross-references to CARD ontology terms and compare keyword-derived with ontology-derived mechanism assignments. [src: amr_pangenome_atlas]
- Test environment-specific AMR false-negative rates using validated resistance genes and balanced environmental benchmarks. [src: amr_environmental_resistome, amr_pangenome_atlas]
- Experimentally test the 44 high-confidence metabolic assignments and apply enzyme-prediction tools to the 50 EC-less gapfilled reactions. [src: annotation_gap_discovery]
- Reclassify the 462 residual deep-clay enriched OGs with domain-aware and structure-aware methods, then expand the deep-clay cohort with phylogenetic controls. [src: bacillota_b_subsurface_accessory]
- Scale ecotype functional-differentiation analysis to all 456 eligible species, compare clustering methods, and control for core-genome phylogeny. [src: ecotype_functional_differentiation]
- Characterise ecotype-associated S-category proteins and truly dark genes with domain analysis, protein-structure prediction, genomic context, and targeted experiments. [src: ecotype_functional_differentiation, truly_dark_genes]
- Compare Module-ICA process predictions with ortholog, domain, and structure-based annotations, and test whether module membership predicts condition-specific essentiality after controlling for genomic adjacency. [src: fitness_modules]
- Use CheckM2 and ORF-integrity analysis to resolve the 897 xoxF genomes with no PQQ evidence, and test whether xoxF-bearing Acidobacteriota and Gemmatimonadota contain intact methylotrophy cassettes. [src: lanthanide_methylotrophy_atlas]
- Combine InterProScan domains, COGs, pangenome class, metabolic gapfilling, fitness, ecological metadata, and structural predictions to prioritise proteins supported by multiple independent evidence types. [src: alphafold_msa_annotation, annotation_gap_discovery, conservation_vs_fitness, ecotype_functional_differentiation, fitness_modules, truly_dark_genes]

## Related Documents

- [[summaries/alphafold_msa_annotation__REPORT]]
- [[summaries/amr_cofitness_networks__REPORT]]
- [[summaries/amr_environmental_resistome__REPORT]]
- [[summaries/amr_pangenome_atlas__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/bacillota_b_subsurface_accessory__REPORT]]
- [[summaries/conservation_vs_fitness__REPORT]]
- [[summaries/ecotype_functional_differentiation__REPORT]]
- [[summaries/fitness_modules__REPORT]]
- [[summaries/lanthanide_methylotrophy_atlas__REPORT]]
- [[summaries/truly_dark_genes__REPORT]]
- [[summaries/amr_fitness_cost__REPORT]]
- [[summaries/amr_strain_variation__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]
- [[summaries/bacdive_metal_validation__REPORT]]
- [[summaries/bacdive_phenotype_metal_tolerance__REPORT]]
- [[summaries/berdl_data_atlas__REPORT]]
- [[summaries/counter_ion_effects__REPORT]]
- [[summaries/env_embedding_explorer__REPORT]]
- [[summaries/gene_function_ecological_agora__REPORT]]
- [[summaries/metabolic_capability_dependency__REPORT]]
- [[summaries/metal_fitness_atlas__REPORT]]
- [[summaries/microbeatlas_metal_ecology__REPORT]]
- [[summaries/pathway_capability_dependency__REPORT]]
- [[summaries/pgp_pangenome_ecology__REPORT]]
- [[summaries/phage_defense_arsenal__REPORT]]
- [[summaries/pitfalls]]
- [[summaries/prophage_ecology__REPORT]]
- [[summaries/respiratory_chain_wiring__REPORT]]