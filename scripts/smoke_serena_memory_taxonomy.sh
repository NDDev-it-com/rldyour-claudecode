#!/usr/bin/env bash
# smoke_serena_memory_taxonomy.sh — focused checks for the Serena memory brain contract.
#
# Coverage:
#   1. analyze_sync_scope.py schema v2, taxonomy, and target routing.
#   2. agent-instruction-only commits require memory sync.
#   3. serena_memory_state.py counts nested .serena/memories/**/*.md files.
#   4. stop_memory_sync.sh stale advisory includes taxonomy guidance and loop guard works.
#   5. commit_serena_knowledge.sh acknowledges fullrepo-managed current memories and
#      refuses stale memories.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ANALYZER="$ROOT/plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py"
STATE_SCRIPT="$ROOT/plugins/rldyour-serena-mcp/scripts/serena_memory_state.py"
MARK_HOOK="$ROOT/plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh"
STOP_HOOK="$ROOT/plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh"
COMMIT_SCRIPT="$ROOT/plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh"

step() {
  printf '\n\033[1;36m== %s ==\033[0m\n' "$1"
}

fail() {
  printf '\033[1;31m%s\033[0m\n' "$1" >&2
  exit 1
}

git_commit() {
  git -c user.name="rldyour smoke" -c user.email="smoke@example.invalid" commit -q -m "$1"
}

assert_json() {
  python3 - "$@"
}

step "analyzer schema and target routing"
assert_json "$ANALYZER" <<'PY'
import json
import subprocess
import sys

analyzer = sys.argv[1]


def analyze(*paths: str) -> dict:
    args = ["python3", analyzer]
    for path in paths:
        args.extend(["--path", path])
    proc = subprocess.run(args, check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


def target_paths(payload: dict) -> set[str]:
    return {item["path"] for item in payload.get("memory_targets", [])}


empty = analyze()
assert empty["schema_version"] == 2, empty
assert empty["memory_taxonomy"]["index_memory"] == "CORE-01-INDEX.md", empty
assert empty["memory_taxonomy"]["filename_pattern"] == "AREA-01-SLUG.md", empty
assert empty["memory_targets"] == [], empty

cases = [
    (
        ("plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py",),
        {"SERENA-01-MEMORY-SYNC.md", "HOOKS-01-LIFECYCLE.md", "CORE-02-MARKETPLACE.md"},
    ),
    (
        ("plugins/rldyour-serena-mcp/README.md",),
        {"SERENA-01-MEMORY-SYNC.md", "HOOKS-01-LIFECYCLE.md", "CORE-02-MARKETPLACE.md"},
    ),
    (
        ("plugins/rldyour-serena-mcp/agents/flow-memory-sync.md",),
        {
            "SERENA-01-MEMORY-SYNC.md",
            "HOOKS-01-LIFECYCLE.md",
            "CORE-02-MARKETPLACE.md",
            "CLAUDECODE-01-PLUGIN-CANON.md",
        },
    ),
    (
        ("AGENTS.md",),
        {"DOCS-01-INSTRUCTIONS.md", "TECHDEBT-01-NOW.md", "CLAUDECODE-01-PLUGIN-CANON.md"},
    ),
    (
        ("plugins/rldyour-flow/hooks/stop_post_task_sync.sh",),
        {"FLOW-01-SDLC.md", "HOOKS-01-LIFECYCLE.md", "TECHDEBT-01-NOW.md", "CLAUDECODE-01-PLUGIN-CANON.md"},
    ),
]

for paths, expected in cases:
    payload = analyze(*paths)
    actual = target_paths(payload)
    missing = expected - actual
    assert not missing, {"paths": paths, "missing": sorted(missing), "actual": sorted(actual)}

print("OK analyzer taxonomy targets")
PY

TMP_ROOT=$(mktemp -d)
trap 'rm -rf "$TMP_ROOT"' EXIT

step "agent-instruction commits require sync"
MARK_REPO="$TMP_ROOT/mark"
mkdir "$MARK_REPO"
cd "$MARK_REPO"
git init -q
printf 'base\n' > README.md
git add README.md
git_commit "init"
PRE_HEAD=$(git rev-parse HEAD)
mkdir -p .serena
printf '%s\n' "$PRE_HEAD" > .serena/.auto_sync_head
printf '# Agent docs\n' > AGENTS.md
git add AGENTS.md
git_commit "docs"
printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m docs"}}' | bash "$MARK_HOOK" >/dev/null
if [ ! -f .serena/.serena_sync_state.json ]; then
  fail "mark hook did not write .serena/.serena_sync_state.json"
fi
assert_json <<'PY'
import json
payload = json.load(open(".serena/.serena_sync_state.json", encoding="utf-8"))
targets = {item["path"] for item in payload["analysis"]["memory_targets"]}
assert payload["required"] is True, payload
assert "AGENTS.md" in payload["non_knowledge_changed_files"], payload
assert {"DOCS-01-INSTRUCTIONS.md", "TECHDEBT-01-NOW.md", "CLAUDECODE-01-PLUGIN-CANON.md"} <= targets, targets
print("OK agent instruction marker")
PY

step "recursive memory state scan"
STATE_REPO="$TMP_ROOT/state"
mkdir "$STATE_REPO"
cd "$STATE_REPO"
git init -q
printf 'state\n' > file.txt
git add file.txt
git_commit "init"
HEAD_SHORT=$(git rev-parse --short=7 HEAD)
mkdir -p .serena/memories/SERENA
cat > .serena/memories/SERENA/NESTED.md <<EOF
<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: ${HEAD_SHORT} init
Scope: nested smoke
Area: SERENA
-->

# SERENA-NESTED
EOF
STATE_JSON=$(python3 "$STATE_SCRIPT")
assert_json "$STATE_JSON" <<'PY'
import json
import sys
payload = json.loads(sys.argv[1])
assert payload["memory_count"] == 1, payload
assert payload["memory_directly_mentions_head"] is True, payload
assert payload["memory_match_reason"] == "direct-head-reference", payload
assert payload["is_current"] is True, payload
print("OK nested memory scan")
PY

step "stop hook stale advisory and loop guard"
STOP_REPO="$TMP_ROOT/stop"
mkdir "$STOP_REPO"
cd "$STOP_REPO"
git init -q
printf 'base\n' > base.txt
git add base.txt
git_commit "init"
OLD_SHORT=$(git rev-parse --short=7 HEAD)
mkdir -p .serena/memories
cat > .serena/memories/CORE-01-INDEX.md <<EOF
<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: ${OLD_SHORT} init
Scope: smoke
Area: CORE
-->

# CORE-01-INDEX
EOF
printf '# Agent docs\n' > AGENTS.md
git add AGENTS.md
git_commit "docs"
set +e
bash "$STOP_HOOK" >stop.out 2>stop.err
STOP_RC=$?
set -e
if [ "$STOP_RC" -ne 2 ]; then
  cat stop.err >&2
  fail "stop hook expected exit 2, got $STOP_RC"
fi
grep -q "Memory taxonomy" stop.err || fail "stop advisory missing Memory taxonomy"
grep -q "CORE-01-INDEX.md" stop.err || fail "stop advisory missing CORE-01-INDEX.md"
grep -q "AREA-01-SLUG.md" stop.err || fail "stop advisory missing AREA-01-SLUG.md"
grep -q "DOCS-01-INSTRUCTIONS.md" stop.err || fail "stop advisory missing DOCS target"
set +e
printf '{"stop_hook_active":true}' | bash "$STOP_HOOK" >/dev/null 2>loop.err
LOOP_RC=$?
set -e
if [ "$LOOP_RC" -ne 0 ]; then
  cat loop.err >&2
  fail "stop loop guard expected exit 0, got $LOOP_RC"
fi
echo "OK stop hook advisory"

step "fullrepo-managed commit acknowledgement"
ACK_REPO="$TMP_ROOT/ack"
mkdir "$ACK_REPO"
cd "$ACK_REPO"
git init -q
printf 'ack\n' > file.txt
git add file.txt
git_commit "init"
CURRENT_SHORT=$(git rev-parse --short=7 HEAD)
mkdir -p .serena/memories .git/info
cat >> .git/info/exclude <<'EOF'
.serena/memories/**
EOF
cat > .serena/memories/CORE-01-INDEX.md <<EOF
<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: ${CURRENT_SHORT} init
Scope: smoke
Area: CORE
-->

# CORE-01-INDEX
EOF
touch .serena/.sync_marker .serena/.serena_sync_state.json .serena/.auto_sync_head
BEFORE=$(git rev-parse HEAD)
bash "$COMMIT_SCRIPT" >/dev/null
AFTER=$(git rev-parse HEAD)
test "$BEFORE" = "$AFTER" || fail "commit_serena_knowledge created a commit in fullrepo-managed ack path"
test ! -e .serena/.sync_marker || fail "sync marker was not cleared"
test ! -e .serena/.serena_sync_state.json || fail "sync state was not cleared"
test ! -e .serena/.auto_sync_head || fail "auto sync marker was not cleared"

STALE_REPO="$TMP_ROOT/stale"
mkdir "$STALE_REPO"
cd "$STALE_REPO"
git init -q
printf 'old\n' > file.txt
git add file.txt
git_commit "old"
OLD_SHORT=$(git rev-parse --short=7 HEAD)
printf 'new\n' > file.txt
git add file.txt
git_commit "new"
mkdir -p .serena/memories .git/info
cat >> .git/info/exclude <<'EOF'
.serena/memories/**
EOF
cat > .serena/memories/CORE-01-INDEX.md <<EOF
<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: ${OLD_SHORT} old
Scope: smoke
Area: CORE
-->

# CORE-01-INDEX
EOF
touch .serena/.sync_marker
set +e
STALE_ERR="$TMP_ROOT/stale.err"
bash "$COMMIT_SCRIPT" >/dev/null 2>"$STALE_ERR"
STALE_RC=$?
set -e
if [ "$STALE_RC" -eq 0 ]; then
  fail "commit_serena_knowledge acknowledged stale fullrepo-managed memory"
fi
if ! grep -Eq "do not match HEAD|memories do not match" "$STALE_ERR"; then
  cat "$STALE_ERR" >&2
  fail "stale ack error message missing"
fi
echo "OK fullrepo-managed acknowledgement"

cd "$ROOT"
printf '\n\033[1;32m✔ smoke_serena_memory_taxonomy passed\033[0m\n'
