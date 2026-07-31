#!/usr/bin/env python3
"""Record whether the agent is blocked on a human, for the live dashboard.

Writes `projects/<id>/.agent-state.json`. One dashboard, one project, one file;
`tools/dashboard.py` reads it in `scan()` and renders a chip, a strip, a title
marker and a favicon dot from it. Nothing else consumes it.

Registered on four events, and **which four is a measured result, not the
documented shape**. The hook docs list a `Notification` matcher over
`permission_prompt | agent_needs_input | idle_prompt | agent_completed` and give
no payload schema, so this was derived by registering a logging hook against
Claude Code 2.1.220 and driving a real session through a pty:

- `PermissionRequest` fires ~2s after the blocking tool call and carries
  `tool_name` + the full `tool_input`. It does **not** fire for a call the
  permission rules auto-allow (verified by allowlisting `Bash(sw_vers:*)` and
  watching it go silent), so its presence alone means a human is being asked.
  It is the only event that carries what the agent is asking *for*.
- `Notification/permission_prompt` fires ~6s *later* and its message is the
  compile-time constant "Claude needs your permission" — no tool, no argument.
  It is kept because it is the only signal for the notification types that never
  reach `PermissionRequest`, and because `agent_needs_input` puts a real detail
  in its message. It never overwrites a detail `PermissionRequest` already
  recorded for the same prompt: generic text must not displace specific text.
- `Stop` carries `last_assistant_message`, which is the closing line the reader
  would otherwise have to switch tabs to see.
- `UserPromptSubmit` means the human is back at the keyboard, whatever the file
  said.

`agent_needs_input` and `agent_completed` never fired for the main session in
any probe: in the bundle they are emitted from the background-agent fleet
tracker, labelled per sub-agent. They cost nothing to keep listening for.

Best-effort, like every other hook here: it always exits 0 and it prints
nothing. A `UserPromptSubmit` hook's stdout is appended to the agent's context,
so a stray `print` here would feed the dashboard's plumbing back into the
conversation.
"""

import json
import os
import sys
import time
from pathlib import Path

STATE_FILE = ".agent-state.json"

# "leave the file exactly as it is", which None cannot mean — None clears it.
UNCHANGED = object()

# Long enough for a real `Bash` command line, short enough that the amber strip
# stays one line in the header. The renderer escapes it; it does not trim it.
MAX_DETAIL = 200

# The argument that identifies a tool call to a human, in falling order of
# usefulness. Searched at any depth because `AskUserQuestion` — the single most
# important case, the agent literally asking a question — nests its text under
# `questions[0].question` while `Bash` puts it flat in `command`.
#
# `skill` and `query` are here because a bare tool name is a poor answer for the
# two that ask most often: "Skill" alone says nothing, and an MCP search tool is
# only meaningful as what it is searching for.
DETAIL_KEYS = (
    "command", "question", "skill", "query",
    "file_path", "path", "url", "pattern", "prompt",
)

# Fixed strings Claude Code sends as a Notification `message`. They carry no
# information a `state` of `waiting` does not already carry, so they are dropped
# rather than shown — "waiting · Claude needs your permission" is two words for
# one fact. A message that is *not* on this list (`agent_needs_input` formats
# "<label> needs your input: <what>") is real detail and is kept.
GENERIC = {"Claude needs your permission", "Claude is waiting for your input"}

# absolute(), not resolve(): resolve() follows a symlinked copy of this hook back
# to wherever it really lives, which in a test tree is the wrong repo. Same
# reasoning as dash_stop.py, which is the other half of this file's lifecycle.
ROOT = Path(__file__).absolute().parent.parent.parent


def find_detail(value, keys=DETAIL_KEYS) -> "str | None":
    """The first non-empty string under any of `keys`, at any depth.

    Keys are tried in priority order at each level before descending, so a
    `command` two levels down still loses to a `question` at the top.
    """
    if isinstance(value, dict):
        for key in keys:
            found = value.get(key)
            if isinstance(found, str) and found.strip():
                return found.strip()
        for child in value.values():
            found = find_detail(child, keys)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_detail(child, keys)
            if found:
                return found
    return None


def read_state(project: Path) -> dict:
    try:
        current = json.loads((project / STATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return current if isinstance(current, dict) else {}


def write_state(project: Path, record: "dict | None") -> None:
    """Replace the state file, or remove it when `record` is None.

    Atomically, via a sibling and `os.replace`. The dashboard polls this
    directory every 4s and `scan()` walks every file in it, so a reader landing
    mid-write is the expected interleaving rather than a rare one — writing in
    place is a bug already fixed once in `_write_snapshot`, and it would surface
    here as a `waiting` banner flickering off and on.
    """
    target = project / STATE_FILE
    if record is None:
        try:
            target.unlink()
        except OSError:
            pass
        return
    staging = target.with_name(STATE_FILE + ".tmp")
    staging.write_text(json.dumps(record), encoding="utf-8")
    os.replace(staging, target)


def clear_waiting(session_id) -> None:
    """Drop this session's `waiting`, wherever it is. The answer arrived.

    Claude Code emits **no event for "the prompt was answered"** — measured, by
    logging every hook across an approved prompt. `PreToolUse` fires *before*
    `PermissionRequest`, so it cannot mean granted; the first thing that happens
    only because a human said yes is `PostToolUse`, when the tool has run.

    Without it the strip clears at `Stop`, which is the end of the whole turn.
    Approving a `Skill` and then watching the agent work for ten minutes under a
    banner saying it is still blocked on you is the bug this fixes, and it is
    worse than showing nothing: the reader learns to distrust the strip.

    **No project resolution here, deliberately.** This runs after *every* tool
    call, so it skips the git subprocess and the `beril_cli` import that
    `resolve` needs — the state file already records which session wrote it, and
    that is the only question being asked. Session-scoped, so two sessions in
    one clone cannot clear each other's.

    That still leaves 59ms against the resolving path's 78ms, and 36ms of it is
    bare `python3` startup — so `settings.json` wraps this one in the same kind
    of shell guard `beril-runtime.sh` uses, and never starts an interpreter when
    no state file exists at all (6ms). The guard is nearly free here rather than
    a compromise: between `UserPromptSubmit` clearing the file and `Stop`
    writing the next one, a state file exists *only* while a prompt is genuinely
    pending, which is exactly when this needs to run.

    Only `waiting` is cleared. `turn_ended` is a fact about the past that the
    next `UserPromptSubmit` retires; a tool call has nothing to say about it.
    """
    if not session_id:
        return
    for path in (ROOT / "projects").glob("*/" + STATE_FILE):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (
            isinstance(record, dict)
            and record.get("state") == "waiting"
            and record.get("session_id") == session_id
        ):
            try:
                path.unlink()
            except OSError:
                pass


def resolve(payload: dict) -> "Path | None":
    """The project this session is working on, or None.

    `beril_cli.project_resolution` is imported rather than reimplemented: this
    would be the fourth copy of the lookup, and the previous duplication put the
    same first-match-wins bug in two places at once.
    """
    sys.path.insert(0, str(ROOT))
    try:
        from beril_cli.project_resolution import project_from_runtime, resolve_project
    except Exception:
        return None

    try:
        # Explicit binding, then a path in the payload, then cwd, then branch.
        project_id = resolve_project(payload, repo_root=ROOT)
    except Exception:
        project_id = None  # a shelled-out git call can fail; runtime.json answers
    if not project_id:
        # The signal the others cannot supply: a project created *during* this
        # session has no cwd, branch or path to be found by.
        project_id = project_from_runtime(payload.get("session_id"), ROOT)
    if not project_id:
        return None
    project = ROOT / "projects" / project_id
    return project if project.is_dir() else None


def record_for(payload: dict, project: Path):
    """The new state file contents: a dict, None to clear, or UNCHANGED."""
    event = payload.get("hook_event_name")

    if event == "UserPromptSubmit":
        return None

    if event == "PermissionRequest":
        tool = str(payload.get("tool_name") or "a tool")
        argument = find_detail(payload.get("tool_input"))
        detail = f"{tool}: {argument}" if argument else tool
    elif event == "Notification":
        # `PermissionRequest` fires ~6s earlier and knows the tool; this event
        # does not. Restating `waiting` here would blank that detail out and
        # reset `since`, which is the key the browser debounces notifications on
        # — so the reader would be told twice about one prompt.
        if read_state(project).get("state") == "waiting":
            return UNCHANGED
        message = str(payload.get("message") or "")
        detail = "" if message in GENERIC else message
    elif event == "Stop":
        detail = str(payload.get("last_assistant_message") or "")
    else:
        return UNCHANGED

    return {
        "state": "turn_ended" if event == "Stop" else "waiting",
        "detail": detail[:MAX_DETAIL],
        "since": time.time(),
        # Cross-checked against runtime.json by the renderer: a state file left
        # behind by a session that is long gone must not read as `waiting`.
        "session_id": payload.get("session_id") or "",
    }


def main() -> None:
    payload = json.load(sys.stdin)
    # Before `resolve`, because this is the one event that fires on every single
    # tool call and it does not need a project to do its job.
    if payload.get("hook_event_name") == "PostToolUse":
        return clear_waiting(payload.get("session_id"))

    project = resolve(payload)
    if project is None:
        return
    record = record_for(payload, project)
    if record is not UNCHANGED:
        write_state(project, record)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a hook that blocks the agent is worse than a stale dashboard
