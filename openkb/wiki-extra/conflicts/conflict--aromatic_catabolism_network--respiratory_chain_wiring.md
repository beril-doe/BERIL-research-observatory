<!-- tension-hash: 26307e6d479abb62 -->
# Total NADH Yield vs. NADH Production Rate: What Explains Complex I Essentiality?

A central question in respiratory-constraint studies of ADP1 and related species is why Complex I becomes essential on some carbon sources but not others. The intuitive explanation — that substrates generating more NADH create greater Complex I dependency — is directly contradicted by ADP1's own substrate map, forcing a choice between a rate-based explanation and unresolved cross-species confounds involving alternative dehydrogenases. Resolving this matters because it determines whether Complex I essentiality can be predicted from stoichiometry alone or requires flux/kinetic data. See [[concepts/nadh-flux-respiratory-constraints]].

## Evidence Sides

**Total NADH yield / aromatic-substrate association**: Within ADP1, Complex I is strongly associated with quinate-specific growth defects and elevated aromatic-substrate flux. [src: aromatic_catabolism_network] Yet across species, the strongest Complex I defects also occur on acetate and succinate — non-aromatic substrates — suggesting the dependency tracks general NADH load rather than aromatic catabolism specifically. [src: aromatic_catabolism_network]

**Rate-of-production (burst) hypothesis**: The ADP1 substrate map shows quinate yields only 4 theoretical NADH molecules versus 9 for glucose, yet Complex I is essential on quinate and dispensable on glucose — the opposite of a simple total-yield prediction. [src: respiratory_chain_wiring] The proposed explanation is that quinate concentrates NADH production in a TCA-cycle burst, while glucose spreads production across Entner-Doudoroff and TCA reactions. [src: respiratory_chain_wiring] This remains a hypothesis, since the stoichiometry is theoretical and intracellular fluxes were not measured. [src: respiratory_chain_wiring]

**NDH-2 compensation, ADP1 vs. cross-species**: In ADP1, mild Complex I phenotypes on lactate and lack of glucose-specific respiratory requirement are consistent with NDH-2 compensation, though NDH-2 itself has no direct deletion phenotype. [src: respiratory_chain_wiring] Across species, however, validated NDH-2 presence coincided with *larger*, not smaller, aromatic Complex I deficits — though this difference was not significant. [src: respiratory_chain_wiring]

## Possible Reconciliations

- **Scope-difference hypothesis**: Within-species (ADP1) associations reflect true mechanistic burst dynamics, while cross-species associations are confounded by phylogenetic differences in respiratory wiring, making the two comparisons not directly commensurable. [src: aromatic_catabolism_network, respiratory_chain_wiring]
- **Measurement-differential hypothesis**: Theoretical NADH yield (stoichiometric counting) and actual NADH production rate (flux over time) are different quantities; essentiality may track the latter, not the former. [src: respiratory_chain_wiring]
- **Compensation-capacity hypothesis**: NDH-2 compensation may depend on organism-specific enzyme capacity or respiratory architecture rather than mere presence/absence, explaining why annotated NDH-2 doesn't uniformly reduce Complex I deficits across species. [src: respiratory_chain_wiring]
- **Annotation-error hypothesis**: Cross-species NDH-2 annotations may be unreliable, obscuring a true compensatory relationship. [src: respiratory_chain_wiring]

## Resolving Work

- Measure intracellular NADH production flux (not just stoichiometric yield) on quinate vs. glucose in ADP1 using isotope tracing or biosensors, to test the "burst" hypothesis directly. [src: respiratory_chain_wiring]
- Construct ADP1 NDH-2 deletion/overexpression strains and quantify growth on aromatic vs. non-aromatic substrates to establish a direct (not annotation-based) compensation phenotype. [src: respiratory_chain_wiring]
- Re-validate NDH-2 annotations experimentally across the cross-species panel before re-testing the compensation correlation. [src: respiratory_chain_wiring]
- Compare Complex I essentiality across a matched substrate panel (aromatic and non-aromatic) within single organisms other than ADP1 to separate substrate chemistry from species-specific wiring. [src: aromatic_catabolism_network, respiratory_chain_wiring]
