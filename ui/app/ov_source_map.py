"""Resolve an OpenViking resource URI back to the repo file that produced it.

Ingest stages a *flat* copy of each project's curated files
(``observatory_context/staging.py: stage_project``) and uploads the staged
directory as one resource. OpenViking then decomposes each file server-side,
so a search hit looks like::

    viking://resources/projects/<project_id>/<STEM>/<...OV chunking...>
                                            ^^^^^^ the staged file, sans extension

Everything below ``<STEM>`` is OV's own naming (section dirs, document dirs
with content hashes, ``_2more`` chunk files) and has no repo counterpart, so
resolution is file-level: we can name the source file, not the source lines.

Two strategies, in order:

1. **Manifest lookup** (authoritative). The ingest manifest already records
   ``{target_uri: {repo_relative_path: sha256}}`` for every staged file, so the
   mapping is *recorded* rather than guessed. Nothing extra is written at
   ingest time — see ``observatory_context/manifest.py: build_manifest``.
2. **Reconstruction** (fallback). If the manifest is missing or does not cover
   the project, match ``<STEM>`` against the known staged-name list. This is
   what the URI shape implies, and it breaks silently if staging ever stops
   being flat — hence the manifest is preferred.

``PROJECT_METADATA`` and ``CLAIMS_CONTEXT`` are synthesized during staging and
have no source file; they resolve to ``kind="generated"`` with ``source=None``
rather than being reported as failures.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PROJECTS_PREFIX = "viking://resources/projects/"
DOCS_PREFIX = "viking://resources/docs/"

# Mirrors observatory_context/constants.py: PROJECT_CURATED_NAMES. Duplicated
# because the webapp has no dependency on that package (same reasoning as
# RESOURCES_TARGET_URI in app/routes/search.py).
CURATED_NAMES = (
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

# Staged files with no on-disk source: written by stage_project itself.
GENERATED_STEMS = frozenset({"PROJECT_METADATA", "CLAIMS_CONTEXT"})

MEMORY_DIR_NAME = "memories"


@dataclass(frozen=True)
class SourceRef:
    """Where an OV URI came from.

    ``source`` is a repo-relative POSIX path, or None when there is no source
    file (generated content, or an unresolvable URI — ``reason`` says which).
    """

    kind: str  # curated | memory | generated | doc | project | unknown
    source: str | None
    project_id: str | None = None
    via: str | None = None  # "manifest" | "reconstruction"
    reason: str | None = None

    @property
    def resolved(self) -> bool:
        return self.source is not None


def load_manifest(manifest_path: Path) -> dict[str, dict[str, str]]:
    """Read the ingest manifest, or return {} if absent/unreadable.

    A missing manifest is normal (fresh checkout, ingest never run), so this
    degrades to reconstruction rather than raising.
    """
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def resolve(
    uri: str,
    *,
    repo_root: Path,
    manifest: dict[str, dict[str, str]] | None = None,
) -> SourceRef:
    """Resolve an OV resource URI to the repo file that produced it."""
    if uri.startswith(DOCS_PREFIX):
        return _resolve_doc(uri, repo_root)
    if not uri.startswith(PROJECTS_PREFIX):
        return SourceRef("unknown", None, reason="not a projects/ or docs/ URI")

    parts = [p for p in uri[len(PROJECTS_PREFIX) :].split("/") if p]
    if not parts:
        return SourceRef("unknown", None, reason="URI has no project segment")

    project_id = parts[0]
    if len(parts) == 1:
        # The project root itself.
        if (repo_root / "projects" / project_id).is_dir():
            return SourceRef("project", f"projects/{project_id}", project_id)
        return SourceRef(
            "project", None, project_id, reason=f"no project dir: {project_id}"
        )

    stem = parts[1]

    if stem in GENERATED_STEMS:
        return SourceRef(
            "generated",
            None,
            project_id,
            reason=f"{stem} is synthesized during staging, not a repo file",
        )

    # memories/<name>/... -> projects/<id>/memories/<name>.md
    if stem == MEMORY_DIR_NAME:
        if len(parts) < 3:
            return SourceRef(
                "memory", f"projects/{project_id}/{MEMORY_DIR_NAME}", project_id
            )
        candidate = f"projects/{project_id}/{MEMORY_DIR_NAME}/{parts[2]}.md"
        return _confirm(candidate, "memory", project_id, repo_root, manifest)

    # A curated file: the staged name whose stem matches this segment.
    for name in CURATED_NAMES:
        if name == stem or name.rsplit(".", 1)[0] == stem:
            return _confirm(
                f"projects/{project_id}/{name}",
                "curated",
                project_id,
                repo_root,
                manifest,
            )

    # REFUTATION_<n>.md and anything else staged under its own name.
    return _confirm(
        f"projects/{project_id}/{stem}.md",
        "curated",
        project_id,
        repo_root,
        manifest,
    )


def _confirm(
    candidate: str,
    kind: str,
    project_id: str,
    repo_root: Path,
    manifest: dict[str, dict[str, str]] | None,
) -> SourceRef:
    """Prefer the manifest's record; fall back to checking the filesystem."""
    recorded = _manifest_entry(manifest, project_id)
    if recorded:
        if candidate in recorded:
            return SourceRef(kind, candidate, project_id, via="manifest")
        # The manifest covers this project but not this file: the URI is stale
        # (source removed since ingest) or staging changed shape. Say so rather
        # than falling through to a filesystem guess that would hide the drift.
        return SourceRef(
            kind,
            None,
            project_id,
            via="manifest",
            reason=f"{candidate} is not in the ingest manifest for {project_id}",
        )

    if (repo_root / candidate).is_file():
        return SourceRef(kind, candidate, project_id, via="reconstruction")
    return SourceRef(
        kind,
        None,
        project_id,
        via="reconstruction",
        reason=f"no staged file at {candidate}",
    )


def _manifest_entry(
    manifest: dict[str, dict[str, str]] | None, project_id: str
) -> dict[str, str]:
    """The manifest's file map for a project, tolerating the trailing slash.

    Project targets are written with a trailing slash
    (``viking://resources/projects/<id>/``) but the URIs in search results are
    not, so look both up.
    """
    if not manifest:
        return {}
    target = f"{PROJECTS_PREFIX}{project_id}"
    entry = manifest.get(f"{target}/") or manifest.get(target) or {}
    return entry if isinstance(entry, dict) else {}


def _resolve_doc(uri: str, repo_root: Path) -> SourceRef:
    stem = uri[len(DOCS_PREFIX) :].split("/")[0]
    if not stem:
        return SourceRef("doc", None, reason="docs URI has no segment")
    for candidate in (f"docs/{stem}.md", f"{stem}.md"):
        if (repo_root / candidate).is_file():
            return SourceRef("doc", candidate, via="reconstruction")
    return SourceRef("doc", None, reason=f"no docs file for {stem!r}")
