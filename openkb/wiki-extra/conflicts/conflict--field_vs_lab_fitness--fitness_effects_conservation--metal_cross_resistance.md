<!-- tension-hash: 35eac44982fad029 -->
# Does Ecological Relevance Drive Gene Conservation, or Is Conservation Indifferent to Field Activity?

A recurring question across the fitness-conservation literature is whether genes that matter in field/ecological conditions are more evolutionarily conserved than genes that matter only in lab conditions. Several independent analyses converge on the general link between fitness importance and conservation, but disagree sharply on whether *ecological/field* specificity adds anything beyond that general importance signal — and the metal-stress data show this disagreement playing out concretely, with conservation values for "metal-important" genes ranging from below baseline to well above it depending on scope. This matters because it determines whether conservation should be read as a proxy for ecological relevance or as a more generic marker of functional integration.

## Evidence Sides

**Side A — Field/ecological importance is linked to conservation**
- Field-stress and field-core genes are significantly conserved in condition-class analysis. [src: field_vs_lab_fitness]
- Core genes are more likely to be essential, reinforcing a general importance–conservation relationship. [src: fitness_effects_conservation]
- The pan-bacterial atlas found the full set of metal-important genes to be 87.4% core and above baseline. [src: metal_fitness_atlas]
- Narrowly metal-specific genes are 88.0% core by organism mean. [src: metal_specificity]
- Metal fitness correlations were nearly all positive (e.g., Fe–Zn r = 0.61, Co–Ni r = 0.56, Al–Co r = 0.30), suggesting shared stress biology. [src: metal_cross_resistance]

**Side B — Field/ecological specificity adds nothing beyond general importance, or even weakens the relationship**
- Field-specific genes were not significantly more conserved than lab-specific genes. [src: field_vs_lab_fitness]
- Module-level analysis found no significant relationship between field activity and conservation, despite identifying highly conserved ecological modules and low-conservation lab modules. [src: field_vs_lab_fitness]
- Module-family breadth is unrelated to core fraction (rho = -0.01, p = 0.914). [src: module_conservation]
- The *D. vulgaris* heavy-metal condition-specific set was only 71.2% core and below baseline. [src: field_vs_lab_fitness, metal_fitness_atlas]
- Core genes are also more likely to show beneficial deletion effects and strong condition-specific phenotypes, complicating a simple "core = important" story. [src: fitness_effects_conservation]

## Possible Reconciliations

- **Scope-dependence hypothesis**: organism-specific condition sets (D. vulgaris) versus pan-bacterial aggregate sets (metal atlas) measure different functional tiers, so 71.2% vs. 87.4% core reflect different populations of genes, not a contradiction. [src: field_vs_lab_fitness, metal_fitness_atlas]
- **Specificity-tier hypothesis**: narrowly specific genes, general "sick" genes, and broadly important genes occupy distinct conservation bands, as suggested by the 88.0% figure being high but "less core-enriched than general sick genes." [src: metal_specificity]
- **Definitional hypothesis**: "field activity" at the module level may not equal "field activity" at the gene/condition-class level, explaining why one analysis finds significance and the other does not. [src: field_vs_lab_fitness]
- **Multi-causal hypothesis**: conservation may be driven by functional integration, stress biology, module architecture, and phylogenetic/genomic dynamics simultaneously, making any single ecological-relevance test underpowered. [src: fitness_effects_conservation, module_conservation, metal_cross_resistance]

## Resolving Work

- Re-run field-vs-lab conservation tests with matched organism scope (single-organism vs. pan-bacterial) to isolate scope effects on the 71.2%/87.4% discrepancy.
- Directly compare core-fraction distributions across the three specificity tiers (narrow metal-specific, general sick, broad core) with formal statistical tests rather than descriptive percentages.
- Test whether module-level "field activity" and gene-level "field-specific" labels are measuring the same construct, using a shared operational definition across [[concepts/field-vs-lab-fitness]] and [[concepts/module-conservation]].
- Decompose the Fe–Zn/Co–Ni/Al–Co correlation spread to determine whether variable magnitude tracks chemistry, phylogeny, or measurement noise, informing [[concepts/metal-cross-resistance]].
- Model conservation jointly against essentiality, deletion-effect sign, and condition-specificity to separate general importance from ecological specificity per [[concepts/fitness-effects-conservation]].
