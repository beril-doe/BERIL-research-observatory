<!-- tension-hash: 0ff99dfbf22dec37 -->
# Genome-Wide HGT Signature vs. Gene-Set-Specific Inheritance

Several analyses converge on genomic features — co-localization with mobile elements, phylogenetic incongruence, contig-level co-occurrence with AMR, prevalence discordance — that are read as evidence of horizontal gene transfer shaping accessory genomes. But at least one focal gene set (plant-growth-promoting, PGP) shows the opposite pattern: overwhelmingly core status that explicitly rejects a general HGT-centered model. The disagreement matters because it determines whether "costly," "dispensable," "accessory," and "co-localized with mobile DNA" can be treated as a single syndrome pointing to transfer, or whether HGT signatures are properly gene-set-specific and must be argued for, not assumed, in each case. See [[concepts/horizontal-gene-transfer]].

## Evidence Sides

**Side A: Multiple gene families carry acquisition/mobility signatures**
- The costly+dispensable gene profile "is consistent with genomic debris from HGT" [src: costly_dispensable_genes].
- GT2 loci were co-localized with T4SS machinery, and phylogenetic incongruence provided evidence for 32 cross-phylum events [src: t4ss_cazy_environmental_hgt].
- Prophage markers occurred on the same contigs as 55.7% of AMR instances, and prophage density predicted AMR breadth strongly [src: prophage_amr_comobilization].
- PHB acquisitions and losses (311 acquisitions, 278 losses) were defined from family-level prevalence discordance, with a 60.1% accessory rate as supporting evidence [src: phb_granule_ecology].

**Side B: PGP genes reject an HGT-centered model**
- All 13 PGP genes had core fractions above the 46.8% genome-wide baseline, although pqqD retained a comparatively high singleton fraction of 27.5% [src: pgp_pangenome_ecology].

## Possible Reconciliations

- **Scope-of-claim hypothesis**: The two sides describe different gene classes entirely — mobile-element-associated costly genes, prophage-linked AMR genes, T4SS-proximal GT2 loci, and discordant phaC copies versus ecologically specialized PGP genes — so no genome-wide rule is being contradicted, only conflated [src: costly_dispensable_genes, prophage_amr_comobilization, t4ss_cazy_environmental_hgt, phb_granule_ecology, pgp_pangenome_ecology].
- **Mechanism-vs-correlation hypothesis**: Side A's strongest claims (T4SS co-localization, prophage-AMR co-occurrence) are association evidence, not demonstrated transfer mechanisms — no experiment has shown T4SS-mediated transfer, and local proximity predicts accessory status only weakly [src: t4ss_cazy_environmental_hgt, prophage_amr_comobilization].
- **Detection-bias hypothesis**: Core status for PGP genes could still mask historical transfer, since exact-name annotation can miss divergent homologues [src: pgp_pangenome_ecology].
- **Method-artifact hypothesis**: recent-acquisition signals depend on incomplete annotation, binary core/accessory calls, a 48-organism ortholog search, and a 90% identity threshold, so apparent acquisition rates may be inflated or biased relative to PGP's pangenome method [src: costly_dispensable_genes, prophage_amr_comobilization].

## Resolving Work

- Run BLAST validation on Node_4915 and re-test the ≤10 kb co-localization threshold against a randomized-genome null [src: t4ss_cazy_environmental_hgt].
- Conduct direct T4SS conjugation assays to test whether GT2-adjacent loci are mobilizable, rather than relying on co-localization [src: t4ss_cazy_environmental_hgt].
- Apply gene-tree/species-tree reconciliation and genomic-context analysis to the 311 PHB acquisition and 278 loss events to confirm transfer versus differential retention [src: phb_granule_ecology].
- Extend the ortholog search beyond 48 organisms toward the full ~293,000-genome set to check whether recent-acquisition and core-fraction estimates are threshold-sensitive [src: costly_dispensable_genes, prophage_amr_comobilization].
- Re-annotate PGP gene families with divergent-homologue-sensitive methods (not exact-name matching) to test whether pqqD's 27.5% singleton fraction reflects undetected transfer [src: pgp_pangenome_ecology].
