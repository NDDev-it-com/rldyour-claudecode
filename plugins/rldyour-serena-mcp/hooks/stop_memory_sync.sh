#!/usr/bin/env bash
# stop_memory_sync.sh - advisory enforcement gate for Stop event.
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

STATE_JSON=$("${PYTHON_BIN}" "$STATE_SCRIPT" 2>/dev/null || true)
if [ -z "$STATE_JSON" ]; then
  exit 0
fi

IS_CURRENT=$(printf "%s" "$STATE_JSON" | "${PYTHON_BIN}" -c 'import json,sys; print("true" if json.load(sys.stdin).get("is_current") else "false")' 2>/dev/null || echo "false")
HEAD_SHA=$(printf "%s" "$STATE_JSON" | "${PYTHON_BIN}" -c 'import json,sys; print(json.load(sys.stdin).get("head_sha", ""))' 2>/dev/null || true)
NEWEST_SHA=$(printf "%s" "$STATE_JSON" | "${PYTHON_BIN}" -c 'import json,sys; print(json.load(sys.stdin).get("newest_synced_sha", ""))' 2>/dev/null || true)
ANALYSIS_SOURCE=$(printf "%s" "$STATE_JSON" | "${PYTHON_BIN}" -c 'import json,sys; print(json.load(sys.stdin).get("analysis_source", "none"))' 2>/dev/null || echo "none")

if [ "$IS_CURRENT" = "true" ]; then
  rm -f "$SYNC_MARKER" .serena/.serena_sync_state.json
  exit 0
fi

if [ -z "$HEAD_SHA" ]; then
  exit 0
fi

STOP_HOOK_ACTIVE=$(printf "%s" "$HOOK_INPUT" | "${PYTHON_BIN}" -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}

print("true" if payload.get("stop_hook_active") is True else "false")
' 2>/dev/null || echo "false")

MARKER_FINGERPRINT="${HEAD_SHA}:${NEWEST_SHA:-none}"

if [ "$STOP_HOOK_ACTIVE" = "true" ] && [ -f "$SYNC_MARKER" ] && [ "$(cat "$SYNC_MARKER" 2>/dev/null || true)" = "$MARKER_FINGERPRINT" ]; then
  exit 0
fi

mkdir -p .serena
printf "%s\n" "$MARKER_FINGERPRINT" > "$SYNC_MARKER"

COMMITS="(no prior synced memory commit metadata)"
if [ -n "$NEWEST_SHA" ]; then
  COMMITS=$(git log --oneline "${NEWEST_SHA}..HEAD" 2>/dev/null || echo "(unable to compute commit range)")
fi

NON_KNOWLEDGE_FILES=$(printf "%s" "$STATE_JSON" | "${PYTHON_BIN}" -c '
import json
import sys

payload = json.load(sys.stdin)
files = payload.get("non_knowledge_changed_files_since_sync")
if not files:
    files = payload.get("sync_state", {}).get("non_knowledge_changed_files")
if not files:
    files = payload.get("sync_state", {}).get("changed_files", []) or payload.get("changed_files_since_sync", [])
print("\n".join(str(item) for item in files))
' 2>/dev/null || true)

SYNC_CONTEXT=$(printf "%s" "$STATE_JSON" | "${PYTHON_BIN}" -c '
import json
import sys

head_sha = sys.argv[1]
newest_sha = sys.argv[2]
analysis_source = sys.argv[3] if len(sys.argv) > 3 else "none"
try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}
sync_state = payload.get("sync_state", {}) or {}
analysis = payload.get("analysis") or {}
analysis_by_payload = sync_state.get("analysis") or {}
if not analysis and isinstance(analysis_by_payload, dict):
    analysis = analysis_by_payload
areas_summary = analysis.get("areas_summary", {}) or {}
risk_profile = analysis.get("risk_profile", {}) or {}
memory_targets = analysis.get("memory_targets", []) or []
memory_taxonomy = analysis.get("memory_taxonomy", {}) or {}
reason = (sync_state.get("reason") or "").strip() or "non-knowledge project changes detected"
high_impact = areas_summary.get("high_impact", [])
candidates = sorted({item.get("path") for item in memory_targets if isinstance(item, dict) and item.get("path")})
focus = risk_profile.get("sync_focus", "medium")
analysis_file_count = analysis.get("file_count", 0)
areas = analysis.get("areas") or []
has_analysis = bool(analysis_file_count or areas)
filename_pattern = memory_taxonomy.get("filename_pattern") or "AREA-01-SLUG.md"
index_memory = memory_taxonomy.get("index_memory") or "CORE-01-INDEX.md"

lines = [
    "Change impact (sync analysis):",
    f"- Risk profile: {focus}",
    f"- Analysis source: {analysis_source}",
    f"- Changed files total: {analysis_file_count if isinstance(analysis_file_count, int) else 0}",
    f"- Analysis reason: {reason}",
    f"- Analysis available: {has_analysis}",
    f"- Memory taxonomy: {filename_pattern}; index={index_memory}",
]
if candidates:
    lines.append("- Memory targets: " + ", ".join(candidates))
if high_impact:
    lines.append("- High-priority areas: " + ", ".join(sorted(high_impact)))
print("\n".join(lines))
' "$HEAD_SHA" "$NEWEST_SHA" "$ANALYSIS_SOURCE")

MESSAGE="[RLDYOUR-SERENA SYNC REQUIRED] Project knowledge is stale for HEAD ${HEAD_SHA}.

Last synced memory commit: ${NEWEST_SHA:-none}

Relevant commits:
${COMMITS}

${SYNC_CONTEXT}

Changed non-Serena-knowledge files:
${NON_KNOWLEDGE_FILES:-unknown}

Continue this turn and run the serena-memory-sync workflow now.

Preferred path - invoke the flow-memory-sync subagent:

  Agent({
    description: 'Sync Serena memories against HEAD ${HEAD_SHA}',
    subagent_type: 'rldyour-serena-mcp:flow-memory-sync',
    prompt: 'Synchronize numbered .serena/memories against HEAD ${HEAD_SHA}. Newest synced commit: ${NEWEST_SHA:-none}. Changed non-knowledge files: ${NON_KNOWLEDGE_FILES:-unknown}. Use CORE-01-INDEX.md as the memory map when present and keep names in AREA-01-SLUG.md form. Follow the agent definition strictly: source-of-truth hierarchy = code > tests > git diff > existing memories; never speculate; cite or omit; emit final JSON report.'
  })

The flow-memory-sync subagent has narrow tool access (Serena memory tools + Read/Grep/Glob/Bash; Edit/Write/NotebookEdit are disallowed in its frontmatter). It enforces fact-only updates with anti-hallucination guards and runs ${COMMIT_SCRIPT} at the end.

Fallback path (if the subagent is not available - e.g. plugin not yet reloaded):
1. Use Serena MCP for code inspection: check_onboarding_performed -> list_memories -> read_memory(relevant) -> get_symbols_overview -> find_symbol(include_body=false) -> find_symbol(include_body=true only where needed) -> find_referencing_symbols -> search_for_pattern.
2. Update .serena/memories with high-signal fact-only English content. Use numbered topic files (AREA-01-SLUG.md) and update CORE-01-INDEX.md when adding, renaming, or splitting memories. Code, git diff, and tests are the source of truth.
3. Each touched memory must contain a 'Last commit: ${HEAD_SHA}' line so the state script recognises sync via direct-head-reference.
4. Run ${COMMIT_SCRIPT} to acknowledge sync state and clear runtime markers.
5. Stop again after the sync or report the exact blocker."

echo "$MESSAGE" >&2
exit 2
