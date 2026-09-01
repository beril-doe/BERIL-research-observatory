#!/usr/bin/env python3
"""Generate the narrative hub layer: ~12 topic pages + a home page, v2-style.

Sits ON TOP of the OpenKB wiki (reads wiki/concepts + wiki/entities), writes to
wiki-extra/topics/ and wiki-extra/index.md so OpenKB recompiles never touch it.
Topic membership is deterministic (Louvain over the concept co-source/wikilink
graph); an LLM names the topics and writes the hub prose, citing only what the
member concept pages already cite.

    OPENAI_API_KEY=$CBORG_API_KEY OPENAI_BASE_URL=https://api.cborg.lbl.gov \
        .venv/bin/python topics_build.py

Model comes from HUB_MODEL below (hub pages are the showcase — Sonnet by decision).
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re

import networkx as nx
from litellm import completion

HERE = pathlib.Path(__file__).parent
OUT = HERE / "wiki-extra"
HUB_MODEL = "openai/claude-sonnet-5"
MIN_CLUSTER = 3
PER_PAGE_CHARS = 7000  # truncate very long concept pages in hub context

TEMPLATE = """You are writing a TOPIC HUB page for the BERIL Research Observatory wiki — the
entry point a scientist reads first to learn what the corpus says about this topic,
before drilling into the finer-grained concept pages.

Write markdown with exactly these sections:
# <Topic Title>
(one-paragraph lead: what this topic is and why this corpus speaks to it)
## What the Corpus Shows
(the heart of the page: argue ACROSS the member concepts/projects as one narrative,
 organized into 3-6 bold-led sub-themes; cite every factual claim with [src: project_id]
 tags COPIED from the member pages — never invent numbers or citations; link liberally
 to member pages with [[concepts/<file-stem>]] wikilinks where a claim is elaborated)
## Tensions and Caveats
(real disagreements between projects and the load-bearing limitations, cited)
## Where to Go Deeper
(a guided reading path: 4-8 bullets, each "[[concepts/x]] — why you'd read it next";
 then a short list of key entities [[entities/y]] and project reports [[summaries/z__REPORT]])

Rules: numbers must be copied exactly from the member pages; a claim you cannot
attribute must not be written; define specialist terms at first use; write for a
scientist-engineer who knows biology but not this corpus. 900-1400 words.
CITATION SYNTAX (strict): a [src: ...] tag contains ONLY project ids from the
PROJECTS IN SCOPE list, comma-separated — never concept names, conflict-page
paths, dashes, or prose. Conflict and concept pages are referenced only as
[[conflicts/...]] / [[concepts/...]] wikilinks, never inside [src: ...].
"""


def parse_page(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'^sources:\s*\[(.*?)\]', text, re.M)
    if m:
        sources = re.findall(r'summaries/([\w.-]+?)__REPORT', m.group(1)) or re.findall(r'"([^"]+)"', m.group(1))
    else:
        m2 = re.search(r'^sources:\n((?:\s+-\s.*\n)+)', text, re.M)
        sources = re.findall(r'summaries/([\w.-]+?)__REPORT', m2.group(1)) if m2 else []
    h1 = re.search(r'^# (.+)$', text, re.M)
    desc = re.search(r'^description:\s*"?(.*?)"?$', text, re.M)
    links = set(re.findall(r'\[\[concepts/([\w.-]+?)(?:\|[^\]]*)?\]\]', text))
    return {
        "stem": path.stem,
        "title": h1.group(1).strip() if h1 else path.stem,
        "desc": desc.group(1).strip() if desc else "",
        "sources": set(sources),
        "links": links,
        "text": text,
    }


def cluster_concepts(concepts: dict[str, dict]) -> list[list[str]]:
    g = nx.Graph()
    g.add_nodes_from(concepts)
    stems = list(concepts)
    for i, a in enumerate(stems):
        for b in stems[i + 1:]:
            w = len(concepts[a]["sources"] & concepts[b]["sources"])
            w += 2 * ((b in concepts[a]["links"]) + (a in concepts[b]["links"]))
            if w:
                g.add_edge(a, b, weight=w)
    # resolution=2.0 -> ~14 topics of 3-9 concepts on this corpus (default 1.0 gave 4 mega-hubs)
    comms = [set(c) for c in nx.community.louvain_communities(g, weight="weight", seed=42, resolution=2.0)]
    # Fold tiny clusters into the neighbor cluster with the strongest total edge weight.
    big = [c for c in comms if len(c) >= MIN_CLUSTER]
    for small in (c for c in comms if len(c) < MIN_CLUSTER):
        def pull(target: set) -> float:
            return sum(g[u][v]["weight"] for u in small for v in g.neighbors(u) if v in target)
        best = max(big, key=pull, default=None)
        (best if best is not None else big[0] if big else comms[0]).update(small)
    return [sorted(c) for c in sorted(big, key=len, reverse=True)]


def llm(prompt: str, system: str = "") -> str:
    resp = completion(
        model=HUB_MODEL,
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.cborg.lbl.gov"),
        messages=([{"role": "system", "content": system}] if system else [])
        + [{"role": "user", "content": prompt}],
        temperature=0.3,
        timeout=600,
    )
    return resp.choices[0].message.content


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main() -> None:
    concepts = {p.stem: parse_page(p) for p in sorted((HERE / "wiki/concepts").glob("*.md"))}
    entities = {p.stem: parse_page(p) for p in sorted((HERE / "wiki/entities").glob("*.md"))}
    clusters = cluster_concepts(concepts)
    print(f"{len(concepts)} concepts -> {len(clusters)} clusters: {[len(c) for c in clusters]}")

    (OUT / "topics").mkdir(parents=True, exist_ok=True)
    state_path = HERE / ".topics-state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}

    # Topic names are cached by member set so identical clusters never get
    # renamed (renames churn page identity and force needless hub regens).
    name_cache: dict[str, str] = state.setdefault("__names__", {})
    keys = [hashlib.sha256(",".join(c).encode()).hexdigest()[:12] for c in clusters]
    unnamed = [i for i, k in enumerate(keys) if k not in name_cache]
    if unnamed:
        listing = "\n".join(
            f"CLUSTER {i}:\n" + "\n".join(f"  - {concepts[s]['title']}: {concepts[s]['desc']}" for s in clusters[i])
            for i in unnamed
        )
        fresh = json.loads(re.search(r"\{.*\}", llm(
            "Name each cluster of research-wiki concepts as a scientific TOPIC (2-4 words, "
            "noun phrase, distinctive). Reply with ONLY a JSON object mapping cluster number "
            f"(string) to topic name.\n\n{listing}"), re.S).group(0))
        for i in unnamed:
            if str(i) in fresh:
                name_cache[keys[i]] = fresh[str(i)]
    names = {str(i): name_cache.get(k, f"Topic {i}") for i, k in enumerate(keys)}
    conflicts = {p.stem: p.read_text(encoding="utf-8", errors="replace")
                 for p in sorted((OUT / "conflicts").glob("*.md"))} if (OUT / "conflicts").is_dir() else {}

    hubs = []
    any_changed = False
    for i, members in enumerate(clusters):
        topic = names.get(str(i), f"Topic {i}")
        slug = slugify(topic)
        srcs = set().union(*(concepts[s]["sources"] for s in members))
        rel_conflicts = [c for c, t in conflicts.items()
                         if len({p for p in srcs if p in t}) >= 2]
        digest = hashlib.sha256(("\n".join(concepts[s]["text"] for s in members)
                                + "".join(conflicts[c] for c in rel_conflicts)).encode()).hexdigest()[:16]
        out_path = OUT / "topics" / f"{slug}.md"
        if state.get(slug) == digest and out_path.exists():
            page = out_path.read_text(encoding="utf-8")
            lead = re.search(r"^# .+?\n+(.+?)(?:\n\n|\n#)", page, re.S)
            hubs.append((topic, slug, (lead.group(1).strip() if lead else "")[:400], len(members)))
            print(f"  unchanged topics/{slug}.md")
            continue
        member_text = "\n\n---\n\n".join(
            f"[file: concepts/{s}]\n{concepts[s]['text'][:PER_PAGE_CHARS]}" for s in members
        )
        conflict_text = "\n\n".join(
            f"[conflict page: conflicts/{c}]\n{conflicts[c][:3000]}" for c in rel_conflicts
        )
        ents = sorted(entities, key=lambda e: -len(entities[e]["sources"] & srcs))[:10]
        page = llm(
            f"TOPIC: {topic}\n\nMEMBER CONCEPT PAGES:\n\n{member_text}\n\n"
            + (f"PROMOTED CONFLICT PAGES (anchor the Tensions section on these; link them as [[conflicts/<stem>]]):\n{conflict_text}\n\n" if conflict_text else "")
            + f"RELATED ENTITY PAGES (link candidates): {', '.join('entities/' + e for e in ents)}\n"
            f"PROJECTS IN SCOPE (for [src:] tags and [[summaries/<id>__REPORT]] links): {', '.join(sorted(srcs))}",
            system=TEMPLATE,
        )
        out_path.write_text(page.strip() + "\n", encoding="utf-8")
        state[slug] = digest
        any_changed = True
        lead = re.search(r"^# .+?\n+(.+?)(?:\n\n|\n#)", page, re.S)
        hubs.append((topic, slug, (lead.group(1).strip() if lead else "")[:400], len(members)))
        print(f"  wrote topics/{slug}.md ({len(members)} concepts, {len(srcs)} projects, {len(rel_conflicts)} conflicts)")
    state_path.write_text(json.dumps(state, indent=1))
    # Retire hub pages for topics that no longer exist after re-clustering.
    live = {slugify(names.get(str(i), f"Topic {i}")) for i in range(len(clusters))}
    for stale in (OUT / "topics").glob("*.md"):
        if stale.stem not in live:
            stale.unlink()
            any_changed = True
            print(f"  removed stale topics/{stale.stem}.md")
    if not any_changed and (OUT / "index.md").exists():
        print("home unchanged; done")
        return

    n_sum = len(list((HERE / "wiki/summaries").glob("*.md")))
    n_digests = sum((HERE / "wiki/summaries" / f"{d}.md").exists() for d in ("discoveries", "pitfalls"))
    stats = (f"{n_sum - n_digests} project reports + {n_digests} cross-project digests, "
             f"{len(concepts)} concepts, {len(entities)} entities, {len(hubs)} topics")
    hub_list = "\n".join(f"- [[topics/{slug}|{t}]] ({n} concepts): {lead}" for t, slug, lead, n in hubs)
    home = llm(
        "Write the HOME page (markdown, H1 title 'BERIL Knowledge Wiki') for this research "
        "wiki: 2-3 paragraphs introducing the BERIL Research Observatory corpus (AI-conducted "
        "microbial-biology research over the KBase BER Data Lakehouse) and how to read the wiki "
        "(topics are the entry points; concepts/entities/summaries are the reference layers), "
        f"then a '## Topics' section presenting each topic with its one-line hook as a wikilink "
        f"list, then a '## Corpus' line with these stats: {stats}, then a '## Browse' section "
        "linking [[catalog|Full page catalog]], [[summaries/discoveries|Discoveries digest]], "
        "[[summaries/pitfalls|Pitfalls digest]], [[authors/index|Authors]], and [[data/index|Data collections]]. "
        f"Base every topic description on these leads, do not invent findings:\n\n{hub_list}")
    (OUT / "index.md").write_text(home.strip() + "\n", encoding="utf-8")
    print(f"wrote index.md; {stats}")


if __name__ == "__main__":
    main()
