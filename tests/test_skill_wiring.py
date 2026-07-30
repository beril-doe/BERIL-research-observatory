"""Guards that the worklog and dashboard hooks stay wired into the skills.

The hooks live in skill markdown, which nothing else tests. That makes them
invisible to the one event most likely to drop them: a refactor that moves a
lifecycle phase between skills, which is exactly what `feat/planning-workflow`
does when it splits `/berdl_start` into `/research-plan` and `/execute-plan`.

That failure is silent in the worst way. Simulating the merge with a naive
`--ours` resolution on `berdl_start/SKILL.md` left **0** worklog references and
**0** dashboard references across all three skills — and **346 tests still
passed**. The files existed, the code ran, and the agent would simply never have
written another worklog entry or started the dashboard again.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".claude" / "skills"
WORKLOG_SKILL = SKILLS / "worklog-capture" / "SKILL.md"

# Rows of the "Lifecycle transitions" table look like:
#   | `exploration` → `proposed` | `/research-plan` | `plan written → proposed` |
_OWNER_RE = re.compile(r"`/([a-z_][a-z0-9_-]*)`")


def _transition_owners() -> list:
    """(transition, owning_skill) per row. worklog-capture's own table is the
    source of truth, so a stale table fails as loudly as a dropped hook."""
    section = (
        WORKLOG_SKILL.read_text(encoding="utf-8")
        .split("### Lifecycle transitions", 1)[1]
        .split("###", 1)[0]
    )
    owners = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].startswith("---") or cells[0] == "Transition":
            continue
        found = _OWNER_RE.search(cells[1])
        if found:
            owners.append((cells[0], found.group(1)))
    return owners


def test_every_lifecycle_transition_owner_hooks_the_worklog():
    owners = _transition_owners()
    assert len(owners) == 6, f"expected 6 lifecycle transitions, parsed {len(owners)}"

    broken = []
    for transition, skill in owners:
        skill_file = SKILLS / skill / "SKILL.md"
        if not skill_file.is_file():
            broken.append(f"{transition}: `/{skill}` does not exist")
        elif "worklog" not in skill_file.read_text(encoding="utf-8").lower():
            broken.append(f"{transition}: `/{skill}` never mentions the worklog")
    assert not broken, "lifecycle transitions with no worklog hook:\n  " + "\n  ".join(
        broken
    )


def test_dashboard_launcher_is_wired_into_exactly_one_lifecycle_skill():
    """Zero means it never starts for the operator. More than one means the URL
    is re-printed every phase — the noise the design explicitly cut."""
    launchers = [
        path.parent.name
        for path in sorted(SKILLS.glob("*/SKILL.md"))
        if "tools/dashboard.py" in path.read_text(encoding="utf-8")
        and path.parent.name != "worklog-capture"
    ]
    assert len(launchers) == 1, f"expected exactly one launcher skill, found {launchers}"

    assert "tools/dashboard.py" in WORKLOG_SKILL.read_text(encoding="utf-8"), (
        "worklog-capture no longer re-runs the launcher; a dashboard killed by a "
        "pod restart would never come back"
    )
