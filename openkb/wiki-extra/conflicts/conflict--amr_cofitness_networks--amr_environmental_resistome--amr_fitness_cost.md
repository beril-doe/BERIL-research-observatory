<!-- tension-hash: 01eb4eb0a53a1ffb -->
# Organism-Specific Cofitness Networks: Regulatory Architecture or Shared Lab-Condition Response?

Cofitness neighborhoods computed from Fitness Browser data show strong organism-specific structure, but it is unclear whether this structure reflects genuine species-level regulatory wiring or is instead an artifact of shared experimental conditions and recurring dispensable functions across the growth conditions tested. Because cofitness networks are widely used to infer functional relationships and regulatory architecture, resolving this determines whether organism-specific patterns can be trusted as biological signal or must first be corrected for condition-driven bias. See [[concepts/organism-specificity]].

## Evidence Sides

**Organism-level regulatory organization**
- The relative Jaccard result supports organism-level organization of cofitness neighborhoods. [src: amr_cofitness_networks]
- The complete support-function profile is more similar within organisms across mechanisms than across organisms for the same mechanism, indicating organism-specific combinations of transport, signaling, and transcriptional regulation. [src: amr_cofitness_networks]

**Shared response to laboratory conditions**
- Recurring categories such as flagellar motility and amino-acid biosynthesis may reflect common dispensability under Fitness Browser conditions rather than organism-specific regulation. [src: amr_cofitness_networks]
- Transport, signaling, and transcription regulation recur broadly across organisms, suggesting a conserved functional backbone rather than organism-unique architecture. [src: amr_cofitness_networks]

## Possible Reconciliations

- **Layered signal hypothesis**: broad functional categories (motility, amino-acid biosynthesis, transport) may be conserved because they are commonly dispensable under standard growth conditions, while the *specific gene combinations and neighborhood partners* within those categories are organism-specific — meaning both claims are compatible at different levels of resolution.
- **Condition-coverage hypothesis**: the Fitness Browser's condition set may itself be non-representative, so recurring categories reflect the conditions sampled rather than universal biology; testing under a broader or organism-tailored condition panel could shift which categories appear conserved.
- **Metric-sensitivity hypothesis**: relative Jaccard similarity and profile-similarity comparisons may be differentially sensitive to shared "background" genes versus organism-specific "edge" genes, so the two results could be measuring different aspects of the same network rather than contradicting each other.

## Resolving Work

- Recompute cofitness neighborhoods after stratifying or reweighting by condition type to test whether recurring categories (motility, amino-acid biosynthesis) persist when condition composition is controlled or expanded.
- Compare cofitness architecture for the same organism across independent condition panels (e.g., Fitness Browser vs. an alternative dataset) to see whether organism-specific structure is stable or condition-dependent.
- Decompose the relative Jaccard and profile-similarity metrics gene-by-gene to identify which genes drive organism-level clustering versus which drive cross-organism conservation.
- Directly test whether flagellar motility and amino-acid biosynthesis genes show uniformly high dispensability across all sampled conditions, which would support the shared-response explanation over regulatory specificity.
- Extend the analysis to additional organisms with denser condition sampling to determine whether the organism-specificity signal scales with the number of conditions tested, which would indicate a sampling artifact rather than true architecture.
