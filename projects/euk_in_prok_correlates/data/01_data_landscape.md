# Data Landscape — can we exceed 16 studies? (2026-07-10)

Motivated by the finding that the analysis cohort spans only ~16 studies and that environment is
confounded with study (out-of-study R² = −0.21). Question: is there a broader / more recent /
more comprehensive on-system source of **per-sample eukaryotic read fraction** across many studies?

## Sources that provide a per-sample read-based eukaryotic fraction (the response variable)

| Source | Studies | Samples | Euk-positive files | Notes |
|---|---|---|---|---|
| `kbase.nmdc_arkin` gottcha/kraken/centrifuge (**used**) | 16 (GOLD ids) | 5,871 | Euk 359 / plastid 1,162 | curated Arkin snapshot |
| `nmdc.results` gottcha2/kraken2/centrifuge | **9** (sty- ids) | 4,770 | Euk 807 / plastid 1,787 | native NMDC results; **67% one soil study** (`sty-11-34xj1150`, 3,208 samples); slightly more euk-positive but FEWER independent studies |

Both are the **same underlying NMDC metagenome program** — few studies, one dominant soil study.
Per-study concentration (nmdc.results): 3,208 / 454 / 406 / 317 / 168 / 139 / 36 / 28 / 14.
Switching tables does **not** add study diversity or break the environment↔study confounding.

Processing flags in `nmdc.metadata.biosample_to_workflow_run` (`has_extraction`, `has_filtration`,
`has_library_prep`, `has_pooling`, `has_subsampling`) are near-constant on the classified set
(`has_filtration` is **all false**; `has_extraction` almost always true) → no usable wet-lab variance.

## Metadata ceiling (no read-based taxonomy attached)
`nmdc.metadata`: **84 studies, 16,640 biosamples, 7,752 metagenomics** samples — but read-based
taxonomic classification exists for only ~9–16 of those studies. The rest are amplicon (16S),
metabolomics, NOM, or metagenomes without the ReadbasedAnalysis product.

## Other on-system collections checked — none provide per-sample euk read fraction across many studies
- `kescience.mgnify` — MGnify **Genomes catalog** (genome/species/pangenome/biome): a MAG *reference*, not per-sample read profiles.
- `refdata.spire`, `refdata.smag`, `refdata.jgi_gem` — MAG collections (genome-level), no per-sample euk read fraction.
- `refdata.tara_ocean` — single study (size-fractionated).
- `refdata.emp_16s` — 16S amplicon (prokaryote-targeted primers); cannot quantify eukaryotic read fraction.
- `kbase.nmdc_neon`, `kbase.nmdc_mags` — NMDC MAG/bin catalogs, not read-based domain profiles.

## Conclusion
On this system, a per-sample eukaryotic read fraction only exists for the NMDC metagenome program,
which is a **few-study, one-dominant-study** collection. No on-system source escapes the
environment↔study confounding. To test metadata correlates of eukaryotic contamination across
**many independent studies** we would need to either:
1. **Bring in a many-study raw-read resource** — e.g. the SPF collection (Eisenhofer/Alberdi/Woodcroft
   2026; 136,284 metagenomes across thousands of studies) or compute euk fraction ourselves from a
   multi-study read set (external; not currently on BERDL); or
2. **Reframe to what NMDC can honestly answer** — a within-collection descriptive/QC characterization
   (euk fraction and plant-vs-host source by biome), explicitly caveated as confounded with study,
   not a causal metadata-correlate claim; or
3. **User supplies** a curated multi-study table (euk fraction or raw reads + collection/processing
   metadata) for the correlate analysis.
