# Project pitfalls — euk_in_prok_correlates

_Append-only. Newest at bottom. Corrections annotated inline, not deleted._

## [euk_in_prok_correlates] NMDC Kraken DB is prokaryote-restricted — do NOT use it to measure total eukaryotic fraction

**Problem**: `kbase.nmdc_arkin.kraken_gold` uses a prokaryote-focused reference database. At
`rank='superkingdom'`, Eukaryota averages only **0.35%** of classified reads, and the *only*
eukaryotic entry at `rank='kingdom'` is **Metazoa** (i.e., human host reads). Per-file
superkingdom `percent` values sum to only ~7–20% because most reads are unclassified. Using
Kraken as the eukaryotic-fraction response variable therefore massively **understates**
eukaryotic content and misses plant/fungal/protist contamination entirely.

**Solution**:
- Use **`gottcha_gold`** as the primary eukaryotic-signal source — its DB includes plastid and
  eukaryote references. At `rank='superkingdom'` it reports `Eukaryota` (359 files) and
  `Eukaryota (plastid)` (1,162 files ≈ 35%). Compute relative euk abundance as
  `SUM(abundance WHERE label LIKE 'Eukaryota%') / SUM(abundance)` at `rank='superkingdom'`
  (GOTTCHA `abundance` is within-sample relative and sums ≈ 1).
- Treat the three classifiers as **complementary, source-specific** detectors, not
  interchangeable: GOTTCHA `Eukaryota (plastid)` → plant/algal chloroplast; Kraken `Metazoa`
  → host/animal; GOTTCHA/Centrifuge `Eukaryota` → protist/fungal/general.
- Classifier reference-DB composition is itself a confounder — report cross-classifier
  concordance as a robustness dimension.

**Symptom if ignored**: near-zero euk fractions everywhere, no plant signal, spurious
conclusion that eukaryotic contamination is negligible in NMDC metagenomes.

## [euk_in_prok_correlates] NMDC child tables (has_input, instrument_used) join on `parent_id`, not `id`

**Problem**: `nmdc.metadata.data_generation_set_has_input`,
`material_processing_set_has_input`, and `*_instrument_used` have only `has_input`/`parent_id`
(or `instrument_used`/`parent_id`) — there is no `id` column. Joining `... ON child.id = parent.id`
throws `UNRESOLVED_COLUMN`.

**Solution**: link the multivalued child table back to its parent set on `parent_id`:
`... JOIN data_generation_set_has_input hi ON hi.has_input = biosample_id
     JOIN data_generation_set_instrument_used iu ON iu.parent_id = hi.parent_id
     JOIN instrument_set ins ON ins.id = iu.instrument_used`.

## [euk_in_prok_correlates] Classifier file_id → biosample bridge is `omics_files_table`, joins at 99.7%

Read-based taxonomy `file_id` (`nmdc:dobj-11-*`) → `kbase.nmdc_arkin.omics_files_table`
(`file_id`→`sample_id`,`omics_processing_id`,`study_id`) → `nmdc.metadata.biosample_set.id`.
5,853 / 5,871 classified biosamples (99.7%) join. The `nmdc:bsm-11-*` vs `nmdc:bsm-13-*`
minting-code difference between tables is cosmetic and does **not** block the join.
