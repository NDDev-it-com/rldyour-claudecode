#!/usr/bin/env bash
# stop_post_task_sync.sh - advisory enforcement gate for Stop event.
#
# Behaviour: this hook does NOT perform git push, merge, fullrepo publish, or
# branch/worktree cleanup. Those are high-blast-radius operations and belong to
# the workflow executor (flow-post-task-sync skill, ry-start, ry-deploy), not
# to a shell hook firing without LLM judgement.
#
# The hook computes machine-readable state via flow_post_task_state.py and:
#   - exits 0 if everything is already in order (markers cleared);
#   - exits 0 if Serena memory sync hasn't completed yet (defers to Serena hook);
#   - exits 0 if loop guard recognises the same fingerprint already attempted;
#   - otherwise emits an advisory message via stderr and exits 2 (blocking),
#     forcing the orchestrator to run the flow-post-task-sync workflow before
#     allowing the session to stop.

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

if [ "${RLDYOUR_SKIP_STOP_GATES:-0}" = "1" ] || [ "${RLDYOUR_SKIP_FLOW_SYNC:-0}" = "1" ]; then
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
SYNC_MARKER=".serena/.flow_sync_marker"
HOOK_INPUT=$(cat 2>/dev/null || true)

if [ ! -f "$STATE_SCRIPT" ]; then
  exit 0
fi

STATE_JSON=$(RLDYOUR_FLOW_STATE_LOCAL_ONLY=1 RLDYOUR_FULLREPO_STATUS_LOCAL_ONLY=1 "${PYTHON_BIN}" "$STATE_SCRIPT" 2>/dev/null || true)
if [ -z "$STATE_JSON" ]; then
  exit 0
fi

STATE_JSON="$STATE_JSON" HOOK_INPUT="$HOOK_INPUT" SYNC_MARKER="$SYNC_MARKER" "${PYTHON_BIN}" <<'PY'
import json
import os
import sys
from pathlib import Path

try:
    payload = json.loads(os.environ.get("HOOK_INPUT", "") or "{}")
except Exception:
    payload = {}

try:
    state = json.loads(os.environ.get("STATE_JSON", "") or "{}")
except Exception:
    raise SystemExit(0)

serena_current = bool(state.get("serena_current"))
needs_sync = bool(state.get("needs_flow_sync"))
fingerprint = str(state.get("fingerprint") or "")
head_sha = str(state.get("head_sha") or "")
sync_marker = Path(os.environ.get("SYNC_MARKER", ".serena/.flow_sync_marker"))
state_path = Path(".serena/.flow_post_task_state.json")

# Serena owns memory freshness. Flow waits for Serena Stop hook to finish first.
if not serena_current:
    raise SystemExit(0)

if not needs_sync or not fingerprint:
    sync_marker.unlink(missing_ok=True)
    state_path.unlink(missing_ok=True)
    raise SystemExit(0)

if payload.get("stop_hook_active") is True and sync_marker.is_file():
    try:
        marker = sync_marker.read_text(encoding="utf-8").strip()
    except OSError:
        marker = ""
    if marker == fingerprint:
        print(json.dumps({
            "systemMessage": (
                "rldyour-flow post-task sync was already requested for this state. "
                "Allowing stop now to avoid a Stop-hook loop."
            )
        }))
        raise SystemExit(0)

sync_marker.parent.mkdir(parents=True, exist_ok=True)
sync_marker.write_text(fingerprint + "\n", encoding="utf-8")
state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

fullrepo_state = state.get("fullrepo_state", {})
if not isinstance(fullrepo_state, dict):
    fullrepo_state = {}
instruction_docs_state = state.get("instruction_docs_state", {})
if not isinstance(instruction_docs_state, dict):
    instruction_docs_state = {}
tracked_agent_paths = fullrepo_state.get("tracked_agent_paths", [])
if not isinstance(tracked_agent_paths, list):
    tracked_agent_paths = []
branch_cleanup_state = state.get("branch_cleanup_state", {})
if not isinstance(branch_cleanup_state, dict):
    branch_cleanup_state = {}
summary = json.dumps({
    "branch": state.get("branch"),
    "head": state.get("head_sha"),
    "dirty_files": state.get("dirty_files", []),
    "doc_files_present": state.get("doc_files_present", []),
    "doc_files_changed": state.get("doc_files_changed", []),
    "ahead": state.get("ahead", 0),
    "behind": state.get("behind", 0),
    "worktree_count": state.get("worktree_count", 0),
    "instruction_docs": {
        "required": instruction_docs_state.get("required_docs", []),
        "present": instruction_docs_state.get("present_docs", []),
        "missing": instruction_docs_state.get("missing_docs", []),
        "review_needed": bool(instruction_docs_state.get("needs_instruction_docs_review")),
        "review_reasons": instruction_docs_state.get("review_reasons", []),
    },
    "fullrepo": {
        "branch": fullrepo_state.get("fullrepo_branch", "fullrepo"),
        "remote_exists": bool(fullrepo_state.get("remote_fullrepo_exists")),
        "exclude_installed": bool(fullrepo_state.get("exclude_installed", False)),
        "tracked_agent_paths": len(tracked_agent_paths),
    },
    "branch_cleanup": {
        "base": branch_cleanup_state.get("base"),
        "local_merged_branches": branch_cleanup_state.get("local_merged_branches", []),
        "remote_merged_branches": branch_cleanup_state.get("remote_merged_branches", []),
        "worktree_cleanup_candidates": branch_cleanup_state.get("worktree_cleanup_candidates", []),
        "needs_cleanup": bool(branch_cleanup_state.get("needs_cleanup")),
    },
}, ensure_ascii=False, indent=2)

message = f"""[RLDYOUR-FLOW POST-TASK SYNC REQUIRED] Serena memories are current for HEAD {head_sha or 'unknown'}; now synchronize project docs and git state.

Current state:
{summary}

Continue this turn and run the flow-post-task-sync workflow now.

Required order:
1. Verify Serena memories are current. Do not duplicate Serena memory sync.
2. Run instruction-docs-sync when instruction docs review is needed. Keep AGENTS.md as concise root project instructions and .claude/CLAUDE.md as Claude Code project memory, using only verified project rules, commands, deploy contracts, quality gates, or workflow facts.
3. Review all uncommitted changes. Do not commit secrets, runtime markers, browser artifacts, or accidental junk.
4. Run applicable quality checks or document why a check is unavailable.
5. Commit atomically with Conventional Commits. Keep Serena knowledge/docs sync commits separate when useful.
6. Push/synchronize with GitHub using git/gh when an upstream exists.
7. Restore or install .git/info/exclude for agent-only files, keep normal branch history clean, and publish fullrepo with safe --force-with-lease when agent-only files exist.
8. Clean merged worktrees and merged local/remote workflow branches only after confirming they are merged and safe to remove. Leave protected branches such as main and fullrepo.
9. Stop again after sync or report the exact blocker."""

print(message, file=sys.stderr)
raise SystemExit(2)
PY
