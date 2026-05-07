#!/usr/bin/env bash
set -euo pipefail

SERVER="${1:-}"
ROOT="${2:-$(pwd)}"
cd "$ROOT"

echo "Deploy readiness for: $ROOT"

for file in AGENTS.md .claude/CLAUDE.md CLAUDE.md .serena/deploy/*.md; do
  [ -e "$file" ] || continue
  echo
  echo "Candidate deploy contract: $file"
  grep -nE 'Deploy|Server|SSH|Manager|Logs|Health|Rollback|production|staging' "$file" || true
done

if [ -n "$SERVER" ]; then
  echo
  echo "Requested server: $SERVER"
fi

echo
echo "Git state:"
git status --short

echo
echo "Open PR for current branch:"
gh pr list --state open --head "$(git branch --show-current)" --json number,title,state,url 2>/dev/null || true
