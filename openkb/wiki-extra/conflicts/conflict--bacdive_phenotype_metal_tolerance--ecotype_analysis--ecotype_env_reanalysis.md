<!-- tension-hash: cab12c7b1f6f97ab -->
# Mechanistic Trait Signals vs. Phylogenetic Confounding in Metal Tolerance and Ecotype

Several trait-environment associations in bacterial metal tolerance and lifestyle ecotypes have plausible mechanistic stories, but the statistical evidence for those stories keeps collapsing once phylogeny is properly accounted for. This is a recurring, unresolved tension: does the data support environment- or trait-driven adaptation, or is nearly everything explained by lineage structure (Proteobacteria vs. Actinomycetes, clinical vs. environmental sampling)? Because these traits (metal tolerance, ecological lifestyle) are often cited as evidence of adaptive evolution, getting this right matters for how confidently such claims can be made. See [[concepts/phylogenetic-confounding]].

## Evidence Sides

**For mechanistic/environmental signal:**
- The Gram-negative outer membrane can restrict metal-cation uptake, offering a plausible mechanism for the observed Gram-negative association. [src: bacdive_phenotype_metal_tolerance]
- Urease requires nickel handling, a plausible mechanistic link to nickel-specific tolerance. [src: bacdive_phenotype_metal_tolerance]
- Environment dominated in 39.5% of species in the original ecotype analysis, a substantial minority suggesting real environmental influence. [src: ecotype_analysis]
- The AlphaEarth subset is clinically skewed, which could in principle produce or mask an environment effect through sampling imbalance. [src: ecotype_env_reanalysis]

**For phylogenetic confounding / no statistical support:**
- The class-stratified analysis cannot separate the Gram-negative mechanism from broad Proteobacteria-versus-Actinomycetes lineage differences. [src: bacdive_phenotype_metal_tolerance]
- The urease-nickel association was negative at the aggregate level and absent within the tested non-Actinomycete classes. [src: bacdive_phenotype_metal_tolerance]
- Phylogeny dominated in most species in the original analysis. [src: ecotype_analysis]
- Neither the original comparison (p=0.66) nor the genome-level reanalysis (p=0.83) found a significant lifestyle difference. [src: ecotype_analysis, ecotype_env_reanalysis]
- The environmental group did not show the predicted stronger signal even after harmonized genome-level classification, so sampling bias is not supported as the principal explanation for the weak environment effect. [src: ecotype_env_reanalysis]

## Possible Reconciliations

- **Hypothesis: mixed-mechanism traits.** Metal tolerance may be genuinely mechanistic for some metals (nickel via urease) but phylogenetically inherited as a package for others (broad Gram-negative membrane effects), so a single class-level test conflates two different processes.
- **Hypothesis: minority-environment subgroup exists but is diluted.** The 39.5% of species where environment dominates could reflect a real but taxonomically localized effect that a whole-dataset significance test (p=0.66/0.83) is underpowered to detect.
- **Hypothesis: sampling bias is a real but secondary confound.** Clinical skew may distort effect *size* estimates without being large enough to flip overall significance, explaining why correcting for it did not change the conclusion.

## Resolving Work

- Re-run metal-tolerance associations per-metal and within matched sister-lineage pairs (e.g., matched Proteobacteria vs. Actinomycetes clades) rather than composite scores across diverse species. [src: bacdive_phenotype_metal_tolerance]
- Test whether the 39.5% environment-dominated species cluster within specific clades, using a phylogenetically-stratified subgroup significance test rather than a single global p-value. [src: ecotype_analysis]
- Directly compare effect sizes (not just p-values) between the original and genome-level reanalysis to see if clinical-sampling correction shifted magnitude even without shifting significance. [src: ecotype_env_reanalysis]
- Obtain independent, non-clinical environmental genome collections to test the ecotype effect outside the AlphaEarth-skewed subset.
- Conduct phylogenetically-controlled (e.g., phylogenetic logistic regression) tests for both urease-nickel and Gram-negative-metal associations to quantify how much of each signal survives lineage correction.
