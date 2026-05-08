#!/usr/bin/env bash
# stop_post_task_sync.sh — full git pipeline automation after task completion.
#
# Sequence (deterministic, no LLM):
#   1. Wait for Serena memory sync to finish (serena_current=true).
#   2. If feature branch with ahead>0 commits: push -u origin <branch> ; checkout main ;
#      pull --ff-only ; merge --ff-only <branch> ; push origin main.
#   3. If on main branch with ahead>0: push origin main.
#   4. Delete merged feature branch (local + remote).
#   5. Run fullrepo_sync.py --publish (pushes agent-only files to fullrepo with --force-with-lease).
#   6. Delete merged worktrees and merged remote/local feature branches detected by flow_post_task_state.
#   7. Clear runtime markers, exit 0 (allow stop).
#
# Refuses to run if:
#   - dirty non-agent files exist (model is expected to commit before Stop)
#   - merge cannot be fast-forward (would require manual rebase / conflict resolution)
#   - Serena memory sync hasn't completed yet (serena_current=false)

set -euo pipefail

if [ "${RLDYOUR_SKIP_STOP_GATES:-0}" = "1" ] || [ "${RLDYOUR_SKIP_FLOW_SYNC:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_SCRIPT="$PLUGIN_DIR/scripts/flow_post_task_state.py"
FULLREPO_SCRIPT="$PLUGIN_DIR/scripts/fullrepo_sync.py"
SYNC_MARKER=".serena/.flow_sync_marker"
HOOK_INPUT=$(cat 2>/dev/null || true)

if [ ! -f "$STATE_SCRIPT" ] || [ ! -f "$FULLREPO_SCRIPT" ]; then
  exit 0
fi

STATE_JSON=$(python3 "$STATE_SCRIPT" 2>/dev/null || true)
if [ -z "$STATE_JSON" ]; then
  exit 0
fi

# Helpers to read state JSON.
state_get() {
  printf "%s" "$STATE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('$1', ''))"
}

state_get_int() {
  printf "%s" "$STATE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('$1', 0))"
}

state_get_bool() {
  printf "%s" "$STATE_JSON" | python3 -c "import json,sys; print('true' if json.load(sys.stdin).get('$1') else 'false')"
}

SERENA_CURRENT=$(state_get_bool "serena_current")
NEEDS_SYNC=$(state_get_bool "needs_flow_sync")
FINGERPRINT=$(state_get "fingerprint")
HEAD_SHA=$(state_get "head_sha")
BRANCH=$(state_get "branch")
AHEAD=$(state_get_int "ahead")
DIRTY_COUNT=$(state_get_int "dirty_count")

# Step 1: Defer if Serena memory sync hasn't completed.
if [ "$SERENA_CURRENT" != "true" ]; then
  exit 0
fi

# Nothing to do — clear markers and allow stop.
if [ "$NEEDS_SYNC" != "true" ] || [ -z "$FINGERPRINT" ]; then
  rm -f "$SYNC_MARKER" .serena/.flow_post_task_state.json
  exit 0
fi

# Loop guard: if same fingerprint already tried during this Stop chain, allow stop.
STOP_HOOK_ACTIVE=$(printf "%s" "$HOOK_INPUT" | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}
print("true" if payload.get("stop_hook_active") is True else "false")
' 2>/dev/null || echo "false")

if [ "$STOP_HOOK_ACTIVE" = "true" ] && [ -f "$SYNC_MARKER" ] && [ "$(cat "$SYNC_MARKER" 2>/dev/null || true)" = "$FINGERPRINT" ]; then
  exit 0
fi

mkdir -p .serena
printf "%s\n" "$FINGERPRINT" > "$SYNC_MARKER"
printf "%s" "$STATE_JSON" > .serena/.flow_post_task_state.json

# Step 2: refuse if there are dirty non-agent files. The model is expected to
# commit before signalling Stop; we don't auto-create commits with synthetic
# messages.
if [ "$DIRTY_COUNT" -gt 0 ]; then
  DIRTY_LIST=$(printf "%s" "$STATE_JSON" | python3 -c '
import json, sys
print("\n".join(json.load(sys.stdin).get("dirty_files", [])))
')
  echo "[RLDYOUR-FLOW AUTO] uncommitted non-agent paths exist; finalize aborted:" >&2
  printf "%s\n" "$DIRTY_LIST" >&2
  exit 2
fi

PROTECTED_BRANCHES_RE='^(main|master|develop|development|staging|production|prod|fullrepo)$'
DEFAULT_BRANCH=""
for candidate in main master; do
  if git show-ref --verify --quiet "refs/heads/$candidate"; then
    DEFAULT_BRANCH="$candidate"
    break
  fi
done

if [ -z "$DEFAULT_BRANCH" ]; then
  echo "[RLDYOUR-FLOW AUTO] no main/master branch found; finalize aborted" >&2
  exit 2
fi

ORIGIN_DEFAULT="origin/$DEFAULT_BRANCH"

echo "[RLDYOUR-FLOW AUTO] start: branch=$BRANCH ahead=$AHEAD head=$HEAD_SHA default=$DEFAULT_BRANCH" >&2

git fetch origin --prune >/dev/null 2>&1 || true

ON_DEFAULT=0
if [ "$BRANCH" = "$DEFAULT_BRANCH" ]; then
  ON_DEFAULT=1
fi

# Step 3: branch handling.
if [ "$ON_DEFAULT" -eq 1 ]; then
  # Already on main: just push if ahead.
  if [ "$AHEAD" -gt 0 ]; then
    echo "[RLDYOUR-FLOW AUTO] pushing $DEFAULT_BRANCH (ahead=$AHEAD)" >&2
    git push origin "$DEFAULT_BRANCH"
  fi
else
  # Feature branch — must be safe to ff-merge into default.
  if echo "$BRANCH" | grep -Eq "$PROTECTED_BRANCHES_RE"; then
    echo "[RLDYOUR-FLOW AUTO] on protected branch $BRANCH (not $DEFAULT_BRANCH); finalize aborted" >&2
    exit 2
  fi

  # Push feature branch to remote (creates upstream if missing).
  if [ "$AHEAD" -gt 0 ]; then
    echo "[RLDYOUR-FLOW AUTO] pushing feature branch $BRANCH to origin" >&2
    git push -u origin "$BRANCH"
  fi

  # Verify ff-merge possible: default-branch tip must be ancestor of feature branch.
  DEFAULT_TIP=$(git rev-parse "$DEFAULT_BRANCH" 2>/dev/null || true)
  FEATURE_TIP=$(git rev-parse "$BRANCH" 2>/dev/null || true)

  if [ -z "$DEFAULT_TIP" ] || [ -z "$FEATURE_TIP" ]; then
    echo "[RLDYOUR-FLOW AUTO] cannot resolve branch tips; finalize aborted" >&2
    exit 2
  fi

  if ! git merge-base --is-ancestor "$DEFAULT_TIP" "$FEATURE_TIP"; then
    echo "[RLDYOUR-FLOW AUTO] $DEFAULT_BRANCH has commits not in $BRANCH; non-ff merge required; finalize aborted" >&2
    exit 2
  fi

  # Sync local default with origin if remote moved.
  ORIGIN_DEFAULT_TIP=$(git rev-parse "$ORIGIN_DEFAULT" 2>/dev/null || true)
  if [ -n "$ORIGIN_DEFAULT_TIP" ] && [ "$ORIGIN_DEFAULT_TIP" != "$DEFAULT_TIP" ]; then
    if git merge-base --is-ancestor "$DEFAULT_TIP" "$ORIGIN_DEFAULT_TIP"; then
      echo "[RLDYOUR-FLOW AUTO] $DEFAULT_BRANCH local behind origin; updating" >&2
      git checkout "$DEFAULT_BRANCH"
      git merge --ff-only "$ORIGIN_DEFAULT" || {
        echo "[RLDYOUR-FLOW AUTO] cannot ff-update local $DEFAULT_BRANCH from origin; finalize aborted" >&2
        git checkout "$BRANCH" || true
        exit 2
      }
      git checkout "$BRANCH"
      # Re-check ff possibility after default update.
      DEFAULT_TIP=$(git rev-parse "$DEFAULT_BRANCH")
      if ! git merge-base --is-ancestor "$DEFAULT_TIP" "$FEATURE_TIP"; then
        echo "[RLDYOUR-FLOW AUTO] $BRANCH no longer ff-ancestor of $DEFAULT_BRANCH after origin sync; rebase required" >&2
        exit 2
      fi
    fi
  fi

  # Merge feature -> default (ff-only).
  echo "[RLDYOUR-FLOW AUTO] ff-merging $BRANCH into $DEFAULT_BRANCH" >&2
  git checkout "$DEFAULT_BRANCH"
  if ! git merge --ff-only "$BRANCH"; then
    echo "[RLDYOUR-FLOW AUTO] ff-merge failed unexpectedly; restoring branch" >&2
    git checkout "$BRANCH" || true
    exit 2
  fi
  git push origin "$DEFAULT_BRANCH"

  # Cleanup feature branch (local + remote).
  echo "[RLDYOUR-FLOW AUTO] deleting merged branch $BRANCH" >&2
  git branch -d "$BRANCH" 2>/dev/null || true
  git push origin --delete "$BRANCH" 2>/dev/null || true
fi

# Step 4: publish fullrepo (agent-only files).
echo "[RLDYOUR-FLOW AUTO] publishing fullrepo" >&2
python3 "$FULLREPO_SCRIPT" --publish

# Step 5: cleanup merged branches and worktrees that flow_post_task_state already
# identified as safe candidates.
CLEANUP_LOCAL=$(printf "%s" "$STATE_JSON" | python3 -c '
import json, sys
state = json.load(sys.stdin).get("branch_cleanup_state", {})
for b in state.get("local_merged_branches", []):
    print(b)
')
for b in $CLEANUP_LOCAL; do
  if [ "$b" != "$DEFAULT_BRANCH" ] && ! echo "$b" | grep -Eq "$PROTECTED_BRANCHES_RE"; then
    git branch -d "$b" 2>/dev/null && echo "[RLDYOUR-FLOW AUTO] deleted merged local branch $b" >&2 || true
  fi
done

CLEANUP_REMOTE=$(printf "%s" "$STATE_JSON" | python3 -c '
import json, sys
state = json.load(sys.stdin).get("branch_cleanup_state", {})
for b in state.get("remote_merged_branches", []):
    print(b)
')
for b in $CLEANUP_REMOTE; do
  if [ "$b" != "$DEFAULT_BRANCH" ] && ! echo "$b" | grep -Eq "$PROTECTED_BRANCHES_RE"; then
    git push origin --delete "$b" 2>/dev/null && echo "[RLDYOUR-FLOW AUTO] deleted merged remote branch $b" >&2 || true
  fi
done

CLEANUP_WORKTREES=$(printf "%s" "$STATE_JSON" | python3 -c '
import json, sys
state = json.load(sys.stdin).get("branch_cleanup_state", {})
for path in state.get("worktree_cleanup_candidates", []):
    print(path)
')
for wt in $CLEANUP_WORKTREES; do
  if [ -d "$wt" ] && [ "$wt" != "$ROOT" ]; then
    git worktree remove "$wt" --force 2>/dev/null && echo "[RLDYOUR-FLOW AUTO] removed worktree $wt" >&2 || true
  fi
done

# Step 6: clear runtime markers, allow stop.
rm -f "$SYNC_MARKER" .serena/.flow_post_task_state.json

echo "[RLDYOUR-FLOW AUTO] post-task pipeline complete: head=$HEAD_SHA branch=$DEFAULT_BRANCH" >&2
exit 0
