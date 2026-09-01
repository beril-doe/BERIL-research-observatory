<!-- tension-hash: 3499471b6f89a834 -->
# Condition-Dependence Scope in ADP1: 31% vs. 70%

Two analyses of *Acinetobacter baylyi* ADP1 fitness data disagree sharply on how much of the genome shows condition-dependent essentiality. One survey of the complete deletion matrix finds condition-specific effects in under a third of genes; a second, narrower analysis of a triple-essentiality subset finds such effects in more than two-thirds. The gap (31% vs. 70%) is large enough to change the basic picture of how modular or pervasive condition-dependence is in this organism, and it matters because downstream claims about pathway flexibility, core-vs-accessory burden, and comparative genomics all rest on estimates of how common conditional essentiality actually is. See [[concepts/condition-dependent-essentiality]].

## Evidence Sides

**Complete deletion matrix**
Across the full deletion set, 625 of 2,034 genes (31%) reached a condition-specificity score of at least 1.0. [src: adp1_deletion_phenotypes]

**Triple-essentiality subset**
Within the smaller triple-essentiality gene set, 333 of 478 genes (70%) showed at least one Q25-defined defect across eight conditions. [src: adp1_triple_essentiality]

## Possible Reconciliations

- **Gene-set coverage hypothesis**: the triple-essentiality subset (478 genes) is not a random sample of the full 2,034-gene matrix — it may be enriched for genes already flagged as essential or near-essential under some condition, inflating the apparent rate of condition-dependence.
- **Threshold-definition hypothesis**: "condition-specificity score ≥ 1.0" and "at least one Q25-defined defect" are different statistical constructs (a continuous score vs. a quantile-based defect call) and may simply have different sensitivities, independent of the underlying biology.
- **Condition-count hypothesis**: the two analyses may sample different numbers or types of conditions, so a gene could clear one condition-dependence bar over eight conditions but not another bar computed differently across a different condition panel.
- **Scale hypothesis**: with fewer genes tested (478 vs. 2,034), the triple-essentiality subset has less multiple-testing burden per gene, which could mechanically raise the fraction called condition-dependent regardless of true biology.

## Resolving Work

- Recompute the condition-specificity score (≥1.0 threshold) restricted to the same 478 genes used in the triple-essentiality subset, to test the gene-set coverage hypothesis directly.
- Recompute the Q25-defect rate against the full 2,034-gene deletion matrix, to see whether 70% holds outside the triple-essentiality subset.
- Cross-tabulate genes flagged by score ≥1.0 against genes flagged by Q25-defect calls on an identical condition panel, to isolate threshold-definition effects from real disagreement.
- Report the number and identity of conditions used in each analysis, since a mismatch in condition count (rather than gene set or threshold) could alone explain much of the gap.
- Re-derive both metrics using a single, pre-registered defect-calling method (e.g., always Q25-based, or always score-based) applied uniformly to determine whether 31% or 70% is closer to the "true" rate under matched conditions.
