<!-- tension-hash: 3c830ee370ee5c2a -->
# Model-Predicted Flux vs. Phenotype-Observed Essentiality in ADP1 Complex I

The [[concepts/aromatic-catabolism-network]] project reports a disagreement between two evidence streams for the same biological question: does Complex I matter for aromatic catabolism in ADP1? Flux balance analysis (FBA) sees elevated flux through Complex I but calls it non-essential, while growth-phenotype screens see strong, condition-specific fitness defects across most of the operon. The tension matters because it bears on whether flux magnitude — a purely model-internal quantity — can be used as a proxy for genetic necessity, or whether the two measurements are answering different questions entirely.

## Evidence Sides

**Model-visible evidence (FBA)**
FBA detected increased Complex I flux under the relevant condition but predicted no essentiality for the corresponding genes. [src: aromatic_catabolism_network]

**Phenotype-visible evidence (growth screens)**
Growth phenotyping identified 21 Complex I–associated genes, and 10 of 13 core operon subunits produced quinate-specific growth defects. [src: aromatic_catabolism_network]

A qualifying third data point complicates a simple "aromatic-specific" reading of the phenotype side: cross-species data show Complex I orthologs with stronger defects on aromatic conditions overall, but acetate and succinate produced larger per-condition defects than some aromatic conditions — evidence favoring a high-NADH-flux explanation over strict aromatic specificity. [src: aromatic_catabolism_network]

## Possible Reconciliations

- **Different axes, not contradictory measurements (hypothesis):** flux demand and condition-dependent essentiality may simply be non-interchangeable properties — a reaction can carry high flux without being non-redundant, if alternative routes or buffering capacity exist that FBA's stoichiometric constraints do not penalize but real growth conditions do.
- **Redox-demand generalization (hypothesis):** the phenotypic defects may reflect general high-NADH-flux stress rather than an aromatic-pathway-specific requirement, since acetate and succinate — non-aromatic, NADH-generating substrates — show comparably large defects. If so, "quinate-specific" defects would really be "high-flux-condition" defects, softening the apparent FBA/phenotype conflict to a labeling issue.
- **Model incompleteness (hypothesis):** FBA's steady-state, condition-averaged framing may not encode the same environmental or regulatory constraints active during quinate growth, so it is not that FBA is "wrong" but that it is answering a static optimality question, not a dynamic fitness question.

## Resolving Work

- Run direct single-organism growth-defect assays on matched aromatic vs. non-aromatic (acetate, succinate) substrates to separate NADH-flux effects from aromatic-pathway-specific effects.
- Re-run FBA with condition-specific enzyme-capacity or regulatory constraints for quinate growth and check whether essentiality predictions shift toward the phenotype data.
- Pair transcriptomic/proteomic profiling under quinate growth with the 13 core operon subunits to test whether upregulation, not just flux, tracks with the observed defects.
- Extend cross-species phenotype screens to more NADH-generating conditions to test whether the "aromatic-specific" defect pattern holds or dissolves into a general high-flux-defect pattern.
