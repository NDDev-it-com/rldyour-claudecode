#!/usr/bin/env bash
# pre_tool_use_ci_advisory.sh - manual-first CI policy programmatic reminder.
#
# Security F-3 closure: the manual-first CI rule was previously docs-only
# (.github/workflows/README.md "Manual operator gestures" section). This
# PreToolUse hook adds a programmatic reminder when the model tries to
# execute `gh workflow run`, `gh run`, or `gh actions` commands - prompting
# the operator to confirm the gesture was explicitly requested.
#
# Behaviour: advisory ONLY. Hook emits a stderr warning and exits 0 (no
# blocking). The hook is filtered to fire only on the three gh CI-control
# subcommands via the hooks.json `if` filter; the script itself does NOT
# self-filter further.
#
# Skip flag: RLDYOUR_SKIP_CI_ADVISORY=1 -> exit 0 immediately.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

# Defensive python3 resolution: subprocess shells (e.g. Claude Code hook runner)
# may have a sanitized PATH that omits ~/.local/bin, and uv-managed Python
# symlinks can be transiently broken during interpreter upgrades. Resolve once
# and exit 0 if no working interpreter exists - hooks must stay non-blocking
# when Python is unavailable. Canonical pattern (tw93/Mole, rsyslog).
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)}"
if [ -z "${PYTHON_BIN}" ] || [ ! -x "${PYTHON_BIN}" ]; then
  exit 0
fi

if [ "${RLDYOUR_SKIP_CI_ADVISORY:-0}" = "1" ]; then
  exit 0
fi

INPUT=$(cat 2>/dev/null || true)

# Parse the Bash command being executed from the hook input payload.
COMMAND=$(RLDYOUR_HOOK_INPUT="$INPUT" "${PYTHON_BIN}" <<'PY' 2>/dev/null || true
import json
import os
import sys
try:
    payload = json.loads(os.environ.get("RLDYOUR_HOOK_INPUT", ""))
except (json.JSONDecodeError, ValueError):
    payload = {}
tool_input = payload.get("tool_input", {})
if not isinstance(tool_input, dict):
    tool_input = {}
cmd = tool_input.get("command", "")
print(cmd if isinstance(cmd, str) else "")
PY
)

# Only fire when the parsed command actually starts with one of the
# CI-control gh subcommands (defensive - hook is also filtered via
# hooks.json `if`).
case "$COMMAND" in
  "gh workflow run"*|"gh workflow disable"*|"gh workflow enable"*|"gh run rerun"*|"gh run cancel"*|"gh actions"*)
    cat >&2 <<'ADVISORY'
[RLDYOUR-FLOW CI-ADVISORY] About to invoke a GitHub Actions control command.

The repository's manual-first CI policy says agents (Claude, Codex, etc.)
should run `gh workflow run` / `gh run` / `gh actions` only when the user
explicitly asked ("сделай ci", "запусти сиай", "прогони на гитхабе",
"run CI", etc.). Push to main + PR merges trigger CI automatically; the
gh commands above are reserved for advisory workflows and re-runs.

If this gesture is in response to an explicit user instruction - proceed.
If it is proactive - reconsider and let the existing PR gate handle it.

Reference: .github/workflows/README.md "Manual operator gestures".
Skip this advisory in trusted automation: RLDYOUR_SKIP_CI_ADVISORY=1.
ADVISORY
    ;;
esac

exit 0
