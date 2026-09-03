<!-- tension-hash: 00ba316476a1afc0 -->
# Debris or Cargo: Are Costly Accessory Genes Decaying Junk or Retained Adaptive Function?

Across several concept pages, the same class of costly, dispensable, mobile-element-associated genes is interpreted two ways: as evolutionary debris from horizontal transfer that should be purged because it burdens the host, or as retained ecological cargo whose costs are context-dependent and whose benefits appear only under untested conditions. The distinction matters because it determines whether defense islands, prophage-linked AMR genes, and CAZy–T4SS associations should be read as decaying relics or as functionally maintained accessory systems — a question none of the individual studies can settle alone.

## Evidence Sides

**Debris/purging side**: Costly+dispensable genes are framed as genomic debris from HGT that tends to be purged over evolutionary time because it burdens the host and is not broadly conserved [src: costly_dispensable_genes]. The costly+dispensable set is described as predominantly selfish elements rather than metabolic pathways, cautioning against applying community-dependency (Black Queen) explanations wholesale [src: costly_dispensable_genes]. Prophage-marked AMR co-localization is weak at fine scale: only 10.4% of AMR instances were within 10 genes of a marker, with a modest, sign-reversing proximity-accessory association at 3–5 genes [src: prophage_amr_comobilization].

**Adaptive/retained-function side**: Condition-specific phenotypes suggest genes costly only in the tested lab context may be beneficial elsewhere [src: costly_dispensable_genes]. Accessory enrichment and strong defense-system co-occurrence, plus a positive association between defense count and prophage burden, support retained defense investment under phage pressure [src: phage_defense_arsenal, snipe_defense_system]. SNIPE detected 4,572 PF13250-containing clusters, 86.7% accessory or singleton, spanning 33 phyla [src: snipe_defense_system]. ManYZ/SNIPE mechanics show a defense gene can be retained without disabling a costly transporter [src: snipe_defense_system]. More than half of AMR instances in high-burden species were on prophage-marked contigs [src: prophage_amr_comobilization]. GT2–T4SS co-localisation, tree incongruence, and 32 cross-phylum transfer events support adaptive mobilization of CAZy genes [src: t4ss_cazy_environmental_hgt]. Ecotype defense categories V and L were differentiated in 11/12 and 9/12 species respectively (mean effect size 0.0337 for L) [src: ecotype_functional_differentiation].

## Possible Reconciliations

- **Scope-splitting hypothesis**: the costly+dispensable set is heterogeneous — some genes are true debris en route to loss, others (defense islands, GT2 loci) are element-level or host-level adaptive cargo; aggregate statistics blur this split [src: costly_dispensable_genes].
- **Scale-mismatch hypothesis**: species-level prophage burden and local gene-proximity are different measurements (openness to acquisition vs. specific conservation), so weak local co-localization does not contradict strong aggregate defense/AMR associations [src: prophage_amr_comobilization].
- **Marker-breadth hypothesis**: PF13250-based SNIPE calls (80.4% attributable to just two domain descriptions) may overcount functional defense systems, inflating apparent adaptive signal [src: snipe_defense_system].
- **Confound hypothesis**: shared habitat, phylogeny, or genome quality could produce CAZy–metal or T4SS co-occurrence without actual co-transfer [src: t4ss_cazy_environmental_hgt].

## Resolving Work

- Direct fitness assays (multi-condition growth/competition) for individual defense and CAZy loci to test cost-context-dependence directly [src: costly_dispensable_genes, snipe_defense_system].
- Synteny-threshold and Node_4915 BLAST validation plus housekeeping-gene null models for T4SS-CAZy transfer claims [src: t4ss_cazy_environmental_hgt].
- Fine-scale phylogenetic dating of individual costly+dispensable genes to separate decay trajectories from stably maintained cargo.
- Re-annotation of SNIPE architectures beyond PF13250/DUF4041 (only 54 clusters had Mug113-related descriptions) to correct marker specificity [src: snipe_defense_system].
- Paired species-level and gene-level proximity analyses on the same AMR/prophage dataset to test whether the two association strengths converge [src: prophage_amr_comobilization].
