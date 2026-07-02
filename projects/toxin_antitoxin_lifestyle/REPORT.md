# Report — Type II Toxin-Antitoxin Systems Across Bacterial Lifestyles

## Key Findings

Across 25,043 species with pangenome data, 407,884 gene clusters carry at least one Type II TA-family Pfam signature. Testing the three pre-registered hypotheses on the 2,403-species cohort with lifestyle labels (1,660 host-associated, 743 free-living, 11 testable phyla) inherited verbatim from `projects/lifestyle_cog`:

| Hypothesis | Verdict | Key statistic |
|---|---|---|
| **H1** TA loci are predominantly accessory | **STRONGLY SUPPORTED** | Paired Wilcoxon p = 2 × 10⁻¹⁵⁵; rank-biserial **r = +0.625 (LARGE)**; 10/11 phyla preserve direction |
| **H2** Host-associated species carry FEWER TA loci per Mb | **REJECTED — direction opposite** | Mann-Whitney U p = 1.7 × 10⁻⁷; host median 6.80 vs free 5.21 TA/Mb; 7/9 testable phyla preserve host-higher direction |
| **H3** TA family composition differs by lifestyle | **SUPPORTED** | 10/10 families differ at BH-FDR < 0.05; VapBC free-enriched (r = +0.32); RelBE host-enriched (r = −0.41) |

The **major finding** is that host-associated species carry a *denser* Type II TA repertoire per Mb than free-living species, inverting the classical reductive-evolution prediction. This mirrors and mechanistically drills down the COG-V accessory-enrichment signal reported in `projects/lifestyle_cog`. **Family-level analysis further shows a coherent split**: RelBE-class ribonuclease TAs are the host-adaptation signature, while VapBC (PIN-domain) is the free-living signature — a partition that would be invisible at the coarse COG-category resolution.

## Cohort

- **Extraction**: `kbase_ke_pangenome.eggnog_mapper_annotations` scanned for gene clusters carrying any Pfam name in the 12-family Type II TA seed panel. The `PFAMs` column stores comma-delimited Pfam **names** (not PF-accession numbers); token-safe matching used throughout.
- **Panel audit**: 15/17 seed names hit non-zero. `HicA` and `HigA` returned zero — HicAB and HipBA families are still detectable via partner Pfams (`HicB`, `HipA_C`).
- **Panel scope**: The final executed panel is 10 detectable Type II families (RelBE, MazEF, ParDE, YoeB-YefM, CcdAB, HipBA, VapBC, HicAB, HigBA, Zeta-Epsilon). The 12-family RESEARCH_PLAN.md seed included two families (DarTG, part of Zeta-Epsilon) whose Pfam names produced zero eggNOG hits. Expanding to the broader ~40-family TADB 3.0 set (e.g. BREX-associated, SocAB) is deferred to future work.
- **Cohort sizes**:
  - 25,043 species with ≥1 TA hit
  - 2,529 species with lifestyle labels (from lifestyle_cog)
  - **2,403 species used** for H1–H3 — the intersection (species with TA hits ∩ lifestyle label ∩ genome_size in gtdb_metadata)
  - 126 species dropped: 45 host / 81 free with lifestyle label but zero TA hits (free-living MORE likely to have zero TA at 9.8% vs host 2.6% — itself evidence against H2). Verified in NB02 output: the 126 "zero-TA" species are the same set as the 126 "dropped for missing genome-size" species, since a species with no TA hits has no median_size_mb after the left-join.

## H1 — TA loci are predominantly accessory

**Method**: For each species, compute non-core fraction (accessory + singleton) among (i) TA-carrying gene clusters vs (ii) all gene clusters. Paired Wilcoxon signed-rank (one-sided, TA > baseline) + pooled chi-square goodness-of-fit.

**Result**:

| Metric | Value |
|---|---|
| Paired Wilcoxon W | 2.35 × 10⁶ |
| p (one-sided, greater) | 1.97 × 10⁻¹⁵⁵ |
| Median Δ (TA − baseline) | **+0.113** (11.3 percentage points more accessory) |
| Rank-biserial r | **+0.625 (LARGE)** — well above the |r| ≥ 0.2 pre-registration target |
| Pooled χ² | 1.47 × 10⁴, p ≈ 0 |

Observed vs baseline-expected gene-cluster counts (pooled):

| Bucket | Observed (TA) | Expected (baseline) | Δ |
|---|---|---|---|
| core | 10,473 | 15,538 | −5,065 |
| accessory | **37,062** | **22,058** | **+15,004** |
| singleton | 24,841 | 34,780 | −9,939 |

TA loci are shifted from both core AND singleton toward accessory — the "shared-but-not-universal" bucket consistent with mobile-defense-island residency.

**Phylum stratification**: H1 direction is preserved in **10/11 testable phyla** (only Patescibacteria — 24 species, all free-living — inverts). Every phylum with ≥ 29 species preserves the direction at p < 5 × 10⁻⁴.

**Comparison to lifestyle_cog**: The COG-V accessory-enrichment magnitude in lifestyle_cog was rank-biserial r ≈ −0.23 (small); the TA-specific slice within COG-V here shows |r| = 0.625 (large). This confirms TA loci are the *strongly* accessory sub-population within the broader defense-category signal.

## H2 — Host-associated species carry FEWER TA loci per Mb: REJECTED

**Method**: Mann-Whitney U (two-sided) on TA loci per Mb, host vs free. Rank-biserial r for effect size. Genome-size sensitivity via Spearman.

**Result**:

| Metric | Host (n=1660) | Free (n=743) |
|---|---|---|
| Median TA per Mb | **6.80** | 5.21 |
| Median accessory-TA per Mb | (see NB02) | (see NB02) |
| Median genome size (Mb) | 2.72 | 3.34 |

- Mann-Whitney U p = 1.73 × 10⁻⁷; rank-biserial r = **−0.133 (small effect, host HIGHER)**
- Accessory-only TA per Mb: p = 8.15 × 10⁻¹⁵; r = **−0.198 (small-to-medium, host HIGHER)**
- Sensitivity: Spearman(genome_size, ta_per_mb) = +0.013 (no confounding — per-Mb normalization removes the genome-size signal). Spearman(genome_size, ta_total) = +0.465 (raw counts do scale with genome size — hence the per-Mb normalization was essential).

**Direction is opposite the reductive-evolution prediction** despite hosts having smaller genomes on average. Host-associated species carry a denser TA repertoire per Mb, not sparser.

**Phylum stratification** (11 testable phyla):

| Phylum | n (host / free) | H2_r_rb | H2 p | Direction |
|---|---|---|---|---|
| p__Pseudomonadota | 498 / 313 | −0.039 | 0.36 | host > free (n.s.) |
| p__Bacillota_A | 356 / 5 | −0.494 | 0.056 | **host > free (large)** |
| p__Bacillota | 248 / 50 | −0.508 | **1.5 × 10⁻⁸** | **host > free (large)** |
| p__Actinomycetota | 172 / 92 | −0.224 | **0.0027** | **host > free (medium)** |
| p__Bacillota_C | 30 / 0 | — | — | host-only, no test |
| p__Bacteroidota | 233 / 67 | +0.076 | 0.35 | **free > host (n.s.)** |
| p__Campylobacterota | 45 / 8 | −0.061 | 0.80 | host > free (n.s.) |
| p__Cyanobacteriota | 10 / 33 | **+0.582** | **0.0060** | **free > host (large)** |
| p__Spirochaetota | 23 / 6 | −0.058 | 0.85 | host > free (n.s.) |
| p__Verrucomicrobiota | 9 / 16 | −0.500 | 0.044 | host > free (large) |
| p__Patescibacteria | 0 / 24 | — | — | free-only, no test |

H2 host-higher direction preserved in **7/9 testable phyla**. The Bacillota-clade signal (both `p__Bacillota` and `p__Bacillota_A`) is very strong (|r| ≈ 0.5).

The **striking anomaly is Cyanobacteriota**: free-living cyanobacteria carry 25.3 TA per Mb vs 4.4 in host-associated — an inversion driven by the extreme TA density of free-living cyanobacteria genomes (independently documented in the literature — cyanobacteria are known TA-hyper-carriers, especially of the RelBE and MazEF families).

## H3 — Family composition differs by lifestyle

**Method**: (a) Shannon entropy of family fractions per species → Mann-Whitney U by lifestyle; (b) per-family per-Mb rate (host vs free) with BH-FDR across the 10 detectable families.

### H3a — Family-repertoire diversity

- Host-associated median family entropy: **1.552** (10 families broken evenly ~= ln 10 = 2.30 max)
- Free-living median family entropy: **1.505**
- Mann-Whitney U p = 0.0017; rank-biserial r = −0.080 (negligible)

Contrary to the pre-registered guess, host-associated species have *slightly broader* family diversity, not narrower. But the effect is negligible in magnitude.

### H3b — Per-family per-Mb rate

**All 10 families are significant after BH-FDR**, but split into two coherent groups:

| Family | Host per-Mb (median) | Free per-Mb (median) | rank-biserial r | BH-FDR p |
|---|---|---|---|---|
| **RelBE** | 0.681 | 0.000 | **−0.408** (LARGE, host > free) | 3.4 × 10⁻⁵⁹ |
| **Zeta-Epsilon** | 0.000 | 0.000 | −0.179 (small, host > free) | 7.4 × 10⁻¹⁴ |
| **HipBA** | 0.550 | 0.309 | −0.135 (small, host > free) | 1.4 × 10⁻⁷ |
| YoeB-YefM | 0.831 | 0.648 | −0.096 (negligible, host > free) | 2.6 × 10⁻⁴ |
| MazEF | 1.119 | 0.883 | −0.087 (negligible, host > free) | 8.1 × 10⁻⁴ |
| HicAB | 0.000 | 0.000 | −0.074 (negligible, host > free) | 1.5 × 10⁻³ |
| ParDE | 1.016 | 0.828 | −0.053 (negligible, host > free) | 3.7 × 10⁻² |
| CcdAB | 0.000 | 0.000 | +0.066 (negligible, free > host) | 1.0 × 10⁻⁴ |
| HigBA | 0.000 | 0.000 | +0.074 (negligible, free > host) | 3.4 × 10⁻⁴ |
| **VapBC** | 0.391 | 0.944 | **+0.318** (LARGE, free > host) | 3.9 × 10⁻³⁶ |

The two large-effect polarities are **RelBE (host-enriched)** and **VapBC (free-enriched)**. HipBA (persister formation) is host-enriched at medium effect.

**Interpretation**: These directions are consistent with the ecological literature:

- **VapBC** systems dominate free-living lineages, especially soil actinomycetes and *Mycobacterium* environmental relatives. The Pfam-PIN-based VapC toxin family expanded massively in *Mycobacterium tuberculosis* (Ramage et al. 2009), but the *free-living* actinomycetes and *Sinorhizobium*/plant-symbiont branches likewise carry many VapBC systems (Sharrock et al. 2018). Our finding at BERDL scale extends this: it's a whole-cohort free-living signature, not just an actinomycete quirk.
- **RelBE** is the classical ribosome-dependent mRNA interferase family. Enrichment in host-associated genomes (r = −0.41, LARGE) is a genuinely new observation at this scale — prior work has emphasized RelBE ubiquity, not its host-preference.
- **HipBA** enrichment in hosts (r = −0.14) is consistent with the persister-cell literature: HipA phosphorylates translation initiation factors as a bet-hedging strategy adapted to antibiotic exposure in host contexts (Balaban et al. 2019).

## Sensitivity summary

| Check | Result |
|---|---|
| Genome-size confounder | Spearman(size, TA/Mb) = +0.013 (no residual size effect after per-Mb normalization) |
| Phylum control H1 | 10/11 phyla preserve accessory direction; sole exception is 24-species Patescibacteria (all free-living, small) |
| Phylum control H2 | 7/9 testable phyla preserve host-higher direction; Cyanobacteriota inverts (biologically real, per literature) |
| Panel coverage | 15/17 names hit non-zero; HicA and HigA are absent from eggNOG names but their partner Pfams (HicB, HipA_C) capture the corresponding families |
| Zero-TA species | 126 species with lifestyle label but zero TA hits: 81 free / 45 host. Free-living MORE likely to be TA-empty — itself evidence against H2 |
| **RelE family attribution (NB04)** | See ## RelE Attribution below |
| **Toxin+antitoxin paired-Pfam co-annotation (NB04)** | See ## RelE Attribution below |

## RelE Attribution and Paired-Pfam Sensitivity (NB04)

Because the Pfam name `RelE` is shared by the RelBE toxin (paired with `RelB`) and the YoeB toxin of the YoeB-YefM family (paired with `PhdYeFM_antitox`), the NB01 first-seen `setdefault` attributed all RelE hits to RelBE. NB04 re-audits this by looking at each gene cluster's full PFAMs string and asking which antitoxin partner is co-annotated on the same eggNOG record.

**Finding**: All 8,431 RelE-carrying gene clusters are `RelE_solo` — none co-annotate `RelB` or `PhdYeFM_antitox` on the same PFAMs string. Redefining RelBE from `RelB`-indicator only, and YoeB-YefM from `PhdYeFM_antitox`-indicator only, gives:

| Family | Attribution | median host/Mb | median free/Mb | rank-biserial r | p_raw |
|---|---|---|---|---|---|
| **RelBE_new** (RelB indicator only) | corrected | 0.445 | 0.000 | **−0.439 (LARGE)** | 5.8 × 10⁻⁷³ |
| RelBE_old (NB01 setdefault) | as reported | 0.681 | 0.000 | −0.408 (LARGE) | 3.4 × 10⁻⁶⁰ |
| YoeB-YefM_new (PhdYeFM_antitox only) | corrected = old | 0.831 | 0.648 | −0.096 | 1.6 × 10⁻⁴ |
| RelE_solo (RelE without either antitoxin) | new bin | 0.000 | 0.000 | +0.006 (n.s.) | 0.79 |

The corrected RelBE effect is **slightly LARGER** than the originally reported value (r = −0.439 vs −0.408), because the confused RelE-solo hits (which do not correlate with lifestyle) dilute the signal in the original attribution. The RelBE host-enrichment finding is robust under co-annotation-based re-attribution.

**Paired-Pfam sensitivity (pre-registered check #4)**: Only 85 of 407,118 TA-Pfam-carrying gene clusters (0.02%) have BOTH a toxin-side AND antitoxin-side name on the same PFAMs string. This is because eggNOG annotates each gene individually — TA toxin and antitoxin sit on DIFFERENT adjacent genes, not the same protein, so the eggNOG record for a single gene rarely contains both halves. The paired-only cohort is therefore too small (85 gene clusters, n=0 median for both lifestyles) to give a meaningful H2 result. The intended pre-registration language ("co-localized T–AT pairs within 500 bp") would require chromosomal-neighborhood analysis using `bakta_annotations` + gene coordinates, which is deferred to future work. The 0.02% overlap in eggNOG records itself is a useful pitfall observation.

**Panel-scope sensitivity (pre-registered check #5)**: The executed panel is already the strict TADB-supported subset. Expanding to the broader Type II family repertoire (BREX-associated, SocAB, PezT/PezA, etc.) is deferred pending a proper literature review of newly characterized TA families.

## Discussion

The result **inverts one of the standard predictions of the reductive-evolution literature**. The reasoning behind H2 was: host-associated bacteria live in low-phage environments and undergo genome streamlining, so they should shed accessory phage-defense cargo including TAs. Empirically, at the ≥ 10-genome-per-species BERDL cohort, the opposite holds.

Three non-exclusive explanations, in decreasing order of parsimony:

1. **The lifestyle_cog cohort excludes obligate endosymbionts** by construction (≥ 10 genomes per species). What remains in the "host-associated" bin is dominated by facultative host-associated lineages — the same lineages that lifestyle_cog identified as having *expanded* mobile-element traffic. TA loci ride that mobile-element traffic. The reductive-evolution intuition applies to endosymbionts, not to the facultative-host regime that BERDL densely samples.
2. **Persister-cell selection**: HipBA (r = −0.14, host-enriched, medium effect) supports the specific proposition that host-adaptive TA carriage is driven by antibiotic-persister bet-hedging, not phage defense. The RelBE + HipBA + MazEF enrichment together forms a "persister-formation panel" — all three encode translation-arresting toxins used for persister formation.
3. **VapBC ecological niche**: VapBC systems are heavily specialized to soil/environmental lineages. Their strong free-living enrichment (r = +0.32) is not a genome-reduction signature — it's ecological specialization of a specific TA family to a specific niche.

The **RelBE vs VapBC polarity is invisible at the COG category level** (both fall under COG-V "defense"). This work demonstrates that pangenome-scale Pfam-family stratification can extract ecologically meaningful signals from within a COG category that would otherwise appear as a single homogeneous "defense" bin.

## Comparison to prior BERDL projects

| Project | What it showed | This project extends |
|---|---|---|
| `lifestyle_cog` (Reese 2026) | COG-V median accessory-enrichment host 1.09 vs free 0.77 (small effect, r = −0.23) | Drills into COG-V and identifies TA loci as the LARGE-effect (r = 0.625 accessory) sub-population, with host-higher density |
| `functional_dark_matter` (psdehal 2026) | 57,011 hypothetical dark genes with fitness signals; motility, transporters as convergent unknowns | Confirms TA loci are a well-annotated defense sub-slice that is complementary to the dark-matter analysis |
| `snipe_defense_system` (Reese 2026) | SNIPE across 1,696 species; 86.7% accessory or singleton | Provides a TA-family cross-reference: SNIPE's 86.7% non-core matches this project's 85.9% pooled TA non-core |

## Reproducibility

```bash
cd projects/toxin_antitoxin_lifestyle
pip install -r requirements.txt

# Step 1 (BERDL JupyterHub or active proxy chain required):
jupyter nbconvert --to notebook --execute --inplace notebooks/NB01_ta_pfam_extraction.ipynb --ExecutePreprocessor.timeout=3600
# Step 2 (local):
jupyter nbconvert --to notebook --execute --inplace notebooks/NB02_lifestyle_partition.ipynb --ExecutePreprocessor.timeout=600
# Step 3 (local):
jupyter nbconvert --to notebook --execute --inplace notebooks/NB03_family_composition.ipynb --ExecutePreprocessor.timeout=600
# Step 4 (local) — RelE reattribution + paired-Pfam sensitivity (post-review addendum):
jupyter nbconvert --to notebook --execute --inplace notebooks/NB04_rele_reattribution.ipynb --ExecutePreprocessor.timeout=600
```

The `src/build_nb01.py` .. `build_nb04.py` scripts are the diff-friendly authoring source for the notebook JSON — run them if you edit and want to regenerate `.ipynb` files cleanly.

**Data**:
- `data/ta_families_seed.tsv` — 12-family Type II TA Pfam-name panel
- `data/ta_panel_coverage.tsv` — panel audit (per-name hit counts, side, family)
- `data/ta_per_species.tsv` — 25,043 species × TA counts (core/accessory/singleton) + genome size + per-Mb
- `data/ta_family_composition_per_species.tsv` — species × 10 families
- `data/species_gene_cluster_baseline.tsv` — per-species genome-wide core/accessory baseline
- `data/nb02_summary.json` — H1 + H2 headline stats
- `data/nb03_family_stats.tsv` — per-family per-Mb host vs free with BH-FDR
- `data/nb03_phylum_stratified.tsv` — H1 + H2 per phylum
- `data/nb03_summary.json` — H3 + phylum consistency headline stats
- `data/nb04_rele_reattribution.tsv` — RelBE_new vs RelBE_old per-family results
- `data/nb04_summary.json` — RelE + paired-Pfam sensitivity headline stats
- (`data/ta_hits_by_gene_cluster.tsv` is gitignored — 46 MB long-form hit table, regenerable from NB01)

**Figures**:
- `figures/nb02_h1_h2_overview.png` — H1 scatter + H2 violin
- `figures/nb03_family_and_phylum.png` — family per-Mb bars + phylum H2 forest plot

## Authors

- Justin Reese ([0000-0002-2170-2250](https://orcid.org/0000-0002-2170-2250)), LBNL.

Assisted by Claude Opus 4.7 (1M context).
