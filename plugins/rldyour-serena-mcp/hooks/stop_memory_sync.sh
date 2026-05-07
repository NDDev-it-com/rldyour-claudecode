#!/usr/bin/env bash
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

Required actions:
1. Use Serena MCP as the primary source for code inspection:
   check_onboarding_performed -> list_memories -> read_memory(relevant) -> get_symbols_overview -> find_symbol(include_body=false) -> find_symbol(include_body=true only where needed) -> find_referencing_symbols -> search_for_pattern.
2. Update .serena/memories with high-signal fact-only English content. Each memory should preserve source-of-truth paths, entry points, current behavior, contracts/data, invariants, change rules, verification, and known gaps when relevant. Code, git diff, and tests are the source of truth.
3. Do not store chat history, generic advice, speculative plans, TODO lists, or secrets in memories. Preserve non-trivial plans in .serena/plans and long source-backed research in .serena/research only when useful for future sessions.
4. If only .serena/memories, .serena/plans, or .serena/research changed, run:
   ${COMMIT_SCRIPT}
   In fullrepo-managed projects this acknowledges current memories and leaves publishing to flow-post-task-sync instead of committing AI files to the current branch.
5. Stop again after the sync or report the exact blocker."

echo "$MESSAGE" >&2
exit 2
