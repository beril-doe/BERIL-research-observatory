---
type: "Summary"
description: "Tests the clay shield hypothesis and identifies genomic sampling gaps in soils."
doc_type: short
full_text: "sources/soil_frontier_genomics__REPORT.md"
---

# Soil Microbial Dark Matter and the Clay Shield Null Result

## Overview

This preliminary report evaluates the global-scale clay shield hypothesis and introduces the [[entities/genomic-discovery-index]] (GDI) for identifying soil microbiome genomic frontiers. Clay-shield and GDI analyses are complete, while NB05 spatial validation and NB06 figures remain pending. [src: soil_frontier_genomics]

## Key Findings

### Clay shield hypothesis

The analysis included **5,441 soil samples** with clay content, mine proximity, nighttime lights, uranium, and functional gene counts. All three predictive model families produced negative out-of-sample R² values: Soil & Climate, −0.205 ± 0.197; Geochemical, −0.331 ± 0.071; and Industrial, −0.221 ± 0.042. [src: soil_frontier_genomics]

The shield-efficiency comparison also found no significant difference between low-clay soils (CV R² = −0.268) and high-clay soils (CV R² = −0.292): the difference was 0.024 with a 95% CI of −0.423 to 0.161. Clay was a consistent feature with importance of approximately 0.14, but did not improve predictive accuracy in high-clay soils. [src: soil_frontier_genomics]

The report therefore does not support the clay shield hypothesis at global scale. However, the negative predictive scores do not yet establish a biological null because they may reflect [[concepts/negative-out-of-sample-prediction]], spatial distributional shift associated with [[concepts/geospatial-coverage-gaps]], high-leverage test-fold outliers, or genuine unpredictability from the measured predictors. [src: soil_frontier_genomics]

### Genomic Discovery Index

The GDI is defined as **OTU Richness / (Mean Genome Completeness + 1)**, calculated in 1° spatial bins. Forest had a GDI of 902.36 and cropland 890.82, while grassland and wetland had lower values of 503.42 and 525.13, respectively. The report emphasizes that forest and cropland should be treated as jointly highest-GDI biomes because their 1.3% difference has not been tested with uncertainty estimates. [src: soil_frontier_genomics]

The index is provisional: it has no published precedent, combines richness and genome completeness into a single scalar, and can produce a GDI of 902 even when zero genomes are present if completeness is 0. Separate richness and completeness reporting, supported by a two-dimensional plot, may be more interpretable. [src: soil_frontier_genomics]

### Alkaline-soil discovery bias

Areas with GDI greater than 1000 had mean pH of 6.74, compared with 5.94 in mapped areas, a +0.8 pH-unit gap. This suggests a systematic under-sampling of alkaline soil microbiomes in public genomic databases, but the cause is unresolved. The difference could reflect fewer sequencing efforts in alkaline pH ranges rather than an assembly or annotation barrier specific to alkaline-soil microbes. This issue connects to [[concepts/spatial-sampling-effort]], [[concepts/resource-darkness]], and [[concepts/annotation-gap]]. [src: soil_frontier_genomics]

## Interpretation and Limitations

The report weakens a broad global claim that clay content shields soil microbial functional potential from industrial or geochemical stressors. Associations between clay and functional potential may still exist, but measured stressors did not predict functional gene counts out of sample at this scale. Spatial autocorrelation, [[concepts/batch-confounding]], and unmeasured confounders are possible explanations. [src: soil_frontier_genomics]

The central methodological issues connect to [[concepts/negative-out-of-sample-prediction]], [[concepts/geospatial-coverage-gaps]], [[concepts/resource-darkness]], and [[concepts/evidence-triangulation]]. In particular, the GDI should not be interpreted as a validated measure of genomic undersampling until richness is rarefaction-corrected and the index components are examined separately. [src: soil_frontier_genomics]

## Pending Validation

1. Decompose negative R² into distributional shift, outlier leverage, and genuine unpredictability using spatial blocking.
2. Recalculate GDI after uniformizing [[entities/16s-ribosomal-rna-sequencing]] sequencing depth through rarefaction.
3. Estimate bootstrap 95% CIs for biome-level GDI values.
4. Control the pH comparison for the number of 16S samples per pH bin to distinguish sampling effort from assembly or annotation gaps.
5. Re-run NB05 validations from BERIL Observatory 16S tables and [[entities/kbase-ke-pangenome]] completeness data; no local CSV output is available.
6. Report forest and cropland as jointly highest-GDI biomes unless uncertainty supports a ranked distinction.

[src: soil_frontier_genomics]

## Related Concepts
- [[concepts/coverage-limited-inference]]
- [[concepts/computational-reproducibility]]
- [[concepts/scalable-spark-data-analysis]]
