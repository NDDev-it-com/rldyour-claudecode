#!/usr/bin/env bash
# smoke_hooks.sh — verify hook lifecycle scripts exist, parse, and execute cleanly with skip flags.
#
# Coverage:
#   1. hooks.json files parse as JSON.
#   2. Every command-handler script referenced exists, is executable, has valid bash syntax.
#   3. Every script exits 0 when its skip flag is set (no side effects).
#   4. Every script exits 0 outside a git work tree (defensive guard active).
#
# This is a static smoke — it does not exercise actual hook firing during a
# Claude Code session. Use `claude --debug api,hooks` for live observation.

set -euo pipefail

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
trap "rm -rf $TMP" EXIT
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

printf '\n\033[1;32m✔ smoke_hooks passed\033[0m\n'
