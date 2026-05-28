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

STATE_JSON="$STATE_JSON" HOOK_INPUT="$HOOK_INPUT" SYNC_MARKER="$SYNC_MARKER" COMMIT_SCRIPT="$COMMIT_SCRIPT" "${PYTHON_BIN}" <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    hook_payload = json.loads(os.environ.get("HOOK_INPUT", "") or "{}")
except Exception:
    hook_payload = {}

try:
    payload = json.loads(os.environ.get("STATE_JSON", "") or "{}")
except Exception:
    raise SystemExit(0)

is_current = bool(payload.get("is_current"))
head_sha = str(payload.get("head_sha") or "")
newest_sha = str(payload.get("newest_synced_sha") or "")
analysis_source = str(payload.get("analysis_source") or "none")
sync_marker = Path(os.environ.get("SYNC_MARKER", ".serena/.sync_marker"))

if is_current:
    sync_marker.unlink(missing_ok=True)
    Path(".serena/.serena_sync_state.json").unlink(missing_ok=True)
    raise SystemExit(0)

if not head_sha:
    raise SystemExit(0)

marker_fingerprint = f"{head_sha}:{newest_sha or 'none'}"
if hook_payload.get("stop_hook_active") is True and sync_marker.is_file():
    try:
        marker = sync_marker.read_text(encoding="utf-8").strip()
    except OSError:
        marker = ""
    if marker == marker_fingerprint:
        raise SystemExit(0)

sync_marker.parent.mkdir(parents=True, exist_ok=True)
sync_marker.write_text(marker_fingerprint + "\n", encoding="utf-8")

commits = "(no prior synced memory commit metadata)"
if newest_sha:
    proc = subprocess.run(
        ["git", "log", "--oneline", f"{newest_sha}..HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    commits = proc.stdout.strip() if proc.returncode == 0 else "(unable to compute commit range)"
    if not commits:
        commits = "(no commits in range)"

files = payload.get("non_knowledge_changed_files_since_sync")
if not files:
    files = payload.get("sync_state", {}).get("non_knowledge_changed_files")
if not files:
    files = payload.get("sync_state", {}).get("changed_files", []) or payload.get("changed_files_since_sync", [])
non_knowledge_files = "\n".join(str(item) for item in files) if files else "unknown"

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
sync_context = "\n".join(lines)

commit_script = os.environ.get("COMMIT_SCRIPT", "commit_serena_knowledge.sh")
message = f"""[RLDYOUR-SERENA SYNC REQUIRED] Project knowledge is stale for HEAD {head_sha}.

Last synced memory commit: {newest_sha or 'none'}

Relevant commits:
{commits}

{sync_context}

Changed non-Serena-knowledge files:
{non_knowledge_files}

Continue this turn and run the serena-memory-sync workflow now.

Preferred path - invoke the flow-memory-sync subagent:

  Agent({{
    description: 'Sync Serena memories against HEAD {head_sha}',
    subagent_type: 'rldyour-serena-mcp:flow-memory-sync',
    prompt: 'Synchronize numbered .serena/memories against HEAD {head_sha}. Newest synced commit: {newest_sha or 'none'}. Changed non-knowledge files: {non_knowledge_files}. Use CORE-01-INDEX.md as the memory map when present and keep names in AREA-01-SLUG.md form. Follow the agent definition strictly: source-of-truth hierarchy = code > tests > git diff > existing memories; never speculate; cite or omit; emit final JSON report.'
  }})

The flow-memory-sync subagent has narrow tool access (Serena memory tools + Read/Grep/Glob/Bash; Edit/Write/NotebookEdit are disallowed in its frontmatter). It enforces fact-only updates with anti-hallucination guards and runs {commit_script} at the end.

Fallback path (if the subagent is not available - e.g. plugin not yet reloaded):
1. Use Serena MCP for code inspection: check_onboarding_performed -> list_memories -> read_memory(relevant) -> get_symbols_overview -> find_symbol(include_body=false) -> find_symbol(include_body=true only where needed) -> find_referencing_symbols -> search_for_pattern.
2. Update .serena/memories with high-signal fact-only English content. Use numbered topic files (AREA-01-SLUG.md) and update CORE-01-INDEX.md when adding, renaming, or splitting memories. Code, git diff, and tests are the source of truth.
3. Each touched memory must contain a 'Last commit: {head_sha}' line so the state script recognises sync via direct-head-reference.
4. Run {commit_script} to acknowledge sync state and clear runtime markers.
5. Stop again after the sync or report the exact blocker."""

print(message, file=sys.stderr)
raise SystemExit(2)
PY
