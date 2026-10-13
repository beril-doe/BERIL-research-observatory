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

[ -s "${HOME:-}/.beril/auth.json" ] || exit 0

# Settings can come from the shell or from the repo's .env, which is where
# `beril setup` writes the opt-in and where the docs say to put
# LANGFUSE_USER_ID. Nothing else loads .env where direnv isn't installed, the
# BERDL Hub included, so without this those settings did nothing there
# (issue 454). A value in the shell wins. .env is read, never sourced, and only
# the keys named below are looked at. Values are read the way setup's
# _parse_env_file reads them: the last assignment wins and surrounding
# whitespace and quotes are stripped.
dotenv_value() {
  [ -f "$root/.env" ] || return 0
  sed -n -E "s/^[[:space:]]*$1[[:space:]]*=(.*)\$/\\1/p" "$root/.env" | tail -n 1 |
    sed -E "s/^[[:space:]]+//; s/[[:space:]]+\$//; s/^'+//; s/'+\$//; s/^\"+//; s/\"+\$//"
}

# Only `true`, in any case, opts in, as in setup's _run_tracing_step, so the
# launcher never traces a session that `beril setup` would report as off.
if [ -z "${TRACE_TO_LANGFUSE+x}" ]; then
  flag="$(dotenv_value TRACE_TO_LANGFUSE | tr "[:upper:]" "[:lower:]")"
  [ "$flag" = true ] && export TRACE_TO_LANGFUSE=true
fi
[ "${TRACE_TO_LANGFUSE:-}" = true ] || exit 0

# Attribution for every trace. Left unset when .env has no value, so the hooks
# fall back to the ORCiD from `beril login`.
if [ -z "${LANGFUSE_USER_ID+x}" ]; then
  uid="$(dotenv_value LANGFUSE_USER_ID)"
  [ -n "$uid" ] && export LANGFUSE_USER_ID="$uid"
fi

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
