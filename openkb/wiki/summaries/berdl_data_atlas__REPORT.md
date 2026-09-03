---
type: "Summary"
description: "BERDL inventory maps data depth, cross-tenant bridges, reuse, and validated synergies."
doc_type: short
full_text: "sources/berdl_data_atlas__REPORT.md"
---

# BERDL Data Atlas — Summary

## Overview

The BERDL Data Atlas provides a comprehensive inventory of the lakehouse, mapping 1,740 deduplicated tables across 119 databases, 17 tenants, 10 funding agencies or programs, and 17 biological topics. It combines catalog metadata, data-volume measurements, canonical join-key analysis, and a README-based audit of 66 BERIL projects to characterize both the depth of available data and the extent of cross-program reuse.

The atlas is primarily a resource for [[concepts/multi-omics-integration]] and [[concepts/pangenome-integration]]: it identifies where users can find data, which identifiers connect collections, which cross-tenant combinations have already been used, and which high-value analyses remain unexplored.

## Major Findings

- BERDL contains data at billion-row scale, including 1,011,650,903 KBase pangenome gene rows, 475,217,233 UniRef100 clusters, 241,070,489 AlphaFold structures, 260,831,135 MicrobeAtlas OTU-count rows, 75,119,498 metatranscriptomic abundance rows, 27,410,721 FitnessBrowser measurements, and 39,994,988 PubMed records.
- DOE-BER is the broadest funder, contributing approximately 63% of tables and covering all 15 mapped biological topics. DOE BRaVE, ARPA-H, NSF, DOE-FE, and DOI provide narrower but distinctive resources, especially phage, clinical, marine, and produced-water data.
- The catalog contains 536 schema-level cross-tenant bridges based on 29 canonical keys. The most widely distributed keys are `sample_id`, `genome_id`, `ncbi_taxon_id`, `feature_id`, and `ec_number`.
- Cross-tenant use is already substantial: 51 of 66 audited BERIL projects, or 77%, use multiple tenants. The `kbase`–`kescience` axis dominates, accounting for 36 cross-tenant projects, largely through pangenome and fitness joins.
- Schema connectivity does not guarantee compatible values. The atlas explicitly distinguishes theoretical bridges from value-space validation and notes that most proposed use cases still require live-cluster testing.

## Validated Use Case: Fitness and Structure

The strongest demonstrated synergy is UC1, a structural fitness atlas linking FitnessBrowser measurements to AlphaFold models. The initial proposed join was corrected after SQL probing: FitnessBrowser does not expose `protein_id`; the working path is:

```text
genefitness --(orgId, locusId)--> besthitswissprot
besthitswissprot.sprotAccession --(UniProt accession)--> alphafold_entries
```

The live-cluster sample produced 55,454 genes across 48 organisms with both fitness data and an AlphaFold model, representing 22,303 distinct AlphaFold models. SwissProt-best-hit coverage in AlphaFold was 99.5% (78,753 of 79,180 best hits). The joined cohort includes 6,635 essential genes, 8,271 strong-defect genes, 10,950 moderate-defect genes, 29,467 mild-defect genes, and 131 genes with no defect under the stated fitness classification.

This result supports a concrete [[concepts/structural-novelty]] and structure–function analysis opportunity, while the report cautions that AlphaFold entries lack per-residue pLDDT and structural-feature data needed for a fuller analysis.

## Untapped Synergies

Five high-leverage bridges had no realized use at audit time:

1. **`kescience` ↔ `refdata`** — structural fitness signatures using AlphaFold and related reference data.
2. **`enigma` ↔ `phagefoundry`** — subsurface prophages, metal resistance, and contamination gradients.
3. **`kbase` ↔ `refdata`** — GTDB clade and KBase pangenome reconciliation, including gene-flow questions.
4. **`nmdc` ↔ `protect`** — environmental distributions and biogeochemical correlates of clinically relevant pathogens.
5. **`nmdc` ↔ `refdata`** — completeness and geographic or sample-type gaps in ENVO ontology annotation.

UC2–UC5 are hypotheses or proposed analyses rather than established findings because their identifier overlap has not yet been validated against live values. They represent opportunities in [[concepts/environmental-metal-tolerance]], [[concepts/subsurface-microbial-specialization]], [[concepts/pangenome-integration]], and [[concepts/annotation-gap]].

## Data Landscape

The atlas organizes BERDL resources into several connected layers:

- **Genomes and pangenomes:** KBase genomes, GTDB species clades, gene clusters, ENIGMA genomes, MAGs, and pathogen or phage-host genome depots.
- **Proteins and structures:** UniProt, UniRef50/90/100, AlphaFold, and experimental PDB structures.
- **Phenotypes and fitness:** FitnessBrowser, BacDive, carbon-source phenotypes, and Web of Microbes growth observations.
- **Environmental and community data:** NMDC multi-omics, MicrobeAtlas 16S profiles, ENIGMA field samples, USGS and NETL produced-water data, Planet Microbe samples, and AlphaEarth embeddings.
- **Viruses and mobile elements:** MetaVR, IMG/VR, and PhageFoundry host-specific catalogs.
- **Biochemistry, ontology, and literature:** ModelSEED reactions and compounds, Rhea, GO and EC terms, PaperBLAST, and PubMed.

The report emphasizes that the value of small collections such as Planet Microbe, NETL, and USGS is not table count but unique sample provenance and potential use as external validation sets.

## Interpretation

BERDL is both broad and deep: it spans many biological topics while maintaining extremely large reference, phenotype, environmental, and literature collections. The architecture is already enabling cross-program work, but reuse is uneven. KBase and KE Science function as the principal reference and knowledge-engine hub, while ENIGMA, PhageFoundry, PROTECT, NMDC, and external sample collections are comparatively underused relative to their potential.

A practical user heuristic is to select the source by analysis layer and then identify the shared canonical key. Genome, phenotype, and environmental analyses will often cross tenants, with `genome_id`, `ncbi_taxon_id`, `sample_id`, or `feature_id` serving as likely bridges. However, identifiers must be checked for semantic equivalence: a `genome_id` may represent a KBase UPA, an NCBI accession, or a MAG-specific hash.

## Limitations

- Only UC1 has been validated for value-space overlap; the remaining use cases are schema-level proposals.
- Two tenant-to-agency mappings, `evaluation` and `lambda`, remain unverified.
- The realized-use audit mined project READMEs and is therefore a lower bound on actual tenant breadth.
- Most depth statistics are row counts rather than deduplicated biological entities.
- Cross-tenant duplicate records were not removed, so collections such as UniProt and ENIGMA genome layers may overlap.

## Recommended Next Steps

1. Validate UC2–UC5 with live-cluster SQL probing, prioritizing UC3 GTDB/KBase harmonization.
2. Develop UC1 into a standalone structure–phenotype project using the 55,454-gene cohort.
3. Add per-residue confidence and structural features to AlphaFold-derived data.
4. Verify remaining agency mappings and refresh the inventory at major ingest milestones.
5. Improve discoverability through a concise BERDL availability summary for KBase users.
6. Investigate underused NMDC metabolomics, proteomics, and lipidomics as cross-validation layers.

## Related Concepts
- [[concepts/evidence-triangulation]]
- [[concepts/genome-ecology-validation]]
- [[concepts/condition-dependent-essentiality]]
- [[concepts/method-concordance]]
- [[concepts/phylogenetic-confounding]]

## Entities
- [[entities/random-barcode-transposon-sequencing]]
- [[entities/kegg]]
- [[entities/proteomics]]
