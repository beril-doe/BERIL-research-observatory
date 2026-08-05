from __future__ import annotations

import json
import shutil
from pathlib import Path

from .metadata import build_project_metadata
from .selection import MEMORY_DIR_NAME, select_project_files, select_project_memories


def stage_project(project_dir: Path, staging_dir: Path) -> Path:
    target = staging_dir / "projects" / project_dir.name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    for source in select_project_files(project_dir):
        shutil.copy2(source, target / source.name)

    memories = select_project_memories(project_dir)
    if memories:
        memories_target = target / MEMORY_DIR_NAME
        memories_target.mkdir(parents=True, exist_ok=True)
        for source in memories:
            shutil.copy2(source, memories_target / source.name)

    metadata = build_project_metadata(project_dir)
    (target / "PROJECT_METADATA.md").write_text(metadata.markdown, encoding="utf-8")
    claims_markdown = _claims_markdown(project_dir / "claims.json", project_dir.name)
    if claims_markdown:
        (target / "CLAIMS_CONTEXT.md").write_text(claims_markdown, encoding="utf-8")
    return target


def _claims_markdown(claims_path: Path, project_id: str) -> str | None:
    """Render claims.json as searchable Markdown without making it authoritative."""
    if not claims_path.is_file():
        return None
    try:
        state = json.loads(claims_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    claims = state.get("claims") if isinstance(state, dict) else None
    if not isinstance(claims, list):
        return None

    lines = [
        f"# Claims and Evidence: {project_id}",
        "",
        "> Derived from claims.json for retrieval. REPORT.md and the cited project artifacts remain authoritative. Status and confidence are author assertions, not independently proven verdicts.",
    ]
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        assertions = claim.get("author_assertions")
        assertions = assertions if isinstance(assertions, dict) else {}
        computed = claim.get("computed")
        computed = computed if isinstance(computed, dict) else {}
        support = computed.get("resolved_artifact_support", "unknown")
        mismatch = computed.get("confidence_mismatch", False)
        lines.extend(
            [
                "",
                f"## {claim.get('claim', claim.get('claim_id', 'Claim'))}",
                "",
                f"- Claim ID: {claim.get('claim_id', '')}",
                f"- Author-asserted status: {assertions.get('status', '')}",
                f"- Author-written confidence: {assertions.get('confidence', '')}",
                f"- Computed resolved artifact support: {support}",
                f"- Computed confidence mismatch: {mismatch}",
            ]
        )
        _append_evidence(lines, "Supporting evidence", claim.get("supports"))
        _append_evidence(lines, "Contradicting evidence", claim.get("refutes"))
    return "\n".join(lines) + "\n"


def _append_evidence(lines: list[str], heading: str, pointers) -> None:
    lines.extend(["", f"### {heading}", ""])
    if not isinstance(pointers, list) or not pointers:
        lines.append("- None recorded")
        return
    for pointer in pointers:
        if not isinstance(pointer, dict):
            continue
        resolution = pointer.get("resolution")
        status = (
            resolution.get("status") if isinstance(resolution, dict) else "unknown"
        )
        stream = f"; stream={pointer['stream']}" if pointer.get("stream") else ""
        exact = f" — {pointer['exact']}" if pointer.get("exact") else ""
        lines.append(
            f"- [{status}] {pointer.get('kind', 'unknown')}: {pointer.get('locator', '')}{stream}{exact}"
        )


def stage_doc(doc_path: Path, staging_dir: Path) -> Path:
    target = staging_dir / "docs" / doc_path.stem
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(doc_path, target / doc_path.name)
    return target
