<!-- tension-hash: ba3d05718d9f96c9 -->
# Does Geographic Context Predict Genome Content, or Just Genome Location?

Two independent analyses on [[concepts/genome-ecology-validation]] disagree about how strongly a genome's geographic/environmental embedding relates to its gene content. One finds a clear, quantified geographic signal that differs by lifestyle; the other finds no detectable link between that same kind of environmental context and gene-content partial correlations. The disagreement matters because it bears on whether spatial/environmental embeddings (like AlphaEarth) can be used as proxies for predicting accessory-genome adaptation, or whether they capture something ecologically real but functionally orthogonal to gene content.

## Evidence Sides

**Side A — Geographic embeddings show a strong, lifestyle-dependent gradient**
AlphaEarth embeddings show a stronger geographic gradient for environmental samples than for human-associated samples, with ratios of 3.4x and 2.0x, respectively. [src: env_embedding_explorer]

**Side B — No detectable link between environmental context and gene content**
Ecotype analysis found no significant difference in environment–gene-content partial correlations between environmental and human-associated species. [src: ecotype_env_reanalysis]

## Possible Reconciliations

- **Hypothesis (different targets):** AlphaEarth's geographic gradient measures where genomes are sampled (spatial embedding of isolation sites), while the ecotype analysis measures whether environmental variables statistically explain gene-content variation — these are related but distinct quantities, so a strong signal in one need not imply a strong signal in the other. [src: env_embedding_explorer, ecotype_env_reanalysis]
- **Hypothesis (scale/specificity mismatch):** Spatial structure may be biologically real (genomes cluster geographically) without being specific enough, or aligned with the right timescale, to predict accessory-gene turnover, which may respond to more local or transient selective pressures than broad geographic embedding captures. [src: env_embedding_explorer, ecotype_env_reanalysis]
- **Hypothesis (statistical power/partial correlation design):** The partial-correlation approach in the ecotype analysis may control away shared variance that the raw geographic-gradient ratio in the embedding analysis does not, masking a real but confounded association.

## Resolving Work

- Re-run the ecotype partial-correlation analysis using the same AlphaEarth embedding features and gradient definitions used in the 3.4x/2.0x comparison, to test whether measurement choice alone explains the discrepancy.
- Decompose gene content into core versus accessory components and test each separately against geographic embedding, since accessory content is the more plausible carrier of local adaptation.
- Stratify both analyses by taxonomic resolution (species vs. lineage) to check whether phylogenetic signal is confounding the geographic gradient in Side A but is properly controlled in Side B.
- Directly test whether the environmental-vs-human-associated gradient ratio (3.4x/2.0x) predicts any specific functional gene categories (e.g., metal tolerance, secondary metabolism) rather than whole-genome content, to see if a narrower gene-content signal exists.
- Compare sampling density and geographic spread between the two datasets to rule out an artifact where one dataset simply has more resolving power to detect small effects.
