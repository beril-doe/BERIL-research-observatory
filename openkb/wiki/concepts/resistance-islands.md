---
type: "Concept"
sources: ["summaries/prophage_amr_comobilization__REPORT.md", "summaries/cofitness_coinheritance__REPORT.md", "summaries/amr_strain_variation__REPORT.md"]
description: "Co-inherited AMR gene modules that structure strain-level resistance variation."
---

# Resistance Islands

Resistance islands are tightly co-occurring groups of antimicrobial-resistance (AMR) genes that may be inherited or maintained as linked genomic modules. They provide a structural explanation for why within-species AMR variation can be extensive yet non-random, complementing the broader [[concepts/core-accessory-resistance]] distinction. [src: amr_strain_variation]

## Evidence from the strain-variation analysis

The analysis identified 1,517 resistance islands across 705 species, representing 54% of the species analyzed. [src: amr_strain_variation] Islands contained a mean of 6.2 genes, a median of 4 genes, and a maximum of 43 genes. [src: amr_strain_variation] Their mean phi coefficient was 0.827, indicating tight within-species co-occurrence among genes assigned to the same island. [src: amr_strain_variation]

Most detected islands were multi-mechanism modules: 1,343 of 1,517 islands (88%) contained genes associated with more than one resistance mechanism. [src: amr_strain_variation] Efflux genes occurred in 954 islands, enzymatic-inactivation genes in 698, oxidoreductase genes in 694, regulatory genes in 502, beta-lactamase genes in 341, target-modification genes in 293, and cell-wall-modification genes in 137. [src: amr_strain_variation] Other or unclassified mechanisms appeared in 1,026 islands. [src: amr_strain_variation]

These results indicate that AMR genes are frequently organized into co-inherited or otherwise tightly linked combinations rather than distributed independently among strains. [src: amr_strain_variation] The multi-mechanism composition suggests the hypothesis that resistance islands can provide coordinated protection against multiple drug classes, but the observed associations alone do not establish functional synergy. [src: amr_strain_variation]

## Relationship to phylogeny and AMR variation

Resistance islands help connect two findings from the report: AMR repertoires differ substantially among strains, while AMR profiles also track bacterial relatedness. [src: amr_strain_variation] Across 1,261 species tested with ANI-based Mantel analyses, 701 species (55.6%) showed significant phylogenetic signal after FDR correction, and the median Mantel r for all AMR genes was 0.247. [src: amr_strain_variation] This pattern is consistent with a model in which a lineage acquires a linked resistance module and subsequently maintains or vertically transmits it, producing lineage-specific AMR signatures. [src: amr_strain_variation]

The report found stronger phylogenetic signal for non-core, putatively acquired AMR genes than for core genes: median Mantel r values were 0.222 and 0.117, respectively, with a paired-test p-value of 7.0e-16 across 489 comparisons. [src: amr_strain_variation] This result supports lineage-restricted maintenance as a plausible explanation, but it does not by itself prove that the genes reside on islands or distinguish vertical inheritance from repeated horizontal transfer among closely related strains. [src: amr_strain_variation] The interpretation is also affected by the near-universal prevalence of core genes, which limits their Jaccard-distance variation and can suppress distance-based correlation statistics. [src: amr_strain_variation]

## Mechanistic interpretation

Resistance islands may bring together efflux, enzymatic inactivation, target modification, regulatory, and other mechanisms in a single linked unit. [src: amr_strain_variation] Such linkage could facilitate simultaneous movement or retention of resistance determinants, potentially explaining why strains acquire characteristic multi-gene AMR profiles. [src: amr_strain_variation] However, co-occurrence may reflect physical linkage on a plasmid, integron, transposon, chromosome, or other mobile genetic element without implying that selection directly favors every gene in the module. [src: amr_strain_variation]

This distinction matters for [[concepts/phylogenetic-amr-structure]]: a phylogenetically clustered AMR profile can arise through clonal expansion after acquisition, restricted transfer among compatible lineages, or a combination of these processes. [src: amr_strain_variation] It also connects resistance-island analysis to [[concepts/environmental-resistome]], because ecological and host-associated settings may impose different selection pressures on linked resistance modules. [src: amr_strain_variation]

## Tensions

The report interprets the high mean phi coefficient and prevalence of multi-mechanism islands as evidence that resistance genes are often inherited as intact units. [src: amr_strain_variation] The same report explicitly cautions that island co-occurrence does not prove co-selection or functional synergy; linkage on a shared mobile element could produce the pattern without complementary biological action. [src: amr_strain_variation]

A second unresolved issue is whether resistance islands primarily explain stable clonal AMR lineages or ongoing horizontal dissemination. [src: amr_strain_variation] The observed phylogenetic signal favors lineage-restricted maintenance as one explanation, but genomic-context mapping and explicit transfer analyses are required to separate vertical transmission, clonal expansion, and repeated transfer among close relatives. [src: amr_strain_variation]

## Open Directions

- Map the 1,517 detected islands to plasmids, chromosomes, integrons, transposons, and insertion sequences to test their physical genomic context. [src: amr_strain_variation]
- Compare island presence with strain phylogeny and ANI to distinguish clonal inheritance from recent horizontal transfer. [src: amr_strain_variation]
- Test whether multi-mechanism islands improve survival or resistance across multiple antibiotic classes, rather than merely reflecting linkage. [src: amr_strain_variation]
- Integrate island profiles with virulence and metabolic variation to determine whether resistance-island ecotypes correspond to broader strain phenotypes. [src: amr_strain_variation]
- Use the observed co-occurrence network to predict which AMR genes are likely to be co-acquired, then evaluate those predictions against newly sampled genomes. [src: amr_strain_variation]

## Related Documents
- [[summaries/amr_strain_variation__REPORT]]


See also: [[summaries/cofitness_coinheritance__REPORT]]

See also: [[summaries/prophage_amr_comobilization__REPORT]]