#!/usr/bin/env bash
set -euo pipefail

emit_additional_context() {
  python3 - "$1" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": sys.argv[1],
            }
        }
    )
)
PY
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

MARKER=".serena/.auto_sync_head"
if [ ! -f "$MARKER" ]; then
  exit 0
fi

cleanup() {
  rm -f "$MARKER"
}
trap cleanup EXIT

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

PRE_HEAD=$(cat "$MARKER" 2>/dev/null || true)
CUR_HEAD=$(git rev-parse HEAD 2>/dev/null || true)
CUR_HEAD_SHORT=$(git rev-parse --short=7 HEAD 2>/dev/null || true)
if [ -z "$PRE_HEAD" ] || [ -z "$CUR_HEAD" ] || [ "$PRE_HEAD" = "$CUR_HEAD" ]; then
  exit 0
fi

HEAD_NON_KNOWLEDGE=$(git show --name-only --pretty= HEAD 2>/dev/null \
  | grep -vE '^$|^\.serena/(memories|plans|research)/|^\.serena/(\.sync_marker|\.serena_sync_state\.json|\.auto_sync_head|\.active_workflow_intent\.json|\.dirty_stop_ack)$' || true)
if [ -z "$HEAD_NON_KNOWLEDGE" ]; then
  exit 0
fi

mkdir -p .serena
python3 - "$PRE_HEAD" "$CUR_HEAD" "$CUR_HEAD_SHORT" "$HEAD_NON_KNOWLEDGE" <<'PY'
import json
import sys
import time
from pathlib import Path

previous, head, short, files = sys.argv[1:5]
payload = {
    "version": 1,
    "required": True,
    "reason": "git change touched non-Serena-knowledge files",
    "created_at": int(time.time()),
    "previous_head_full": previous,
    "head_full": head,
    "head_sha": short,
    "changed_files": [line for line in files.splitlines() if line],
}
Path(".serena/.serena_sync_state.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

emit_additional_context "[RLDYOUR-SERENA] Commit ${CUR_HEAD_SHORT} changed project code/config/docs. The Stop hook will require serena-memory-sync before final stop."
