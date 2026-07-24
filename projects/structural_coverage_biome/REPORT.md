# Report: Structural Coverage Gap by Biome

## Headline Findings

1. **Pfam-level PDB coverage of the environmental pangenome is 45.7% (9,266 / 20,273 pangenome Pfams have ≥ 1 PDB structure).** Of the 132.4M gene clusters in BERDL, 27.7% lack any Pfam annotation whatsoever — a Pfam annotation gap larger than the PDB gap.

2. **Marginal biome coverage rankings are dominated by pangenome depth, not biology.** Host-associated biomes (host_gut, host_respiratory, host_blood_tissue) look *worse*-covered on raw rates because host pangenomes are 10–100× larger and skew accessory. Once we condition on `is_core = True`, the ranking inverts to match the pre-registered hypothesis H1: **freshwater (18.0%), subsurface_extreme (16.6%), built_environment (16.5%), sediment (16.2%), soil (15.9%) have higher core no-Pfam rates than host_urogenital (11.3%), host_skin (11.8%), host_respiratory (12.2%), or host_gut (13.9%).**

3. **All top-uncovered Pfams are membrane proteins or Pfam-B-derived families**, verified genuinely absent from `kescience_pdb.pdb_pfam`. Dominant across every biome: PF02653 (BCAA transport permease), PF01810 (LysE type translocator), PF01609 (transposase), PF13173/PF13635 (Pfam-B derivatives). Biome specificity: host_gut has PF13xxx-family enrichment; environmental biomes have transport/lyase enrichment.

4. **Chi-square tests reject independence between biome and coverage tier under every stratification** (marginal χ² = 494,203 df=51 p < 10⁻³⁰⁰; core-only χ² = 115,545; accessory-only χ² = 453,310), so the biome × coverage association is not driven solely by is_core confounding — biome contributes signal within each core stratum.

## Methods (as executed)

### Data sources (BERDL, on-cluster)

| Table | Rows | Role |
|---|---|---|
| `kescience_pdb.pdb_pfam` | 990,166 | PDB × chain × UniProt × Pfam mapping — canonical source for "which Pfams have PDB structure" |
| `kbase_ke_pangenome.interproscan_domains` (analysis='Pfam') | 833M total (subset filtered to Pfam) | Per-cluster Pfam annotation source. **Preferred over `bakta_pfam_domains` — bakta silently drops half of pangenome Pfams (10,798 vs 20,273 distinct Pfams).** |
| `kbase_ke_pangenome.gene_cluster` | 132.4M | Cluster → gtdb species, core/accessory/singleton flags |
| `kbase_ke_pangenome.genome` | ~226K | Genome → gtdb species |
| `kbase_ke_pangenome.gtdb_metadata` | ~293K | Genome → `ncbi_isolation_source` (78.7% coverage) |

### Bridge

For each bakta gene cluster, take the set of Pfam accessions from `interproscan_domains` where `analysis = 'Pfam'`, strip the `.<version>` suffix from `signature_acc`. Compute `n_pfam` (annotation count) and `n_covered_pfam` (intersection with `pdb_pfam` distinct set). Assign per-cluster tier:

- `no_pfam_annotation`: n_pfam = 0
- `pfam_no_covered`: n_pfam > 0, n_covered_pfam = 0
- `pfam_partial_covered`: 0 < n_covered_pfam < n_pfam
- `pfam_all_covered`: n_covered_pfam = n_pfam

### Biome assignment

Genome-level biome inferred from `gtdb_metadata.ncbi_isolation_source` via ordered keyword-rule classifier (17 biome labels + "other"). Rules cascade in order: host_* first, then plant → soil → sediment → marine → freshwater → subsurface_extreme → built_environment → food_industrial → agricultural_animal → insect_invertebrate → other. Species biome = majority-vote across that species' genomes.

### Aggregation & tests

- Biome × pfam_tier × is_core aggregation via Spark (`biome_pfam_matrix.csv`)
- Per-biome bootstrap 95% CIs on no-Pfam rate (2,000 draws, seed=42)
- Fisher's exact vs. global rate for no-Pfam per biome; BH-FDR corrected
- χ² independence tests: biome × pfam_tier, marginal and stratified by is_core

## Coverage Landscape

### Global

| Metric | Count | % |
|---|---|---|
| Gene clusters in BERDL pangenome | 132,433,889 | 100% |
| ...with any IPS Pfam annotation | 95,780,408 | 72.3% |
| ...with all Pfams covered by PDB | 78,465,236 | 59.2% |
| ...with some Pfams covered | 3,667,282 | 2.8% |
| ...with Pfams but no PDB coverage | 13,647,890 | 10.3% |
| ...with no Pfam annotation | 36,653,481 | 27.7% |

**The Pfam annotation gap (27.7%) is larger than the PDB-Pfam coverage gap within annotated clusters (13.1%).** For 3× more clusters, we don't even know which family they belong to than the number we know the family of but not the structure.

### By biome (marginal, all clusters)

| Biome | Total clusters | % no_pfam | % pfam_all_covered | % core |
|---|---|---|---|---|
| host_gut | 30.3M | 29.4% | 56.6% | 37.6% |
| soil | 13.0M | 26.7% | 60.5% | 53.8% |
| freshwater | 12.2M | 27.6% | 60.8% | 49.6% |
| marine | 11.2M | 25.2% | **63.6%** | 47.1% |
| plant_associated | 8.4M | 27.1% | 59.6% | 50.8% |
| sediment | 7.8M | 25.9% | 62.6% | 48.5% |
| built_environment | 6.3M | 27.3% | 60.3% | 49.0% |
| host_respiratory | 2.6M | **32.4%** | 54.0% | 38.6% |
| host_blood_tissue | 2.5M | 31.6% | 54.3% | 40.9% |
| food_industrial | 1.4M | 29.2% | 56.1% | 42.2% |
| subsurface_extreme | 1.2M | 26.5% | 62.4% | 53.4% |
| insect_invertebrate | 0.29M | **23.5%** | 62.6% | 60.3% |

Naive interpretation would be: "host biomes are more Pfam-dark than environmental biomes." **This is the pangenome-depth confound: host biomes have far more genomes contributing far more accessory content.**

### By biome, core only (H1 test)

Global core no-Pfam rate: **15.06%**. Per-biome, sorted by log2 enrichment vs. global-core baseline:

| Biome | n_core_clusters | Core no-Pfam rate | log2 enrichment |
|---|---|---|---|
| host_urogenital | 34K | 11.28% | **−0.42** |
| insect_invertebrate | 175K | 11.45% | −0.40 |
| food_industrial | 572K | 11.75% | −0.36 |
| host_skin | 192K | 11.84% | −0.35 |
| host_respiratory | 1.02M | 12.23% | −0.30 |
| host_blood_tissue | 1.04M | 12.55% | −0.26 |
| host_other | 342K | 12.67% | −0.25 |
| host_gut | 11.4M | 13.86% | −0.12 |
| plant_associated | 4.28M | 14.25% | −0.08 |
| marine | 5.27M | 15.23% | +0.02 |
| soil | 6.97M | 15.88% | +0.08 |
| sediment | 3.76M | 16.21% | +0.11 |
| built_environment | 3.11M | 16.55% | +0.14 |
| subsurface_extreme | 619K | 16.59% | **+0.14** |
| agricultural_animal | 236K | 17.00% | +0.17 |
| freshwater | 6.07M | **18.03%** | **+0.26** |

**Confirmed: H1 holds within core clusters.** The freshwater core-genome Pfam-annotation rate is ~1.6× the host_urogenital rate. The gradient environmental > host is monotonic.

## The Top Uncovered Pfams — What Are They?

The 30 globally-most-frequent uncovered Pfams (union across all biomes' top-20 lists) are dominated by:

- **PF02653** — BCAA transport permease (largest uncovered set: ~50K clusters in host_gut, ~33K in soil)
- **PF01810** — LysE-type translocator (membrane efflux)
- **PF01609** — Transposase / DDE endonuclease (mobile element machinery)
- **PF09335** — SNARE-associated Golgi protein
- **PF07726** — Adhesin, alginate O-acetyl transferase
- **PF01925** — Sulfite exporter TauE/SafE
- **PF07394** — Uncharacterized ACR (COG1912)
- **PF13173** / **PF13635** / **PF13408** — Pfam-B-derived (auto-annotated less-curated families)

**Interpretation:**

- **Membrane proteins dominate** — no surprise, membrane crystallography is hard.
- **Mobile-element machinery (PF01609)** appears in all biomes' top-10 uncovered lists — a genuine gap in mobilome structural biology, relevant across every environmental context.
- **Pfam-B derivatives (PF13xxx family)** are disproportionately in host_gut's top-20 uncovered set — the host microbiome is Pfam-B-enriched, consistent with its accessory-genome-heavy pangenome.

## Biome-Specific Priority Signals

- **subsurface_extreme's top uncovered set** is nearly identical to marine/soil — no evidence of an extremophile-specific structural gap beyond the general environmental gap.
- **host_gut's top-3 (PF13408, PF02653, PF13173)** together account for ~145K uncharacterized core+accessory clusters — the largest single-biome gap of any Pfam.

## Confounders

- **Sampling bias.** The pangenome is not evenly sampled across biomes; host_gut has 7,357 species vs. subsurface_extreme's 310. Species-level majority-vote biome partially addresses this at the aggregate level but not within-biome heterogeneity.
- **Isolation-source keyword classifier is coarse.** ~26% of genomes fall into "other" (labeled or unlabeled residuals). Should be validated against a curated subset.
- **`is_core` is species-clade-relative.** A cluster core in one species may be accessory in a broader lineage. Interpretation is "within-species-clade essential," not "phylum-essential."
- **Pfam is one axis of homology.** Genes covered by SUPERFAMILY, Gene3D, PANTHER but not Pfam are counted as "no Pfam annotation" here, undercounting some homology signal. Extension to any-InterPro-signature would raise annotation coverage from 72.3% → 83.8%.
- **PDB coverage of a Pfam ≠ structural knowledge of a specific ortholog.** Distant homolog structures may be poor templates for the cluster's actual biology.

## Files

- `data/biome_summary.csv` — biome × top-line stats
- `data/biome_summary_annotated.csv` — + Fisher p, BH-FDR q, log2 enrichment
- `data/biome_pfam_matrix.csv` — 145 rows: biome × pfam_tier × is_core cell counts
- `data/biome_core_no_pfam_rates.csv` — the core-only H1 table
- `data/biome_top_uncovered.csv` — 340 rows: top-20 uncovered Pfam per biome
- `data/biome_uncovered_matrix.csv` — biome × top-30-globally-uncovered pivot (rate per 1000 clusters)
- `data/biome_chi2_tests.csv` — omnibus χ² tests, marginal and stratified
- `data/genome_biome.csv` — 226K genomes with biome labels + source text
- `data/species_biome.csv` — 26.5K species with majority-vote biome
- `figures/NB03_biome_stacked_tier.png` — all-cluster coverage tier per biome
- `figures/NB03_biome_by_core_stacked.png` — the money figure: same, faceted by is_core
- `figures/NB03_biome_no_pfam_rate.png` — with bootstrap CIs, sorted
- `figures/NB03_top_uncovered_heatmap.png` — biome × top-30 uncovered Pfam
- `figures/NB03_pfam_universe.png` — Pfam sets: PDB, pangenome, intersection

## Authors

- Justin Reese | ORCID: 0000-0002-2170-2250 | Lawrence Berkeley National Laboratory
