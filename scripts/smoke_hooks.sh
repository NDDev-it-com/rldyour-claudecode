#!/usr/bin/env bash
# smoke_hooks.sh - verify hook lifecycle scripts exist, parse, and execute cleanly with skip flags.
#
# Coverage:
#   1. hooks.json files parse as JSON.
#   2. Every command-handler script referenced exists, is executable, has valid bash syntax.
#   3. Every script exits 0 when its skip flag is set (no side effects).
#   4. Every script exits 0 outside a git work tree (defensive guard active).
#
# This is a static smoke - it does not exercise actual hook firing during a
# Claude Code session. Use `claude --debug api,hooks` for live observation.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

step() {
  printf '\n\033[1;36m== %s ==\033[0m\n' "$1"
}

fail() {
  printf '\033[1;31m%s\033[0m\n' "$1" >&2
  exit 1
}

step "hooks.json parse"
for hf in plugins/rldyour-flow/hooks/hooks.json plugins/rldyour-serena-mcp/hooks/hooks.json; do
  if [ ! -f "$hf" ]; then
    fail "missing $hf"
  fi
  python3 -c "import json,sys; json.load(open('$hf'))" || fail "invalid JSON: $hf"
  echo "OK $hf"
done

step "hook scripts exist + bash -n"
fail_count=0
HOOK_SCRIPTS=$(python3 - <<'PY'
import json, glob, re

scripts = []
for hf in glob.glob("plugins/*/hooks/hooks.json"):
    plugin_dir = hf.split("/hooks/")[0]
    data = json.load(open(hf))
    for event_handlers in data.get("hooks", {}).values():
        for matcher_block in event_handlers:
            for handler in matcher_block.get("hooks", []):
                if handler.get("type") != "command":
                    continue
                cmd = handler.get("command", "")
                # Extract script path: bash ${CLAUDE_PLUGIN_ROOT}/hooks/<script>.sh
                m = re.search(r"hooks/([\w._-]+\.sh)", cmd)
                if m:
                    scripts.append(f"{plugin_dir}/hooks/{m.group(1)}")

for s in sorted(set(scripts)):
    print(s)
PY
)

while IFS= read -r script; do
  [ -z "$script" ] && continue
  if [ ! -f "$script" ]; then
    echo "FAIL missing: $script" >&2
    fail_count=$((fail_count+1))
    continue
  fi
  if [ ! -x "$script" ]; then
    echo "FAIL not executable: $script" >&2
    fail_count=$((fail_count+1))
    continue
  fi
  if ! bash -n "$script"; then
    echo "FAIL bash -n: $script" >&2
    fail_count=$((fail_count+1))
    continue
  fi
  echo "OK $script"
done <<< "$HOOK_SCRIPTS"

test "$fail_count" -eq 0 || fail "hook script checks failed"

step "skip-flag exit 0"
SKIP_TESTS=(
  "RLDYOUR_SKIP_FLOW_SESSION_CONTEXT=1:plugins/rldyour-flow/hooks/session_start_context.sh"
  "RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1:plugins/rldyour-flow/hooks/session_start_worktree_bootstrap.sh"
  "RLDYOUR_SKIP_FLOW_COMMIT_ADVICE=1:plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh"
  "RLDYOUR_SKIP_STOP_GATES=1:plugins/rldyour-flow/hooks/stop_post_task_sync.sh"
  "RLDYOUR_SKIP_STOP_GATES=1:plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh"
  "RLDYOUR_SKIP_FLOW_SYNC=1:plugins/rldyour-flow/hooks/stop_post_task_sync.sh"
  "RLDYOUR_SKIP_SERENA_SYNC=1:plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh"
)

for entry in "${SKIP_TESTS[@]}"; do
  flag="${entry%%:*}"
  script="${entry#*:}"
  if env -i PATH="$PATH" $flag bash "$script" </dev/null >/dev/null 2>&1; then
    echo "OK $flag → $script exits 0"
  else
    echo "FAIL $flag did not short-circuit $script" >&2
    fail_count=$((fail_count+1))
  fi
done

test "$fail_count" -eq 0 || fail "skip-flag checks failed"

step "outside-git defensive guard"
TMP=$(mktemp -d)
# Use single quotes so $TMP is expanded when the trap fires (not now), and
# quote the variable to handle paths with spaces (shellcheck SC2064 fix).
trap 'rm -rf "$TMP"' EXIT
for script in plugins/rldyour-flow/hooks/*.sh plugins/rldyour-serena-mcp/hooks/*.sh; do
  if (cd "$TMP" && bash "$ROOT/$script" </dev/null >/dev/null 2>&1); then
    echo "OK $script exits 0 outside git tree"
  else
    rc=$?
    echo "FAIL $script exited $rc outside git tree" >&2
    fail_count=$((fail_count+1))
  fi
done

test "$fail_count" -eq 0 || fail "defensive-guard checks failed"

step "runtime stdin payloads (parse safety + advisory routing)"
# This step actually exercises each hook with realistic JSON stdin to verify
# that the recent shell strict mode changes (IFS=$'\n\t' + unset CDPATH) didn't
# break stdin parsing. Hooks that mutate state (mark_sync_required.sh,
# prepare_auto_sync.sh) are intentionally not exercised here - they write to
# .serena/.serena_sync_state.json and .serena/.auto_sync_head, which would
# pollute the working tree state during a smoke run.

# UserPromptSubmit: empty prompt should silently exit 0 (no additionalContext).
empty_out=$(printf '%s' '{"prompt":""}' | bash plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh 2>/dev/null || true)
if [ -z "$empty_out" ]; then
  echo "OK user_prompt_submit empty prompt → no advisory"
else
  echo "FAIL user_prompt_submit emitted advisory on empty prompt: $empty_out" >&2
  fail_count=$((fail_count+1))
fi

# UserPromptSubmit: non-code prompt should silently exit 0.
nontrig_out=$(printf '%s' '{"prompt":"hello there"}' | bash plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh 2>/dev/null || true)
if [ -z "$nontrig_out" ]; then
  echo "OK user_prompt_submit non-trigger prompt → no advisory"
else
  echo "FAIL user_prompt_submit emitted advisory on non-trigger prompt" >&2
  fail_count=$((fail_count+1))
fi

# UserPromptSubmit: Russian code-related prompt should emit Serena-first advisory.
ru_out=$(printf '%s' '{"prompt":"изучи код в этом проекте и найди класс RouterModule"}' | bash plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh 2>/dev/null || true)
if printf '%s' "$ru_out" | python3 -c "import json,sys; d=json.load(sys.stdin); ctx=d.get('hookSpecificOutput',{}).get('additionalContext',''); sys.exit(0 if 'Serena-first' in ctx else 1)" 2>/dev/null; then
  echo "OK user_prompt_submit RU code-related prompt → Serena-first advisory"
else
  echo "FAIL user_prompt_submit did not emit Serena-first advisory for RU code prompt" >&2
  fail_count=$((fail_count+1))
fi

# UserPromptSubmit: English code-related prompt should also emit advisory.
en_out=$(printf '%s' '{"prompt":"inspect the repository and refactor this method"}' | bash plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh 2>/dev/null || true)
if printf '%s' "$en_out" | python3 -c "import json,sys; d=json.load(sys.stdin); ctx=d.get('hookSpecificOutput',{}).get('additionalContext',''); sys.exit(0 if 'Serena-first' in ctx else 1)" 2>/dev/null; then
  echo "OK user_prompt_submit EN code-related prompt → Serena-first advisory"
else
  echo "FAIL user_prompt_submit did not emit Serena-first advisory for EN code prompt" >&2
  fail_count=$((fail_count+1))
fi

# Stop hooks: stop_hook_active=true should pass through without blocking when
# current state already matches the loop-guard marker. The hook reads stdin
# JSON via python3 - a parse error would surface as exit code 0 (silent) but
# we already cover parse safety via skip-flag/outside-git tests above. Here
# we verify behaviour on stop_hook_active=false (normal Stop) - should also
# exit 0 when serena+flow state is already clean.
clean_stop_out=$(printf '%s' '{"stop_hook_active":false}' | bash plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh 2>&1 || true)
if [ -z "$clean_stop_out" ] || ! printf '%s' "$clean_stop_out" | grep -q "SYNC REQUIRED"; then
  echo "OK stop_memory_sync clean state → no blocking advisory"
else
  # Memory may have legitimately been stale at this point in the smoke run.
  # Just record it; don't fail.
  echo "INFO stop_memory_sync emitted advisory (memories may be stale; not a smoke failure)"
fi

# PostToolUse:Bash with non-git command should silently exit 0.
non_git_out=$(printf '%s' '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | bash plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh 2>/dev/null || true)
if [ -z "$non_git_out" ]; then
  echo "OK post_tool_use_commit_advice non-git command → silent"
else
  echo "FAIL post_tool_use_commit_advice emitted advisory for non-git command" >&2
  fail_count=$((fail_count+1))
fi

test "$fail_count" -eq 0 || fail "runtime stdin checks failed"

printf '\n\033[1;32m✔ smoke_hooks passed\033[0m\n'
