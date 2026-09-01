---
type: "Concept"
sources: ["summaries/webofmicrobes_explorer__REPORT.md", "summaries/pgp_pangenome_ecology__REPORT.md", "summaries/pangenome_openness__REPORT.md", "summaries/nmdc_community_metabolic_ecology__REPORT.md", "summaries/metabolic_capability_dependency__REPORT.md"]
description: "Within-species metabolic pathway variation that forms ecologically meaningful clusters."
---

# Metabolic Ecotypes

## Definition

**Metabolic ecotypes** are within-species groups distinguished by contrasting metabolic pathway profiles, often reflecting differences in resource use, biosynthetic independence, or environmental adaptation. [src: metabolic_capability_dependency]

This concept connects [[concepts/metabolic-ecotypes]] with [[concepts/phenotypic-landscape]], [[concepts/organism-specificity]], and [[concepts/phylogenetic-confounding]].

## Evidence from the BERIL analysis

The report identified distinct metabolic clustering in all 10 target species analyzed, with every species having a silhouette score greater than 0.2. [src: metabolic_capability_dependency] Silhouette scores ranged from 0.349 in *PALSA-747* sp. to 0.894 in *Salmonella enterica*, indicating substantial variation in the sharpness of ecotype boundaries among species. [src: metabolic_capability_dependency]

The strongest structure occurred in *Salmonella enterica*, which was partitioned into six metabolic clusters across 11,396 genomes, with a silhouette score of 0.894. [src: metabolic_capability_dependency] Other examples included two clusters in *Stutzerimonas stutzeri* across 149 genomes, two clusters in *Alteromonas macleodii* across 56 genomes, and six clusters in *Acetatifactor intestinalis* across 59 genomes. [src: metabolic_capability_dependency]

Metabolic clusters were significantly associated with isolation environment in *Salmonella enterica* (χ²=1570.2, df=25, p<0.0001) and *Phenylobacterium* sp. (χ²=12.2, df=1, p=0.0005). [src: metabolic_capability_dependency] The tested marine organisms *Stutzerimonas*, *Alteromonas*, *Pelagibacter*, and *Prochlorococcus* did not show significant environment–cluster associations. [src: metabolic_capability_dependency]

The most heterogeneous pathways across species were valine/leucine biosynthesis (heterogeneity=0.60), tryptophan biosynthesis (0.51), and lysine/threonine biosynthesis (0.49). [src: metabolic_capability_dependency] These differences indicate that populations can vary in whether they retain biosynthetic independence for particular amino acids. [src: metabolic_capability_dependency]

## Interpretation

The results support the hypothesis that within-species metabolic pathway heterogeneity is widespread rather than exceptional. [src: metabolic_capability_dependency] In copiotrophic organisms such as *Salmonella enterica*, the association between metabolic clusters and isolation source is consistent with ecological or epidemiological differentiation, although the observational analysis does not establish causation. [src: metabolic_capability_dependency]

The absence of significant environment–cluster associations in marine organisms has several possible explanations: isolation-source metadata may be too coarse, clusters may track depth or nutrient zones rather than recorded source categories, or pathway-level annotations may miss the gene-content differences most relevant to marine ecological divergence. [src: metabolic_capability_dependency] These possibilities motivate [[concepts/phenotype-resolution-matching]] and [[concepts/microbiome-ecotype-portability]] as related analytical concerns.

Metabolic ecotypes should not be equated automatically with discrete ecological species or stable phenotypes. [src: metabolic_capability_dependency] Cluster boundaries may reflect gradients in pathway content, uneven sampling, phylogenetic structure, or technical choices in pathway prediction and clustering. [src: metabolic_capability_dependency] Explicit phylogenetic correction is therefore needed before attributing cluster structure to ecological selection. [src: metabolic_capability_dependency]

## Relationship to pathway capability and dependency

The ecotype analysis complements the report's finding that genomic pathway completeness does not always imply functional dependency. [src: metabolic_capability_dependency] Across 1,695 pathway–organism pairs from 48 organisms, 15.8% of complete pathways were classified as latent capabilities, while 32.3% were intermediate and 51.9% were active dependencies. [src: metabolic_capability_dependency] This distinction makes [[concepts/pathway-completeness]], [[concepts/condition-dependent-essentiality]], and [[concepts/latent-metabolic-capabilities]] relevant to interpreting metabolic ecotypes.

A pathway may differentiate ecotypes at the genomic level without being required under the conditions used for fitness measurement. [src: metabolic_capability_dependency] Conversely, a pathway that is active or essential in one environment may be dispensable in another if resources or metabolites are externally available. [src: metabolic_capability_dependency] Ecotype interpretation therefore benefits from combining pathway presence, measured fitness, environmental metadata, and—where possible—expression or metabolite data through [[concepts/multi-omics-integration]].

## Methodological considerations

The report used hierarchical clustering and principal-component analysis of within-species pathway variation to identify ecotypes. [src: metabolic_capability_dependency] The analysis included species with at least 50 genomes and at least 15 variable pathways. [src: metabolic_capability_dependency]

GapMind pathway predictions were used to represent metabolic profiles, so the resulting ecotypes describe pathway-level variation rather than complete biochemical or regulatory phenotypes. [src: metabolic_capability_dependency] Pathway annotations may fail to capture partial pathway erosion, alternate enzymes, expression differences, substrate specificity, or flux regulation. [src: metabolic_capability_dependency] These limitations connect the concept to [[concepts/annotation-gap]], [[concepts/capability-versus-kinetics]], and [[concepts/metabolic-model-gapfilling]].

Environmental associations may also be confounded by lineage, geographic sampling, or dataset composition. [src: metabolic_capability_dependency] The report specifically identifies phylogenetic structure as a possible confounder in the *Salmonella* and *Phenylobacterium* associations. [src: metabolic_capability_dependency] This makes [[concepts/phylogenetic-confounding]] and [[concepts/cultivation-bias]] important safeguards when comparing ecotypes across environments.

## Tensions

The report found clear metabolic clustering in all 10 target species, but environment–cluster associations were significant only for *Salmonella enterica* and *Phenylobacterium* sp. [src: metabolic_capability_dependency] Thus, metabolic differentiation appears broadly detectable, whereas its relationship to recorded environment is taxon- and metadata-dependent. [src: metabolic_capability_dependency]

## Open Directions

- Use phylogenetically corrected association tests to determine whether metabolic clusters predict environment independently of lineage. [src: metabolic_capability_dependency]
- Reanalyze the 10 species with direct GapMind gene assignments and gene-level presence/absence to test whether pathway-level clustering conceals finer ecotype structure. [src: metabolic_capability_dependency]
- Enrich marine isolation metadata with depth, nutrient regime, geographic coordinates, and habitat measurements to test whether the apparently weak marine associations reflect metadata resolution. [src: metabolic_capability_dependency]
- Combine cluster assignments with transcriptomic, proteomic, or metabolomic measurements to test whether pathway differences produce distinct functional states rather than only genomic profiles. [src: metabolic_capability_dependency]
- Compare ecotype stability across independent genome collections to test whether clusters are portable across sampling locations and datasets. [src: metabolic_capability_dependency]

## Source

- [[summaries/metabolic_capability_dependency__REPORT]] — analysis of metabolic capability, pathway dependency, pangenome openness, and within-species metabolic ecotypes.

See also: [[summaries/nmdc_community_metabolic_ecology__REPORT]]

See also: [[summaries/pangenome_openness__REPORT]]

See also: [[summaries/pgp_pangenome_ecology__REPORT]]

See also: [[summaries/webofmicrobes_explorer__REPORT]]