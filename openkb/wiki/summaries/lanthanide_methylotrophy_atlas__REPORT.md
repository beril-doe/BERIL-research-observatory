---
type: "Summary"
description: "A 293K-genome atlas finds strong xoxF dominance and soil-linked lanthanide methylotrophy."
doc_type: short
full_text: "sources/lanthanide_methylotrophy_atlas__REPORT.md"
---

# Lanthanide Methylotrophy Atlas — Summary

## Scope

This report presents a pangenome-scale survey of lanthanide-dependent methanol oxidation across **293,059 GTDB-r214 genomes** in the BER Data Lakehouse. It compares the REE-dependent methanol dehydrogenase marker [[entities/xoxf]] with the calcium-dependent [[entities/mxaf]], evaluates environmental associations, tests [[entities/lanmodulin]] distribution, characterizes REE-acid-mine-drainage MAGs, and calibrates [[entities/eggnog]] versus [[entities/bakta]] marker calls. The report contributes to [[concepts/pangenome-integration]], [[concepts/annotation-gap]], and [[concepts/environmental-occupancy-vs-activity]] as cross-document themes. [src: lanthanide_methylotrophy_atlas]

## Key Findings

### XoxF strongly dominates mxaF

EggNOG annotations identified **3,690 xoxF genomes** and **195 mxaF genomes**, yielding an xoxF:mxaF ratio of **18.92:1** with a 95% confidence interval of **[13.07, 27.69]**. XoxF represented **0.9498** of joint MDH calls, and a one-sided binomial test against the pre-registered 10:1 dominance threshold gave **p = 7.6 × 10⁻²²**. The H1 hypothesis was supported after Benjamini-Hochberg correction across testable phyla. [src: lanthanide_methylotrophy_atlas]

Three phylogenetic-validation approaches reached the same directional conclusion: genome-level pooling gave an xoxF fraction of **0.950**, family-equal weighting gave **0.960 [0.941, 0.976]**, and a Bayesian binomial GLMM with phylum and family random effects gave **0.993 [0.992, 0.994]**, corresponding to an estimated phylogeny-corrected ratio of approximately **143:1 [122, 169]**. These analyses address [[concepts/phylogenetic-confounding]] and support [[concepts/evidence-triangulation]]. [src: lanthanide_methylotrophy_atlas]

### High xoxF rates extend beyond canonical methylotrophs

The highest per-genome xoxF rates occurred in **Acidobacteriota** (**285/1,006; 28.3%**) and **Gemmatimonadota** (**98/386; 25.4%**), alongside **Methylomirabilota** (**23/80; 28.7%**). Canonical methylotroph families also showed high rates, including **Beijerinckiaceae** (**171/508; 33.7%**) and **Hyphomicrobiaceae** (**33/56; 58.9%**). Several phyla, including Bacteroidota, Cyanobacteriota, Chloroflexota, Planctomycetota, Campylobacterota, Actinomycetota, Halobacteriota, and Thermoproteota, had xoxF calls but no mxaF calls. These results expand the candidate set for experimental study beyond familiar methylotroph lineages, although gene annotation alone does not establish active methylotrophy. This distinction reflects [[concepts/capability-versus-kinetics]] and [[concepts/environmental-occupancy-vs-activity]]. [src: lanthanide_methylotrophy_atlas]

### Lanmodulin is phylogenetically restricted

Bakta-validated lanmodulin occurred in **62 genomes spanning 10 species**, with **62/62 (100%)** located in Beijerinckiaceae, Acetobacteraceae, or Hyphomicrobiaceae. This supported H3a (**p = 9.8 × 10⁻⁷**). XoxF co-occurred in **49/62 genomes (79.0%)**, just below the pre-registered 80% threshold; H3b was therefore not formally supported (**p = 0.65**). The 13 lanmodulin-positive genomes without xoxF may reflect annotation incompleteness or lanthanide-handling functions decoupled from methanol oxidation. This pattern illustrates [[concepts/organism-specificity]] and [[concepts/pathway-completeness]]. [src: lanthanide_methylotrophy_atlas]

[[entities/methylobacterium-extorquens]] was the largest lanmodulin contributor, with **22 genomes and one copy per genome**. Other carriers included an uncharacterized Acetobacteraceae genus, *M. thiocyanatum*, *M. rhodesianum*, *M. aminovorans*, *Hyphomicrobium_B*, and *Methylocella*. [src: lanthanide_methylotrophy_atlas]

### Soil and sediment show the clearest environmental enrichment

The strongest broad environmental association was for **soil/sediment**, where xoxF occurred in **6.84% of 13,779 genomes** with an odds ratio of **1.92** versus generic environmental samples (**p_BH = 6.1 × 10⁻³⁹**). Marine samples were also enriched (**4.76%; OR = 1.31; p_BH = 7.8 × 10⁻⁷**). REE-impacted samples showed a descriptive elevation (**10.81% of 37; OR = 3.51**) but did not pass FDR correction (**p_BH = 0.082**). Host-associated genomes were strongly depleted (**0.22%; OR = 0.058; p_BH = 0**). Within Acidobacteriota, the soil/sediment association remained detectable (**OR = 2.16; p_BH = 2.2 × 10⁻⁵**), reducing—but not eliminating—the possibility of phylogenetic confounding. These results connect [[concepts/environmental-occupancy-vs-activity]] with [[concepts/phylogenetic-confounding]] and [[concepts/coverage-limited-inference]]. [src: lanthanide_methylotrophy_atlas]

### REE-acid-mine-drainage MAGs are primarily stress-adapted

The **37 REE-AMD MAGs** came from a single rare-earth-element acid-mine-drainage river-water collection. They were dominated by acidophilic and metal-tolerant lineages such as *Acidocella*, *Acidiphilium*, *Thiomonas*, *Metallibacterium*, Burkholderiaceae_A/_B lineages, and other diverse taxa, including the previously uncharacterized **f__REEB76 / g__REEB76** clade ([[entities/reeb76]]). Only **4/37** MAGs carried xoxF, and **0/37** carried Bakta-validated lanmodulin or xoxJ. DNA repair, acid-resistance, heavy-metal regulation, and oxidative-stress products were much more prevalent, indicating that this community is characterized primarily by acid-mine-drainage stress adaptation rather than methylotrophy. The contrast is relevant to [[concepts/environmental-metal-tolerance]] and [[concepts/shared-stress-biology]]. [src: lanthanide_methylotrophy_atlas]

### Apparent PQQ gaps are often annotation gaps

Among xoxF-bearing genomes lacking eggNOG PQQ annotations, **1,288 of 2,185 (59%)** had at least one Bakta PQQ product. Across the xoxF set, **33** genomes had complete eggNOG pqqA-E annotations, **1,472** had partial eggNOG PQQ annotations, **899** had strong Bakta-only evidence, **389** had partial Bakta-only evidence, and **897 (24.3%)** had no PQQ evidence from either source. The latter group remains consistent with assembly fragmentation, pseudogenization, or community-acquired PQQ and requires sequence-level investigation. This supports [[concepts/annotation-gap]], [[concepts/pathway-completeness]], and the use of [[entities/pqq]] and [[entities/pqq-biosynthesis]] as calibrated pathway markers. [src: lanthanide_methylotrophy_atlas]

### Marker sources require calibration

EggNOG and Bakta showed marker-specific disagreement. Bakta was treated as the trustworthy source for lanmodulin and xoxJ, while eggNOG K00114 and K14028 were primary sources for xoxF and mxaF, respectively. EggNOG's `Preferred_name='lanM'` produced **505 likely false positives**, concentrated in unrelated gut Bacillota, whereas Bakta identified **62** lanmodulin-positive genomes restricted to canonical α-Proteobacterial methylotroph families. EggNOG KO `K02030` was also considered non-specific for xoxJ, and Bakta was found to over-call PQQ products when used alone. These results motivate [[concepts/method-concordance]] and [[concepts/evidence-triangulation]]. [src: lanthanide_methylotrophy_atlas]

## Interpretation

The atlas provides strong, phylogenetically validated evidence that xoxF is far more prevalent than mxaF in the BERDL pangenome. However, xoxF presence should be interpreted as a candidate for lanthanide-dependent methanol oxidation rather than proof of pathway activity, because the analysis is based on gene-call annotations and does not assess ORF integrity, expression, enzyme function, or substrate use. This is a case of [[concepts/capability-versus-kinetics]] and [[concepts/environmental-occupancy-vs-activity]]. [src: lanthanide_methylotrophy_atlas]

The distribution across Acidobacteriota, Gemmatimonadota, Methylomirabilota, and other less-studied groups suggests a broader biological range for lanthanide-associated MDH than the classical methylotroph literature captures. The environmental results point most strongly toward soil and sediment as reservoirs, while the small REE-AMD sample does not yet establish that REE exposure selects for xoxF-bearing organisms. [src: lanthanide_methylotrophy_atlas]

The restricted lanmodulin distribution also indicates that lanmodulin is not a general marker of bacterial REE biology at this resolution. Its partial co-occurrence with xoxF is compatible with multiple lanthanide-handling strategies or incomplete annotations, but distinguishing these explanations requires comparative sequence and genomic-context analysis. [src: lanthanide_methylotrophy_atlas]

## Limitations

- H1 received three phylogenetic validations, but H2 relied on stratified analyses rather than a fully phylogeny-aware environmental mixed model.
- The REE-AMD comparison is based on only **37 MAGs from one bioproject** and is descriptive.
- Environmental classes were generated by text mining `ncbi_env`, so classification errors are possible.
- AlphaEarth coordinates covered **1,457/3,690 xoxF genomes (39.5%)**, limiting niche analysis.
- Gene-call presence/absence does not detect truncated genes, pseudogenes, assembly problems, or novel unannotated pathways.

## Follow-up Analyses

1. Use CheckM2 completeness and ORF-integrity analyses to resolve the **~897 xoxF genomes with no PQQ evidence**.
2. Apply [[entities/alphaearth-environmental-embeddings]] PCA or UMAP to the **39.5% coordinate-covered xoxF set**, stratified by phylum, to test for environmental clustering.
3. Recruit larger and independent REE-mining, tailings, leachate, and bioreactor metagenome collections to test the REE-impacted enrichment.
4. Characterize the **f__REEB76** clade using phylogenomics, metabolic prediction, and targeted searches for xoxF and lanmodulin.
5. Test lanthanum and cerium tolerance with [[entities/random-barcode-transposon-sequencing]] in xoxF-bearing soil organisms, building on [[entities/metal-fitness-atlas]].
6. Compare lanmodulin sequences across the **22 *M. extorquens* genomes** to assess locus conservation and diversification.
7. Report the eggNOG `lanM` false-positive pattern upstream for seed-ortholog and annotation review.

## Source Materials

Primary analyses were implemented in notebooks `01_marker_calibration.ipynb` through `08_phylogenetic_validation.ipynb`, using BERDL eggNOG, Bakta, gene, genome, GTDB taxonomy, and environmental tables, together with [[entities/bacdive]] culture and metabolite metadata. [src: lanthanide_methylotrophy_atlas]

## Related Concepts
- [[concepts/gene-neighborhood-inference]]
- [[concepts/metabolic-support-networks]]
- [[concepts/phenotype-resolution-matching]]
- [[concepts/resource-darkness]]
- [[concepts/cultivation-bias]]

## Entities
- [[entities/kegg]]
- [[entities/fitness-browser]]
- [[entities/modelseed]]
- [[entities/uniprot]]
- [[entities/diamond]]
- [[entities/interproscan]]
