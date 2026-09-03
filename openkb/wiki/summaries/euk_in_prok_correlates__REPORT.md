---
type: "Summary"
description: "Shows photosynthetic eukaryotic contamination and exposes its cross-study batch confounding."
doc_type: short
full_text: "sources/euk_in_prok_correlates__REPORT.md"
---

# Metadata Correlates of Eukaryotic Contamination in NMDC Metagenomes

## Overview

This report analyzes eukaryotic DNA in 2,759 NMDC ReadbasedAnalysis runs from nine studies targeting prokaryotic metagenomes. It develops a run-level contamination estimate from native [[entities/gottcha2]] classifications, identifies environmental correlates and eukaryotic sources, and tests whether apparent environment effects generalize across studies. The central conclusion is that [[concepts/batch-confounding]] makes cross-study metadata associations unreliable, while within-study environmental contrasts reveal genuine biological variation.

## Key Findings

- Eukaryotic reads were detectable in **77%** of runs. The median eukaryotic fraction was **2.7%**, the mean was **13.3%**, and **20%** of runs exceeded **20%** eukaryotic reads.
- Among runs with detectable eukaryotic signal, plastid DNA represented a median of **100%** of that signal. Contamination was therefore dominated by photosynthetic environmental DNA, especially plant and algal chloroplasts, rather than animal-host DNA.
- Eukaryotic source composition varied coherently by matrix: freshwater samples were **99.5%** detectable with a plastid share of **1.00**; terrestrial soil samples were **55.7%** detectable with a plastid share of **0.43**; and plant-root samples were **100%** detectable with a plastid share of **0.03**, indicating stronger contributions from fungi and protists.
- Eukaryotic fraction differed significantly by matrix (Kruskal–Wallis **H=77.8, p=1.3×10⁻¹⁷**), but matrix and ecosystem effects are largely confounded with study identity.
- Cross-study prediction did not generalize: environment achieved **R²=−0.30** under out-of-study GroupKFold, while environment plus sequencing metadata achieved **R²=−0.39**. Out-of-study detection AUC was **0.56**, approximately chance. Environment explained no more variance than study identity alone.
- A cross-study depth association was observed (**Spearman ρ=−0.29, p=5.2×10⁻⁷, n=292**), with shallower samples carrying more eukaryotic DNA, but this result is not batch-controlled and is only suggestive.
- Within the single dominant [[entities/neon]] soil study, environmental variation was predictive after holding the study and protocol constant. Local vegetation differed strongly (**H=119.1, p=7.6×10⁻²¹**), as did geography (**H=310.4, p=2.4×10⁻⁴⁶**). Arctic tundra and herbaceous or wetland soils had higher eukaryotic fractions than temperate forests, cropland, or pasture.
- The within-study model achieved **5-fold R²=+0.17 ± 0.06**, contrasting with the cross-study out-of-study value of **−0.30**.

## Methodological Lessons

The report demonstrates a [[concepts/batch-confounding]] trap in public metagenomic collections: environmental categories may be 80–100% nested within individual studies, so apparently strong biome associations can reflect batch, protocol, or collection differences. Cross-collection analyses should use study-grouped validation or within-study contrasts rather than relying on random cross-validation, directly motivating attention to [[concepts/cross-study-generalization]].

Analyses should operate at the `workflow_run_id` level because NMDC pools multiple biosamples into individual ReadbasedAnalysis runs. The report identifies **1,067 of 2,759** runs as pooled and warns that biosample-level joins can create pseudo-replication. Classifier tables should first be aggregated to one row per run before joining metadata.

The NMDC classifiers are not interchangeable for eukaryote quantification. [[entities/kraken2]] and [[entities/centrifuge]] reference databases are prokaryote-restricted and yield approximately zero domain-level Eukaryota signals; [[entities/gottcha2]] is the only usable estimator in this analysis because it resolves eukaryotic and plastid signal.

## Interpretation

The measured signal is best interpreted as co-sampled environmental DNA rather than laboratory or animal-host contamination. Algal chloroplasts dominate freshwater samples, plant plastids and soil fungi or protists contribute in terrestrial samples, and root-associated fungi or protists dominate the plant-associated signal. The magnitude of the signal appears to be set primarily during collection by aboveground input and microbial biomass dilution, although this interpretation is based on relative, database-dependent abundance rather than an absolutely calibrated contamination measure.

The strongest biological evidence comes from the batch-controlled NEON soil analysis, where vegetation and geography predict eukaryotic fraction within one study. Because this result is demonstrated in one soil study and may still track sub-batches or sampling campaigns, its generalization to aquatic or host-associated metagenomes remains a hypothesis.

## Limitations and Open Directions

Only approximately nine studies contain the relevant read-based taxonomy, and one NEON soil study contributes about **43%** of runs. NMDC lacks key wet-lab metadata, including extraction kit, size fractionation, host-depletion method, and library-preparation details. More than one-third of runs are pooled, with environmental metadata inherited from a representative biosample, which can add label noise. [[entities/gottcha2]] fractions are database-dependent and should be treated as relative or ordinal estimates.

Future work should extend the pipeline to broader multi-study resources, test within-study effects in aquatic and plant-associated cohorts, acquire wet-lab metadata, and calibrate GOTTCHA2 estimates against spike-ins or an independent eukaryotic-fraction benchmark. These analyses would directly address [[concepts/cross-study-generalization]], [[concepts/coverage-limited-inference]], and measurement bias.

## Related Concepts
- [[concepts/evidence-triangulation]]
- [[concepts/phylogenetic-confounding]]
- [[concepts/pangenome-integration]]
- [[concepts/microbiome-ecotype-portability]]

## Entities
- [[entities/fitness-browser]]
- [[entities/gtdb]]
