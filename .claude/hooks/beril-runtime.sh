#!/usr/bin/env bash
# SessionStart + PostToolUse hook → append/replace one atomic session in
# runtime.json. Strictly best-effort: it must NEVER block, so it always exits 0.
# The hook payload (JSON) arrives on stdin and is passed through to the CLI verb.
#
# PostToolUse is what binds a project *created during a session*. None of the
# status line's other signals can: Claude Code was launched before the directory
# existed, /berdl_start only offers to create the branch, and the SessionStart
# snapshot ran before Phase 0 scaffolded anything. The first write into the
# project is the earliest moment the binding is knowable. The consumer is
# .claude/statusline.sh::from_runtime, which is otherwise unreachable for a new
# project.
#
# stdin is captured up front rather than left to flow implicitly into the CLI:
# the guard below reads it, and a pipeline that greps stdin would eat the payload
# so the snapshot would then receive nothing.
payload="$(cat)"

# Cost guard. Unguarded this costs ~65ms on *every* Write/Edit; guarded, a write
# outside any project costs ~8ms (medians of 21 runs on this checkout).
#
# Pinned by tests/test_statusline.py::test_the_guard_does_not_start_the_interpreter_
# for_a_write_outside_a_project, which asserts the *boolean* — whether the
# interpreter starts — not the milliseconds, so it cannot go stale the way the
# earlier ~103ms/~16ms figures here did.
#
# It applies to tool events ONLY. A SessionStart payload for a session on branch
# `projects/<id>` sitting at the repo root contains no `projects/` string at all
# — resolve_project shells out to git for the branch — so a blanket "skip unless
# the payload mentions projects/" would silently break the path that works today.
case "$payload" in
  *'"tool_input"'*|*'"PostToolUse"'*)
    case "$payload" in
      *projects/*) ;;                 # touches a project — snapshot it
      *) exit 0 ;;                    # ordinary edit elsewhere — skip the cost
    esac
    ;;
esac

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)"
if [ -n "$root" ]; then
  py="$root/.venv/bin/python"
  [ -x "$py" ] || py="python3"
  cd "$root" 2>/dev/null && printf '%s' "$payload" \
    | "$py" -m beril_cli.cli runtime-snapshot >/dev/null 2>&1
fi
exit 0
