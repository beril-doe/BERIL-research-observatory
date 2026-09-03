---
type: "Summary"
description: "Cross-project log of validated findings, methodological lessons, and open research directions."
doc_type: short
full_text: "sources/discoveries.md"
---

# Discoveries Log Summary

This running log records durable findings from BERIL research projects, emphasizing cross-project methodological lessons, validated biological patterns, contradictions, and analyses that should be refactored into structured documentation.

## Major cross-project concepts

- [[concepts/pangenome-integration]]: Tree-aware Sankoff attribution across 17 million gain events shows that recent-to-ancient acquisition ratios distinguish horizontally transferred functions from vertically inherited housekeeping genes. CRISPR-Cas has a 24.5× recent/ancient ratio, strict housekeeping is approximately 1×, and mixed regulatory-metabolic pathways show roughly twice the Innovator-Exchange rate of pure regulatory or metabolic functions. Leaf-consistency analysis independently reproduces the depth trend.
- [[concepts/core-accessory-resistance]]: Core and accessory status is not a simple proxy for fitness importance. Core genes are modestly enriched among essential, condition-specific, module-associated, and trade-off genes, and are also more likely to be burdensome under some conditions. Function-specific exceptions exist, especially for cell-wall genes.
- [[concepts/horizontal-gene-transfer]] and [[concepts/two-speed-genome]]: Pangenome novelty is consistently enriched for mobile elements, defense functions, and unknown-function genes. However, individual projects can reverse the expected HGT interpretation: plant-growth-promoting genes are predominantly core and appear vertically inherited, whereas plant marker-gene singletons strongly co-localize with mobile-element singletons.
- [[concepts/annotation-gap]]: Most apparently dark genes are not completely unknowable. Only 16.3% of Fitness Browser dark genes remain hypothetical after Bakta reannotation, and only 7.5% of dark ortholog groups have no evidence. Fitness phenotypes, orthology, domains, modules, and environmental distributions provide converging clues, while orphan essential genes remain high-value experimental targets.
- [[concepts/cofitness-networks]] and independent component analysis: ICA decomposes fitness variation into biologically coherent, adjacency-enriched modules when membership thresholds are calibrated to module weights. Modules are useful for process-level inference rather than precise KO prediction, and cross-organism module families require ortholog data from all organisms rather than a small pilot subset.
- [[concepts/condition-dependent-essentiality]] and [[concepts/metabolic-model-gapfilling]]: Pathway completeness does not imply metabolic dependency. Many complete pathways are latent in rich media but become important under nutrient limitation, stress, or carbon-source changes. Pathway variability is strongly associated with pangenome openness, and ecosystem metabolic variation is dominated by carbon-utilization pathways before amino-acid biosynthesis.
- [[concepts/nadh-flux-respiratory-constraints]]: In [[entities/acinetobacter-baylyi-adp1]], respiratory configuration depends on substrate-specific NADH flux rather than total carbon yield or transcriptional switching. [[entities/complex-i]], [[entities/ndh-2]], and ACIAD3522 have distinct condition requirements, and aromatic catabolism requires extensive respiratory, iron-acquisition, and PQQ support infrastructure that [[entities/flux-balance-analysis]] misses.
- [[concepts/microbiome-ecotype-portability]]: Four microbiome ecotypes reproduce published gut structure and separate disease from healthy samples, but projection and classifier performance are sensitive to classifier mismatch and cohort-axis leakage. Pseudo-count LDA is more robust than CLR/PCA-based GMM across taxonomic namespaces; cross-cohort ARI is a better K-selection criterion than monotonic perplexity or BIC.
- [[concepts/evidence-triangulation]] and [[concepts/multi-omics-integration]]: Strong biological claims should converge across analytical granularities and independent substrates. Examples combine pathway statistics, ecology, phenotype, metabolomics, BGC content, strain-level tests, and literature. Multi-line convergence is more reliable than any single statistical result.
- [[concepts/shared-stress-biology]], [[concepts/method-concordance]], and [[concepts/phylogenetic-confounding]]: Relative-abundance feature spaces can be comparatively portable across cohorts, whereas absolute-intensity metabolomics requires explicit batch correction. Pathway capacity and metabolite pools measure different biological quantities, so opposite directions are not necessarily contradictory. Taxonomic stratification can create feature leakage and false within-group associations.
- [[concepts/adversarial-methodological-review]]: Standard review is useful for surface and documentation issues but systematically misses structural inferential problems such as leakage, missing null distributions, incorrect sample-size claims, and verdict rules that treat non-significance as support. High-stakes projects should pair standard review with explicit adversarial review at both plan and notebook scope.
- [[concepts/phylogenetic-confounding]]: Habitat and phenotype signals frequently reflect lineage composition. Corrected analyses show that apparent subsurface anaerobic-toolkit enrichment can disappear within phylum, BacDive metal-tolerance phenotypes add no predictive value beyond taxonomy, and phylogeny often dominates environment in gene-content analyses.
- [[concepts/genome-ecology-validation]] and [[concepts/environmental-metal-tolerance]]: Independent validation supports genomic predictions: metal-tolerance scores predict isolation from contaminated environments, community-weighted amino-acid pathway completeness tracks soil metabolite pools in Black Queen Hypothesis-consistent directions, and plant compartment strongly structures microbial functional profiles.

## Selected biological findings

### Gene acquisition and clade structure

The [[concepts/pangenome-integration]] analysis shows that acquisition-depth ratios can serve as function-class signatures, independently of pre-registered hypothesis testing. Family-level averages can conceal strong within-clade heterogeneity: Mycobacteriaceae mycolic-acid effects sharpen when restricted to the mycolic-positive subclade, where producer-side Cohen's d rises from 0.309 at family rank to 0.394.

Three-substrate validation of atlas findings combines Sankoff-derived effect sizes, biome enrichment, and BacDive phenotype anchors. This framework is recommended as a minimum publication standard for comparative-genomics innovation claims.

### Microbiome targeting and IBD analysis

The IBD phage-targeting project found that its original 33-species Tier-A list collapsed to three independently supported candidates after correcting feature leakage, non-independent stratification, and decision-logic errors: *Mediterraneibacter gnavus*, *Flavonifractor plautii*, and *Blautia wexlerae*. The apparent resolution of the *Clostridioides scindens* paradox was invalid; independent within-substudy analysis instead supports genuine CD enrichment.

The four-ecotype framework is biologically interpretable, with E0 diverse commensal and E2 *Prevotella copri* communities enriched in healthy samples, and E1 Bacteroides2 and E3 severe Bacteroides-expanded communities distributed across disease states. However, clinical classifier utility must be tested on cohorts where disease status is held constant, and cross-cohort metabolomics must correct batch effects before clustering.

Pathway category schemas materially change conclusions. Regex-based pathway names produced a degenerate negative test, while MetaCyc's curator-validated hierarchy identified iron/heme acquisition as the dominant CD-up theme. Structurally degenerate results should trigger schema repair rather than scientific closure.

### AMR, defense, and dark genes

AMR composition varies strongly by environment: efflux dominates human-gut AMR, metal resistance dominates soil and aquatic contexts, and clinical species carry more accessory AMR. Across 25 bacteria, AMR knockouts show a universal pooled fitness shift of +0.086, while acquisition history—not fitness cost—largely determines core versus accessory status.

Within species, 51.3% of AMR occurrences are rare, and resistance islands occur in 54% of species with a mean of 6.2 genes. Acquired AMR tracks phylogeny more strongly than intrinsic AMR, suggesting stable maintenance and vertical inheritance after acquisition.

The SNIPE antiphage defense system occurs in 1,696 species across 33 phyla, with 86.7% of genes accessory or singleton. Its nuclease is PF13455/Mug113 rather than canonical PF01541 GIY-YIG. A complete two-domain SNIPE protein with fitness data occurs in *Methanococcus maripaludis*, and Klebsiella carries both SNIPE and ManYZ-related annotations.

### Plant and environmental microbiology

Plant-associated bacteria are often dual-nature rather than simply beneficial or pathogenic: 60–85% carry both PGP and pathogenic markers. Plant compartment explains 53% of functional-profile variance, with roots most specialized. ACC deaminase (*acdS*) is strongly root-enriched, with odds ratio 69.3, while co-occurring genera show redundancy rather than complementarity.

In contrast to the HGT-rich singleton pattern for some plant markers, the pqqC–acdS module is strongly soil-enriched, co-occurs at OR 7.24, and is predominantly core. Nitrogen fixation forms a separate ecological guild, and the tryptophan-to-*ipdC* relationship reverses in soil-associated species.

The ENIGMA SSO study demonstrates meter-scale contamination-plume mapping through 16S community similarity, including a *Rhodanobacter* denitrification hotspot and strong *Candidatus Nitrosotalea*–*Sideroxydans* coupling (rho = +0.95). The key validation limitation is that 221 registered geochemistry samples have no linked analytical measurements in BERDL.

### Metabolism and ecological function

The Black Queen Hypothesis is detectable at community scale: 11 of 13 amino-acid pathways trend in the predicted direction, with leucine and arginine reaching FDR significance. Leucine remains significant after soil-only and study-blocked analyses, although 95% of samples come from one study and metabolite annotation is only approximately 2% KEGG-linked.

For [[entities/pseudomonas-fluorescens-fw300-n2e3]], four-database evidence supports tryptophan overflow or cross-feeding rather than tryptophan catabolism. However, the reported 94% concordance is structurally inflated because [[entities/fitness-browser]] and [[entities/gapmind]] comparisons are inherently aligned; [[entities/bacdive]] is the only informative component.

In CF formulation design, metabolic overlap explains 27.4% of PA14 inhibition, but the strongest commensal inhibitors exceed overlap-based predictions, implying direct antagonism in addition to resource competition. PA14 outgrows commensals on all tested amino acids, so effective formulations require multi-organism niche coverage. Sugar alcohols and plant-derived sugars are candidate prebiotics, and *Rothia dentocariosa* and *Neisseria mucosa* show respiratory-source enrichment.

## Methodological and data-engineering lessons

- Use live, access-aware BERDL discovery helpers rather than historical catalog snapshots; important omitted resources included MGnify, PhageFoundry collections, InterPro, PubMed, and additional pangenome databases.
- For large local data marts, `lineage.yaml`, `schema_overview.yaml`, per-table dictionaries, and explicit pending-data codes make provenance and missingness agent-readable.
- Validate text-based gene identification. A false NDH-2 compensation result arose from misidentified Complex I subunits, and corrected analysis reversed the apparent effect.
- Calibrate enrichment thresholds to annotation granularity: PFam domains support module-level enrichment, whereas KEGG KOs are often too fine-grained.
- Avoid large broadcast joins against the 2.5-billion-row UniProt identifier table; disable Spark automatic broadcasting and force sort-merge joins.
- Run large Spark queries interactively and cache outputs before `nbconvert`; direct execution can cause dead kernels.
- Treat precomputed reference tables as starting points requiring verification, especially where taxonomy, strain content, or compositionality may create artifacts.
- Keep strict and relaxed feature-construction modes independent. In the ENIGMA contamination analysis, 71.7% of genus-feature pairs differed between modes.
- Explicitly distinguish production from consumption in [[entities/web-of-microbes]]: action `E` means de novo emergence, `I` means increased abundance, and the 2018 snapshot records production but no organism-level decrease action.

## Tensions and unresolved interpretations

- Core and accessory genes show different associations across projects: core genes are linked to essentiality, condition-specific fitness, and functional coherence, while other analyses emphasize accessory genes as ecological innovation and mobile defense carriers. The likely resolution is function- and condition-specific rather than a universal core/accessory rule.
- [[concepts/phylogenetic-confounding]] usually dominates species gene-content/environment associations, but niche breadth strongly predicts pathway diversity and environmental signals can be detected after appropriate stratification. Clinical sampling bias does not explain the weak ecotype environment signal.
- [[concepts/subsurface-microbial-specialization]]: Patescibacteria/CPR streamlining does not generalize to cultivable subsurface Bacillota_B, where deep-clay isolates have larger genomes and more ortholog groups than soil controls.
- [[concepts/cultivation-bias]]: Classical BacDive phenotypes correlate with metal tolerance but add no predictive power after taxonomy, whereas genome-based resistance counts perform strongly. The phenotype signal is therefore primarily phylogenetic.

## Open directions

1. Recompute clade-level innovation findings routinely with leaf-consistency and subclade-restricted models to separate population mixtures from genuine family-wide effects.
2. Build a reusable three-substrate validation pipeline joining atlas effect sizes, biome metadata, and phenotype databases with explicit coverage reporting.
3. Reanalyze IBD targeting using functional-feature ecotypes or within-substudy diagnosis contrasts, with independent candidate validation before intervention design.
4. Establish batch-correction and held-out-cohort standards for cross-cohort metabolomics and clinical classifiers.
5. Expand geochemistry ingestion for the SSO campaign so the 16S plume model can be tested against measured redox and metal gradients.
6. Experimentally test the pqqC–acdS module's vertical inheritance and root-associated function, including whether its apparent core status varies by taxonomic lineage.
7. Characterize orphan essential and truly dark genes using cross-organism module transfer, targeted genetics, and environmental-condition fitness assays.
8. Resolve whether costly conserved genes reflect selection in unrepresented natural environments by combining laboratory fitness with environmental abundance and metatranscriptomic data.

## Related Concepts
- [[concepts/gene-co-inheritance]]
- [[concepts/metabolic-competitive-exclusion]]
- [[concepts/phenotypic-landscape]]
- [[concepts/organism-specificity]]
- [[concepts/phylogenetic-amr-structure]]
- [[concepts/compensatory-evolution]]
- [[concepts/prevalence-ceiling]]
- [[concepts/structural-novelty]]

## Entities
- [[entities/amrfinderplus]]
- [[entities/average-nucleotide-identity]]
- [[entities/der-simonian-laird-random-effects-meta-analysis]]
- [[entities/diamond]]
- [[entities/escherichia-coli]]
- [[entities/flagellar-motility]]
- [[entities/iron]]
- [[entities/kbase-ke-pangenome]]
- [[entities/kegg]]
- [[entities/klebsiella-pneumoniae]]
- [[entities/mycobacterium-tuberculosis]]
- [[entities/pqq-biosynthesis]]
- [[entities/pqq]]
- [[entities/proteomics]]
- [[entities/protocatechuate-3-4-dioxygenase]]
- [[entities/quinate-aromatic-degradation]]
- [[entities/salmonella-enterica]]
- [[entities/tryptophan-biosynthesis]]
