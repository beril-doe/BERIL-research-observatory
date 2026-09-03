<!-- tension-hash: e5b12397adf35d97 -->
# Conserved-and-Tractable vs. Rare-and-Restricted: Where Does "Dark" Function Actually Live?

Two prioritization strategies built on the same starting resource — Fitness Browser "dark gene" labels — disagree about where genuine functional darkness is concentrated and how reliable the starting labels even are. One framework prioritizes genes that are broadly conserved and experimentally tractable; the other finds that the genes most likely to be *truly* unannotated are short, accessory, taxonomically restricted, and clustered in a handful of underrepresented organisms. Layered on top is a more basic problem: a large fraction of the "dark" genes used to seed both approaches turn out to already have known functions once reannotated. This matters because it determines whether resources should chase broad, easy-to-study conservation or narrow, hard-to-study novelty — and whether the starting gene set is even trustworthy.

## Evidence Sides

**Conservation/tractability framework**
The framework treats Fitness Browser labels as a useful starting definition of darkness but notes Bakta reclassified 83.7% of linked dark genes as non-hypothetical. [src: functional_dark_matter, truly_dark_genes] It advances two complementary prioritization routes: a conservation-weighted route targeting widely distributed knowledge gaps, and an evidence-weighted route favoring organisms with deep condition coverage and established perturbation systems. [src: functional_dark_matter]

**Truly-dark-genes framework**
This project finds the opposite distributional pattern: many truly dark genes are short, accessory, taxonomically restricted, and concentrated in underrepresented organisms — especially Methanococcus strains, which account for 55% of the truly dark set. [src: truly_dark_genes] It also documents the same 83.7% reannotation-reclassification rate, treating it as evidence that "dark" is often an artifact of outdated annotation rather than genuine novelty. [src: truly_dark_genes]

## Possible Reconciliations

- **Definitional-scope hypothesis**: "Darkness" may refer to two different populations — a large, shallow layer of merely under-annotated genes (resolved by reannotation, as the 83.7% figure suggests) and a small, deep layer of genuinely novel genes concentrated in restricted lineages. The frameworks may simply be describing different layers of the same distribution.
- **Selection-bias hypothesis**: Conservation-weighted prioritization may systematically exclude the Methanococcus-heavy, accessory-gene population by design (favoring breadth), not because that population is less "dark," making the two results compatible rather than contradictory.
- **Pipeline-order hypothesis**: If reannotation is applied before conservation/evidence weighting, the residual truly-dark set may naturally skew toward taxonomically restricted genes, reconciling both patterns as sequential filtering stages rather than competing claims.

## Resolving Work

- Rerun both prioritization routes on a Bakta-reannotated gene set and compare whether the Methanococcus-heavy skew (55%) persists after removing the 83.7% reclassified genes.
- Directly test whether conservation-weighted candidates and truly-dark candidates are disjoint or overlapping sets across the same organism panel.
- Quantify how much of the taxonomic-restriction signal is explained by underrepresentation in reference databases versus genuine lineage-specific gene content.
- Track outcomes of experimental follow-up on both candidate pools to see whether tractability actually differs, or whether it's confounded by existing strain/tool availability for well-studied organisms.
