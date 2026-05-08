#!/usr/bin/env bash
# sync_fullrepo_branch.sh — top-level wrapper around the canonical fullrepo CLI.
#
# Forwards every argument to plugins/rldyour-flow/scripts/fullrepo_sync.py.
# Use this wrapper from the marketplace root for shorter, stable invocations:
#
#   scripts/sync_fullrepo_branch.sh --bootstrap-init
#   scripts/sync_fullrepo_branch.sh --status-json
#   scripts/sync_fullrepo_branch.sh --restore
#   scripts/sync_fullrepo_branch.sh --migrate-main
#   scripts/sync_fullrepo_branch.sh --publish

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$ROOT/plugins/rldyour-flow/scripts/fullrepo_sync.py"

if [ ! -f "$TARGET" ]; then
  echo "fullrepo_sync.py not found at $TARGET" >&2
  exit 1
fi

exec python3 "$TARGET" "$@"
