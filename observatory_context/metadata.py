from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from .selection import select_project_refutations


@dataclass(frozen=True)
class ProjectMetadata:
    project_id: str
    title: str
    status: str
    author_names: list[str]
    markdown: str


def build_project_metadata(project_dir: str | Path) -> ProjectMetadata:
    project_path = Path(project_dir)
    beril = _read_beril_yaml(project_path / "beril.yaml")
    readme = _read_text(project_path / "README.md")

    project_id = _string_field(beril.get("project_id")) or project_path.name
    title = _readme_title(readme) or project_id
    status = _string_field(beril.get("status")) or _readme_status(readme)
    engine_value = beril.get("engine")
    engine: dict[str, Any] = engine_value if isinstance(engine_value, dict) else {}
    authors = _authors(beril.get("authors"))
    if not any(a["name"] or a["orcid"] for a in authors):
        # Most projects predate beril.yaml; their authors are only in prose.
        authors = _markdown_authors(readme) or _markdown_authors(
            _read_text(project_path / "RESEARCH_PLAN.md")
        )
    author_names = [author["name"] for author in authors if author["name"]]

    markdown = _metadata_markdown(
        project_id=project_id,
        title=title,
        status=status,
        created_at=_string_field(beril.get("created_at")),
        last_session_at=_string_field(beril.get("last_session_at")),
        branch=_string_field(beril.get("branch")),
        engine_name=_string_field(engine.get("name")),
        authors=authors,
        source_files=_source_metadata_files(project_path),
    )

    return ProjectMetadata(
        project_id=project_id,
        title=title,
        status=status,
        author_names=author_names,
        markdown=markdown,
    )


def _read_beril_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _readme_title(readme: str) -> str:
    for line in readme.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _readme_status(readme: str) -> str:
    lines = readme.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## Status":
            for status_line in lines[index + 1 :]:
                stripped = status_line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    return ""
                return stripped
    return ""


def _authors(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    authors = []
    for author in value:
        author_fields = author if isinstance(author, dict) else {}
        authors.append(
            {
                "name": _string_field(author_fields.get("name")),
                "affiliation": _string_field(author_fields.get("affiliation")),
                "orcid": _string_field(author_fields.get("orcid")),
            }
        )
    return authors


_ORCID = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")
_AUTHORS_HEADING = re.compile(r"^#{2,3}\s*(Authors|Contributors)\b", re.IGNORECASE)
_ANY_HEADING = re.compile(r"^#{1,6}\s")
_ROLE_WORDS = {"author", "authors", "contributor", "lead", "pi"}


def _markdown_authors(text: str) -> list[dict[str, str]]:
    """Authors from a markdown ``## Authors`` (or ``Contributors``) list.

    The fallback for projects with no ``beril.yaml`` authors — most of the
    repo — so their ``PROJECT_METADATA.md`` names who wrote them. Reads the
    formats the repo's READMEs actually use: ``Name (https://orcid.org/…),
    Affiliation``; ``**Name** | ORCID: … | Role``; ``Name (ORCID: [id](url)) —
    Affiliation``; ``Name (Affiliation) — ORCID …``; an author split over
    bullets (``**Name**`` then ``ORCID: …`` then ``Affiliation: …``); and a
    bare line with no bullet at all (``Name`` or ``Name (LBL), ORCID …``).

    A plain line is an author only when it looks like one: it carries an
    ORCiD, or it is short and not a sentence. That keeps a paragraph under
    the heading ("The following people contributed:") from becoming a name.
    """
    lines = text.splitlines()
    start = next((i for i, row in enumerate(lines) if _AUTHORS_HEADING.match(row.strip())), None)
    if start is None:
        return []
    authors: list[dict[str, str]] = []
    for raw in lines[start + 1:]:
        line = raw.strip()
        if _ANY_HEADING.match(line):
            break
        if not line:
            continue
        if not line.startswith(("-", "*")) and not _plain_author_line(line):
            continue
        item = line.lstrip("-* ").strip()
        if not item:
            continue
        lowered = item.lower()
        if authors and lowered.startswith(("orcid:", "affiliation:")):
            # A continuation bullet for the author above.
            key, _, value = item.partition(":")
            if key.strip().lower() == "orcid":
                found = _ORCID.search(value)
                authors[-1]["orcid"] = found.group(0) if found else authors[-1]["orcid"]
            else:
                authors[-1]["affiliation"] = _clean(value)
            continue
        authors.append(_author_from_line(item))
    return [a for a in authors if a["name"] or a["orcid"]]


_MAX_PLAIN_AUTHOR_LINE = 120


def _plain_author_line(line: str) -> bool:
    """Whether an unbulleted line under the heading names an author."""
    if line.startswith(("|", ">", "`", "<", "!")):
        return False
    if _ORCID.search(line):
        return True
    return len(line) <= _MAX_PLAIN_AUTHOR_LINE and not line.endswith((".", ":", "?", "!"))


def _author_from_line(item: str) -> dict[str, str]:
    found = _ORCID.search(item)
    orcid = found.group(0) if found else ""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", item)        # [text](url) -> text
    text = re.sub(r"https?://\S+", "", text)
    text = _ORCID.sub("", text)
    text = re.sub(r"\bORCID\b:?", "", text, flags=re.IGNORECASE)
    text = text.replace("**", "")
    text = re.sub(r"\(\s*\)", "", text)
    # Name first; then whatever follows a separator is the affiliation.
    parts = [p.strip(" ,;-—()") for p in re.split(r"\s*[|—,(]\s*|\s+-\s+", text)]
    parts = [p for p in parts if p and p.lower() not in _ROLE_WORDS]
    name = parts[0] if parts else ""
    affiliation = ", ".join(parts[1:])
    return {"name": _clean(name), "affiliation": _clean(affiliation), "orcid": orcid}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" ,;-—()")


def _metadata_markdown(
    *,
    project_id: str,
    title: str,
    status: str,
    created_at: str,
    last_session_at: str,
    branch: str,
    engine_name: str,
    authors: list[dict[str, str]],
    source_files: list[str],
) -> str:
    lines = [
        f"# Project Metadata: {project_id}",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Project ID | {project_id} |",
        f"| Title | {title} |",
        f"| Status | {status} |",
        f"| Created At | {created_at} |",
        f"| Last Session At | {last_session_at} |",
        f"| Branch | {branch} |",
        f"| Engine | {engine_name} |",
        f"| Context source files | {', '.join(source_files)} |",
        "",
        "## Authors",
        "",
        "| Name | Affiliation | ORCID |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| {author['name']} | {author['affiliation']} | {author['orcid']} |"
        for author in authors
    )
    return "\n".join(lines)


def _source_metadata_files(project_path: Path) -> list[str]:
    names = []
    if (project_path / "beril.yaml").is_file():
        names.append("beril.yaml")
    if (project_path / "README.md").is_file():
        names.append("README.md")
    if (project_path / "claims.json").is_file():
        names.append("claims.json")
    names.extend(path.name for path in select_project_refutations(project_path))
    return names


def _string_field(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime | date):
        return value.isoformat()
    return str(value)
