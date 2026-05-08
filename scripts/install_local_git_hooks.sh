#!/usr/bin/env bash
# install_local_git_hooks.sh — install rldyour pre-push guard in a consumer repo.
#
# The guard is the local_git_ai_guard.sh shipped in plugins/rldyour-flow/scripts/.
# It is branch-aware: product branches get strict protection against agent-only
# paths (AGENTS.md, .claude/**, .serena/{memories,plans,research,...}, AI tool
# config) and AI-marker additions. The configured fullrepo branch
# (`fullrepo` by default, or `RLDYOUR_FULLREPO_BRANCH`) allows durable AI
# context but still blocks definite secrets, runtime markers, browser
# artifacts, and local env files.
#
# Usage:
#   scripts/install_local_git_hooks.sh                              # current repo, dry-run
#   scripts/install_local_git_hooks.sh --apply                       # current repo, install
#   scripts/install_local_git_hooks.sh --repo /path/to/project --apply
#   scripts/install_local_git_hooks.sh --uninstall --repo /path
#
# Idempotent: re-running --apply overwrites the existing pre-push hook with
# the latest version of local_git_ai_guard.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GUARD_SOURCE="$ROOT/plugins/rldyour-flow/scripts/local_git_ai_guard.sh"

REPO=""
APPLY=0
UNINSTALL=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)
      REPO="$2"; shift 2 ;;
    --apply)
      APPLY=1; shift ;;
    --dry-run)
      APPLY=0; shift ;;
    --uninstall)
      UNINSTALL=1; shift ;;
    -h|--help)
      sed -n '2,17p' "$0"; exit 0 ;;
    *)
      echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$REPO" ]; then
  REPO="$(pwd)"
fi

REPO="$(cd "$REPO" && pwd)"

if ! git -C "$REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "FAIL $REPO is not a git working tree" >&2
  exit 1
fi

GIT_DIR="$(git -C "$REPO" rev-parse --git-dir)"
HOOK_PATH="$GIT_DIR/hooks/pre-push"

if [ "$UNINSTALL" -eq 1 ]; then
  if [ -f "$HOOK_PATH" ] && grep -q "rldyour local_git_ai_guard" "$HOOK_PATH"; then
    rm -f "$HOOK_PATH"
    echo "REMOVED $HOOK_PATH"
  else
    echo "SKIP $HOOK_PATH does not look like an rldyour-installed guard"
  fi
  exit 0
fi

if [ ! -f "$GUARD_SOURCE" ]; then
  echo "FAIL guard source missing: $GUARD_SOURCE" >&2
  exit 1
fi

if [ "$APPLY" -eq 0 ]; then
  echo "DRY-RUN — would install:"
  echo "  source: $GUARD_SOURCE"
  echo "  target: $HOOK_PATH"
  exit 0
fi

mkdir -p "$(dirname "$HOOK_PATH")"
{
  echo "#!/usr/bin/env bash"
  echo "# rldyour local_git_ai_guard pre-push hook"
  echo "# Installed by $(basename "$0") on $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "exec bash $GUARD_SOURCE \"\$@\""
} > "$HOOK_PATH"
chmod +x "$HOOK_PATH"

echo "INSTALLED $HOOK_PATH (delegates to $GUARD_SOURCE)"
echo "Note: the guard reads stdin per-ref, so it is invoked automatically by 'git push'."
echo "      Set RLDYOUR_FULLREPO_BRANCH to override the default fullrepo branch name."
