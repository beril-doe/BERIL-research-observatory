---
type: "Summary"
description: "Reanalysis finds clinical sampling bias does not explain the weak environment signal."
doc_type: short
full_text: "sources/ecotype_env_reanalysis__REPORT.md"
---

# Ecotype Reanalysis — Environmental vs Human-Associated Species

## Summary

This reanalysis tests whether the weak relationship between environment and bacterial gene content in the [[concepts/phylogenetic-confounding]] results is caused by clinical sampling bias. Using genome-level environment classifications and the full set of available AlphaEarth-embedded genomes, it finds no evidence that environmental species have stronger environment–gene content correlations than human-associated species.

## Key findings

- Among 224 species selected for the analysis, 106 (47%) were classified as human-associated, 47 (21%) as environmental, and 71 (32%) as mixed/other based on the majority environment of their genomes.
- Environmental species had a median partial correlation of 0.051, compared with 0.084 for human-associated species. The Mann–Whitney test found no support for stronger environmental correlations (U=1536, p=0.83, one-sided).
- The continuous analysis also found no association between the fraction of environmental genomes and partial correlation strength (Spearman rho=-0.085, p=0.25), or between the fraction of human-associated genomes and correlation strength (rho=0.030, p=0.69).
- The null result persists despite environmental species having a higher rate of excluded NaN correlations: 10/47 (21%) for environmental species versus 7/100 (7%) for human-associated species.
- The median partial correlation across 183 species with valid results was 0.081, compared with 0.003 in the original analysis—a 27-fold difference attributed primarily to using all genomes rather than diversity-maximizing downsampling to a maximum of 250 genomes per species.

## Interpretation

The analysis confirms that clinical sampling bias is substantial in the [[entities/alphaearth-environmental-embeddings]] subset, but does not explain the weak environment signal in the ecotype analysis. Environmental embeddings showed stronger geographic differentiation in the preceding [[entities/env-embedding-explorer]], yet embedding geography may not correspond to ecological variation that determines whole-genome gene content. Conversely, human-associated species may exhibit genuine geographic epidemiological structure that produces environment–gene content associations.

The result agrees with the original [[entities/ecotype-analysis]] conclusion that phylogeny dominates over the coarse environment-versus-host comparison. The genome-level harmonized classification provides a more systematic test, but reaches the same null conclusion. The comparison is internally valid because both groups were analyzed with the same no-downsampling methodology, although the absolute correlation values are not directly comparable with the original analysis.

## Methodological considerations

The analysis used genome metadata, AlphaEarth embeddings, ANI distances, gene data, and gene-cluster memberships from [[entities/kbase-ke-pangenome]]. Partial correlations from `ecotype_analysis` were merged with environment classifications from [[entities/env-embedding-explorer]]. Classification by majority vote can misrepresent species containing diverse environments; however, the continuous environmental-fraction analysis also found no relationship. *Klebsiella pneumoniae* was excluded because gene-cluster extraction exceeded Spark’s `maxResultSize`.

The higher environmental NaN rate could affect group composition, but its direction would tend to remove environmental species with missing correlations rather than create the observed higher human-associated median. Genome count remains a possible confounder because larger species datasets may provide more power to detect weak correlations.

## Implications and open directions

The findings redirect attention from clinical bias toward biological specificity and methodological effects. Future work should compare downsampled and full-genome correlation extraction, test functional gene subsets such as transport and secondary metabolism, use structured ENVO terms from `env_broad_scale`, and control for genome count. These analyses could determine whether environment affects particular gene functions even when no strong whole-genome signal is detectable, a question relevant to [[concepts/genome-ecology-validation]].

## Related Concepts
- [[concepts/evidence-triangulation]]
- [[concepts/pangenome-integration]]
- [[concepts/environmental-resistome]]

## Entities
- [[entities/berdl]]
- [[entities/gtdb]]
