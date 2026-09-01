# Independent comparative review of the BERIL knowledge wikis

## Scope and method

This is an independent review of the three supplied wiki generations. I did not read any prior wiki review or comparative-review artifact.

The corpus check confirmed 78 directories under `projects/`. Seventy-three contain `REPORT.md`. The five without reports are `openness_functional_composition`, `pangenome_pathway_ecology`, `pangenome_pathway_geography`, `resistance_hotspots`, and `temporal_core_dynamics`. I use the 73 report-backed projects as the main completeness denominator and discuss the five report-less directories separately.

Coverage was measured by taking each report-backed project ID, normalizing hyphens and underscores, and searching Markdown filenames plus contents for an exact ID. I also ran a stricter body-only pass that removed YAML frontmatter. For V3, I excluded `openkb/quartz/content/sources/` in the main count so that copied raw reports could not create a false 73/73 result. I then repeated the count over only V3's synthesis layers: `topics/`, `concepts/`, `conflicts/`, `entities/`, `data/`, `authors/`, and the home page.

The link audit resolved Markdown and wiki links against real files. An orphan means no incoming body link from another Markdown page. Frontmatter IDs were not counted as links because a human cannot follow them in Markdown. Quartz's Explorer can still expose body-link orphans, so the orphan counts measure the narrative graph, not absolute file discoverability.

V1 and V3 paths below are relative to this worktree. V2 paths are relative to `/Volumes/WorkSSD/superset/worktrees/beril-upstream/feat/kg-wiki/compendium/wiki/`.

Full reading sample:

- V1: `atlas/atlas.md`, `atlas/topics/critical-minerals.md`, `atlas/claims/metal-specific-genes-core-enriched.md`, `atlas/conflicts/metal-specificity-vs-general-stress.md`, and `atlas/opportunities/metal-amr-site-analysis.md`.
- V2: `compendium/wiki/index.md`, `topics/metal-resistance.md`, `projects/metal-specificity.md`, `projects/metal-fitness-atlas.md`, and `data/kescience-fitnessbrowser.md` in the read-only worktree.
- V3: `openkb/quartz/content/index.md`, `topics/microbial-metal-tolerance.md`, `concepts/shared-stress-biology.md`, `concepts/metal-resistance-breadth.md`, `conflicts/conflict--counter_ion_effects--metal_cross_resistance--soil_metal_functional_genomics.md`, and `summaries/metal_specificity__REPORT.md`.

I also checked representative claims against `projects/*/REPORT.md` and compared selected V3 pages with their generation sources in `openkb/wiki/` and `openkb/wiki-extra/`.

## V1: `atlas/`

### Completeness

V1 references 55 of the 73 report-backed projects, or 75.3%, when filenames and frontmatter count. The stricter visible-body result is 51 of 73, or 69.9%. Four projects only appear in metadata, not visible prose: `enigma_contamination_functional_potential`, `fw300_metabolic_consistency`, `genotype_to_phenotype_enigma`, and `metal_cross_resistance`.

The 18 projects absent even from the generous count are:

`acinetobacter_adp1_explorer`, `adp1_deletion_phenotypes`, `adp1_triple_essentiality`, `alphafold_msa_annotation`, `annotation_gap_discovery`, `aromatic_catabolism_network`, `berdl_data_atlas`, `caulobacter_fur_lipida_loss`, `clay_confined_subsurface`, `costly_dispensable_genes`, `ecotype_functional_differentiation`, `enigma_carbon_census_1`, `euk_in_prok_correlates`, `fitness_effects_conservation`, `lignin_community_enrichment`, `nmdc_context_audit`, `phage_defense_arsenal`, and `respiratory_chain_wiring`.

Six covered projects occur in only one Atlas file: `cofitness_coinheritance`, `conservation_fitness_synthesis`, `fw300_metabolic_consistency`, `gene_function_ecological_agora`, `metal_cross_resistance`, and `module_conservation`. Some of these occurrences are only list or metadata entries. This makes 55/73 a generous coverage figure rather than proof of substantive treatment.

The metal-specificity spot check shows what survives and what does not. `atlas/claims/metal-specific-genes-core-enriched.md` preserves the 54.9% headline, the 5% non-metal sick-rate threshold, and the qualitative core-enrichment result from `projects/metal_specificity/REPORT.md`. It drops the exact 84.8% versus 90.2% comparison, the 40.7% record attrition, the failed ICA analysis, and the UCP030820, YebC, and DUF1043 candidate ranking. The page is a useful claim card, but it is not a project record.

V1 also references four of the five report-less directories. For example, `atlas/opportunities/metal-amr-site-analysis.md` treats `resistance_hotspots` as evidence even though that directory has no `REPORT.md`. That may be defensible as planning context, but it is weaker provenance than the page's evidence framing suggests.

The later AlphaFold study illustrates the update gap. V1 has `atlas/data/collections/kescience_alphafold.md`, which describes the dataset, but it contains none of the `alphafold_msa_annotation` project's central findings: the 2.89-fold core/accessory MSA-depth difference, rho 0.7563 annotation correlation, or 415,603 paradox proteins.

### Human readability

`atlas/atlas.md` is a good 325-word landing page. It tells readers whether to start from topics, data, claims, tensions, opportunities, or methods. `atlas/topics/critical-minerals.md` then supplies a coherent eight-layer narrative, moving from fitness architecture through specificity, field validation, rare-earth biology, and research directions. This is V1's strongest feature. The author has made choices about what story the corpus tells.

The problem is audience drift. Forty-one of 141 pages contain a `Review Brief` with repeated blocks such as "What changed," "Why review matters," and "Questions for reviewers." `atlas/topics/critical-minerals.md` is partly a scientific synthesis and partly an editorial work packet. That is useful for maintaining the Atlas, but it interrupts a new scientist's reading flow. Frontmatter is also large relative to many short pages.

V1 is the smallest corpus at about 43,000 words, with a median page near 230 words. The compression makes individual claim, conflict, and opportunity pages easy to scan. It also leaves jargon exposed. The critical-minerals topic uses RB-TnSeq, PGLS-adjacent statistical ideas, and lakehouse collection names without consistently defining them on first use.

### Connectivity

The body-link graph has 165 resolved internal links, no dead local targets, and a median of zero outgoing links per page. Ninety-seven of 141 pages have no outgoing body link. Seventy pages have no incoming body link; 54 of those are under `atlas/data/`. For example, most `atlas/data/collections/*.md` pages are not linked from a catalog or topic page. V1's frontmatter contains many `related_pages` IDs, but they are not followable Markdown links.

The checked multi-hop path was:

`atlas/atlas.md` -> `atlas/topics/index.md` -> `atlas/topics/critical-minerals.md` -> `atlas/claims/metal-specific-genes-core-enriched.md` -> `atlas/conflicts/metal-specificity-vs-general-stress.md`.

It taught a clear sequence: metal fitness signals are mostly conserved, a 5% non-metal sick-rate filter narrows them, and counter-ion plus broad-stress controls are still required before treating a gene as metal-specific. The path breaks at provenance. Project IDs appear as code-formatted names, not links to project reports, so the reader cannot continue from the claim or conflict to the underlying evidence.

### V1 judgment

V1 is a good editorial map over a partial corpus. It is the easiest version to skim and the weakest at letting a human verify or exhaust the research record. Its lack of dead links is less impressive once the 70 body-link orphans and 97 pages with no outgoing links are considered.

## V2: `compendium/wiki/`

### Completeness

V2 has 110 Markdown pages: 70 project pages, 12 topics, 10 data pages, 17 author pages, and the home page. It references 65 of the 73 report-backed projects, or 89.0%, both in the full wiki and in the non-project synthesis layers.

The eight missing report-backed projects are:

`alphafold_msa_annotation`, `berdl_data_atlas`, `caulobacter_fur_lipida_loss`, `enigma_carbon_census_1`, `euk_in_prok_correlates`, `lignin_community_enrichment`, `nmdc_context_audit`, and `phage_defense_arsenal`.

V2's claimed total of 70 projects in `compendium/wiki/index.md` is not the current 73-report corpus. It consists of 65 report-backed project pages plus pages for all five report-less directories. Each of those five pages ends with an `Open the full report` link to a nonexistent `REPORT.md`. The page count therefore hides both staleness and five false full-report affordances.

The metal-specificity project page preserves more than V1: 7,609 records, 55%, 84.8% core, and the 1.64-fold metal-resistance annotation enrichment. It still drops candidate-level findings, exclusion details, and failed analyses. The metal-resistance topic restores much of the larger scientific context and gives 86 report-heading references.

That synthesis is not fully reliable. `topics/metal-resistance.md` says metal-specificity is "confirmed by gene knockout validation," but `projects/metal_specificity/REPORT.md` says validation against the Fitness Browser `specificphenotype` table was not performed. The same topic reduces the project's definition to "important for metal but not for NaCl stress," although the project classified genes against 5,945 non-metal experiments. It also contains the visible typo "Gram-negative-negative counterparts." These are exactly the kinds of confident compression errors a generated synthesis must avoid.

### Human readability

`compendium/wiki/index.md` is the strongest single overview among the three versions. It defines core and accessory genomes, RB-TnSeq, GapMind, FBA, and recurring caveats before sending readers into topic pages. A scientist new to BERIL can learn what the body of work is about from this page alone.

The cost is length. The home page is about 3,342 words and `topics/metal-resistance.md` about 4,310 words. Both are coherent, but neither offers V3's short landing step. Topic pages often end in dozens of numbered references, and the metal page has 86. A reader can verify claims, but scanning the page becomes slow.

The project pages are pleasantly short and consistent. Their repeated `Key findings`, `Topics`, `Data`, `Authors`, and full-report structure is useful boilerplate. The author pages are not. They consume about 35,000 words, roughly 23% of V2, and often retell a single project's science at great length. `authors/dileep-kishore.md`, for example, turns one credited project into a long second summary. That duplication adds little to a human knowledge base.

### Connectivity

V2 has the cleanest body-link graph: 1,305 resolved internal links, a median of nine outgoing links per page, and no body-link orphans. The five dead local targets are the nonexistent full reports for the five report-less projects. Sixty-five full-report links resolve outside the wiki to the actual project reports in the read-only worktree.

The checked path was:

`index.md` -> `topics/metal-resistance.md` -> `projects/metal-specificity.md` -> `topics/metal-resistance.md`, with a side branch through `projects/metal-fitness-atlas.md` -> `data/kescience-fitnessbrowser.md` -> other Fitness Browser projects.

The path taught that metal tolerance has a conserved core layer, a narrower specificity layer, and a field-validation layer, while the Fitness Browser page exposed phylogenetic bias, lab adaptation, media mismatch, and the ADP1 coverage gap. The weakness is topology. Project pages mostly route back to a topic or a large data hub, so cross-project travel often loops through long list pages. Supporting and limiting findings are present in prose, but there is no explicit conflict-page layer.

### V2 judgment

V2 is a strong, readable snapshot of an earlier 65-report corpus. It has the best direct path to primary reports and the least orphaning. It loses the comparison because it is stale, treats five unfinished directories as report-bearing projects, and contains at least one unsupported validation claim in a major topic synthesis.

## V3: `openkb/quartz/content/`

### Completeness

V3 has 353 Markdown pages: 75 raw sources, 75 summaries, 81 concepts, 53 entities, 21 conflicts, 18 authors, 14 data pages, 14 topic hubs, a catalog, and a home page. Excluding all 75 raw source pages, it references 73 of 73 report-backed projects. More importantly, the synthesis-only layers also reference 73 of 73, with a median of seven synthesis files per project. V3's full coverage is therefore real integration, not a copied-source counting trick.

It includes all eight report-backed projects missing from V2. The `alphafold_msa_annotation` spot check is especially strong. `summaries/alphafold_msa_annotation__REPORT.md`, `concepts/msa-depth.md`, `concepts/structural-novelty.md`, and `topics/protein-sequence-novelty.md` preserve the original report's 2.89-fold median MSA-depth contrast, rho 0.7563 across 38,051,842 pairs, and 415,603 low-depth core "paradox proteins." The concept pages also retain the sampling and causality limits instead of turning low MSA depth into proof of a novel fold.

For metal specificity, `summaries/metal_specificity__REPORT.md` preserves the main count, threshold sensitivity, exact core fractions, three candidate families, excluded organisms, failed ICA analysis, and data-product inventory. That is substantially better information survival than V1 or V2.

The fidelity is not flawless. The original report's prose says general-sick genes have more general-stress keywords at "11.5% vs 13.7%," while its table shows 11.5% for general-sick and 13.7% for metal-specific. V3 faithfully reproduces the contradictory sentence in `summaries/metal_specificity__REPORT.md`. This is source-inherited rather than invented during assembly, but the wiki does not catch or flag it.

Selected source-to-assembly diffs show that V3 generally preserves prose while converting `[src: project_id]` markers into summary links. `openkb/wiki/index.md` is byte-identical to `openkb/quartz/content/catalog.md`. The home page and metal topic differ from `openkb/wiki-extra/` mainly through link and citation rewriting. One assembly change is harmful: `openkb/wiki-extra/index.md` contains `[[catalog|Full page catalog]]`, but `openkb/quartz/content/index.md` reduces it to plain text even though `catalog.md` exists.

### Human readability

V3 has the best landing sequence. The 717-word home page explains the corpus, names 14 topic entry points, states the correct 73-report plus two-digest inventory, and tells a newcomer how to move from topics to concepts, entities, and reports. `topics/microbial-metal-tolerance.md` is about 1,069 words and reads as a guided argument rather than an encyclopedia dump. The explicit `Tensions and Caveats` and `Where to Go Deeper` sections are useful.

The next layer is much heavier. `concepts/shared-stress-biology.md` is about 2,419 words and repeats many numbers already present in the topic and project summaries. The reader-facing corpus excluding raw sources is about 313,000 words, more than twice V2. The 81 concepts account for roughly half of those words. V3's completeness is partly achieved through repeated restatement, which raises maintenance and contradiction risk.

Prose quality is generally careful. Claims distinguish association from causation, underpowered nulls from evidence of absence, and conditional from total variance. Jargon handling is uneven. The home page is accessible, while deeper pages can introduce PGLS, db-RDA, FDR, COG, Mantel tests, and taxonomic proxies rapidly. The conflict pages are shorter and plainer than the concepts.

Some peripheral pages are too thin. The 18 author pages contain only about 400 words total; `authors/dileep-kishore.md` is a title plus one project link. Several data pages are useful inventories, but the category's median text is around 60 words. These stubs contrast sharply with the very long concepts.

### Connectivity

V3's reader layer has 3,924 resolved internal page links and a median of 11 outgoing links per page. It also has five dead link occurrences aimed at three nonexistent entity paths:

- `entities/enigma-coral` from `summaries/lab_field_ecology__REPORT.md` twice and `entities/oak-ridge.md` once. The real page is `data/enigma-coral.md`.
- `entities/nmdc-ncbi-biosamples` from `summaries/nmdc_context_audit__REPORT.md`. The real page is under `data/`.
- `entities/phagefoundry` from `summaries/pitfalls.md`. The real page is under `data/`.

There are 35 body-link orphans after excluding raw sources: all 18 author pages, all 14 data pages, two conflict pages, and `catalog.md`. Quartz's Explorer can expose them, and many link outward, but the home and topic narrative does not lead into them. The stripped home-to-catalog link is especially avoidable.

The raw provenance layer is weaker than the home page promises. All 75 `sources/` pages have no incoming body link. Summary frontmatter contains `full_text: "sources/..."`, but the Quartz code does not render that field as a link. Per-claim citations on a project summary point back to that same summary. The audit counted 503 self-citation link occurrences. The built HTML for `summaries/metal_specificity__REPORT.md`, for example, repeatedly links `metal_specificity` to the current summary and provides no link to `sources/metal_specificity__REPORT.md`. A reader can find the raw report through Explorer, but cannot follow the advertised evidence chain from the claim.

The checked narrative path was:

`index.md` -> `topics/microbial-metal-tolerance.md` -> `concepts/shared-stress-biology.md` -> `conflicts/conflict--counter_ion_effects--metal_cross_resistance--soil_metal_functional_genomics.md` -> the three cited project summaries.

It taught a genuinely cross-project result: roughly 40% metal-to-NaCl overlap supports a general stress layer; near-universal positive metal-pair correlations support a shared directional response; chemistry-specific magnitudes remain; and the soil R-squared cannot identify causal metals because it is conditional and co-contamination is unresolved. The conflict page then says what experiments would separate those readings. This is the best multi-hop scientific path in the comparison. It breaks only when the reader tries to move from a summary citation to the raw report.

### V3 judgment

V3 is the most complete and the best organized for progressive scientific reading. Its explicit concepts and conflicts turn cross-project relationships into knowledge rather than a list of related pages. It still needs a provenance-link pass, namespace link repair, and aggressive control of duplicated synthesis.

## Criteria comparison

| Criterion | V1 Atlas | V2 Compendium | V3 OpenKB |
|---|---:|---:|---:|
| Completeness | 5.5/10 | 7.5/10 | 9.5/10 |
| Human readability | 6.5/10 | 7.0/10 | 8.0/10 |
| Connectivity | 4.0/10 | 8.0/10 | 8.5/10 |
| Mean | 5.3/10 | 7.5/10 | 8.7/10 |

Why these scores:

- V1 covers only 55/73 projects even with metadata and has a severely sparse body-link graph, but its curated topic narratives are concise and purposeful.
- V2 covers 65/73, defines the science well, links every page into the graph, and reaches 65 real reports. It is stale, verbose, and has five dead report links plus an unsupported validation claim.
- V3 covers and synthesizes all 73, has the strongest entry-to-topic-to-conflict path, and retains detailed findings. Its score is held below 10 by duplication, thin peripheral pages, five dead namespace links, a stripped catalog link, and a broken summary-to-source provenance chain.

## Ranked verdict

1. **V3 OpenKB**. Best overall knowledge base for humans. It is current, complete, explicit about tensions, and offers the clearest progressive path from corpus overview to cross-project interpretation.
2. **V2 Compendium**. Best direct-report navigation and strongest single long-form overview, but it reflects an older 65-report snapshot and occasionally overstates what its cited projects established.
3. **V1 Atlas**. Best compact editorial layer, but not complete or connected enough to stand alone as the corpus knowledge base.

### Strongest argument against V3, the top pick

V3 can give a false impression of auditability. Its pages display dense per-claim citations, but a project summary cites itself, not the raw report, 503 times across the corpus. All 75 raw source pages are body-link orphans. The home page says readers can drill into underlying reports, yet the body graph does not provide that route, and even the source-authored catalog link is stripped during assembly. V2 is much better on this narrow but important point because 65 project pages link directly to real `REPORT.md` files.

The scale magnifies the risk. V3 has about 313,000 reader-layer words and repeats the same evidence across topics, concepts, conflicts, entities, and summaries. The inherited 11.5% versus 13.7% contradiction shows how a source error can be copied into an authoritative-looking synthesis. If scientists value traceable evidence above breadth, V3's citation presentation is the strongest reason to prefer V2 until the source links and duplication are fixed.
