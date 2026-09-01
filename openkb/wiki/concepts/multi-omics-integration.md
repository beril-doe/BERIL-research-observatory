---
type: "Concept"
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/respiratory_chain_wiring__REPORT.md", "summaries/functional_dark_matter__REPORT.md", "summaries/enigma_sso_asv_ecology__REPORT.md", "summaries/clay_confined_subsurface__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/annotation_gap_discovery__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md", "summaries/acinetobacter_adp1_explorer__REPORT.md"]
description: "Integrating complementary omics reveals condition-dependent biology and model limitations."
---

# Multi-Omics Integration

[[concepts/multi-omics-integration]] combines complementary molecular, genetic, comparative, and metabolic measurements so that biological interpretations can be evaluated across evidence types rather than within a single assay. The ADP1 exploration, triple-essentiality analysis, aromatic-catabolism network, and Web of Microbes integration demonstrate both the value of this approach and the practical limits imposed by incomplete overlap, condition dependence, annotation gaps, and differences in what each assay measures. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality, aromatic_catabolism_network, webofmicrobes_explorer]

## ADP1 as an integrated resource

The *Acinetobacter baylyi* ADP1 database contains 15 interconnected tables, 461,522 total rows, and 135 MB of data covering ADP1 and 13 related genomes. [src: acinetobacter_adp1_explorer] Its `genome_features` table contains 5,852 genes and 51 annotation columns spanning TnSeq essentiality, FBA metabolic flux, mutant growth fitness on eight carbon sources, proteomics across seven strains, pangenome classification, and COG/KO/Pfam/UniRef functional annotations. [src: acinetobacter_adp1_explorer]

The modalities have uneven coverage: TnSeq essentiality covers 58% of genes, FBA flux 15%, mutant growth fitness 39%, proteomics 41%, pangenome classification 54%, and functional annotations 34–55%. [src: acinetobacter_adp1_explorer] No gene has data across all six modalities, but pairwise overlaps are substantial, especially among essentiality, pangenome, and proteomics measurements. [src: acinetobacter_adp1_explorer] These coverage constraints mean that integration generally supports pairwise or subset analyses rather than complete gene-level evidence profiles. [src: acinetobacter_adp1_explorer]

The refined triple-essentiality analysis expands the comparison to all available genes and explicitly combines knockout phenotypes, FBA, RB-TnSeq thresholds and continuous fitness, and proteomics. [src: adp1_triple_essentiality] It therefore distinguishes agreement at the lethality boundary from quantitative variation among genes that remain viable after disruption. [src: adp1_triple_essentiality]

The aromatic-catabolism analysis provides a complementary integration case centered on 51 quinate-specific genes in ADP1. It combines growth phenotypes, FBA flux and reaction mappings, genomic organization, co-fitness correlations, biochemical annotation, and ortholog-transferred fitness data. [src: aromatic_catabolism_network] Unlike a single-pathway analysis, this integration identifies a distributed support network spanning core aromatic degradation, Complex I, iron acquisition, PQQ biosynthesis, and regulation. [src: aromatic_catabolism_network]

## What integration reveals

### Experimental and computational essentiality

FBA predictions and TnSeq essentiality calls overlap for 866 genes. [src: acinetobacter_adp1_explorer] The two approaches agree for 639 genes, or 73.8%, while 227 genes are discordant. [src: acinetobacter_adp1_explorer] The concordant majority provides cross-method support for essentiality inference, whereas the discordant genes are candidates for metabolic-model refinement or for investigating regulatory effects not represented by FBA. [src: acinetobacter_adp1_explorer] This analysis connects [[entities/flux-balance-analysis]] with [[entities/random-barcode-transposon-sequencing]].

When evaluated against experimental knockout phenotypes, FBA showed moderate rather than complete concordance: in rich medium, F1 = 0.624 and κ = 0.486, while in minimal medium, F1 = 0.673 and κ = 0.493. [src: adp1_triple_essentiality] FBA recall was 60.8% in rich medium and 65.6% in minimal medium, with precision values of 64.0% and 69.2%, respectively. [src: adp1_triple_essentiality] The stronger minimal-medium performance suggests that tighter metabolic constraints may make FBA assumptions more representative, although this explanation remains an interpretation rather than a directly tested mechanism. [src: adp1_triple_essentiality]

Essentiality also changes with growth environment: 499 genes are essential on minimal media compared with 346 on LB. [src: acinetobacter_adp1_explorer] Thus, integrating genetic essentiality with metabolic context can distinguish condition-dependent requirements from more general cellular requirements, linking this resource to [[concepts/condition-dependent-essentiality]]. [src: acinetobacter_adp1_explorer]

The triple-essentiality analysis adds an important boundary condition: FBA did not predict growth defects among 478 genes that were all TnSeq-dispensable. [src: adp1_triple_essentiality] At the Q25 threshold, defect rates were 73.1% for FBA-essential genes, 73.5% for FBA-variable genes, and 69.4% for FBA-blocked genes; the association was not significant (chi-squared = 0.93, p = 0.63). [src: adp1_triple_essentiality] Thus, FBA can provide moderate discrimination between knockout-lethal and knockout-dispensable genes, but its binary class does not explain continuous growth variation within the dispensable set. [src: adp1_triple_essentiality]

### Fitness and metabolic context

Mutant growth fitness across eight carbon sources has a mean pairwise correlation of 0.44. [src: acinetobacter_adp1_explorer] Urea fitness is weakly correlated with the other conditions (r = 0.12–0.28) and has a correlation of r = 0.11 with quinate, suggesting the hypothesis that urea catabolism uses a comparatively distinct gene set. [src: acinetobacter_adp1_explorer] Butanediol-acetate and butanediol-lactate show the strongest correlations, r = 0.58 and r = 0.53, respectively, consistent with shared central-carbon metabolism. [src: acinetobacter_adp1_explorer]

The original triple-essentiality analysis found that 333 of 478 genes (70%) had condition-specific growth defects across the eight tested carbon sources, only 10 genes (2%) had defects in all eight conditions, and 135 genes (28%) had no defect on any condition. [src: adp1_triple_essentiality] Mean pairwise defect correlation was 0.38, indicating partial overlap among condition-specific requirements. [src: adp1_triple_essentiality] These results strengthen the role of [[concepts/phenotypic-landscape]] in interpreting essentiality: growth importance is often continuous and substrate-dependent rather than a single binary property. [src: adp1_triple_essentiality]

FBA flux classes provide an additional environmental dimension: 177 of 866 genes (20%) change flux class between rich and minimal media. [src: acinetobacter_adp1_explorer] However, condition-specific FBA flux showed weak and mixed correlations with measured growth across six matched carbon sources, ranging from ρ = -0.257 for asparagine to ρ = +0.246 for glucarate. [src: adp1_triple_essentiality] The positive glucarate correlation is opposite to the expected direction and indicates that condition-specific model assumptions can affect integrated interpretation. [src: adp1_triple_essentiality]

Continuous measurements also outperform some binary TnSeq summaries. In the refined analysis, inverted continuous fitness predicted knockout essentiality with AUC = 0.700 in rich medium and AUC = 0.725 in minimal medium, whereas essentiality fraction produced AUC = 0.344 and AUC = 0.403, respectively. [src: adp1_triple_essentiality] At an essentiality-fraction threshold of 0.05, RB-TnSeq versus knockout data had recall = 7.9%, precision = 5.8%, F1 = 0.067, and κ = -0.081; all tested thresholds produced negative κ values. [src: adp1_triple_essentiality] This distinction shows why [[entities/random-barcode-transposon-sequencing]] should be integrated through continuous fitness and condition-matched measurements rather than treated as a direct substitute for complete-gene knockout data. [src: adp1_triple_essentiality]

### Aromatic catabolism as a metabolic-support network

The aromatic-catabolism analysis shows how integrating phenotypic, metabolic, genomic, and comparative evidence can reveal dependencies outside a core pathway. Of 51 quinate-specific genes, 44 (86%) were assigned to four functional subsystems: 8 aromatic-pathway genes, 21 Complex I genes, 7 iron-acquisition genes, and 2 PQQ-biosynthesis genes; 6 transcriptional regulators and 7 unassigned genes completed the set. [src: aromatic_catabolism_network] This is an example of [[concepts/metabolic-support-networks]] in which cofactor supply, respiratory capacity, and regulation are required alongside substrate-conversion enzymes.

The biochemical interpretation is coherent across modalities. Quinate dehydrogenase requires the [[entities/pqq]] cofactor, protocatechuate 3,4-dioxygenase requires Fe²⁺ supplied through [[entities/iron]] acquisition, and TCA-cycle oxidation of β-ketoadipate products generates NADH that must be reoxidized by [[entities/complex-i]]. [src: aromatic_catabolism_network] The four subsystems are genomically separated—Complex I at 714–729 kb, the pca/qui pathway at 1,709–1,724 kb, PQQ biosynthesis at 2,461 kb, and iron-acquisition genes across four loci—so their functional coupling emerges from metabolism rather than cross-category operon organization. [src: aromatic_catabolism_network]

The integrated evidence also exposes a specific FBA limitation. FBA predicted 1.76× higher Complex I flux on aromatic substrates (0.55 versus 0.31) but 0% essentiality, while 30 of the 51 quinate-specific genes had no FBA reaction mappings. [src: aromatic_catabolism_network] The analysis therefore links [[entities/flux-balance-analysis]] to [[concepts/metabolic-model-gapfilling]]: flux calculations can register increased demand while omitting cofactor supply chains, regulatory genes, accessory factors, and the threshold behavior of a multi-subunit respiratory complex. [src: aromatic_catabolism_network]

Co-fitness adds functional evidence for poorly annotated genes. Sixteen of 23 initially Other/Unknown genes were assigned to support subsystems with medium or high confidence; within-category correlations were high for Complex I (r = 0.992) and the aromatic pathway (r = 0.961). [src: aromatic_catabolism_network] ACIAD3137 and ACIAD2176 correlated with Complex I genes at r > 0.98 and are candidates for uncharacterized Complex I accessory factors, although correlation alone does not establish physical association. [src: aromatic_catabolism_network] This illustrates how [[concepts/cofitness-networks]] can connect phenotypic profiles to biochemical hypotheses.

Cross-species fitness data qualifies the interpretation further. Complex I orthologs had mean fitness of -1.35 on aromatic conditions versus -0.77 on non-aromatic conditions (Mann–Whitney p < 0.0001), but the largest defects relative to background occurred on acetate (-1.55) and succinate (-1.39). [src: aromatic_catabolism_network] The result supports the hypothesis that Complex I dependence tracks high NADH flux rather than aromaticity specifically, with [[entities/ndh-2]] potentially compensating on lower-NADH substrates. [src: aromatic_catabolism_network] Because the comparison uses ortholog-transferred data from organisms with different respiratory architectures, the hypothesis requires direct testing in ADP1. [src: aromatic_catabolism_network]

### Comparative genomics and functional annotation

The database links gene-level measurements to pangenome context through a complete bridge between BERDL cluster identifiers and ADP1 cluster identifiers. [src: acinetobacter_adp1_explorer] All 4,891 BERDL clusters mapped to 4,081 unique ADP1 clusters through gene membership, enabling comparative annotations to be joined to ADP1 measurements. [src: acinetobacter_adp1_explorer] This linkage illustrates the role of [[concepts/pangenome-integration]] in extending multi-omics interpretation beyond one reference genome.

Essential genes are more frequently annotated than dispensable genes: 33% of essential genes have COG assignments versus 5% of dispensable genes, and 92% have KEGG KO assignments versus 53% of dispensable genes. [src: acinetobacter_adp1_explorer] Approximately 8% of essential genes lack KO assignments, making them candidates for investigation, although their novelty is not established by annotation absence alone. [src: acinetobacter_adp1_explorer] Essential genes are also more likely to belong to the core pangenome. [src: acinetobacter_adp1_explorer]

The triple-essentiality analysis found no significant pangenome-status enrichment among its FBA-discordant genes: core genes represented 93–100% of the analyzed concordance classes, with Fisher OR = 0.89 and p = 0.80. [src: adp1_triple_essentiality] This result qualifies the broader association between essentiality and core-genome membership: pangenome context remains informative, but it did not explain the specific FBA discordance examined in the 478-gene study. [src: acinetobacter_adp1_explorer, adp1_triple_essentiality]

### Proteomics and engineered strains

Proteomics measurements cover 2,383 genes across seven ADP1 strains, including wild type and six derivatives with aromatic amino acid pathway modifications. [src: acinetobacter_adp1_explorer] High cross-strain protein-abundance correlations indicate that these engineered modifications have targeted rather than globally disruptive effects on the proteome. [src: acinetobacter_adp1_explorer] This provides a strain-comparison layer complementary to gene essentiality, metabolic flux, and growth fitness; the relevant measurement type is represented by [[entities/proteomics]].

The refined analysis further showed that proteomics expression is associated with knockout essentiality. [src: adp1_triple_essentiality] Among 2,288 genes, essential genes had mean log2 expression of 28.43 and dispensable genes had mean log2 expression of 25.73, a 2.70-log2-unit difference corresponding to 6.5-fold higher expression in essential genes. [src: adp1_triple_essentiality] The association was highly significant (Mann-Whitney p = 9.91×10⁻⁵⁹), with Pearson r = 0.345, Spearman ρ = 0.338, and ROC AUC = 0.743. [src: adp1_triple_essentiality] Expression therefore supplies an independent, fair-to-good predictor of essentiality, but it should be interpreted as supporting evidence rather than proof of causal requirement. [src: adp1_triple_essentiality]

### Web of Microbes and metabolite-to-gene integration

The [[entities/web-of-microbes]] analysis extends multi-omics integration from intracellular gene and flux measurements to extracellular metabolite production. A 2018 snapshot contains 37 organisms across 5 ENIGMA-funded projects, 589 tracked metabolites, and 10 growth environments. [src: webofmicrobes_explorer] Its organism observations use four distinct action semantics: controls record detected (`D`) or not detected (`N`) metabolites, while organisms record increased (`I`), emerged (`E`), or unchanged (`N`) metabolites. [src: webofmicrobes_explorer]

The distinction between `E` and `I` is especially useful for integration. `E` denotes a metabolite absent from the starting medium that subsequently appeared, consistent with de novo production, whereas `I` denotes amplification of a metabolite already present. The two actions had zero overlap across 10,744 observations. [src: webofmicrobes_explorer] No organism-level decrease or consumption action appears in this snapshot, so the data support analysis of production and [[concepts/metabolic-novelty]] but not direct inference about uptake or consumption. [src: webofmicrobes_explorer]

Two direct WoM–Fitness Browser strain matches are available: *Pseudomonas* sp. FW300-N2E3 maps to `pseudo3_N2E3` with 5,854 genes and 211 experiments, and *Pseudomonas* sp. GW456-L13 maps to `pseudo13_GW456_L13` with 5,243 genes and 106 experiments. [src: webofmicrobes_explorer] *E. coli* BW25113 also matches the `Keio` strain, while a *Synechococcus* match is only at the genus level. [src: webofmicrobes_explorer] For pseudo3_N2E3, 19 WoM-produced metabolites are tested in Fitness Browser carbon- or nitrogen-source experiments; 5 are `E` products and 14 are `I` products. [src: webofmicrobes_explorer] This creates a direct testable connection between extracellular output and gene fitness during metabolite utilization, linking [[entities/fitness-browser]] to [[concepts/condition-dependent-essentiality]] and [[concepts/metabolite-production-utilization-decoupling]].

WoM also links to [[entities/modelseed]] at two confidence levels. Exact name matching gives definitive links for 69 of 257 identified compounds (26.8%), while formula-only matching adds 107 compounds (41.6%) and yields 176 compounds (68.5%) with any candidate link. [src: webofmicrobes_explorer] Formula matches are ambiguous, expanding from 107 WoM compounds to 900 ModelSEED molecules, or an average of 8.4 candidate molecules per WoM compound. [src: webofmicrobes_explorer] The result demonstrates that cross-collection linkage can be actionable without implying that every chemical identity is resolved; exact matches and formula candidates should be analyzed separately.

The ENIGMA isolates also exhibit distinct metabolic novelty rates in R2A medium. The fraction of changed metabolites classified as `E` ranges from 15.2% in *Bacillus* FW507-8R2A to 32.4% in *Pseudomonas* GW456-L13, with the other reported isolates ranging from 28.6% to 31.4%. [src: webofmicrobes_explorer] Because the dataset contains only 37 organisms and 20 experimental organisms, this is a phenotype for hypothesis generation rather than a validated comparative trait. It suggests the hypothesis that de novo production rates may relate to pangenome openness or accessory-gene content, a question that can be addressed through [[concepts/pangenome-integration]].

All WoM genera have pangenome representation, including 2,557 genomes for *Bacillus*, 449 for *Rhizobium*, 139 for *Pseudomonas fluorescens*, 88 for *Synechococcus*, 80 for *Phenylobacterium*, 79 for *Acidovorax*, 26 for *Zymomonas mobilis*, and 2 for *Escherichia coli*. [src: webofmicrobes_explorer] However, these links are currently genus-level; strain-to-genome matching was not attempted. [src: webofmicrobes_explorer]

## Integration with external resources

The ADP1 database connects to BERDL through genome identifiers, reactions, compounds, and pangenome clusters. [src: acinetobacter_adp1_explorer] Genome identifiers and compounds matched at 100%, pangenome clusters matched at 100% through the gene-level bridge, and 1,210 of 1,330 reactions matched ModelSEED biochemistry (91%). [src: acinetobacter_adp1_explorer] The 120 unmatched reactions may represent custom or draft reactions not yet present in ModelSEED. [src: acinetobacter_adp1_explorer] The database's relationship to [[entities/berdl]] and [[entities/modelseed]] therefore supports both contextual annotation and model interpretation.

The aromatic-catabolism analysis additionally used ortholog-transferred fitness from the [[entities/fitness-browser]], ADP1 gene-phenotype and reaction data, and pangenome annotations. [src: aromatic_catabolism_network] Its cross-species comparison demonstrates the value and risk of comparative integration: it revealed that Complex I defects extend to acetate and succinate, but mixed respiratory architectures limit organism-level inference. [src: aromatic_catabolism_network]

The WoM analysis adds an exometabolomics layer to this integration landscape. WoM links strongly to the Fitness Browser for the two *Pseudomonas* strains, moderately to ModelSEED through exact and formula-based compound matching, and at genus level to pangenomes. [src: webofmicrobes_explorer] Its connection to GapMind is currently blocked by pathway naming conventions: internal pathway identifiers do not expose simple substrate and product names, so a dedicated pathway-to-metabolite lookup table is required. [src: webofmicrobes_explorer]

ADP1 was absent from the Fitness Browser, so its mutant growth data on eight carbon sources is not duplicated there. [src: acinetobacter_adp1_explorer] This makes the database a distinctive source for integrating ADP1 fitness with comparative genomics and metabolic-model data, while cross-organism fitness comparisons remain a future opportunity. [src: acinetobacter_adp1_explorer]

## Tensions and limitations

The strongest limitation is incomplete modality overlap: FBA data covers only 15% of genes, and no gene has all six modalities. [src: acinetobacter_adp1_explorer] Consequently, integrated conclusions may be concentrated in better-characterized genes and may underrepresent poorly annotated or experimentally inaccessible functions. [src: acinetobacter_adp1_explorer]

A second limitation is that the assays do not share a single biological endpoint. Knockout experiments measure viability after complete deletion, FBA predicts metabolic necessity under specified constraints, RB-TnSeq measures insertion-associated fitness, proteomics measures abundance, and growth assays measure condition-specific optimization. [src: adp1_triple_essentiality] Their disagreements are therefore biologically informative rather than automatically evidence that one method is incorrect. [src: adp1_triple_essentiality]

RB-TnSeq and knockout results were systematically discordant in the refined comparison. At the 0.05 threshold, 211 genes were knockout-essential but TnSeq-dispensable, while 293 were knockout-dispensable but TnSeq-essential. [src: adp1_triple_essentiality] Possible explanations include residual function from transposon-disrupted alleles, condition differences, and the distinction between fitness cost and lethality; these mechanisms were proposed by the analysis but were not individually resolved. [src: adp1_triple_essentiality]

Aromatic degradation was a specific source of FBA discordance: 9 of 11 annotated aromatic-degradation genes were discordant (OR = 9.70, q = 0.012), and directional analysis gave OR = 12.0, q = 0.004 for FBA under-prediction. [src: adp1_triple_essentiality] The pattern includes beta-ketoadipate-pathway enzymes that were predicted to be blocked despite deletion-associated growth defects. [src: adp1_triple_essentiality] The report proposes that missing aromatic substrates or other environmental assumptions may explain the pattern, but trace aromatics and moonlighting functions remain hypotheses requiring testing. [src: adp1_triple_essentiality]

The aromatic-catabolism study adds a related model limitation: 30 of 51 quinate-specific genes lacked FBA reaction mappings, including PQQ, iron-acquisition, regulatory, and candidate Complex I accessory genes. [src: aromatic_catabolism_network] Its Complex I result also conflicts with the binary FBA essentiality prediction: elevated predicted flux coexists with 0% predicted essentiality, whereas gene-level phenotypes identify a substantial Complex I support requirement. [src: aromatic_catabolism_network] This is a limitation of model scope and representation, not evidence that the flux increase or the phenotype is incorrect.

The WoM data introduces a complementary limitation: it measures production more effectively than consumption in the available snapshot. The absence of organism-level decreases prevents testing whether consumed metabolites predict gene essentiality, resource competition, or cross-feeding direction. [src: webofmicrobes_explorer] The dataset is also small—37 organisms across 5 projects—and originates from a 2018 frozen snapshot, so its apparent metabolite-production patterns should not be generalized to current WoM coverage or broader microbial diversity without validation. [src: webofmicrobes_explorer]

Compound identity is another source of uncertainty. Only 26.8% of identified WoM compounds have definitive ModelSEED name links; formula-only matches account for 41.6% but average 8.4 candidate molecules per compound. [src: webofmicrobes_explorer] These ambiguous mappings can support candidate generation but should not be treated as resolved metabolite identities. GapMind integration is similarly incomplete because pathway-to-metabolite mappings are absent. [src: webofmicrobes_explorer]

The pangenome connection is complete at the reported gene level but indirect, because it passes through three tables and different clustering identifier systems. [src: acinetobacter_adp1_explorer] Potential cluster splits or merges between analyses should therefore be checked when interpreting cluster-level claims. [src: acinetobacter_adp1_explorer]

Growth prediction integration is also dependent on model assumptions: 105,376 of 121,519 predictions (87%) require at least one gapfilled reaction, and 243 missing functions were cataloged. [src: acinetobacter_adp1_explorer] This dependence makes gapfilling quality a major source of uncertainty and links multi-omics interpretation to [[concepts/metabolic-model-gapfilling]].

## Open Directions

- Test whether the 227 FBA–TnSeq discordant genes are enriched for regulatory functions, specific pathways, or accessory pangenome clusters. [src: acinetobacter_adp1_explorer]
- Reanalyze FBA, continuous fitness, knockout status, and proteomics jointly to determine whether a combined predictor improves on the reported individual AUC values. [src: adp1_triple_essentiality]
- Compare condition-matched TnSeq and knockout experiments to separate media effects from differences between insertion and complete-deletion mechanisms. [src: adp1_triple_essentiality]
- Analyze transposon insertion positions and protein domains in the 211 knockout-essential/TnSeq-dispensable genes to test whether residual function explains their discordance. [src: adp1_triple_essentiality]
- Add trace aromatic substrates or measured media compositions to FBA and test whether the 9 of 11 aromatic-degradation discordances are reduced. [src: adp1_triple_essentiality]
- Integrate quinate-specific growth phenotypes, Complex I flux, reaction mappings, and co-fitness assignments to test whether respiratory capacity predicts aromatic-catabolism defects better than pathway annotation alone. [src: aromatic_catabolism_network]
- Search ADP1 for [[entities/ndh-2]] and compare its deletion phenotype with Complex I deletions on quinate, glucose, acetate, and succinate. [src: aromatic_catabolism_network]
- Experimentally test ACIAD3137 and ACIAD2176 through protein-interaction or Complex I co-purification studies. [src: aromatic_catabolism_network]
- Expand the condition matrix with benzoate, catechol, vanillate, iron limitation, and respiratory inhibitors to test the NADH-flux hypothesis directly. [src: aromatic_catabolism_network]
- Compare pca-pathway-containing *Acinetobacter* genomes for retention of Complex I KOs K00330–K00343 using pangenome data. [src: aromatic_catabolism_network]
- Evaluate the 243 missing functions and the 30 unmapped quinate-specific genes as candidates for adding PQQ biosynthesis, iron homeostasis, and respiratory-capacity constraints to the FBA model. [src: acinetobacter_adp1_explorer, aromatic_catabolism_network]
- Join urea-specific fitness effects to the mapped pangenome clusters and ask whether candidate genes are conserved across the 14 genomes. [src: acinetobacter_adp1_explorer]
- Use protein abundance, essentiality, and flux-class transitions to distinguish direct pathway effects from broader condition-dependent responses in the engineered strains. [src: acinetobacter_adp1_explorer]
- Compare ADP1 fitness patterns with related organisms in the Fitness Browser after transferring homologous or pangenome-linked gene groups. [src: acinetobacter_adp1_explorer]
- For pseudo3_N2E3 and pseudo13_GW456_L13, join WoM-produced metabolites to condition-matched Fitness Browser gene effects to test whether extracellular production predicts utilization fitness. [src: webofmicrobes_explorer]
- Obtain current WoM or GNPS2 data containing consumption observations and test whether production–consumption profiles predict gene essentiality or cross-feeding relationships. [src: webofmicrobes_explorer]
- Build a GapMind pathway-to-metabolite lookup table and use it to connect predicted pathway capabilities with WoM production and Fitness Browser utilization conditions. [src: webofmicrobes_explorer]
- Test whether the WoM `E/(E+I)` metabolic novelty rate correlates with pangenome openness or accessory-gene content after strain-to-genome matching. [src: webofmicrobes_explorer]
- Manually curate formula-only ModelSEED matches and quantify how compound-identity uncertainty changes downstream metabolite-to-gene conclusions. [src: webofmicrobes_explorer]

See also: [[summaries/adp1_deletion_phenotypes__REPORT]]

## Related Documents

- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/alphafold_msa_annotation__REPORT]]
- [[summaries/annotation_gap_discovery__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]
- [[summaries/webofmicrobes_explorer__REPORT]]

See also: [[summaries/clay_confined_subsurface__REPORT]]

See also: [[summaries/enigma_sso_asv_ecology__REPORT]]

See also: [[summaries/functional_dark_matter__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]