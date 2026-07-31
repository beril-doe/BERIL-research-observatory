#!/usr/bin/env bash
# Built for a BERIL session, not as a copy of the global statusline.
#
# Kept, because you act on them mid-research: which project, what stage it is
# at, where to watch it, and how close context is to running out.
# Dropped: model, cost, elapsed, directory. All true, none of them change what
# you do next while a project is running.
#
# python3 rather than jq: jq is not guaranteed on the BERDL singleuser image and
# python3 always is, and this has to work in the pod where the dashboard runs.
python3 -c '
import json, os, re, socket, subprocess, sys
from pathlib import Path

d = json.load(sys.stdin)
cwd = d.get("workspace", {}).get("current_dir", "") or os.getcwd()
pct = int(float(d.get("context_window", {}).get("used_percentage") or 0))

C, G, Y, R, DIM, X = "\033[36m", "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"

def run(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=2,
                              cwd=cwd or None).stdout.strip()
    except Exception:
        return ""

# One git invocation, not two: each fork costs ~15ms and this renders every turn.
out = run("git", "rev-parse", "--show-toplevel", "--abbrev-ref", "HEAD").splitlines()
root = Path(out[0] if out else cwd)
branch = out[1] if len(out) > 1 and out[1] != "HEAD" else ""

# Which project this session is working on, in falling order of certainty.
#
# Every signal is either explicit or scoped to this session. None of them is
# shared mutable state, which is the requirement: several Claude Code sessions
# can run in one clone on different projects at once, and a repo-wide value
# (settings env, or "newest beril.yaml") would give all of them the same answer
# and flip under them as each one writes. Those were rejected for that reason.
projects_dir = (root / "projects").resolve()


def under_projects(candidate):
    """The <id> in projects/<id>/..., or None if the path is somewhere else."""
    try:
        rel = Path(candidate).resolve().relative_to(projects_dir)
    except (ValueError, OSError):
        return None
    return rel.parts[0] if rel.parts else None


def from_runtime(session_id):
    """The project whose runtime.json most recently recorded this session.

    Keyed by the id of the running session, so two sessions on two projects each
    resolve to their own. Shared with `.claude/hooks/dash_stop.py` rather than
    copied: both had the same first-match-wins bug, so the exit hook stopped the
    dashboard of whichever project sorted earlier.
    """
    try:
        from beril_cli.project_resolution import project_from_runtime

        return project_from_runtime(session_id, root)
    except Exception:
        return None


# 1. cwd. Only fires when Claude Code was *launched* inside the project:
#    workspace.current_dir does not follow a cd run in a tool call (measured).
pid = under_projects(cwd)
# 2. branch, for the projects/<id> convention. cwd wins, so you can sit on
#    projects/<a> while working in <b>.
if not pid:
    m = re.fullmatch(r"projects/([\w.-]+)", branch or "")
    pid = m.group(1) if m else None
# 3. /add-dir. An explicit per-session declaration, and the only override for a
#    session with no provenance yet, such as one editing tools/ from the root.
if not pid:
    for added in d.get("workspace", {}).get("added_dirs", []) or []:
        pid = under_projects(added)
        if pid:
            break
# 4. runtime.json. Unprompted, and the one that covers a normal research session.
if not pid:
    pid = from_runtime(d.get("session_id"))

pdir = root / "projects" / pid if pid else None
if not (pdir and pdir.is_dir()):
    pid = pdir = None

bar = "▓" * (pct // 10) + "░" * (10 - pct // 10)
heat = R if pct >= 90 else Y if pct >= 70 else G
# The checkout, ~-relative. Not the basename: there are two clones and both are
# named BERIL-research-observatory, so the folder name alone would look like it
# was telling you which one while telling you nothing.
home = str(Path.home())
where = str(root)
if where.startswith(home):
    where = "~" + where[len(home):]
line = [f"{C}BERIL{X}", f"{DIM}{where}{X}"]
# Always shown. Suppressing it on `projects/<id>` branches to avoid repeating the
# project name meant those branches — the ones an actual research session runs on
# — displayed no branch at all, which reads as "detached" rather than "same name".
if branch:
    line.append(branch)
line.append(f"{heat}{bar}{X} {pct}%")
print(" | ".join(line))

if not pdir:
    sys.exit(0)

# Stage and URL come from the dashboard itself, so the two cannot disagree.
sys.path.insert(0, str(root))
try:
    from tools.dashboard import (SETUP_CMD, STAGE_LABELS, can_serve_live, port_for,
                                 public_url, resolve_stage, snapshot_url)
    stage, inferred = resolve_stage(pdir)
    label = STAGE_LABELS.get(stage, stage) + ("?" if inferred else "")
    port = port_for(pid)
except Exception:
    label, port = "", None

# Only advertise a URL that answers. A dead link is exactly the small lie the
# page itself is built to avoid.
#
# ...and if nothing answers, start it. This is the only place that reliably can:
# it already resolves the project and derives the port, it runs every turn so a
# dashboard lost to a pod restart comes back by itself, and it is the thing
# displaying the URL, so there is no second step to surface it. The two skill-text
# launchers this replaces never fired during exploration — the earliest one sat in
# Phase C, after the plan is written *and* approved.
#
# A display component with a side effect is unusual, so it is bounded: it fires
# only when a project resolved AND the port is closed, and the launcher exits 0 on
# EADDRINUSE. Steady state is one 0.05s socket check and nothing else.
#
# `can_serve_live()` gates *which* launcher, and it sits inside the not-listening
# branch on purpose. Without it this loop was unbounded: on an image with no
# jupyter-server-proxy the server cannot bind, so it wrote a snapshot and exited
# 0, the port stayed closed, and the next turn spawned it again — forever, one
# process per turn, with the install instructions accumulating in `.dash.log`
# where nobody had a reason to look. Below, that case spawns `--static`
# deliberately instead: bounded work, no port, and a snapshot that is genuinely
# refreshed every turn. Placing the probe here rather than above the socket check
# keeps the steady state free — it only runs on turns that were about to spawn
# anyway (measured: 0.08ms enabled, 1.01ms worst case).
url = snap = ""
if port:
    s = socket.socket()
    s.settimeout(0.05)
    listening = s.connect_ex(("127.0.0.1", port)) == 0
    s.close()
    if listening:
        url = public_url(port)
    else:
        live = can_serve_live()
        try:
            log = open(pdir / ".dash.log", "ab")
            subprocess.Popen(
                [sys.executable, str(root / "tools" / "dashboard.py"), str(pdir)]
                + ([] if live else ["--static"]),
                # The server logs its one startup line; the snapshot writer says
                # the same thing this status line is already displaying, every
                # turn, so its stdout is dropped. stderr is kept either way —
                # that is the half worth having in a log.
                stdout=log if live else subprocess.DEVNULL, stderr=log,
                stdin=subprocess.DEVNULL, start_new_session=True, cwd=str(root),
            )
        except Exception:
            pass  # never let a display component break a turn
        if not live:
            snap = snapshot_url(pdir)

tail = [f"{G}●{X} {pid}" if url else f"{DIM}○{X} {pid}"]
if label:
    tail.append(label)
if url:
    tail.append(url)
elif snap:
    # Both halves matter: the URL is the only way to find the snapshot at all,
    # and the command is the only way out of snapshot mode. This is where the
    # instructions live now — the log file they used to sit in is gitignored.
    tail.append(snap)
    tail.append(f"{Y}{SETUP_CMD}{X} for live")
else:
    tail.append(f"{DIM}dashboard starting{X}")
print(f"  {DIM}└{X} " + f" {DIM}·{X} ".join(tail))
'
