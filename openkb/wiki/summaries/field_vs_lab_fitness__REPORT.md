---
type: "Summary"
description: "Tests whether field-relevant fitness effects predict gene conservation in DvH."
doc_type: short
full_text: "sources/field_vs_lab_fitness__REPORT.md"
---

# Field vs Lab Fitness in *Desulfovibrio vulgaris* Hildenborough

## Overview

This report tests whether gene fitness importance under field-relevant conditions predicts pangenome conservation differently from fitness importance under laboratory conditions. It analyzes 757 *Desulfovibrio vulgaris* Hildenborough experiments from [[entities/random-barcode-transposon-sequencing]]/Fitness Browser data alongside pangenome classifications from KBase. The study also surveys ENIGMA CORAL for complementary data and characterizes conservation patterns across 52 ICA fitness modules. [src: field_vs_lab_fitness]

The central conclusion is that **fitness importance generally predicts conservation more strongly than ecological condition type**. Field-stress and field-core genes are significantly enriched in the core genome, but lab-nutrient genes show a similar enrichment, and field-specific genes are not more conserved than lab-specific genes. [src: field_vs_lab_fitness]

## Data and classification

- The Fitness Browser collection contains 757 DvH experiments covering 2,741 genes; 337 experiments were classified as field-related and 420 as laboratory-related. [src: field_vs_lab_fitness]
- Experiments were assigned to six categories: lab-nutrient (237), field-core (204), lab-other (140), field-stress (78), heavy-metals (55), and lab-antibiotic (43). [src: field_vs_lab_fitness]
- The conservation analysis included 2,725 non-essential genes with both fitness and pangenome links. Their overall core-genome fraction was 76.3%. A further 678 essential genes lacked fitness measurements because transposon mutants were not recovered; 80.1% of these genes were core. [src: field_vs_lab_fitness]
- ENIGMA CORAL contains no DvH fitness data. Its 4,346 field samples, geochemistry measurements, and 213,044 ASVs may support future ecological analyses but cannot currently provide DvH gene-level fitness evidence. [src: field_vs_lab_fitness]

## Main findings

### Condition-class conservation

Genes with strong fitness defects, defined as fitness < -2, differed in conservation by condition class:

| Condition class | Important genes | Core fraction | Odds ratio vs baseline | FDR q |
|---|---:|---:|---:|---:|
| Field-stress | 298 | 83.6% | 1.58 | 0.026 |
| Field-core | 376 | 82.4% | 1.46 | 0.026 |
| Lab-other | 292 | 81.5% | 1.37 | 0.073 |
| Lab-nutrient | 452 | 81.4% | 1.36 | 0.037 |
| Lab-antibiotic | 109 | 73.4% | 0.86 | 0.49 |
| Heavy-metals | 198 | 71.2% | 0.77 | 0.14 |

Field-stress, field-core, and lab-nutrient fitness-important genes are significantly enriched in the core genome after BH-FDR correction. This supports a link between [[concepts/condition-dependent-essentiality]] and conservation, but it does not show that field relevance alone is the determining factor. [src: field_vs_lab_fitness]

### Specificity does not favor field importance

The field-specific and lab-specific gene sets were small and showed an unexpected pattern:

- Lab-specific genes: 50 genes, 96.0% core.
- Field-specific genes: 52 genes, 88.5% core.
- Field-biased genes: 89 genes, 83.1% core.
- Universally important genes: 352 genes, 79.8% core.
- Neutral genes: 2,083 genes, 74.5% core.

Lab-specific genes were more core than field-specific genes, although the difference was not statistically significant (Fisher exact OR = 0.32, p = 0.27). Universally important genes were significantly more core than neutral genes (OR = 1.35, p = 0.033). Thus, the strongest supported pattern is that **any substantial fitness effect is associated with conservation**, rather than that field-specific importance is uniquely conserved. [src: field_vs_lab_fitness]

### Fitness weakly predicts core status

Cross-validated logistic regression showed that fitness effects alone were weak predictors of whether a gene belonged to the core genome:

| Model | Cross-validated AUC | Standard deviation |
|---|---:|---:|
| Field fitness only | 0.517 | 0.052 |
| Lab fitness only | 0.531 | 0.052 |
| Field + lab fitness | 0.548 | 0.053 |
| Full model including gene length | 0.645 | 0.068 |

Gene length was substantially more predictive than either field or lab fitness. The report notes that length may be confounded with both transposon measurement quality and core status. These results qualify interpretations of [[concepts/fitness-conservation]]: measured fitness effects have biological signal, but limited standalone power for predicting binary core/auxiliary membership. [src: field_vs_lab_fitness]

### Threshold robustness

The conservation pattern persisted across fitness thresholds from -1 to -3. Field-stress genes had the highest core fraction at every tested threshold, while heavy-metal genes were consistently among the least conserved. At the primary -2 threshold, field-stress genes were 83.6% core and heavy-metal genes were 71.2% core. The lab-antibiotic result was more variable because of its smaller sample size. [src: field_vs_lab_fitness]

### Module-level analysis

Across 52 ICA fitness modules, the mean core fraction was 0.886 and the median was 1.000. Module conservation was not significantly correlated with field activity (Spearman rho = 0.071, p = 0.62). Using the mean core fraction as the partition threshold produced four groups:

- 21 ecological modules: field-active and conserved; mean core fraction 0.980.
- 17 conserved-quiet modules: weak field activity but conserved; mean core fraction 0.983.
- 5 field-variable modules: field-active and less conserved; mean core fraction 0.829.
- 9 lab modules: weak field activity and less conserved; mean core fraction 0.516.

The ecological modules contain 239 genes, including 52 unannotated genes that are candidates for environmental adaptation functions. The low conservation of the nine lab modules suggests that accessory-genome modules can respond preferentially to laboratory-type conditions, but the lack of an overall activity-conservation correlation means this is not a general field-versus-lab rule. [src: field_vs_lab_fitness]

## Biological interpretation

The report identifies antibiotic and heavy-metal fitness-important genes as the least conserved categories. It interprets this as consistent with resistance functions being disproportionately accessory and potentially mobile, although genomic-location and mobility analyses were not performed here. [src: field_vs_lab_fitness]

The heavy-metal result is particularly notable because heavy-metal conditions were grouped broadly with field-relevant conditions, yet genes important under cobalt, nickel, zinc, copper, manganese, selenium, molybdate, tungstate, and aluminum were only 71.2% core. By contrast, uranium- and mercury-related conditions were included in field-stress, whose important genes were 83.6% core. The report suggests the hypothesis that specific metal-resistance mechanisms are more accessory, whereas uranium- and mercury-associated phenotypes may involve broadly conserved stress, DNA-repair, or sulfate-reduction functions. [src: field_vs_lab_fitness]

Overall, the findings support a [[concepts/core-accessory-resistance]] distinction in which general metabolic and stress functions tend to be conserved, while some resistance functions are more variable. The report cautions that this interpretation is based on a single organism and a relatively small pangenome. [src: field_vs_lab_fitness]

## Hypothesis outcomes

- **H1 partially supported:** Field-stress and field-core genes were significantly more conserved than baseline, but lab-nutrient genes were also enriched, and field-specific genes were not significantly more conserved than lab-specific genes. [src: field_vs_lab_fitness]
- **H2 not supported:** Module conservation did not correlate significantly with field activity, although low-conservation lab modules emerged under the revised classification. [src: field_vs_lab_fitness]
- **H3 partially supported:** Ecological modules were highly conserved and included 52 unannotated genes among 239 members, providing candidates for environmental adaptation studies. [src: field_vs_lab_fitness]

## Limitations

The analysis excludes 678 essential genes without fitness measurements, uses a single organism with a relatively small pangenome, and relies on manually mapped experimental condition labels. The binary core/auxiliary classification may compress effect sizes, and field-specific and lab-specific groups contain only 50–52 genes each. Fitness effects are also correlated between field and lab conditions (approximately r ~ 0.7), and gene length is confounded with both measurement quality and conservation. [src: field_vs_lab_fitness]

## Follow-up directions

1. Extend the field-versus-lab framework to other organisms with both environmental relevance and fitness data, such as *Pseudomonas* FW300 strains.
2. Replace binary core/auxiliary status with quantitative gene-cluster prevalence across genomes.
3. Combine ENIGMA CORAL community and geochemistry data with DvH ecological measurements to test whether field abundance tracks relevant conditions.
4. Determine whether accessory antibiotic and metal-resistance genes are mobile, recently acquired, or shared with co-occurring organisms.
5. Use continuous fitness scores rather than binary fitness-important calls in predictive models.

These directions connect the report to broader [[concepts/condition-dependent-essentiality]], [[concepts/pangenome-integration]], [[concepts/fitness-conservation]], and [[concepts/environmental-metal-tolerance]] questions.

## Related Concepts
- [[concepts/horizontal-gene-transfer]]
- [[concepts/organism-specificity]]
- [[concepts/method-concordance]]
- [[concepts/coverage-limited-inference]]
- [[concepts/environmental-occupancy-vs-activity]]
- [[concepts/evidence-triangulation]]
