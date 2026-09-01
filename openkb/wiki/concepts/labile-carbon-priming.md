---
type: "Concept"
sources: ["summaries/lignin_community_enrichment__REPORT.md"]
description: "Labile carbon reshapes lignin-enriched communities toward copiotrophic taxa."
---

# Labile-Carbon Priming

## Definition

Labile-carbon priming is the ecological effect whereby readily metabolized carbon added alongside a recalcitrant substrate changes microbial community composition and potentially alters processing of the recalcitrant substrate. In the lignin enrichment experiment, the strongest evidence concerns community restructuring rather than a directly measured increase in lignin degradation. [src: lignin_community_enrichment]

## Evidence from lignin enrichment

Adding labile carbon with lignin produced a distinct bacterial assemblage relative to lignin-only enrichment. [[entities/acinetobacter]] increased from 25.2% in lignin-only cultures to 41.7% with labile carbon, while [[entities/pseudomonas]] declined from 39.3% to 23.0%. [[entities/aeromonas]] emerged as a major component at 20.2% in the lignin-plus-labile-carbon group, compared with 0.1% under lignin-only enrichment. [src: lignin_community_enrichment]

The labile-carbon treatment also reduced bacterial diversity: Shannon diversity declined from 3.16 under lignin-only enrichment to 2.41 with labile carbon, and Pielou’s evenness declined from 0.62 to 0.49. These results indicate stronger dominance by a smaller number of taxa rather than a uniformly broadened community. [src: lignin_community_enrichment]

CLR-based contrasts similarly identified Aeromonas and Shewanella as enriched under labile carbon, whereas Peredibacter and Comamonas were favored under lignin-only conditions. Because each group had n=3, individual pairwise tests had a minimum achievable p-value of 0.10; these taxon-level results are therefore effect-size evidence rather than FDR-significant discoveries. [src: lignin_community_enrichment]

## Proposed mechanism

The report interprets the shift as consistent with labile carbon relaxing stringent selection for specialist lignin-associated organisms and enabling fast-growing copiotrophs to co-dominate. This mechanism is plausible but remains a hypothesis in this dataset because lignin disappearance, aromatic intermediates, enzyme activity, and pathway expression were not directly measured. [src: lignin_community_enrichment]

The fungal response was also treatment-specific: lignin-only enrichment favored Fusarium and Fusicolla, whereas lignin plus labile carbon favored Chrysosporium and Aspergillus. However, ITS replicate Bray–Curtis distances reached 0.99–1.00 for several Round 2 groups, so the fungal component provides weaker evidence than the bacterial result. [src: lignin_community_enrichment]

## Persistence across passages

The labile-carbon effect extended beyond the initial enrichment. Communities with a lignin-plus-labile-carbon Round 1 history remained more Acinetobacter-dominant in Round 2 and showed elevated Enterobacter relative to communities with a lignin-only history. Round 1 history explained 58.9% of Round 2 bacterial community variance (F=14.31, p=0.002), whereas the current Round 2 carbon source explained 32.7% (F=4.85, p=0.018). [src: lignin_community_enrichment]

This persistence connects labile-carbon priming to [[concepts/ecological-memory]] and [[concepts/metabolic-competitive-exclusion]]. The result suggests the hypothesis that early access to labile carbon establishes a community state that resists convergence under later conditions, rather than producing only a transient physiological response. [src: lignin_community_enrichment]

## Relation to broader concepts

Labile-carbon priming should be distinguished from [[concepts/capability-versus-kinetics]]: enrichment of a taxon associated with aromatic catabolism demonstrates ecological selection, not necessarily faster lignin turnover. It also motivates [[concepts/multi-omics-integration]], because linking community shifts to metagenomic pathway presence, transcript activity, protein abundance, metabolite flux, and direct lignin chemistry would test whether compositional priming produces a functional priming effect. [src: lignin_community_enrichment]

The source report places this result in the context of established soil-ecology work on interactions between simple and recalcitrant carbon, while emphasizing that the present experiment demonstrates restructuring at the community level rather than directly confirming enhanced lignin degradation. [src: lignin_community_enrichment]

## Tensions

- Labile carbon is commonly expected to stimulate broader microbial activity, but in this experiment it reduced bacterial Shannon diversity from 3.16 to 2.41 and evenness from 0.62 to 0.49. The data therefore support selective dominance by copiotrophic taxa, not increased evenness. [src: lignin_community_enrichment]
- Current carbon conditions still explained 32.7% of Round 2 bacterial variance, while Round 1 history explained 58.9%. Thus labile-carbon effects are both condition-dependent and historically persistent; the relative contribution of present conditions versus history should not be treated as universal. [src: lignin_community_enrichment]
- Bacterial evidence is reproducible, with reported within-group Bray–Curtis distance of 0.09, whereas fungal evidence is highly variable, with Round 2 distances reaching 0.99–1.00. Cross-kingdom generalization is therefore not warranted. [src: lignin_community_enrichment]

## Open Directions

- Pair n>=5 replicate cultures with direct lignin-loss measurements and aromatic-metabolite profiling to test whether the Acinetobacter/Aeromonas shift changes lignin-processing rates. [src: lignin_community_enrichment]
- Map Round 1 and Round 2 taxa to [[entities/kbase-ke-pangenome]] and quantify beta-ketoadipate, protocatechuate, and other aromatic-catabolism genes to distinguish functional capacity from realized activity. [src: lignin_community_enrichment]
- Add metatranscriptomics, proteomics, and metabolomics to test whether labile carbon changes pathway expression and metabolite exchange; this would connect priming to [[concepts/multi-omics-integration]]. [src: lignin_community_enrichment]
- Sample intermediate time points across both passages to determine how quickly labile-carbon community states form and how long they persist. [src: lignin_community_enrichment]

## Related source

- [[summaries/lignin_community_enrichment__REPORT]]