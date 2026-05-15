#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not a git repository"
  exit 1
fi

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

echo "Repository: $ROOT"
echo "Branch: $(git branch --show-current 2>/dev/null || echo detached)"
echo "HEAD: $(git rev-parse --short=12 HEAD)"

UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)
if [ -n "$UPSTREAM" ]; then
  echo "Upstream: $UPSTREAM"
  git rev-list --left-right --count "$UPSTREAM...HEAD" | awk '{print "Behind: "$1"\nAhead: "$2}'
else
  echo "Upstream: none"
fi

echo
echo "Status:"
git status --short

echo
echo "Worktrees:"
git worktree list

echo
echo "Branches:"
git branch --format='%(refname:short) %(upstream:short) %(committerdate:relative)'

BASE_REF=origin/main
if ! git rev-parse --verify --quiet "$BASE_REF" >/dev/null; then
  BASE_REF=main
fi

echo
echo "Merged local branches cleanup candidates (base: $BASE_REF):"
git branch --format='%(refname:short)' --merged "$BASE_REF" \
  | grep -Ev '^(main|master|develop|development|staging|production|prod|fullrepo)$' \
  | grep -Fvx "$(git branch --show-current 2>/dev/null || true)" \
  || true

echo
echo "Merged remote branches cleanup candidates (base: $BASE_REF):"
git branch -r --format='%(refname:short) %(symref)' --merged "$BASE_REF" \
  | awk '$2 == "" { print $1 }' \
  | grep -Ev '(/HEAD| -> |^(origin/)?(main|master|develop|development|staging|production|prod|fullrepo)$)' \
  || true
