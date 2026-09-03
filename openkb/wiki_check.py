#!/usr/bin/env python3
"""Post-compile citation and numeric-fidelity checks for the OpenKB wiki.

Carried over from the v2 compendium's citation-whitelist idea, recast as a
checker over OpenKB output. Run after every `openkb add` / `recompile`:

    python3 wiki_check.py [<kb-root>]

Checks (concepts/ and entities/ pages):
  ERROR  [src: id] cites an id with no corresponding source document
  WARN   a paragraph containing figures (numbers/percentages) has no [src:] tag
  WARN   a number in a cited paragraph appears in none of its cited sources

Exit code 1 if any ERROR, else 0. WARNs are reported but do not fail.
"""

from __future__ import annotations

import pathlib
import re
import sys

SRC_TAG = re.compile(r"\[src:\s*([^\]]+)\]")
# Numbers worth verifying: decimals, percentages, thousands-separated, or >=3 digits.
# Skips small integers (list positions, "3 lines of evidence") to avoid noise.
NUMBER = re.compile(r"\d[\d,]*\.\d+|\d[\d,]{3,}|\d+(?:\.\d+)?%|\d+\.\d+e-?\d+")


def norm_num(tok: str) -> str:
    return tok.replace(",", "").rstrip("%")


def source_ids(kb: pathlib.Path) -> dict[str, str]:
    """Map source id -> source text. Ids match the [src: <id>] convention:
    the staging filename minus __REPORT.md / .md."""
    texts: dict[str, str] = {}
    for d in (kb / "staging", kb / "raw"):
        if not d.is_dir():
            continue
        for f in d.glob("*.md"):
            sid = re.sub(r"__REPORT$", "", f.stem)
            texts.setdefault(sid, f.read_text(encoding="utf-8", errors="replace"))
    return texts


def paragraphs(body: str) -> list[str]:
    # Fold bullet lists into their own paragraphs; skip headings and frontmatter.
    body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S)
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.lstrip().startswith("#")]


def cited_ids(par: str) -> list[str]:
    ids: list[str] = []
    for m in SRC_TAG.finditer(par):
        for part in re.split(r"[,;]", m.group(1)):
            sid = re.sub(r"__REPORT$", "", part.strip())
            if sid and sid not in ids:
                ids.append(sid)
    return ids


def is_table_or_links(par: str) -> bool:
    """Tables and link-list bullets get cited at section level; don't warn on them."""
    lines = [ln.strip() for ln in par.splitlines() if ln.strip()]
    return all(ln.startswith("|") or ln.startswith("- [[") for ln in lines)


def main() -> int:
    kb = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent
    sources = source_ids(kb)
    if not sources:
        print(f"wiki_check: no sources found under {kb}/staging or {kb}/raw", file=sys.stderr)
        return 1

    errors: list[str] = []
    warns: list[str] = []
    n_pages = n_cited_pars = n_numeric_pars = 0

    roots = [(kb / "wiki", "concepts"), (kb / "wiki", "entities"), (kb / "wiki-extra", "topics")]
    for base, sub in roots:
        for page in sorted((base / sub).glob("*.md")):
            n_pages += 1
            rel = f"{sub}/{page.name}"
            for i, par in enumerate(paragraphs(page.read_text(encoding="utf-8", errors="replace")), 1):
                ids = cited_ids(par)
                nums = NUMBER.findall(SRC_TAG.sub("", par))
                if ids:
                    n_cited_pars += 1
                unknown = [s for s in ids if s not in sources]
                for s in unknown:
                    errors.append(f"{rel} ¶{i}: unknown source id [src: {s}]")
                if nums and not ids:
                    if not is_table_or_links(par):
                        warns.append(f"{rel} ¶{i}: {len(nums)} figure(s) but no [src:] citation: {par[:90]!r}")
                    continue
                if nums and ids:
                    n_numeric_pars += 1
                    pool = "".join(sources[s] for s in ids if s in sources).replace(",", "")
                    for tok in nums:
                        if norm_num(tok) not in pool:
                            warns.append(f"{rel} ¶{i}: number {tok!r} not found in cited source(s) {ids}")

    # Integration-depth audit: every project should feed >=2 concept/topic pages.
    uptake: dict[str, int] = {}
    proj_ids = {s for s in sources if not s.startswith(("discoveries", "pitfalls"))}
    for base, sub in [(kb / "wiki", "concepts"), (kb / "wiki-extra", "topics")]:
        for page in (base / sub).glob("*.md"):
            for sid in set(cited_ids(page.read_text(encoding="utf-8", errors="replace"))):
                if sid in proj_ids:
                    uptake[sid] = uptake.get(sid, 0) + 1
    for p in sorted(proj_ids):
        if uptake.get(p, 0) < 2:
            warns.append(f"uptake: project '{p}' cited by only {uptake.get(p, 0)} concept/topic page(s) — under-integrated")

    # Near-duplicate concepts: heavy source overlap + shared name tokens.
    stops = {"the", "of", "in", "and", "for", "to", "a", "vs", "with"}
    cinfo = []
    for page in (kb / "wiki" / "concepts").glob("*.md"):
        text = page.read_text(encoding="utf-8", errors="replace")
        srcs = set(re.findall(r'summaries/([\w.-]+?)__REPORT', text[:1500]))
        toks = set(page.stem.split("-")) - stops
        cinfo.append((page.stem, srcs, toks))
    for i, (a, sa, ta) in enumerate(cinfo):
        for b, sb, tb in cinfo[i + 1:]:
            if sa and sb and len(sa & sb) / max(1, len(sa | sb)) >= 0.5 and len(ta & tb) >= 2:
                warns.append(f"duplicate-concepts? '{a}' and '{b}' share {len(sa & sb)} sources and name tokens {sorted(ta & tb)}")

    print(f"wiki_check: {n_pages} pages, {n_cited_pars} cited paragraphs, "
          f"{n_numeric_pars} numeric paragraphs verified against {len(sources)} sources")
    for w in warns:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    print(f"wiki_check: {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
