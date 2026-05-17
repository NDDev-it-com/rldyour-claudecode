#!/usr/bin/env bash
# bootstrap_check.sh - verify a fresh-clone or new-machine bootstrap works end-to-end.
#
# Coverage:
#   1. Agent-only worktree divergence guard (TECHDEBT-01 R5 mitigation):
#      refuse `--bootstrap-init` when worktree agent-only files diverge from
#      origin/fullrepo, because the restore would silently overwrite local edits.
#      Override: RLDYOUR_FORCE_BOOTSTRAP=1.
#   2. fullrepo --bootstrap-init produces tracked_agent_paths=[].
#   3. claude plugin validate marketplace + every plugin succeeds.
#   4. .git/info/exclude contains the rldyour fullrepo block.
#   5. Required env vars from .env.example are either set in the environment
#      or documented (default-empty entries).
#   6. dart SDK version >=3.9.0 for dart-flutter MCP.
#   7. Optional pre-push guard advisory.
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

step "agent-only divergence guard (TECHDEBT-01 R5)"
# Before --bootstrap-init: detect whether worktree agent-only files have local
# edits that are not yet in origin/fullrepo. If they do, running
# --bootstrap-init silently overwrites them with the remote tree - exactly the
# footgun documented in TECHDEBT-01 R5. Refuse here unless the operator sets
# RLDYOUR_FORCE_BOOTSTRAP=1 to accept the overwrite explicitly.
#
# Content-based comparison is required because agent-only files are excluded
# from `main` branch index via `.git/info/exclude`. `git diff origin/fullrepo`
# would treat them as "deleted" (they exist only in fullrepo tree, not in main
# index), so we use `git cat-file -e` + `cmp -s` against `git show` content.
if [ "${RLDYOUR_FORCE_BOOTSTRAP:-0}" = "1" ]; then
  echo "WARN RLDYOUR_FORCE_BOOTSTRAP=1 set - divergence guard BYPASSED (operator accepted overwrite risk; see TECHDEBT-01 R5)" >&2
  # File audit trail (closure of security F-7 from review wave 2026-05-16T1859Z-61b913d):
  # every bypass appends to .serena/.bootstrap_overrides.log so post-hoc
  # investigation of "who overwrote memory edits" has a durable record.
  # File is gitignored by .serena/ rule; stays on disk per worktree.
  if [ -d .serena ] || mkdir -p .serena 2>/dev/null; then
    ts=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    head_sha=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
    user_id="${USER:-${LOGNAME:-${HOSTNAME:-unknown}}}"
    printf '%s\tHEAD=%s\tuser=%s\tcwd=%s\n' "$ts" "$head_sha" "$user_id" "$PWD" \
      >> .serena/.bootstrap_overrides.log 2>/dev/null || true
  fi
elif ! git ls-remote --exit-code origin fullrepo >/dev/null 2>&1; then
  echo "INFO origin/fullrepo does not exist yet - no divergence possible (initial-publish flow)"
else
  # Make sure refs/remotes/origin/fullrepo is fresh for accurate comparison.
  # If fetch fails (offline, auth issue), emit explicit WARN - comparison
  # against a stale local ref is a false-positive risk that operators must
  # see in stderr rather than silently swallow.
  if ! git fetch origin fullrepo --quiet 2>/dev/null; then
    echo "WARN git fetch origin fullrepo failed - comparison uses possibly stale local ref" >&2
  fi
  # Agent-only path roots. The canonical full list is AGENT_ONLY_PATTERNS in
  # plugins/rldyour-flow/scripts/fullrepo_sync.py - keep this array in sync
  # with that constant. The `.aider*` glob from fullrepo_sync.py is expanded
  # explicitly below the array because bash literal entries cannot match
  # `.aiderignore`/`.aider.conf.yml`/etc. SKILL.md only covers the minimal
  # AGENTS.md/CLAUDE.md instruction subset for downstream product repos and
  # is NOT a source of truth for the full marketplace agent-only list.
  AGENT_ONLY_PATHS=(
    "AGENTS.md"
    "CLAUDE.md"
    "REVIEW.md"
    "GEMINI.md"
    "QWEN.md"
    ".cursorrules"
    ".windsurfrules"
    ".claude"
    ".cursor/rules"
    ".gemini"
    ".roo"
    ".windsurf"
    ".openhands"
    ".agents/skills"
    ".agents/commands"
    ".agents/hooks"
    ".github/copilot-instructions.md"
    ".github/instructions"
    ".github/prompts"
    ".serena/project.yml"
    ".serena/memories"
    ".serena/plans"
    ".serena/research"
    ".serena/newproj"
    ".serena/deploy"
  )
  # Expand the `.aider*` glob from fullrepo_sync.py AGENT_ONLY_PATTERNS so
  # `.aiderignore`, `.aider.conf.yml`, `.aider.chat.history.md`, etc. are
  # also covered. `shopt -s nullglob` makes the expansion empty (instead of
  # the literal pattern) when no matching file exists in the worktree root.
  shopt -s nullglob
  for aider_path in .aider*; do
    AGENT_ONLY_PATHS+=("$aider_path")
  done
  shopt -u nullglob

  # Helper: compare single worktree file against the same path in origin/fullrepo.
  # Sets the global `diverged` array.
  diverged=()
  check_file() {
    local file=$1
    if ! git cat-file -e "origin/fullrepo:$file" 2>/dev/null; then
      diverged+=("$file (new - not yet in origin/fullrepo)")
      return
    fi
    if ! cmp -s "$file" <(git show "origin/fullrepo:$file" 2>/dev/null); then
      diverged+=("$file (modified locally - not yet published)")
    fi
  }

  for path in "${AGENT_ONLY_PATHS[@]}"; do
    [ -e "$path" ] || continue
    if [ -d "$path" ]; then
      while IFS= read -r -d '' file; do
        check_file "$file"
      done < <(find "$path" -type f -print0 2>/dev/null)
    else
      check_file "$path"
    fi
  done

  if [ ${#diverged[@]} -gt 0 ]; then
    {
      echo "WARN agent-only files differ from origin/fullrepo:"
      for p in "${diverged[@]}"; do
        echo "       - $p"
      done
    } >&2
    fail "Running --bootstrap-init now would silently overwrite these local changes (TECHDEBT-01 R5 footgun).
Resolution:
  (a) Publish local changes first:
      python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish
  (b) Discard local changes intentionally:
      RLDYOUR_FORCE_BOOTSTRAP=1 bash scripts/bootstrap_check.sh"
  fi
  echo "OK agent-only files match origin/fullrepo"
fi

step "fullrepo bootstrap"
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init >/dev/null 2>&1 || fail "--bootstrap-init failed"
TRACKED=$(python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["tracked_agent_paths"]))')
if [ "$TRACKED" != "0" ]; then
  fail "tracked_agent_paths=$TRACKED (expected 0 - agent-only files leaking into branch index)"
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
      fail "dart $DART_VERSION below 3.9.0 - dart-flutter MCP requires >=3.9.0 (https://docs.flutter.dev/ai/mcp-server)"
    fi
  fi
else
  echo "INFO dart not on PATH - dart-flutter MCP will not start until Dart SDK 3.9+ is installed"
fi

step "required MCP credentials (mandatory)"
# CONTEXT7_API_KEY and GITHUB_PERSONAL_ACCESS_TOKEN are referenced by
# plugins/rldyour-mcps/.mcp.json via ${VAR} expansion (no default).
# Claude Code docs are explicit: required env without ${VAR:-default}
# fallback aborts config parse. The audit (2026-05-17 review wave)
# recommends fail-fast over silent degraded MCP. Override flag
# RLDYOUR_SKIP_ENV_CHECK=1 is intentionally not provided - we want
# operators to set the secret rather than bypass the gate.
REQUIRED_ENV=(
  "CONTEXT7_API_KEY"
  "GITHUB_PERSONAL_ACCESS_TOKEN"
)
missing_required=()
for key in "${REQUIRED_ENV[@]}"; do
  if [ -z "${!key:-}" ]; then
    missing_required+=("$key")
  else
    echo "OK $key set in environment"
  fi
done
if [ "${#missing_required[@]}" -gt 0 ]; then
  printf '\033[1;31mFAIL required MCP env var(s) unset:\033[0m\n' >&2
  for key in "${missing_required[@]}"; do
    printf '  %s\n' "$key" >&2
  done
  printf '\n' >&2
  printf 'These secrets are referenced by plugins/rldyour-mcps/.mcp.json without a\n' >&2
  printf 'default; Claude Code aborts config parse when they are unset. Set them in\n' >&2
  printf 'your shell profile or a .env file consumed before launching Claude Code.\n' >&2
  printf 'See docs/runtime-env.md and plugins/rldyour-mcps/.env.example.\n' >&2
  exit 1
fi

step "env example coverage (optional vars)"
if [ -f plugins/rldyour-mcps/.env.example ]; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    [[ "$line" =~ ^# ]] && continue
    key="${line%%=*}"
    # Skip the required keys we already reported in the previous step.
    case " ${REQUIRED_ENV[*]} " in
      *" $key "*) continue ;;
    esac
    if [ -z "${!key:-}" ]; then
      echo "INFO $key not set in environment (default empty in .env.example - set before running MCP server)"
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
