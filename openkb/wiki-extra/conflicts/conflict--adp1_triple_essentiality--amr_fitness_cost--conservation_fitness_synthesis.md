<!-- tension-hash: d4cbe93c487163b5 -->
# Core Genome Conservation Versus Fitness Importance: A Two-Way Mismatch

A recurring tension in [[concepts/gene-essentiality]] research is whether evolutionary conservation — membership in the core genome, shared across most or all strains/organisms in a family — is a reliable proxy for a gene's functional importance (essentiality, low fitness cost, freedom from burden). Some data support a tight link between conservation and importance; other data show large, systematic exceptions in both directions. The disagreement matters because comparative genomics routinely uses "core" as shorthand for "essential" or "important," and the exceptions are numerous enough to question that shorthand.

## Evidence Sides

**Conservation tracks importance**
- 859 gene families were essential in every organism where the family had members, and most fitness modules were core-rich. [src: essential_genome, module_conservation]

**Conservation and essentiality frequently diverge**
- Only 15 families were essential in all 48 organisms sampled, a far smaller number than the 859 essential-when-present. [src: essential_genome]
- The pangenome-linked analysis identified 3,683 essential-auxiliary genes and 1,259 essential-unmapped genes; the pan-bacterial analysis found 7,084 orphan essentials with only 49.5% core representation. [src: conservation_vs_fitness, essential_genome]
- Core genes were more conserved yet also more likely to be burdensome, beneficial when deleted, or condition-specific in laboratory assays. [src: conservation_fitness_synthesis, conservation_vs_fitness, fitness_effects_conservation]
- Core genes were more burdensome in Protein Metabolism, Motility, and RNA Metabolism, but non-core Cell Wall genes were more burdensome. [src: core_gene_tradeoffs]
- 38 module families were below 50% core, and family breadth did not predict conservation. [src: module_conservation]

## Possible Reconciliations

- **Denominator hypothesis**: "essential in every organism where present" (859) and "essential across all 48 organisms" (15) use different conditioning sets — presence-conditional essentiality versus universal presence — so the gap is definitional rather than contradictory. [src: essential_genome]
- **Function-specific hypothesis**: core-burden associations are not uniform; they run in opposite directions across functional categories, so pooled "core = costly" or "core = important" claims mask real heterogeneity. [src: core_gene_tradeoffs]
- **Unrepresented-environment hypothesis**: core genes that look burdensome or dispensable in lab conditions may carry selected benefits in natural environments not captured by laboratory fitness assays. [src: conservation_fitness_synthesis, conservation_vs_fitness, fitness_effects_conservation]
- **Missed-homology hypothesis**: orphan and essential-unmapped genes may reflect detection limits of homology search rather than genuine lineage-specific novelty. [src: conservation_vs_fitness, essential_genome]

## Resolving Work

- Re-search the 7,084 orphan essential genes with remote-homology/structure-based methods to partition true lineage-specificity from missed detection. [conservation_vs_fitness, essential_genome]
- Measure fitness of "burdensome" core genes across ecologically realistic, non-laboratory conditions to test the unrepresented-environment hypothesis directly. [conservation_fitness_synthesis]
- Recompute essentiality-conservation correlations using matched denominators (presence-conditional vs. whole-panel) to see whether the 15-vs-859 gap disappears under a common definition. [essential_genome]
- Stratify module-conservation and gene-burden statistics by functional category across datasets to test whether the core-importance link is function-dependent rather than universal. [core_gene_tradeoffs, module_conservation]
