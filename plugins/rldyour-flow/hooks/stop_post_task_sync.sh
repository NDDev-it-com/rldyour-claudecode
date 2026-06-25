#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

HOOK_INPUT=$(cat 2>/dev/null || true)

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

if [ ! -f "$STATE_SCRIPT" ]; then
  exit 0
fi

FLOW_STATE_TIMEOUT="${RLDYOUR_FLOW_STATE_TIMEOUT_SECONDS:-25}"
STATE_JSON=$(RLDYOUR_FLOW_STATE_LOCAL_ONLY=1 RLDYOUR_STATE_SCRIPT="$STATE_SCRIPT" RLDYOUR_STATE_PYTHON="${PYTHON_BIN:-python3}" RLDYOUR_FLOW_STATE_TIMEOUT_SECONDS="$FLOW_STATE_TIMEOUT" "${PYTHON_BIN:-python3}" <<'PY' 2>/dev/null || true
import os
import subprocess
import sys

raw_timeout = os.environ.get("RLDYOUR_FLOW_STATE_TIMEOUT_SECONDS", "25")
try:
    timeout = max(0.1, float(raw_timeout))
except ValueError:
    timeout = 25.0
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

SERENA_CURRENT=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("serena_current") else "false")' 2>/dev/null || echo "true")
NEEDS_SYNC=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("needs_flow_sync") else "false")' 2>/dev/null || echo "false")
FINGERPRINT=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("fingerprint", ""))' 2>/dev/null || true)
HEAD_SHA=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("head_sha", ""))' 2>/dev/null || true)
EXECUTION_MODE=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; p=json.load(sys.stdin).get("execution", {}); print(p.get("execution_mode", "standard") if isinstance(p, dict) else "standard")' 2>/dev/null || echo "standard")
AGENT_ROLE=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; p=json.load(sys.stdin).get("execution", {}); print(p.get("agent_role", "standalone") if isinstance(p, dict) else "standalone")' 2>/dev/null || echo "standalone")
WORKER_ID=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; p=json.load(sys.stdin).get("execution", {}); print(p.get("worker_id") or p.get("agent_role", "worker") if isinstance(p, dict) else "worker")' 2>/dev/null || echo "worker")

# Serena owns memory freshness. Flow waits for Serena Stop hook to finish first.
if [ "$SERENA_CURRENT" != "true" ]; then
  exit 0
fi

if [ "$NEEDS_SYNC" != "true" ] || [ -z "$FINGERPRINT" ]; then
  rm -f "$SYNC_MARKER" "$ACK_MARKER" .serena/.flow_post_task_state.json
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

if [ "$STOP_HOOK_ACTIVE" = "true" ] && [ -f "$SYNC_MARKER" ] && [ "$(cat "$SYNC_MARKER" 2>/dev/null || true)" = "$FINGERPRINT" ]; then
  mkdir -p .serena
  printf "%s" "$STATE_JSON" > .serena/.flow_post_task_state.json
  STATE_PATH=".serena/.flow_post_task_state.json" FINGERPRINT="$FINGERPRINT" HEAD_SHA="$HEAD_SHA" ACK_MARKER="$ACK_MARKER" python3 <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

state_path = Path(os.environ["STATE_PATH"])
try:
    state = json.loads(state_path.read_text(encoding="utf-8"))
except Exception:
    state = {}
policy = state.get("project_policy", {})
ack = {
    "schema_version": 1,
    "fingerprint": os.environ.get("FINGERPRINT", ""),
    "head": state.get("head_full") or os.environ.get("HEAD_SHA", ""),
    "reported_at": datetime.now(timezone.utc).isoformat(),
    "blocked_reasons": state.get("blocking_reasons", []),
    "advisory_reasons": state.get("advisory_reasons", []),
    "policy_source": policy.get("source", "built-in defaults") if isinstance(policy, dict) else "built-in defaults",
}
Path(os.environ["ACK_MARKER"]).write_text(json.dumps(ack, sort_keys=True) + "\n", encoding="utf-8")

print(json.dumps({
    "systemMessage": (
        "rldyour-flow worker report was already requested for this state. "
        "Allowing stop now to avoid a Stop-hook loop."
        if state.get("execution", {}).get("agent_role") == "worker"
        else
        "rldyour-flow post-task sync was already requested for this state. "
        "Allowing stop now to avoid a Stop-hook loop."
    )
}))
PY
  exit 0
fi

mkdir -p .serena
printf "%s\n" "$FINGERPRINT" > "$SYNC_MARKER"
printf "%s" "$STATE_JSON" > .serena/.flow_post_task_state.json

SUMMARY=$(printf "%s" "$STATE_JSON" | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
instruction_docs_state = payload.get("instruction_docs_state", {})
if not isinstance(instruction_docs_state, dict):
    instruction_docs_state = {}
branch_cleanup_state = payload.get("branch_cleanup_state", {})
if not isinstance(branch_cleanup_state, dict):
    branch_cleanup_state = {}
print(json.dumps({
    "branch": payload.get("branch"),
    "head": payload.get("head_sha"),
    "execution": payload.get("execution", {}),
    "dirty_files": payload.get("dirty_files", []),
    "doc_files_present": payload.get("doc_files_present", []),
    "doc_files_changed": payload.get("doc_files_changed", []),
    "ahead": payload.get("ahead", 0),
    "behind": payload.get("behind", 0),
    "worktree_count": payload.get("worktree_count", 0),
    "project_policy": {
        "source": payload.get("project_policy", {}).get("source") if isinstance(payload.get("project_policy"), dict) else None,
        "source_kind": payload.get("project_policy", {}).get("source_kind") if isinstance(payload.get("project_policy"), dict) else None,
        "profile": payload.get("project_policy", {}).get("profile") if isinstance(payload.get("project_policy"), dict) else None,
        "valid": payload.get("project_policy", {}).get("valid") if isinstance(payload.get("project_policy"), dict) else None,
    },
    "blocking_reasons": payload.get("blocking_reasons", []),
    "advisory_reasons": payload.get("advisory_reasons", []),
    "instruction_docs": {
        "mode": instruction_docs_state.get("instruction_docs_mode", "auto"),
        "required": instruction_docs_state.get("required_docs", []),
        "present": instruction_docs_state.get("present_docs", []),
        "missing": instruction_docs_state.get("missing_docs", []),
        "review_needed": bool(instruction_docs_state.get("needs_instruction_docs_review")),
        "review_reasons": instruction_docs_state.get("review_reasons", []),
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
}, ensure_ascii=False, indent=2))
')

POLICY_GUIDANCE=$(printf "%s" "$STATE_JSON" | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
policy = payload.get("project_policy", {})
effective = policy.get("effective", {}) if isinstance(policy, dict) else {}
branch_cleanup = effective.get("branch_cleanup", {}) if isinstance(effective.get("branch_cleanup"), dict) else {}
instruction_docs = effective.get("instruction_docs", {}) if isinstance(effective.get("instruction_docs"), dict) else {}

policy_source = policy.get("source", "built-in defaults")
policy_source_kind = policy.get("source_kind", "default")
lines = [
    f"Project policy source: {policy_source} ({policy_source_kind}).",
    "Agent context (.serena/, AGENTS.md, .claude/) is tracked normally on main; commit it as ordinary source.",
]

doc_mode = instruction_docs.get("mode", "tracked-main")
if doc_mode == "disabled":
    lines.append("Instruction docs sync is disabled unless the user explicitly requests it.")
else:
    lines.append("Instruction docs are tracked on main; keep AGENTS.md and .claude/CLAUDE.md current.")

cleanup_mode = branch_cleanup.get("mode", "advisory")
if cleanup_mode == "disabled":
    lines.append("Branch cleanup is disabled by project policy.")
elif cleanup_mode == "advisory":
    lines.append("Merged branch cleanup is advisory; do not delete local or remote branches without explicit user confirmation.")
else:
    lines.append("Branch cleanup is strict only for configured workflow prefixes; never delete protected branches.")

print("\n".join(lines))
')

if [ "$EXECUTION_MODE" = "orchestrator" ] && [ "$AGENT_ROLE" = "worker" ]; then
  MESSAGE="[RLDYOUR-FLOW CMUX WORKER REPORT REQUIRED] Worker state has policy-scoped blockers for HEAD ${HEAD_SHA:-unknown}; report to the orchestrator instead of running global sync.

Current state:
${SUMMARY}

Worker role: ${WORKER_ID}

Effective policy:
${POLICY_GUIDANCE}

Worker rules:
1. Do not push, force-push, delete branches, install system configs, or mutate project policy.
2. Do not run \$flow-post-task-sync unless the orchestrator explicitly delegates final sync.
3. If dirty files are outside assigned scope, stop and report the exact paths.
4. Return a structured worker report to the orchestrator:
{
  \"status\": \"pass|fail|blocked|not_proven\",
  \"files_changed\": [],
  \"commands_run\": [],
  \"findings\": [],
  \"risks\": [],
  \"needs_orchestrator_action\": []
}
5. Stop again after reporting or after the orchestrator delegates a specific cleanup."
else
  MESSAGE="[RLDYOUR-FLOW POST-TASK SYNC REQUIRED] Serena memories are current for HEAD ${HEAD_SHA:-unknown}; now synchronize project docs and git state.

Current state:
${SUMMARY}

Effective policy:
${POLICY_GUIDANCE}

Continue this turn and run the \$flow-post-task-sync workflow now.

Installed rldyour-flow script paths for repositories that do not vendor this plugin:
- Flow state: ${STATE_SCRIPT}
- Git sync audit: ${PLUGIN_DIR}/scripts/git_sync_audit.sh
- Instruction docs state: ${PLUGIN_DIR}/scripts/instruction_docs_state.py

Use repo-local scripts only when they exist; otherwise use the installed paths above.

Required order:
1. Verify Serena memories are current. Do not duplicate Serena memory sync.
2. Run \$instruction-docs-sync when instruction docs review is needed. Keep AGENTS.md Codex-native and .claude/CLAUDE.md Claude Code-native, using only verified project rules, commands, deploy contracts, quality gates, or workflow facts.
3. Review all uncommitted changes. Agent context (.serena/, AGENTS.md, .claude/) is tracked normally on main; commit it as ordinary source. Do not commit secrets, runtime markers, browser artifacts, or accidental junk.
4. Run applicable quality checks or document why a check is unavailable.
5. Commit atomically with Conventional Commits. Keep Serena knowledge/docs sync commits separate when useful.
6. Push/synchronize with GitHub using git/gh when an upstream exists.
7. Treat branch cleanup according to policy; never delete protected branches or remote branches without explicit confirmation.
8. Stop again after sync or report the exact blocker."
fi

echo "$MESSAGE" >&2
exit 2
