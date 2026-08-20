#!/usr/bin/env python3
"""
Build manifest.json for the BERIL retro-load driver.

Reads people.json (who, what sources, what consent/role/group each source
carries) and, for each source, discovers every session .jsonl under its
find_root and runs `retro_load.py --dry-run` on it to get turn counts and
per-turn dates -- self-sufficient, no dependency on any prior manual dump.
Content-safe: --dry-run only ever prints timestamps and turn counts, never
message text, so this is fine to run against the frozen workshop corpus too.

Must run on the pod, next to retro_load.py -- that's where the actual
transcripts (both the frozen workshop corpus and anyone's live pod-home)
live. See README.md for the full workflow and the governance reason for
this (raw .jsonl must never leave the pod).

Usage:
    python3 build_manifest.py                        # people.json, ./manifest.json
    python3 build_manifest.py --people other.json --out other-manifest.json
    python3 build_manifest.py --event-day 2026-05-07  # override the target date
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent


def find_jsonl_files(find_root: str) -> list[Path]:
    root = Path(find_root.replace("~", str(Path.home())))
    if not root.exists():
        print(f"  ! find_root does not exist, skipping: {root}")
        return []
    out = subprocess.run(["find", str(root), "-maxdepth", "2", "-name", "*.jsonl"],
                          capture_output=True, text=True).stdout
    return [Path(p) for p in out.splitlines() if p.strip()]


def dry_run_summary(path: Path, event_day: str) -> dict:
    """Run retro_load.py --dry-run on one file; return turn count + whether
    any turn's timestamp falls on event_day. Never reads message content.

    Handles two distinct --dry-run output shapes: a fresh file prints a
    per-turn timestamp listing; an already-loaded file (has a marker --
    the normal case on any re-run after a real load) prints a single
    "already retro-loaded (N turns, tags=[...])" line instead, with no
    per-turn timestamps at all. For that case, turn count comes from the
    stated N and event_day comes from whether 'event_day:<date>' is one of
    the previously-recorded tags in that same line, not from re-scanning
    timestamps that were never re-printed.
    """
    r = subprocess.run(["python3", str(HERE / "retro_load.py"), "--dry-run", str(path)],
                        capture_output=True, text=True)
    turns = 0
    saw_event_day = False

    already = re.search(r"already retro-loaded \((\d+) turns, tags=(\[.*?\])\)", r.stdout)
    if already:
        turns = int(already.group(1))
        saw_event_day = f"event_day:{event_day}" in already.group(2)
        return {"turns": turns, "event_day": saw_event_day}

    for line in r.stdout.splitlines():
        m = re.match(r"^\S+\.jsonl: \d+ jsonl lines -> (\d+) turns", line)
        if m:
            turns = int(m.group(1))
            continue
        m2 = re.search(r"turn \d+: (\d{4}-\d{2}-\d{2})T", line)
        if m2 and m2.group(1) == event_day:
            saw_event_day = True
    return {"turns": turns, "event_day": saw_event_day}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--people", default=str(HERE / "people.json"))
    ap.add_argument("--out", default=str(HERE / "manifest.json"))
    ap.add_argument("--event-day", default="2026-05-07",
                     help="date (YYYY-MM-DD) that counts as the special-event flag")
    args = ap.parse_args()

    people = json.loads(Path(args.people).read_text())
    manifest = []

    for person in people:
        for source in person["sources"]:
            files = find_jsonl_files(source["find_root"])
            print(f"{person['person']}/{source['type']}: {len(files)} files found")
            for path in files:
                sid = path.stem
                summary = dry_run_summary(path, args.event_day)
                event_day = summary["event_day"] or sid in source.get("force_event_day", [])
                manifest.append({
                    "session_id": sid,
                    "person": person["person"],
                    "source": source["type"],
                    "find_root": source["find_root"],
                    "user_id": person["user_id"],
                    "consent_bin": source.get("consent_bin"),
                    "event_day": event_day if source.get("consent_bin") or source["type"] == "workshop-frozen-corpus" else None,
                    "role": person.get("role"),
                    "group": person.get("group"),
                    "turns_expected": summary["turns"],
                })

    Path(args.out).write_text(json.dumps(manifest, indent=2))
    print(f"\n{len(manifest)} entries written to {args.out}")
    by_source = {}
    for e in manifest:
        by_source.setdefault((e["person"], e["source"]), []).append(e)
    for (person, source), entries in sorted(by_source.items()):
        total_turns = sum(e["turns_expected"] for e in entries)
        n_event = sum(1 for e in entries if e["event_day"])
        print(f"  {person}/{source}: {len(entries)} files, {total_turns} turns, {n_event} event-day")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
