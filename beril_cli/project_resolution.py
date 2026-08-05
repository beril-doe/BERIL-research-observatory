"""Conservative, reusable project resolution for repository-level hooks."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


_PROJECT_PATH = re.compile(
    r"(?:^|[\s/])projects/([A-Za-z0-9][A-Za-z0-9._-]*)(?=$|[\s/])"
)
_SIMPLE_PROJECT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*$")
_DEFAULT_BRANCHES = frozenset({"main", "master"})


def _iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_strings(child)


def _existing_project(repo_root: Path, project_id: str | None) -> str | None:
    if not isinstance(project_id, str) or not _SIMPLE_PROJECT_ID.fullmatch(project_id):
        return None
    return project_id if (repo_root / "projects" / project_id).is_dir() else None


def _explicit_binding(payload: dict) -> tuple[bool, str | None]:
    candidates = [payload.get("project_id"), payload.get("project")]
    for container_name in ("beril", "session"):
        container = payload.get(container_name)
        if isinstance(container, dict):
            candidates.append(container.get("project_id"))
    present = [value for value in candidates if value is not None]
    if not present:
        return False, None
    unique = {value for value in present if isinstance(value, str)}
    return True, unique.pop() if len(unique) == 1 else None


def _path_projects(value: Any) -> set[str]:
    projects: set[str] = set()
    for text in _iter_strings(value):
        projects.update(match.group(1) for match in _PROJECT_PATH.finditer(text))
    return projects


def _cwd_project(repo_root: Path, cwd: str) -> tuple[bool, str | None]:
    cwd_path = Path(cwd).resolve()
    projects_root = (repo_root / "projects").resolve()
    if not cwd_path.is_relative_to(projects_root):
        return False, None
    relative = cwd_path.relative_to(projects_root)
    if not relative.parts:
        return True, None
    return True, _existing_project(repo_root, relative.parts[0])


def _git_branch(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    branch = result.stdout.strip()
    return branch if result.returncode == 0 and branch else None


def _manifest_branch(project_dir: Path) -> str | None:
    try:
        text = (project_dir / "beril.yaml").read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^branch:\s*['\"]?([^'\"\s#]+)", text, re.MULTILINE)
    return match.group(1) if match else None


def _branch_project(repo_root: Path, branch: str | None) -> str | None:
    if not branch:
        return None
    conventional = re.fullmatch(r"projects/([A-Za-z0-9][A-Za-z0-9._-]*)", branch)
    if conventional:
        return _existing_project(repo_root, conventional.group(1))
    # The manifest scan below binds a session by an *exact* `branch:` match, which
    # is meaningful for a working branch (`feat/p2-analysis`) and meaningless for
    # the default branch: a lone manifest recording `branch: main` captures every
    # repo-root session on `main`, including sessions doing unrelated work. One
    # such value is indistinguishable from a correct one — the len(matches) == 1
    # ambiguity guard only fires when a *second* project collides. Excluded here
    # rather than validated at write time so an already-committed manifest cannot
    # reintroduce it. The conventional `projects/<id>` form above is unaffected.
    if branch in _DEFAULT_BRANCHES:
        return None
    projects_root = repo_root / "projects"
    matches = (
        [
            project_dir.name
            for project_dir in projects_root.iterdir()
            if project_dir.is_dir() and _manifest_branch(project_dir) == branch
        ]
        if projects_root.is_dir()
        else []
    )
    return matches[0] if len(matches) == 1 else None


def resolve_project(
    payload: dict,
    *,
    repo_root: Path | None = None,
    branch: str | None = None,
) -> str | None:
    """Resolve explicit binding, payload path, cwd, then exact branch mapping.

    A present-but-invalid or ambiguous higher-priority signal returns ``None``;
    it never falls through to a guess from a lower-priority signal.
    """
    root = Path(repo_root or Path.cwd()).resolve()

    binding_present, binding = _explicit_binding(payload)
    if binding_present:
        return _existing_project(root, binding)

    payload_without_cwd = {key: value for key, value in payload.items() if key != "cwd"}
    path_projects = _path_projects(payload_without_cwd)
    if path_projects:
        if len(path_projects) != 1:
            return None
        return _existing_project(root, next(iter(path_projects)))

    cwd = payload.get("cwd")
    if isinstance(cwd, str):
        cwd_present, cwd_project = _cwd_project(root, cwd)
        if cwd_present:
            return cwd_project

    return _branch_project(root, branch if branch is not None else _git_branch(root))


def project_from_runtime(session_id: str | None, repo_root: Path) -> str | None:
    """The project this session most recently bound to, by `observed_at`.

    The signal `resolve_project` cannot supply: a project created *during* a
    session has no cwd, branch or path to be found by, and `runtime.json` keyed by
    session id is the only record that it was worked on. Session-scoped by
    construction, so two sessions in one clone still resolve to their own.

    **Newest wins, never the first match.** A session that moved between projects
    is recorded in both files, and taking the first hit from a sorted glob returned
    whichever project sorted earlier — so working in `zeta_current` after
    `alpha_old` displayed `alpha_old`, with a live dashboard URL for the project
    you left.

    `observed_at` means "when this session's provenance for this project last
    materially changed", not "last touched": `audit_cmd._effective_session` strips
    the timestamp before its idempotency check, so a repeat write with the same
    git state, model and mode does not refresh it. Switching *to* a project always
    writes a record, so the forward case is exact; switching *back* with nothing
    else changed keeps the older stamp until the next commit refreshes it.

    `observed_at` is stamped to the second (`audit_cmd._now_iso`), so two bindings
    made in the same second tie — which is exactly what pinning one project and
    then another does. Ties break on the manifest's mtime, which has sub-second
    resolution; only if that also ties does sorted order decide, so the answer
    stays deterministic.
    """
    if not session_id:
        return None
    best: tuple[tuple[str, float], str] | None = None
    for manifest in sorted((repo_root / "projects").glob("*/runtime.json")):
        try:
            recorded = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(recorded, dict):
            continue
        stamps = [
            item.get("observed_at") or ""
            for item in recorded.get("sessions", [])
            if isinstance(item, dict) and item.get("session_id") == session_id
        ]
        if not stamps:
            continue
        # ISO-8601 UTC to a fixed format, so string order is time order.
        try:
            mtime = manifest.stat().st_mtime
        except OSError:
            mtime = 0.0
        key = (max(stamps), mtime)
        project = recorded.get("project") or manifest.parent.name
        if best is None or key > best[0]:
            best = (key, project)
    return best[1] if best else None


def projects_for_session(session_id: str | None, repo_root: Path) -> list[str]:
    """Every project this session bound to, oldest binding first.

    `project_from_runtime` answers "which one is it *now*", which is the question a
    display asks. Cleanup asks a different one: a session that switched projects
    started a dashboard for each, on its own port, and stopping only the current
    one leaves the rest running after Claude Code exits.
    """
    if not session_id:
        return []
    found = []
    for manifest in sorted((repo_root / "projects").glob("*/runtime.json")):
        try:
            recorded = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(recorded, dict):
            continue
        if any(
            isinstance(item, dict) and item.get("session_id") == session_id
            for item in recorded.get("sessions", [])
        ):
            found.append(recorded.get("project") or manifest.parent.name)
    return found
