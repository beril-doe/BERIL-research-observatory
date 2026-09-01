---
type: "Concept"
sources: ["summaries/harvard_forest_warming__REPORT.md"]
description: "Soil horizons impose distinct microbial warming responses."
---

# Horizon-Specific Microbial Responses to Soil Warming

## Definition

[[concepts/horizon-specific-warming-response]] describes the pattern in which microbial community, functional-gene, and metabolite responses to warming differ between soil horizons rather than following one uniform profile throughout the soil column. In the Harvard Forest Barre Woods experiment, horizon-specificity was a strong genome-wide pattern, although selected functions—especially methanotrophy—responded similarly in organic and mineral soil. [src: harvard_forest_warming]

## Evidence from Harvard Forest

The 25-year +5°C warming experiment at [[entities/harvard-forest-barre-woods]] compared control and heated organic and mineral horizons across DNA, RNA, taxonomy, and metabolite measurements. [src: harvard_forest_warming]

- Horizon explained 30.6% of genus-level Bray–Curtis variation in a PERMANOVA (p=0.0002), while the four-cell treatment-by-horizon design explained 41% (p=0.0002). [src: harvard_forest_warming]
- In organic soil, Actinobacteria increased from 0.249 in controls to 0.315 under warming (log2 FC +0.341, BH q=0.049), while Acidobacteria decreased from 0.035 to 0.024 (log2 FC −0.549, BH q=0.049). No phylum-level changes remained after FDR correction in mineral soil. [src: harvard_forest_warming]
- Warming-associated KO effects were weakly correlated between organic and mineral horizons: DNA responses had Pearson r=0.075 and Spearman ρ=0.216, while RNA responses had Pearson r=0.034 and Spearman ρ=0.120. [src: harvard_forest_warming]
- Approximately 39% of DNA KOs were classified as organic-only, mineral-only, or sign-flipping responders, indicating that a substantial fraction of functional responses depended on horizon. [src: harvard_forest_warming]

These results support [[concepts/multi-omics-integration]]: the horizon effect is visible in taxonomic composition, DNA functional potential, RNA-pool composition, and metabolite detection, but the magnitude and resolution of the signal differ among layers. [src: harvard_forest_warming]

## Shared Versus Horizon-Specific Functions

The curated 62-KO carbon-cycling set was not differentially enriched among horizon-specific response classes; all reported odds ratios were below 1 with p>0.87. [src: harvard_forest_warming] This indicates that carbon-cycling genes did not primarily explain the genome-wide treatment-by-horizon interaction in this analysis. [src: harvard_forest_warming]

In contrast, pmoA and pmoB, which encode the alpha and beta subunits of particulate methane monooxygenase, increased in heated RNA pools in both horizons. pmoA showed log2 fold changes of +0.730 in organic soil and +0.743 in mineral soil, while pmoB showed +0.669 and +0.880, respectively; the associated p-values ranged from 0.009 to 0.054 and were nominal rather than FDR-significant across the approximately 14,000-KO test space. [src: harvard_forest_warming] This cross-horizon direction suggests a potentially shared warming-associated methanotrophy response, but it remains a hypothesis requiring replication and quantitative expression or activity measurements. [src: harvard_forest_warming]

The glyoxylate cycle showed a more localized response: isocitrate lyase (aceA/icl; K01637) and malate synthase (aceB/glcB; K01638) were both upregulated in heated mineral RNA (log2 FC +0.460 and +0.268; p=0.037 for each), without an equivalent reported organic-horizon signal. [src: harvard_forest_warming] This contrast illustrates how a shared broad process—carbon stress or altered substrate use—can be expressed through different functions in different horizons. [src: harvard_forest_warming]

## Metabolite Pattern

Heated mineral samples had a mean of 155 detectable ChEBI metabolites per sample, compared with 167 in control mineral samples; the treatment contrast had Mann–Whitney p=0.012. [src: harvard_forest_warming] Organic samples showed the same direction, with 160 detectable metabolites in heated samples versus 173 in controls, but the contrast was not significant (p=0.209). [src: harvard_forest_warming] Because the study measured metabolite presence rather than quantitative concentrations and did not resolve the top ChEBI labels, the pattern supports—but does not establish—a horizon-dependent effect of warming on substrate availability or turnover. [src: harvard_forest_warming]

This observation connects horizon-specific response to [[concepts/chronic-warming-substrate-depletion]]: mineral-soil metabolite loss may be consistent with faster turnover or reduced substrate pools, but direct chemical measurements are needed to distinguish those mechanisms. [src: harvard_forest_warming]

## Interpretation and Scope

The most direct interpretation is that soil horizon is an ecological context that filters both which microbial lineages respond to chronic warming and which functions are expressed or retained. [src: harvard_forest_warming] Organic and mineral soils differ in resources, physicochemical conditions, and resident communities, but this report did not include usable in-lakehouse measurements of soil temperature, pH, or nitrogen because `abiotic_features` was all zeros for these samples. [src: harvard_forest_warming]

The horizon comparison is also constrained by experimental coverage: all organic-horizon DNA samples were lab-incubated, whereas mineral DNA samples were direct, so incubation cannot be fully separated from horizon in the DNA analysis. [src: harvard_forest_warming] The report therefore provides strong evidence for horizon-specific associations, but causal attribution to horizon chemistry or microenvironment remains incomplete. [src: harvard_forest_warming] This limitation exemplifies [[concepts/batch-confounding]] and [[concepts/coverage-limited-inference]].

The findings should not be generalized automatically to all soils or warming experiments. The experiment used one sampling date (2017-05-24), the DNA cohort contained 28 samples, and the RNA cohort contained 39 samples, limiting seasonal inference and per-KO statistical power. [src: harvard_forest_warming] Cross-site comparison with other warming studies is needed to determine whether the shared methanotrophy signal is portable or specific to Harvard Forest. [src: harvard_forest_warming]

## Relation to the Source Report

The complete evidence, sample design, statistical results, and proposed follow-up analyses are summarized in [[summaries/harvard_forest_warming__REPORT]]. [src: harvard_forest_warming]

## Open Directions

- Use quantitative soil chemistry and `nmdc_arkin` metabolomics, NOM, and proteomics data to test whether mineral-horizon metabolite loss reflects substrate depletion, altered production, or consumption. [src: harvard_forest_warming]
- Reanalyze direct samples with models that explicitly separate horizon, incubation, treatment, and their interactions to determine which DNA and RNA differences remain after confounding control. [src: harvard_forest_warming]
- Compare pmoA/pmoB responses across Harvard Forest, SPRUCE peatland, and Alaskan permafrost datasets to test whether cross-horizon methanotrophy activation is reproducible across ecosystems. [src: harvard_forest_warming]
- Link pmoA/pmoB-bearing MAGs to taxonomic and horizon metadata to identify the organisms responsible for the shared signal. [src: harvard_forest_warming]
- Collect seasonal and depth-resolved samples with matched DNA, RNA, metabolite, and environmental measurements to distinguish persistent horizon effects from time-specific responses. [src: harvard_forest_warming]