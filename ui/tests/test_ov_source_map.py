"""Tests for resolving OpenViking URIs back to their source repo files.

Uses a synthetic repo/manifest rather than the live corpus so the expectations
are explicit and don't drift as projects are added.
"""

from __future__ import annotations

import json

import pytest

from app.ov_source_map import (
    PROJECTS_PREFIX,
    SourceRef,
    load_manifest,
    resolve,
)

PROJECT = "caulobacter_fur_lipida_loss"

# The real URI from a search hit: 4 levels of OV decomposition below the stem.
DEEP_URI = (
    f"{PROJECTS_PREFIX}{PROJECT}/references/References/"
    "Caulobacter_Δfur_permits_ΔlpxC_published__b5b23115/"
    "Theme_B_ChvG-ChvI_2more_a7ee18b9.md"
)


@pytest.fixture
def repo(tmp_path):
    """A minimal repo with the staged-file layout ingest expects."""
    proj = tmp_path / "projects" / PROJECT
    proj.mkdir(parents=True)
    for name in ("README.md", "REPORT.md", "references.md", "beril.yaml"):
        (proj / name).write_text(f"# {name}\n", encoding="utf-8")
    (proj / "REFUTATION_1.md").write_text("# refutation\n", encoding="utf-8")
    memories = proj / "memories"
    memories.mkdir()
    (memories / "discoveries.md").write_text("# discoveries\n", encoding="utf-8")

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "pitfalls.md").write_text("# pitfalls\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def manifest(repo):
    """Manifest in the real on-disk shape: target URIs carry a trailing slash."""
    return {
        f"{PROJECTS_PREFIX}{PROJECT}/": {
            f"projects/{PROJECT}/README.md": "aaa",
            f"projects/{PROJECT}/REPORT.md": "bbb",
            f"projects/{PROJECT}/references.md": "ccc",
            f"projects/{PROJECT}/beril.yaml": "ddd",
            f"projects/{PROJECT}/REFUTATION_1.md": "eee",
            f"projects/{PROJECT}/memories/discoveries.md": "fff",
        }
    }


# ---------------------------------------------------------------------------
# The core mapping
# ---------------------------------------------------------------------------


def test_deep_chunk_resolves_to_source_file(repo, manifest):
    """The motivating case: 4 levels of OV chunking -> references.md."""
    ref = resolve(DEEP_URI, repo_root=repo, manifest=manifest)
    assert ref.source == f"projects/{PROJECT}/references.md"
    assert ref.kind == "curated"
    assert ref.project_id == PROJECT
    assert ref.via == "manifest"
    assert ref.resolved


@pytest.mark.parametrize(
    ("stem", "expected"),
    [
        ("README", "README.md"),
        ("REPORT", "REPORT.md"),
        ("references", "references.md"),
        ("beril.yaml", "beril.yaml"),  # not decomposed; keeps its extension
        ("REFUTATION_1", "REFUTATION_1.md"),
    ],
)
def test_each_staged_name_resolves(repo, manifest, stem, expected):
    uri = f"{PROJECTS_PREFIX}{PROJECT}/{stem}/some/ov/chunk.md"
    ref = resolve(uri, repo_root=repo, manifest=manifest)
    assert ref.source == f"projects/{PROJECT}/{expected}"


def test_memories_resolve_to_their_markdown(repo, manifest):
    uri = f"{PROJECTS_PREFIX}{PROJECT}/memories/discoveries/chunk.md"
    ref = resolve(uri, repo_root=repo, manifest=manifest)
    assert ref.kind == "memory"
    assert ref.source == f"projects/{PROJECT}/memories/discoveries.md"


def test_project_root_resolves_to_directory(repo, manifest):
    ref = resolve(f"{PROJECTS_PREFIX}{PROJECT}", repo_root=repo, manifest=manifest)
    assert ref.kind == "project"
    assert ref.source == f"projects/{PROJECT}"


def test_resolution_is_file_level_not_chunk_level(repo, manifest):
    """Two different chunks of one file resolve to the same source."""
    a = resolve(DEEP_URI, repo_root=repo, manifest=manifest)
    b = resolve(
        f"{PROJECTS_PREFIX}{PROJECT}/references/References/Other_ab12cd34.md",
        repo_root=repo,
        manifest=manifest,
    )
    assert a.source == b.source


# ---------------------------------------------------------------------------
# Generated content has no source
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stem", ["PROJECT_METADATA", "CLAIMS_CONTEXT"])
def test_generated_files_report_no_source(repo, manifest, stem):
    """Synthesized at staging — not a failure, but not a repo file either."""
    ref = resolve(
        f"{PROJECTS_PREFIX}{PROJECT}/{stem}/chunk.md", repo_root=repo, manifest=manifest
    )
    assert ref.kind == "generated"
    assert ref.source is None
    assert not ref.resolved
    assert "synthesized" in ref.reason


# ---------------------------------------------------------------------------
# Manifest vs reconstruction
# ---------------------------------------------------------------------------


def test_reconstruction_used_when_no_manifest(repo):
    ref = resolve(DEEP_URI, repo_root=repo, manifest=None)
    assert ref.source == f"projects/{PROJECT}/references.md"
    assert ref.via == "reconstruction"


def test_reconstruction_used_when_project_absent_from_manifest(repo):
    """A project ingested after the manifest was last written still resolves."""
    ref = resolve(DEEP_URI, repo_root=repo, manifest={"viking://resources/projects/other/": {}})
    assert ref.source == f"projects/{PROJECT}/references.md"
    assert ref.via == "reconstruction"


def test_manifest_and_reconstruction_agree(repo, manifest):
    for stem in ("README", "REPORT", "references"):
        uri = f"{PROJECTS_PREFIX}{PROJECT}/{stem}/c.md"
        assert (
            resolve(uri, repo_root=repo, manifest=manifest).source
            == resolve(uri, repo_root=repo, manifest=None).source
        )


def test_manifest_miss_is_reported_not_guessed(repo, manifest):
    """A file dropped from the manifest resolves to None even though it's on disk.

    Silently falling back to the filesystem here would mask ingest drift — the
    whole reason the manifest is authoritative.
    """
    del manifest[f"{PROJECTS_PREFIX}{PROJECT}/"][f"projects/{PROJECT}/references.md"]
    ref = resolve(DEEP_URI, repo_root=repo, manifest=manifest)
    assert ref.source is None
    assert ref.via == "manifest"
    assert "not in the ingest manifest" in ref.reason


def test_manifest_target_without_trailing_slash_still_matches(repo, manifest):
    """Search-result URIs have no trailing slash; manifest targets do."""
    entry = manifest.pop(f"{PROJECTS_PREFIX}{PROJECT}/")
    manifest[f"{PROJECTS_PREFIX}{PROJECT}"] = entry
    ref = resolve(DEEP_URI, repo_root=repo, manifest=manifest)
    assert ref.source == f"projects/{PROJECT}/references.md"
    assert ref.via == "manifest"


# ---------------------------------------------------------------------------
# Docs and malformed input
# ---------------------------------------------------------------------------


def test_docs_uri_resolves(repo):
    ref = resolve("viking://resources/docs/pitfalls/chunk.md", repo_root=repo)
    assert ref.kind == "doc"
    assert ref.source == "docs/pitfalls.md"


def test_unknown_docs_file_reports_reason(repo):
    ref = resolve("viking://resources/docs/nonexistent/c.md", repo_root=repo)
    assert ref.source is None
    assert "nonexistent" in ref.reason


@pytest.mark.parametrize(
    "uri",
    [
        "viking://memories/something/else.md",  # wrong scope
        "viking://resources/skills/berdl.md",
        "not-a-uri",
        "",
    ],
)
def test_non_project_uris_are_unknown(repo, uri):
    ref = resolve(uri, repo_root=repo)
    assert ref.kind == "unknown"
    assert not ref.resolved


def test_bare_projects_prefix_is_unknown(repo):
    ref = resolve(PROJECTS_PREFIX, repo_root=repo)
    assert ref.kind == "unknown"
    assert "no project segment" in ref.reason


def test_missing_project_dir_reports_reason(repo):
    ref = resolve(f"{PROJECTS_PREFIX}ghost_project", repo_root=repo)
    assert ref.source is None
    assert "no project dir" in ref.reason


def test_unstaged_file_does_not_resolve(repo):
    """Only curated/staged files reach OV; a random name must not resolve."""
    ref = resolve(f"{PROJECTS_PREFIX}{PROJECT}/notes/c.md", repo_root=repo, manifest=None)
    assert ref.source is None
    assert not ref.resolved


def test_path_traversal_segment_does_not_escape_repo(repo):
    """A hostile URI segment must not resolve to a file outside the project."""
    (repo / "secret.md").write_text("secret\n", encoding="utf-8")
    ref = resolve(f"{PROJECTS_PREFIX}{PROJECT}/../../secret/c.md", repo_root=repo)
    assert ref.source is None


# ---------------------------------------------------------------------------
# load_manifest
# ---------------------------------------------------------------------------


def test_load_manifest_reads_real_shape(tmp_path):
    path = tmp_path / "context_manifest.json"
    payload = {f"{PROJECTS_PREFIX}{PROJECT}/": {f"projects/{PROJECT}/README.md": "sha"}}
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert load_manifest(path) == payload


@pytest.mark.parametrize("content", [None, "not json{", '"a string"', "[1,2]"])
def test_load_manifest_degrades_to_empty(tmp_path, content):
    """Missing or malformed manifest falls back to reconstruction, never raises."""
    path = tmp_path / "context_manifest.json"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    assert load_manifest(path) == {}


def test_sourceref_resolved_property():
    assert SourceRef("curated", "projects/x/README.md").resolved
    assert not SourceRef("generated", None).resolved
