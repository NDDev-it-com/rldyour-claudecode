#!/usr/bin/env bash
# bootstrap_check.sh — verify a fresh-clone or new-machine bootstrap works end-to-end.
#
# Coverage:
#   1. fullrepo --bootstrap-init produces tracked_agent_paths=[].
#   2. claude plugin validate marketplace + every plugin succeeds.
#   3. .git/info/exclude contains the rldyour fullrepo block.
#   4. Required env vars from .env.example are either set in the environment
#      or documented (default-empty entries).
#
# This is the canonical "did the marketplace install correctly?" check after
# a fresh clone or after pulling a major change.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1;36m== %s ==\033[0m\n' "$1"; }
fail() { printf '\033[1;31m%s\033[0m\n' "$1" >&2; exit 1; }

step "fullrepo bootstrap"
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init >/dev/null 2>&1 || fail "--bootstrap-init failed"
TRACKED=$(python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["tracked_agent_paths"]))')
if [ "$TRACKED" != "0" ]; then
  fail "tracked_agent_paths=$TRACKED (expected 0 — agent-only files leaking into branch index)"
fi
echo "OK bootstrap clean (tracked_agent_paths=0)"

step ".git/info/exclude block installed"
EXCLUDE_FILE=".git/info/exclude"
if [ -f "$EXCLUDE_FILE" ] && grep -q "rldyour fullrepo agent-only files" "$EXCLUDE_FILE"; then
  echo "OK exclude block present"
else
  fail "missing rldyour fullrepo block in $EXCLUDE_FILE"
fi

step "claude plugin validate"
claude plugin validate . >/dev/null 2>&1 || fail "marketplace validate failed"
echo "OK marketplace"
for p in plugins/*/; do
  if claude plugin validate "$p" >/dev/null 2>&1; then
    echo "OK $(basename "$p")"
  else
    fail "$(basename "$p") validate failed"
  fi
done

step "env example coverage"
if [ -f plugins/rldyour-mcps/.env.example ]; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    [[ "$line" =~ ^# ]] && continue
    key="${line%%=*}"
    if [ -z "${!key:-}" ]; then
      echo "INFO $key not set in environment (default empty in .env.example — set before running MCP server)"
    else
      echo "OK $key set in environment"
    fi
  done < plugins/rldyour-mcps/.env.example
else
  fail "missing plugins/rldyour-mcps/.env.example"
fi

printf '\n\033[1;32m✔ bootstrap_check passed\033[0m\n'
