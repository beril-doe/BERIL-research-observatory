#!/usr/bin/env python3
"""Copy the OpenKB wiki + wiki-extra pages into a Quartz content/ dir.

Adapted from the v2 compendium prototype. Transformations:
  - [src: a; b] / [src: a, b] tags become wikilinks to the project summary pages
  - AGENTS.md, log.md, and reports/ are skipped (operational files, not content)

Usage: quartz_ingest.py <kb-root> <quartz-content-dir>
"""

from __future__ import annotations

import pathlib
import re
import shutil
import sys

SRC_TAG = re.compile(r"\[src:\s*([^\]]+)\]")
SKIP = {"AGENTS.md", "log.md"}


def linkify_src(text: str, summary_pages: dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        links = []
        for part in re.split(r"[,;]", m.group(1)):
            sid = re.sub(r"__REPORT$", "", part.strip())
            if not sid:
                continue
            page = summary_pages.get(sid)
            links.append(f"[[summaries/{page}|{sid}]]" if page else sid)
        return "<sub>src: " + ", ".join(links) + "</sub>"

    return SRC_TAG.sub(repl, text)


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9/]+", "-", s.lower()).strip("-")


def strip_dead_wikilinks(text: str, targets: set[str]) -> str:
    """Downgrade [[links]] Quartz can't resolve to plain text.

    Quartz resolves slugified targets by full path or file basename, so both are
    accepted here. The wiki source keeps the dangling links (future compiles may
    create the targets); only the published site hides them.
    """
    by_basename: dict[str, list[str]] = {}
    for t in targets:
        by_basename.setdefault(t.rsplit("/", 1)[-1], []).append(t)

    def repl(m: re.Match) -> str:
        slug, label = _slug(m.group(1).lstrip("/")), m.group(2)
        if slug in targets:
            return m.group(0)
        hits = by_basename.get(slug.rsplit("/", 1)[-1], [])
        if len(hits) == 1:  # wrong/omitted namespace but unique page: repair the path
            return f"[[{hits[0]}|{label or m.group(1).rsplit('/', 1)[-1]}]]"
        return label or m.group(1).rsplit("/", 1)[-1].replace("-", " ")

    return re.sub(r"\[\[([^\]|#]+?)(?:\|([^\]]*))?\]\]", repl, text)


def main() -> None:
    kb, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    known = {
        re.sub(r"__REPORT$", "", f.stem): f.stem
        for f in (kb / "wiki" / "summaries").glob("*.md")
    }
    targets = {
        _slug(str(f.relative_to(root)).removesuffix(".md"))
        for root in (kb / "wiki", kb / "wiki-extra") if root.is_dir()
        for f in root.rglob("*.md")
    }
    targets.add("catalog")  # wiki/index.md is renamed to catalog.md below
    targets.discard("index")
    shutil.rmtree(dst, ignore_errors=True)

    n = 0
    for root in (kb / "wiki", kb / "wiki-extra"):
        if not root.is_dir():
            continue
        for src in root.rglob("*.md"):
            rel = src.relative_to(root)
            if src.name in SKIP or rel.parts[0] == "reports":
                continue
            # OpenKB's catalog index steps aside for the narrative home in wiki-extra/.
            if root.name == "wiki" and rel == pathlib.Path("index.md"):
                rel = pathlib.Path("catalog.md")
            out = dst / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            text = src.read_text(encoding="utf-8", errors="replace")
            text = linkify_src(strip_dead_wikilinks(text, targets), known)
            # Summaries must lead to their raw report, and self-[src:] tags are
            # circular — point both at the sources/ page (the provenance hop
            # reviewers need).
            if rel.parts[0] == "summaries" and (root / "sources" / src.name).exists():
                raw = f"sources/{rel.stem}"
                text = text.replace(f"[[summaries/{rel.stem}|", f"[[{raw}|")
                text = re.sub(r"^# .+$", lambda m: m.group(0) + f"\n\n> Raw report: [[{raw}|{rel.stem}]]",
                              text, count=1, flags=re.M)
            out.write_text(text, encoding="utf-8")
            n += 1

    images = kb / "wiki" / "sources" / "images"
    if images.is_dir():
        shutil.copytree(images, dst / "sources" / "images", dirs_exist_ok=True)

    print(f"wrote {n} pages -> {dst}")


if __name__ == "__main__":
    main()
