#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mistune>=3"]
# ///
"""Live HTML dashboard for one in-progress BERIL project.

Renders the project directory as it stands right now: where it is in the
lifecycle, what the agent has done (``WORKLOG.md``), and what exists on disk.
The operator opens it in a browser tab and watches the co-scientist work.

Design and rationale: ``docs/live-dashboard-design.md``.

Two constraints shape this file:

- **Runnable on stdlib alone.** It is run with a bare ``python3`` inside an
  ephemeral JupyterHub pod, so it must never *require* an install. Every
  third-party import is optional and guarded — see ``render_markdown``.
- **Relative asset URLs.** It is reached through ``jupyter-server-proxy`` at
  ``/proxy/<port>/``, which strips the prefix before the request arrives, so
  every emitted asset ``href``/``src``/fetch target must be relative. This
  breaks only inside JupyterHub, never on a developer's machine, so it is
  tested. The one deliberate exception is a link that opens a file in the
  surrounding Jupyter server (``JupyterRoutes``): it has to escape the proxy
  path, so it is a full ``https://`` URL built from ``HUB`` — never
  root-relative, which is what the self-test actually forbids.

Usage — two invocations, and the difference is deliberate::

    # On the hub. The PEP 723 block above is inert to python3, so this stays a
    # zero-install launch that picks up whatever the image already provides
    # (mistune is present on BERDL, so markdown renders). No network, no venv.
    setsid nohup python3 tools/dashboard.py projects/<id> > projects/<id>/.dash.log 2>&1 &

    # Off-cluster. uv honours the block even inside this project, building an
    # isolated script env, so markdown renders on a laptop whose system python
    # has nothing installed. Needs network the first time.
    uv run tools/dashboard.py projects/<id>

``uv run`` deliberately does **not** inherit the interpreter's site-packages, so
it is the wrong launcher for the pod — it would re-fetch deps the image already
has, and fail outright with no egress. Hence the skills use ``python3`` and this
docstring documents ``uv run`` for local work.

It is idempotent: a second launch binds the same deterministic port, gets
EADDRINUSE, prints the URL and exits 0. The kernel is the mutex, so there is no
pidfile to go stale and no stop command to misfire on a recycled PID.
"""

from __future__ import annotations

import argparse
import hashlib
import html as _html
import json
import os
import re
import shutil
import site
import sys
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

HUB = "https://hub.berdl.kbase.us"

STAGES = ["exploration", "proposed", "active", "analysis", "reviewed", "complete"]

# Human labels for the rail. The enum is the contract and is not touched here;
# these exist because `analysis` names the activity that actually happens during
# `active`, so the raw values read backwards to anyone watching a run.
STAGE_LABELS = {
    "exploration": "exploring",
    "proposed": "plan written",
    "active": "running analysis",
    "analysis": "report drafted",
    "reviewed": "reviewed",
    "complete": "approved",
}

# Live mode needs jupyter-server-proxy, which the BERDL image does not ship, so
# every new user meets this text once. It lives here as one constant because it
# has two audiences — the snapshot banner and the status line — and two
# hand-maintained copies of the same instruction is how they end up disagreeing.
#
# `beril setup` rather than a flag on this file: the wizard is where a user already
# goes to get their environment working, and one entry point is one thing to
# remember. This used to read `python3 tools/dashboard.py --setup`, because the
# image's `beril` is a pinned copy under `/opt/conda` (an *overlay* mount, so it
# reverts on every pod restart and cannot be updated by a user) and could predate
# this feature. That is being handled by shipping a newer `beril` in the image
# instead, which is the right place to fix it.
SETUP_CMD = "beril setup"
# Step 2 is unavoidable: jupyter_server builds its handler table at startup, so a
# newly enabled extension is invisible until the server restarts. Step 3 exists
# because that restart kills the terminal Claude Code is running in, and people
# reasonably assume it kills the session with it. It does not.
RESTART_STEPS = (
    "Hub Control Panel → Stop My Server, then Start.",
    "Reopen a terminal and run `claude --resume` to pick this session back up.",
)
SETUP_STEPS = (f"Run `{SETUP_CMD}` and answer yes to the live dashboard step.",) + RESTART_STEPS

# Written by .claude/hooks/agent_state.py, read here and nowhere else.
AGENT_STATE_FILE = ".agent-state.json"
# How long a `waiting` claim is believed. It is the one *present tense* thing
# this page says — "a human is blocked on this right now" — and the only event
# that ends it is one Claude Code has to still be alive to send. A pod culled or
# a SIGKILL mid-prompt leaves `waiting` on disk with nobody left to answer it,
# and a page that says "waiting for you" about a process that no longer exists
# is worse than one that says nothing.
#
# 30 minutes because the file is not evidence of a *live* prompt, only of one
# opened at `since`: stepping away for lunch with a real prompt open is normal,
# and expiring at 5 minutes would call that a lie. `turn_ended` never expires —
# it is a claim about the past, so it cannot go stale.
WAIT_TTL = 1800.0

FIGURE_EXT = {".png", ".jpg", ".jpeg", ".svg"}
DATA_EXT = {".csv", ".tsv", ".json", ".parquet"}
PRUNE_DIRS = {".ipynb_checkpoints", "__pycache__", ".git"}

# Which Jupyter route actually *renders* each type. Measured against this image
# (jupyter-server 2.17.0, jupyterlab 4.4.10, notebook 7.4.7) — see JupyterRoutes.
#
# Markdown is the exception: it is not routed to Jupyter at all. This dashboard
# renders it itself and shows it in the same overlay the figures use — see
# render_markdown and the `/_doc/` route.
#
# The rejected alternative, for the next person who reads Jupyter's URL routes and
# thinks it should work: `lab/tree/<path>` opens a file with its *default* widget
# factory, and markdown's default is the plain text editor (FileEditorFactory
# declares `defaultFor:["markdown","*"]`), so it shows raw source. Lab's tree
# resolver reads only `file-browser-path` out of the query string and discards
# everything else, so `?factory=` cannot override it. Notebook 7's `/edit/` route
# *does* do `urlParams.get('factory') ?? defaultFactory`, so
# `edit/<path>?factory=Markdown+Preview` looks like the answer — and it is the URL
# Notebook 7's own file browser generates for "Open With -> Markdown Preview".
# It was tried and it fails on the BERDL image: the edit page renders a blank
# pane, because markdownviewer-extension is not in that page's plugin set. The
# console also shows `Command 'filebrowser:open-path' not registered`, since this
# image disables `@jupyterlab/filebrowser-extension:defaultFileBrowser` (BERDL
# ships its own browser) and that command is registered inside the plugin which
# requires it. Rendering in-process avoids depending on any of that, and is the
# only option that also works off-cluster.
MARKDOWN_EXT = {".md", ".markdown"}
# Where the overlay fetches rendered markdown from. Kept off the project's own
# namespace by the leading underscore, since every other path this server answers
# is a real file. LIGHTBOX_JS hardcodes the same prefix without the leading slash.
DOC_ROUTE = "/_doc/"
# Types with a real Lab viewer: Notebook, the DataGrid CSV/TSV viewers, and the
# collapsible JSON tree. `.parquet` is deliberately absent — see open_url.
LAB_TREE_EXT = {".ipynb", ".csv", ".tsv", ".json", ".geojson", ".jsonl"}

_STATUS_RE = re.compile(r"^status:\s*([\w-]+)", re.M)
_APPROVAL_RE = re.compile(r"^approval:\s*$", re.M)
_PLAN_BLOCK_RE = re.compile(r"^plan_approval:\s*$(.*?)(?=^\S|\Z)", re.M | re.S)
_FIELD_RE = re.compile(r'^\s+(\w+):\s*"?([^"\n]*?)"?\s*$', re.M)
# Byte-identical twin of beril_cli.approve_cmd.plan_digest / plan-gate.py.
# Bytes, not text, and no strip(): see plan_digest below.
_REVHIST_RE = re.compile(rb"^##[ \t]+Revision History[ \t\r]*$", re.M)
_NEXT_SECTION_RE = re.compile(rb"^##[ \t]", re.M)
_REPORT_HASH_RE = re.compile(r"<!--\s*report_hash:\s*sha256:([0-9a-f]+)\s*-->")
# `tools/review.sh --type plan` writes this footer instead; see review_docs for
# why it is checked against the whole RESEARCH_PLAN.md and not plan_digest().
_PLAN_HASH_RE = re.compile(r"<!--\s*plan_hash:\s*sha256:([0-9a-f]+)\s*-->")

# Separator, arrow and multiplier codepoints are copied from
# .claude/skills/worklog-capture/SKILL.md — the producer contract.
_ENTRY_RE = re.compile(r"^## (\d{4}-\d\d-\d\d) · (.+?)(?: → (\w+))?$")
_LINK_RE = re.compile(r"^→ \[([^\]]*)\]\(([^)]*)\)(?:\s*[×x](\d+))?\s*$")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass
class Doc:
    name: str
    path: str
    chip: "str | None" = None


@dataclass
class Link:
    label: str
    path: str
    count: int
    exists: bool


@dataclass
class Entry:
    date: str
    title: str
    new_status: "str | None"
    prose: str = ""
    links: list = field(default_factory=list)
    correction: bool = False


@dataclass
class Notebook:
    name: str
    path: str
    cells: int
    with_output: int
    errors: int
    mtime: float


@dataclass
class FileRef:
    name: str
    path: str
    size: int
    mtime: float


@dataclass
class JupyterRoutes:
    """Absolute URLs that open a project file in the surrounding Jupyter server.

    These are deliberately **absolute**, unlike every other URL this page emits.
    The dashboard is reached through ``/proxy/<port>/``, which strips the prefix
    before the request arrives, so a relative href would resolve back inside the
    dashboard's own little file server instead of Jupyter. Built from ``HUB`` +
    ``JUPYTERHUB_SERVICE_PREFIX`` exactly as ``public_url`` builds the proxy URL.
    Being full ``https://`` URLs they coexist with the relative-asset invariant
    rather than violating it: the self-test bans *root-relative* (``href="/``)
    URLs, which these are not.

    ``base`` is ``https://hub.berdl.kbase.us/user/<name>/``; ``rel`` is the
    project directory relative to the server's ``root_dir`` (``""`` when the
    project *is* the root).
    """

    base: str
    rel: str

    def _path(self, path: str) -> str:
        """Percent-encode per segment, keeping ``/`` literal — what Jupyter's own
        ``URLExt.encodeParts`` does. Without this a filename containing a space
        or ``#`` silently produces a broken link."""
        joined = f"{self.rel}/{path.lstrip('/')}" if self.rel else path.lstrip("/")
        return "/".join(quote(seg, safe="") for seg in joined.split("/"))

    def open_url(self, path: str) -> "str | None":
        """The URL that opens ``path`` in a viewer that actually renders it, or
        ``None`` when Jupyter has no such viewer and the caller should keep the
        plain relative link.

        One route: ``lab/tree/<path>`` opens a file with its **default** widget
        factory. That is right for notebooks (Notebook), ``.csv``/``.tsv`` (the
        DataGrid viewers) and ``.json`` (the collapsible JSON tree).

        Markdown is deliberately **not** here — it never goes to Jupyter. The
        dashboard renders it itself and opens it in the figure overlay; see the
        module-level comment on ``MARKDOWN_EXT`` for why the ``/edit/?factory=``
        route was tried and abandoned.

        ``.parquet`` returns ``None`` on purpose. Nothing on this image registers
        a parquet viewer, so it falls through to the wildcard text editor, whose
        text model asks the contents API to decode it and gets back
        ``400 … is not UTF-8 encoded`` — an error dialog and a disposed tab. The
        relative link instead downloads the file, which is the useful action.
        """
        ext = Path(path).suffix.lower()
        if ext in LAB_TREE_EXT:
            return f"{self.base}lab/tree/{self._path(path)}"
        return None

    def nbconvert_url(self, path: str) -> str:
        """A static, kernel-free HTML render of a notebook, with its saved
        outputs. Complements the Lab link rather than replacing it: no kernel
        boots, so it paints in well under a second, but it is a dead snapshot.
        Only ever call this for ``.ipynb`` — jupyter-server returns a blank 200
        for anything else on this route."""
        return f"{self.base}nbconvert/html/{self._path(path)}"


@dataclass
class State:
    project_id: str
    stage: str
    inferred: bool
    approval: dict
    deviations: int
    entries: list
    docs: list
    notebooks: list
    figures: list
    data: list
    last_activity: float
    first_activity: float
    etag: str
    routes: "JupyterRoutes | None"
    plan: dict = field(default_factory=dict)
    agent: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Stage
# ---------------------------------------------------------------------------


def read_status(project: Path) -> tuple:
    """Return ``(status, has_approval_block)`` from ``beril.yaml``.

    One key is not a parsing problem, and PyYAML is not worth a runtime
    dependency inside an ephemeral pod. ``plan_approval:`` is deliberately not
    matched here — that is the plan-review witness, not the submission approval.
    """
    try:
        text = (project / "beril.yaml").read_text(encoding="utf-8")
    except OSError:
        return None, False
    found = _STATUS_RE.search(text)
    return (found.group(1) if found else None), bool(_APPROVAL_RE.search(text))


def _session_is_gone(project: Path, session_id) -> bool:
    """True when `runtime.json` knows this project's sessions and not this one.

    The cheap half of not lying. `runtime.json` is written by
    `.claude/hooks/beril-runtime.sh` on SessionStart and on the first write into
    a project, so by the time anything can resolve a project well enough to
    record a state for it, that session is already listed — an absence therefore
    means the file outlived the session that wrote it.

    No `runtime.json` at all is not evidence of anything, so it is not treated
    as any: the check only fires on a file that *does* have an opinion.
    """
    try:
        recorded = json.loads((project / "runtime.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    sessions = recorded.get("sessions") if isinstance(recorded, dict) else None
    if not isinstance(sessions, list) or not sessions:
        return False
    return not any(
        isinstance(item, dict) and item.get("session_id") == session_id
        for item in sessions
    )


def read_agent_state(project: Path) -> dict:
    """Is the agent blocked on a human? `{}` when there is nothing to say.

    Expiry happens **here rather than in the hook**, because the hook only runs
    when something happens and going stale is precisely what happens when
    nothing does. There is no event for "the pod was culled".

    `state` is therefore not the file's state: a `waiting` past `WAIT_TTL`, or
    one whose session `runtime.json` has never heard of, is downgraded to
    `unknown` — which renders as a neutral chip, no strip and no notification.
    Saying "I no longer know" costs a reader nothing; saying "come back, you are
    blocking the agent" about a dead process costs them a trip.
    """
    try:
        record = json.loads((project / AGENT_STATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(record, dict) or record.get("state") not in ("waiting", "turn_ended"):
        return {}

    since = record.get("since")
    since = float(since) if isinstance(since, (int, float)) else 0.0
    state = record["state"]
    if state == "waiting" and (
        time.time() - since > WAIT_TTL
        or _session_is_gone(project, record.get("session_id"))
    ):
        state = "unknown"
    return {"state": state, "detail": str(record.get("detail") or ""), "since": since}


def _has_executed_notebook(project: Path) -> bool:
    for path in sorted((project / "notebooks").glob("*.ipynb")):
        stats = notebook_stats(path)
        if stats and stats.with_output:
            return True
    return False


def _infer_stage(project: Path) -> str:
    """Filesystem-only inference — the only thing that works for the majority of
    projects, which have no ``beril.yaml``.

    ``complete`` is never inferred from anything but ``SUBMITTED.md``: approval
    is a human act and the page must not imply one happened.
    """
    if (project / "SUBMITTED.md").exists():
        return "complete"
    if any(project.glob("REVIEW*.md")):
        return "reviewed"
    if (project / "REPORT.md").exists():
        return "analysis"
    if _has_executed_notebook(project):
        return "active"
    if (project / "RESEARCH_PLAN.md").exists():
        return "proposed"
    return "exploration"


def resolve_stage(project: Path) -> tuple:
    """Return ``(stage, inferred)``. ``inferred`` drives the honesty label."""
    status, has_approval = read_status(project)
    if has_approval:
        return "complete", False
    if status in STAGES:
        return status, False
    return _infer_stage(project), True


# ---------------------------------------------------------------------------
# Witnesses — plan approval, deviations, review freshness
# ---------------------------------------------------------------------------


def plan_digest(plan_bytes: bytes) -> str:
    """sha256 of the plan *above* ``## Revision History``.

    **This must stay byte-identical to ``beril_cli.approve_cmd.plan_digest``**,
    which is itself twinned with ``.claude/hooks/plan-gate.py``. It is a third
    deliberate copy: this file runs under a bare ``python3`` in an ephemeral pod
    and cannot import ``beril_cli``. ``test_plan_digest_is_a_twin_of_beril_approve``
    pins it and activates automatically once that module exists.

    Two details are load-bearing and were both wrong in the first draft here:

    - **Bytes, not text.** ``Path.read_text`` translates CRLF to LF, so a CRLF
      plan would hash differently than the bytes ``beril approve`` signed.
    - **No ``strip()``.** The canonical digest keeps the whitespace above the
      heading. Stripping produced a digest that never matched, which would have
      rendered every approved plan as "approval stale".
    """
    match = _REVHIST_RE.search(plan_bytes)
    if match is None:
        return hashlib.sha256(plan_bytes).hexdigest()
    tail = plan_bytes[match.end():]
    following = _NEXT_SECTION_RE.search(tail)
    rest = tail[following.start():] if following is not None else b""
    return hashlib.sha256(plan_bytes[: match.start()] + rest).hexdigest()


_SECTION_RE = r"^##+ +{}\s*$(.*?)(?=^##(?!#)|\Z)"
_PLANNED_NB_RE = re.compile(r"^#{3,} +Notebook +\d+", re.M)


def _md_section(text: str, *names: str) -> str:
    """First matching ``## <name>`` section, flattened to one line of prose.

    Tolerates the heading spellings that actually occur across the 73 plans on
    disk (``Hypothesis`` and ``Hypotheses``); returns ``""`` when absent, which
    is the case for a handful of older plans.
    """
    for name in names:
        found = re.search(_SECTION_RE.format(re.escape(name)), text, re.M | re.S)
        if not found:
            continue
        body = re.sub(r"^\s*[-*+]\s+", "", found.group(1).strip(), flags=re.M)
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            return body
    return ""


def plan_summary(project: Path) -> dict:
    """The plan's orientation content: what is being asked, and what is predicted.

    This is the one thing the page was missing entirely — the plan was a card in
    § Documents, indistinguishable from the report, so the question the project
    exists to answer was invisible unless you opened and read the file. Measured
    coverage across the 73 plans on disk: Research Question 71, Hypothesis or
    Hypotheses 69.

    ``planned_notebooks`` is a **count, not a mapping**. Plan section numbers do
    not correspond to filenames — measured: one plan's "Notebook 1" is
    ``00_inventory_audit.ipynb`` and another's is ``02_essential_families.ipynb``,
    notebooks get renamed after the plan is frozen, and unplanned ones appear. A
    per-notebook "done/not done" would therefore be confidently wrong, so the
    page reports both counts and lets the reader draw the conclusion.
    """
    try:
        text = (project / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
    except OSError:
        return {}
    return {
        "question": _md_section(text, "Research Question"),
        "hypothesis": _md_section(text, "Competing Hypotheses", "Hypotheses", "Hypothesis"),
        # What would settle it. Present in 50 of the 73 plans, and the section a
        # reader needs in order to judge whether a worklog entry moved the
        # project toward an answer or away from one.
        "outcomes": _md_section(
            text, "Expected Outcomes", "Pre-registered Decision Rule", "Decision Criteria"
        ),
        "planned_notebooks": len(_PLANNED_NB_RE.findall(text)),
    }


def _planning_workflow_installed() -> bool:
    """Does this repo have the plan-approval machinery at all?

    Without ``plan-gate.py`` there is no such thing as an unapproved plan, so
    accusing a project of missing an approval would be a false alarm.
    """
    root = Path(__file__).resolve().parent.parent
    return (root / ".claude" / "hooks" / "plan-gate.py").is_file()


def _accusable(project: Path, stage: str) -> bool:
    """Can this project meaningfully be said to have *skipped* the checkpoint?

    Repo-wide machinery detection is not enough, and gating on it alone was still
    a false accusation — just a deferred one. Simulated: the day the plan-gate
    lands, ``plan-gate.py`` exists, so all **78** projects on disk flip to
    ``plan not approved ✗``, 17 of them already ``complete``. They predate the
    concept; they cannot have skipped a gate that did not exist.

    Two things make an accusation meaningful, and it needs either:

    - **work still in flight** (``active``/``analysis``) — the checkpoint is live
      and the approval is genuinely absent; or
    - **a deviation record on disk** — the hook ran, saw analysis written under
      no valid approval, and logged it. That is proof the gate was watching, so
      the accusation stands even on a finished project.

    A ``reviewed``/``complete`` project with neither is pre-gate and stays silent.
    """
    if not _planning_workflow_installed():
        return False
    if (project / "plan_deviations.jsonl").is_file():
        return True
    return stage in ("active", "analysis")


def plan_approval(project: Path, stage: str) -> dict:
    """The plan-review witness.

    ``status`` grants nothing — an agent writing ``status: active`` records no
    approval. Only the ``plan_approval`` block, written by a human running
    ``beril approve``, is evidence.

    Returns ``na`` (chip omitted) when the repo has no plan-gate machinery: a
    project cannot fail a checkpoint that did not exist when it ran.
    """
    try:
        manifest = (project / "beril.yaml").read_text(encoding="utf-8")
    except OSError:
        manifest = ""

    block = _PLAN_BLOCK_RE.search(manifest)
    past_checkpoint = STAGES.index(stage) >= STAGES.index("active")
    if not block:
        accusable = past_checkpoint and _accusable(project, stage)
        return {"state": "missing" if accusable else "na"}

    fields = dict(_FIELD_RE.findall(block.group(1)))
    recorded = fields.get("plan_hash", "").replace("sha256:", "")
    try:
        current = plan_digest((project / "RESEARCH_PLAN.md").read_bytes())
    except OSError:
        return {"state": "stale"}

    return {
        "state": "approved" if recorded == current else "stale",
        "by": fields.get("by", ""),
        "at": fields.get("at", ""),
        # `beril approve --relayed` writes this; a TTY-confirmed approval omits
        # it. Absent means witnessed, which is the stronger claim.
        "via": fields.get("via", ""),
    }


def count_deviations(project: Path) -> int:
    """Advisory count from ``.claude/hooks/plan-gate.py``.

    The hook is a witness, not a gate, and the dashboard must not upgrade it
    into one — this is a number next to a link, nothing more.
    """
    try:
        text = (project / "plan_deviations.jsonl").read_text(encoding="utf-8")
    except OSError:
        return 0
    return sum(1 for line in text.splitlines() if line.strip())


def review_docs(project: Path) -> list:
    """Every review file with a freshness chip against the thing it reviewed.

    Without this the page shows "reviewed" for a review that no longer applies —
    the single most misleading thing a lifecycle dashboard can do.

    **Two families, two subjects.** ``glob("REVIEW*.md")`` is anchored at the
    start of the filename, so it never matched ``PLAN_REVIEW_1.md`` — the file
    ``tools/review.sh --type plan`` writes, and the one ``/berdl_start``'s
    plan-review checkpoint option (b) tells the operator to produce. The default
    path through the workflow therefore generated a document § Documents could
    not see. Each family is chipped against its own subject: report reviews
    against ``REPORT.md``, plan reviews against ``RESEARCH_PLAN.md``.

    **The plan chip uses the whole file, not ``plan_digest``.** Those are
    deliberately different hashes and mixing them would mark every plan review
    stale forever. ``plan_digest`` excludes ``## Revision History`` so a
    revision bump does not void a human's approval; ``review.sh`` line 130
    writes ``sha256sum`` of the *entire* ``RESEARCH_PLAN.md`` into its
    ``plan_hash`` footer, because a review is only current for the exact text
    that was reviewed. This function must match the producer, so it hashes the
    whole file.
    """

    def subject(name: str):
        try:
            return hashlib.sha256((project / name).read_bytes()).hexdigest()
        except OSError:
            return None

    # (glob, subject hash, footer pattern). PLAN_REVIEW is listed first only so
    # the intent is obvious; the result is sorted by name below.
    families = (
        ("PLAN_REVIEW*.md", subject("RESEARCH_PLAN.md"), _PLAN_HASH_RE),
        ("REVIEW*.md", subject("REPORT.md"), _REPORT_HASH_RE),
    )

    docs = []
    for pattern, current, footer_re in families:
        for path in sorted(project.glob(pattern)):
            chip = None
            if current is not None:
                try:
                    found = footer_re.search(path.read_text(encoding="utf-8"))
                except OSError:
                    found = None
                # No footer reads as stale, matching the pre-existing behaviour
                # for report reviews: a review that cannot prove what it covers
                # is not evidence that the current subject was reviewed.
                chip = "current" if found and found.group(1) == current else "stale"
            docs.append(Doc(path.name, path.name, chip))
    return sorted(docs, key=lambda d: d.name)


# ---------------------------------------------------------------------------
# Worklog
# ---------------------------------------------------------------------------


def parse_worklog(text: str, project: Path) -> list:
    """Parse ``WORKLOG.md`` in file order (oldest first; the renderer reverses).

    Anything that is neither a heading nor a link line is prose.
    """
    entries: list = []
    for line in text.splitlines():
        head = _ENTRY_RE.match(line)
        if head:
            title = head.group(2).strip()
            # A leading `!` marks a correction — a bug found, a re-run, an
            # approach abandoned. Detected after the match rather than in the
            # regex so the grammar itself is unchanged and an unmarked worklog
            # keeps parsing exactly as before.
            correction = title.startswith("!")
            if correction:
                title = title[1:].strip()
            entries.append(
                Entry(head.group(1), title, head.group(3), correction=correction)
            )
            continue
        if not entries:
            continue
        link = _LINK_RE.match(line)
        if link:
            target = link.group(2)
            entries[-1].links.append(
                Link(
                    label=link.group(1),
                    path=target,
                    count=int(link.group(3)) if link.group(3) else 1,
                    exists=(project / target).exists(),
                )
            )
        elif line.strip():
            entries[-1].prose = (entries[-1].prose + " " + line.strip()).strip()
    return entries


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------


def notebook_stats(path: Path) -> "Notebook | None":
    """Cell counts from raw JSON — no nbformat, no nbconvert.

    Returns ``None`` when unreadable. A partial read while the agent is writing
    the notebook is routine, not exceptional; the caller renders a placeholder
    and it self-heals on the next poll.
    """
    try:
        cells = json.loads(path.read_text(encoding="utf-8")).get("cells", [])
        stat = path.stat()
    except (OSError, ValueError, AttributeError):
        return None
    with_output = sum(1 for c in cells if c.get("outputs"))
    errors = sum(
        1
        for c in cells
        for o in (c.get("outputs") or [])
        if o.get("output_type") == "error"
    )
    return Notebook(
        path.name, "notebooks/" + path.name, len(cells), with_output, errors, stat.st_mtime
    )


def _files(directory: Path, extensions: set, prefix: str) -> list:
    refs = []
    if not directory.is_dir():
        return refs
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in extensions:
            stat = path.stat()
            refs.append(
                FileRef(path.name, prefix + "/" + path.name, stat.st_size, stat.st_mtime)
            )
    return refs


def compute_etag(fingerprint: list) -> str:
    digest = hashlib.sha1()
    for item in sorted(fingerprint):
        digest.update(repr(item).encode("utf-8"))
    return digest.hexdigest()[:16]


def scan(project: Path) -> State:
    """Read the entire project off disk. A pure function of the directory —
    nothing is cached, so a cold restart loses only the TCP connection."""
    stage, inferred = resolve_stage(project)

    notebooks = []
    for path in sorted((project / "notebooks").glob("*.ipynb")):
        stats = notebook_stats(path)
        if stats is None:
            stats = Notebook(path.name, "notebooks/" + path.name, 0, 0, 0, 0.0)
        notebooks.append(stats)

    docs = [
        Doc(name, name)
        for name in ("RESEARCH_PLAN.md", "REPORT.md")
        if (project / name).exists()
    ] + review_docs(project)

    try:
        worklog = (project / "WORKLOG.md").read_text(encoding="utf-8")
    except OSError:
        worklog = ""

    stamps: list = []
    fingerprint: list = []
    for root, dirs, names in os.walk(project):
        dirs[:] = [d for d in dirs if d not in PRUNE_DIRS]
        for name in names:
            try:
                stat = os.stat(os.path.join(root, name))
            except OSError:
                continue
            stamps.append(stat.st_mtime)
            fingerprint.append(
                (os.path.join(root, name), stat.st_mtime_ns, stat.st_size)
            )

    # The agent state goes into the fingerprint as its *resolved* value, not as
    # the file's mtime — the two disagree exactly when it matters. Nothing on
    # disk changes when a `waiting` ages past WAIT_TTL, so an mtime-only etag
    # keeps answering 304 and the page holds "waiting for you" on screen forever
    # while `read_agent_state` has long since stopped believing it. Folding the
    # answer in means the expiry itself invalidates the cache.
    agent = read_agent_state(project)
    fingerprint.append(("\x00agent-state", agent.get("state", ""), agent.get("since", 0)))

    return State(
        project_id=project.name,
        stage=stage,
        inferred=inferred,
        approval=plan_approval(project, stage),
        deviations=count_deviations(project),
        entries=parse_worklog(worklog, project),
        docs=docs,
        notebooks=notebooks,
        figures=_files(project / "figures", FIGURE_EXT, "figures"),
        data=_files(project / "data", DATA_EXT, "data"),
        last_activity=max(stamps) if stamps else 0.0,
        first_activity=min(stamps) if stamps else 0.0,
        etag=compute_etag(fingerprint),
        routes=jupyter_routes(project),
        plan=plan_summary(project),
        agent=agent,
    )


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

DASH_CSS = """
:root{--d-bg:#12141a;--d-panel:#171a21;--d-card:#1b1f28;--d-line:#262a35;
--d-fg:#e6e8ee;--d-mut:#8b93a7;--d-dim:#5c6478;--d-accent:#58a6ff;--d-ok:#3fb950;
--d-warn:#d29922;--d-bad:#ff7b72;}
body{background:var(--d-bg);color:var(--d-fg);margin:0;
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
#root{max-width:1100px;margin:0 auto;padding:0 20px 60px;}
/* Sticky, so it must stay short — everything inside is either one line or
   clamped. A shadow rather than a hairline: content genuinely passes beneath
   it, and the border alone read as a seam cutting through the text. */
.d-hd{position:sticky;top:0;z-index:9;background:var(--d-panel);
border-bottom:1px solid var(--d-line);margin:0 -20px 24px;padding:12px 20px 14px;
box-shadow:0 8px 20px -12px #000c;}
/* Anchors and scrolled-to elements must clear the sticky region. */
#root [id]{scroll-margin-top:180px;}
.d-id{font-family:ui-monospace,SFMono-Regular,monospace;font-weight:650;}
.d-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.d-chip{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;
font-weight:600;border:1px solid var(--d-line);background:var(--d-card);color:var(--d-mut);}
.d-chip.ok{color:#7ee787;border-color:#238636aa;background:#23863626;}
.d-chip.bad{color:var(--d-bad);border-color:#ff7b7255;background:#ff7b7218;}
.d-chip.warn{color:#e3b341;border-color:#d2992255;background:#d2992218;}
.d-chip.now{color:#79b8ff;border-color:#1f6feb66;background:#1f6feb26;}
.live{color:var(--d-ok);}.idle{color:var(--d-warn);}.cold{color:var(--d-dim);}
.d-rail{display:flex;list-style:none;margin:12px 0 4px;padding:0;}
.d-rail li{flex:1;text-align:center;font-size:11px;position:relative;color:var(--d-dim);}
.d-rail li i{display:block;width:10px;height:10px;border-radius:50%;
margin:0 auto 6px;background:#2b3040;}
.d-rail li[data-state=done]{color:#7ee787;}.d-rail li[data-state=done] i{background:var(--d-ok);}
.d-rail li[data-state=current]{color:#79b8ff;font-weight:700;}
.d-rail li[data-state=current] i{background:var(--d-accent);box-shadow:0 0 0 4px #58a6ff2e;}
.d-rail li[data-state=future]{opacity:.32;}
.d-rail li:not(:last-child):after{content:'';position:absolute;top:4px;
left:calc(50% + 11px);right:calc(-50% + 11px);height:1px;background:#2b3040;}
/* Inline readouts. Tabular figures matter here: the page repaints every 4s and
   proportional digits make the elapsed clock jitter sideways as they change. */
.d-read{display:flex;flex-direction:column;align-items:flex-end;line-height:1.15;}
.d-read.push{margin-left:auto;}
/* No `color` here on purpose: relTimes() sets .live/.idle/.cold on this element
   and a `.d-read b` rule would outrank them, silencing the liveness signal. */
.d-read b{font:600 13px/1.15 ui-monospace,SFMono-Regular,monospace;
font-variant-numeric:tabular-nums;}
.d-read i{font-style:normal;font-size:9px;text-transform:uppercase;
letter-spacing:.08em;color:var(--d-dim);}
/* The dot inherits currentColor, so it turns amber then grey with the number —
   one glance answers "is the agent alive". Only on the activity readout. */
.d-read.push b::before{content:'';display:inline-block;width:6px;height:6px;
border-radius:50%;background:currentColor;margin-right:6px;vertical-align:.1em;}
.d-eyebrow{display:block;font-size:9px;text-transform:uppercase;
letter-spacing:.1em;color:var(--d-dim);margin-bottom:3px;}
.d-now{border-left:2px solid var(--d-accent);background:#161b24;padding:8px 14px;
margin-top:12px;border-radius:0 6px 6px 0;}
.d-now b{font-size:14px;}
/* Snapshot mode only, and loud on purpose: it is the one thing on this page the
   reader has to act on, and the instructions it replaces were five lines in a
   gitignored log file nobody had a reason to open. Above #root's header rather
   than inside it — the header is sticky and must stay short. */
.d-setup{border-left:2px solid var(--d-warn);background:#221c10;padding:10px 14px;
margin:0 0 18px;border-radius:0 6px 6px 0;font-size:13.5px;color:#c4cad8;}
.d-setup b{color:#e3b341;}
.d-setup ol{margin:8px 0 0;padding-left:20px;}
.d-setup li{margin:4px 0;}
.d-setup code{font-family:ui-monospace,SFMono-Regular,monospace;font-size:12.5px;
background:#0d1017;border:1px solid var(--d-line);border-radius:4px;padding:1px 6px;}
/* "The agent is blocked on you." Same anchoring as .d-setup and for the same
   reason — a sibling of #root, so the 4s poll cannot wipe it — but with a
   second reason on top: an element inside #root is destroyed and rebuilt every
   4s, which would restart the pulse below on every poll. A 0.6s highlight every
   4s, forever, is a flashing banner: WCAG 2.3.1, and unbearable to sit next to.
   Out here it animates once, on the transition that earned it.
   Filled by STATE_JS, which is why it starts empty and hidden. */
.d-wait{border-left:2px solid var(--d-warn);background:#2a1f0c;padding:9px 14px;
margin:0 0 14px;border-radius:0 6px 6px 0;font-size:13.5px;color:#e8dcc0;}
.d-wait b{color:#e3b341;}
.d-wait code{font-family:ui-monospace,SFMono-Regular,monospace;font-size:12.5px;
background:#0d1017;border:1px solid var(--d-line);border-radius:4px;padding:1px 6px;}
.d-wait.pulse{animation:d-pulse .6s ease-out 1;}
@keyframes d-pulse{from{background:#5a3f10;}to{background:#2a1f0c;}}
/* No sustained flashing anywhere, and none at all for a reader who has asked
   the OS not to move things. The strip still appears; it just appears. */
@media (prefers-reduced-motion:reduce){.d-wait.pulse{animation:none;}}
/* Two lines, then fade. The full text is the first timeline entry. */
.d-clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
overflow:hidden;margin:3px 0 0;color:#c4cad8;font-size:13.5px;max-width:none;}
/* The contract the worklog below is measured against, so it gets the accent
   rather than the neutral card outline every other block uses — it is not just
   another card. */
.d-plan{border-left:2px solid var(--d-accent);background:linear-gradient(
90deg,#58a6ff0d,transparent 60%);padding:10px 0 12px 16px;margin:26px 0 4px;
border-radius:0 6px 6px 0;}
.d-plan .d-eyebrow{margin-top:12px;color:var(--d-mut);}
.d-plan .d-eyebrow:first-child{margin-top:0;}
.d-clamp2{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
overflow:hidden;margin:2px 0 0;max-width:78ch;color:#c9cfdd;}
.d-clamp3{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;
overflow:hidden;margin:2px 0 0;max-width:78ch;color:#c9cfdd;}
.d-sec{font-size:11px;text-transform:uppercase;letter-spacing:.09em;color:var(--d-mut);
margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--d-line);}
.d-tl{position:relative;padding-left:22px;}
.d-tl:before{content:'';position:absolute;left:4px;top:6px;bottom:4px;width:1px;
background:#2b3040;}
.d-ev{position:relative;margin-bottom:18px;}
.d-ev:before{content:'';position:absolute;left:-22px;top:6px;width:8px;height:8px;
border-radius:50%;border:1.5px solid #4a5265;background:var(--d-bg);}
.d-ev.big:before{left:-24px;top:4px;width:12px;height:12px;border:none;
background:var(--d-accent);}
/* Corrections: amber ring and an amber rule down the entry, so a scan of the
   timeline finds the moments the project changed direction. */
.d-ev.fix:before{background:var(--d-warn);border-color:var(--d-warn);}
.d-ev.fix{border-left:2px solid #d2992255;margin-left:-14px;padding-left:12px;}
.d-ev p{max-width:68ch;margin:4px 0;color:#c4cad8;}
.d-links{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin-top:6px;}
/* The gallery earns real size; the 104px inline thumbs in the timeline do not.
   Same white plate, since matplotlib output is white and should read as
   intentional rather than as a hole punched in a dark page. */
.d-figs{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));
gap:12px;margin-top:0;}
.d-figs img{width:100%;padding:6px;box-sizing:border-box;
transition:border-color .15s ease,transform .15s ease;}
.d-figs img:hover{border-color:var(--d-accent);transform:translateY(-2px);}
.d-links img{width:104px;height:auto;background:#ffffffeb;border-radius:4px;
border:1px solid var(--d-line);display:block;}
.d-grid{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));}
.d-card{background:var(--d-card);border:1px solid var(--d-line);border-radius:6px;
padding:9px 12px;font-size:13px;}
.d-empty{color:var(--d-dim);font-style:italic;}
a{color:#79b8ff;}
table{border-collapse:collapse;font-size:13px;width:100%;}
td,th{border-bottom:1px solid var(--d-line);padding:5px 8px;text-align:left;}
.doc-trigger{cursor:pointer;}
/* Document mode for the shared overlay. main.css centres a bare <img>; a report
   instead needs a bounded, scrollable panel, so the two modes are switched by a
   class on the overlay rather than given separate overlays — one close path. */
.lightbox-doc{display:none;}
/* Child combinator, not descendant. The overlay's own figure <img> is a direct
   child of #lightbox; every image inside a rendered document is nested in
   .lightbox-doc. A descendant selector here hid the figures embedded in
   REPORT.md — which are the whole point of inlining them next to each finding. */
.lightbox-overlay.mode-doc>img{display:none;}
.lightbox-overlay.mode-doc .lightbox-doc{display:block;text-align:left;
background:var(--d-panel);border:1px solid var(--d-line);border-radius:8px;
width:min(880px,calc(100vw - 56px));max-height:calc(100vh - 96px);
overflow-y:auto;overscroll-behavior:contain;padding:24px 32px;}
.lightbox-doc>:first-child{margin-top:0;}
.lightbox-doc h1{font-size:1.5rem;}.lightbox-doc h2{font-size:1.22rem;}
.lightbox-doc h3{font-size:1.05rem;}.lightbox-doc h4{font-size:.95rem;}
.lightbox-doc h1,.lightbox-doc h2{border-bottom:1px solid var(--d-line);
padding-bottom:6px;}
.lightbox-doc h1,.lightbox-doc h2,.lightbox-doc h3,.lightbox-doc h4{
margin:26px 0 10px;line-height:1.3;}
.lightbox-doc p,.lightbox-doc li{color:#c9cfdd;}
.lightbox-doc li{margin:3px 0;}
.lightbox-doc code{background:#0f1117;border:1px solid var(--d-line);
border-radius:4px;padding:1px 5px;font-size:.88em;
font-family:ui-monospace,SFMono-Regular,monospace;}
.lightbox-doc pre{background:#0f1117;border:1px solid var(--d-line);
border-radius:6px;padding:12px 14px;overflow-x:auto;}
.lightbox-doc pre code{background:none;border:none;padding:0;}
.lightbox-doc blockquote{margin:12px 0;padding:2px 14px;color:var(--d-mut);
border-left:3px solid var(--d-line);}
.lightbox-doc table{display:block;overflow-x:auto;white-space:nowrap;}
.lightbox-doc th{color:var(--d-fg);font-weight:650;}
.lightbox-doc img{max-width:100%;height:auto;}
.lightbox-doc hr{border:none;border-top:1px solid var(--d-line);margin:20px 0;}
.lightbox-doc .doc-error{color:var(--d-bad);}
"""

# The page ships in two halves because it has two transports and only one of
# them can poll.
#
# REL_JS always runs. Every timestamp renders client-side from `data-epoch`
# (see the design doc), so without it the readouts are empty elements — which
# is why the snapshot gets this half rather than no script at all. It is also
# what keeps a *stale* snapshot honest: `relTimes` measures age against the
# reader's clock, not the render time, so an abandoned snapshot visibly ages
# green -> amber -> grey instead of freezing on a green dot.
REL_JS = """
var R=document.getElementById('root'),tag=null;
function rel(s){var d=Math.max(0,Date.now()/1000-s);
if(d<60)return Math.floor(d)+'s ago';if(d<3600)return Math.floor(d/60)+'m ago';
if(d<86400)return Math.floor(d/3600)+'h ago';return Math.floor(d/86400)+'d ago';}
function since(s){var d=Math.max(0,Date.now()/1000-s);
if(d<3600)return Math.floor(d/60)+'m';if(d<86400)return Math.floor(d/3600)+'h '+
Math.floor((d%3600)/60)+'m';return Math.floor(d/86400)+'d';}
function relTimes(){
var n=document.querySelectorAll('[data-epoch]');
for(var i=0;i<n.length;i++){var el=n[i],s=parseFloat(el.dataset.epoch);
if(!s){el.textContent='--';continue;}
var age=Date.now()/1000-s;
el.textContent=(el.dataset.mode==='since')?since(s):rel(s);
if(el.dataset.mode!=='since')
el.className=age<600?'live':(age<3600?'idle':'cold');}}
setInterval(relTimes,15000);relTimes();
"""

# Everything about "the agent needs you" that cannot be server-rendered, for the
# same reason relative times cannot be: a 304 freezes whatever the server wrote,
# and this is the one readout whose whole job is to be current. The server emits
# `#d-state` inside #root carrying `data-state` and `data-since`; `mark()` reads
# them after every swap and drives four things off them.
#
# Two channels reach a reader who is not looking at the page — the title marker
# and the favicon — and they are the only two a browser gives a foreground tab.
# A closed tab gets nothing without a service worker and a push service, which a
# stdlib server inside a pod cannot be.
#
# `#d-detail` is agent-authored text, so it is *not* interpolated here. The
# server renders it through the same `inline_md` -> `e()` path as the worklog and
# this copies the resulting node's HTML verbatim; the escaping decision stays in
# one place, in Python, where it is tested.
#
# The `(state, since)` pair is what makes a *transition* distinguishable from a
# re-render. Without it the strip would re-pulse every 4s, which is a flashing
# banner rather than a signal.
STATE_JS = """
(function(){
var W=document.getElementById('d-wait'),
F=document.getElementById('d-favicon'),BASE=document.title,last=null;
var MARK={waiting:'\\u25cf ',turn_ended:'\\u2713 '};
function icon(c){return 'data:image/svg+xml,'+encodeURIComponent(
'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'+
'<circle cx="8" cy="8" r="7" fill="'+c+'"/></svg>');}
var ICON={waiting:icon('#d29922'),turn_ended:icon('#3fb950'),'':icon('#30363d')};
function mark(){
var c=document.getElementById('d-state'),d=document.getElementById('d-detail'),
s=c?(c.dataset.state||''):'',key=s+'|'+(c?c.dataset.since:'');
document.title=(MARK[s]||'')+BASE;
if(F)F.href=ICON[s]||ICON[''];
if(key===last)return;
if(s==='waiting'&&W){
W.innerHTML='<b>The agent is waiting for you.</b> '+(d?d.innerHTML:'');
W.hidden=false;
W.classList.remove('pulse');void W.offsetWidth;W.classList.add('pulse');}
else if(W){W.hidden=true;W.innerHTML='';}
last=key;}
window.dashMark=mark;mark();})();
"""

# POLL_JS is emitted **only in live mode**, and both of its outer statements are
# why: the trailing-slash redirect and the `fetch` are each actively wrong on a
# snapshot.
#
# - The redirect exists so relative asset URLs resolve under `/proxy/<port>`.
#   A snapshot is served at `<prefix>files/<rel>/dashboard.html`, which does not
#   end in `/`, so this line would navigate the page to `dashboard.html/` — a
#   Jupyter 404. The page would destroy itself on load.
# - `files/` responses carry `Content-Security-Policy: sandbox allow-scripts`
#   with no `allow-same-origin` (measured against the live server), so the
#   document has an opaque origin and `fetch` cannot send the hub cookie. The
#   poll could only ever fail, silently, forever.
#
# **A hidden tab still fetches**, at 15s instead of 4s. It used to skip the
# fetch entirely, which is cheaper and wrong: a backgrounded tab is exactly the
# tab that needs to learn the agent is blocked on a permission prompt, and one
# that never fetches can never learn anything — it has only the title and the
# favicon to speak through, and both are painted from the response. The cost is
# small enough to check rather than argue about: a 304 still runs a full
# `scan()` at 6.8ms measured, so 15s hidden is ~1.6s of CPU per hour per tab,
# less than a *visible* tab costs today.
#
# The single `timer` handle is not decoration. `tick` schedules the next tick,
# and the visibilitychange listener calls `tick` directly, so every return to
# the tab used to start a second concurrent chain that never ended — harmless
# while hidden ticks were free, a compounding multiplier on real requests now.
POLL_JS = """
if(!location.pathname.endsWith('/'))location.replace(location.pathname+'/');
var timer=0;
function tick(){
var h=tag?{'If-None-Match':tag}:{};
fetch('.',{headers:h}).then(function(r){
if(r.status!==200)return null;tag=r.headers.get('ETag');return r.text();})
.then(function(t){if(!t)return;
var open=[],ds=R.querySelectorAll('details[open]');
for(var i=0;i<ds.length;i++)if(ds[i].id)open.push(ds[i].id);
var doc=new DOMParser().parseFromString(t,'text/html');
var next=doc.getElementById('root');if(!next)return;
R.innerHTML=next.innerHTML;
for(var j=0;j<open.length;j++){var d=R.querySelector('#'+CSS.escape(open[j]));
if(d)d.open=true;}
relTimes();dashMark();}).catch(function(){});
clearTimeout(timer);timer=setTimeout(tick,document.hidden?15000:4000);}
document.addEventListener('visibilitychange',function(){
if(document.visibilityState==='visible')tick();});
timer=setTimeout(tick,4000);
"""

# The overlay is a sibling of #root, and every listener is delegated on document,
# so a trigger stays clickable after the 4s poll swaps #root's innerHTML — the
# trigger elements are replaced, but the handler and the overlay are not.
#
# Two modes share one overlay: an <img> for figures, and a scrollable panel for
# markdown fetched from `/_doc/`. Sharing it means Esc, the backdrop and the ×
# have exactly one implementation. An <iframe> was the obvious alternative for the
# document mode and was rejected: keystrokes inside an iframe never reach the
# parent document, so Esc would silently stop closing the popup.
LIGHTBOX_JS = """
(function(){var L=document.getElementById('lightbox');if(!L)return;
var I=L.querySelector('img'),D=L.querySelector('.lightbox-doc'),seq=0;
function close(){L.classList.remove('active','mode-doc');}
function near(t,sel){return t&&t.closest?t.closest(sel):null;}
function note(cls,msg){D.innerHTML='<p class="'+cls+'"></p>';
D.firstChild.textContent=msg;}
document.addEventListener('click',function(e){
var fig=near(e.target,'.lightbox-trigger');
if(fig){I.src=fig.getAttribute('src');I.alt=fig.getAttribute('alt')||'';
L.classList.remove('mode-doc');L.classList.add('active');return;}
var doc=near(e.target,'.doc-trigger');
if(doc&&e.button===0&&!e.metaKey&&!e.ctrlKey&&!e.shiftKey&&!e.altKey){
e.preventDefault();
var path=doc.getAttribute('data-doc'),n=++seq;
note('d-empty','loading\\u2026');
L.classList.add('active','mode-doc');D.scrollTop=0;
fetch('_doc/'+path.split('/').map(encodeURIComponent).join('/'))
.then(function(r){return r.ok?r.text():r.status;})
.then(function(v){if(n!==seq)return;
if(typeof v==='number'){note('doc-error','could not render '+path+' ('+v+')');return;}
D.innerHTML=v;D.scrollTop=0;})
.catch(function(){if(n!==seq)return;
// fetch rejected outright: nothing is serving this page, which is what a
// written-out dashboard.html opened from disk looks like. Follow the real
// href instead of leaving an empty overlay open.
close();location.href=doc.getAttribute('href');});
return;}
if(e.target===L||near(e.target,'.lightbox-close'))close();});
document.addEventListener('keydown',function(e){
if(e.key==='Escape'||e.key==='Esc')close();});})();
"""


_MD_CODE_RE = re.compile(r"`([^`\n]+)`")
_MD_BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")
_MD_ITALIC_RE = re.compile(r"\*([^*\n]+)\*")


def inline_md(value) -> str:
    """Escape, then render the three inline constructs agent prose actually uses.

    The worklog and the plan are markdown, and rendering them as flat text left
    literal ``**`` and backticks all over the page. Measured across the 72
    projects whose plan text appears inline: ``**bold**`` in 62, ``*italic*`` in
    21, ``` `code` ``` in 14. No links and no strikethrough, so neither is
    implemented — a full markdown pass belongs in the document overlay, not in a
    one-line summary.

    **Escaping happens first, always.** By the time the patterns run, any HTML in
    the source is already inert, so the only tags this can introduce are the
    three it emits. That ordering is the whole safety argument; do not reverse it.

    Code spans are stashed behind placeholders rather than split out, so a ``*``
    inside backticks still stays literal *and* emphasis can span a code span —
    ``**motif count in `bakta_annotations`**`` is real prose from two projects,
    and splitting first left the opening and closing ``**`` in different
    fragments where neither could match.
    """
    text = e(value)
    codes: list = []

    def stash(match: "re.Match") -> str:
        codes.append(match.group(1))
        return f"\x00{len(codes) - 1}\x00"

    text = _MD_CODE_RE.sub(stash, text)
    text = _MD_BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = _MD_ITALIC_RE.sub(r"<em>\1</em>", text)
    return re.sub(
        r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text
    )


def e(value) -> str:
    """Escape agent-authored text. This is a trust boundary — the agent writes
    the worklog prose, the link labels and the filenames."""
    return _html.escape(str(value), quote=True)


def render_markdown(text: str) -> str:
    """Markdown to an HTML **fragment**, for the document overlay.

    Two tiers, because this file is otherwise pure stdlib and a dashboard that
    refuses to start without a markdown library would be a worse tool. The popup
    always works; only its typography depends on an optional import:

    1. ``mistune`` — tables and strikethrough, the two things reports actually use.
       Declared in the PEP 723 header, so ``uv run`` always gets it, and present
       on the BERDL image, so the pod's bare ``python3`` does too.
    2. Not installed: the escaped source in a ``<pre>``. Readable, unstyled, and
       still a working popup.

    A third tier using ``markdown`` was removed: reaching it required an
    environment with that library but *not* mistune, running bare ``python3``,
    which is none of the three we actually run in.

    **Raw HTML is escaped in every tier.** Markdown here is agent-authored, the
    same trust boundary ``e()`` exists for, and this page is served under the hub's
    own origin — a ``<script>`` in a REPORT.md would run with the reader's Jupyter
    session cookies. mistune is asked for ``escape=True``; the fallback escapes
    the source outright.
    """
    try:
        import mistune

        return mistune.create_markdown(
            escape=True, plugins=["table", "strikethrough"]
        )(text)
    except ImportError:
        pass
    return f"<pre>{e(text)}</pre>"


def load_css(repo_root: Path) -> str:
    """Inline the observatory stylesheet so the in-progress dashboard matches the
    site a project graduates into. It has zero ``url()`` references, so it is
    self-contained. Missing is survivable: unstyled but fully readable."""
    try:
        return (repo_root / "ui" / "app" / "static" / "css" / "main.css").read_text(
            encoding="utf-8"
        )
    except OSError:
        return ""


def _human(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return "%d %s" % (size, unit) if unit == "B" else "%.1f %s" % (size, unit)
        size /= 1024.0
    return str(size)


def _approval_chip(approval: dict) -> str:
    state = approval.get("state")
    if state == "na":
        return ""
    if state == "approved":
        who = e(approval.get("by", ""))
        when = e((approval.get("at", "") or "")[:10])
        # `beril approve` records HOW the approval happened. A human at a TTY
        # confirming it and an agent relaying one on their behalf are different
        # kinds of evidence, and rendering them identically would overstate the
        # weaker one — the failure this page exists to avoid.
        if approval.get("via") == "agent-relayed":
            return (
                f'<span class="d-chip warn" title="{who} — recorded by the agent '
                f'on the author\'s behalf, not confirmed at a terminal">'
                f"plan approved (relayed) {when}</span>"
            )
        return f'<span class="d-chip ok" title="{who}">plan approved &#10003; {when}</span>'
    if state == "stale":
        return '<span class="d-chip bad">approval stale &#10007;</span>'
    return '<span class="d-chip bad">plan not approved &#10007;</span>'


def _rail(stage: str) -> str:
    """The stage rail, labelled for humans rather than with the raw enum.

    ``analysis`` is the one status whose name says the opposite of what it
    means: analysis *happens* during ``active``, and ``analysis`` means the
    report has been drafted. Showing the raw value on a page whose whole job is
    telling you where the agent is would mislead at exactly the wrong moment.

    Labels are the wording ``/synthesize`` and ``/submit`` already write into
    each project's README. The raw status stays on the header badge and in each
    ``title``, so nothing that reads ``beril.yaml`` is hidden. A rename of the
    enum itself (``analysis`` → ``synthesized``) is planned as its own change.
    """
    current = STAGES.index(stage)
    items = []
    for index, name in enumerate(STAGES):
        state = "done" if index < current else ("current" if index == current else "future")
        aria = ' aria-current="step"' if state == "current" else ""
        items.append(
            f'<li data-state="{state}"{aria} title="beril.yaml status: {name}">'
            f"<i></i>{STAGE_LABELS[name]}</li>"
        )
    return '<ol class="d-rail" aria-live="polite">' + "".join(items) + "</ol>"


def _open_href(routes: "JupyterRoutes | None", path: str) -> str:
    """Where a document link points: a Jupyter viewer that renders it when one
    exists and we can reach it, otherwise the relative file the dashboard serves
    itself — today's behaviour, and the only thing that works off-cluster."""
    if routes is not None:
        url = routes.open_url(path)
        if url:
            return url
    return path


def _is_doc(path: str) -> bool:
    """Whether this dashboard renders ``path`` itself, in the overlay."""
    return Path(path).suffix.lower() in MARKDOWN_EXT


def _doc_trigger(path: str, label: str, css_class: str = "") -> str:
    """An ``<a>`` that opens ``path`` in the document overlay.

    **Every anchor that can point at a markdown file must come from here.** Two
    places emit one — the worklog chips and the Documents cards — and they did not
    share this logic when the overlay was added, so the cards kept their
    ``target="_blank"`` and went on opening raw source in a new tab while the
    chips opened the popup. Same rendering decision in two spots drifted the first
    time it changed; one function is the fix.

    No ``target="_blank"``: not leaving the page is the entire point. The ``href``
    stays real so middle-click still opens the source and the no-server fallback in
    LIGHTBOX_JS has somewhere to go.
    """
    cls = f"{css_class} doc-trigger".strip()
    return f'<a class="{cls}" href="{e(path)}" data-doc="{e(path)}">{label}</a>'


def _link_html(link: Link, routes: "JupyterRoutes | None") -> str:
    label = e(link.label)
    count = f" &#215;{link.count}" if link.count > 1 else ""
    if not link.exists:
        return f'<span class="d-chip bad"><s>{label}</s> missing</span>'
    if Path(link.path).suffix.lower() in FIGURE_EXT:
        # A figure opens in the lightbox, not a new tab. The overlay lives
        # outside #root and the handler is delegated on document, so both
        # survive the 4s poll that replaces #root's innerHTML.
        badge = f'<span class="d-chip">&#215;{link.count}</span>' if link.count > 1 else ""
        return (
            f'<img class="lightbox-trigger" src="{e(link.path)}" alt="{label}">{badge}'
        )
    if _is_doc(link.path):
        return _doc_trigger(link.path, f"{label}{count}", "d-chip")
    href = e(_open_href(routes, link.path))
    return f'<a class="d-chip" href="{href}" target="_blank">{label}{count}</a>'


def _entry_html(entry: Entry, routes: "JupyterRoutes | None") -> str:
    big = " big" if entry.new_status else ""
    # Corrections are the only record of why a project was not a straight line,
    # and they used to render identically to "ran notebook 3". Labelled as well
    # as coloured — hue alone is not a signal everyone can read.
    if entry.correction:
        big += " fix"
    badge = (
        f'<span class="d-chip now">{e(entry.new_status)}</span>' if entry.new_status else ""
    )
    if entry.correction:
        badge += '<span class="d-chip warn">correction</span>'
    prose = f"<p>{inline_md(entry.prose)}</p>" if entry.prose else ""
    links = (
        '<div class="d-links">'
        + "".join(_link_html(link, routes) for link in entry.links)
        + "</div>"
        if entry.links
        else ""
    )
    return (
        f'<div class="d-ev{big}"><div class="d-row"><b>{inline_md(entry.title)}</b>{badge}'
        f'<span class="d-chip">{e(entry.date)}</span></div>{prose}{links}</div>'
    )


def _notebook_html(notebook: Notebook, routes: "JupyterRoutes | None") -> str:
    if notebook.mtime == 0.0:
        detail = '<span class="d-empty">unreadable — being written?</span>'
    else:
        detail = (
            f"{notebook.cells} cells &middot; {notebook.with_output} with output "
            f'&middot; <span data-epoch="{notebook.mtime}"></span>'
        )
    flags = ""
    if notebook.errors:
        plural = "s" if notebook.errors > 1 else ""
        flags += f'<span class="d-chip bad">&#9888; {notebook.errors} error{plural}</span>'
    elif notebook.cells and not notebook.with_output:
        flags += '<span class="d-chip warn">&#9888; no outputs</span>'
    href = e(_open_href(routes, notebook.path))
    # A second link, only inside Jupyter: nbconvert renders the saved outputs as
    # static HTML without booting a kernel, which is the fast way to read a
    # notebook you do not intend to run. Gated on the suffix because this route
    # answers a blank 200 for anything that is not a notebook.
    preview = ""
    if routes is not None and notebook.path.lower().endswith(".ipynb"):
        preview = (
            f'<a class="d-chip" href="{e(routes.nbconvert_url(notebook.path))}" '
            'target="_blank" title="Static HTML render of the saved outputs — '
            'no kernel">preview</a>'
        )
    return (
        f'<div class="d-card"><div class="d-row"><a href="{href}" '
        f'target="_blank">{e(notebook.name)}</a>{flags}{preview}</div>{detail}</div>'
    )


def _plan_html(state: State) -> str:
    """The contract, above the log of what happened against it.

    Deliberately outside the sticky header: this is orientation you read once,
    not state worth pinning, and the header is kept short on purpose. Clamped —
    the point is to anchor the entries below, not to reproduce the plan.
    """
    plan = state.plan or {}
    question = plan.get("question", "")
    hypothesis = plan.get("hypothesis", "")
    outcomes = plan.get("outcomes", "")
    if not (question or hypothesis or outcomes):
        return ""

    doc = next((d for d in state.docs if d.name == "RESEARCH_PLAN.md"), None)
    link = (
        f'<a class="doc-trigger d-chip" data-doc="{e(doc.path)}" '
        f'href="{e(doc.path)}">RESEARCH_PLAN.md</a>'
        if doc
        else ""
    )

    # Counts, never a mapping: plan section numbers do not correspond to
    # filenames on disk (measured — see plan_summary), so a per-notebook
    # done/not-done would be confidently wrong.
    # Order matters. With the plan count first — "3 planned · 4 written" — the
    # two numbers sit in an n/m relationship and read as a fraction, so a
    # perfectly correct tally looks like an error the moment an unplanned
    # notebook exists. And one always does: /berdl_start Phase A mandates an
    # exploration notebook that the RESEARCH_PLAN template never lists. State on
    # disk leads; the plan follows as a labelled reference, not a denominator.
    planned = plan.get("planned_notebooks") or 0
    ran = sum(1 for nb in state.notebooks if nb.with_output)
    tally = ""
    if planned or state.notebooks:
        bits = [f"{len(state.notebooks)} written", f"{ran} executed"]
        if planned:
            bits.append(f"plan lists {planned}")
        tally = f'<span class="d-chip">{" &middot; ".join(bits)}</span>'

    blocks = []
    if question:
        blocks.append(
            f'<span class="d-eyebrow">research question</span>'
            f'<p class="d-clamp3">{inline_md(question)}</p>'
        )
    if hypothesis:
        blocks.append(
            f'<span class="d-eyebrow">hypothesis</span>'
            f'<p class="d-clamp3">{inline_md(hypothesis)}</p>'
        )
    if outcomes:
        blocks.append(
            f'<span class="d-eyebrow">what would settle it</span>'
            f'<p class="d-clamp2">{inline_md(outcomes)}</p>'
        )
    return (
        '<section class="d-plan">' + "".join(blocks)
        + f'<div class="d-links">{tally}{link}</div></section>'
    )


def _artifacts_html(state: State) -> str:
    blocks = []
    if state.docs:
        cards = []
        for doc in state.docs:
            chip = ""
            if doc.chip == "current":
                chip = '<span class="d-chip ok">current &#10003;</span>'
            elif doc.chip == "stale":
                chip = '<span class="d-chip bad">stale &#10007;</span>'
            # These are RESEARCH_PLAN.md / REPORT.md / REVIEW_N.md, so in practice
            # always the overlay; the else branch is for a non-markdown document
            # this section ever learns to list.
            if _is_doc(doc.path):
                anchor = _doc_trigger(doc.path, e(doc.name))
            else:
                anchor = (
                    f'<a href="{e(_open_href(state.routes, doc.path))}" '
                    f'target="_blank">{e(doc.name)}</a>'
                )
            cards.append(
                f'<div class="d-card"><div class="d-row">{anchor}{chip}</div></div>'
            )
        blocks.append(
            '<h3 class="d-sec">Documents</h3><div class="d-grid">' + "".join(cards) + "</div>"
        )

    if state.notebooks:
        blocks.append(
            f'<h3 class="d-sec">Notebooks ({len(state.notebooks)})</h3>'
            '<div class="d-grid">'
            + "".join(_notebook_html(nb, state.routes) for nb in state.notebooks)
            + "</div>"
        )

    if state.figures:
        tiles = "".join(
            f'<img class="lightbox-trigger" src="{e(f.path)}" alt="{e(f.name)}" '
            'loading="lazy">'
            for f in state.figures
        )
        blocks.append(
            f'<h3 class="d-sec">Figures ({len(state.figures)})</h3>'
            f'<div class="d-links d-figs">{tiles}</div>'
        )

    if state.data:
        rows = "".join(
            f'<tr><td><a href="{e(_open_href(state.routes, f.path))}" '
            f'target="_blank">{e(f.name)}</a></td>'
            f'<td>{_human(f.size)}</td>'
            f'<td><span data-epoch="{f.mtime}"></span></td></tr>'
            for f in state.data
        )
        blocks.append(
            f'<h3 class="d-sec">Data ({len(state.data)})</h3>'
            f"<table><tr><th>file</th><th>size</th><th>modified</th></tr>{rows}</table>"
        )

    if not blocks:
        return ""
    total = len(state.docs) + len(state.notebooks) + len(state.figures) + len(state.data)
    return f'<h2 class="d-sec">Artifacts ({total})</h2>' + "".join(blocks)


# What the chip says, and how loudly. `unknown` is deliberately the quiet one:
# it is what a `waiting` decays into, and a decayed claim should read as a
# shrug, not as an alarm.
AGENT_LABELS = {
    "waiting": "waiting for you",
    "turn_ended": "turn ended",
    "unknown": "state unknown",
}
AGENT_CHIP = {"waiting": " warn", "turn_ended": " ok", "unknown": ""}


def _agent_html(agent: dict) -> str:
    """The header chip, plus the hidden node STATE_JS lifts into the strip.

    `data-state` and `data-since` are the whole client-side contract: the title
    marker, the favicon, the strip and the notification all derive from them, so
    a 304 cannot freeze any of it into a stale claim.

    The detail is escaped here and only here. It is agent-authored — the tool
    argument the agent chose, or a question it wrote — so it runs through the
    same `inline_md` -> `e()` path as the worklog prose, which is the same trust
    boundary. STATE_JS copies the resulting node rather than building markup out
    of a string, so there is exactly one place where this text becomes HTML.
    """
    state = agent.get("state")
    if state not in AGENT_LABELS:
        return ""
    detail = agent.get("detail") or ""
    return (
        f'<span class="d-chip{AGENT_CHIP[state]}" id="d-state" data-state="{e(state)}"'
        f' data-since="{agent.get("since", 0)}">{AGENT_LABELS[state]}</span>'
        + (f'<span id="d-detail" hidden>{inline_md(detail)}</span>' if detail else "")
    )


def _setup_banner() -> str:
    """The snapshot-mode banner: what the reader is looking at, and how to fix it.

    Only rendered when ``live`` is false, because in live mode there is nothing
    to act on. The wording leads with what this *is* rather than what is missing:
    the page in front of them works, it just does not update itself, and burying
    that under an error made the earlier version read as a broken dashboard.
    """
    steps = "".join(f"<li>{inline_md(step)}</li>" for step in SETUP_STEPS)
    return (
        '<div class="d-setup"><b>Snapshot — this page does not update itself.</b> '
        "Reload to refresh it; it is rewritten every turn while a session is running. "
        "Live updates need <code>jupyter-server-proxy</code>, which this image does "
        "not ship. To switch this project — and every one after it — to a live "
        f"dashboard, once:<ol>{steps}</ol></div>"
    )


def render(state: State, css: str, live: bool = True) -> str:
    """Build the whole page. Every href/src is relative — see module docstring.

    ``live`` selects the transport, not the content: a snapshot renders exactly
    the same page, minus the poll it cannot run, plus the banner saying so.
    """
    inferred = (
        '<span class="d-chip warn">stage inferred from files</span>'
        if state.inferred
        else ""
    )
    deviations = (
        f'<span class="d-chip warn">{state.deviations} deviations</span>'
        if state.deviations
        else ""
    )

    # The newest entry, echoed above the fold. Its prose is clamped: this is a
    # summary, and the same entry sits in full at the top of the timeline a
    # scroll away. Unclamped, a long review write-up pushed the sticky header to
    # ~390px and buried the content it was supposed to sit above.
    newest = state.entries[-1] if state.entries else None
    now_card = (
        '<div class="d-now"><span class="d-eyebrow">now</span>'
        f"<b>{inline_md(newest.title)}</b>"
        + (f'<p class="d-clamp">{inline_md(newest.prose)}</p>' if newest.prose else "")
        + "</div>"
        if newest
        else ""
    )

    if state.entries:
        timeline = '<div class="d-tl">' + "".join(
            _entry_html(entry, state.routes) for entry in reversed(state.entries)
        ) + "</div>"
    else:
        timeline = (
            '<p class="d-empty">No worklog entries yet — the agent writes one per '
            "lifecycle transition and per unit of work.</p>"
        )

    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{e(state.project_id)}</title>\n"
        # Swapped by STATE_JS for a coloured dot. Declared here with the neutral
        # one so there is a <link> to retarget; a browser will not adopt one that
        # appears later in a page it has already painted.
        '<link rel="icon" id="d-favicon" href="data:,">\n'
        f"<style>{css}\n{DASH_CSS}</style>\n</head>\n<body>\n"
        # Outside #root, so the 4s poll cannot wipe it and so it does not sit
        # under the sticky header. Empty string in live mode.
        + ("" if live else _setup_banner())
        # A sibling of #root, filled by STATE_JS: it has to survive the poll to
        # pulse once on a transition rather than every 4s.
        + '<div class="d-wait" id="d-wait" role="status" hidden></div>\n'
        + '<div id="root">\n'
        '<header class="d-hd">'
        '<div class="d-row">'
        f'<span class="d-id">{e(state.project_id)}</span>'
        f'<span class="d-chip now">{e(state.stage)}</span>'
        f"{_approval_chip(state.approval)}{deviations}{inferred}"
        f"{_agent_html(state.agent)}"
        # Readouts sit inline on the identity row rather than in a band of their
        # own: it reclaims the dead space to the right and keeps the sticky
        # region short, which is the whole point of the clamp below.
        '<span class="d-read push">'
        f'<b data-epoch="{state.last_activity}"></b><i>last activity</i></span>'
        '<span class="d-read">'
        f'<b data-epoch="{state.first_activity}" data-mode="since"></b>'
        "<i>elapsed</i></span>"
        "</div>"
        f"{_rail(state.stage)}"
        f"{now_card}"
        "</header>\n"
        f"{_plan_html(state)}\n"
        f'<h2 class="d-sec">Worklog ({len(state.entries)})</h2>{timeline}\n'
        f"{_artifacts_html(state)}\n"
        "</div>\n"
        # Sibling of #root, so the 4s poll never wipes it. Reuses main.css's
        # .lightbox-* classes (already inlined above); DASH_CSS adds only the
        # document mode, which main.css has no reason to know about.
        '<div class="lightbox-overlay" id="lightbox">'
        '<button class="lightbox-close" aria-label="Close">&#215;</button>'
        '<img src="" alt="Full size figure">'
        '<div class="lightbox-doc" role="document"></div>'
        "</div>\n"
        # STATE_JS ships in both modes: a snapshot still has a title and a
        # favicon, and a snapshot written while a prompt was open should still
        # say so.
        f"<script>{REL_JS}{STATE_JS}{POLL_JS if live else ''}</script>\n"
        f"<script>{LIGHTBOX_JS}</script>\n</body>\n</html>\n"
    )


# ---------------------------------------------------------------------------
# Serving
# ---------------------------------------------------------------------------


def port_for(project_id: str) -> int:
    """Deterministic per-project port, so the URL is bookmarkable across
    restarts and two concurrent projects do not collide."""
    return 8700 + zlib.crc32(project_id.encode("utf-8")) % 100


def _jupyter_config_dirs() -> list:
    """The config dirs the *running single-user server* searches for extension
    enable files, computed with stdlib only (this module has a no-dependency
    constraint, so we cannot call ``jupyter_core.paths``).

    Mirrors Jupyter's own search order, and deliberately includes the pip
    ``--user`` location ``<userbase>/etc/jupyter`` **unconditionally**. The
    launcher may run with user-site config off while the server that actually
    loads the extension runs with it on; ``site.getuserbase()`` returns the path
    regardless of ``site.ENABLE_USER_SITE``, so we never silently omit it.
    """
    dirs = []
    # JUPYTER_CONFIG_PATH outranks the user config dir — jupyter_core/paths.py
    # calls it "highest priority is explicit environment variable".
    for entry in os.environ.get("JUPYTER_CONFIG_PATH", "").split(os.pathsep):
        if entry:
            dirs.append(Path(entry))
    env_cfg = os.environ.get("JUPYTER_CONFIG_DIR")
    dirs.append(Path(env_cfg) if env_cfg else Path.home() / ".jupyter")
    dirs.append(Path(site.getuserbase()) / "etc" / "jupyter")  # ~/.local/etc/jupyter
    dirs.append(Path(sys.prefix) / "etc" / "jupyter")  # e.g. /opt/conda/etc/jupyter
    dirs.append(Path("/usr/local/etc/jupyter"))
    dirs.append(Path("/etc/jupyter"))
    return dirs


def proxy_enabled() -> bool:
    """True when the ``/user/<name>/proxy/<port>/`` URL will actually resolve.

    Replicates jupyter_server's own config merge rather than asking the CLI.
    Within a directory the ``jupyter_server_config.d/*.json`` drop-ins are read
    in sorted order and then ``jupyter_server_config.json``, last writer
    winning; the first directory with an opinion decides.

    Three things make the obvious implementations wrong, each reproduced against
    a real jupyter-server-proxy install:

    - **Asking the CLI.** ``jupyter server extension list`` builds its config
      manager from a fixed three-tuple that structurally cannot include
      ``~/.local/etc/jupyter``, so a ``pip --user`` install reads as "not
      enabled" while the running server has it loaded.
    - **Reading only the shipped drop-in.** ``jupyter server extension disable``
      writes a *second* file, ``jupyter_server_proxy.json`` (underscore),
      holding ``false`` into the same directory. ``_`` sorts after ``-``, so it
      wins the real merge — a probe that reads only the hyphenated file reports
      enabled and then prints a URL that 404s.
    - **Hardcoding the filename.** jupyter-server-proxy < 4.0 ships its drop-in
      under a different name entirely, so a fixed name finds nothing on a 3.x
      image.

    Globbing the whole directory and honouring last-writer-wins handles all
    three. Deliberately no import check: ``importlib.util.find_spec`` resolves
    against the *launcher's* ``sys.path``, which misses a ``--user`` install
    whenever ``site.ENABLE_USER_SITE`` is false — true inside any venv, and this
    repo ships one. Gating a filesystem check behind an environment-dependent
    one would reintroduce the bug this function exists to fix.
    """
    for cfg_dir in _jupyter_config_dirs():
        verdict = None
        files = sorted((cfg_dir / "jupyter_server_config.d").glob("*.json"))
        files.append(cfg_dir / "jupyter_server_config.json")
        for path in files:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                verdict = bool(
                    data["ServerApp"]["jpserver_extensions"]["jupyter_server_proxy"]
                )
            except (OSError, ValueError, KeyError, TypeError):
                continue
        if verdict is not None:
            return verdict
    return False


def public_url(port: int) -> str:
    """The URL to hand the operator.

    ``JUPYTERHUB_SERVICE_PREFIX`` is set by the Spawner to exactly
    ``/user/<name>/`` and covers named servers, which ``JUPYTERHUB_USER`` does
    not. Unset means we are on a local machine.
    """
    prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX")
    return f"{HUB}{prefix}proxy/{port}/" if prefix else f"http://127.0.0.1:{port}/"


def jupyter_routes(project: Path) -> "JupyterRoutes | None":
    """URL builder for opening this project's files in Jupyter, or ``None``.

    ``<rel>`` is the project directory relative to the running server's
    ``root_dir``. On this image ``root_dir`` is exposed verbatim as
    ``$JUPYTER_SERVER_ROOT`` (it happens to be ``$HOME``, but the repo is nested
    well below it, so the variable — not an assumption — is what makes this
    work), and a stdlib ``os.path.relpath`` against it yields exactly the path
    component Jupyter URLs expect.

    ``None`` — every link falls back to the relative file the dashboard serves
    itself — whenever there is no Jupyter to reach: off-cluster (prefix unset),
    the server root is unknown, or the project lives outside that root, which no
    Jupyter URL can address.
    """
    prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX")
    root = os.environ.get("JUPYTER_SERVER_ROOT")
    if not prefix or not root:
        return None
    try:
        rel = os.path.relpath(project.resolve(), Path(root).resolve())
    except (OSError, ValueError):  # e.g. different drive on Windows
        return None
    if os.path.isabs(rel) or rel == os.pardir or rel.startswith(os.pardir + os.sep):
        return None  # outside root_dir — no Jupyter URL can address it
    return JupyterRoutes(f"{HUB}{prefix}", "" if rel == "." else rel.replace(os.sep, "/"))


def snapshot_url(project: Path) -> str:
    """Where to open ``dashboard.html``, as a URL the reader can actually click.

    Jupyter's ``files/`` route resolves against the server's ``root_dir``, so the
    path after it must be **root-relative**. Interpolating the absolute path
    instead produces ``files//home/<user>/...``, which Jupyter resolves to
    ``<root_dir>/home/<user>/...`` and answers 404 — verified against the running
    server, which returns 200 for the relative form and 404 for the absolute one.
    That was the earlier behaviour, and it broke the fallback in exactly the
    situation where the fallback is the only thing the user has.

    Reuses ``jupyter_routes`` rather than recomputing the relative path: it
    already handles the root-relative case and the outside-root case, and a
    second implementation is a second thing to get wrong.
    """
    snapshot = project / "dashboard.html"
    routes = jupyter_routes(project)
    if routes is None:  # off-cluster, or outside root_dir — no URL can reach it
        return str(snapshot)
    rel = f"{routes.rel}/dashboard.html" if routes.rel else "dashboard.html"
    return f"{routes.base}files/{quote(rel)}"


def in_jupyterhub() -> bool:
    return bool(os.environ.get("JUPYTERHUB_SERVICE_PREFIX"))


def can_serve_live() -> bool:
    """Live mode needs the proxy only *inside* JupyterHub.

    On a local machine ``http://127.0.0.1:<port>/`` is directly reachable, so
    requiring jupyter-server-proxy there would refuse to run for no reason.
    """
    return proxy_enabled() if in_jupyterhub() else True


def _handler_factory(project: Path, css: str):
    # Imported here, not at module scope: http.server costs ~30ms to import
    # (measured), and the statusline imports this module purely for
    # resolve_stage/port_for on every render. Serving pays it; nobody else does.
    from http.server import SimpleHTTPRequestHandler

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(project), **kwargs)

        def log_message(self, fmt, *args):
            """Silent by design. jupyter-server-proxy copies every request
            header to the backend, including the hub session token."""

        def _is_index(self) -> bool:
            return self.path.split("?")[0] in ("/", "/index.html")

        def _doc_target(self) -> "Path | None":
            """The markdown file a ``/_doc/`` request names, or ``None``.

            ``translate_path`` is ``SimpleHTTPRequestHandler``'s own sanitiser —
            it unquotes, normalises, and drops every ``..`` or separator-bearing
            segment, so its result cannot climb out of ``directory``. Reusing it
            is deliberate: a hand-rolled check here would be a second, weaker
            implementation of the guard that already protects every other path.

            It compares strings, though, so it cannot see a symlink inside the
            project pointing outside it. ``resolve()`` plus ``is_relative_to``
            closes that, and the suffix check keeps this route from becoming a
            general file reader.
            """
            raw = self.path.split("?")[0].split("#")[0]
            rest = raw[len(DOC_ROUTE) :]
            if not rest:
                return None
            try:
                resolved = Path(self.translate_path("/" + rest)).resolve(strict=True)
            except OSError:
                return None
            if not resolved.is_relative_to(Path(self.directory).resolve()):
                return None
            if not resolved.is_file() or resolved.suffix.lower() not in MARKDOWN_EXT:
                return None
            return resolved

        def _doc(self, body: bool):
            target = self._doc_target()
            if target is None:
                return self.send_error(404, "not a document in this project")
            try:
                text = target.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                return self.send_error(404, "document could not be read")
            payload = render_markdown(text).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if body:
                self.wfile.write(payload)

        def do_GET(self):  # noqa: N802
            if self._is_index():
                return self._page(body=True)
            if self.path.startswith(DOC_ROUTE):
                return self._doc(body=True)
            return super().do_GET()

        def do_HEAD(self):  # noqa: N802
            if self._is_index():
                return self._page(body=False)
            if self.path.startswith(DOC_ROUTE):
                return self._doc(body=False)
            return super().do_HEAD()

        def _page(self, body: bool):
            state = scan(project)
            if self.headers.get("If-None-Match") == state.etag:
                self.send_response(304)
                self.end_headers()
                return
            payload = render(state, css).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("ETag", state.etag)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if body:
                self.wfile.write(payload)

    def _reject(self):
        self.send_error(405, "read-only dashboard")

    for verb in ("POST", "PUT", "DELETE", "PATCH", "OPTIONS"):
        setattr(Handler, "do_" + verb, _reject)
    return Handler


def serve(project: Path, port: int, css: str) -> None:
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", port), _handler_factory(project, css))
    print(f"Dashboard: {public_url(port)}", flush=True)
    server.serve_forever()


def _write_snapshot(project: Path, css: str, live: bool = False) -> Path:
    snapshot = project / "dashboard.html"
    # Rendered to a sibling and renamed, because the banner tells the reader to
    # reload and the status line rewrites this file every turn — so a reload
    # landing mid-write is the *expected* interleaving, not a rare one. write_text
    # truncates first, which would serve half a page. os.replace is atomic on
    # POSIX, so a reader sees either the old snapshot or the new one. Two sessions
    # on one project resolve the same way: last writer wins, whole file.
    staging = snapshot.with_name("dashboard.html.tmp")
    staging.write_text(render(scan(project), css, live=live), encoding="utf-8")
    os.replace(staging, snapshot)
    return snapshot


def jupyter_python() -> "str | None":
    """The interpreter the Jupyter server runs on, or ``None`` if it can't be found.

    **Not `sys.executable`.** The extension has to be importable by the process
    serving `/proxy/<port>/`, which on this image is `/opt/conda/bin/python3`. Any
    other interpreter installs it somewhere that server never reads, and the
    failure is not always loud: inside a venv built with system site-packages,
    `pip install --user` is *permitted* and drops the module into
    `~/.local/lib/python3.<venv-version>/`, while `jupyter server extension enable
    --user` still writes the drop-in into `~/.local/etc/jupyter/`. `proxy_enabled()`
    then reads True, the dashboard goes live, and every URL 404s — the exact state
    the probe exists to prevent.

    Derived from the `jupyter` on PATH, since that is the same resolution the user
    performs when they start their server. Reading its shebang beats guessing:
    `sys.base_prefix` is wrong under uv, whose base is a managed CPython rather
    than the conda prefix.
    """
    launcher = shutil.which("jupyter")
    if launcher is None:
        return None
    try:
        first = Path(launcher).read_text(errors="replace").split("\n", 1)[0]
    except OSError:
        return None
    if not first.startswith("#!"):
        return None  # a binary or wrapper, not a script we can read an interpreter from
    for token in first[2:].split():
        name = Path(token).name
        if not name.startswith("python"):
            continue  # skips /usr/bin/env in `#!/usr/bin/env python3`
        return token if Path(token).exists() else shutil.which(name)
    return None


def _print_snapshot_fallback(project: Path) -> None:
    """The console half of the snapshot banner, for whoever ran this by hand."""
    print("Snapshot written — this page does not update itself; reload to refresh.")
    print(f"  {snapshot_url(project)}")
    if in_jupyterhub():
        print('  (or right-click it in the file browser → "Open in New Browser Tab")')
    print("\nFor a live dashboard that updates itself, once:")
    for step in SETUP_STEPS:
        print(f"  - {step.replace('`', '')}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Live dashboard for one BERIL project.")
    parser.add_argument("project", nargs="?", help="Path to projects/<id>")
    parser.add_argument("--port", type=int, help="Override the derived port")
    parser.add_argument(
        "--static", action="store_true", help="Write dashboard.html and exit"
    )
    args = parser.parse_args(argv)

    if not args.project:
        parser.error("the following arguments are required: project")

    project = Path(args.project).resolve()
    if not project.is_dir():
        print(f"no such project directory: {project}", file=sys.stderr)
        return 1

    css = load_css(Path(__file__).resolve().parent.parent)
    port = args.port or port_for(project.name)

    # Two callers, one branch. `--static` is someone asking for a snapshot;
    # `not can_serve_live()` is the status line's fallback, which passes
    # `--static` too — so the only difference is who explains themselves.
    if args.static or not can_serve_live():
        _write_snapshot(project, css)
        _print_snapshot_fallback(project)
        return 0

    try:
        serve(project, port, css)
    except OSError as exc:
        if exc.errno in (48, 98):  # EADDRINUSE on macOS / Linux
            print(f"Dashboard already running: {public_url(port)}")
            return 0
        raise
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
