# Wiki Schema

## Directory Structure
- sources/ — Document content. Short docs as .md, long docs as .json (per-page). Do not modify directly.
- sources/images/ — Extracted images from documents, referenced by sources.
- summaries/ — One per source document. Summary of key content.
- concepts/ — Cross-document topic synthesis. Created when a theme spans multiple documents.
- entities/ — Specific named things: people, organizations, places, products, named works, events. One page per entity, accumulated across documents.
- explorations/ — Saved query results, analyses, and comparisons worth keeping.
- reports/ — Lint health check reports. Auto-generated.

## Special Files
- index.md — Content catalog: every page with link, one-line summary, organized by category.
- log.md — Chronological append-only record of operations (ingests, queries, lints).

## Page Types
- **Summary Page** (summaries/): Key content of a single source document.
- **Concept Page** (concepts/): Cross-document topic synthesis with [[wikilinks]].
- **Entity Page** (entities/): A specific named thing (proper noun) — e.g. a person, organization, place, product, named work, or event. Each page has a `type:` frontmatter field; the exact allowed type set is configurable (default: person, organization, place, product, work, event, other) and the authoritative set for this run is given in the compilation prompt. An entity differs from a concept: a concept is an abstract recurring idea; an entity is a specific named thing. Create an entity page only when the entity is central to a document or recurs across sources — do not page passing mentions.
- **Exploration Page** (explorations/): Saved query results — analyses, comparisons, syntheses.
- **Index Page** (index.md): One-liner summary of every page in the wiki. Auto-maintained.

## Index Page Format
index.md lists all documents, concepts, entities, and explorations with metadata:
- Documents: name, one-liner description, type (short|pageindex), detail access path
- Concepts: name, one-liner description
- Entities: name, type, one-liner description
- Explorations: name, one-liner description

## Log Format
Each log entry: `## [YYYY-MM-DD HH:MM:SS] operation | description`
Operations: ingest, query, lint

## Format
- Use [[wikilink]] to link other wiki pages (e.g., [[concepts/attention]])
- Standard Markdown heading hierarchy
- Keep each page focused on a single topic

## Domain Rules (BERIL research corpus)
This KB compiles research-project reports from a microbial-biology observatory (the BERIL Research Observatory over the KBase BER Data Lakehouse). Source files are named `<project_id>__REPORT.md`; two central cross-project digests (`discoveries.md`, `pitfalls.md`) are also sources.

- **Entity types for this KB**: organism, gene_or_pathway, compound, method, dataset, place, person, other. Metals (cobalt, copper, nickel...), media, and chemicals are `compound`. Assays and statistical approaches (e.g. RB-TnSeq, PGLS, db-RDA) are `method`. Databases and data collections (e.g. Fitness Browser, BacDive, MicrobeAtlas, GTDB, ENIGMA) are `dataset`.
- **Canonical entity names**: one page per real-world entity. Merge aliases and abbreviations onto the canonical page (e.g. "E. coli" / "Escherichia coli"; "Cu" / "copper"; "RB-TnSeq" / "random barcode transposon sequencing"). List known aliases on the page. Where a stable external identifier exists, record it (NCBI taxid for organisms, gene symbol, CHEBI/KEGG id for compounds).
- **Per-claim citations (mandatory)**: every factual claim in a concept or entity page must end with a citation to its source project(s) in the form `[src: <project_id>]` (comma-separate multiple ids; use the project id exactly as it appears before `__REPORT` in the source filename, or `discoveries`/`pitfalls` for the central docs). Numbers must be copied exactly from the source — never round, estimate, or reconcile conflicting numbers silently. A claim you cannot attribute must not be written.

## Integration Rules (how new sources change the wiki)
- **Claim-delta integration**: when compiling a new source, the goal is not to mention it everywhere — decide which existing wiki statements it *strengthens, weakens, redirects, or makes newly testable*, and update the smallest set of pages that captures that change. Do not dump project summaries into concept pages; concept pages argue across projects.
- **Evidence grading**: label the strength of key claims in prose — findings backed by direct measurement or strong statistics are stated plainly; extrapolated or single-organism results are marked as such; a claim that rests mostly on extrapolation must be phrased as a hypothesis ("...suggests the hypothesis that..."), never as an established finding.
- **Contradictions and conflict pages**: when sources disagree, record the disagreement under a `## Tensions` heading on the affected concept page, citing each side. When a tension spans two or more concept pages or three or more projects, promote it to its own concept page named `conflict--<slug>` with two required sections: `## Evidence Sides` (each side's claim with citations) and `## Resolving Work` (the specific analyses or data that would settle it). Never resolve a tension by averaging or by silently preferring one side.
- **Open directions**: every concept page ends with a short `## Open Directions` section — concrete next analyses this corpus makes possible, each tied to the gap it would close. Keep entries specific (data + method + question), not aspirational.
- **Slotting**: every summary page ends with a `## Slots Into` section listing the concept pages this project's findings feed (`- [[concepts/x]] — which finding and why`). A finding that slots nowhere means a concept page is missing — create or extend one.
- **Typed relations in prose**: when adding evidence to a concept page that already carries related claims, state the relation explicitly — "this **supports**...", "this **contradicts**...", "this **refines**..." — never just append a parallel fact.
- **Extend, don't duplicate**: before creating a concept page, check the existing concept list; if an existing concept covers the same phenomenon at a different angle, extend it with a new section instead of creating a near-duplicate page.
- **Define jargon at first use per page**: FDR, PGLS, db-RDA, MAG, COG, RB-TnSeq, FBA and similar get a one-clause definition the first time they appear on each concept or summary page.

## Frontmatter (managed by code — do NOT emit it in generated content)
- Every summary/concept/entity page carries a non-empty `type:` — `Summary`,
  `Concept`, or a capitalized entity subtype (e.g. `Organization`). This is the
  one field OKF requires; consumers use it for routing/filtering/presentation.
- `description:` — a single-sentence one-liner (the field formerly named `brief`).
- Do not include YAML frontmatter (---) in generated content; it is managed by code.
