from __future__ import annotations

from pathlib import Path
import re

from .config import DOCS_TARGET_URI, PROJECTS_TARGET_URI


PROJECT_CURATED_NAMES = (
    "README.md",
    "RESEARCH_PLAN.md",
    "REPORT.md",
    "REVIEW.md",
    "references.md",
    "FINDINGS.md",
    "EXECUTIVE_SUMMARY.md",
    "FAILURE_ANALYSIS.md",
    "DESIGN_NOTES.md",
    "CORRECTIONS.md",
    "beril.yaml",
)

CENTRAL_DOC_NAMES = (
    "pitfalls.md",
    "discoveries.md",
    "performance.md",
    "research_ideas.md",
)

DOC_SOURCE_PATHS = [f"docs/{name}" for name in CENTRAL_DOC_NAMES]

# Per-project canonical knowledge (pitfalls/discoveries/performance) lives in
# projects/<id>/memories/*.md (see /pitfall-capture, /synthesize). Ingest them
# alongside the project's curated docs so OpenViking carries cross-project
# semantic recall.
MEMORY_DIR_NAME = "memories"
_REFUTATION_NAME = re.compile(r"REFUTATION_([1-9][0-9]*)\.md$")


def select_project_files(project_dir: Path) -> list[Path]:
    project_path = Path(project_dir)
    curated = [
        project_path / name
        for name in PROJECT_CURATED_NAMES
        if (project_path / name).is_file()
    ]
    return curated + select_project_refutations(project_path)


def select_project_refutations(project_dir: Path) -> list[Path]:
    """Return numbered refutations in numeric order for semantic recall."""
    numbered = []
    for path in Path(project_dir).glob("REFUTATION_*.md"):
        match = _REFUTATION_NAME.fullmatch(path.name)
        if path.is_file() and match:
            numbered.append((int(match.group(1)), path))
    return [path for _, path in sorted(numbered)]


def select_project_memories(project_dir: Path) -> list[Path]:
    memories_dir = Path(project_dir) / MEMORY_DIR_NAME
    if not memories_dir.is_dir():
        return []
    return sorted(path for path in memories_dir.glob("*.md") if path.is_file())


def select_project_context_sources(project_dir: Path) -> list[Path]:
    """Files that determine staged semantic context and its manifest entry.

    ``claims.json`` drives a Markdown projection. ``runtime.json`` is
    intentionally absent: runtime metadata is available only by direct project
    inspection, never scientific semantic recall.
    """
    project_path = Path(project_dir)
    sources = select_project_files(project_path) + select_project_memories(project_path)
    claims = project_path / "claims.json"
    if claims.is_file():
        sources.append(claims)
    return sources


def select_central_docs(repo_root: Path) -> list[Path]:
    root = Path(repo_root)
    return [root / rel for rel in DOC_SOURCE_PATHS if (root / rel).is_file()]


def project_target_uri(project_id: str) -> str:
    return f"{PROJECTS_TARGET_URI}{project_id}/"


def docs_target_uri(doc_path: Path) -> str:
    return f"{DOCS_TARGET_URI}{Path(doc_path).stem}/"


def iter_project_dirs(projects_dir: Path) -> list[Path]:
    path = Path(projects_dir)
    if not path.exists():
        return []
    return sorted(child for child in path.iterdir() if child.is_dir())
