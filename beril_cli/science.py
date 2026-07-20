"""Pure computation for the conservative claims projection.

Confidence and status are author assertions. This module computes only whether
resolved, re-runnable artifacts cover zero, one, or multiple explicitly named
evidence streams. Different filenames never imply scientific independence.
"""

from __future__ import annotations

import re

#: Resolved artifact-support levels, strongest first.
ARTIFACT_SUPPORT_LEVELS = ("multiple-streams", "single-stream", "none")
#: Per-claim status enum (a separate axis from the project lifecycle states).
CLAIM_STATUSES = (
    "open",
    "supported",
    "refuted",
    "needs-replication",
    "blocked",
    "needs-evidence",
)
#: Evidence pointer kinds; only ``query``/``notebook`` are re-runnable results.
EVIDENCE_KINDS = ("query", "notebook", "figure", "paper", "web", "docs")


def is_result(pointer: dict) -> bool:
    """A re-runnable data/code result (vs literature, which alone stays ``low``).

    Tolerant of malformed (non-dict) elements — returns False rather than raising.
    """
    return isinstance(pointer, dict) and pointer.get("kind") in ("query", "notebook")


def resolved_artifact_support(supports: list[dict]) -> str:
    """Classify resolved re-runnable support by explicit evidence stream.

    Only notebook/query pointers whose ``resolution.status`` is ``resolved``
    count. Pointers without an explicit ``stream`` share one conservative
    ``default`` stream, so multiple filenames cannot manufacture independence.
    """
    streams: set[str] = set()
    for pointer in supports or []:
        if not is_result(pointer):
            continue
        resolution = pointer.get("resolution")
        if not isinstance(resolution, dict) or resolution.get("status") != "resolved":
            continue
        stream = str(pointer.get("stream") or "default").strip().lower()
        if stream:
            streams.add(stream)
    if len(streams) >= 2:
        return "multiple-streams"
    if streams:
        return "single-stream"
    return "none"


def confidence_mismatch(confidence: str, artifact_support: str) -> bool:
    """Whether written high/medium confidence lacks multi-stream artifact support."""
    return confidence in ("high", "medium") and artifact_support != "multiple-streams"


def confidence_from(text: str) -> str | None:
    """First recognized confidence word (high|medium|low) in a string, else None.

    The canonical word ladder is ``atlas/methods/evidence-grading.md`` (high/medium/
    low, graded by independent evidence streams); this matches it. Resolved
    artifact support is a separate computed axis.
    """
    m = re.search(r"\b(high|medium|low)\b", text, re.IGNORECASE)
    return m.group(1).lower() if m else None


_STATUS_RE = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in CLAIM_STATUSES) + r")\b", re.IGNORECASE
)


def status_from(text: str) -> str | None:
    """First recognized claim status token in a string (by position), else None.

    Position-based like :func:`confidence_from`, so a written value followed by a
    comment listing the other options resolves to the written value, not the
    first enum member that happens to appear.
    """
    m = _STATUS_RE.search(text)
    return m.group(1).lower() if m else None


def claim_id(text: str) -> str:
    """Stable slug for a claim: lowercased, non-alnum -> '-', trimmed THEN
    truncated to 56 chars (matches the reference order; no re-trim after slice)."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    slug = re.sub(r"^-+|-+$", "", slug)
    slug = slug[:56]
    return slug or "claim"
