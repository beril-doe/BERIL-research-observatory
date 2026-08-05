# Discoveries — euk_in_prok_correlates

<!-- [euk_in_prok_correlates] 2026-07-10T16:07:02Z  approved-report extraction (REVIEW: REVIEW_3.md) -->

- **Cross-collection contamination-QC correlates are a confounding trap.** In NMDC, sample matrix/biome is
  ~80–100% nested within study, so the eukaryotic fraction's strong association with environment (p≈10⁻¹⁷ to
  10⁻⁵⁰) does not survive holding out whole studies (out-of-study R² = −0.30; = `study_id`-only R²). Any
  cross-collection "metadata correlate of contamination" analysis must control for study/batch (e.g., GroupKFold
  by study or within-study contrasts) or it will over-claim. This likely also qualifies biome-level correlates
  reported at scale elsewhere.
- **Within a batch-controlled study, environmental drivers of eukaryotic contamination are real and large:** in
  a NEON soil study, aboveground vegetation type and geography predict soil eukaryotic (plant/algal) read
  fraction (within-study R²=0.17; Arctic tundra ≫ temperate forest), i.e. eukaryotic contamination of soil
  metagenomes is set largely by aboveground photosynthetic input.
- **Eukaryotic contamination of environmental metagenomes is photosynthetic, not host-derived:** plastid is a
  median 100% of the GOTTCHA2 eukaryotic signal; source composition partitions by biome (algal plastid in
  freshwater, root fungi on plants, plant plastid in herbaceous soil).
- **NMDC read-based classifiers are not interchangeable for eukaryote quantification** — the Kraken2 and
  Centrifuge reference databases are prokaryote-restricted (domain-level Eukaryota ≈0; Kraken's only eukaryotic
  kingdom is Metazoa/human). Use GOTTCHA2 (plastid- and eukaryote-aware) to measure eukaryotic fraction.
