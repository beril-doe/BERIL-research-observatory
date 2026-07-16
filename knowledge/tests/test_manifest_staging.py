from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from observatory_context import staging
from observatory_context.manifest import build_manifest, changed_targets
from observatory_context.selection import select_project_context_sources


def write(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_manifest_detects_changed_and_unchanged_targets(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    write(source, "same")

    old = build_manifest({"target-b": [source], "target-a": [source]}, tmp_path)
    unchanged = build_manifest({"target-b": [source], "target-a": [source]}, tmp_path)

    assert changed_targets(old, unchanged) == []

    write(source, "changed")
    changed = build_manifest({"target-b": [source], "target-a": [source]}, tmp_path)

    assert changed_targets(old, changed) == ["target-a", "target-b"]


def test_stage_project_excludes_data_and_removes_stale_file(
    tmp_path: Path, monkeypatch
) -> None:
    project = tmp_path / "projects" / "demo"
    staging_dir = tmp_path / "knowledge" / "staging"
    write(project / "README.md", "# Demo\n")
    write(project / "REPORT.md", "# Report\n")
    write(project / "data" / "README.md", "# Data\n")
    write(staging_dir / "projects" / "demo" / "OLD.md", "old")

    monkeypatch.setattr(
        staging,
        "select_project_files",
        lambda project_dir: [project_dir / "README.md", project_dir / "REPORT.md"],
    )
    monkeypatch.setattr(
        staging,
        "build_project_metadata",
        lambda project_dir: SimpleNamespace(markdown="# Metadata\n"),
    )

    staged = staging.stage_project(project, staging_dir)

    assert staged == staging_dir / "projects" / "demo"
    assert (staged / "README.md").read_text(encoding="utf-8") == "# Demo\n"
    assert (staged / "REPORT.md").is_file()
    assert (staged / "PROJECT_METADATA.md").read_text(
        encoding="utf-8"
    ) == "# Metadata\n"
    assert not (staged / "data" / "README.md").exists()
    assert not (staged / "OLD.md").exists()


def test_stage_project_includes_per_project_memories(
    tmp_path: Path, monkeypatch
) -> None:
    project = tmp_path / "projects" / "demo"
    staging_dir = tmp_path / "knowledge" / "staging"
    write(project / "README.md", "# Demo\n")
    write(project / "memories" / "pitfalls.md", "# Pitfalls\n")
    write(project / "memories" / "discoveries.md", "# Discoveries\n")

    monkeypatch.setattr(
        staging,
        "select_project_files",
        lambda project_dir: [project_dir / "README.md"],
    )
    monkeypatch.setattr(
        staging,
        "build_project_metadata",
        lambda project_dir: SimpleNamespace(markdown="# Metadata\n"),
    )

    staged = staging.stage_project(project, staging_dir)

    assert (staged / "memories" / "pitfalls.md").read_text(
        encoding="utf-8"
    ) == "# Pitfalls\n"
    assert (staged / "memories" / "discoveries.md").is_file()


def test_stage_project_renders_claims_and_copies_refutations_but_not_runtime(
    tmp_path: Path,
) -> None:
    project = tmp_path / "projects" / "demo"
    staging_dir = tmp_path / "knowledge" / "staging"
    write(project / "README.md", "# Demo\n")
    write(project / "REPORT.md", "# Report\n")
    write(project / "REFUTATION_1.md", "# Refutation\n- **Verdict**: undermined\n")
    write(
        project / "runtime.json",
        '{"sessions": [{"agent": {"model_id": "secret-model"}}]}\n',
    )
    write(
        project / "claims.json",
        """{
  "schema_version": "2.0",
  "project": "demo",
  "report_hash": "sha256:abc",
  "claims": [
    {
      "claim_id": "claim-a",
      "claim": "Claim A",
      "author_assertions": {"status": "supported", "confidence": "high", "source": "REPORT.md"},
      "computed": {"resolved_artifact_support": "single-stream", "confidence_mismatch": true},
      "supports": [{"kind": "notebook", "locator": "notebooks/a.ipynb", "exact": "result", "resolution": {"status": "resolved"}}],
      "refutes": [{"kind": "paper", "locator": "PMID:1", "exact": "opposes", "resolution": {"status": "not-checked"}}]
    }
  ]
}
""",
    )

    staged = staging.stage_project(project, staging_dir)
    claims = (staged / "CLAIMS_CONTEXT.md").read_text()
    assert "Author-asserted status: supported" in claims
    assert "Supporting evidence" in claims and "Contradicting evidence" in claims
    assert "resolved artifact support: single-stream" in claims
    assert "Verdict**: undermined" in (staged / "REFUTATION_1.md").read_text()
    assert not (staged / "runtime.json").exists()
    assert not (staged / "claims.json").exists()
    assert "secret-model" not in "\n".join(
        path.read_text() for path in staged.rglob("*") if path.is_file()
    )


def test_manifest_tracks_claims_and_refutations_but_not_runtime(tmp_path: Path) -> None:
    project = tmp_path / "projects" / "demo"
    write(project / "README.md", "# Demo\n")
    write(project / "claims.json", "{}\n")
    write(project / "REFUTATION_1.md", "# R1\n")
    write(project / "runtime.json", "{}\n")
    target = "viking://resources/beril/projects/demo/"
    old = build_manifest({target: select_project_context_sources(project)}, tmp_path)
    assert any(path.endswith("claims.json") for path in old[target])
    assert any(path.endswith("REFUTATION_1.md") for path in old[target])
    assert not any(path.endswith("runtime.json") for path in old[target])

    write(project / "claims.json", '{"changed": true}\n')
    new = build_manifest({target: select_project_context_sources(project)}, tmp_path)
    assert changed_targets(old, new) == [target]
