# Research Plan: Toxin-Antitoxin Systems Across Bacterial Lifestyles

## Research Question

How does bacterial lifestyle (host-associated vs free-living) shape the carriage, family composition, and pangenome partitioning of Type II toxin-antitoxin (TA) loci across the BERDL pangenome?

## Background

Type II TA systems are two-gene modules — a stable toxin and a labile antitoxin — implicated in plasmid maintenance ("addiction modules"), phage defense (abortive infection), stress response, and persister-cell formation. TADB 3.0 (Guan et al. 2023, NAR) catalogs ~50 experimentally characterized TA families with mapped Pfam accessions for both toxin and antitoxin partners.

The `lifestyle_cog` project (Reese, 2026) found that COG-V (Defense) is one of the most lifestyle-discriminating COG categories at the pangenome scale (2,529 species): host-associated accessory genomes show median V-enrichment 1.09 vs 0.77 free-living (rank-biserial r = −0.23, p_adj = 2.3 × 10⁻²¹). COG-V is a coarse-grained bin that lumps TA systems, restriction-modification, CRISPR-Cas, SNIPE, and other defense mechanisms together. This project asks a mechanistic follow-up: **is the V-category asymmetry driven, dampened, or reversed at the TA-system layer specifically?**

## Hypotheses

### H1 — TA loci are predominantly accessory

**H1**: Across all lifestyle-labeled species, TA-locus-carrying gene clusters are enriched in accessory relative to core, with a magnitude comparable to or exceeding COG-V accessory enrichment (rank-biserial |r| ≥ 0.2).

**H0**: TA locus core/accessory frequency matches the genome-wide baseline (gene-cluster–level).

**Rationale**: TA modules are mobile-element cargo (plasmids, integrative conjugative elements, prophage). Prior work (Ramisetty & Santhosh 2017, FEMS) shows plasmid-borne TA far outnumber chromosomal-fixed TA. If BERDL confirms this pattern, we establish that TA carriage is a pangenome-accessory phenomenon amenable to lifestyle stratification.

### H2 — Host-associated species carry fewer TA loci per Mb

**H2**: Host-associated species carry fewer TA loci per genome per Mb than free-living species (Mann-Whitney U, p_adj < 0.05 BH-FDR, rank-biserial |r| ≥ 0.15).

**H0**: TA loci per Mb is independent of lifestyle.

**Rationale**: The reductive-evolution hypothesis for host-adapted lineages (Moran 2002; McCutcheon & Moran 2012, Nat Rev Micro) predicts loss of accessory-lineage cargo. Reduced phage predation in host environments (host immunity + spatial structure) additionally lowers the selective pressure to retain phage-defense TA modules. This should manifest as fewer TA loci per Mb, even after excluding obligate endosymbionts (lifestyle_cog's ≥10-genome filter already does this).

### H3 — TA family composition differs by lifestyle

**H3**: TA family composition (fractions across ~40 Type II TA families) differs between lifestyles. Free-living species carry a broader diversity (higher Shannon entropy of family fractions); host-associated species show bias toward a smaller family repertoire.

**H0**: TA family composition is independent of lifestyle.

**Rationale**: HipA/HipB-type systems are strongly linked to persister-cell physiology relevant to host colonization (Balaban et al. 2019). MazF/MazE and RelE/RelB are ubiquitous stress-response systems. VapC/VapB systems are heavily used in host-adapted mycobacteria (Ramage et al. 2009). Family-level bias, if present, would offer a mechanistic layer beneath the coarse COG-V signal.

## Sensitivity Checks (Pre-registered)

1. **Genome-size confounder**: All rates are computed per Mb of genome. Report Spearman correlation of TA count with genome size for both lifestyles and confirm the lifestyle effect survives partial correlation controlling for genome size.
2. **Phylogenetic confounder**: Rerun H1–H3 within each of the 10 phyla in the lifestyle_cog cohort. Require ≥ 6/10 phyla to preserve direction of the effect for the whole-cohort claim to stand.
3. **Annotation coverage**: Compare Pfam annotation rates between host-associated and free-living species (parallel to lifestyle_cog Review #6). If host coverage is systematically lower, TA counts would appear lower for host — a coverage artifact rather than a biological signal. Report both raw counts and coverage-normalized counts.
4. **Toxin-only vs toxin+antitoxin**: TADB includes solitary toxin genes (orphans). Report H2/H3 both restricted to co-localized T–AT pairs (within 500 bp) and including orphans.
5. **Pfam family definition sensitivity**: Rerun H3 with two family lists — the strict TADB-only set (~40 families) and an expanded set that includes recently identified Type II families (e.g., Type II BREX-associated, SocAB). Direction should be preserved.

## Cohort and Lifestyle Labels

**Reuse `lifestyle_cog` cohort verbatim**: 2,529 species (1,705 host-associated, 824 free-living) across 10 phyla, ≥ 10 genomes per species. Species-level lifestyle labels come from `projects/lifestyle_cog/data/species_lifestyle_classification.csv` (already computed, committed, and reviewed).

No new lifestyle classification work required. This is a strict extension.

## TA Family Panel

Primary panel (Type II TA, Pfam accessions from TADB 3.0):

| Family | Toxin Pfam | Antitoxin Pfam | Notes |
|---|---|---|---|
| RelE/ParE | PF06769 (RelE), PF05016 (ParE) | PF13298 (RHH_5), PF01381 (HTH_3) | Superfamily; ribonuclease |
| HipA/HipB | PF07803 (HipA_C) | PF13412 (HTH_24) | Persister formation; kinase |
| VapC/VapB | PF01850 (PIN) | PF08681 (VapB_antitoxin) | PIN nuclease; Mtb-heavy |
| MazF/MazE | PF04552 (MazF) | PF04014 (MazE) | mRNA interferase |
| HicA/HicB | PF07927 (HicA) | PF15919 (HicB_lg_2), PF05534 (HicB) | Ribonuclease |
| RelBE | PF05016 (RelE) | PF04221 (RelB) | Ribonuclease |
| ParDE | PF05016 (ParE) | PF03693 (ParD) | Plasmid maintenance |
| MqsRA | PF13970 (MqsR) | PF15731 (MqsA) | Biofilm/persister |
| YoeB/YefM | PF06769 (YoeB) | PF02604 (PhdYeFM) | Ribosome-dependent |
| CcdB/CcdA | PF01845 (CcdB) | PF07362 (CcdA) | F-plasmid classic |
| Kid/Kis | PF04552 (MazF-like) | PF04014 (MazE-like) | Plasmid R1 |
| Doc/Phd | PF03693 (Doc) | PF03693 (Phd) | Phage P1 |
| HigBA | PF05015 (HigB) | PF09907 (HigA) | Stress-response |
| RatA/RatB | PF12882 (RatA) | PF13710 (RatB) | Uncommon |

*(final list assembled programmatically from TADB 3.0 in NB01; the table above is the review-audit target.)*

**Executed panel (post-audit)**: 10 families listed in `data/ta_families_seed.tsv` — RelBE, MazEF, ParDE, YoeB-YefM, CcdAB, HipBA, VapBC, HicAB, HigBA, Zeta-Epsilon. The `PFAMs` column of `eggnog_mapper_annotations` stores Pfam NAMES rather than PF-accession numbers, so the panel is defined by name tokens rather than the accession-lookup shown in the audit table above. Candidate families dropped during curation: **MqsRA** (both MqsR and MqsA hit zero in eggNOG naming); **DarTG** (both DarT_ART and DarG_macro hit zero); **Kid/Kis** (subsumed under MazEF via PF04552/PF04014 which are the same Pfams); **Doc/Phd** (name ambiguity with ParDE's ParD_antitoxin); **RatA/RatB** (rare and uncertain). See REPORT.md §Cohort for the final scope rationale.

## Data Sources

| Table | Purpose | Rows | Filter Strategy |
|---|---|---|---|
| `kbase_ke_pangenome.eggnog_mapper_annotations` | Pfam hits per gene cluster | 93M | Filter `pfams RLIKE '<TA-Pfam-regex>'` |
| `kbase_ke_pangenome.gene_cluster` | Core / accessory / singleton status | 132M | Join on `gene_cluster_id`; project to species-level counts |
| `kbase_ke_pangenome.genome` | Genome size (Mb) | 293K | Compute median genome size per species |
| `kbase_ke_pangenome.pangenome` | Per-species totals for normalization | 27K | `no_gene_clusters` denominator |
| `kbase_ke_pangenome.gtdb_species_clade` | Phylum for stratification | 27K | Left-join |

## Analysis Notebooks

### NB01 — TA-Pfam Extraction (`notebooks/NB01_ta_pfam_extraction.ipynb`)

**Requires BERDL JupyterHub or Spark Connect.**

- Load TADB 3.0 Pfam list; commit as `data/ta_families.tsv`.
- Query gene clusters carrying any TA Pfam. Persist to `data/ta_hits_by_gene_cluster.tsv` (expected ~10⁶ rows).
- Aggregate to species-level: `species_id | ta_locus_count | ta_locus_core | ta_locus_accessory | family_composition_json | median_genome_size_mb`. Persist to `data/ta_per_species.tsv`.

### NB02 — Lifestyle Partition and H1/H2 Tests (`notebooks/NB02_lifestyle_partition.ipynb`)

**Runs locally from cached data.**

- Join `data/ta_per_species.tsv` with `../lifestyle_cog/data/species_lifestyle_classification.csv`.
- **H1**: For each gene cluster carrying a TA Pfam, tabulate core/accessory/singleton frequency and compare to the genome-wide baseline gene-cluster frequency. Report rank-biserial r and p (chi-square + BH-FDR).
- **H2**: Per-species TA-loci-per-Mb by lifestyle. Mann-Whitney U; rank-biserial; BH-FDR at family panel level.
- Save `figures/ta_core_accessory.png`, `figures/ta_per_mb_by_lifestyle.png`.

### NB03 — Family Composition and Phylum Controls (`notebooks/NB03_family_composition.ipynb`)

**Runs locally from cached data.**

- **H3**: Shannon entropy of TA-family composition per species → Mann-Whitney host vs free.
- Chi-square on per-family fractions with BH-FDR across families.
- Rerun H1/H2/H3 within each of the 10 phyla.
- Sensitivity: repeat with coverage-normalized counts (Pfam annotation rate correction from lifestyle_cog Review #6).
- Save `figures/ta_family_stacked_bar.png`, `figures/phylum_stratified_ta.png`.

## Revision History

- **v1.0 (2026-07-02, Reese)**: Initial plan. Novelty verified against 42 project branches, `origin/main` (75 project dirs), all commit messages, and `docs/research_ideas.md`.
