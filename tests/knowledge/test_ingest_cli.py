from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "knowledge" / "scripts" / "ingest_context.py"


def test_empty_project_is_rejected_not_silent_success():
    """`--project ""` must be rejected, not reported as a successful no-op.

    The validator runs before any server contact, so this needs no server.
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", ""],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "Ingest finished" not in combined
    assert "Project ID must be a simple directory name" in proc.stderr
    assert "Traceback" not in proc.stderr


def _load_script():
    import importlib.util

    spec = importlib.util.spec_from_file_location("ingest_context_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mirror_withdraws_approval_gated_memories_the_project_lacks(tmp_path):
    """`/submit` deletes these memories when the approved REPORT drops the
    section; the mirror follows with an explicit withdrawal for each one that
    is absent. One the project still carries is never withdrawn."""
    script = _load_script()
    staged = tmp_path / "staged"
    (staged / "memories").mkdir(parents=True)
    (staged / "memories" / "performance.md").write_text("fast", encoding="utf-8")
    (staged / "memories" / "pitfalls.md").write_text("careful", encoding="utf-8")

    assert script._withdrawn_memories(staged) == ["memories/discoveries.md"]


def test_mirror_withdraws_both_gated_memories_when_none_are_staged(tmp_path):
    script = _load_script()
    staged = tmp_path / "staged"
    staged.mkdir()

    assert script._withdrawn_memories(staged) == [
        "memories/discoveries.md", "memories/performance.md"
    ]


def test_remove_requires_json_mode():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", "x", "--remove", "a.md"],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert proc.returncode != 0
    assert "--remove can only be used with --json" in proc.stderr
