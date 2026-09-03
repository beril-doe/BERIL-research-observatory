# BERIL Knowledge Wiki (v3)

OpenKB-compiled, hub-structured knowledge wiki over the observatory's project
corpus. One command runs everything — first pass and every later addition:

```bash
CBORG_API_KEY=... ./run_pipeline.sh
```

Every stage is incremental: unchanged reports are hash-skipped by `openkb add`,
already-promoted conflicts and unchanged topic hubs are skipped by content hash,
and the deterministic layers (authors, data, checks, publish) are cheap to rerun.
Adding one new project costs roughly $0.50 (Sonnet 5) end to end.

## Layout

| Path | What | Owner |
|---|---|---|
| `staging/` | report copies fed to OpenKB (synced from `projects/`) | pipeline |
| `wiki/` | summaries, concepts, entities + `AGENTS.md` (the compile rules) | **OpenKB — never hand-edit pages** |
| `wiki-extra/` | topic hubs, home, conflicts, authors, data pages | our generators |
| `quartz/` | Quartz v5 clone + built site (gitignored) | `build_quartz.sh` |
| `.openkb/config.yaml` | model + entity types; `openai/claude-sonnet-5` steady state | you |

## Pieces

- `run_pipeline.sh` — the orchestrator (stage → compile → conflicts → hubs → extras → check → publish).
- `wiki/AGENTS.md` — editorial contract for the compile LLM: per-claim `[src:]`
  citations with exact numbers, alias merging, claim-delta integration, typed
  relations ("supports/contradicts/refines"), slotting sections, conflict rules.
- `conflicts_build.py` — promotes multi-project `## Tensions` to dedicated
  conflict pages (Evidence Sides / Reconciliations / Resolving Work).
- `topics_build.py` — Louvain-clusters the concept graph into ~14 topics
  (resolution 2.0), writes v2-style hub pages + the home page (Sonnet 5),
  anchored on conflict pages; only changed hubs regenerate.
- `extra_pages.py` + `people.py` — deterministic author (ORCID) and
  data-collection pages.
- `wiki_check.py` — post-compile audit: unknown `[src:]` ids (errors), uncited
  numeric paragraphs, numbers absent from cited sources, per-project
  integration depth (<2 concept/topic citations ⇒ under-integrated), and
  near-duplicate concept detection (warnings).
- `quartz_ingest.py` / `build_quartz.sh` — publish: `[src:]` → links to summary
  pages, wikilinks Quartz can't resolve stripped to plain text (wiki source
  keeps them for future compiles), OpenKB catalog demoted to `/catalog`.

Serve: `cd quartz && npx quartz build --serve` → http://localhost:8080.

## Model policy

Backfill was compiled with `openai/gpt-5.6-luna` (~$2.20 for 75 docs); steady
state uses `claude-sonnet-5` so the hub/hot pages deepen as projects land
(pilot A/B showed Sonnet consolidates deeper pages; Luna shards more finely).
All LLM traffic goes through CBORG (`OPENAI_BASE_URL=https://api.cborg.lbl.gov`).

## Known limits

- `openkb recompile` regenerates from scratch and would overwrite any manual
  edit inside `wiki/` — treat `wiki/` as generated output.
- OpenKB upstream (VectifyAI, Apache-2.0) is pinned; carry patches in a fork if
  it stays dormant (lint turn cap already patched in the venv:
  `openkb/agent/linter.py` MAX_TURNS 50 → 300).
- Concept consolidation is advisory: `wiki_check` flags near-duplicates, and
  hubs weave shards into one narrative, but merging pages inside `wiki/` is
  left to OpenKB to avoid fighting its compiler.
