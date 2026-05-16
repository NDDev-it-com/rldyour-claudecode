#!/usr/bin/env bash
# collect_diagnostics.sh - bundle local diagnostic state for failure triage.
#
# Writes a timestamped tarball under .serena/diagnostics/ (gitignored) that
# captures everything an off-machine reviewer would need to investigate a
# Claude Code marketplace bug without access to the local box: CLI version,
# plugin list, manifest snapshots, MCP server config, hook scripts, current
# branch state, fullrepo sync state, runtime state files, recent CI logs.
#
# The bundle never contains secrets - env vars are filtered, .env files are
# skipped, and OAuth/API tokens never appear because we only read from the
# repo, not from the environment.
#
# Usage:
#   scripts/collect_diagnostics.sh           # write bundle, print path
#   scripts/collect_diagnostics.sh --print   # also print bundle contents to stdout

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

PRINT=0
if [ "${1:-}" = "--print" ]; then
  PRINT=1
fi

OUT_DIR=".serena/diagnostics"
mkdir -p "$OUT_DIR"
TS=$(date -u +"%Y%m%dT%H%M%SZ")
BUNDLE_DIR="$OUT_DIR/diag-$TS"
mkdir -p "$BUNDLE_DIR"

dump() {
  local name="$1"
  shift
  local target="$BUNDLE_DIR/$name"
  if "$@" > "$target" 2>&1; then
    echo "OK $name" >&2
  else
    echo "PARTIAL $name (exit $?)" >&2
  fi
}

dump "claude-version.txt" claude --version
dump "claude-plugin-list.txt" claude plugin list
dump "git-status.txt" git status --short --branch
dump "git-log.txt" git log --oneline -20
dump "git-worktree.txt" git worktree list
dump "git-branches.txt" git branch -avv

dump "fullrepo-status.json" python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json
dump "flow-post-task-state.json" python3 plugins/rldyour-flow/scripts/flow_post_task_state.py
dump "instruction-docs-state.json" python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json
dump "serena-memory-state.json" python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py

cp .claude-plugin/marketplace.json "$BUNDLE_DIR/marketplace.json" 2>/dev/null || true
cp plugins/rldyour-mcps/.mcp.json "$BUNDLE_DIR/mcp.json" 2>/dev/null || true
cp plugins/rldyour-flow/hooks/hooks.json "$BUNDLE_DIR/flow-hooks.json" 2>/dev/null || true
cp plugins/rldyour-serena-mcp/hooks/hooks.json "$BUNDLE_DIR/serena-hooks.json" 2>/dev/null || true
cp config/mcp-runtime-versions.env "$BUNDLE_DIR/mcp-runtime-versions.env" 2>/dev/null || true

# Recent runtime markers (these are in .gitignore but useful for triage).
for marker in .serena/.sync_marker .serena/.flow_sync_marker .serena/.serena_sync_state.json .serena/.flow_post_task_state.json; do
  if [ -f "$marker" ]; then
    cp "$marker" "$BUNDLE_DIR/$(basename "$marker").snapshot" 2>/dev/null || true
  fi
done

# Short summary.
{
  echo "# rldyour-claudecode diagnostics bundle"
  echo "Generated: $(date -u)"
  echo "Marketplace VERSION: $(cat VERSION 2>/dev/null || echo unknown)"
  echo "HEAD: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  echo
  echo "## Bundle contents"
  ls -la "$BUNDLE_DIR"
} > "$BUNDLE_DIR/SUMMARY.md"

ARCHIVE="$OUT_DIR/diag-$TS.tar.gz"
tar -czf "$ARCHIVE" -C "$OUT_DIR" "diag-$TS"
rm -rf "$BUNDLE_DIR"

echo "$ARCHIVE"

if [ "$PRINT" -eq 1 ]; then
  tar -tzf "$ARCHIVE"
fi
