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
    # beril_cli and the hook are symlinked in too, so the hook resolves *this*
    # tree as its repo root (it derives it from its own path) and can never
    # write into the real projects/ directory.
    (tmp_path / "beril_cli").symlink_to(ROOT / "beril_cli")
    # audit_cmd._find_repo_root walks up from cwd looking for this marker;
    # without it the snapshot silently declines to resolve any project.
    (tmp_path / "PROJECT.md").write_text("# throwaway\n")
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude" / "hooks" / "beril-runtime.sh").symlink_to(
        ROOT / ".claude" / "hooks" / "beril-runtime.sh"
    )
    (tmp_path / ".claude" / "hooks" / "dash_stop.py").symlink_to(
        ROOT / ".claude" / "hooks" / "dash_stop.py"
    )
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


# --------------------------------------------------------------------------
# Binding a mid-session project — the PostToolUse hook
# --------------------------------------------------------------------------

def _hook(repo: Path, payload: dict, session_id: str) -> subprocess.CompletedProcess:
    """Run the hook the way Claude Code does, but from inside the throwaway repo.

    Invoked through the symlink in `repo/.claude/hooks/`, because the hook
    derives its root from its own resolved path — running the one in the real
    repo would make every assertion here about the real projects/ tree.
    """
    import os

    env = {**os.environ, "CLAUDE_CODE_SESSION_ID": session_id}
    return subprocess.run(
        ["bash", str(repo / ".claude" / "hooks" / "beril-runtime.sh")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(repo),
        env=env,
        timeout=60,
    )


def test_a_tool_write_binds_the_session_to_the_project_it_touched(tmp_path):
    """The gap this closes: a project created *during* a session was never bound.

    None of the other signals can fire — Claude Code was launched before the
    directory existed, `/berdl_start` only *offers* to create the branch, and the
    SessionStart snapshot ran before Phase 0 scaffolded anything. The first write
    into the project is the earliest moment the binding is knowable.
    """
    repo = _repo(tmp_path, {"newproj": None})   # no runtime.json yet
    sid = "sess-posttooluse"

    done = _hook(repo, {
        "session_id": sid,
        "hook_event_name": "PostToolUse",
        "cwd": str(repo),
        "tool_name": "Write",
        "tool_input": {"file_path": str(repo / "projects" / "newproj" / "beril.yaml")},
    }, sid)
    assert done.returncode == 0, done.stderr          # never blocks a tool call

    # Gotcha 1: a guard that reads stdin would eat the payload and this file
    # would never be written.
    recorded = json.loads((repo / "projects" / "newproj" / "runtime.json").read_text())
    assert any(s.get("session_id") == sid for s in recorded["sessions"])

    # ...and the status line now names it, having had no other signal.
    assert "newproj" in _render(repo, session_id=sid)


def test_the_guard_does_not_skip_a_non_tool_payload(tmp_path):
    """Gotcha 2. A SessionStart payload for a session on branch `projects/<id>`
    sitting at the repo root contains no `projects/` string at all — the branch is
    read by shelling out to git. A blanket "skip unless the payload mentions
    projects/" would silently break the path that works today."""
    repo = _repo(tmp_path, {"branchproj": None})
    subprocess.run(["git", "checkout", "-q", "-b", "projects/branchproj"],
                   cwd=repo, check=True)
    sid = "sess-sessionstart"

    done = _hook(repo, {"session_id": sid, "hook_event_name": "SessionStart",
                        "cwd": str(repo), "source": "startup"}, sid)
    assert done.returncode == 0, done.stderr
    assert (repo / "projects" / "branchproj" / "runtime.json").is_file(), (
        "the guard skipped a SessionStart payload whose only project signal is the "
        "git branch, which is never in the payload"
    )


def test_a_write_outside_any_project_records_nothing(tmp_path):
    """The guard's whole purpose: most writes are not into a project, and paying
    ~70ms for each would be the cost that made the hook not worth registering."""
    repo = _repo(tmp_path, {"untouched": None})
    done = _hook(repo, {
        "session_id": "sess-elsewhere",
        "hook_event_name": "PostToolUse",
        "cwd": str(repo),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(repo / "tools" / "dashboard.py")},
    }, "sess-elsewhere")
    assert done.returncode == 0, done.stderr
    assert not (repo / "projects" / "untouched" / "runtime.json").exists()


def test_the_statusline_starts_a_dashboard_that_is_not_running(tmp_path):
    """The launcher moved here because skill prose never fired during
    exploration: the earliest copy sat in `/berdl_start` Phase C, after the plan
    is written *and* approved.

    Bounded on purpose — it fires only when a project resolved and the port is
    closed, so the steady state is one socket check and nothing else.
    """
    import socket
    import time

    repo = _repo(tmp_path, {"spawnme": ["sess-spawn"]})
    port = 8700 + __import__("zlib").crc32(b"spawnme") % 100

    probe = socket.socket(); probe.settimeout(0.2)
    assert probe.connect_ex(("127.0.0.1", port)) != 0, f"port {port} already in use"
    probe.close()

    first = _render(repo, session_id="sess-spawn")
    assert "dashboard not running" in first          # nothing to advertise yet

    try:
        for _ in range(40):                          # give it a moment to bind
            time.sleep(0.25)
            probe = socket.socket(); probe.settimeout(0.2)
            up = probe.connect_ex(("127.0.0.1", port)) == 0
            probe.close()
            if up:
                break
        assert up, "the statusline did not start a dashboard"
        assert f":{port}/" in _render(repo, session_id="sess-spawn")
    finally:
        subprocess.run(["pkill", "-f", f"dashboard.py {repo}/projects/spawnme"],
                       capture_output=True)


def test_it_does_not_spawn_when_no_project_resolves(tmp_path):
    """A display component with a side effect has to stay bounded: no project,
    no process."""
    repo = _repo(tmp_path, {"unbound": None})
    before = subprocess.run(["pgrep", "-fc", "tools/dashboard.py"],
                            capture_output=True, text=True).stdout.strip() or "0"
    assert "unbound" not in _render(repo, session_id="no-such-session")
    after = subprocess.run(["pgrep", "-fc", "tools/dashboard.py"],
                           capture_output=True, text=True).stdout.strip() or "0"
    assert before == after, "spawned a dashboard with no project resolved"


# --------------------------------------------------------------------------
# Stopping it — the SessionEnd hook
# --------------------------------------------------------------------------

def _stop(repo: Path, payload: dict, session_id: str) -> subprocess.CompletedProcess:
    import os

    return subprocess.run(
        ["python3", str(repo / ".claude" / "hooks" / "dash_stop.py")],
        input=json.dumps(payload), capture_output=True, text=True,
        cwd=str(repo), env={**os.environ, "CLAUDE_CODE_SESSION_ID": session_id},
        timeout=60,
    )


def _spawn_dashboard(repo: Path, pid: str):
    import subprocess as sp
    import sys as s

    return sp.Popen(
        [s.executable, str(ROOT / "tools" / "dashboard.py"), str(repo / "projects" / pid)],
        stdout=sp.DEVNULL, stderr=sp.DEVNULL, start_new_session=True,
    )


def test_session_end_stops_the_dashboard_for_its_project(tmp_path):
    """The counterpart to the status line starting it. Without this the server is
    detached, so it outlives Claude Code and nothing ever stops it."""
    repo = _repo(tmp_path, {"stopme": ["sess-stop"]})
    proc = _spawn_dashboard(repo, "stopme")
    try:
        import time
        time.sleep(2)
        assert proc.poll() is None, "dashboard did not start"

        done = _stop(repo, {"session_id": "sess-stop", "hook_event_name": "SessionEnd",
                            "cwd": str(repo), "reason": "other"}, "sess-stop")
        assert done.returncode == 0, done.stderr      # must never block the exit
        assert proc.wait(timeout=15) is not None
    finally:
        if proc.poll() is None:
            proc.kill()


def test_a_mode_toggle_does_not_stop_the_dashboard(tmp_path):
    """SessionEnd fires for things that end nothing. `bypass_permissions_disabled`
    is a mode toggle — same session, same project — so killing there is pure
    churn. Every other reason, `clear` included, ends the session: /clear starts
    a fresh one that may be a different project, so the old dashboard should go."""
    repo = _repo(tmp_path, {"keepme": ["sess-clear"]})
    proc = _spawn_dashboard(repo, "keepme")
    try:
        import time
        time.sleep(2)
        for reason in ("bypass_permissions_disabled",):
            done = _stop(repo, {"session_id": "sess-clear", "reason": reason,
                                "hook_event_name": "SessionEnd", "cwd": str(repo)},
                         "sess-clear")
            assert done.returncode == 0
        time.sleep(1)
        assert proc.poll() is None, "the dashboard was killed on a non-exit reason"
    finally:
        proc.kill()
