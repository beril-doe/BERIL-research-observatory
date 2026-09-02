#!/usr/bin/env python3
"""Copy the published wiki into a Quartz content/ dir with injected frontmatter.

Prototype stand-in for a future deterministic `export-quartz` pipeline step.
Usage: quartz_ingest.py <wiki-dir> <quartz-content-dir>
"""

import json
import pathlib
import sys

TYPE_BY_DIR = {"topics": "topic", "projects": "project", "authors": "author", "data": "data"}

# The wiki H1s are naive title-cased slugs, so acronyms come out mangled ("Amr Resistome").
# ponytail: hardcoded map, swap for a curated title map in the real export step.
ACRONYMS = {
    "Amr": "AMR", "Adp1": "ADP1", "Kbase": "KBase", "Ke": "KE", "Nmdc": "NMDC",
    "Pgp": "PGP", "Hgt": "HGT", "T4ss": "T4SS", "Cazy": "CAZy", "Ibd": "IBD",
    "Phb": "PHB", "Cog": "COG", "Fw300": "FW300", "Snipe": "SNIPE", "Sso": "SSO",
    "Asv": "ASV", "Cf": "CF", "Enigma": "ENIGMA", "Msd": "MSD", "Uniref": "UniRef",
    "Fba": "FBA", "Tnseq": "TnSeq", "Paperblast": "PaperBLAST",
    "Webofmicrobes": "WebOfMicrobes", "Microbeatlas": "MicrobeAtlas",
}


def main() -> None:
    src_root, dst_root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pages = [p for p in src_root.rglob("*.md") if ".manifests" not in p.parts]

    for src in pages:
        rel = src.relative_to(src_root)
        typ = "home" if rel.parent == pathlib.Path(".") else TYPE_BY_DIR.get(rel.parts[0], "page")

        lines = src.read_text(encoding="utf-8").splitlines()
        title = rel.stem
        for i, line in enumerate(lines):
            if line.startswith("# "):
                title = line[2:].strip()
                del lines[i]  # Quartz renders the frontmatter title; keeping the H1 duplicates it
                if i < len(lines) and not lines[i].strip():
                    del lines[i]
                break

        if typ != "author":  # author titles are real human names, leave them alone
            title = " ".join(ACRONYMS.get(tok, tok) for tok in title.split(" "))

        out = dst_root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join(lines).lstrip("\n")
        out.write_text(
            f"---\ntitle: {json.dumps(title)}\ntags: [{typ}]\n---\n\n{body}\n", encoding="utf-8"
        )

    print(f"wrote {len(pages)} pages -> {dst_root}")


if __name__ == "__main__":
    main()
