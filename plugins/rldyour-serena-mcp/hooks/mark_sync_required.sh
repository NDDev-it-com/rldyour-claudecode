#!/usr/bin/env bash
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

emit_additional_context() {
  "${PYTHON_BIN}" - "$1" <<'PY'
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
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

MARKER=".serena/.auto_sync_head"
if [ ! -f "$MARKER" ]; then
  exit 0
fi

ANALYSIS_FILE=""
cleanup() {
  rm -f "$MARKER"
  if [ -n "$ANALYSIS_FILE" ]; then
    rm -f "$ANALYSIS_FILE"
  fi
}
trap cleanup EXIT

INPUT=$(cat 2>/dev/null || true)
COMMAND=$(printf "%s" "$INPUT" | "${PYTHON_BIN}" -c '
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

ANALYSIS_FILE="$(mktemp)"
if ! "${PYTHON_BIN}" "$PLUGIN_DIR/scripts/analyze_sync_scope.py" --from-ref "$PRE_HEAD" --to-ref "$CUR_HEAD" >"$ANALYSIS_FILE" 2>/dev/null; then
  printf '{}\n' >"$ANALYSIS_FILE"
fi

mkdir -p .serena
"${PYTHON_BIN}" - "$PRE_HEAD" "$CUR_HEAD" "$CUR_HEAD_SHORT" "$ANALYSIS_FILE" <<'PY'
import json
import subprocess
import sys
import time
from pathlib import Path

previous, head, short, analysis_file = sys.argv[1:5]
try:
    analysis_text = Path(analysis_file).read_text(encoding="utf-8")
    analysis = json.loads(analysis_text) if analysis_text.strip() else {}
except (OSError, json.JSONDecodeError):
    analysis = {}

SERENA_KNOWLEDGE_PREFIXES = (
    ".serena/memories/",
    ".serena/plans/",
    ".serena/research/",
    ".serena/newproj/",
    ".serena/deploy/",
)

# Mirror of serena_memory_state.AGENT_INSTRUCTION_PATHS. Kept inline because
# this hook runs in a separate Python heredoc subprocess without import access
# to the plugin scripts. Drift between the two definitions is asserted by
# `tests/test_serena_memory_state.py::test_inline_hook_path_canon_matches`.
AGENT_INSTRUCTION_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    "REVIEW.md",
    "GEMINI.md",
    "QWEN.md",
    ".cursorrules",
    ".windsurfrules",
    ".aider",
    ".claude/",
    ".codex/",
    ".cursor/",
    ".gemini/",
    ".windsurf/",
    ".roo/",
    ".openhands/",
    ".github/copilot-instructions.md",
    ".github/instructions/",
    ".github/prompts/",
    ".agents/skills/",
    ".agents/commands/",
    ".agents/hooks/",
    ".serena/project.yml",
)

RUNTIME_IGNORED = {
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
    ".serena/.stop_lifecycle_timeout_marker",
}


def is_knowledge_path(path: str) -> bool:
    if any(path.startswith(prefix) for prefix in SERENA_KNOWLEDGE_PREFIXES):
        return True
    # See serena_memory_state.py:_is_knowledge_path for matching semantics
    # (directory prefixes use startswith; exact files use equality;
    # '.aider' is the dotfile-family prefix). Drift caught by
    # tests/test_serena_memory_state.py::TestInlineHookCanonDrift.
    for ai_path in AGENT_INSTRUCTION_PATHS:
        if ai_path.endswith("/"):
            if path.startswith(ai_path):
                return True
        elif ai_path == ".aider":
            if path == ai_path or path.startswith(".aider"):
                return True
        else:
            if path == ai_path:
                return True
    return False

changed_files = analysis.get("changed_files") or []
if not isinstance(changed_files, list):
    changed_files = []
if not changed_files:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{previous}..{head}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        changed_files = [line.strip() for line in proc.stdout.splitlines() if line.strip()]

non_knowledge_files = [
    path
    for path in changed_files
    if isinstance(path, str)
    and path.strip()
    and path not in RUNTIME_IGNORED
    and not is_knowledge_path(path)
]

payload = {
    "version": 1,
    "required": bool(non_knowledge_files),
    "reason": "git change touched non-Serena-knowledge files",
    "created_at": int(time.time()),
    "previous_head_full": previous,
    "head_full": head,
    "head_sha": short,
    "changed_files": changed_files,
    "non_knowledge_changed_files": non_knowledge_files,
    "analysis": analysis,
}
Path(".serena/.serena_sync_state.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

HEAD_NON_KNOWLEDGE=$("${PYTHON_BIN}" - <<'PY'
import json
try:
    payload = json.loads(open(".serena/.serena_sync_state.json", "r", encoding="utf-8").read())
except Exception:
    payload = {}
for path in payload.get("non_knowledge_changed_files", []):
    if isinstance(path, str):
        print(path)
PY
)
if [ -z "$HEAD_NON_KNOWLEDGE" ]; then
  exit 0
fi

emit_additional_context "[RLDYOUR-SERENA] Commit ${CUR_HEAD_SHORT} changed project code/config/docs. The Stop hook will require serena-memory-sync before final stop."
