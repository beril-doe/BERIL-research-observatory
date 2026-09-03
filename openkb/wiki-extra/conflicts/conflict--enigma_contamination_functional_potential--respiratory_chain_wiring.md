<!-- tension-hash: 89d217d861a46345 -->
# Does Functional Redundancy Mask or Merely Confound Metal/Contamination Response Signals?

A central disagreement running through the functional-redundancy work is whether apparent community- and organism-level buffering against metal stress reflects genuine functional redundancy, or whether statistical and resolution artifacts are producing an illusion of redundancy where finer analysis would reveal differentiated, non-interchangeable functions. This matters because the redundancy interpretation underlies claims about ecosystem resilience to contamination, while the alternative interpretation implies that current models are simply underpowered or misspecified.

## Evidence Sides

**Redundancy holds (null/overlap results)**
- "The confirmatory analyses support a null community-level relationship" [src: enigma_contamination_functional_potential]
- "The genus-level analysis is consistent with overlapping broad functions" [src: enigma_contamination_functional_potential]
- ADP1 "has multiple respiratory entry points expressed at similar baseline protein levels" [src: respiratory_chain_wiring]

**Redundancy breaks down or is inconclusive (positive/conditional/anomalous results)**
- "Coverage-adjusted exploratory models show positive defense coefficients and nominally significant p-values in some specifications" [src: enigma_contamination_functional_potential]
- "The species-proxy analysis is too coverage-limited to determine whether finer taxonomic resolution would reveal differentiated metal-response functions" [src: enigma_contamination_functional_potential]
- Respiratory components "are not uniformly interchangeable: carbon source changes which component is required," supporting "conditional or capacity-limited redundancy rather than complete functional equivalence" [src: respiratory_chain_wiring]
- "NDH-2 presence was not associated with a smaller Complex I aromatic deficit and, descriptively, organisms with validated NDH-2 had the larger deficit" [src: respiratory_chain_wiring]

## Possible Reconciliations

- **Model-specification hypothesis**: the null vs. positive discrepancy could stem purely from coverage-adjustment choices or fraction aggregation, not from any real biological signal — i.e., "model sensitivity" as stated directly in the source [src: enigma_contamination_functional_potential].
- **Resolution hypothesis**: redundancy may be real at genus level (broad function overlap) but false at species level, simply because species-proxy data are too sparse to detect differentiation — not yet falsifiable either way.
- **Conditional-redundancy hypothesis**: redundancy may exist only under some environmental conditions (e.g., baseline carbon source) and disappear under others, reconciling "similar baseline expression" with "required under specific conditions."
- **Underpowered cross-species test hypothesis**: the NDH-2 anomaly may reflect small sample size rather than a true failure of compensation, meaning ADP1-based extrapolation could still hold once power improves [src: respiratory_chain_wiring].

## Resolving Work

- Rerun the community-level defense-coefficient models with matched coverage-adjustment strategies across confirmatory and exploratory pipelines to isolate whether the null/positive split is a specification artifact.
- Acquire deeper species-level metagenomic coverage to directly test whether genus-level overlap dissolves into differentiated species-level metal-response functions.
- Run controlled carbon-source-switch experiments in ADP1 to map which respiratory components are truly interchangeable vs. required, quantifying "capacity-limited" redundancy directly.
- Expand the cross-species NDH-2 dataset to increase power and re-test whether NDH-2 presence associates with smaller Complex I aromatic deficits.
- Conduct a sensitivity analysis varying fraction-aggregation methods to determine how much of the "positive defense coefficient" result depends on aggregation choice.
