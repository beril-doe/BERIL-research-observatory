#!/usr/bin/env bash
# Single launcher for the Langfuse hooks, so the "is tracing on" rule and the
# interpreter pick live in one place instead of four escaped-JSON one-liners.
#
# The guard matters: the hooks import the Langfuse SDK, which costs 0.2s warm /
# 0.6s cold before any work happens (same cost-guard rationale as
# beril-runtime.sh). Unconfigured users pay a few ms here and no interpreter
# ever starts. "Configured" = opted in AND logged in via `beril login`: the hooks
# reach Langfuse through the BERIL relay with that login token, so there are
# no Langfuse keys to check for.
#
# --bg detaches the script: nothing reads either hook's result, the Stop hook's
# FileLock serializes overlapping runs, and SessionEnd hooks share a 1.5s
# budget (Claude Code default) that an SDK import plus an upload can't meet.
# nohup so the detached upload survives the session's terminal going away.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)" || exit 0

# The opt-in can come from the shell or from the repo's .env, which is where
# `beril setup` writes it. Nothing else loads .env where direnv isn't
# installed, the BERDL Hub included, so without this the opt-in did nothing
# there (issue 454). The shell wins, so TRACE_TO_LANGFUSE=false in the
# environment still turns tracing off. .env is read, never sourced, and only
# this one key is looked at; the last assignment wins, as in setup's parser.
if [ -z "${TRACE_TO_LANGFUSE+x}" ] && [ -f "$root/.env" ]; then
  flag="$(sed -n -E 's/^[[:space:]]*(export[[:space:]]+)?TRACE_TO_LANGFUSE[[:space:]]*=[[:space:]]*["'"'"']?([^"'"'"'#[:space:]]*).*/\2/p' "$root/.env" | tail -n 1)"
  [ "$flag" = true ] && export TRACE_TO_LANGFUSE=true
fi
[ "${TRACE_TO_LANGFUSE:-}" = true ] || exit 0
[ -s "${HOME:-}/.beril/auth.json" ] || exit 0

py="$root/.venv/bin/python"
[ -x "$py" ] || py=python3

if [ "$1" = "--bg" ]; then
  shift
  payload="$(cat)"
  printf '%s' "$payload" | nohup "$py" "$root/.claude/hooks/$1" >/dev/null 2>&1 &
else
  "$py" "$root/.claude/hooks/$1"
fi
exit 0
