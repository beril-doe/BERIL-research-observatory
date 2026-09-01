#!/usr/bin/env python3
"""Deterministic wiki pages OpenKB shouldn't hallucinate: authors and data collections.

Carried over from v1/v2: author pages from project README ``## Authors`` blocks
(ORCID-keyed, via people.py) and data-collection pages from ui/config/collections.yaml.
Output goes to wiki-extra/ (NOT wiki/ — OpenKB owns that tree) and is merged into
the Quartz content dir at publish time by build_quartz.sh.

    .venv/bin/python extra_pages.py          # writes wiki-extra/{authors,data}/
"""

from __future__ import annotations

import pathlib
import re

import yaml

from people import build_author_index

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent
OUT = HERE / "wiki-extra"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def wiki_projects() -> list[str]:
    """Project ids that have (or will have) a summary page, from staging/."""
    return sorted(
        re.sub(r"__REPORT$", "", f.stem)
        for f in (HERE / "staging").glob("*__REPORT.md")
    )


def write_authors() -> int:
    readmes = {
        p.parent.name: (p.read_text(encoding="utf-8", errors="replace"))
        for p in REPO.glob("projects/*/README.md")
        if (p.parent / "REPORT.md").exists()
    }
    index = build_author_index(readmes)
    out = OUT / "authors"
    out.mkdir(parents=True, exist_ok=True)
    known = set(wiki_projects())
    for record in index.values():
        lines = [f"# {record.name}", ""]
        if record.orcid:
            lines.append(f"ORCID: [{record.orcid}](https://orcid.org/{record.orcid})")
            lines.append("")
        lines.append(f"## Projects ({len(record.projects)})")
        lines.append("")
        for proj in record.projects:
            link = f"[[summaries/{proj}__REPORT|{proj}]]" if proj in known else proj
            lines.append(f"- {link}")
        (out / f"{slugify(record.name)}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(index)


def write_collections() -> int:
    cfg = yaml.safe_load((REPO / "ui/config/collections.yaml").read_text(encoding="utf-8"))
    out = OUT / "data"
    out.mkdir(parents=True, exist_ok=True)
    projects = wiki_projects()
    # Which projects mention this collection id in their report (cheap deterministic join).
    mention: dict[str, list[str]] = {}
    for proj in projects:
        text = (HERE / "staging" / f"{proj}__REPORT.md").read_text(encoding="utf-8", errors="replace")
        for coll in cfg["collections"]:
            if coll["id"] in text:
                mention.setdefault(coll["id"], []).append(proj)

    for coll in cfg["collections"]:
        lines = [f"# {coll['name']}", ""]
        meta = [f"Provider: {coll.get('provider', '?')}"]
        if coll.get("website"):
            meta.append(f"[Website]({coll['website']})")
        if coll.get("doi"):
            meta.append(f"DOI: [{coll['doi']}](https://doi.org/{coll['doi']})")
        lines += [" · ".join(meta), ""]
        for key, heading in (("description", "Description"), ("philosophy", "Purpose")):
            if coll.get(key):
                lines += [f"## {heading}", "", str(coll[key]).strip(), ""]
        if coll.get("scale_stats"):
            lines += ["## Scale", ""]
            lines += [f"- {k}: {v:,}" if isinstance(v, int) else f"- {k}: {v}"
                      for k, v in coll["scale_stats"].items()]
            lines.append("")
        used = mention.get(coll["id"], [])
        if used:
            lines += [f"## Used by projects ({len(used)})", ""]
            lines += [f"- [[summaries/{p}__REPORT|{p}]]" for p in used]
            lines.append("")
        (out / f"{slugify(coll['id'])}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(cfg["collections"])


def write_indexes() -> None:
    for sub, title in (("authors", "Authors"), ("data", "Data Collections")):
        pages = sorted(p.stem for p in (OUT / sub).glob("*.md") if p.stem != "index")
        lines = [f"# {title}", ""]
        lines += [f"- [[{sub}/{s}|{s.replace('-', ' ').title()}]]" for s in pages]
        (OUT / sub / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    n_a = write_authors()
    n_c = write_collections()
    write_indexes()
    print(f"wrote {n_a} author pages, {n_c} collection pages + 2 indexes -> {OUT}")
