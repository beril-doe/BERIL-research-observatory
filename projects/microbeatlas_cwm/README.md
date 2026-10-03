# MicrobeAtlas × ke_pangenome: CWM Metal Ecology

**Project ID:** microbeatlas_cwm  
**Thesis chapter:** Chapter 3 — Community Genomic Survey (CWM arm)  
**Authors:** Heather MacGregor (Lawrence Berkeley National Laboratory, ORCID: 0000-0003-1112-3009)

## Research Question

Does metal exposure in soil predict shifts in community-weighted mean (CWM) functional gene content, after controlling for pH, soil properties, climate, lithology, and community composition?

## Status

Analysis — report drafted, awaiting `/berdl-review` and `/submit`.

## Approach

16S community data from MicrobeAtlas (4,884 globally thinned terrestrial cells, 0.45° grid) joined to per-genus KEGG KO/Pfam/COG prevalence from ke_pangenome (terrestrial subset, CheckM ≥90/≤5%). CWM[cell,annotation] = Σ(genus_RA × genus_prevalence). Forward FWL (Frisch-Waugh-Lovell) regression at seven causal levels (L0–L6) tests each annotation unit against measured metal concentrations (23 USGS elements). BH-FDR within metal × level. Regional replication in EUR (GEMAS) and AUS (NGSA).

## Key Results

- **560 L1 (pH-adjusted) FDR hits** across 14 elements from 6,557 KOs; mechanism is community turnover not gene gain (3 orthogonal tests)
- **EUR replication: 84–100% overlap, 100% directional concordance** for As, Cd, Cr, Ni, Pb, Zn
- **Mine proximity: 481 L1 hits, 2.7% overlap with metal hits**; elevation-driven confound rather than contamination signal
- **pH: 4,322 L1 hits, constitutive core genes, spatially recoverable** — structurally stronger functional driver than metals
- **Pfam (NB08): 761 Cd-specific hits; COG: 22 hits** (V=18, Cd=2, Cu=1, Pb=1)

## Data Collections

- `arkinlab.microbeatlas` — MicrobeAtlas 16S community data
- `kbase.ke_pangenome` — KO/Pfam/COG functional annotation reference (terrestrial subset)
- `arkinlab.envdbs.soilgrids_master` — pH and soil property fallback
- `arkinlab.envdbs.gemas` — EUR measured metal concentrations
- `arkinlab.envdbs.ngsa_geochemistry` — AUS measured metal concentrations
- `/data/envdbs/usgs_geochem/` — USA USGS measured metals (50+ elements)
- `/projects/microbeatlas_metal_ecology/data/mindat.csv` — Mine localities (157K)

## Notebooks

| Notebook | Status | Key output |
|---|---|---|
| NB00_data_qc | COMPLETE | 4,884 thinned cells, three-tier pH |
| NB01_cwm_construction | COMPLETE | ke_pangenome terrestrial prevalence matrices |
| NB02_metal_associations | COMPLETE | 560 L1 FDR hits; turnover evidence |
| NB03_functional_interpretation | COMPLETE | 17 stable hits; DAG attrition audit |
| NB04_regional_replication | COMPLETE | EUR 84–100% overlap; AUS null (power) |
| NB05_mine_proximity | COMPLETE | 481 L1 hits, 2.7% metal overlap |
| NB06_mine_extended | COMPLETE | Elevation stratification; EUR elev |
| NB07_sensitivity | COMPLETE | 6/7 metals pass permutation; robust |
| NB08_pfam_cog | COMPLETE | Pfam=761 Cd hits; COG=22 hits |
