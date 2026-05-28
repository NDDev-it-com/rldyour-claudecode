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
TIMEOUT_MARKER=".serena/.stop_lifecycle_timeout_marker"

STOP_HOOK_ACTIVE=$(python3 - "$HOOK_INPUT_FILE" <<'PY' 2>/dev/null || echo "false"
import json
import sys
from pathlib import Path

try:
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace"))
except Exception:
    payload = {}
print("true" if payload.get("stop_hook_active") is True else "false")
PY
)

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || pwd
}

timeout_fingerprint() {
  local child_name=$1
  local root head branch dirty_hash
  root=$(repo_root)
  head=$(git -C "$root" rev-parse HEAD 2>/dev/null || echo "no-head")
  branch=$(git -C "$root" branch --show-current 2>/dev/null || echo "detached")
  dirty_hash=$(git -C "$root" status --porcelain=v1 -z -uall 2>/dev/null \
    | tr '\0' '\n' \
    | grep -Ev '^.. \.serena/\.(sync_marker|serena_sync_state\.json|auto_sync_head|active_workflow_intent\.json|dirty_stop_ack|flow_sync_marker|flow_post_task_state\.json|stop_lifecycle_timeout_marker)$' \
    | shasum -a 256 | awk '{print $1}')
  printf '%s:%s:%s:%s\n' "$child_name" "$head" "$branch" "$dirty_hash"
}

handle_timeout() {
  local child_name=$1
  local timeout_seconds=$2
  local plugin_dir=$3
  local fingerprint root marker_text
  root=$(repo_root)
  fingerprint=$(timeout_fingerprint "$child_name")
  marker_text=$(cat "$root/$TIMEOUT_MARKER" 2>/dev/null || true)

  if [ "$STOP_HOOK_ACTIVE" = "true" ] && [ "$marker_text" = "$fingerprint" ]; then
    python3 - <<'PY'
import json

print(json.dumps({
    "systemMessage": (
        "rldyour Stop lifecycle check timed out again for the same state. "
        "Allowing stop now to avoid a Stop-hook timeout loop; run the sync "
        "workflow manually if the project still needs finalization."
    )
}))
PY
    exit 0
  fi

  mkdir -p "$root/.serena"
  printf '%s\n' "$fingerprint" > "$root/$TIMEOUT_MARKER"
  printf '%s\n' "[RLDYOUR-${child_name} STOP CHECK TIMEOUT] Stop lifecycle child check exceeded ${timeout_seconds}s. Continue this turn and run the matching sync workflow or inspect ${plugin_dir} manually, then stop again. If Claude invokes Stop again with the same state, the timeout loop guard will allow Stop." >&2
  exit 2
}

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
  SERENA_OUTPUT=$(run_stop_child "$SERENA_PLUGIN_DIR/hooks/stop_memory_sync.sh" "${RLDYOUR_STOP_SERENA_TIMEOUT:-15}")
  SERENA_STATUS=$?
  set -e
  if [ -n "$SERENA_OUTPUT" ]; then
    if [ "$SERENA_STATUS" -eq 0 ]; then
      printf '%s\n' "$SERENA_OUTPUT"
    else
      printf '%s\n' "$SERENA_OUTPUT" >&2
    fi
  fi
  if [ "$SERENA_STATUS" -eq 124 ]; then
    handle_timeout "SERENA" "${RLDYOUR_STOP_SERENA_TIMEOUT:-15}" "$SERENA_PLUGIN_DIR"
  fi
  if [ "$SERENA_STATUS" -ne 0 ]; then
    exit "$SERENA_STATUS"
  fi
fi

set +e
FLOW_OUTPUT=$(run_stop_child "$FLOW_PLUGIN_DIR/hooks/stop_post_task_sync.sh" "${RLDYOUR_STOP_FLOW_TIMEOUT:-25}")
FLOW_STATUS=$?
set -e
if [ -n "$FLOW_OUTPUT" ]; then
  if [ "$FLOW_STATUS" -eq 0 ]; then
    printf '%s\n' "$FLOW_OUTPUT"
  else
    printf '%s\n' "$FLOW_OUTPUT" >&2
  fi
fi
if [ "$FLOW_STATUS" -eq 124 ]; then
  handle_timeout "FLOW" "${RLDYOUR_STOP_FLOW_TIMEOUT:-25}" "$FLOW_PLUGIN_DIR"
fi
rm -f "$(repo_root)/$TIMEOUT_MARKER"
exit "$FLOW_STATUS"
