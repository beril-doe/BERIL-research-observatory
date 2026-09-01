---
type: "Summary"
description: "Harvard Forest warming reveals comparable DNA/RNA responses and carbon-cycle shifts."
doc_type: short
full_text: "sources/harvard_forest_warming__REPORT.md"
---

# Harvard Forest Long-Term Warming — DNA vs RNA Functional Response

## Overview

This report analyzes a 25-year, +5°C soil-warming experiment at [[entities/harvard-forest-barre-woods]] (NMDC study `nmdc:sty-11-8ws97026`; 42 biosamples). Using only `nmdc_metadata` and `nmdc_results`, it compares community composition, DNA and RNA functional-gene pools, carbon-cycling genes, and metabolite detection across control/heated and organic/mineral soils. The study reproduces the site's published Actinobacteria-up/Acidobacteria-down pattern and finds that DNA and RNA functional responses to chronic warming are comparable rather than transcript-dominated.

## Key Findings

- **Community composition:** In organic soil, [[entities/actinobacteria]] increased from 0.249 to 0.315 (log2 FC +0.341, q=0.049), while [[entities/acidobacteria]] decreased from 0.035 to 0.024 (log2 FC −0.549, q=0.049). Treatment explained 7.6% of genus-level Bray–Curtis variation (PERMANOVA p=0.069), whereas horizon explained 30.6% (p=0.0002).
- **DNA versus RNA response:** The proposed hypothesis that RNA would shift more strongly than DNA was not supported. In direct-sample sensitivity analyses, treatment R² values were 12.7% for DNA/mineral, 11.4% for RNA/mineral, and 10.0% for RNA/organic. The paired analysis was confounded because all organic samples were incubated and all mineral samples were direct. This finding informs [[concepts/dna-rna-functional-response]].
- **Carbon-cycling enrichment:** Heated-up carbon-cycling KOs were enriched in DNA from organic soil (Fisher OR=2.78, p=0.042), with 5 of 57 curated carbon-cycling hits among 433 total heated-up KOs. No corresponding FDR-significant enrichment appeared in the other pool-by-horizon combinations.
- **Methanotrophy and glyoxylate cycle:** RNA from heated soils showed nominal increases in [[entities/particulate-methane-monooxygenase]] genes pmoA (K10944; log2 FC +0.730 organic, +0.743 mineral) and pmoB (K10945; +0.669 organic, +0.880 mineral). In heated mineral soil, isocitrate lyase/aceA/icl (K01637) and malate synthase/aceB/glcB (K01638) both increased (p=0.037). These individual signals do not survive FDR across approximately 14,000 KOs but are directionally informative.
- **Horizon specificity:** Organic- and mineral-soil KO responses were only weakly correlated. DNA responses had Pearson r=0.075 and Spearman ρ=0.216; RNA responses had Pearson r=0.034 and Spearman ρ=0.120. Approximately 39% of DNA KOs were organic-only, mineral-only, or sign-flipping, supporting strong horizon-specificity at the genome-wide level and [[concepts/horizon-specific-warming-response]].
- **Metabolite richness:** Heated mineral samples contained fewer detectable [[entities/chebi]] metabolites than controls (155 versus 167 per sample; Mann–Whitney p=0.012). The organic-soil difference was in the same direction but not significant (160 versus 173; p=0.209). No individual metabolite passed BH-FDR.

## Interpretation

The results support a chronic-warming response involving both community turnover and functional restructuring. The failure of RNA to show a larger response than DNA may reflect long-term compositional equilibration after roughly 25 years of treatment, single-timepoint transcript variability, compositional dilution from a richer RNA KO repertoire, or broad transcript down-regulation under substrate depletion. Thus, the data do not exclude an early transient RNA-leading response, but suggest that DNA and RNA responses converge over multi-decadal timescales. This finding informs the cross-study concept of [[concepts/dna-rna-functional-response]].

The paired pmoA/pmoB increases suggest enhanced methane oxidation under warming in both horizons, while coordinated [[entities/glyoxylate-cycle]] activation in mineral soil is consistent with C2-substrate use or stress metabolism. These are hypotheses supported by nominal RNA-pool statistics rather than definitive genome-wide discoveries. The carbon-cycling enrichment in heated organic DNA and reduced heated-mineral metabolite richness fit a broader [[concepts/chronic-warming-substrate-depletion]] framework, but the study lacks quantitative metabolomics, soil chemistry, and proteomics to directly test substrate limitation.

The strong dependence of KO responses on soil horizon reinforces [[concepts/horizon-specific-warming-response]]. However, pmoA/pmoB responses were consistent across horizons, indicating that some functional signals may generalize beyond the dominant genome-wide horizon interaction.

## Design and Limitations

The experiment includes control/heated treatments, organic/mineral horizons, and direct/lab-incubated samples, but omics coverage is unbalanced. The DNA cohort contains 28 samples, the RNA cohort 39, and the paired DNA/RNA subset contains 25 samples. Organic-horizon DNA samples are all incubated, preventing a fully clean separation of horizon and incubation effects. Sampling occurred on one date (2017-05-24), and RNA annotations represent transcript-pool composition from contig annotations rather than TPM-quantified expression; this is relevant to interpreting [[entities/metatranscriptomics]] data. The `abiotic_features` fields are all zero for these samples, so the analysis cannot incorporate measured soil temperature, pH, or nitrogen. The project also excludes `nmdc_arkin` quantitative NOM, metabolomics, and [[entities/proteomics]] layers.

## Follow-up Directions

1. Add `nmdc_arkin` NOM, metabolomics, and proteomics data to test whether reduced metabolite richness reflects substrate depletion.
2. Resolve the identities of top differential ChEBI compounds and perform pathway enrichment.
3. Compare pmoA/pmoB responses with other warming studies, including SPRUCE peatland and Alaskan permafrost thaw datasets.
4. Track pmoA/pmoB-bearing MAGs to determine whether the response is concentrated in USCα methanotrophs or distributed across taxa.
5. Test whether an Actinobacteria-, glyoxylate-cycle-, and methanotrophy-associated “ruderal subset” explains part of the warming response.

## Source

Primary source: `harvard_forest_warming__REPORT`; NMDC study `nmdc:sty-11-8ws97026`. Analyses are documented in notebooks `01_sample_design.ipynb` through `08_synthesis.ipynb`.

## Related Concepts
- [[concepts/functional-redundancy]]
- [[concepts/genome-ecology-validation]]
- [[concepts/pathway-completeness]]
- [[concepts/redox-zonation]]
- [[concepts/organism-specificity]]

## Entities
- [[entities/fitness-browser]]
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/modelseed]]
