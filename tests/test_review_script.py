"""Focused tests for review subject hashes and TOCTOU protection."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "tools" / "review.sh"


@pytest.fixture()
def review_repo(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "projects" / "demo"
    project.mkdir(parents=True)
    (project / "REPORT.md").write_text("# Stable report\n")
    (project / "RESEARCH_PLAN.md").write_text("# Stable plan\n")
    (project / "README.md").write_text("# Demo\n")
    prompts = tmp_path / ".claude" / "reviewer"
    prompts.mkdir(parents=True)
    for name in ("SYSTEM_PROMPT.md", "REFUTATION_PROMPT.md", "PLAN_REVIEW_PROMPT.md"):
        (prompts / name).write_text("Write the requested review.\n")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "claude"
    fake.write_text(
        "#!/bin/sh\n"
        "{\n"
        "  printf '%s\\n' '---' 'reviewer: fake' '---' '# Review'\n"
        "  printf '%s\\n' '<!-- report_hash: sha256:0000000000000000000000000000000000000000000000000000000000000000 -->'\n"
        "  printf '%s\\n' '<!-- plan_hash: sha256:0000000000000000000000000000000000000000000000000000000000000000 -->'\n"
        '} > "$FAKE_OUTPUT"\n'
        'if [ -n "${FAKE_MUTATE_SUBJECT:-}" ]; then\n'
        "  printf '%s\\n' 'changed during review' >> \"$FAKE_MUTATE_SUBJECT\"\n"
        "fi\n"
    )
    fake.chmod(0o755)
    return tmp_path, bin_dir


def _run(review_repo, review_type: str, *, mutate: bool = False):
    root, bin_dir = review_repo
    output = root / "projects" / "demo" / f"{review_type}.md"
    subject = (
        root
        / "projects"
        / "demo"
        / ("RESEARCH_PLAN.md" if review_type == "plan" else "REPORT.md")
    )
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "BERIL_REPO_ROOT": str(root),
        "FAKE_OUTPUT": str(output),
    }
    if mutate:
        env["FAKE_MUTATE_SUBJECT"] = str(subject)
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "demo",
            "--type",
            review_type,
            "--reviewer",
            "claude",
            "--output",
            str(output),
        ],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )
    return result, output, subject


@pytest.mark.parametrize(
    ("review_type", "hash_key"),
    [("project", "report_hash"), ("refute", "report_hash"), ("plan", "plan_hash")],
)
def test_each_review_artifact_has_one_canonical_subject_hash(
    review_repo, review_type, hash_key
):
    result, output, subject = _run(review_repo, review_type)
    assert result.returncode == 0, result.stderr
    digest = hashlib.sha256(subject.read_bytes()).hexdigest()
    canonical = f"<!-- {hash_key}: sha256:{digest} -->"
    text = output.read_text()
    assert text.rstrip().endswith(canonical)
    assert text.count(f"<!-- {hash_key}:") == 1
    assert (
        "0000000000000000000000000000000000000000000000000000000000000000" not in text
    )


@pytest.mark.parametrize("review_type", ["project", "refute", "plan"])
def test_subject_change_during_review_discards_output(review_repo, review_type):
    result, output, _ = _run(review_repo, review_type, mutate=True)
    assert result.returncode == 1
    assert "changed during" in result.stderr
    assert not output.exists()
