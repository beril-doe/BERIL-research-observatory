#!/usr/bin/env bash
# Single launcher for the Langfuse hooks, so the "is tracing on" rule and the
# interpreter pick live in one place instead of four escaped-JSON one-liners.
#
# The guard matters: the hooks import the Langfuse SDK, which costs 0.2s warm /
# 0.6s cold before any work happens (same cost-guard rationale as
# beril-runtime.sh). Unconfigured users pay ~1ms here and no interpreter ever
# starts. Keys are accepted under either name the hook itself accepts.
#
# --bg detaches the script (used for the per-response Stop hook, which is
# fire-and-forget: nothing reads its result, and its FileLock serializes
# overlapping runs). SessionEnd's artifact upload runs foreground so it
# finishes before the session exits.
[ "${TRACE_TO_LANGFUSE:-}" = true ] || exit 0
[ -n "${LANGFUSE_SECRET_KEY:-}${CC_LANGFUSE_SECRET_KEY:-}" ] || exit 0

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)" || exit 0
py="$root/.venv/bin/python"
[ -x "$py" ] || py=python3

if [ "$1" = "--bg" ]; then
  shift
  payload="$(cat)"
  printf '%s' "$payload" | "$py" "$root/.claude/hooks/$1" >/dev/null 2>&1 &
else
  "$py" "$root/.claude/hooks/$1"
fi
exit 0
