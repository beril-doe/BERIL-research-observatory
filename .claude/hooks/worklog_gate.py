#!/usr/bin/env python3
"""Stop hook: refuse to end the turn while WORKLOG.md is behind the work.

The worklog was purely advisory before this — six skills each carry a one-line
"append a worklog entry", and an agent optimising for the analysis drops it. The
result across this repo was zero WORKLOG.md files, so the dashboard's timeline
had nothing to render.

Two triggers, OR'd, no stage branching:

* **an artifact is newer than the last entry** — a notebook ran, figures landed,
  data exported. Bounded by construction: a project has as many of these as it
  has notebooks.
* **nothing has been written for IDLE_SECONDS** — the backstop, and the only
  thing that covers exploration, which produces no artifact at all and so was
  invisible to a file-mtime rule. The reply is an activity entry (`~`), which
  the dashboard folds into a collapsed run.

Both self-debounce: writing the entry updates the mtime, which *is* the rate
limit. No counter, no state file, no transcript parsing.

Idle is mostly handled by the mechanism rather than by code — a Stop hook only
fires at the end of an agent turn, so waiting on a human, a permission prompt or
an overnight gap fires nothing. What is left is the turn *after* a long gap, and
for that the block explicitly accepts "nothing to record" as an answer: the
point is a reset mtime, not a manufactured entry.

The harness runs this with the *system* interpreter (3.9), so: stdlib only and
no modern syntax. `beril_cli` is imported the way dash_stop.py does it — best
effort, behind a bare except — because it is stdlib-only in practice but is not
guaranteed to be importable from whatever interpreter the harness picked.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# 15 minutes. The effective cadence is looser than this number suggests: a Stop
# hook fires at most once per turn, so a single turn running forty tool calls
# over half an hour produces one entry, not two. Turn this up if it nags.
IDLE_SECONDS = 900

# Scanned for the artifact trigger. Deliberately not the project root: beril.yaml
# and README.md are touched by tooling, and gating on those would fire the
# narrative branch for a status bump nobody would write an entry about.
ARTIFACT_DIRS = ("notebooks", "figures", "data")

# A complete project is archived. Artifacts stop moving, so only the time floor
# could fire, and it would then fire every fifteen minutes for as long as anyone
# sat reading the thing.
TERMINAL = ("complete",)

# absolute(), not resolve(): resolve() follows a symlinked copy of this hook back
# to wherever it really lives, which in a test tree is the wrong repo. Same
# reasoning as dash_stop.py.
ROOT = Path(__file__).absolute().parent.parent.parent


def resolve(payload):
    """Project id for this session, or None. Never raises."""
    sys.path.insert(0, str(ROOT))
    try:
        from beril_cli.project_resolution import resolve_project

        return resolve_project(payload, repo_root=ROOT)
    except Exception:
        return None


def status_of(project):
    """`status:` from beril.yaml, lowercased, or "" — a top-level key only.

    A hand-rolled scan rather than PyYAML, which the hook cannot import. Same
    constraint plan-gate.py works under.
    """
    try:
        with open(str(project / "beril.yaml"), encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line[:1] in (" ", "\t", "#", "\n"):
                    continue
                key, sep, value = line.partition(":")
                if sep and key.strip() == "status":
                    return value.split("#", 1)[0].strip().strip("'\"").lower()
    except OSError:
        pass
    return ""


def newest_artifact(project):
    """Newest mtime under the artifact directories, or 0.0 when there are none."""
    newest = 0.0
    for name in ARTIFACT_DIRS:
        for root, _dirs, files in os.walk(str(project / name)):
            for filename in files:
                try:
                    stamp = os.stat(os.path.join(root, filename)).st_mtime
                except OSError:
                    continue
                if stamp > newest:
                    newest = stamp
    return newest


NARRATIVE = (
    "Work has landed since the last worklog entry — a notebook ran, figures or "
    "data were written. Append one entry to projects/{pid}/WORKLOG.md per "
    ".claude/skills/worklog-capture/SKILL.md covering everything since: the "
    "decision, not the mechanics, and link the artifacts. One entry for the "
    "whole stretch, not one per file. Prefix the title with `!` if it records a "
    "correction. Then finish."
)

ACTIVITY = (
    "No worklog entry for {mins} minutes. Append an activity entry to "
    "projects/{pid}/WORKLOG.md — same format as .claude/skills/worklog-capture/"
    "SKILL.md, but prefix the title with `~`: '## YYYY-MM-DD · ~ what you were "
    "doing'. Two sentences on what this stretch ruled out, constrained or "
    "established. If it genuinely produced nothing, say exactly that in one "
    "line — an inconclusive stretch is a real constraint on the plan and a short "
    "honest entry beats a padded one. Then finish."
)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    # Set on the turn that this hook already blocked. Without it a block asking
    # for an entry would fire again on the turn that writes the entry, forever.
    if payload.get("stop_hook_active"):
        return

    pid = resolve(payload)
    if not pid:
        return
    project = ROOT / "projects" / pid
    if not project.is_dir() or status_of(project) in TERMINAL:
        return

    worklog = project / "WORKLOG.md"
    try:
        written = worklog.stat().st_mtime
    except OSError:
        written = 0.0  # no worklog yet: both triggers fire, either creates it

    if newest_artifact(project) > written:
        reason = NARRATIVE.format(pid=pid)
    elif time.time() - written > IDLE_SECONDS:
        reason = ACTIVITY.format(pid=pid, mins=int(IDLE_SECONDS / 60))
    else:
        return

    json.dump({"decision": "block", "reason": reason}, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a Stop hook that raises is a Stop hook that strands the turn
    sys.exit(0)
