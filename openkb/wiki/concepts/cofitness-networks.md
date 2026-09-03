---
type: "Concept"
sources: ["summaries/truly_dark_genes__REPORT.md", "summaries/snipe_defense_system__REPORT.md", "summaries/fw300_metabolic_consistency__REPORT.md", "summaries/fitness_modules__REPORT.md", "summaries/conservation_fitness_synthesis__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/amr_cofitness_networks__REPORT.md"]
description: "Cofitness networks reveal shared fitness programs but not necessarily direct molecular functions."
---

# Cofitness Networks and Functional Inference

## Definition

A cofitness network connects genes whose experimental fitness profiles covary across conditions, allowing shared phenotypes to suggest functional relationships or common cellular programs. [src: amr_cofitness_networks] Cofitness is not equivalent to direct transcriptional co-regulation: correlated fitness profiles establish shared fitness behavior, but do not by themselves identify the regulatory mechanism connecting genes. [src: amr_cofitness_networks]

The approach is related to [[concepts/condition-dependent-essentiality]] and can be analyzed using fitness data from [[entities/fitness-browser]] and module structure inferred with [[entities/independent-component-analysis]]. [src: amr_cofitness_networks] Cofitness is especially useful for identifying functional support relationships that may be absent from pathway annotations or metabolic models. [src: aromatic_catabolism_network]

Independent-component analysis of fitness profiles provides a complementary, larger-scale implementation of this idea. Across 32 organisms, it identified 1,116 stable modules, and 94.2% of modules showed significantly elevated within-module cofitness (Mann–Whitney U, p < 0.05). [src: fitness_modules] These modules are best interpreted as process-level co-regulation or shared biological programs rather than assignments to individual molecular functions. [src: fitness_modules]

## Evidence from AMR support networks

The AMR cofitness analysis covered 28 organisms and 801 AMR genes with fitness data. [src: amr_cofitness_networks] At a correlation threshold of |r| > 0.3, 769 AMR genes (96%) had at least one extra-operon cofitness partner, yielding 180,370 total partners and 179,375 extra-operon partners. [src: amr_cofitness_networks]

Support networks were large: their mean size was 233 genes at |r| > 0.3, 110 genes at |r| > 0.4, and 71 genes at |r| > 0.5. [src: amr_cofitness_networks] The large network sizes make threshold sensitivity and the inclusion of weak associations important considerations for functional interpretation. [src: amr_cofitness_networks]

AMR genes assigned to independent-component-analysis modules occurred in larger modules than non-AMR genes, with median sizes of 46 versus 27 genes (MWU p = 1.7×10⁻⁸). [src: amr_cofitness_networks] Of 209 AMR gene–module assignments, 208 (99%) belonged to cross-organism conserved module families, suggesting that some AMR genes participate in broad, conserved cellular programs. [src: amr_cofitness_networks]

The pan-bacterial module analysis independently supports the existence of conserved cofitness structure. It found 156 module families spanning at least two organisms, including 28 spanning 5 or more organisms, 7 spanning 10 or more organisms, and 1 spanning 21 organisms. [src: fitness_modules] Of these families, 145 had consensus functional labels, or 93% of the total. [src: fitness_modules]

## Functional enrichment and annotation quality

InterProScan GO annotations identified enrichment for flagellum-dependent motility, flagellum assembly, bacterial-type flagella, flagellum-dependent swarming, histidine biosynthesis, and tryptophan biosynthesis in AMR support networks. [src: amr_cofitness_networks] The six terms were significantly enriched in three to five organisms, with mean odds ratios from 4.7 to 5.3. [src: amr_cofitness_networks]

The result depended strongly on annotation quality. Legacy SEED annotations produced zero significant results in 280 enrichment tests, whereas InterProScan GO annotations produced 35 significant results among 3,193 tests. [src: amr_cofitness_networks] InterProScan also increased cross-organism Jaccard similarity from 0.069 to 0.207 for within-mechanism comparisons and from 0.249 to 0.375 for cross-mechanism comparisons. [src: amr_cofitness_networks] This supports [[concepts/annotation-gap]] and the use of [[entities/interproscan]] when comparing functional neighborhoods across organisms. [src: amr_cofitness_networks]

The fitness-module analysis reached a related conclusion about annotation breadth. Adding PFam domains and lowering the enrichment overlap threshold from 3 to 2 increased the module annotation rate from 8% to 80%, covering 890 rather than 92 modules and unlocking 7.6-fold more function predictions. [src: fitness_modules] PFam provided the broadest annotation coverage, whereas KEGG KOs were too gene-specific for reliable module-level enrichment. [src: fitness_modules]

The ADP1 aromatic-catabolism analysis provides a complementary example in which cofitness recovered pathway membership and assigned previously uncharacterized genes to support subsystems. [src: aromatic_catabolism_network] Among 51 quinate-specific genes, 16 of 23 genes initially categorized as Other or Unknown were assigned to a subsystem with medium or high confidence. [src: aromatic_catabolism_network] The analysis recovered pcaC, which had been miscategorized by keyword matching, and identified ACIAD3137 and ACIAD2176 as candidate Complex I accessory factors because each had r > 0.98 correlations with Complex I genes. [src: aromatic_catabolism_network] These assignments are hypotheses based on phenotypic correlation rather than direct evidence of physical association. [src: aromatic_catabolism_network]

The pan-bacterial analysis generated 6,691 function predictions for hypothetical proteins across 32 organisms. [src: fitness_modules] Of these, 2,455 (37%) were backed by conserved module families and 4,236 were module-only predictions. [src: fitness_modules] These predictions should be phrased as involvement in a biological process rather than possession of a specific KEGG function. [src: fitness_modules]

## Organism-specific network structure

Different AMR mechanisms within the same organism shared more GO support terms than the same mechanism across organisms. [src: amr_cofitness_networks] Mean Jaccard similarity was 0.375 for cross-mechanism comparisons within an organism and 0.207 for within-mechanism comparisons across organisms (MWU p = 4.3×10⁻¹³). [src: amr_cofitness_networks]

The conserved functional core included transmembrane transport, signal transduction, transcription regulation, and phosphorelay signaling. [src: amr_cofitness_networks] Flagellar motility and amino-acid biosynthesis formed a less universal second tier, while no GO term remained mechanism-specific after FDR correction. [src: amr_cofitness_networks] These findings support [[concepts/organism-specificity]]: the host organism’s regulatory and metabolic architecture appears to shape AMR support networks more strongly than resistance mechanism. [src: amr_cofitness_networks]

The ADP1 study shows that cofitness can also resolve dependencies that are genomically dispersed. [src: aromatic_catabolism_network] The 51-gene quinate support network spans the aromatic pathway, [[entities/complex-i]], iron acquisition, [[entities/pqq-biosynthesis]], and regulation, even though these subsystems occupy distinct chromosomal regions and lack cross-category operons. [src: aromatic_catabolism_network] Complex I genes had mean within-category correlation of r = 0.992, while aromatic-pathway genes had r = 0.961, and the report interpreted these tightly correlated profiles as consistent with shared subsystem-level behavior. [src: aromatic_catabolism_network]

The ICA modules showed a related genomic and phenotypic organization: module genes had a mean within-module absolute correlation of 0.34 versus 0.12 for the background, corresponding to 2.8-fold enrichment, and showed 22.7-fold genomic adjacency enrichment consistent with co-location in operons. [src: fitness_modules] The adjacency signal strengthens the interpretation that some cofitness groups represent coordinated cellular programs, but it does not imply that every network connection is an operon or direct interaction. [src: fitness_modules]

## Network size and fitness cost

Support-network size did not predict AMR gene fitness cost: Spearman rho = −0.006, p = 0.87, N = 769. [src: amr_cofitness_networks] The null association persisted within efflux, enzymatic, and metal-resistance mechanisms, with all mechanism-specific p-values > 0.4. [src: amr_cofitness_networks]

This result separates network structure from resistance cost in the analyzed data. [src: amr_cofitness_networks] A large cofitness neighborhood should therefore not be interpreted as evidence that an AMR gene imposes a larger or smaller fitness burden. [src: amr_cofitness_networks] More generally, the ADP1 results demonstrate that a large or tightly correlated network can represent a biochemical support requirement without establishing that every associated gene is physically part of the same complex. [src: aromatic_catabolism_network]

The module-ICA benchmark reinforces this separation between network/process structure and exact function. In a held-out test withholding 20% of KEGG-annotated genes, ortholog transfer achieved 95.8% strict precision, 91.2% coverage, and an F1 of 0.934, whereas Module-ICA had below-1% strict precision and 23.3% coverage. [src: fitness_modules] Cofitness voting also had below-1% strict precision despite 73.0% coverage. [src: fitness_modules] Because unique KEGG groups averaged approximately 1.2 genes and a module with 20 annotated members typically contained 20 different KOs, module and cofitness methods are poorly suited to exact KO assignment. [src: fitness_modules]

## Tensions

### Co-regulation versus shared dispensability

One interpretation is that AMR genes are genuinely connected to motility, signaling, and biosynthetic programs through shared regulation or cellular resource allocation. [src: amr_cofitness_networks] This interpretation is compatible with known links between metabolism and antibiotic resistance and with the possibility that efflux and flagellar systems compete for proton-motive force, but the cofitness analysis does not directly establish either mechanism. [src: amr_cofitness_networks]

An alternative interpretation is [[concepts/shared-dispensability]]: AMR genes are often dispensable without antibiotics, flagella are less useful in shaken liquid culture, and amino-acid biosynthesis can be redundant in supplemented media. [src: amr_cofitness_networks] Similar condition-dependent fitness responses could therefore produce cofitness without direct co-regulation. [src: amr_cofitness_networks]

The existing permutation test matched conservation class but not mean fitness level, so it cannot determine whether the enriched categories are uniquely associated with AMR genes or broadly associated with slightly positive-fitness genes. [src: amr_cofitness_networks] Pearson correlation removes each gene’s mean fitness before calculating correlation, but shared responses to environmental axes can remain even when genes are not directly co-regulated. [src: amr_cofitness_networks]

### Robust structure versus uncertain mechanism

The organism-specificity comparison is less dependent on the biological interpretation of individual enriched categories because it compares the relative similarity of networks within and across organisms. [src: amr_cofitness_networks] Nevertheless, cofitness remains an indirect phenotype-based measure, and the analysis treated missing fitness values as zero in z-score space rather than using exact pairwise-complete correlations. [src: amr_cofitness_networks]

The ADP1 analysis adds a related methodological tension: very high cofitness can identify a shared functional subsystem, but it does not distinguish direct physical interaction, common operon regulation, indirect metabolic coupling, or shared dispensability. [src: aromatic_catabolism_network] In particular, 11 Complex I-associated assignments beyond the core nuo operon were based on cofitness and may include indirect connections. [src: aromatic_catabolism_network]

The pan-bacterial ICA results clarify that robust cofitness structure does not resolve this mechanistic ambiguity. Although 94.2% of modules showed significant cofitness enrichment, the method had below-1% strict precision for exact KEGG KO prediction. [src: fitness_modules] Thus, strong within-module correlation is evidence for coordinated fitness behavior, not by itself evidence for a shared molecular function. [src: fitness_modules]

### Cofitness signal versus biochemical specificity

In ADP1, Complex I orthologs showed worse fitness on aromatic conditions than on non-aromatic conditions, with means of −1.35 and −0.77, respectively (Mann–Whitney p < 0.0001). [src: aromatic_catabolism_network] However, the strongest condition-level defects occurred on acetate (−1.55) and succinate (−1.39), which are non-aromatic, high-NADH substrates. [src: aromatic_catabolism_network] This weakens a purely aromatic interpretation and supports the hypothesis that the cofitness signal reflects [[concepts/nadh-flux-respiratory-constraints|NADH-flux respiratory constraints]] shaped by organism-specific respiratory architecture. [src: aromatic_catabolism_network]

## Open Directions

- Perform a fitness-matched permutation by drawing non-AMR genes with the same mean-fitness distribution as AMR genes, testing whether flagellar and biosynthetic enrichment remains AMR-specific. [src: amr_cofitness_networks]
- Recalculate networks separately for antibiotic-stress and standard-growth conditions to test whether AMR–motility associations are condition-specific. [src: amr_cofitness_networks]
- Measure the distribution of flagellar-gene knockout fitness across [[entities/fitness-browser]] experiments to test the plausibility of the shared-dispensability explanation. [src: amr_cofitness_networks]
- Repeat enrichment at |r| > 0.4 and |r| > 0.5, and evaluate PFam domains, to determine whether the strongest associations yield more specific functions than broad GO categories. [src: amr_cofitness_networks]
- Compare AMR networks with phage-defense and secondary-metabolite gene networks to test whether the pattern is a general property of conditionally dispensable genes. [src: amr_cofitness_networks]
- Expand the ADP1 fitness panel beyond 8 conditions with aromatic substrates, acetate, succinate, iron limitation, and respiratory inhibitors to test whether cofitness clusters track substrate-specific pathways or NADH load. [src: aromatic_catabolism_network]
- Test ACIAD3137 and ACIAD2176 using protein-interaction or Complex I co-purification experiments to distinguish physical accessory roles from indirect phenotypic coupling. [src: aromatic_catabolism_network]
- Integrate cofitness assignments with [[entities/flux-balance-analysis]] reaction mappings and [[concepts/metabolic-model-gapfilling]] to determine whether support genes omitted from metabolic models improve condition-dependent essentiality predictions. [src: aromatic_catabolism_network]
- Compare the 6,691 module-based predictions with ortholog-transfer predictions and domain annotations to identify cases where process-level cofitness adds information beyond sequence similarity. [src: fitness_modules]
- Test whether module strength and family conservation vary with experiment count, particularly in organisms with fewer than approximately 100 experiments, and assess whether the 40% component cap omits reproducible modules. [src: fitness_modules]
- Integrate module families with pangenome core, auxiliary, and singleton classifications to test whether conserved cofitness programs are preferentially associated with core genes or also recruit accessory genes. [src: fitness_modules]

## Related sources

See [[summaries/amr_cofitness_networks__REPORT]] for the complete AMR project summary and supporting analyses.

See [[summaries/aromatic_catabolism_network__REPORT]] for the ADP1 aromatic-catabolism support-network analysis.

See [[summaries/fitness_modules__REPORT]] for the pan-bacterial ICA module analysis and benchmarking.

See also: [[summaries/annotation_gap_discovery__REPORT]]

See also: [[summaries/conservation_fitness_synthesis__REPORT]]

See also: [[summaries/fw300_metabolic_consistency__REPORT]]

See also: [[summaries/snipe_defense_system__REPORT]]

See also: [[summaries/truly_dark_genes__REPORT]]