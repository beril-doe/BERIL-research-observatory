#!/usr/bin/env python3
"""PreToolUse witness: records analysis code written under an unapproved plan.

Appends one line to ``projects/<id>/plan_deviations.jsonl`` when a write targets
``projects/<id>/**/*.{ipynb,py}`` while the project has a ``RESEARCH_PLAN.md``,
has no committed ``REPORT.md``, and ``beril.yaml`` carries no
``plan_approval.plan_hash`` matching the plan on disk. It never refuses the
write: exploration and light analysis have to stay supported, and
pre-registration integrity does not require that departing from the plan be
impossible, only that it be undeniable afterwards.

Never reads ``status``: an agent writing ``status: active`` records nothing
different, because the only thing that counts as approval is a hash of the plan
a human actually read.

The harness runs this with the *system* interpreter (3.9), so: stdlib only, no
modern syntax, and no importing ``beril_cli`` (that needs the venv).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# Anchored: matched against the path *relative to this checkout*, so a checkout
# living under some other ``projects/`` directory resolves to its own project
# dir, and ``scratch/projects/demo/x.py`` — which merely contains the string —
# resolves to nothing.
PROJECT = re.compile(r"projects/([^/]+)/")

# Twin of the pair in beril_cli/approve_cmd.py — edit both or neither.
REVISION_HISTORY = re.compile(rb"^##[ \t]+Revision History[ \t\r]*$", re.MULTILINE)
NEXT_SECTION = re.compile(rb"^##[ \t]", re.MULTILINE)
PATH_KEYS = ("file_path", "notebook_path", "relative_path", "path")
# The MCP matcher in settings.json is ``mcp__.*``, so read-only servers fire this
# hook too, and reading a file is not a deviation. An allowlist of mutating verbs
# rather than a denylist of read verbs: the mutating vocabulary is small and
# closed, while "read-only" is open-ended (get/list/find/search/overview/...) and
# every unlisted one would become a false accusation in the audit trail. The
# failure mode is inverted, and inverted the right way — an unrecognised writer
# is a missed record, not a deviation logged against a human who read a file.
MUTATING = (
    "write",
    "edit",
    "create",
    "replace",
    "insert",
    "append",
    "delete",
    "rename",
    "move",
    "patch",
    "save",
    "update",
)


def plan_digest(path: str) -> str:
    """Hash the plan content above its ``## Revision History`` heading.

    Twin of ``beril_cli.approve_cmd.plan_digest``. The hook runs on the system
    interpreter and cannot import the package, so the logic is duplicated. The
    two take different arguments and cannot be byte-identical sources — they
    must agree on *output*, which ``tests/test_plan_gate.py`` pins. If they
    drift, ``beril approve`` records a hash this hook can never match and every
    later write is logged as a deviation from a plan that was in fact approved.

    Deliberately *not* ``tools/review.sh``'s whole-file ``plan_hash``: a minor
    Revision-History append must not read as a deviation, while a material edit
    (hypotheses, thresholds, discrimination strategy — all above that heading)
    must.

    Parameters
    ----------
    path
        Path to a ``RESEARCH_PLAN.md``.

    Returns
    -------
    str
        Bare hex sha256 of the plan bytes up to the heading, or of the whole
        file when the heading is absent.
    """
    with open(path, "rb") as handle:
        content = handle.read()
    return _digest_bytes(content)


def _digest_bytes(content):
    """Digest plan bytes with only the Revision History SECTION excised.

    Excising the whole tail would be a hole, not a rule: plans in this repo
    routinely carry `## Authors` and even whole pivot sections below Revision
    History (the template at research-plan/SKILL.md puts Authors there), so
    everything after the heading must still be covered.
    """
    match = REVISION_HISTORY.search(content)
    if match is None:
        return hashlib.sha256(content).hexdigest()
    tail = content[match.end() :]
    following = NEXT_SECTION.search(tail)
    rest = tail[following.start() :] if following is not None else b""
    return hashlib.sha256(content[: match.start()] + rest).hexdigest()


def _stored_hash(manifest: str) -> str | None:
    """Read ``plan_approval.plan_hash`` from ``beril.yaml``, scoped to that block.

    A hand-rolled scan rather than PyYAML, which the hook cannot import. Scoped
    on purpose: a ``plan_hash`` under any other top-level key (``artifacts:``,
    ``approval:``), or nested one level deeper inside ``plan_approval:``, is not
    an approval — only a direct child of that block counts.

    Parameters
    ----------
    manifest
        Path to a project ``beril.yaml``.

    Returns
    -------
    str or None
        The bare hex digest, with any ``sha256:`` prefix and quotes stripped, or
        None when the file or the key is absent.
    """
    inside = False
    child = None
    try:
        with open(manifest, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                if line[:1] not in (" ", "\t"):
                    inside = line.split(":", 1)[0].strip() == "plan_approval"
                    child = None
                    continue
                if not inside:
                    continue
                # Only a *direct* child counts: the indent of the block's first
                # child sets the level, and anything deeper (a nested
                # ``metadata:`` mapping) is some other key that happens to be
                # spelled plan_hash.
                indent = len(line) - len(line.lstrip())
                if child is None:
                    child = indent
                key, sep, value = line.partition(":")
                if sep and indent == child and key.strip() == "plan_hash":
                    return (
                        value.split("#", 1)[0].strip().strip("'\"").rsplit(":", 1)[-1]
                    )
    except OSError:
        return None
    return None


def _report_committed(pdir: str) -> bool:
    """True when ``REPORT.md`` exists in the last commit.

    The "analysis is written up" exemption keys on a *committed* report, not a
    file that exists: an empty stub written this session would otherwise silence
    the witness permanently, and scaffolding one is ordinary agent behaviour.

    Asks ``cat-file -e HEAD:REPORT.md`` rather than ``ls-files``: ls-files also
    succeeds for a merely *staged* file, so ``git add`` on a stub would silence
    the witness exactly as writing one used to.

    Parameters
    ----------
    pdir
        Path to the project directory.

    Returns
    -------
    bool
        True when tracked, or when there is no git work tree to ask (nothing to
        check against, so fall back to mere existence). Any other failure
        answers False: 128 is git's generic fatal code (dubious ownership, a
        broken index, an unreadable object store), and trusting it would let an
        unrelated breakage silence the witness for good. Not exempting only
        means recording, and recording never blocks anything.
    """
    try:
        proc = subprocess.run(
            # `HEAD:./REPORT.md` — the `./` makes the path relative to -C's
            # directory. Bare `HEAD:REPORT.md` resolves from the repo ROOT and
            # would never find a project's report.
            ["git", "-C", pdir, "cat-file", "-e", "HEAD:./REPORT.md"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except OSError:
        return True  # no git binary: fall back to mere existence
    if proc.returncode == 0:
        return True  # tracked
    return b"not a git repository" in (proc.stderr or b"").lower()


def _record(pdir: str, path: str, digest: str) -> None:
    """Append one deviation record to ``projects/<id>/plan_deviations.jsonl``.

    Append-only JSONL because the hook is stdlib-only under Python 3.9 and
    cannot import PyYAML: appending a line needs no read-modify-write, so two
    concurrent tool calls cannot corrupt the file. Each record carries the plan
    digest as it stood at the time, which separates "worked ahead of approval on
    this plan" from "worked, then the plan changed underneath".

    Parameters
    ----------
    pdir
        Path to the project directory.
    path
        Normalized path of the file the tool call was about to write.
    digest
        ``plan_digest`` of the project's ``RESEARCH_PLAN.md`` right now.
    """
    record = {
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "path": path,
        "plan_hash": digest,
    }
    target = os.path.join(pdir, "plan_deviations.jsonl")
    with open(target, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def main() -> None:
    """Record the call when it writes analysis code under an unapproved plan."""
    if os.environ.get("BERIL_PLAN_GATE") == "off":
        return
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name") or ""
    if not any(verb in tool_name.lower() for verb in MUTATING):
        return  # a read carries a file_path too, and reading is not a deviation
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or "."
    for key in PATH_KEYS:
        path = tool_input.get(key)
        if not isinstance(path, str) or not path.endswith((".ipynb", ".py")):
            continue
        # normpath first: the harness canonicalizes file_path/notebook_path, but
        # not arbitrary MCP arguments, so `projects/./<project>/x.py` would
        # otherwise be attributed to a project named ".".
        path = os.path.normpath(path).replace(os.sep, "/")
        # Attribution is by position inside *this* checkout, not by the path
        # containing the string "projects/": `scratch/projects/demo/x.py` and
        # another checkout's absolute path both contain it and belong to neither
        # project here. relpath resolves both forms against the repo root, so
        # anything outside falls out as a leading `../`.
        inside = os.path.relpath(os.path.join(root, path), root)
        match = PROJECT.match(inside.replace(os.sep, "/"))
        if match is None:
            continue
        pdir = os.path.join(root, "projects", match.group(1))
        plan = os.path.join(pdir, "RESEARCH_PLAN.md")
        if not os.path.isfile(plan):
            continue  # no frozen contract yet: this is exploration
        if os.path.isfile(os.path.join(pdir, "REPORT.md")) and _report_committed(pdir):
            continue  # analysis already written up (a stub written now is not)
        digest = plan_digest(plan)
        if _stored_hash(os.path.join(pdir, "beril.yaml")) == digest:
            continue
        _record(pdir, path, digest)
        return  # one record per tool call


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # a witness must never break a write: fail open
        # Deliberately does not name the escape hatch. This stderr goes to the
        # model, which is the one audience that should not be handed a working
        # switch — and this path is agent-triggerable (an unreadable plan raises
        # here). BERIL_PLAN_GATE=off is documented for humans in PROJECT.md.
        sys.stderr.write(
            "plan witness error (%s: %s). Report this to the user.\n"
            % (type(exc).__name__, exc)
        )
