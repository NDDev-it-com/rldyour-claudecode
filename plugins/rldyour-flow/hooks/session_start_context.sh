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

if [ "${RLDYOUR_SKIP_FLOW_SESSION_CONTEXT:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_SCRIPT="$PLUGIN_DIR/scripts/flow_post_task_state.py"
HOOK_INPUT=$(cat 2>/dev/null || true)

if [ ! -f "$STATE_SCRIPT" ]; then
  exit 0
fi

STATE_JSON=$("${PYTHON_BIN}" "$STATE_SCRIPT" 2>/dev/null || true)
if [ -z "$STATE_JSON" ]; then
  exit 0
fi

SOURCE=$(printf "%s" "$HOOK_INPUT" | "${PYTHON_BIN}" -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}

source = payload.get("source", "unknown")
print(source if isinstance(source, str) else "unknown")
' 2>/dev/null || echo "unknown")

CONTEXT=$("${PYTHON_BIN}" - "$ROOT" "$SOURCE" "$STATE_JSON" <<'PY'
import json
import sys

root, source, raw_state = sys.argv[1:4]

try:
    state = json.loads(raw_state)
except json.JSONDecodeError:
    raise SystemExit(0)

dirty_files = state.get("dirty_files", [])
if not isinstance(dirty_files, list):
    dirty_files = []

shown_dirty = dirty_files[:12]
remaining_dirty = max(len(dirty_files) - len(shown_dirty), 0)

serena_state = state.get("serena_state", {})
if not isinstance(serena_state, dict):
    serena_state = {}

serena_current = state.get("serena_current", True)
serena_text = "current" if serena_current else "stale"
memory_count = serena_state.get("memory_count")
newest_synced = serena_state.get("newest_synced_sha") or "none"
fullrepo_state = state.get("fullrepo_state", {})
if not isinstance(fullrepo_state, dict):
    fullrepo_state = {}
tracked_agent_paths = fullrepo_state.get("tracked_agent_paths", [])
if not isinstance(tracked_agent_paths, list):
    tracked_agent_paths = []
branch_cleanup_state = state.get("branch_cleanup_state", {})
if not isinstance(branch_cleanup_state, dict):
    branch_cleanup_state = {}
local_merged = branch_cleanup_state.get("local_merged_branches", [])
if not isinstance(local_merged, list):
    local_merged = []
remote_merged = branch_cleanup_state.get("remote_merged_branches", [])
if not isinstance(remote_merged, list):
    remote_merged = []
worktree_cleanup = branch_cleanup_state.get("worktree_cleanup_candidates", [])
if not isinstance(worktree_cleanup, list):
    worktree_cleanup = []

lines = [
    "rldyour-flow session context (non-blocking, read-only):",
    f"- Session source: {source}.",
    f"- Repository: {root}.",
    (
        "- Git: "
        f"branch {state.get('branch') or 'unknown'}, "
        f"HEAD {state.get('head_sha') or 'unknown'}, "
        f"upstream {state.get('upstream') or 'none'}, "
        f"ahead {state.get('ahead', 0)}, behind {state.get('behind', 0)}."
    ),
    f"- Worktrees detected: {state.get('worktree_count', 0)}.",
    (
        "- Serena memories: "
        f"{serena_text}, memory_count {memory_count if memory_count is not None else 'unknown'}, "
        f"newest synced commit {newest_synced}."
    ),
    (
        "- Fullrepo sync: "
        f"branch {fullrepo_state.get('fullrepo_branch', 'fullrepo')}, "
        f"remote exists {bool(fullrepo_state.get('remote_fullrepo_exists'))}, "
        f"exclude installed {bool(fullrepo_state.get('exclude_installed', False))}, "
        f"tracked agent-only paths {len(tracked_agent_paths)}."
    ),
    (
        "- Branch cleanup: "
        f"base {branch_cleanup_state.get('base') or 'unknown'}, "
        f"local merged {len(local_merged)}, "
        f"remote merged {len(remote_merged)}, "
        f"worktree candidates {len(worktree_cleanup)}."
    ),
]

if dirty_files:
    lines.append(f"- Dirty files ({len(dirty_files)}):")
    lines.extend(f"  - {path}" for path in shown_dirty)
    if remaining_dirty:
        lines.append(f"  - ... plus {remaining_dirty} more")
else:
    lines.append("- Dirty files: none.")

doc_files = state.get("doc_files_present", [])
if doc_files:
    lines.append("- Project instruction docs present: " + ", ".join(str(item) for item in doc_files) + ".")

if state.get("needs_flow_sync"):
    lines.append(
        "- Flow sync signal: pending. Before final delivery, run flow-post-task-sync after Serena memories are current and publish fullrepo when agent-only files exist."
    )
else:
    lines.append("- Flow sync signal: clean.")

lines.extend(
    [
        "- If a task starts with insufficient context, trigger scoped ry-init before editing.",
        "- At init, restore agent-only context from fullrepo when available before relying on AGENTS.md, CLAUDE.md, or .serena knowledge.",
        "- Before edits, pass the context sufficiency gate: code paths, symbols, data contracts, integration points, existing patterns, checks, and research evidence must be known or explicitly marked as unknown.",
        "- This context is advisory only. Do not block execution only because this hook emitted warnings.",
    ]
)

print("\n".join(lines))
PY
)

if [ -z "$CONTEXT" ]; then
  exit 0
fi

"${PYTHON_BIN}" - "$CONTEXT" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": sys.argv[1],
            }
        }
    )
)
PY
