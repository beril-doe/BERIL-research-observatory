#!/usr/bin/env python3
"""
Build manifest.json for the BERIL retro-load driver from the dry-run survey
outputs already gathered this session (turn counts + per-turn dates parsed
from `retro_load.py --dry-run` output, never message content).

Encodes the decisions made 2026-08-20:
  - event_day true for Mark's 4a1f0add (starts night before, 14/24 turns
    land on 2026-05-07) -- counted as event-day per Mark's explicit call
  - role/group from the invite-list sheet (Mark: NMDC/Observe,
    Dileep: KBase/Observe), verified 2026-08-20
  - Dileep's consent: "yes" directly in the invite-list sheet's own
    consented? column, independently verified -- not just Mark's attestation
"""
import json
import re
from pathlib import Path

DEST = Path("/private/tmp/claude-502/-Users-mam-gitrepos-nmdc-lakehouse"
             "/40fa7bb5-461a-4d85-99e9-36f78af5aa17/scratchpad/beril-langfuse-retro-load")

MARK_ROLE = "Observe"
MARK_GROUP = "NMDC"
DKISHORE_ROLE = "Observe"
DKISHORE_GROUP = "KBase"

# Mark's 4a1f0add explicitly counted as event-day per Mark's 2026-08-20 decision,
# even though the summary-only dry-run doesn't show per-turn dates for it here.
MARK_FORCE_EVENT_DAY = {"4a1f0add-391b-4775-bc15-bd21c4e459ac"}


def parse_summary_with_dates(path):
    """Parse a dry-run capture that has per-turn date lines (not stripped)."""
    entries = {}
    cur = None
    for line in open(path):
        m = re.match(r'^(\S+)\.jsonl: (\d+) jsonl lines -> (\d+) turns', line)
        if m:
            cur = m.group(1)
            entries[cur] = {"turns": int(m.group(3)), "event_day": False}
            continue
        m2 = re.search(r'turn \d+: (\d{4}-\d{2}-\d{2})T', line)
        if m2 and cur and m2.group(1) == "2026-05-07":
            entries[cur]["event_day"] = True
    return entries


def parse_summary_turns_only(path):
    """Parse a dry-run capture with per-turn lines stripped (count only)."""
    entries = {}
    for line in open(path):
        m = re.match(r'^(\S+)\.jsonl: (\d+) jsonl lines -> (\d+) turns', line)
        if m:
            # group(2) is jsonl LINE count (file size), group(3) is TURN count --
            # bug caught 2026-08-20: this used to read group(2) and produced a
            # 13,359 "turn" total across 60 files (actually ~232). Fixed.
            entries[m.group(1)] = {"turns": int(m.group(3)), "event_day": False}
    return entries


manifest = []

# 1. Mark's frozen workshop corpus (14 files, has per-turn dates)
mark_frozen = parse_summary_with_dates(DEST / "_dryrun_all.txt")
for sid, info in mark_frozen.items():
    event_day = info["event_day"] or sid in MARK_FORCE_EVENT_DAY
    manifest.append({
        "session_id": sid,
        "person": "mamillerpa",
        "source": "workshop-frozen-corpus",
        "find_root": "~/justin-trace-analysis/data/claudefiles/mamillerpa/.claude/projects",
        "user_id": "mamillerpa",
        "consent_bin": "team",
        "event_day": event_day,
        "role": MARK_ROLE,
        "group": MARK_GROUP,
        "turns_expected": info["turns"],
    })

# 2. Mark's live pod-home (60 files, turn counts only -- event_day doesn't
#    apply to ongoing/live work, only to the frozen workshop-day framing)
mark_live = parse_summary_turns_only(DEST / "_dryrun_markpod_summary.txt")
for sid, info in mark_live.items():
    manifest.append({
        "session_id": sid,
        "person": "mamillerpa",
        "source": "pod-live",
        "find_root": "~/.claude/projects",
        "user_id": "mamillerpa",
        "consent_bin": None,
        "event_day": None,
        "role": None,
        "group": None,
        "turns_expected": info["turns"],
    })

# 3. Dileep's frozen workshop corpus (37 files, has per-turn dates now)
dkishore_frozen = parse_summary_with_dates(DEST / "_dkishore_dates_full.txt")
for sid, info in dkishore_frozen.items():
    manifest.append({
        "session_id": sid,
        "person": "dkishore",
        "source": "workshop-frozen-corpus",
        "find_root": "~/justin-trace-analysis/data/claudefiles/dkishore/.claude/projects",
        "user_id": "dkishore",
        "consent_bin": "opt_in",  # verified directly in the invite-list sheet's own column
        "event_day": info["event_day"],
        "role": DKISHORE_ROLE,
        "group": DKISHORE_GROUP,
        "turns_expected": info["turns"],
    })

# 71551c67 is missing from the dry-run sweep above because it was already
# loaded in the original 4-file sample set (has a marker), so --dry-run
# printed "already retro-loaded" instead of the summary line the parser
# above matches on. Adding it back explicitly with its known, already-loaded
# state so the manifest's own counts are complete -- the driver will skip it
# via the marker check regardless, same as it would for any already-loaded file.
manifest.append({
    "session_id": "71551c67-7975-453c-a791-dad2d1a50fb9",
    "person": "dkishore",
    "source": "workshop-frozen-corpus",
    "find_root": "~/justin-trace-analysis/data/claudefiles/dkishore/.claude/projects",
    "user_id": "dkishore",
    "consent_bin": "opt_in",
    "event_day": False,  # not confirmed either way; already loaded, won't be reprocessed
    "role": DKISHORE_ROLE,
    "group": DKISHORE_GROUP,
    "turns_expected": 5,
    "already_loaded": True,
})

out = DEST / "manifest.json"
out.write_text(json.dumps(manifest, indent=2))

print(f"{len(manifest)} entries written to {out}")
by_source = {}
for e in manifest:
    by_source.setdefault((e["person"], e["source"]), []).append(e)
for (person, source), entries in sorted(by_source.items()):
    n_event = sum(1 for e in entries if e["event_day"])
    total_turns = sum(e["turns_expected"] for e in entries)
    print(f"  {person}/{source}: {len(entries)} files, {total_turns} turns, "
          f"{n_event} event-day" if source == "workshop-frozen-corpus" else
          f"  {person}/{source}: {len(entries)} files, {total_turns} turns")
