#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

INPUT=$(cat 2>/dev/null || true)
COMMAND=$(printf "%s" "$INPUT" | python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}

if str(payload.get("tool_name", "")).lower() != "bash":
    raise SystemExit(0)

tool_input = payload.get("tool_input", {})
if isinstance(tool_input, dict):
    print(str(tool_input.get("command", tool_input.get("cmd", ""))))
' 2>/dev/null || true)

if ! printf "%s" "$COMMAND" | grep -qE 'git[[:space:]]+(commit([[:space:]]|$)|merge([[:space:]]|$)|cherry-pick([[:space:]]|$)|rebase([[:space:]]|$)|am([[:space:]]|$))'; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

HEAD_FULL=$(git rev-parse HEAD 2>/dev/null || true)
if [ -z "$HEAD_FULL" ]; then
  exit 0
fi

mkdir -p .serena
printf "%s\n" "$HEAD_FULL" > .serena/.auto_sync_head
