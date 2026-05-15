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
IFS=$'\n\t'
unset CDPATH

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

step "dart SDK version (>=3.9.0 for dart-flutter MCP)"
if command -v dart >/dev/null 2>&1; then
  DART_VERSION=$(dart --version 2>&1 | sed -nE 's/.*Dart SDK version: ([0-9]+\.[0-9]+\.[0-9]+).*/\1/p')
  if [ -z "$DART_VERSION" ]; then
    echo "INFO dart present but version not parseable (dart-flutter MCP requires >=3.9.0)"
  else
    DART_MAJOR=${DART_VERSION%%.*}
    DART_REST=${DART_VERSION#*.}
    DART_MINOR=${DART_REST%%.*}
    if [ "$DART_MAJOR" -gt 3 ] || { [ "$DART_MAJOR" -eq 3 ] && [ "$DART_MINOR" -ge 9 ]; }; then
      echo "OK dart $DART_VERSION (>=3.9.0)"
    else
      fail "dart $DART_VERSION below 3.9.0 — dart-flutter MCP requires >=3.9.0 (https://docs.flutter.dev/ai/mcp-server)"
    fi
  fi
else
  echo "INFO dart not on PATH — dart-flutter MCP will not start until Dart SDK 3.9+ is installed"
fi

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

step "git pre-push hook (advisory)"
if [ ! -d .git ]; then
  echo "INFO not in a git repository; skipping pre-push hook check"
elif [ -e .git/hooks/pre-push ] && grep -q "rldyour" .git/hooks/pre-push 2>/dev/null; then
  echo "OK rldyour pre-push guard installed at .git/hooks/pre-push"
elif [ -e .git/hooks/pre-push ]; then
  echo "INFO .git/hooks/pre-push exists but is not the rldyour guard."
  echo "     To install/upgrade: bash scripts/install_local_git_hooks.sh --apply"
else
  echo "INFO no .git/hooks/pre-push installed."
  echo "     To enable the rldyour pre-push guard (recommended for product"
  echo "     repositories that consume this marketplace):"
  echo "       bash scripts/install_local_git_hooks.sh --dry-run    # preview"
  echo "       bash scripts/install_local_git_hooks.sh --apply      # install"
fi

printf '\n\033[1;32m✔ bootstrap_check passed\033[0m\n'
