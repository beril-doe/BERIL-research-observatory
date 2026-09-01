---
type: "Concept"
sources: ["summaries/respiratory_chain_wiring__REPORT.md", "summaries/plant_microbiome_ecotypes__REPORT.md", "summaries/ibd_phage_targeting__REPORT.md", "summaries/discoveries.md", "summaries/cf_formulation_design__REPORT.md"]
description: "Resource competition can suppress pathogens when communities exhaust their preferred nutrients."
---

# Metabolic Competitive Exclusion

## Definition

**Metabolic competitive exclusion** is the suppression of a pathogen by commensals that collectively consume the nutrients required for pathogen growth, thereby reducing the pathogen’s access to its ecological niche. In the CF airway formulation study, the target was *Pseudomonas aeruginosa* PA14, which preferentially grew on amino acids abundant in CF sputum. [src: cf_formulation_design]

This mechanism is related to [[concepts/rational-microbiome-formulation-design]], but it is narrower: it describes the ecological mechanism of resource depletion rather than the full optimization problem involving safety, engraftment, antagonism, and formulation size. [src: cf_formulation_design]

## Evidence from the CF formulation study

PA14 showed its strongest growth on proline (OD 0.60), histidine (0.56), ornithine (0.46), glutamate (0.40), aspartate (0.36), isoleucine (0.36), and arginine (0.35); glucose supported moderate growth (0.22), while threonine, methionine, cysteine, serine, and glycine supported essentially no growth below OD 0.07. [src: cf_formulation_design]

Across 142 isolates with both inhibition and carbon-utilization measurements, metabolic overlap with PA14 significantly predicted planktonic inhibition (r = 0.384, p = 2.3×10⁻⁶). A multivariate model using metabolic overlap, growth on PA-preferred substrates, metabolic breadth, and maximum growth explained R² = 0.274 of inhibition variance. [src: cf_formulation_design]

The predictive effect is weaker under validation: five-fold cross-validation produced CV R² = 0.145 ± 0.142. Thus, metabolic overlap is a statistically supported mechanism, but it is not sufficient to predict inhibition reliably for unseen isolates. [src: cf_formulation_design]

No individual commensal outgrew PA14 on every tested substrate; commensals exceeded PA14’s maximum growth rate in only 13.8% of substrate comparisons. However, commensals began growing before PA14 in 43.1% of comparisons, suggesting that initial biomass establishment may influence competition even when PA14 has the higher eventual growth rate. [src: cf_formulation_design]

## Community-level niche coverage

The study operationalized exclusion as coverage of PA14’s preferred carbon niche by a consortium. Under a strict safety filter, *Micrococcus luteus* + *Neisseria mucosa* + *Streptococcus salivarius* covered 100% of PA14’s preferred substrates, whereas the one- and two-member candidates covered 18%. [src: cf_formulation_design]

*M. luteus* was the key coverage specialist because it grew on 9 of PA14’s 11 preferred substrates, including proline, histidine, glutamate, aspartate, arginine, and glucose. Its contribution illustrates an emergent property of a community: no single organism needed to dominate PA14 on every substrate if different members collectively occupied the pathogen’s resource space. [src: cf_formulation_design]

The five-member formulation added *Rothia dentocariosa* and *Gemella sanguinis* to the three-member core and retained 100% niche coverage with 78% mean inhibition. However, *M. luteus* was absent from patient metagenomes and had zero lung genomes in the analyzed pangenome, creating a trade-off between metabolic coverage and likely airway persistence. [src: cf_formulation_design]

## Metabolism is not the whole mechanism

The study found that genus-level taxonomy increased the inhibition model’s training R² from 0.274 to 0.360, adding 8.6% explained variance beyond metabolic features. This result indicates that species- or genus-specific mechanisms contribute independently of resource overlap. [src: cf_formulation_design]

The strongest positive residuals included *S. salivarius* ASMA-737 (+74.1%), *G. sanguinis* ASMA-3044 (+62.2%), and *N. mucosa* ASMA-3643 (+57.2%), meaning their observed inhibition exceeded metabolic-model predictions. These isolates were interpreted as candidates for combined metabolic competition and direct antagonism, potentially involving bacteriocins, secreted enzymes, or contact-dependent mechanisms; the specific mechanisms were not established by the study. [src: cf_formulation_design]

Accordingly, metabolic competitive exclusion should be treated as one component of a [[concepts/multi-omics-integration]]-supported, multi-mechanism model rather than as a complete explanation of pathogen suppression. Approximately 73% of inhibition variance remained unexplained by the primary metabolic model, although this residual may include direct antagonism, biofilm behavior, pH, iron competition, quorum-sensing effects, and assay variation. [src: cf_formulation_design]

## Prebiotic implications

The tested substrates did not provide an individual commensal advantage: PA14 outgrew the average commensal on every tested substrate, and no amino acid or simple sugar produced a clear selective prebiotic effect. [src: cf_formulation_design]

The study therefore redirected the prebiotic strategy from competing with PA14 on amino acids to feeding commensals on substrates that PA14 cannot access. Comparative pathway analysis identified myoinositol, xylitol, xylose, arabinose, fucose, and rhamnose as candidate selective prebiotics because the relevant pathways were complete in one or more formulation species but absent or nearly absent in PA14. [src: cf_formulation_design]

This strategy exemplifies [[concepts/selective-prebiotics]], but the genomic predictions remain hypotheses until growth and competition are measured experimentally. The proposed validation panel includes all six substrates, tested with the five formulation species and PA14 under the same endpoint and kinetic conditions as the original assays. [src: cf_formulation_design]

## Robustness and boundary conditions

The formulation study used pangenome data to test whether metabolic capabilities were conserved across strains. At greater than 95% conservation, *M. luteus* retained 18/18 amino acid pathways, *S. salivarius* 18/18, *N. mucosa* 16/16, *R. dentocariosa* 14/18, and *G. sanguinis* 7/18. The results support species-level robustness for several candidates but also identify *G. sanguinis* as especially dependent on strain selection. [src: cf_formulation_design]

Across 1,796 lung-associated *P. aeruginosa* genomes, amino acid catabolic pathways were 97.4% conserved, including proline utilization in 97% of lung isolates. This suggests that the metabolic targets are stable across lung-associated PA diversity, although it does not demonstrate equivalent inhibition in vivo. [src: cf_formulation_design]

The main experimental boundary is that inhibition was measured against planktonic PA14. PA14 represents a minority of CF-associated virulence genotypes: 94% of CF genomes in the analysis were ExoS+ and 5% were ExoU+, while PA14 is ExoU+ and Pel-only. Amino acid pathway scores were nevertheless identical between ExoU+ and ExoS+ groups, supporting the hypothesis that the resource targets are independent of virulence genotype. [src: cf_formulation_design]

Biofilm structure, spatial refuges, diffusion gradients, and clinical-strain physiology could still alter the effectiveness of resource depletion. The study therefore treats confirmation against PAO1, mucoid clinical isolates, biofilm models, and animal models as necessary before concluding that planktonic metabolic exclusion translates to CF airways. [src: cf_formulation_design]

## Tensions

### Niche coverage versus engraftability

The k=3 formulation achieved 100% PA14 niche coverage, but its inferred engraftability score was 0.140 because it included *M. luteus*, which was not detected in patient metagenomes and had no lung genomes in the analyzed pangenome. [src: cf_formulation_design]

The k=2 formulation of *R. dentocariosa* + *N. mucosa* achieved only 18% niche coverage but had 84% mean inhibition and an engraftability score of 0.820. The report therefore recommends k=2 as the primary clinical candidate and k=3 as an aspirational candidate pending in vivo testing. [src: cf_formulation_design]

### Additivity versus interaction effects

Formulation scores assumed that member effects were additive, but the available RFU-based interaction data showed a mean synergy of −5.8%, with pairwise effects ranging from +5.3% to −19.8%. *N. mucosa* combinations were near-additive, whereas some other pairs were antagonistic. [src: cf_formulation_design]

Only 8 comparisons across 5 unique pairs were available, and the complete 10-pair matrix for the five-member core was not measured. Consequently, community-level exclusion cannot yet be inferred from single-isolate coverage alone. [src: cf_formulation_design]

## Open Directions

- Measure all 10 pairwise combinations of the five core species to test whether resource coverage remains effective after inter-member antagonism is included. [src: cf_formulation_design]
- Validate xylitol, myoinositol, xylose, arabinose, fucose, and rhamnose with growth curves and selectivity ratios for each formulation member and PA14. [src: cf_formulation_design]
- Compare k=2, k=3, and k=5 formulations in biofilm and chronic-lung models to determine whether niche coverage or airway engraftment better predicts suppression. [src: cf_formulation_design]
- Repeat inhibition and carbon-utilization assays against PAO1 and 3–5 mucoid clinical PA isolates to test whether conserved amino acid targets produce conserved phenotypic inhibition. [src: cf_formulation_design]
- Screen respiratory-associated Micrococcaceae and other lung-adapted organisms for a broad metabolic profile that could replace *M. luteus* without sacrificing engraftability. [src: cf_formulation_design]
- Use comparative genomics of high-residual and low-residual isolates within formulation species to identify direct-antagonism mechanisms that complement metabolic competition. [src: cf_formulation_design]

## Source

See [[summaries/cf_formulation_design__REPORT]] for the full study summary and supporting analyses.

See also: [[summaries/discoveries]]

See also: [[summaries/ibd_phage_targeting__REPORT]]

See also: [[summaries/plant_microbiome_ecotypes__REPORT]]

See also: [[summaries/respiratory_chain_wiring__REPORT]]