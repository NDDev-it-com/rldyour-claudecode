#!/usr/bin/env bash
set -euo pipefail

APPLY=0
TARGET_REPO=.

usage() {
  cat <<'EOF'
Usage: scripts/install_local_git_hooks.sh [--repo PATH] [--dry-run] [--apply]

Installs rldyour local Git hooks for the current repository. The pre-push hook
delegates to plugins/rldyour-flow/scripts/local_git_ai_guard.sh.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      APPLY=0
      ;;
    --apply)
      APPLY=1
      ;;
    --repo)
      shift
      TARGET_REPO=${1:?--repo requires a path}
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SOURCE_ROOT=$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel)
SOURCE_GUARD="$SOURCE_ROOT/plugins/rldyour-flow/scripts/local_git_ai_guard.sh"
ROOT=$(git -C "$TARGET_REPO" rev-parse --show-toplevel)
GIT_DIR=$(git -C "$ROOT" rev-parse --git-dir)
if [[ $GIT_DIR != /* ]]; then
  GIT_DIR="$ROOT/$GIT_DIR"
fi
HOOK_DIR="$GIT_DIR/hooks"
PRE_PUSH="$HOOK_DIR/pre-push"
LOCAL_GUARD="$HOOK_DIR/_local_guard_ai.sh"
PREVIOUS_PRE_PUSH="$HOOK_DIR/pre-push.rldyour-previous"
STAMP=$(date +%Y%m%d%H%M%S)

managed_pre_push() {
  [ -f "$PRE_PUSH" ] && grep -F "rldyour local git hook manager" "$PRE_PUSH" >/dev/null 2>&1
}

write_file() {
  local path=$1
  local mode=$2
  local tmp
  tmp=$(mktemp)
  cat >"$tmp"
  if [ "$APPLY" -eq 0 ]; then
    printf 'dry-run: would write %s\n' "$path"
    rm -f "$tmp"
    return
  fi
  install -m "$mode" "$tmp" "$path"
  rm -f "$tmp"
}

mkdir -p "$HOOK_DIR"

if [ -f "$PRE_PUSH" ] && ! managed_pre_push; then
  if [ "$APPLY" -eq 0 ]; then
    printf 'dry-run: would preserve existing %s as %s\n' "$PRE_PUSH" "$PREVIOUS_PRE_PUSH"
    if [ -f "$PREVIOUS_PRE_PUSH" ]; then
      printf 'dry-run: would back up existing %s to %s.bak.%s\n' "$PREVIOUS_PRE_PUSH" "$PREVIOUS_PRE_PUSH" "$STAMP"
    fi
  else
    if [ -f "$PREVIOUS_PRE_PUSH" ]; then
      mv "$PREVIOUS_PRE_PUSH" "$PREVIOUS_PRE_PUSH.bak.$STAMP"
      printf 'backed up existing previous pre-push to %s.bak.%s\n' "$PREVIOUS_PRE_PUSH" "$STAMP"
    fi
    mv "$PRE_PUSH" "$PREVIOUS_PRE_PUSH"
    chmod +x "$PREVIOUS_PRE_PUSH"
    printf 'preserved existing pre-push as %s\n' "$PREVIOUS_PRE_PUSH"
  fi
fi

write_file "$LOCAL_GUARD" 0755 <<EOF_GUARD
#!/usr/bin/env bash
set -euo pipefail

ROOT=\$(git rev-parse --show-toplevel)
for guard in \\
  "\$ROOT/plugins/rldyour-flow/scripts/local_git_ai_guard.sh" \\
  "$SOURCE_GUARD" \\
  "\${CODEX_HOME:-\$HOME/.codex}/plugins/cache/rldyour-codex/rldyour-flow"/*/scripts/local_git_ai_guard.sh \\
  "\${CODEX_HOME:-\$HOME/.codex}/plugins/cache/rldyour-codex/rldyour-flow/local/scripts/local_git_ai_guard.sh"; do
  if [ -f "\$guard" ]; then
    exec bash "\$guard" "\$@"
  fi
done

printf 'rldyour local Git AI guard script not found\\n' >&2
exit 1
EOF_GUARD

write_file "$PRE_PUSH" 0755 <<'EOF_PRE_PUSH'
#!/usr/bin/env bash
# rldyour local git hook manager
set -euo pipefail

HOOK_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
INPUT=$(mktemp)
cleanup() {
  rm -f "$INPUT"
}
trap cleanup EXIT

cat >"$INPUT"

bash "$HOOK_DIR/_local_guard_ai.sh" "$@" <"$INPUT"

if [ -x "$HOOK_DIR/pre-push.rldyour-previous" ]; then
  "$HOOK_DIR/pre-push.rldyour-previous" "$@" <"$INPUT"
fi
EOF_PRE_PUSH

if [ "$APPLY" -eq 0 ]; then
  printf 'dry-run complete. Re-run with --apply to install local Git hooks.\n'
else
  printf 'installed rldyour local Git pre-push guard in %s\n' "$HOOK_DIR"
fi
