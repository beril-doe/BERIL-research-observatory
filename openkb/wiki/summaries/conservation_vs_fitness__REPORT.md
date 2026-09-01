---
type: "Summary"
description: "Links bacterial gene essentiality to pangenome conservation across 33 species."
doc_type: short
full_text: "sources/conservation_vs_fitness__REPORT.md"
---

# Conservation vs Fitness — Linking FB Genes to Pangenome Clusters

## Overview

This report links Fitness Browser (FB) gene-level fitness and essentiality data to KBase pangenome clusters using DIAMOND protein similarity. It tests how [[concepts/gene-essentiality]] relates to [[concepts/pangenome-integration]] across diverse bacteria, distinguishing essential genes found in core, auxiliary, or unmapped genomic compartments.

## Key Findings

- **Organism and gene mapping:** 44 of 48 FB organisms mapped to pangenome species clades. The final link table contains **177,863 gene-to-cluster links**, with 100.0% median protein identity and 94.2% median gene coverage.
- **Downstream dataset:** 33 organisms met the coverage requirements for analysis. Dyella79 was excluded because of a locus-tag mismatch, while 10 organisms were excluded for less than 90% DIAMOND coverage.
- **Conservation structure:** Of the linked genes, **145,821 (82.0%)** were core and **32,042 (18.0%)** were auxiliary; 7,574 auxiliary genes were singletons. Four organisms—Cola, Kang, Magneto, and SB2B—were unmatched because their species had too few GTDB genomes for pangenome construction.
- **Essentiality enrichment:** The analysis identified **27,693 putative essential genes**, representing 18.6% of 148,826 protein-coding genes across the 33 analyzed organisms. Essential genes were 86.1% core, compared with 81.2% of non-essential genes, with a median odds ratio of **1.56**. Eighteen of 33 organisms showed significant enrichment by Fisher’s exact test after BH-FDR correction (q < 0.05).
- **Strongest organism-level signals:** *Methanococcus maripaludis* S2 had OR=5.21, *Ralstonia syzygii* PSI07 had OR=3.41, and *Marinobacter adhaerens* had OR=3.08.

## Functional Differences by Conservation Category

Essential-core genes were the most enzyme-rich category (**41.9%**) and had the strongest functional annotation, with 13.0% hypothetical proteins. Relative to non-essential genes, they were enriched in Protein Metabolism (+13.7 percentage points), Cofactors/Vitamins (+6.2%), Cell Wall (+3.9%), and Fatty Acid biosynthesis (+3.1%). They were depleted in Carbohydrates (-7.9%), Amino Acids (-5.6%), and Membrane Transport (-4.0%), functions interpreted as more conditionally important.

Essential-auxiliary genes comprised 3,683 genes. They were less frequently enzymatic (13.4%) and more often hypothetical (38.2%), with prominent assignments involving ribosomes, DNA replication, type 4 secretion, and plasmid replication. This pattern suggests strain-specific variants of core machinery and mobile genetic elements, but the interpretation remains partly inferential.

The 1,259 essential-unmapped genes were the least characterized group, with 44.7% hypothetical proteins. Known annotations included divergent ribosomal proteins, translation factors, transposases, and DNA-binding proteins. These results suggest the hypothesis that some unmapped essentials are recently acquired or highly divergent variants of conserved functions.

## Validation and Interpretation

Gene-length validation found that essential genes were slightly shorter on average, consistent with possible insertion bias in transposon-derived essentiality calls. Stratification by clade size, genomic context, and lifestyle indicated that essential-core enrichment was robust across the tested contexts.

The report places the result within prior work showing that essentiality can be strain-dependent and evolvable, including Rosconi et al.’s categories of universal essential, core strain-specific essential, and accessory essential genes. It also connects the high hypothetical fraction among essential-unmapped genes to findings from minimal-genome research and notes that gene length can bias transposon-based essentiality estimates.

## Limitations

- Essentiality is an upper-bound classification because absent insertions can reflect short genes, low-complexity regions, scaffold edges, or other technical factors rather than true essentiality.
- Pangenomes built from only two genomes can produce trivially high core fractions and reduce the discriminatory value of core-versus-auxiliary status.
- The main *E. coli* clade was excluded because it contained too many genomes; Keio mapped to the small *Escherichia coli* E clade at only 26.1% coverage.
- Essentiality was measured under a single library-construction and growth context, so stress-specific essential genes may not be captured.
- Dyella79 was excluded because FB gene identifiers (`N515DRAFT_*`) did not join to protein identifiers (`ABZR86_RS*`).

## Future Directions

1. Compare pangenome conservation with condition-specific fitness effects, especially genes with fitness < -2 under stress.
2. Use FB orthology data to identify essential gene families conserved across multiple species.
3. Correlate quantitative mean fitness effects with core-genome fraction rather than using only a binary essentiality label.
4. Characterize essential-auxiliary genes to test whether they compensate for missing or divergent core functions.

## Related Concepts
- [[concepts/annotation-gap]]
- [[concepts/evidence-triangulation]]
- [[concepts/prevalence-ceiling]]
- [[concepts/organism-specificity]]

- [[concepts/pangenome-integration]]
- [[concepts/gene-essentiality]]
- Condition-dependent fitness effects
- [[entities/random-barcode-transposon-sequencing]]
- [[concepts/core-accessory-resistance]]

## Entities
- [[entities/streptococcus-pneumoniae]]
- [[entities/uniprot]]
