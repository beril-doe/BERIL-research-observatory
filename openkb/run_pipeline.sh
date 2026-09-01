#!/usr/bin/env bash
# BERIL wiki v3 — the whole pipeline, bootstrap and incremental alike.
#
#   CBORG_API_KEY=... ./run_pipeline.sh            # full run
#   ./run_pipeline.sh --no-publish                 # skip the Quartz build
#
# Every stage is incremental/idempotent, so the SAME command handles the first
# pass and every subsequent addition:
#   stage    copy projects/*/REPORT.md + docs digests into staging/ (rsync-style)
#   compile  openkb add — content-hash skips unchanged docs (model: .openkb/config.yaml)
#   conflicts promote multi-project Tensions to conflict pages (hash-skipped)
#   hubs     re-cluster + regenerate only topic hubs whose members changed
#   extras   deterministic author/data pages
#   check    citation, numeric, uptake, and duplicate-concept audits (fails on errors)
#   publish  Quartz static site (dead links stripped at publish)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$HERE")"
LOG="$HERE/pipeline.log"
: "${CBORG_API_KEY:?set CBORG_API_KEY}"
export OPENAI_API_KEY="$CBORG_API_KEY"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.cborg.lbl.gov}"

echo "== stage" | tee "$LOG"
for d in "$REPO"/projects/*/; do
  p="$(basename "$d")"
  [ -f "$d/REPORT.md" ] && cp "$d/REPORT.md" "$HERE/staging/${p}__REPORT.md"
done
cp "$REPO/docs/discoveries.md" "$REPO/docs/pitfalls.md" "$HERE/staging/"
echo "staged $(ls "$HERE/staging" | wc -l | tr -d ' ') docs" | tee -a "$LOG"

echo "== compile (model: $(grep '^model:' "$HERE/.openkb/config.yaml"))" | tee -a "$LOG"
"$HERE/.venv/bin/openkb" --kb-dir "$HERE" add "$HERE/staging/" 2>&1 | grep -vE "openkb.images WARNING" | tee -a "$LOG" | tail -3
# openkb add exits 0 even on per-doc failures — fail loudly ourselves.
if grep -qE "\[ERROR\]" "$LOG"; then echo "compile had errors — see $LOG"; exit 1; fi

echo "== conflicts" | tee -a "$LOG"
"$HERE/.venv/bin/python" "$HERE/conflicts_build.py" | tee -a "$LOG"

echo "== hubs" | tee -a "$LOG"
"$HERE/.venv/bin/python" "$HERE/topics_build.py" | tee -a "$LOG"

echo "== extras" | tee -a "$LOG"
"$HERE/.venv/bin/python" "$HERE/extra_pages.py" | tee -a "$LOG"

echo "== check" | tee -a "$LOG"
"$HERE/.venv/bin/python" "$HERE/wiki_check.py" "$HERE" | tee -a "$LOG"

if [ "${1:-}" != "--no-publish" ]; then
  echo "== publish" | tee -a "$LOG"
  "$HERE/build_quartz.sh" 2>&1 | tail -2 | tee -a "$LOG"
fi
echo "== pipeline done"
