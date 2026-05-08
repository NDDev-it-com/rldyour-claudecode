#!/usr/bin/env bash
# stop_memory_sync.sh — gate for Stop hook chain.
#
# Behaviour:
#   - If memory state is_current → remove runtime markers, exit 0 (silent allow).
#   - If loop guard matches (stop_hook_active=true + same fingerprint) → exit 0.
#   - Otherwise: write fingerprint marker, exit 0 (allow chain to continue —
#     the type:agent handler in the same matcher block will run automatically
#     and synchronise memories without main-session intervention).
#
# This script no longer emits an advisory message or exit 2. The advisory
# was a fallback for the old manual-sync flow; memory sync is now handled
# automatically by the agent handler defined in hooks.json.

set -euo pipefail

if [ "${RLDYOUR_SKIP_STOP_GATES:-0}" = "1" ] || [ "${RLDYOUR_SKIP_SERENA_SYNC:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_SCRIPT="$PLUGIN_DIR/scripts/serena_memory_state.py"
SYNC_MARKER=".serena/.sync_marker"
HOOK_INPUT=$(cat 2>/dev/null || true)

if [ ! -f "$STATE_SCRIPT" ]; then
  exit 0
fi

STATE_JSON=$(python3 "$STATE_SCRIPT" 2>/dev/null || true)
if [ -z "$STATE_JSON" ]; then
  exit 0
fi

IS_CURRENT=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("is_current") else "false")' 2>/dev/null || echo "true")
HEAD_SHA=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("head_sha", ""))' 2>/dev/null || true)

if [ "$IS_CURRENT" = "true" ]; then
  rm -f "$SYNC_MARKER" .serena/.serena_sync_state.json
  exit 0
fi

if [ -z "$HEAD_SHA" ]; then
  exit 0
fi

STOP_HOOK_ACTIVE=$(printf "%s" "$HOOK_INPUT" | python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}

print("true" if payload.get("stop_hook_active") is True else "false")
' 2>/dev/null || echo "false")

if [ "$STOP_HOOK_ACTIVE" = "true" ] && [ -f "$SYNC_MARKER" ] && [ "$(cat "$SYNC_MARKER" 2>/dev/null || true)" = "$HEAD_SHA" ]; then
  exit 0
fi

mkdir -p .serena
printf "%s\n" "$HEAD_SHA" > "$SYNC_MARKER"

# Memory sync is performed by the type:agent handler in hooks.json; this gate
# script just records the fingerprint and exits 0. The agent does its own
# is_current re-check at the start of its workflow as a safety net.
exit 0
