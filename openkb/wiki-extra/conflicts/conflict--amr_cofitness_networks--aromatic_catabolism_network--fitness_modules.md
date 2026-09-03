<!-- tension-hash: f5a0100001aaf6d3 -->
# Cofitness Signal: Functional Coupling or Shared Dispensability?

Across several fitness-based network studies, high cofitness between genes is used to infer shared function, regulation, or biochemical pathways. But the underlying statistics leave open whether correlated fitness patterns reflect genuine mechanistic coupling (co-regulation, shared complexes, shared metabolic flux) or merely convergent, independent responses to condition-dependent dispensability. This matters because cofitness networks are widely used to assign gene function, and the two interpretations lead to very different confidence levels for any specific claim.

## Evidence Sides

**Functional/mechanistic coupling side**
AMR genes cofitness-cluster with motility, signaling, and biosynthetic programs in ways compatible with shared regulation or resource allocation, including possible competition for proton-motive force between efflux and flagellar systems. [src: amr_cofitness_networks] In ADP1, Complex I orthologs show significantly worse fitness on aromatic than non-aromatic conditions (means −1.35 vs −0.77, Mann–Whitney p < 0.0001), and very high cofitness successfully identifies a shared functional subsystem. [src: aromatic_catabolism_network] Pan-bacterial ICA modules show robust cofitness structure, with 94.2% of modules showing significant cofitness enrichment. [src: fitness_modules] The organism-specificity comparison strengthens this side because it depends only on relative network similarity, not on interpreting individual categories. [src: amr_cofitness_networks]

**Shared-dispensability/indirect-coupling side**
[[concepts/shared-dispensability]] proposes that AMR genes are often dispensable without antibiotics, flagella are less useful in shaken culture, and amino-acid biosynthesis is redundant in supplemented media — so similar condition-dependent fitness, not co-regulation, could produce the observed cofitness. [src: amr_cofitness_networks] The permutation test matched conservation class but not mean fitness level, so it cannot rule out that enrichment is a generic feature of slightly positive-fitness genes rather than AMR-specific. [src: amr_cofitness_networks] In ADP1, 11 Complex I-associated assignments beyond the core nuo operon rest on cofitness alone and may be indirect. [src: aromatic_catabolism_network] The strongest ADP1 fitness defects occur on non-aromatic, high-NADH substrates acetate (−1.55) and succinate (−1.39), undermining a purely aromatic-pathway interpretation and pointing instead to [[concepts/nadh-flux-respiratory-constraints|NADH-flux respiratory constraints]]. [src: aromatic_catabolism_network] Pan-bacterial ICA modules achieve below-1% strict precision for exact KEGG KO prediction despite high cofitness enrichment. [src: fitness_modules]

## Possible Reconciliations

- **Hypothesis (mechanism heterogeneity):** cofitness networks may contain a mixture of true co-regulated pairs and dispensability-driven pairs; the aggregate statistics (94.2% enrichment, <1% precision) average over both classes rather than contradicting each other. [src: fitness_modules]
- **Hypothesis (correlated but non-causal axis):** genes could share an underlying physiological axis (e.g., NADH flux, growth-rate dependence) without direct co-regulation, explaining both the ADP1 aromatic/non-aromatic pattern and the AMR/motility overlap. [src: aromatic_catabolism_network][src: amr_cofitness_networks]
- **Hypothesis (statistical baseline gap):** because the permutation test controls conservation but not mean fitness, some "AMR-specific" enrichment may actually be a general positive-fitness-gene effect, which would reconcile strong correlation with weak specific mechanism. [src: amr_cofitness_networks]

## Resolving Work

- Rerun the AMR permutation test controlling for mean fitness level, not just conservation class, to test whether enrichment is AMR-specific. [src: amr_cofitness_networks]
- Use pairwise-complete correlations instead of zero-filled z-scores to check whether missing-data handling inflates cofitness estimates. [src: amr_cofitness_networks]
- Directly test the 11 non-operon Complex I assignments in ADP1 with targeted genetic epistasis or protein-interaction assays to distinguish direct complex membership from indirect metabolic coupling. [src: aromatic_catabolism_network]
- Compare fitness profiles across a wider NADH-flux gradient beyond acetate/succinate/aromatics to isolate whether Complex I fitness defects track aromaticity or NADH load specifically. [src: aromatic_catabolism_network]
- Cross-validate pan-bacterial ICA modules against orthogonal functional data (operon structure, protein complexes) to see whether the 94.2% enrichment sits mostly among the correctly predicted KOs or the majority that miss strict precision. [src: fitness_modules]
