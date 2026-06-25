#!/usr/bin/env bash
set -euo pipefail

# bootstrap_check.sh - verify a fresh-clone or new-machine bootstrap works.
# Durable AI context is tracked on main; this script never restores from or
# publishes to a secondary branch.

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

step() { printf '\n== %s ==\n' "$1"; }
fail() { printf 'FAIL %s\n' "$1" >&2; exit 1; }

step "Required tools"
command -v python3 >/dev/null || fail "python3 missing"
command -v git >/dev/null || fail "git missing"
command -v node >/dev/null || true

step "Required context files"
for path in AGENTS.md .claude/CLAUDE.md .serena/project.yml .serena/memories; do
  [ -e "$path" ] || fail "missing tracked context path: $path"
done

step "Runtime-local Serena state stays ignored"
for path in .serena/cache/example .serena/diagnostics/example .serena/reviews/example .serena/.flow_post_task_state.json .serena/.serena_sync_state.json; do
  if ! git check-ignore -q "$path"; then
    fail "runtime-local path is not ignored: $path"
  fi
done

step "Tracked context is not ignored"
for path in AGENTS.md .claude/CLAUDE.md .serena/project.yml .serena/memories/CORE-01-INDEX.md; do
  if git check-ignore -q "$path"; then
    fail "durable context path is ignored: $path"
  fi
done

printf '\nOK bootstrap_check passed\n'
