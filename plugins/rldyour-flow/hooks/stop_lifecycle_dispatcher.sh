#!/usr/bin/env bash
# stop_lifecycle_dispatcher.sh - serialize Serena memory gate before Flow sync gate.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

HOOK_INPUT_FILE=$(mktemp)
trap 'rm -f "$HOOK_INPUT_FILE"' EXIT
cat >"$HOOK_INPUT_FILE" 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLOW_PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

find_serena_plugin_dir() {
  local candidate
  if [ -n "${RLDYOUR_SERENA_PLUGIN_ROOT:-}" ] && [ -f "$RLDYOUR_SERENA_PLUGIN_ROOT/hooks/stop_memory_sync.sh" ]; then
    printf '%s\n' "$RLDYOUR_SERENA_PLUGIN_ROOT"
    return 0
  fi

  for candidate in \
    "$FLOW_PLUGIN_DIR/../rldyour-serena-mcp" \
    "$FLOW_PLUGIN_DIR/../../rldyour-serena-mcp/local"; do
    if [ -f "$candidate/hooks/stop_memory_sync.sh" ]; then
      (cd "$candidate" && pwd)
      return 0
    fi
  done

  if ROOT=$(git -C "$FLOW_PLUGIN_DIR" rev-parse --show-toplevel 2>/dev/null); then
    candidate="$ROOT/plugins/rldyour-serena-mcp"
    if [ -f "$candidate/hooks/stop_memory_sync.sh" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  fi

  return 1
}

run_stop_child() {
  local script_path=$1
  local timeout_seconds=$2

  python3 - "$script_path" "$timeout_seconds" "$HOOK_INPUT_FILE" <<'PY'
from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

script_path = sys.argv[1]
timeout_seconds = float(sys.argv[2])
input_file = Path(sys.argv[3])

with input_file.open("r", encoding="utf-8", errors="replace") as stdin:
    proc = subprocess.Popen(
        ["bash", script_path],
        stdin=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        output, _ = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            output, _ = proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            output, _ = proc.communicate()
        sys.stdout.write(output or "")
        raise SystemExit(124)

sys.stdout.write(output or "")
raise SystemExit(proc.returncode)
PY
}

if SERENA_PLUGIN_DIR=$(find_serena_plugin_dir); then
  set +e
  SERENA_OUTPUT=$(run_stop_child "$SERENA_PLUGIN_DIR/hooks/stop_memory_sync.sh" "${RLDYOUR_STOP_SERENA_TIMEOUT:-8}")
  SERENA_STATUS=$?
  set -e
  if [ -n "$SERENA_OUTPUT" ]; then
    printf '%s\n' "$SERENA_OUTPUT" >&2
  fi
  if [ "$SERENA_STATUS" -eq 124 ]; then
    printf '%s\n' "[RLDYOUR-SERENA STOP CHECK TIMEOUT] Serena memory freshness check exceeded ${RLDYOUR_STOP_SERENA_TIMEOUT:-8}s. Continue this turn and run the serena-memory-sync workflow or python3 ${SERENA_PLUGIN_DIR}/scripts/serena_memory_state.py manually, then stop again." >&2
    exit 2
  fi
  if [ "$SERENA_STATUS" -ne 0 ]; then
    exit "$SERENA_STATUS"
  fi
fi

set +e
FLOW_OUTPUT=$(run_stop_child "$FLOW_PLUGIN_DIR/hooks/stop_post_task_sync.sh" "${RLDYOUR_STOP_FLOW_TIMEOUT:-10}")
FLOW_STATUS=$?
set -e
if [ -n "$FLOW_OUTPUT" ]; then
  printf '%s\n' "$FLOW_OUTPUT" >&2
fi
if [ "$FLOW_STATUS" -eq 124 ]; then
  printf '%s\n' "[RLDYOUR-FLOW STOP CHECK TIMEOUT] Flow post-task state check exceeded ${RLDYOUR_STOP_FLOW_TIMEOUT:-10}s. Continue this turn and run the flow-post-task-sync workflow or python3 ${FLOW_PLUGIN_DIR}/scripts/flow_post_task_state.py manually, then stop again." >&2
  exit 2
fi
exit "$FLOW_STATUS"
