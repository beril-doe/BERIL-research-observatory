"""Conservative, reusable project resolution for repository-level hooks."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any


_PROJECT_PATH = re.compile(
    r"(?:^|[\s/])projects/([A-Za-z0-9][A-Za-z0-9._-]*)(?=$|[\s/])"
)
_SIMPLE_PROJECT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*$")


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
