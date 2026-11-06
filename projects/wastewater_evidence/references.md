# References — wastewater_evidence

Searched via Europe PMC and PubMed on 2026-10-17. Searches on the specific
question ("wastewater sample retrieval across BioSample, MGnify, GOLD") returned
nothing; the literature below covers the general problem of metadata
harmonisation and ontology annotation that this project applies to one domain.

## Data sources and portals

- Eloe-Fadrosh EA et al. (2022). "The National Microbiome Data Collaborative
  Data Portal: an integrated multi-omics microbiome data resource."
  *Nucleic Acids Research*. PMCID: PMC8958897.
  NMDC's portal and its use of GOLD ecosystem paths plus MIxS environmental
  triads, the two structured channels this project measures.

## Metadata standards and ontology annotation

- Blumberg KL, Ponsero AJ, Bomhoff M, Wood-Charlson EM, DeLong EF, Hurwitz BL
  (2021). "Ontology-Enriched Specifications Enabling Findable, Accessible,
  Interoperable, and Reusable Marine Metagenomic Datasets in Cyberinfrastructure
  Systems." *Frontiers in Microbiology*. PMID: 34956127.
  Makes the general point this project measures in one domain: community
  standards for minimal metadata exist but are applied inconsistently across
  projects, which blocks interoperability and machine-actionable discovery.

- Griffiths E, Dooley D, Graham M, Van Domselaar G, Brinkman FSL, Hsiao WWL
  (2017). "Context Is Everything: Harmonization of Critical Food Microbiology
  Descriptors and Metadata for Improved Food Safety and Surveillance."
  *Frontiers in Microbiology*. PMID: 28694792.
  Argues for ontology terms with stable identifiers over free text, and for
  mapping institution-specific vocabulary onto a shared standard at whatever
  granularity each source supports. That mapping step is what the transfer
  scheme in this report implements.

## Related observatory work (knowledge layer)

- `env_embedding_explorer` — NCBI environment metadata joined to AlphaEarth
  embeddings; shares the problem of coarse, inconsistent environment labels on
  BioSample records.
- `bacdive_metal_validation` — isolation-environment strings from BacDive used
  as a categorical signal, with the same keyword-matching caveats.
- `nmdc_community_metabolic_ecology` — NMDC biosample ecosystem paths as an
  analysis variable.
