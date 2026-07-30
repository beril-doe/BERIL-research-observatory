"""Tests for `.claude/statusline.sh` — the per-session BERIL status line.

Scoped the way tests/test_dashboard.py is: only what breaks *silently*. Layout is
not tested, because the status line is visible on every turn — if it renders
wrong you see it immediately.

Which **project** it picks is the opposite: a wrong answer looks exactly like a
right one. It has to stay correct when several Claude Code sessions share one
clone on different projects, which is why the two rejected designs (a repo-wide
`BERIL_PROJECT` in settings, and "whichever beril.yaml was touched last") are not
merely less tidy — they hand every session the same answer and flip under them as
each one writes.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUSLINE = ROOT / ".claude" / "statusline.sh"

ANSI = re.compile(r"\033\[[0-9;]*m")


def _repo(tmp_path: Path, projects: dict) -> Path:
    """A throwaway clone-shaped tree.

    `tools` is symlinked to the real one so the status line resolves stage and
    port through the same import it uses in the repo, rather than silently
    falling into its `except Exception` and testing nothing.
    """
    subprocess.run(["git", "init", "-q", "."], cwd=tmp_path, check=True)
    (tmp_path / "tools").symlink_to(ROOT / "tools")
    for pid, sessions in projects.items():
        pdir = tmp_path / "projects" / pid
        pdir.mkdir(parents=True)
        (pdir / "beril.yaml").write_text(f"project_id: {pid}\nstatus: reviewed\n")
        if sessions is not None:
            (pdir / "runtime.json").write_text(
                json.dumps(
                    {
                        "schema_version": "2.0",
                        "project": pid,
                        "sessions": [{"session_id": s} for s in sessions],
                    }
                )
            )
    return tmp_path


def _render(repo: Path, session_id: str = "no-such-session", cwd=None, added=()) -> str:
    payload = {
        "session_id": session_id,
        "workspace": {
            "current_dir": str(cwd or repo),
            "added_dirs": [str(a) for a in added],
        },
        "context_window": {"used_percentage": 20},
    }
    done = subprocess.run(
        ["bash", str(STATUSLINE)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(cwd or repo),
        timeout=30,
    )
    assert done.returncode == 0, done.stderr
    return ANSI.sub("", done.stdout)


def test_simultaneous_sessions_on_one_clone_resolve_to_their_own_project(tmp_path):
    """The requirement that rejected every shared-state design.

    Two sessions, two projects, one clone, no cwd or branch signal for either.
    Each must name *its* project — the mapping is keyed by session id, so there is
    no single value for them to disagree over.
    """
    repo = _repo(tmp_path, {"alpha": ["sid-a"], "beta": ["sid-b"]})

    first = _render(repo, session_id="sid-a")
    second = _render(repo, session_id="sid-b")

    assert "alpha" in first and "beta" not in first
    assert "beta" in second and "alpha" not in second


def test_no_signal_names_no_project(tmp_path):
    """A session with no cwd, branch, `/add-dir` or recorded provenance must name
    nothing at all.

    This is the guard against a guessing fallback being added later: "newest
    project" would make this pass a name, and the line would then assert a project
    the session is not working on — the exact dishonesty the dashboard itself is
    built to avoid.
    """
    repo = _repo(tmp_path, {"alpha": ["sid-a"], "beta": ["sid-b"]})

    out = _render(repo, session_id="belongs-to-no-project")

    assert "alpha" not in out and "beta" not in out
    assert len(out.strip().splitlines()) == 1


def test_added_dir_declares_the_project_with_no_cwd_or_provenance(tmp_path):
    """`/add-dir` is the override for a session that has no runtime.json entry yet
    — one editing `tools/` from the repo root, which is when neither cwd nor
    branch can fire. Per-session by construction, so it does not leak either."""
    repo = _repo(tmp_path, {"alpha": None, "beta": None})

    out = _render(repo, session_id="fresh", added=[repo / "projects" / "beta"])

    assert "beta" in out
    assert "alpha" not in out


def test_cwd_outranks_recorded_provenance(tmp_path):
    """Ordering is load-bearing: you can sit in projects/<a> while the session has
    provenance against <b>, and the directory you are actually in wins."""
    repo = _repo(tmp_path, {"alpha": ["sid-a"], "beta": []})

    out = _render(repo, session_id="sid-a", cwd=repo / "projects" / "beta")

    assert "beta" in out
    assert "alpha" not in out
