#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

FULLREPO_BRANCH=${RLDYOUR_FULLREPO_BRANCH:-fullrepo}
ZERO_SHA_RE='^0{40}$'

AGENT_ONLY_RE='^(AGENTS\.md|CLAUDE\.md|REVIEW\.md|GEMINI\.md|QWEN\.md|\.cursorrules|\.windsurfrules|\.aider.*|\.claude(/|$)|\.cursor/rules(/|$)|\.gemini(/|$)|\.roo(/|$)|\.windsurf(/|$)|\.openhands(/|$)|\.github/copilot-instructions\.md|\.github/instructions(/|$)|\.github/prompts(/|$)|\.agents/(skills|commands|hooks)(/|$)|\.serena/project\.yml|\.serena/(memories|plans|research|newproj|deploy)(/|$))'
RUNTIME_RE='^(\.serena/cache(/|$)|\.serena/\.gitignore$|\.serena/project\.local\.yml$|\.serena/\.(sync_marker|serena_sync_state\.json|auto_sync_head|active_workflow_intent\.json|dirty_stop_ack|flow_sync_marker|flow_post_task_state\.json)$|\.playwright-mcp(/|$)|browser(/|$)|\.env$|\.env\.[^/]+$)'
DEFINITE_SECRET_RE='(ctx7sk-[A-Za-z0-9-]+|ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{16,}|xox[baprs]-[A-Za-z0-9-]+|BEGIN (RSA|OPENSSH|PRIVATE) KEY|Bearer[[:space:]]+[A-Za-z0-9._-]{20,})'
SUSPICIOUS_WORDING_RE='(Bearer token|auth key|localStorage.*(auth|token)|api key|secret|credential)'
AI_MARKER_RE='(AGENTS\.md|CLAUDE\.md|\.serena|\.claude|agent-memory|Claude|ChatGPT|OpenAI|AI-generated)'

failures=0

note() {
  printf '%s\n' "$*" >&2
}

is_zero_sha() {
  [[ $1 =~ $ZERO_SHA_RE ]]
}

range_for_push() {
  local local_sha=$1
  local remote_sha=$2
  if is_zero_sha "$remote_sha"; then
    printf '%s\n' "$local_sha"
  else
    printf '%s..%s\n' "$remote_sha" "$local_sha"
  fi
}

changed_paths() {
  local local_sha=$1
  local remote_sha=$2
  if is_zero_sha "$remote_sha"; then
    git diff-tree --root -r --no-commit-id --name-only "$local_sha"
  else
    git diff --name-only "$remote_sha..$local_sha"
  fi
}

path_exists_at_ref() {
  local ref=$1
  local path=$2
  git cat-file -e "$ref:$path" 2>/dev/null
}

scan_paths_for_definite_secrets() {
  local ref=$1
  shift
  local path
  for path in "$@"; do
    if path_exists_at_ref "$ref" "$path" && git show "$ref:$path" 2>/dev/null | LC_ALL=C grep -Eq "$DEFINITE_SECRET_RE"; then
      note "[RLDYOUR-AI-GUARD] blocked secret-looking content in ${path}"
      failures=1
    fi
  done
}

warn_suspicious_wording() {
  local ref=$1
  shift
  local path
  for path in "$@"; do
    if path_exists_at_ref "$ref" "$path" && git show "$ref:$path" 2>/dev/null | LC_ALL=C grep -Eiq "$SUSPICIOUS_WORDING_RE"; then
      note "[RLDYOUR-AI-GUARD] warning: suspicious security wording in ${path}; verify it is documentation, not a secret"
    fi
  done
}

block_strict_ai_markers() {
  local range=$1
  if git diff --no-ext-diff --unified=0 "$range" -- 2>/dev/null \
    | LC_ALL=C grep -E '^\+[^+]' \
    | LC_ALL=C grep -Eq "$AI_MARKER_RE"; then
    note "[RLDYOUR-AI-GUARD] blocked AI-marker additions on product branch"
    failures=1
  fi
}

guard_product_ref() {
  local local_sha=$1
  local remote_sha=$2
  local remote_ref=$3
  local range
  local paths=()
  local path

  mapfile -t paths < <(changed_paths "$local_sha" "$remote_sha")
  range=$(range_for_push "$local_sha" "$remote_sha")

  for path in "${paths[@]}"; do
    if [[ $path =~ $AGENT_ONLY_RE ]]; then
      note "[RLDYOUR-AI-GUARD] blocked agent-only path on ${remote_ref}: ${path}"
      failures=1
    fi
    if [[ $path =~ $RUNTIME_RE ]]; then
      note "[RLDYOUR-AI-GUARD] blocked runtime/local-only path on ${remote_ref}: ${path}"
      failures=1
    fi
  done

  scan_paths_for_definite_secrets "$local_sha" "${paths[@]}"
  block_strict_ai_markers "$range"
}

guard_fullrepo_ref() {
  local local_sha=$1
  local remote_sha=$2
  local remote_ref=$3
  local range
  local paths=()
  local path

  mapfile -t paths < <(changed_paths "$local_sha" "$remote_sha")
  range=$(range_for_push "$local_sha" "$remote_sha")

  for path in "${paths[@]}"; do
    if [[ $path =~ $RUNTIME_RE ]]; then
      note "[RLDYOUR-AI-GUARD] blocked runtime/local-only path on ${remote_ref}: ${path}"
      failures=1
    fi
  done

  scan_paths_for_definite_secrets "$local_sha" "${paths[@]}"
  warn_suspicious_wording "$local_sha" "${paths[@]}"

  if git diff --no-ext-diff --unified=0 "$range" -- 2>/dev/null \
    | LC_ALL=C grep -E '^\+[^+]' \
    | LC_ALL=C grep -Eq "$AI_MARKER_RE"; then
    note "[RLDYOUR-AI-GUARD] warning: AI-context markers allowed on ${remote_ref}"
  fi
}

main() {
  local local_ref local_sha remote_ref remote_sha
  local fullrepo_ref="refs/heads/${FULLREPO_BRANCH}"

  while read -r local_ref local_sha remote_ref remote_sha; do
    [ -n "${local_ref:-}" ] || continue
    if is_zero_sha "$local_sha"; then
      note "[RLDYOUR-AI-GUARD] branch deletion detected for ${remote_ref}; no content scan"
      continue
    fi

    if [ "$remote_ref" = "$fullrepo_ref" ]; then
      guard_fullrepo_ref "$local_sha" "$remote_sha" "$remote_ref"
    else
      guard_product_ref "$local_sha" "$remote_sha" "$remote_ref"
    fi
  done

  if [ "$failures" -ne 0 ]; then
    note "[RLDYOUR-AI-GUARD] push rejected"
    return 1
  fi

  return 0
}

main "$@"
