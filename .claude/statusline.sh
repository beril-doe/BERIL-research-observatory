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
    """The project whose runtime.json already records this session.

    Keyed by the id of the running session, so two sessions on two projects each
    resolve to their own. Costs ~1ms across the whole tree (measured; 2 of 79
    projects carry one today) and reads state the normal workflow already wrote,
    so it needs no new file and no ceremony.
    """
    if not session_id:
        return None
    for manifest in sorted(projects_dir.glob("*/runtime.json")):
        try:
            recorded = json.loads(manifest.read_text())
        except Exception:
            continue
        for session in recorded.get("sessions", []):
            if session.get("session_id") == session_id:
                return recorded.get("project") or manifest.parent.name
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
    from tools.dashboard import STAGE_LABELS, port_for, public_url, resolve_stage
    stage, inferred = resolve_stage(pdir)
    label = STAGE_LABELS.get(stage, stage) + ("?" if inferred else "")
    port = port_for(pid)
except Exception:
    label, port = "", None

# Only advertise a URL that answers. A dead link is exactly the small lie the
# page itself is built to avoid.
url = ""
if port:
    s = socket.socket()
    s.settimeout(0.05)
    if s.connect_ex(("127.0.0.1", port)) == 0:
        url = public_url(port)
    s.close()

tail = [f"{G}●{X} {pid}" if url else f"{DIM}○{X} {pid}"]
if label:
    tail.append(label)
tail.append(url or f"{DIM}dashboard not running{X}")
print(f"  {DIM}└{X} " + f" {DIM}·{X} ".join(tail))
'
