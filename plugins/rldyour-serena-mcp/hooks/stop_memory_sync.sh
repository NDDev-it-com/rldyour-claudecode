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

Required action — invoke the flow-memory-sync subagent now (do NOT inline-edit memories from the main session):

  Agent({
    description: 'Sync Serena memories against HEAD ${HEAD_SHA}',
    subagent_type: 'rldyour-serena-mcp:flow-memory-sync',
    prompt: 'Synchronize .serena/memories against HEAD ${HEAD_SHA}. Newest synced commit: ${NEWEST_SHA:-none}. Changed non-knowledge files: ${NON_KNOWLEDGE_FILES:-unknown}. Follow the agent definition strictly: source-of-truth hierarchy = code > tests > git diff > existing memories; never speculate; cite or omit; emit final JSON report.'
  })

The flow-memory-sync subagent has narrow tool access (Serena memory tools + Read/Grep/Glob/Bash; Edit/Write/NotebookEdit are disallowed in its frontmatter). It enforces fact-only updates with anti-hallucination guards, runs ${COMMIT_SCRIPT} at the end, and emits a JSON report. After it exits, this hook re-fires; if memories now match HEAD it lets the session stop. If you cannot invoke the subagent (e.g., not enabled), fall back to: list_memories -> read_memory -> verify against code via Serena symbol tools -> write/edit memory with 'Last commit: ${HEAD_SHA}' line -> ${COMMIT_SCRIPT}."

echo "$MESSAGE" >&2
exit 2
