"""Tests for the plan witness: it never blocks, it records what it saw.

Two invariants, everywhere: the hook exits 0 no matter what it is handed — the
`_run` helper asserts that on every call, so the never-blocks rule is pinned by
every test below — and a `plan_deviations.jsonl` record appears exactly when
analysis code is written under a plan carrying no matching human approval.

This file owns the end-to-end digest behaviour (an approval survives a Revision
History append and dies on any other edit), because the witness is what acts on
it. `tests/test_approve.py` does not restate the rule; `test_digest_twins_agree`
holds the CLI's copy to the hook's output.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import pytest

from beril_cli import approve_cmd

HOOK = Path(__file__).parents[1] / ".claude" / "hooks" / "plan-gate.py"

PLAN = "# Plan\n\n## Hypotheses\n\nH1 beats H0 when the effect clears p < 0.01.\n"
APPROVED = hashlib.sha256(PLAN.encode()).hexdigest()
REVISION = "## Revision History  \n\n- **v1** (2026-07-28): renamed an output CSV.\n"
AUTHORS = "\n## Authors\n\n0009-0000-0000-0000\n"

APPROVAL = 'plan_approval:\n  by: "0009-0000-0000-0000"\n  plan_hash: "sha256:%s"\n'
NOTEBOOK = "projects/demo/notebooks/01_analysis.ipynb"


def _digest(plan_text: str) -> str:
    """The digest rule restated independently, so these tests pin it rather than
    echo whichever implementation happens to be in the source: sha256 of the plan
    with only the ``## Revision History`` SECTION removed, up to the next ``##``.
    """
    match = re.search(r"^##[ \t]+Revision History[ \t]*$", plan_text, re.MULTILINE)
    if match is None:
        return hashlib.sha256(plan_text.encode()).hexdigest()
    tail = plan_text[match.end() :]
    following = re.search(r"^##[ \t]", tail, re.MULTILINE)
    body = plan_text[: match.start()] + (tail[following.start() :] if following else "")
    return hashlib.sha256(body.encode()).hexdigest()


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "projects" / "demo").mkdir(parents=True)
    return tmp_path


def _write(repo: Path, name: str, text: str, project: str = "demo") -> None:
    (repo / "projects" / project / name).write_text(text)


def _run(
    repo: Path,
    tool_input: dict,
    *,
    tool_name: str = "Write",
    **env_extra: str,
) -> subprocess.CompletedProcess:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    env.pop("BERIL_PLAN_GATE", None)
    env.update(env_extra)
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(
            {"tool_name": tool_name, "cwd": str(repo), "tool_input": tool_input}
        ),
        env=env,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr  # a witness never blocks
    return result


def _records(repo: Path, project: str = "demo") -> list:
    """Parsed contents of a project's ``plan_deviations.jsonl`` (empty when absent)."""
    log = repo / "projects" / project / "plan_deviations.jsonl"
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text().splitlines()]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", message)


def test_exploration_before_a_plan_is_not_recorded(repo: Path):
    _run(repo, {"file_path": "projects/demo/notebooks/00_explore.ipynb"})
    assert _records(repo) == []


@pytest.mark.parametrize(
    "key,path,expected",
    [
        # analysis code inside a planned project, through each path argument the
        # harness and the MCP servers actually use
        (
            "file_path",
            "projects/demo/nb/deep/01.ipynb",
            "projects/demo/nb/deep/01.ipynb",
        ),
        ("notebook_path", "projects/demo/quick.ipynb", "projects/demo/quick.ipynb"),
        (
            "relative_path",
            "projects/demo/src/pipeline.py",
            "projects/demo/src/pipeline.py",
        ),
        (
            "path",
            "{repo}/projects/demo/scripts/run.py",
            "{repo}/projects/demo/scripts/run.py",
        ),
        # not analysis code
        ("file_path", "projects/demo/README.md", None),
        # merely CONTAINS projects/<id>/ — belongs to no project in this
        # checkout. Inside the checkout but outside projects/, and another
        # checkout's absolute path, resolve to "not ours" by different routes:
        # the first through the anchored match, the second through relpath
        # against this root.
        ("relative_path", "scratch/projects/demo/nb/01.ipynb", None),
        ("file_path", "{parent}/elsewhere/projects/demo/nb/01.ipynb", None),
        # unnormalized: the harness canonicalizes file_path, not MCP arguments.
        # `..` rather than `.` because it is the one that misattributes to a
        # real neighbouring project rather than to a project named ".".
        (
            "relative_path",
            "projects/other/../demo/nb/01.ipynb",
            "projects/demo/nb/01.ipynb",
        ),
    ],
    ids=[
        "nested-nb",
        "notebook-edit",
        "mcp-relative-py",
        "absolute-inside",
        "prose",
        "scratch-lookalike",
        "other-checkout",
        "parent-segment",
    ],
)
def test_records_exactly_the_analysis_writes_in_this_checkout(
    repo: Path, key: str, path: str, expected: str | None
):
    """Attribution is by position inside *this* checkout, after normalization."""
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    native = key in ("file_path", "notebook_path")
    _run(
        repo,
        {key: path.format(repo=repo, parent=repo.parent)},
        tool_name="Write" if native else "mcp__filesystem__write_file",
    )
    if expected is None:
        assert _records(repo) == []
        return
    (record,) = _records(repo)
    assert record["path"] == expected.format(repo=repo)
    assert record["plan_hash"] == APPROVED
    datetime.strptime(record["at"], "%Y-%m-%dT%H:%M:%SZ")  # ISO-8601 UTC, trailing Z


def test_read_only_mcp_tool_is_not_recorded(repo: Path):
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    _run(
        repo,
        {"relative_path": "projects/demo/src/pipeline.py"},
        tool_name="mcp__filesystem__read_file",
    )
    assert _records(repo) == []


@pytest.mark.parametrize(
    "tool_name",
    [
        # The other two names .claude/settings.json registers (Write and the MCP
        # writer are pinned by the path table above). Without these, dropping
        # "edit" from MUTATING left the whole suite green while two write paths
        # silently vanished from the audit trail.
        "Edit",
        "NotebookEdit",
    ],
)
def test_mutating_tools_are_recorded(repo: Path, tool_name: str):
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    _run(repo, {"relative_path": "projects/demo/src/pipeline.py"}, tool_name=tool_name)
    assert len(_records(repo)) == 1


def test_concurrent_writes_all_land(repo: Path):
    """Append-only: parallel tool calls must not lose each other's records.

    The hook is stdlib-only under 3.9 with no lock available, so a
    read-modify-rewrite of the log would drop records under exactly the
    interleaving the harness produces when several writes are in flight.
    """
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    # A long-running project's log, so a read-modify-write costs real time and
    # the records lost to the race are not a matter of luck. Appending is O(1)
    # in this and does not care.
    seeded = [{"at": "2026-01-01T00:00:00Z", "path": "old.py", "plan_hash": APPROVED}]
    (repo / "projects" / "demo" / "plan_deviations.jsonl").write_text(
        "".join(json.dumps(seeded[0]) + "\n" for _ in range(20000))
    )
    paths = [f"projects/demo/notebooks/{index:02d}.py" for index in range(16)]

    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(lambda path: _run(repo, {"file_path": path}), paths))

    written = [r["path"] for r in _records(repo)]
    assert sorted(p for p in written if p != "old.py") == paths
    assert written.count("old.py") == 20000


def test_status_active_alone_is_not_approval(repo: Path):
    """The whole point: the agent writes `status`, so `status` proves nothing."""
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    _write(repo, "beril.yaml", "project_id: demo\nstatus: active\n")
    _run(repo, {"file_path": NOTEBOOK})
    assert len(_records(repo)) == 1


@pytest.mark.parametrize(
    "manifest",
    [
        'project_id: demo\nartifacts:\n  research_plan: true\n  plan_hash: "sha256:%s"\n',
        'plan_approval:\n  metadata:\n    plan_hash: "sha256:%s"\n',
    ],
    ids=["under-artifacts", "nested-in-plan_approval"],
)
def test_only_a_direct_plan_approval_child_counts(repo: Path, manifest: str):
    """A matching `plan_hash` under some other key is not an approval."""
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    _write(repo, "beril.yaml", manifest % APPROVED)
    _run(repo, {"file_path": NOTEBOOK})
    assert len(_records(repo)) == 1


def test_only_the_revision_history_section_is_excised(repo: Path):
    """One approval, three edits: the minor append survives, material edits do not.

    Plans in this repo routinely carry `## Authors` and whole pivot sections
    BELOW the Revision History heading, so excising the tail rather than the
    section would let a rewritten hypothesis keep an old approval valid.
    """
    plan = PLAN + REVISION + AUTHORS
    _write(repo, "RESEARCH_PLAN.md", plan)
    _write(repo, "beril.yaml", "status: proposed\n" + APPROVAL % _digest(plan))
    _run(repo, {"file_path": NOTEBOOK})
    assert _records(repo) == [], "an untouched approved plan records nothing"

    minor = plan.replace("- **v1**", "- **v2** (2026-07-29): renamed a CSV.\n- **v1**")
    _write(repo, "RESEARCH_PLAN.md", minor)
    _run(repo, {"file_path": NOTEBOOK})
    assert _records(repo) == [], "a Revision History append is not a deviation"

    pivot = minor + "\n## REVISION: Pivot\n\n### Revised Hypotheses\n\nH1'\n"
    _write(repo, "RESEARCH_PLAN.md", pivot)
    _run(repo, {"file_path": NOTEBOOK})
    assert [r["plan_hash"] for r in _records(repo)] == [_digest(pivot)]

    above = pivot.replace("p < 0.01", "p < 0.05")
    _write(repo, "RESEARCH_PLAN.md", above)
    _run(repo, {"file_path": "projects/demo/notebooks/02_more.py"})
    # appended, not overwritten, and each record carries the digest as it stood
    assert [r["plan_hash"] for r in _records(repo)] == [_digest(pivot), _digest(above)]


def test_only_a_committed_report_ends_recording(repo: Path):
    """The write-up exemption keys on a REPORT.md in HEAD, not one on disk.

    A stub scaffolded this session — or merely `git add`-ed — would otherwise
    silence the witness permanently, and scaffolding a report before doing the
    work is ordinary agent behaviour.
    """
    _git(repo, "init", "-q", ".")
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    _commit(repo, "plan")

    _write(repo, "REPORT.md", "stub\n")  # exists, untracked
    _run(repo, {"file_path": NOTEBOOK})
    assert len(_records(repo)) == 1

    _git(repo, "add", "projects/demo/REPORT.md")
    _run(repo, {"file_path": NOTEBOOK})
    assert len(_records(repo)) == 2, "`git add` on a stub is not a write-up"

    _commit(repo, "report")
    _run(repo, {"file_path": NOTEBOOK})
    assert len(_records(repo)) == 2, "committed: exempt from here on"


def test_report_exemption_trusts_only_a_readable_git(repo: Path):
    """No work tree to ask: fall back to existence. A broken git: keep recording.

    128 is git's generic fatal code (dubious ownership, a broken index), so
    trusting it would let an unrelated breakage silence the witness for good.
    """
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    _write(repo, "REPORT.md", "# Findings\n")
    _run(repo, {"file_path": NOTEBOOK})
    assert _records(repo) == []

    bin_dir = repo / "bin"
    bin_dir.mkdir()
    fake_git = bin_dir / "git"
    fake_git.write_text(
        "#!/bin/sh\n"
        'echo "fatal: detected dubious ownership in repository" >&2\n'
        "exit 128\n"
    )
    fake_git.chmod(0o755)

    _run(
        repo,
        {"file_path": NOTEBOOK},
        PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
    )
    assert len(_records(repo)) == 1


def test_env_escape_hatch_suppresses_recording(repo: Path):
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    _run(repo, {"file_path": NOTEBOOK}, BERIL_PLAN_GATE="off")
    assert _records(repo) == []


# "" is unparseable, "[]" parses and is the wrong type — two different
# exceptions out of two different lines. A second unparseable string would be
# the same failure twice.
@pytest.mark.parametrize("payload", ["", "[]"])
def test_malformed_stdin_fails_open(repo: Path, payload: str):
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=str(repo)),
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    # Fails open without advertising the escape hatch: this stderr goes to the
    # model, and the path is agent-triggerable (an unreadable plan raises here).
    assert "BERIL_PLAN_GATE" not in result.stderr


def test_unreadable_plan_fails_open(repo: Path):
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    plan = repo / "projects" / "demo" / "RESEARCH_PLAN.md"
    plan.chmod(0o000)
    try:
        result = _run(repo, {"file_path": NOTEBOOK})
    finally:
        plan.chmod(0o644)
    assert "plan witness error" in result.stderr
    assert "BERIL_PLAN_GATE" not in result.stderr
    assert _records(repo) == []


@pytest.mark.parametrize(
    "text",
    [
        PLAN,
        PLAN + REVISION,
        PLAN + REVISION + AUTHORS,
        (PLAN + REVISION + AUTHORS).replace("\n", "\r\n"),
    ],
    ids=["no-heading", "with-heading", "section-below-heading", "crlf"],
)
def test_digest_twins_agree(tmp_path: Path, text: str):
    """The hook's copy of `plan_digest` and the CLI's must agree byte for byte.

    Nothing else cross-checks them: a drift means `beril approve` records a hash
    the hook can never match, and an approved plan logs deviations forever. CRLF
    is in here because the two used to disagree on it; the section below the
    heading because a twin that truncates the tail agrees on every plan without
    one.
    """
    spec = importlib.util.spec_from_file_location("plan_gate", HOOK)
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    plan = tmp_path / "RESEARCH_PLAN.md"
    plan.write_bytes(text.encode())
    assert hook.plan_digest(str(plan)) == approve_cmd.plan_digest(text.encode())


@pytest.mark.skipif(
    not os.path.exists("/usr/bin/python3"), reason="no system interpreter"
)
def test_hook_runs_under_the_system_interpreter(repo: Path):
    """The harness runs the hook outside the venv, so it must work on stock python."""
    _write(repo, "RESEARCH_PLAN.md", PLAN)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    env.pop("BERIL_PLAN_GATE", None)
    result = subprocess.run(
        ["/usr/bin/python3", str(HOOK)],
        input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": NOTEBOOK}}),
        env=env,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert len(_records(repo)) == 1
