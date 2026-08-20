#!/usr/bin/env python3
"""
Drive retro_load.py over every entry in manifest.json, computing each file's
tags/user_id automatically from its manifest record instead of hand-typed
per-file commands (the gap issue #390 was filed for).

Resolves each entry's actual transcript path via `find <find_root> -name
'<session_id>.jsonl'` (same pattern already proven working all session),
then subprocess-calls retro_load.py once per entry, reusing its exact CLI
(credentials, tag/user_id handling, marker-writing) rather than
re-implementing that logic here.

Usage (run on the pod, next to retro_load.py / langfuse_hook_official.py):
    python3 run_manifest.py --dry-run          # prints planned tags, no Langfuse calls
    python3 run_manifest.py                    # real run, all entries
    python3 run_manifest.py --limit 5          # real run, first 5 only (smoke test)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retro_load import already_loaded  # noqa: E402


def resolve_path(find_root: str, session_id: str) -> Path | None:
    root = Path(find_root).expanduser()
    r = subprocess.run(
        ["find", str(root), "-name", f"{session_id}.jsonl"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ! find failed under {root}: {r.stderr.strip()}", file=sys.stderr)
        return None
    hits = [line for line in r.stdout.splitlines() if line.strip()]
    if not hits:
        return None
    if len(hits) > 1:
        print(f"  ! {session_id}: {len(hits)} matches under {root}, using the first: {hits}", file=sys.stderr)
    return Path(hits[0]).resolve()


def compute_tags(entry: dict) -> list[str]:
    tags = ["claude-code", "retro-load", f"source:{entry['source']}", "full-load-2026-08-20"]
    if entry.get("consent_bin"):
        tags.append(f"consent:{entry['consent_bin']}")
    if entry.get("event_day"):
        tags.append("event_day:2026-05-07")
    if entry.get("role"):
        tags.append(f"role:{entry['role']}")
    if entry.get("group"):
        tags.append(f"group:{entry['group']}")
    return tags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="manifest.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    if args.limit:
        manifest = manifest[: args.limit]

    not_found, already, planned, emitted_total, failed = [], [], [], 0, []

    for entry in manifest:
        sid = entry["session_id"]
        path = resolve_path(entry["find_root"], sid)
        if path is None:
            not_found.append(sid)
            continue

        tags = compute_tags(entry)
        user_id = entry["user_id"]

        if args.dry_run:
            prior = already_loaded(path)
            status = f"ALREADY LOADED ({prior['turns_emitted']} turns)" if prior else "would load"
            print(f"{sid}: {status} | user_id={user_id} | tags={tags}")
            planned.append(sid)
            continue

        prior = already_loaded(path)
        if prior and not args.force:
            already.append(sid)
            continue

        # Delegate the actual emission to retro_load.py as a subprocess, reusing
        # its exact CLI (credentials, propagate_attributes, marker-writing) rather
        # than re-implementing that logic here.
        cmd = [sys.executable, str(Path(__file__).parent / "retro_load.py"),
               "--user-id", user_id]
        for t in tags:
            cmd += ["--tag", t]
        cmd.append(str(path))
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"{sid}: {'OK' if ok else 'FAILED'}")
        if not ok:
            failed.append((sid, r.stdout[-500:], r.stderr[-500:]))
        else:
            emitted_total += 1

    print()
    print(f"summary: {len(manifest)} manifest entries")
    if args.dry_run:
        print(f"  {len(planned)} resolved and would run, {len(not_found)} not found on disk")
    else:
        print(f"  {emitted_total} emitted, {len(already)} already loaded (skipped), "
              f"{len(not_found)} not found, {len(failed)} failed")
    if not_found:
        print("  NOT FOUND:", not_found)
    if failed:
        print("  FAILED:")
        for sid, out, err in failed:
            print(f"    {sid}: stdout_tail={out!r} stderr_tail={err!r}")
    return 1 if (not_found or failed) else 0


if __name__ == "__main__":
    sys.exit(main())
