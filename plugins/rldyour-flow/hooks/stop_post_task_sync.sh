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
ACK_MARKER=".serena/.flow_blocker_ack.json"
HOOK_INPUT=$(cat 2>/dev/null || true)

if [ ! -f "$STATE_SCRIPT" ]; then
  exit 0
fi

FLOW_STATE_TIMEOUT="${RLDYOUR_FLOW_STATE_TIMEOUT_SECONDS:-10}"
STATE_JSON=$(RLDYOUR_FLOW_STATE_LOCAL_ONLY=1 RLDYOUR_FULLREPO_STATUS_LOCAL_ONLY=1 RLDYOUR_STATE_SCRIPT="$STATE_SCRIPT" RLDYOUR_STATE_PYTHON="$PYTHON_BIN" RLDYOUR_FLOW_STATE_TIMEOUT_SECONDS="$FLOW_STATE_TIMEOUT" "${PYTHON_BIN}" <<'PY' 2>/dev/null || true
import os
import subprocess
import sys

raw_timeout = os.environ.get("RLDYOUR_FLOW_STATE_TIMEOUT_SECONDS", "10")
try:
    timeout = max(0.1, float(raw_timeout))
except ValueError:
    timeout = 10.0
try:
    proc = subprocess.run(
        [os.environ["RLDYOUR_STATE_PYTHON"], os.environ["RLDYOUR_STATE_SCRIPT"]],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
except subprocess.TimeoutExpired:
    raise SystemExit(0)
if proc.returncode == 0:
    sys.stdout.write(proc.stdout)
PY
)
if [ -z "$STATE_JSON" ]; then
  exit 0
fi

STATE_JSON="$STATE_JSON" HOOK_INPUT="$HOOK_INPUT" SYNC_MARKER="$SYNC_MARKER" ACK_MARKER="$ACK_MARKER" "${PYTHON_BIN}" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone
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
ack_marker = Path(os.environ.get("ACK_MARKER", ".serena/.flow_blocker_ack.json"))
state_path = Path(".serena/.flow_post_task_state.json")

# Serena owns memory freshness. The dispatcher runs that child gate before this one.
if not serena_current:
    raise SystemExit(0)

if not needs_sync or not fingerprint:
    sync_marker.unlink(missing_ok=True)
    ack_marker.unlink(missing_ok=True)
    state_path.unlink(missing_ok=True)
    raise SystemExit(0)

if payload.get("stop_hook_active") is True and sync_marker.is_file():
    try:
        marker = sync_marker.read_text(encoding="utf-8").strip()
    except OSError:
        marker = ""
    if marker == fingerprint:
        policy = state.get("project_policy", {})
        execution = state.get("execution", {})
        is_worker = isinstance(execution, dict) and execution.get("agent_role") == "worker"
        ack = {
            "schema_version": 1,
            "fingerprint": fingerprint,
            "head": state.get("head_full") or head_sha,
            "reported_at": datetime.now(timezone.utc).isoformat(),
            "blocked_reasons": state.get("blocking_reasons", []),
            "advisory_reasons": state.get("advisory_reasons", []),
            "policy_source": policy.get("source", "built-in defaults") if isinstance(policy, dict) else "built-in defaults",
        }
        ack_marker.write_text(json.dumps(ack, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "systemMessage": (
                "rldyour-flow worker report was already requested for this state. "
                "Allowing stop now to avoid a Stop-hook loop."
                if is_worker
                else
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
project_policy = state.get("project_policy", {})
if not isinstance(project_policy, dict):
    project_policy = {}
summary = json.dumps({
    "branch": state.get("branch"),
    "head": state.get("head_sha"),
    "execution": state.get("execution", {}),
    "dirty_files": state.get("dirty_files", []),
    "doc_files_present": state.get("doc_files_present", []),
    "doc_files_changed": state.get("doc_files_changed", []),
    "ahead": state.get("ahead", 0),
    "behind": state.get("behind", 0),
    "worktree_count": state.get("worktree_count", 0),
    "project_policy": {
        "source": project_policy.get("source"),
        "source_kind": project_policy.get("source_kind"),
        "profile": project_policy.get("profile"),
        "valid": project_policy.get("valid"),
    },
    "blocking_reasons": state.get("blocking_reasons", []),
    "advisory_reasons": state.get("advisory_reasons", []),
    "instruction_docs": {
        "mode": instruction_docs_state.get("instruction_docs_mode", "auto"),
        "required": instruction_docs_state.get("required_docs", []),
        "present": instruction_docs_state.get("present_docs", []),
        "missing": instruction_docs_state.get("missing_docs", []),
        "review_needed": bool(instruction_docs_state.get("needs_instruction_docs_review")),
        "review_reasons": instruction_docs_state.get("review_reasons", []),
    },
    "fullrepo": {
        "mode": fullrepo_state.get("mode", "auto"),
        "branch": fullrepo_state.get("fullrepo_branch", "fullrepo"),
        "remote_exists": bool(fullrepo_state.get("remote_fullrepo_exists")),
        "exclude_installed": bool(fullrepo_state.get("exclude_installed", False)),
        "tracked_agent_paths": len(tracked_agent_paths),
    },
    "branch_cleanup": {
        "mode": branch_cleanup_state.get("mode", "advisory"),
        "base": branch_cleanup_state.get("base"),
        "local_merged_branches": branch_cleanup_state.get("local_merged_branches", []),
        "remote_merged_branches": branch_cleanup_state.get("remote_merged_branches", []),
        "blocking_candidates": branch_cleanup_state.get("blocking_candidates", []),
        "advisory_candidates": branch_cleanup_state.get("advisory_candidates", []),
        "worktree_cleanup_candidates": branch_cleanup_state.get("worktree_cleanup_candidates", []),
        "needs_cleanup": bool(branch_cleanup_state.get("needs_cleanup")),
    },
}, ensure_ascii=False, indent=2)

effective = project_policy.get("effective", {})
if not isinstance(effective, dict):
    effective = {}
fullrepo_policy = effective.get("fullrepo", {}) if isinstance(effective.get("fullrepo"), dict) else {}
normal_policy = (
    effective.get("normal_branch_policy", {}) if isinstance(effective.get("normal_branch_policy"), dict) else {}
)
instruction_policy = (
    effective.get("instruction_docs", {}) if isinstance(effective.get("instruction_docs"), dict) else {}
)
cleanup_policy = (
    effective.get("branch_cleanup", {}) if isinstance(effective.get("branch_cleanup"), dict) else {}
)
policy_lines = [
    f"Project policy source: {project_policy.get('source', 'built-in defaults')} ({project_policy.get('source_kind', 'default')})."
]
fullrepo_mode = fullrepo_policy.get("mode", "auto")
if fullrepo_mode == "disabled":
    policy_lines.append("Fullrepo is disabled by project policy; do not restore, migrate, publish, create, or install fullrepo excludes.")
elif fullrepo_mode == "advisory":
    policy_lines.append("Fullrepo is advisory; report drift but do not block Stop or publish without explicit user instruction.")
else:
    policy_lines.append("Use fullrepo only when the effective project policy requires or allows it; do not create a missing fullrepo branch unless policy or current user instruction explicitly allows creation.")
if normal_policy.get("agent_files") == "allowed":
    policy_lines.append("Configured AI instruction files may be tracked in normal branches; do not migrate them to fullrepo.")
doc_mode = instruction_policy.get("mode", "auto")
if doc_mode == "tracked-normal-branch":
    policy_lines.append("Instruction docs are tracked normal-branch files for this project.")
elif doc_mode == "disabled":
    policy_lines.append("Instruction docs sync is disabled unless the user explicitly requests it.")
cleanup_mode = cleanup_policy.get("mode", "advisory")
if cleanup_mode == "disabled":
    policy_lines.append("Branch cleanup is disabled by project policy.")
elif cleanup_mode == "advisory":
    policy_lines.append("Merged branch cleanup is advisory; do not delete local or remote branches without explicit user confirmation.")
else:
    policy_lines.append("Branch cleanup is strict only for configured workflow prefixes; never delete protected branches.")
policy_guidance = "\n".join(policy_lines)

execution_state = state.get("execution", {})
if not isinstance(execution_state, dict):
    execution_state = {}
is_worker = execution_state.get("execution_mode") == "orchestrator" and execution_state.get("agent_role") == "worker"

if is_worker:
    message = f"""[RLDYOUR-FLOW CMUX WORKER REPORT REQUIRED] Worker state has policy-scoped blockers for HEAD {head_sha or 'unknown'}; report to the orchestrator instead of running global sync.

Current state:
{summary}

Worker role: {execution_state.get('worker_id') or execution_state.get('agent_role') or 'worker'}

Effective policy:
{policy_guidance}

Worker rules:
1. Do not run fullrepo publish/migrate/install-exclude.
2. Do not push, force-push, delete branches, install system configs, or mutate project policy.
3. Do not run flow-post-task-sync unless the orchestrator explicitly delegates final sync.
4. If dirty files are outside assigned scope, stop and report the exact paths.
5. Return a structured worker report to the orchestrator:
{{
  "status": "pass|fail|blocked|not_proven",
  "files_changed": [],
  "commands_run": [],
  "findings": [],
  "risks": [],
  "needs_orchestrator_action": []
}}
6. Stop again after reporting or after the orchestrator delegates a specific cleanup."""
else:
    message = f"""[RLDYOUR-FLOW POST-TASK SYNC REQUIRED] Serena memories are current for HEAD {head_sha or 'unknown'}; now synchronize project docs and git state.

Current state:
{summary}

Effective policy:
{policy_guidance}

Continue this turn and run the flow-post-task-sync workflow now.

Required order:
1. Verify Serena memories are current. Do not duplicate Serena memory sync.
2. Run instruction-docs-sync when instruction docs review is needed. Keep AGENTS.md as concise root project instructions and .claude/CLAUDE.md as Claude Code project memory, using only verified project rules, commands, deploy contracts, quality gates, or workflow facts.
3. Review all uncommitted changes. Do not commit secrets, runtime markers, browser artifacts, or accidental junk.
4. Run applicable quality checks or document why a check is unavailable.
5. Commit atomically with Conventional Commits. Keep Serena knowledge/docs sync commits separate when useful.
6. Push/synchronize with GitHub using git/gh when an upstream exists.
7. Follow the effective fullrepo policy above; publish or migrate fullrepo only when policy and current user instruction allow it.
8. Treat branch cleanup according to policy; never delete protected branches or remote branches without explicit confirmation.
9. Stop again after sync or report the exact blocker."""

print(message, file=sys.stderr)
raise SystemExit(2)
PY
