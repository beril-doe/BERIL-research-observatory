#!/usr/bin/env python3
"""Promote cross-project tensions to dedicated conflict pages (v1's best idea).

Scans every concept page's `## Tensions` section, groups tensions that span
multiple projects, and writes one conflict page each to wiki-extra/conflicts/
with the v1 structure: Evidence Sides + Resolving Work. Idempotent: a tension
whose (sorted project set) was already promoted is skipped unless the source
tension text changed (content hash in frontmatter).

    OPENAI_API_KEY=$CBORG_API_KEY OPENAI_BASE_URL=https://api.cborg.lbl.gov \
        .venv/bin/python conflicts_build.py
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import re

from litellm import completion

HERE = pathlib.Path(__file__).parent
OUT = HERE / "wiki-extra" / "conflicts"
MODEL = "openai/claude-sonnet-5"

PROMPT = """You are writing a CONFLICT page for a research wiki: a first-class record of a
real disagreement between projects in the corpus. Input: the tension text as written on
one or more concept pages, with its [src: project] citations.

Write markdown with exactly these sections:
# <Short conflict title — the disagreement, phrased as a tension>
(one-paragraph lead: what the disagreement is and why it matters)
## Evidence Sides
(one bolded subsection per side; each side's claim with its exact numbers and
 [src: project] tags copied from the input — never invent numbers or citations)
## Possible Reconciliations
(hypotheses that could make both sides right — measurement differences, scope
 differences, definitional differences — clearly labeled as hypotheses)
## Resolving Work
(3-5 bullets: the specific analyses or data that would settle it — data + method + question)

Rules: copy numbers exactly; a claim you cannot attribute must not be written; 300-600 words.
Link the source concept pages with [[concepts/<stem>]] wikilinks where given.
"""


def tension_blocks() -> list[dict]:
    blocks = []
    for page in sorted((HERE / "wiki/concepts").glob("*.md")):
        text = page.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^## Tensions?\s*\n(.*?)(?=\n## |\Z)", text, re.M | re.S)
        if not m:
            continue
        body = m.group(1).strip()
        projects = set()
        for t in re.finditer(r"\[src:\s*([^\]]+)\]", body):
            for p in re.split(r"[,;]", t.group(1)):
                projects.add(re.sub(r"__REPORT$", "", p.strip()))
        if len(projects) >= 2:
            blocks.append({"concept": page.stem, "text": body, "projects": projects})
    return blocks


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    existing = {}
    for f in OUT.glob("*.md"):
        m = re.search(r"^<!-- tension-hash: (\w+) -->", f.read_text(encoding="utf-8"), re.M)
        if m:
            existing[f.stem] = m.group(1)

    # Group tensions that share their project set (same disagreement seen from
    # multiple concept pages).
    groups: dict[tuple, list[dict]] = {}
    for b in tension_blocks():
        groups.setdefault(tuple(sorted(b["projects"])), []).append(b)

    written = skipped = 0
    for projects, blocks in sorted(groups.items()):
        slug = "conflict--" + "--".join(projects[:3])
        digest = hashlib.sha256("\n".join(b["text"] for b in blocks).encode()).hexdigest()[:16]
        if existing.get(slug) == digest:
            skipped += 1
            continue
        payload = "\n\n---\n\n".join(
            f"[from concept page: concepts/{b['concept']}]\n{b['text']}" for b in blocks
        )
        resp = completion(
            model=MODEL,
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.cborg.lbl.gov"),
            messages=[{"role": "system", "content": PROMPT},
                      {"role": "user", "content": payload}],
            temperature=0.3, timeout=600,
        ).choices[0].message.content.strip()
        (OUT / f"{slug}.md").write_text(f"<!-- tension-hash: {digest} -->\n{resp}\n", encoding="utf-8")
        written += 1
        print(f"  wrote conflicts/{slug}.md ({len(blocks)} tension block(s), {len(projects)} projects)")
    print(f"conflicts: {written} written, {skipped} unchanged")


if __name__ == "__main__":
    main()
