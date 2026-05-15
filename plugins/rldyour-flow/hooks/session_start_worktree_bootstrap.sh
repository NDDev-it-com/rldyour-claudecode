#!/usr/bin/env bash
# session_start_worktree_bootstrap.sh — restore agent-only files into a fresh
# git worktree on first SessionStart.
#
# Triggers a `fullrepo_sync.py --restore` (NEVER --publish) when:
#   1. Current cwd is inside a git work-tree.
#   2. At least one canonical agent-only file is missing in the worktree
#      (.serena/project.yml is the marker we trust most — small, unique, and
#      always present in a synchronised marketplace tree).
#   3. `origin/fullrepo` exists on the remote (otherwise --restore is a no-op
#      and we exit cleanly without noise).
#
# The hook NEVER publishes, NEVER mutates origin, and NEVER touches non-agent
# files. Behaviour is bounded to: install the .git/info/exclude block for the
# active worktree + checkout agent-only paths from `origin/fullrepo`.
#
# Skip flag: RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1 → exit 0 immediately.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

if [ "${RLDYOUR_SKIP_WORKTREE_BOOTSTRAP:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FULLREPO_SCRIPT="$PLUGIN_DIR/scripts/fullrepo_sync.py"

if [ ! -f "$FULLREPO_SCRIPT" ]; then
  exit 0
fi

# Bootstrap only if a canonical agent-only file is missing. We probe three
# markers: .serena/project.yml (most distinctive), AGENTS.md, .claude/CLAUDE.md.
# Any one missing means the worktree is fresh (or someone deleted state).
need_bootstrap=0
for marker in ".serena/project.yml" "AGENTS.md" ".claude/CLAUDE.md"; do
  if [ ! -e "$ROOT/$marker" ]; then
    need_bootstrap=1
    break
  fi
done

if [ "$need_bootstrap" = "0" ]; then
  exit 0
fi

# Verify origin/fullrepo actually exists before attempting --restore so we
# don't emit confusing "no fullrepo" errors in a brand-new repo.
STATUS_JSON=$(python3 "$FULLREPO_SCRIPT" --status-json 2>/dev/null || true)
if [ -z "$STATUS_JSON" ]; then
  exit 0
fi

remote_present=$(printf "%s" "$STATUS_JSON" | python3 -c '
import json, sys
try:
    s = json.load(sys.stdin)
except Exception:
    print("false")
    raise SystemExit(0)
print("true" if s.get("remote_fullrepo_exists") else "false")
' 2>/dev/null || echo "false")

if [ "$remote_present" != "true" ]; then
  # No fullrepo upstream — nothing to restore. Silent no-op.
  exit 0
fi

# Run --restore, capture stdout for the advisory context.
RESTORE_OUT=$(python3 "$FULLREPO_SCRIPT" --restore 2>&1 || true)

# Compose advisory context. We emit JSON so the new session sees a clean
# "this worktree was auto-bootstrapped" notice in additionalContext.
python3 - "$ROOT" "$RESTORE_OUT" <<'PY'
import json
import sys

root, restore_out = sys.argv[1:3]

# Trim restore_out to first 12 lines to keep advisory bounded.
lines = [line for line in restore_out.splitlines() if line.strip()]
preview = lines[:12]
trailing = max(len(lines) - len(preview), 0)

advisory_lines = [
    "rldyour-flow worktree bootstrap (auto-restored from origin/fullrepo):",
    f"- Worktree root: {root}.",
    "- A canonical agent-only marker (.serena/project.yml / AGENTS.md / .claude/CLAUDE.md) was missing,",
    "  so plugins/rldyour-flow/scripts/fullrepo_sync.py --restore ran to install the .git/info/exclude",
    "  block for this worktree and check out agent-only paths from origin/fullrepo. This restore is",
    "  purely additive: no commits, no pushes, no fullrepo --publish.",
    "- If the restore output below contains a path you do NOT want auto-restored, set",
    "  RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1 in this shell and reopen Claude Code.",
    "- Output:",
]
for line in preview:
    advisory_lines.append(f"  {line}")
if trailing:
    advisory_lines.append(f"  ... plus {trailing} more lines")

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n".join(advisory_lines),
    }
}))
PY
