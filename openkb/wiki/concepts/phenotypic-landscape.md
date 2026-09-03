---
type: "Concept"
sources: ["summaries/respiratory_chain_wiring__REPORT.md", "summaries/fitness_effects_conservation__REPORT.md", "summaries/discoveries.md", "summaries/core_gene_tradeoffs__REPORT.md", "summaries/aromatic_catabolism_network__REPORT.md", "summaries/adp1_triple_essentiality__REPORT.md", "summaries/adp1_deletion_phenotypes__REPORT.md"]
description: "How ADP1 gene-deletion effects form continuous and condition-specific phenotypic patterns"
---

# Phenotypic Landscape Structure

## Overview

The phenotypic landscape describes how gene-deletion growth effects vary across environmental conditions. In the ADP1 deletion collection, eight carbon sources produce mostly continuous, condition-dependent patterns rather than sharply separated functional modules. The main exception is a compact quinate-specific module associated with aromatic degradation. [src: adp1_deletion_phenotypes]

This structure provides a genome-scale example of [[concepts/condition-dependent-essentiality]]: gene importance is not adequately represented by a single essential/non-essential label because the same deletion can have different effects depending on the available carbon source. [src: adp1_deletion_phenotypes]

The triple essentiality analysis reinforces this interpretation by showing that growth-rate effects contain information not captured by binary FBA or TnSeq essentiality classes. Among 478 genes with TnSeq, FBA, and growth data, all were TnSeq-dispensable, yet FBA class was not associated with growth-defect status (chi-squared = 0.93, p = 0.63). [src: adp1_triple_essentiality]

The aromatic-catabolism support-network analysis refines the interpretation of the quinate exception. It identifies 51 quinate-specific genes spanning the pathway itself and distributed support functions, including respiratory NADH reoxidation, iron acquisition, PQQ biosynthesis, and regulation. [src: aromatic_catabolism_network]

## Evidence for a Continuous Landscape

The complete growth matrix contains 2,034 genes measured across all eight carbon sources. Hierarchical clustering of their eight-condition growth profiles gives an optimal K = 3, but the silhouette score is only 0.24. The two large groups contain 1,160 and 850 genes and broadly correspond to generally sensitive and generally tolerant profiles. No functional enrichment survives FDR correction for these groups. [src: adp1_deletion_phenotypes]

The low clustering quality and absence of robust functional enrichment indicate that most genes do not fall into discrete phenotype classes. Instead, their growth effects vary along gradients of overall sensitivity and condition-specific response. This supports the interpretation that the ADP1 phenotype landscape is predominantly continuous rather than modular. [src: adp1_deletion_phenotypes]

The triple-study growth analysis provides an independent quantitative indication of this continuum. Using a Q25 threshold separately for each condition, 333 of 478 genes (70%) showed a defect on some but not all of the eight carbon sources, while 10 genes (2%) were defective across all eight and 135 genes (28%) showed no defect. Mean pairwise defect correlation was 0.38, with values ranging from -0.03 to 1.0. [src: adp1_triple_essentiality]

Because the Q25 threshold flags the lowest-growth quarter within each condition, the resulting any-condition-defect rate is affected by aggregation across eight assays. The observed 72% rate was lower than the 90% expected under independence, consistent with positive inter-condition correlation but also with substantial condition-specific variation. [src: adp1_triple_essentiality]

The 51-gene aromatic support network demonstrates that a continuous genome-wide landscape can contain tightly coordinated local phenotypes. Co-fitness correlations among known Complex I genes reached r = 0.992, and correlations among aromatic-pathway genes reached r = 0.961, indicating highly coherent subsystem-specific responses even though most genes do not form robust global clusters. [src: aromatic_catabolism_network]

## Environmental Dimensions

The eight carbon sources provide approximately five independent dimensions of phenotypic information. Pairwise Pearson correlations are moderate at best, with a maximum of r = 0.58 for acetate–butanediol and a median of r = 0.25 across all 28 condition pairs. PCA requires five components to explain 82% of the variance; PC1 explains 36.7% and captures general growth sensitivity, while PC2 explains 12.7% and isolates urea responses from carbon-metabolism responses. [src: adp1_deletion_phenotypes]

The condition structure therefore cannot be reduced to a simple demanding-versus-robust classification. Urea, acetate, and butanediol are demanding conditions, asparagine and lactate are moderate, and glucarate, glucose, and quinate are robust based on aggregate growth-defect patterns. However, the moderate inter-condition correlations show that these tiers summarize overall severity without eliminating substantial condition-specific information. [src: adp1_deletion_phenotypes]

Condition-matched FBA flux measurements also showed weak and mixed relationships with growth. Spearman correlations ranged from -0.257 for asparagine to +0.246 for glucarate; glucose showed no correlation (rho = -0.021, p = 0.677). The positive glucarate relationship is opposite to the expected direction and suggests that model predictions can fail in a substrate-specific manner. [src: adp1_triple_essentiality]

These results distinguish two levels of prediction: FBA showed moderate concordance with knockout lethality in separate genome-wide comparisons, with F1 = 0.624 in rich medium and F1 = 0.673 in minimal medium, but FBA class did not explain quantitative growth defects among TnSeq-dispensable genes. [src: adp1_triple_essentiality]

The aromatic support-network analysis adds a mechanistic example of this limitation. FBA predicted 1.76× higher Complex I flux on aromatic substrates than on the comparison condition (0.55 versus 0.31), but predicted 0% essentiality for Complex I genes. Thus, the model detected increased flux demand without representing the bottleneck behavior of a multi-subunit respiratory complex. [src: aromatic_catabolism_network]

## The Quinate-Specific Exception

A 24-gene module shows extreme quinate-specific defects, with a mean quinate z-score of -7.28 and near-zero responses in the other conditions. These genes are associated with aromatic degradation and constitute the only clearly discrete phenotypic module identified in the analysis. [src: adp1_deletion_phenotypes]

The result connects the [[entities/quinate-aromatic-degradation]] pathway to a sharply localized region of the phenotype landscape. A larger quinate-specific set contains 51 genes with specificity > 0.5 and z-score < -1, extending beyond core degradation genes to include NADH–ubiquinone oxidoreductase subunits. This broader pattern suggests the hypothesis that aromatic catabolism imposes distinctive electron-transport-chain demands. [src: adp1_deletion_phenotypes]

The support-network analysis gives this larger pattern a biochemical structure. Of the 51 genes, 44 (86%) were assigned to four support subsystems: 8 aromatic-pathway genes, 21 Complex I genes, 7 iron-acquisition genes, and 2 PQQ-biosynthesis genes; 6 additional genes were transcriptional regulators. The network therefore links quinate degradation to PQQ-dependent quinate dehydrogenase, iron-dependent protocatechuate 3,4-dioxygenase, and increased NADH-reoxidation demand after β-ketoadipate-derived metabolites enter the TCA cycle. [src: aromatic_catabolism_network]

The support functions are metabolically coupled but genomically separated. The Complex I operon lies at 714–729 kb, the pca/qui pathway at 1,709–1,724 kb, PQQ biosynthesis at 2,461 kb, and iron-acquisition genes are distributed across four loci. This organization shows that a coherent phenotypic module can emerge from biochemical dependency rather than cross-category genomic co-localization. [src: aromatic_catabolism_network]

Aromatic degradation is also the principal functional category associated with FBA discordance in the triple essentiality analysis. Nine of 11 aromatic degradation genes were discordant (OR = 9.70, q = 0.012), and directional analysis showed enrichment specifically for FBA under-prediction (OR = 12.0, q = 0.004). These genes were generally predicted to be blocked even though their deletion was associated with growth defects. [src: adp1_triple_essentiality]

The convergence of quinate-specific phenotypes and FBA under-prediction suggests a model-environment mismatch as a testable explanation: the in silico minimal-medium definition may omit trace aromatic substrates or other relevant experimental inputs. This is a hypothesis rather than an established mechanism because the media composition and alternative functions of the discordant genes were not directly resolved. [src: adp1_triple_essentiality]

The cross-species analysis qualifies the interpretation that Complex I is aromatic-specific. Complex I orthologs had worse fitness on aromatic conditions than on non-aromatic conditions (mean = -1.35 versus -0.77, Mann–Whitney p < 0.0001), but their largest defects relative to background occurred on acetate (-1.55) and succinate (-1.39). This supports the hypothesis that the apparent quinate-specificity reflects a high-NADH-flux respiratory constraint, with the alternative NADH dehydrogenase NDH-2 potentially compensating on simpler substrates. [src: aromatic_catabolism_network]

## Functional Interpretation

Although broad clustering does not recover discrete functional modules, condition-specific scoring identifies 625 genes, or 31% of the complete matrix, with a specificity score >= 1.0. These genes map to expected pathways for quinate, urea, asparagine, acetate, glucarate, glucose, butanediol, and lactate metabolism. Thus, the absence of broad clusters does not indicate an absence of biological structure; it indicates that much of the structure is distributed across condition-specific gradients rather than concentrated in mutually exclusive modules. [src: adp1_deletion_phenotypes]

The pattern is consistent with the [[concepts/condition-dependent-essentiality]] framework and differs from reports of discrete phenotypic modules in *E. coli* chemical-genetic profiles. The difference may reflect either the interconnected metabolic architecture of ADP1 or the distinction between single-gene deletions and chemical perturbations; the current analysis does not distinguish between these explanations. [src: adp1_deletion_phenotypes]

The triple analysis further indicates that different measurement systems partition this landscape differently. Mutant growth assays capture condition-specific optimization, whereas FBA class primarily captures predicted metabolic necessity near the lethal/dispensable boundary. Continuous TnSeq fitness performed better than binary essentiality fraction for predicting knockout essentiality, with AUC values of 0.700–0.725 versus 0.344–0.403, respectively. [src: adp1_triple_essentiality]

This distinction supports [[concepts/method-concordance]]: a gene can be dispensable for viability yet impose a measurable growth cost, and a gene can show condition-specific growth effects without belonging to a sharply separated phenotypic module. [src: adp1_triple_essentiality]

The aromatic network further supports [[concepts/metabolic-support-networks]]. Its 51 genes include 30 without FBA reaction mappings, particularly genes involved in PQQ supply, iron acquisition, respiratory support, and regulation. The result suggests that model coverage of core reactions does not guarantee coverage of the biological infrastructure required for condition-specific growth. [src: aromatic_catabolism_network]

Co-fitness analysis assigned 16 of 23 initially Other/Unknown genes to support subsystems. Two DUF proteins, ACIAD3137 and ACIAD2176, showed r > 0.98 correlations with Complex I genes and are candidate Complex I accessory factors. These assignments are provisional because they rely on phenotypic correlation rather than direct physical-association evidence. [src: aromatic_catabolism_network]

## Tensions and Scope

The data support both a continuous global landscape and a discrete quinate-associated module. These findings are not necessarily contradictory: the low silhouette score and lack of enrichment describe the dominant genome-wide pattern, whereas the quinate module represents a localized exception. [src: adp1_deletion_phenotypes]

FBA provides a second apparent tension. It shows moderate agreement with knockout lethality but no association with growth defects within TnSeq-dispensable genes. These results concern different endpoints and gene subsets, so they should not be combined into a single estimate of FBA performance. [src: adp1_triple_essentiality]

A further qualification concerns the interpretation of the Complex I module. ADP1 data show quinate-specific Complex I-associated defects, whereas ortholog-transferred data show the strongest Complex I defects on acetate and succinate as well as aromatics. The two observations are compatible with a high-NADH-flux mechanism, but the cross-species evidence does not establish that mechanism directly in ADP1. [src: aromatic_catabolism_network]

The apparent number of independent dimensions is limited by the eight tested carbon sources. The estimate of approximately five dimensions may increase when additional carbon sources, nitrogen sources, or stress conditions are measured. [src: adp1_deletion_phenotypes]

Growth ratios are single-timepoint measurements with unknown technical noise. Consequently, some apparent condition specificity could reflect measurement error rather than biological differentiation. [src: adp1_deletion_phenotypes]

The triple-study defect analysis used per-condition quartile thresholds and an any-condition aggregation, whereas the complete deletion matrix used profile clustering and PCA. The two analyses therefore support the same broad interpretation but are not identical measurements of the landscape. [src: adp1_deletion_phenotypes, adp1_triple_essentiality]

The co-fitness analysis also used only 8 conditions, limiting correlation resolution, and the ortholog-transferred fitness data combines organisms with different respiratory-chain architectures. The 11 non-core Complex I assignments may therefore include indirect dependencies rather than physical Complex I components. [src: aromatic_catabolism_network]

## Open Directions

- Apply [[entities/independent-component-analysis]] to the 2,034 × 8 growth matrix and test whether latent condition-specific factors provide more interpretable structure than hierarchical clustering. [src: adp1_deletion_phenotypes]
- Add carbon, nitrogen, and stress conditions, then re-estimate the number of independent phenotypic dimensions and test whether the continuous landscape persists. [src: adp1_deletion_phenotypes]
- Compare ADP1 condition-specific profiles with overlapping Fitness Browser measurements generated by [[entities/random-barcode-transposon-sequencing]] to test whether pathway-level phenotype gradients recur across organisms. [src: adp1_deletion_phenotypes]
- Re-run condition-specific FBA with measured media compositions, including trace aromatic substrates, and test whether predictions for the quinate/aromatic module and glucarate growth effects improve. [src: adp1_triple_essentiality]
- Identify and perturb ADP1 [[entities/ndh-2]] to test whether it compensates for Complex I on glucose, lactate, acetate, succinate, and quinate. [src: aromatic_catabolism_network]
- Validate ACIAD3137 and ACIAD2176 through protein-interaction or Complex I co-purification experiments. [src: aromatic_catabolism_network]
- Expand the condition panel with benzoate, catechol, vanillate, iron limitation, and respiratory inhibitors to test the NADH-flux hypothesis directly. [src: aromatic_catabolism_network]
- Reassess the 30 unmapped genes by integrating PQQ biosynthesis, iron homeostasis, and respiratory-capacity constraints into the FBA model. [src: aromatic_catabolism_network]
- Test whether continuous FBA flux, rather than binary FBA class, predicts growth-rate magnitude across matched carbon sources. [src: adp1_triple_essentiality]

## Sources

- [[summaries/adp1_deletion_phenotypes__REPORT]]
- [[summaries/adp1_triple_essentiality__REPORT]]
- [[summaries/aromatic_catabolism_network__REPORT]]

See also: [[summaries/core_gene_tradeoffs__REPORT]]

See also: [[summaries/discoveries]]

See also: [[summaries/fitness_effects_conservation__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]