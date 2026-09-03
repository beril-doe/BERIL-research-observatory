#!/usr/bin/env python3
"""Figure placement for the wiki: manifest + LLM-chosen placements, cached.

Phase A (deterministic): parse every project report's ![caption](figures/...)
embeds into figures-manifest.json, keeping the caption and the report paragraph
around each embed (what the figure evidences).

Phase B (LLM, cached by page-content hash): for each summary / topic hub /
conflict page, ask the model WHERE figures from the page's cited projects
support the text. The model returns structured placements only — it never
rewrites prose. Results go to figures-placements.json; quartz_ingest.py splices
them at publish time. Pages whose content hash is unchanged are skipped.

Also emits figures-csv-queue.md: pages the model flags as needing a chart for
tabular/CSV evidence that has no figure (review queue, nothing auto-generated).

    OPENAI_API_KEY=$CBORG_API_KEY OPENAI_BASE_URL=https://api.cborg.lbl.gov \
        .venv/bin/python figures_build.py
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re

from litellm import completion

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent
MODEL = "openai/claude-sonnet-5"
MAX_PLACE = {"summaries": 2, "topics": 3, "conflicts": 1}
MAX_CANDIDATES = 40
PROMPT_V = "v2-flagship"  # bump to invalidate all cached placements

PROMPT = """You place existing figures into a scientific wiki page. You are given the page's
paragraphs (numbered) and candidate figures (numbered), each with its caption and the
report context it illustrates. Place ONLY flagship figures — ones a reader must see to
understand the page's KEY claims, in the context of the reported data. The complete
figure set remains available on the raw project report page, so when in doubt, leave it
out: most pages should get 0-2 figures, and AT MOST {max_place}. Never place decorative,
redundant, or merely-related figures.

Also: if the page discusses quantitative evidence that clearly lacks visual support
(a dense table, a distribution, a correlation described only in prose) and no candidate
figure covers it, add a csv_flag describing what should be visualized.

Reply with ONLY JSON:
{{"placements": [{{"after_paragraph": <int>, "figure": <int>, "caption": "<one-sentence caption, may refine the original>"}}],
  "csv_flags": ["<what to visualize and why>", ...]}}
"""


def paragraphs(body: str) -> list[str]:
    body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S)
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def build_manifest() -> dict[str, list[dict]]:
    manifest: dict[str, list[dict]] = {}
    for report in sorted(REPO.glob("projects/*/REPORT.md")):
        project = report.parent.name
        text = report.read_text(encoding="utf-8", errors="replace")
        figs = []
        for par in paragraphs(text):
            for m in re.finditer(r"!\[([^\]]*)\]\((figures/[^)]+)\)", par):
                path = report.parent / m.group(2)
                if path.exists():
                    ctx = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", par).strip()[:400]
                    figs.append({"file": m.group(2), "caption": m.group(1), "context": ctx})
        if figs:
            manifest[project] = figs
    (HERE / "figures-manifest.json").write_text(json.dumps(manifest, indent=1))
    return manifest


def cited_projects(text: str, projects: set[str]) -> list[str]:
    ids = set()
    for m in re.finditer(r"\[src:\s*([^\]]+)\]", text):
        for p in re.split(r"[,;]", m.group(1)):
            ids.add(re.sub(r"__REPORT$", "", p.strip()))
    return sorted(ids & projects)


def target_pages() -> list[tuple[str, pathlib.Path]]:
    out = []
    for f in sorted((HERE / "wiki/summaries").glob("*__REPORT.md")):
        out.append(("summaries", f))
    for sub in ("topics", "conflicts"):
        for f in sorted((HERE / "wiki-extra" / sub).glob("*.md")):
            out.append((sub, f))
    return out


def main() -> None:
    manifest = build_manifest()
    print(f"manifest: {sum(len(v) for v in manifest.values())} figures across {len(manifest)} projects")
    state_path = HERE / ".figures-state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    placements_path = HERE / "figures-placements.json"
    placements = json.loads(placements_path.read_text()) if placements_path.exists() else {}
    csv_flags: dict[str, list[str]] = {}
    calls = skipped = 0

    for kind, page in target_pages():
        rel = f"{page.parent.name}/{page.name}" if kind == "summaries" else f"{kind}/{page.name}"
        text = page.read_text(encoding="utf-8", errors="replace")
        page_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        digest = hashlib.sha256((PROMPT_V + text).encode()).hexdigest()[:16]
        if state.get(rel) == digest:
            skipped += 1
            continue
        if kind == "summaries":
            projs = [re.sub(r"__REPORT$", "", page.stem)]
        else:
            projs = cited_projects(text, set(manifest))
        cands = []
        for p in projs:
            for fig in manifest.get(p, [])[:6]:
                cands.append({"project": p, **fig})
        cands = cands[:MAX_CANDIDATES]
        if not cands:
            state[rel] = digest
            placements.pop(rel, None)
            continue
        pars = paragraphs(text)
        par_block = "\n".join(f"[{i}] {p[:300]}" for i, p in enumerate(pars))
        cand_block = "\n".join(
            f"[{i}] {c['project']}/{c['file']} — caption: {c['caption']!r} — context: {c['context'][:200]!r}"
            for i, c in enumerate(cands))
        resp = completion(
            model=MODEL,
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.cborg.lbl.gov"),
            messages=[{"role": "system", "content": PROMPT.format(max_place=MAX_PLACE[kind])},
                      {"role": "user", "content": f"PAGE PARAGRAPHS:\n{par_block}\n\nCANDIDATE FIGURES:\n{cand_block}"}],
            temperature=0.2, timeout=300,
        ).choices[0].message.content
        try:
            data = json.loads(re.search(r"\{.*\}", resp, re.S).group(0))
        except (AttributeError, json.JSONDecodeError):
            print(f"  ! unparseable response for {rel}, skipping")
            continue
        placed = []
        for pl in data.get("placements", [])[:MAX_PLACE[kind]]:
            try:
                c = cands[int(pl["figure"])]
                idx = int(pl["after_paragraph"])
            except (KeyError, ValueError, IndexError, TypeError):
                continue
            if 0 <= idx < len(pars):
                placed.append({"after_paragraph": idx, "project": c["project"],
                               "file": c["file"], "caption": str(pl.get("caption") or c["caption"])[:300]})
        placements[rel] = {"page_hash": page_hash, "placements": placed}
        if data.get("csv_flags"):
            csv_flags[rel] = [str(x)[:300] for x in data["csv_flags"][:3]]
        state[rel] = digest
        calls += 1
        print(f"  {rel}: {len(placed)} placement(s)" + (f", {len(data['csv_flags'])} csv flag(s)" if data.get("csv_flags") else ""))

    placements_path.write_text(json.dumps(placements, indent=1))
    state_path.write_text(json.dumps(state, indent=1))
    if csv_flags:
        lines = ["# CSV / visualization review queue", "",
                 "Pages the placement pass flagged as needing a chart for evidence with no figure.", ""]
        for rel, flags in sorted(csv_flags.items()):
            lines.append(f"## {rel}")
            lines += [f"- {f}" for f in flags]
            lines.append("")
        (HERE / "figures-csv-queue.md").write_text("\n".join(lines))
    total = sum(len(v["placements"]) for v in placements.values())
    print(f"figures: {calls} pages placed, {skipped} unchanged, {total} total placements"
          + (f", csv queue: {sum(len(v) for v in csv_flags.values())} flags" if csv_flags else ""))


if __name__ == "__main__":
    main()
