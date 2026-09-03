---
sources: ["summaries/microbeatlas_metal_ecology__REPORT.md", "summaries/lab_field_ecology__REPORT.md", "summaries/ibd_phage_targeting__REPORT.md", "summaries/enigma_contamination_functional_potential__REPORT.md", "summaries/enigma_carbon_census_1__REPORT.md", "summaries/bacdive_metal_validation__REPORT.md"]
type: "Dataset"
description: "Bacterial and archaeal database used to validate metal-tolerance predictions"
---

# BacDive

BacDive is a bacterial and archaeal database providing standardized strain information, including taxonomy, isolation environments, and phenotype records. [src: bacdive_metal_validation]

## Role in the Metal-Tolerance Validation Study

The [[summaries/bacdive_metal_validation__REPORT]] used BacDive isolation-source metadata to test whether genome-based scores from the [[entities/metal-fitness-atlas]] reflect real environmental metal adaptation. [src: bacdive_metal_validation]

The analysis began with 97,334 BacDive strains and linked 42,227 strains (43.4%) to GTDB pangenome species and their metal-tolerance scores. [src: bacdive_metal_validation] Exact species-name matching linked 33,535 strains (34.5%), while removal of GTDB suffixes recovered 8,692 additional strains (8.9%). [src: bacdive_metal_validation] The bridge covered 6,426 unique GTDB species, and 25,089 linked strains had isolation-source metadata. [src: bacdive_metal_validation]

## Environmental Evidence

BacDive strains isolated from heavy-metal contamination sites had metal-tolerance scores one standard deviation above the environmental baseline (Cohen’s d = +1.00, Mann–Whitney p = 0.006, n = 10). [src: bacdive_metal_validation] The reported association also appeared for waste/sludge, all contamination, and industrial environments, with Cohen’s d values of +0.57, +0.43, and +0.20, respectively. [src: bacdive_metal_validation]

The contamination signal remained significant within Pseudomonadota (delta = +0.040, p < 0.001) and Actinomycetota (delta = +0.035, p < 0.001), but not within Bacillota or Bacteroidota. [src: bacdive_metal_validation] These results support [[concepts/genome-ecology-validation]] and [[concepts/environmental-metal-tolerance]], while the phylum-specific differences leave [[concepts/phylogenetic-amr-structure]]-like concerns about phylogenetic structure relevant to interpretation. [src: bacdive_metal_validation]

## Phenotype Coverage and Limitations

Only 24 BacDive metal-utilization records matched strains with metal-tolerance scores: 8 positive and 16 negative results. [src: bacdive_metal_validation] The comparison was inconclusive (Mann–Whitney p = 0.14, Cohen’s d = -0.57) and was considered underpowered. [src: bacdive_metal_validation]

Species-level matching left 55,107 BacDive strains (56.6%) unmatched to a GTDB species, partly because the taxonomies use different species boundaries. [src: bacdive_metal_validation] The report proposes direct GCA-accession matching to pangenome genome IDs as a way to improve coverage. [src: bacdive_metal_validation] BacDive also represents culturable and described strains rather than the full diversity of environmental bacteria, introducing potential culture-collection bias. [src: bacdive_metal_validation]

## Related Resources

- [[entities/gtdb]] — pangenome taxonomy used for species matching.
- [[entities/metal-fitness-atlas]] — source of the genome-based metal-tolerance scores.
- [[concepts/pangenome-integration]] — integration of strain records with pangenome data.
- [[concepts/evidence-triangulation]] — complementary validation using ecology and phenotype data.
- [[summaries/bacdive_metal_validation__REPORT]] — source report for the BacDive bridge and validation analyses.

See also: [[summaries/enigma_carbon_census_1__REPORT]]

See also: [[summaries/enigma_contamination_functional_potential__REPORT]]

See also: [[summaries/ibd_phage_targeting__REPORT]]

See also: [[summaries/lab_field_ecology__REPORT]]

See also: [[summaries/microbeatlas_metal_ecology__REPORT]]