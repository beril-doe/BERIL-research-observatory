"""Tests for the agent-state hook: is the agent blocked on a human right now?

The payloads below are **verbatim captures**, not invented shapes. Claude Code
2.1.220 documents the `Notification` matcher types and no payload schema at all,
so the fields here came from registering a logging hook and driving a real
session through a pty. Two of those findings are load-bearing and are what the
first two tests exist to pin:

- `Notification/permission_prompt` carries the fixed string "Claude needs your
  permission" — no tool name, no argument. On its own it cannot say what the
  agent wants.
- `PermissionRequest` fires ~6s *earlier*, carries `tool_name` and the whole
  `tool_input`, and stays silent for a call the permission rules auto-allow. It
  is both the faster signal and the only specific one.

As in `test_plan_gate.py`, `_run` asserts exit 0 on every call, so the
never-block rule is pinned by every test in the file rather than by one of them.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / ".claude" / "hooks" / "agent_state.py"
SESSION = "sess-1"

# Captured from a real prompt for `Bash(sw_vers)` in `--permission-mode default`.
PERMISSION = {
    "session_id": SESSION,
    "cwd": "/repo",
    "prompt_id": "p1",
    "permission_mode": "default",
    "hook_event_name": "PermissionRequest",
    "tool_name": "Bash",
    "tool_input": {"command": "sw_vers", "description": "Show macOS version info"},
}
# The same session ~6s later. This is the entire payload; there is no more of it.
NOTIFICATION = {
    "session_id": SESSION,
    "cwd": "/repo",
    "prompt_id": "p1",
    "hook_event_name": "Notification",
    "message": "Claude needs your permission",
    "notification_type": "permission_prompt",
}
# AskUserQuestion goes through the permission system too — the agent asking a
# question outright is a permission prompt, not `agent_needs_input`. Its text is
# nested two levels down, which is why the detail search is recursive.
ASK = {
    "session_id": SESSION,
    "cwd": "/repo",
    "hook_event_name": "PermissionRequest",
    "tool_name": "AskUserQuestion",
    "tool_input": {
        "questions": [
            {
                "question": "Do you prefer tabs or spaces for indentation?",
                "header": "Indentation",
                "options": [{"label": "Spaces", "description": "Use spaces"}],
            }
        ]
    },
}
STOP = {
    "session_id": SESSION,
    "cwd": "/repo",
    "hook_event_name": "Stop",
    "stop_hook_active": False,
    "last_assistant_message": "Done — the suite is green at 429 tests.",
}
PROMPT = {
    "session_id": SESSION,
    "cwd": "/repo",
    "hook_event_name": "UserPromptSubmit",
    "prompt": "carry on",
}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A clone-shaped tree the hook resolves as its own root.

    The hook derives the repo root from its own path, so symlinking it in is
    what keeps a test from writing into the real `projects/` directory.
    """
    subprocess.run(["git", "init", "-q", "."], cwd=tmp_path, check=True)
    (tmp_path / "PROJECT.md").write_text("# throwaway\n")
    (tmp_path / "beril_cli").symlink_to(ROOT / "beril_cli")
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude" / "hooks" / "agent_state.py").symlink_to(HOOK)
    project = tmp_path / "projects" / "demo"
    project.mkdir(parents=True)
    (project / "runtime.json").write_text(
        json.dumps({"project": "demo", "sessions": [{"session_id": SESSION}]})
    )
    return tmp_path


def _run(repo: Path, payload) -> "dict | None":
    """Fire the hook, assert it exited clean, return the state file or None."""
    done = subprocess.run(
        ["python3", str(repo / ".claude" / "hooks" / "agent_state.py")],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(repo),
        timeout=60,
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout == "", "a UserPromptSubmit hook's stdout lands in the context"
    state = repo / "projects" / "demo" / ".agent-state.json"
    return json.loads(state.read_text()) if state.exists() else None


def test_it_records_what_the_agent_is_blocked_on(repo):
    """A chip that says only "waiting" makes the reader switch tabs to find out
    what for, which is the tab switch this whole feature exists to avoid.

    Both shapes have to work, and the nested one is the case that matters most:
    `AskUserQuestion` — the agent asking a question outright — buries its text
    under `questions[0].question`, so a flat `tool_input.get("command")` lookup
    would render the useful case as a bare tool name.
    """
    state = _run(repo, PERMISSION)
    assert state["state"] == "waiting"
    assert state["detail"] == "Bash: sw_vers"
    assert state["session_id"] == SESSION, "no session id — the renderer cannot expire it"
    assert state["since"] == pytest.approx(time.time(), abs=30)

    _run(repo, PROMPT)
    assert _run(repo, ASK)["detail"] == (
        "AskUserQuestion: Do you prefer tabs or spaces for indentation?"
    )


def test_the_generic_notification_never_displaces_the_specific_one(repo):
    """Both events fire for one prompt, and the *later* one knows less.

    `Notification` arrives ~6s after `PermissionRequest` with a constant string
    and no tool. Letting it write would replace "Bash: sw_vers" with nothing and
    reset `since` — and `since` is the key the browser debounces on, so the
    reader would be notified twice about a single prompt.
    """
    first = _run(repo, PERMISSION)
    second = _run(repo, NOTIFICATION)

    assert second == first, "the vaguer, later event overwrote the specific one"
    assert "Claude needs your permission" not in json.dumps(second)


def test_a_notification_that_does_carry_detail_is_kept(repo):
    """The reason `Notification` stays registered at all. `agent_needs_input`
    formats "<label> needs your input: <what>", which is real text that no
    `PermissionRequest` precedes — dropping every notification message on the
    grounds that two of them are boilerplate would lose it."""
    state = _run(
        repo,
        {**NOTIFICATION, "notification_type": "agent_needs_input",
         "message": "fix-flaky-tests needs your input: which suite?"},
    )

    assert state["state"] == "waiting"
    assert state["detail"] == "fix-flaky-tests needs your input: which suite?"


POST_TOOL = {
    "session_id": SESSION,
    "cwd": "/repo",
    "hook_event_name": "PostToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "sw_vers"},
    "tool_response": {"stdout": "ProductName: macOS"},
}


def test_an_answered_prompt_clears_before_the_turn_ends(repo):
    """REGRESSION, reported from a real BERDL session: approving a `Skill` left
    "The agent is waiting for you" on screen while the agent worked.

    Claude Code emits no "the prompt was answered" event — logging every hook
    across an approved prompt shows `PreToolUse` firing *before*
    `PermissionRequest`, so it cannot mean granted. `PostToolUse` is the first
    thing that happens only because a human said yes.

    Without it the strip survives until `Stop`, which is the end of the whole
    turn — minutes, for anything that does real work after approval. A banner
    that is wrong for minutes is worse than no banner: it teaches the reader to
    ignore it.
    """
    _run(repo, PERMISSION)

    assert _run(repo, POST_TOOL) is None, "still blocking on a prompt already answered"


def test_clearing_an_answered_prompt_needs_no_project(repo):
    """It runs after *every* tool call, so it must not pay for the git
    subprocess and the `beril_cli` import that resolution costs.

    The state file records which session wrote it, and that is the whole
    question — which also keeps it session-scoped, so two sessions in one clone
    cannot clear each other's. Deleting `runtime.json` removes the only signal
    resolution has here: if this still clears, no resolution happened.
    """
    _run(repo, PERMISSION)

    # Another session's prompt is not this session's to clear.
    assert _run(repo, {**POST_TOOL, "session_id": "someone-else"}) is not None

    # Now remove the only signal resolution has here. If it still clears, the
    # fast path really did skip resolving.
    (repo / "projects" / "demo" / "runtime.json").unlink()
    assert _run(repo, POST_TOOL) is None


def test_the_posttooluse_guard_still_lets_the_clear_through(repo):
    """Run the command string `settings.json` actually registers, not the hook.

    This one is on **every** tool call, so it is wrapped in the same kind of
    shell guard `beril-runtime.sh` uses: no state file, no interpreter — 6ms
    instead of 59, and the guard is nearly free here because a state file only
    exists mid-turn when a prompt is genuinely pending.

    A guard is also a new way to fail silently, in the direction nobody notices:
    skip too much and the strip goes back to surviving until `Stop`, with every
    unit test still green because they call the hook directly. So this drives
    the real string, both ways.
    """
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    command = next(
        hook["command"]
        for entry in settings["hooks"]["PostToolUse"]
        for hook in entry["hooks"]
        if "agent_state" in hook["command"]
    )

    def fire(payload) -> "dict | None":
        done = subprocess.run(
            command, shell=True, input=json.dumps(payload), capture_output=True,
            text=True, cwd=str(repo), timeout=60,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(repo)},
        )
        assert done.returncode == 0, done.stderr
        state = repo / "projects" / "demo" / ".agent-state.json"
        return json.loads(state.read_text()) if state.exists() else None

    # Guard closed: no state file, so it must consume stdin and exit clean.
    assert fire(POST_TOOL) is None

    # Guard open: a real pending prompt has to reach the hook and be cleared.
    _run(repo, PERMISSION)
    assert fire(POST_TOOL) is None, "the guard swallowed a prompt that needed clearing"


def test_a_tool_call_does_not_retire_a_finished_turn(repo):
    """`turn_ended` describes the past; only the next `UserPromptSubmit` retires
    it. Clearing on any tool call would erase the closing line the moment a new
    turn touched anything."""
    _run(repo, STOP)

    assert _run(repo, POST_TOOL)["state"] == "turn_ended"


def test_the_human_coming_back_clears_it(repo):
    """`Stop` is the end of a turn, not a block: the page should say the turn
    ended and show the closing line, not claim anyone is waiting. A prompt
    submitted is proof the human is at the keyboard, so the file goes."""
    _run(repo, PERMISSION)

    ended = _run(repo, STOP)
    assert ended["state"] == "turn_ended"
    assert ended["detail"] == "Done — the suite is green at 429 tests."

    assert _run(repo, PROMPT) is None, "still claiming a state after the human replied"


def test_an_unresolvable_or_malformed_event_writes_nothing(repo):
    """Never block, never guess. `_run` already asserts exit 0; what these add is
    that a hook which cannot tell whose project it is stays silent rather than
    picking one."""
    assert _run(repo, "not json{") is None
    assert _run(repo, {**PERMISSION, "session_id": "belongs-to-nobody"}) is None
    assert _run(repo, {**PERMISSION, "hook_event_name": "PreCompact"}) is None


def test_every_event_it_handles_is_actually_registered():
    """A hook nothing calls is a file that passes its own tests forever.

    The five names are not interchangeable and dropping any one breaks a
    different thing: without `PermissionRequest` the page can say *that* the
    agent is blocked but never on what; without `PostToolUse` an answered prompt
    stays on screen until the whole turn ends; without `Stop` the last state
    ever written is `waiting`, so a finished turn reads as a blocked one;
    without `UserPromptSubmit` nothing clears when the human replies.
    """
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    registered = {
        event
        for event, entries in settings["hooks"].items()
        for entry in entries
        for hook in entry["hooks"]
        if "agent_state.py" in hook["command"]
    }

    assert registered == {
        "PermissionRequest", "Notification", "Stop", "UserPromptSubmit", "PostToolUse",
    }


def test_a_clean_exit_takes_the_state_file_with_it(repo):
    """The honest half of "the agent is waiting". A session killed with a
    permission prompt open leaves `waiting` on disk with nobody left to answer
    it, so `SessionEnd` clears it — for every exit Claude Code gets to announce.
    The renderer expires the rest on age and session id."""
    (repo / ".claude" / "hooks" / "dash_stop.py").symlink_to(
        ROOT / ".claude" / "hooks" / "dash_stop.py"
    )
    _run(repo, PERMISSION)

    done = subprocess.run(
        ["python3", str(repo / ".claude" / "hooks" / "dash_stop.py")],
        input=json.dumps({"session_id": SESSION, "hook_event_name": "SessionEnd",
                          "cwd": str(repo), "reason": "other"}),
        capture_output=True, text=True, cwd=str(repo), timeout=60,
    )

    assert done.returncode == 0, done.stderr
    assert not (repo / "projects" / "demo" / ".agent-state.json").exists()


def test_the_state_file_is_replaced_never_truncated(repo, monkeypatch):
    """REGRESSION by inheritance — `_write_snapshot` shipped this bug once.

    The dashboard polls this directory every 4s and `scan()` stats every file in
    it, so a reader landing mid-write is the expected interleaving, not a rare
    one. `write_text` truncates first; the visible symptom would be the amber
    waiting strip flickering off and back on under a reader who is watching it
    precisely because they are blocked.

    Breaking `os.replace` proves the rename is what publishes the content: with
    it broken, the previous state must still be readable and whole.
    """
    spec = importlib.util.spec_from_file_location("agent_state", HOOK)
    module = importlib.util.module_from_spec(spec)
    sys.modules["agent_state"] = module
    spec.loader.exec_module(module)

    project = repo / "projects" / "demo"
    module.write_state(project, {"state": "waiting", "detail": "Bash: sw_vers"})
    before = (project / ".agent-state.json").read_text()

    monkeypatch.setattr(module.os, "replace", lambda *a: (_ for _ in ()).throw(OSError))
    with pytest.raises(OSError):
        module.write_state(project, {"state": "turn_ended", "detail": "x" * 400})

    assert (project / ".agent-state.json").read_text() == before
