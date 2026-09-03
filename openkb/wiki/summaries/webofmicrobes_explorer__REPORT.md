---
type: "Summary"
description: "Characterizes WoM metabolite-action semantics and links exometabolomics to fitness and pangenomes"
doc_type: short
full_text: "sources/webofmicrobes_explorer__REPORT.md"
---

# Web of Microbes Data Explorer

## Summary

This report characterizes a 2018 snapshot of the [[entities/web-of-microbes]] (WoM) exometabolomics database and evaluates its integration with the Fitness Browser, ModelSEED, GapMind, and pangenome collections. The snapshot contains 37 organisms, 589 tracked metabolites, 5 ENIGMA-funded projects, and 10 growth environments. The analysis finds that WoM can support [[concepts/multi-omics-integration]], but the absence of organism-level consumption observations limits analyses of nutrient uptake and [[concepts/gene-essentiality]].

## Key Findings

### Four action semantics

WoM uses distinct action codes for controls and organisms:

- Control action `D`: metabolite detected in the starting medium (742 observations).
- Control action `N`: metabolite not detected (1,023 observations).
- Organism action `I`: metabolite was already present and increased (1,338 observations).
- Organism action `E`: metabolite emerged despite being absent from the starting medium, indicating de novo production (1,155 observations).
- Organism action `N`: no significant change (7,509 observations).

`E` and `I` are mutually exclusive across all 10,744 observations. Thus, `I` represents amplification of an existing metabolite, whereas `E` represents novel biosynthetic output. No organism has a decrease or consumption action in this snapshot, although the original WoM schema and Kosina et al. (2018) describe decrease as a valid action. This makes [[concepts/metabolic-novelty]] measurable but prevents direct consumption-based cross-feeding analyses and highlights [[concepts/metabolite-production-utilization-decoupling]].

### Fitness Browser overlap

Two direct strain matches were found between WoM and the [[entities/fitness-browser]]:

- *Pseudomonas* sp. FW300-N2E3 → `pseudo3_N2E3`, with 5,854 genes and 211 experiments.
- *Pseudomonas* sp. GW456-L13 → `pseudo13_GW456_L13`, with 5,243 genes and 106 experiments.

Additional matches include *E. coli* BW25113 → `Keio`, representing the same strain, and *Synechococcus* PCC7002 → `SynE`, a genus-level match to PCC 7942. The *E. coli* WoM record is sparse, with only 12 observations focused on sulfur metabolism.

For pseudo3_N2E3, 19 metabolites produced or amplified in WoM are also tested by the Fitness Browser as carbon or nitrogen sources. Five are de novo products (`E`) and 14 are amplified metabolites (`I`). These links enable analyses asking which genes are important for utilizing metabolites that the same organism produces, connecting metabolite production to [[concepts/condition-dependent-essentiality]].

### ModelSEED compound links

Of 257 identified WoM compounds, 69 (26.8%) have definitive [[entities/modelseed]] links through exact name matching. Another 107 compounds (41.6%) have formula-only matches, bringing the total with any candidate link to 176 (68.5%). Formula matches are ambiguous: each WoM formula maps to an average of 8.4 ModelSEED molecules. Consequently, exact name matches support higher-confidence annotation, while formula matches should be treated as candidate sets requiring manual curation. This ambiguity contributes to the broader [[concepts/annotation-gap]].

### Variation in metabolic novelty

ENIGMA isolates grown in R2A medium show a two-fold range in the fraction of changed metabolites classified as de novo products:

- *Pseudomonas* GW456-L13: 34 emerged and 49 increased; 32.4% novel.
- *Pseudomonas* FW507-14TSA: 33 emerged and 44 increased; 31.4% novel.
- *Pseudomonas* FW300-N2A2: 32 emerged and 26 increased; 30.5% novel.
- *Acidovorax* GW101-3E06: 30 emerged and 48 increased; 28.6% novel.
- *Bacillus* FW507-8R2A: 16 emerged and 39 increased; 15.2% novel.

The report presents this 15–32% range as a potential phenotype for comparison with pangenome gene content, while noting that the small organism set is insufficient for robust statistical inference. This proposed comparison is an application of [[concepts/pangenome-integration]] and [[concepts/metabolic-novelty]].

### Pangenome coverage

All WoM organism genera have representation in the [[entities/kbase-ke-pangenome]] collection. The reported total genome counts include 2,557 for *Bacillus*, 449 for *Rhizobium*, 139 for *Pseudomonas fluorescens*, 88 for *Synechococcus*, 80 for *Phenylobacterium*, 79 for *Acidovorax*, 26 for *Zymomonas mobilis*, and 2 for *Escherichia coli*. Genus-level context is therefore broadly available, but strain-to-genome matching and species-level comparisons were not attempted.

## Data Coverage and Quality

The snapshot includes 6 biocrust isolates with 5,604 observations in BG11, 10 ENIGMA groundwater isolates with 1,050 observations in R2A, 4 other isolates, 10 triculture time-series entries, 2 native microbiome entries, 4 theoretical auxotroph predictions, and 1 control. Of the 589 tracked metabolites, 332 (56.4%) are unidentified with an `Unk_` prefix. Among the 257 identified compounds, 408 (69.3% of all 589 compounds) show at least one change across the database; the most active classes include amino acids and nucleotides.

Cross-collection quality is strongest for the two matched *Pseudomonas* strains, moderate for ModelSEED, and currently blocked for GapMind because internal pathway identifiers do not expose simple substrate or product names. A pathway-to-metabolite lookup table is needed to establish the GapMind connection, addressing a [[concepts/pathway-completeness]] and annotation problem.

## Interpretation and Limitations

The report partially supports the hypothesis that WoM can be integrated with genomic and fitness resources. Direct links exist for three organisms, 19 WoM-produced metabolites overlap Fitness Browser source conditions, 26.8% of identified compounds have definitive ModelSEED links, and all WoM genera have pangenome representation. However, the 2018 frozen export is small, comes from a single laboratory context, and lacks organism-level consumption data. The absence of decreases is especially consequential because it prevents testing whether consumed metabolites predict gene essentiality or resource competition.

The report suggests that newer GNPS2 WoM data or the Northen laboratory's defined-medium datasets may contain broader production and consumption measurements. The 110-organism NLDM study described by de Raad et al. (2022) is identified as a potentially important expansion.

## Recommended Follow-up

1. Obtain and ingest the current GNPS2 or Northen laboratory WoM dataset, particularly data containing consumption actions.
2. Build a GapMind pathway-to-metabolite mapping table from pathway substrates and products.
3. For the two direct *Pseudomonas* matches, compare Fitness Browser gene effects on carbon sources with WoM metabolite production.
4. Test whether the `E/(E+I)` novelty rate correlates with pangenome openness or accessory-gene content.
5. Re-run the WoM ingestion and cross-collection analyses when a newer dataset becomes available.

## Related Concepts
- [[concepts/metabolic-niche-partitioning]]
- [[concepts/black-queen-dynamics]]
- [[concepts/latent-metabolic-capabilities]]
- [[concepts/metabolic-ecotypes]]
- [[concepts/fitness-conservation]]
- [[concepts/phenotype-resolution-matching]]
- [[concepts/computational-reproducibility]]

- [[concepts/multi-omics-integration]]
- [[concepts/metabolic-novelty]]
- [[concepts/metabolite-production-utilization-decoupling]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/pangenome-integration]]
- [[concepts/annotation-gap]]

## Entities
- [[entities/berdl]]
- [[entities/gtdb]]
- [[entities/kegg]]
- [[entities/flux-balance-analysis]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/average-nucleotide-identity]]
