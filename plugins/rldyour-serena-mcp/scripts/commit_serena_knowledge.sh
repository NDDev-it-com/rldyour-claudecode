#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository" >&2
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_SCRIPT="$SCRIPT_DIR/serena_memory_state.py"

KNOWLEDGE_PATTERN='^.. \.serena/(memories|plans|research)(/|$)'
RUNTIME_PATTERN='^.. \.serena/(\.sync_marker|\.serena_sync_state\.json|\.auto_sync_head|\.active_workflow_intent\.json|\.dirty_stop_ack|\.flow_sync_marker|\.flow_post_task_state\.json)$'

STATUS=$(git status --porcelain -uall 2>/dev/null | grep -vE "$RUNTIME_PATTERN" || true)
if [ -z "$STATUS" ]; then
  if [ ! -f "$STATE_SCRIPT" ]; then
    echo "No tracked Serena knowledge changes to commit"
    exit 0
  fi
  STATE_JSON=$(python3 "$STATE_SCRIPT" 2>/dev/null || true)
  if [ -z "$STATE_JSON" ]; then
    echo "No tracked Serena knowledge changes to commit"
    exit 0
  fi
  MEMORY_MATCHES_HEAD=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("memory_matches_head") else "false")' 2>/dev/null || echo "false")
  if [ "$MEMORY_MATCHES_HEAD" = "true" ]; then
    rm -f .serena/.sync_marker .serena/.serena_sync_state.json .serena/.auto_sync_head
    echo "Serena knowledge is current; removed runtime sync markers"
    exit 0
  fi
  MEMORY_COUNT=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("memory_count", 0))' 2>/dev/null || echo "0")
  if [ "$MEMORY_COUNT" != "0" ]; then
    echo "Refusing to acknowledge Serena knowledge because memories do not match HEAD" >&2
    exit 1
  fi
  echo "No tracked Serena knowledge changes to commit"
  exit 0
fi

UNEXPECTED=$(printf "%s\n" "$STATUS" | grep -vE "$KNOWLEDGE_PATTERN" || true)
if [ -n "$UNEXPECTED" ]; then
  echo "Refusing to auto-commit because non-Serena-knowledge changes exist:" >&2
  printf "%s\n" "$UNEXPECTED" >&2
  exit 1
fi

HEAD_SHORT=$(git rev-parse --short=7 HEAD 2>/dev/null || echo "unknown")

KNOWLEDGE_PATHS=()
for path in .serena/memories .serena/plans .serena/research; do
  if [ -e "$path" ]; then
    KNOWLEDGE_PATHS+=("$path")
  fi
done

if [ "${#KNOWLEDGE_PATHS[@]}" -eq 0 ]; then
  echo "No Serena knowledge directories exist"
  exit 0
fi

TRACKED_KNOWLEDGE=$(git ls-files -- .serena/memories .serena/plans .serena/research 2>/dev/null || true)
if [ -z "$TRACKED_KNOWLEDGE" ]; then
  if [ ! -f "$STATE_SCRIPT" ]; then
    echo "Refusing to acknowledge fullrepo-managed Serena knowledge because memory state script is unavailable" >&2
    exit 1
  fi
  STATE_JSON=$(python3 "$STATE_SCRIPT" 2>/dev/null || true)
  if [ -z "$STATE_JSON" ]; then
    echo "Refusing to acknowledge fullrepo-managed Serena knowledge because memory state script is unavailable" >&2
    exit 1
  fi
  MEMORY_MATCHES_HEAD=$(printf "%s" "$STATE_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("memory_matches_head") else "false")' 2>/dev/null || echo "false")
  if [ "$MEMORY_MATCHES_HEAD" != "true" ]; then
    echo "Refusing to acknowledge fullrepo-managed Serena knowledge because memories do not match HEAD" >&2
    exit 1
  fi
  rm -f .serena/.sync_marker .serena/.serena_sync_state.json .serena/.auto_sync_head
  echo "Serena knowledge is fullrepo-managed; removed runtime sync markers without committing to the current branch"
  exit 0
fi

git add -- "${KNOWLEDGE_PATHS[@]}"
if git diff --cached --quiet -- "${KNOWLEDGE_PATHS[@]}"; then
  echo "No staged Serena knowledge changes to commit"
  exit 0
fi

git commit -m "chore(serena): sync project knowledge after ${HEAD_SHORT}"
rm -f .serena/.sync_marker .serena/.serena_sync_state.json .serena/.auto_sync_head
