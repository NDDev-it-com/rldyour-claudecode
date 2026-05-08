#!/usr/bin/env bash
# stop_memory_sync.sh — advisory enforcement gate for Stop event.
#
# Behaviour: this hook does NOT mutate memories itself. Memory updates require
# code understanding and source-of-truth verification, which is the job of the
# flow-memory-sync subagent (or a fallback Serena workflow run from the main
# session). The hook computes machine-readable freshness via serena_memory_state.py
# and:
#   - exits 0 if memories already match HEAD (markers cleared);
#   - exits 0 if loop guard recognises the same HEAD already attempted;
#   - otherwise emits an advisory message via stderr and exits 2 (blocking),
#     forcing the orchestrator to invoke the flow-memory-sync subagent (or run
#     the equivalent Serena workflow) before the session is allowed to stop.

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
COMMIT_SCRIPT="$PLUGIN_DIR/scripts/commit_serena_knowledge.sh"
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
NEWEST_SHA=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("newest_synced_sha", ""))' 2>/dev/null || true)

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

COMMITS="(no prior synced memory commit metadata)"
if [ -n "$NEWEST_SHA" ]; then
  COMMITS=$(git log --oneline "${NEWEST_SHA}..HEAD" 2>/dev/null || echo "(unable to compute commit range)")
fi

NON_KNOWLEDGE_FILES=$(printf "%s" "$STATE_JSON" | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
files = payload.get("non_knowledge_changed_files_since_sync") or payload.get("sync_state", {}).get("changed_files", [])
print("\n".join(str(item) for item in files))
' 2>/dev/null || true)

MESSAGE="[RLDYOUR-SERENA SYNC REQUIRED] Project knowledge is stale for HEAD ${HEAD_SHA}.

Last synced memory commit: ${NEWEST_SHA:-none}

Relevant commits:
${COMMITS}

Changed non-Serena-knowledge files:
${NON_KNOWLEDGE_FILES:-unknown}

Continue this turn and run the serena-memory-sync workflow now.

Preferred path — invoke the flow-memory-sync subagent:

  Agent({
    description: 'Sync Serena memories against HEAD ${HEAD_SHA}',
    subagent_type: 'rldyour-serena-mcp:flow-memory-sync',
    prompt: 'Synchronize .serena/memories against HEAD ${HEAD_SHA}. Newest synced commit: ${NEWEST_SHA:-none}. Changed non-knowledge files: ${NON_KNOWLEDGE_FILES:-unknown}. Follow the agent definition strictly: source-of-truth hierarchy = code > tests > git diff > existing memories; never speculate; cite or omit; emit final JSON report.'
  })

The flow-memory-sync subagent has narrow tool access (Serena memory tools + Read/Grep/Glob/Bash; Edit/Write/NotebookEdit are disallowed in its frontmatter). It enforces fact-only updates with anti-hallucination guards and runs ${COMMIT_SCRIPT} at the end.

Fallback path (if the subagent is not available — e.g. plugin not yet reloaded):
1. Use Serena MCP for code inspection: check_onboarding_performed -> list_memories -> read_memory(relevant) -> get_symbols_overview -> find_symbol(include_body=false) -> find_symbol(include_body=true only where needed) -> find_referencing_symbols -> search_for_pattern.
2. Update .serena/memories with high-signal fact-only English content. Code, git diff, and tests are the source of truth.
3. Each touched memory must contain a 'Last commit: ${HEAD_SHA}' line so the state script recognises sync via direct-head-reference.
4. Run ${COMMIT_SCRIPT} to acknowledge sync state and clear runtime markers.
5. Stop again after the sync or report the exact blocker."

echo "$MESSAGE" >&2
exit 2
