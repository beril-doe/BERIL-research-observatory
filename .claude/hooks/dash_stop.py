#!/usr/bin/env python3
"""SessionEnd hook: stop the dashboard this session started.

`.claude/statusline.sh` starts `tools/dashboard.py` detached, so it outlives
Claude Code and nothing stopped it. This is the other half.

Best-effort like the other hook: always exits 0, never blocks. A SessionEnd hook
that hangs delays the user's exit.
"""

import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

# The rule: when the session goes away, so does its dashboard. Documented
# SessionEnd reasons are clear, resume, logout, prompt_input_exit,
# bypass_permissions_disabled, other — taken from the hook docs, not assumed.
#
# All but one end the session, `clear` included: /clear starts a fresh one that
# may well be a different project, so the old dashboard should go rather than
# linger pointing at the last thing. Having none until a project is resolved
# again is the correct state, and the status line starts one on the next turn
# once there is something to point at.
#
# `bypass_permissions_disabled` is the exception: a mode toggle, same session,
# same project, nothing ended.
STAYING = {"bypass_permissions_disabled"}

# absolute(), not resolve(): resolve() follows a symlinked copy of this hook
# back to wherever it really lives, which in a test tree is the wrong repo.
ROOT = Path(__file__).absolute().parent.parent.parent


def projects_for(payload: dict) -> "list[str]":
    """Every project whose dashboard this session may have started.

    Not one project. The status line starts a dashboard for whichever project the
    session is on, so a session that switched has one running per project it
    touched, each on its own port. Stopping only the current one left the rest
    alive after Claude Code exited — the leak this hook exists to prevent.""" 
    sys.path.insert(0, str(ROOT))
    try:
        from beril_cli.project_resolution import projects_for_session, resolve_project
    except Exception:
        return []

    session_id = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID")
    found = list(projects_for_session(session_id, ROOT))
    try:
        # cwd/branch/`/add-dir` can name a project the runtime record never saw.
        current = resolve_project(payload, repo_root=ROOT)
    except Exception:
        current = None  # a shelled-out git call can fail; the records still answer
    if current and current not in found:
        found.append(current)
    return found


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if payload.get("reason") in STAYING:
        return

    projects = projects_for(payload)
    if not projects:
        return

    # Match the process's argv, not the port: tools/dashboard.py rejects pidfiles
    # because they misfire on a recycled PID, and killing whatever holds 87xx has
    # the same failure mode against an unrelated process that grabbed it.
    #
    # Compare resolved paths, never strings. On macOS the spawner's argv carries
    # /var/... while this process sees /private/var/..., and string matching loses
    # that either way round — it silently killed nothing in both directions before
    # this was resolved on both sides.
    wanted = {(ROOT / "projects" / name).resolve() for name in projects}
    try:
        ps = subprocess.run(
            ["ps", "-axo", "pid=,command="], capture_output=True, text=True, timeout=5
        ).stdout
    except Exception:
        return

    for line in ps.splitlines():
        found = re.match(r"\s*(\d+)\s+(.*)$", line)
        if not found or "dashboard.py" not in found.group(2):
            continue
        argv = found.group(2).split("dashboard.py", 1)[1].split()
        if not argv:
            continue
        try:
            if Path(argv[0]).resolve() not in wanted:
                continue
            os.kill(int(found.group(1)), signal.SIGTERM)
        except (OSError, ValueError):
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never block the exit
