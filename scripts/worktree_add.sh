#!/usr/bin/env bash
# worktree_add.sh — one-step git worktree creation for the rldyour-claudecode
# marketplace.
#
# Wraps `git worktree add` + `fullrepo_sync.py --restore` so a fresh
# worktree comes up with the full agent-only context (AGENTS.md,
# .claude/CLAUDE.md, .serena/project.yml, .serena/memories/**) already in
# place. Designed for the parallel-sessions workflow: each worktree gets its
# own working directory and its own agent-only file copy, while sharing the
# same .git object database with the main worktree.
#
# Usage:
#   scripts/worktree_add.sh <branch> [path]
#
# Examples:
#   scripts/worktree_add.sh feat/foo
#       Creates a worktree at ../rldyour-claudecode-feat-foo on branch
#       feat/foo. If the branch doesn't exist, it is created off
#       origin/main (configurable via RLDYOUR_WORKTREE_BASE_REF).
#
#   scripts/worktree_add.sh feat/foo /tmp/rldyour-foo
#       Same, with an explicit worktree path.
#
# Environment:
#   RLDYOUR_WORKTREE_BASE_REF   Ref to branch from when creating a new branch.
#                       Default: origin/main. Set to "HEAD" to preserve
#                       unpushed local commits, mirroring Claude Code's
#                       `worktree.baseRef: "head"` setting.
#   RLDYOUR_DRY_RUN=1   Print what would happen, do not execute.
#
# This script invokes `fullrepo_sync.py --restore` (NOT --bootstrap-init).
# Restore is purely additive — it fetches origin/fullrepo, installs the
# per-worktree .git/info/exclude block, and checks out agent-only paths.
# It NEVER pushes, NEVER publishes, NEVER touches origin write-side.
# If `origin/fullrepo` does not exist yet, the script aborts with a clear
# message instructing the user to publish from the main worktree first via
# `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish`.
#
# Exit codes: 0 success, non-zero on git failure or bootstrap failure.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT}"

BRANCH="${1:-}"
EXPLICIT_PATH="${2:-}"

if [[ -z "${BRANCH}" ]]; then
  cat >&2 <<EOF
usage: scripts/worktree_add.sh <branch> [path]

Creates a git worktree and runs fullrepo_sync.py --restore so the
worktree is immediately usable for a parallel Claude Code session.

See file header for environment variables and examples.
EOF
  exit 2
fi

# Defensive validation: reject branch names containing characters that would
# let `git worktree add` interpret them as options (e.g. -c, --upload-pack).
# Allowed set covers normal git ref characters (letters, digits, dot, slash,
# underscore, hyphen) with a 255-char ceiling. If you legitimately need
# something exotic (Unicode, +, =), update this regex consciously rather than
# loosening it on first failure.
if ! [[ "${BRANCH}" =~ ^[A-Za-z0-9._/-]{1,255}$ ]]; then
  echo "FAIL invalid branch name '${BRANCH}' — must match ^[A-Za-z0-9._/-]{1,255}\$ (rejected to prevent git-option injection via crafted branch strings)" >&2
  exit 1
fi

# Second gate: git's own check-ref-format. The regex above is conservative but
# allows refs git itself rejects (leading hyphen, leading slash, `..`, trailing
# slash, etc.). Asking git to validate gives us the exact rules of
# git-check-ref-format(1) without re-implementing them.
if ! git check-ref-format --branch "${BRANCH}" >/dev/null 2>&1; then
  echo "FAIL branch name '${BRANCH}' rejected by git check-ref-format (invalid ref structure)" >&2
  exit 1
fi

BASE_REF="${RLDYOUR_WORKTREE_BASE_REF:-origin/main}"
DRY_RUN="${RLDYOUR_DRY_RUN:-0}"

# Default worktree path: sibling of main repo, suffixed with the branch
# (with slashes replaced by hyphens for filesystem safety).
if [[ -n "${EXPLICIT_PATH}" ]]; then
  WT_PATH="${EXPLICIT_PATH}"
else
  REPO_NAME="$(basename "${ROOT}")"
  SAFE_BRANCH="$(printf '%s' "${BRANCH}" | tr '/' '-')"
  WT_PATH="$(cd "${ROOT}/.." && pwd)/${REPO_NAME}-${SAFE_BRANCH}"
fi

WT_PATH="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${WT_PATH}")"

if [[ -e "${WT_PATH}" ]]; then
  echo "FAIL worktree path already exists: ${WT_PATH}" >&2
  exit 1
fi

# Decide: does the branch exist locally, on origin, or do we need to create it?
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  BRANCH_MODE="existing-local"
  GIT_ARGS=(worktree add -- "${WT_PATH}" "${BRANCH}")
elif git show-ref --verify --quiet "refs/remotes/origin/${BRANCH}"; then
  BRANCH_MODE="existing-remote"
  GIT_ARGS=(worktree add --track -b "${BRANCH}" -- "${WT_PATH}" "origin/${BRANCH}")
else
  BRANCH_MODE="new-from-${BASE_REF}"
  GIT_ARGS=(worktree add -b "${BRANCH}" -- "${WT_PATH}" "${BASE_REF}")
fi

echo "==> rldyour-claudecode worktree_add"
echo "    branch     : ${BRANCH} (${BRANCH_MODE})"
echo "    path       : ${WT_PATH}"
echo "    base ref   : ${BASE_REF}"
echo "    main root  : ${ROOT}"

if [[ "${DRY_RUN}" = "1" ]]; then
  echo "    [dry-run] would run: git ${GIT_ARGS[*]}"
  echo "    [dry-run] would run: python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --restore (cwd: ${WT_PATH})"
  exit 0
fi

# Before creating the worktree, verify origin/fullrepo exists. Otherwise
# --restore in the new worktree would be a no-op and the user would end up
# with an empty agent-only context, wondering why. We intentionally do NOT
# fall through to --publish here — publishing is a high-blast-radius
# operation that must stay under explicit user judgement, not buried in a
# helper script.
STATUS_JSON=$(python3 "${ROOT}/plugins/rldyour-flow/scripts/fullrepo_sync.py" --status-json 2>/dev/null || true)
REMOTE_PRESENT=$(printf '%s' "${STATUS_JSON}" | python3 -c '
import json, sys
try:
    s = json.load(sys.stdin)
except Exception:
    print("false")
    raise SystemExit(0)
print("true" if s.get("remote_fullrepo_exists") else "false")
' 2>/dev/null || echo "false")

if [[ "${REMOTE_PRESENT}" != "true" ]]; then
  cat >&2 <<EOF
FAIL origin/fullrepo does not exist yet — refusing to auto-publish from a helper script.

Run this once from the main worktree to seed it:
    python3 ${ROOT}/plugins/rldyour-flow/scripts/fullrepo_sync.py --publish

Then re-run scripts/worktree_add.sh.
EOF
  exit 1
fi

# Create the worktree.
git "${GIT_ARGS[@]}"

# Bootstrap agent-only context into the new worktree via --restore (NOT
# --bootstrap-init): restore fetches origin/fullrepo and writes only into
# the worktree; it does not publish under any branch.
(
  cd "${WT_PATH}"
  python3 "${ROOT}/plugins/rldyour-flow/scripts/fullrepo_sync.py" --restore
)

cat <<EOF

==> worktree ready
    cd "${WT_PATH}"
    claude        # opens Claude Code with full agent-only context

The new worktree shares the same .git database with the main repo (origin,
fullrepo, refs, packs). Each worktree has its own:
  - working tree
  - .git/info/exclude block (per-worktree)
  - .serena/memories/ (restored from origin/fullrepo at bootstrap)

To remove later:
    git worktree remove "${WT_PATH}"
EOF
