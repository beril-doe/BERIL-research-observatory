---
sources: ["summaries/paperblast_explorer__REPORT.md", "summaries/metal_fitness_atlas__REPORT.md", "summaries/alphafold_msa_annotation__REPORT.md"]
type: "Dataset"
description: "Protein structure database used to measure bacterial MSA depth"
---

# AlphaFold Protein Structure Database

## Identity

The AlphaFold Protein Structure Database (AFDB; also called the AlphaFold Structure Database) is a dataset of predicted protein structures and associated sequence-based information. [src: alphafold_msa_annotation]

## Role in the BER analysis

The report used the BERDL AlphaFold MSA-depth collection, `kescience_alphafold.alphafold_msa_depths`, to retrieve MSA depth for UniProt-linked bacterial gene-cluster representatives. [src: alphafold_msa_annotation] MSA depth was analysed as both a structural-prediction variable and a proxy for existing functional annotation richness, connecting this dataset to [[concepts/msa-depth]], [[concepts/structural-novelty]], and [[concepts/annotation-gap]]. [src: alphafold_msa_annotation]

Of 132,531,501 total gene clusters, 38,804,903 (29.3%) had a real UniProt accession and 38,051,842 (28.7%) successfully bridged to the AlphaFold MSA-depth table. [src: alphafold_msa_annotation] The remaining 70.7% lacked UniRef100 IDs or had UniParc-only identifiers without an AlphaFold entry. [src: alphafold_msa_annotation]

## Key findings involving AFDB data

- Core gene clusters had a median MSA depth of 15,308, compared with 5,299 for auxiliary-plus-singleton clusters and 5,527 for auxiliary non-singletons. [src: alphafold_msa_annotation]
- Across 38,051,842 gene-cluster–UniProt pairs, MSA depth correlated strongly with domain-hit count (Spearman ρ = 0.7563). [src: alphafold_msa_annotation]
- Mean domain hits ranged from 0.59 for clusters with MSA depth below 10 to 10.83 for clusters with MSA depth at least 10,000. [src: alphafold_msa_annotation]
- The study identified 415,603 core clusters with MSA depth below 10; 286,439 (68.9%) were hypothetical, while 137 (0.033%) had EC annotations and 346 (0.083%) mapped to KEGG. [src: alphafold_msa_annotation]

These low-depth, conserved proteins were designated “paradox proteins” and proposed as a priority set for investigating [[concepts/structural-novelty]] within the bacterial [[concepts/annotation-gap]]. [src: alphafold_msa_annotation]

## Version and limitations

The analysis used a static BERDL AlphaFold version-6 snapshot, so MSA depths may change as sequence databases and AlphaFold resources are updated. [src: alphafold_msa_annotation] Coverage was biased toward better-characterised organisms with established reference proteomes, meaning the analysed proteins do not represent all bacterial diversity uniformly. [src: alphafold_msa_annotation] MSA depth was retrieved for each gene cluster’s representative sequence, so sequence variation among other cluster members was not assessed. [src: alphafold_msa_annotation]

## Related resources and follow-up

The report proposes comparing AlphaFold MSA depth with [[entities/esmfold]] confidence scores as a complementary novelty analysis because ESMFold does not use MSAs. [src: alphafold_msa_annotation] It also proposes mapping low-depth core proteins against [[entities/gtdb]] phylogeny and joining them to [[entities/fitness-browser]] measurements to test their evolutionary distribution and condition-dependent importance. [src: alphafold_msa_annotation]

See [[summaries/alphafold_msa_annotation__REPORT]] for the full source summary.

See also: [[summaries/metal_fitness_atlas__REPORT]]

See also: [[summaries/paperblast_explorer__REPORT]]