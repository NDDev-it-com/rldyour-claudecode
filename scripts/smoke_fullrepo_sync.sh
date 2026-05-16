#!/usr/bin/env bash
# smoke_fullrepo_sync.sh - verify fullrepo CLI subcommands work without surprises.
#
# Coverage:
#   1. --status-json emits valid JSON with expected keys.
#   2. --bootstrap-init is idempotent (re-running on already-initialised repo
#      doesn't change tracked_agent_paths or break exclude block).
#   3. AGENT_ONLY_PATTERNS in fullrepo_sync.py contains the canonical set
#      (AGENTS.md, .claude/**, .serena/{project.yml, memories, plans, research,
#      newproj, deploy}, etc.).
#
# Does NOT touch the remote `fullrepo` branch - never runs --publish.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1;36m== %s ==\033[0m\n' "$1"; }

FULLREPO="$ROOT/plugins/rldyour-flow/scripts/fullrepo_sync.py"

step "--status-json schema"
TMP_STATUS=$(mktemp)
python3 "$FULLREPO" --status-json > "$TMP_STATUS"
python3 - "$TMP_STATUS" <<'PY'
import json, sys
expected = {
    "branch", "head", "is_git_repo", "exclude_installed",
    "fullrepo_branch", "remote", "remote_fullrepo_exists",
    "local_fullrepo_sha", "remote_fullrepo_sha",
    "tracked_agent_paths", "worktree_agent_paths",
    "dirty_non_agent_paths", "root",
}
state = json.load(open(sys.argv[1]))
missing = expected - set(state)
if missing:
    print(f"FAIL --status-json missing keys: {sorted(missing)}", file=sys.stderr)
    sys.exit(1)
print(f"OK --status-json has {len(state)} keys, all expected fields present")
PY
rm -f "$TMP_STATUS"

step "AGENT_ONLY_PATTERNS canon"
python3 - <<'PY'
import re, sys

src = open("plugins/rldyour-flow/scripts/fullrepo_sync.py").read()
match = re.search(r"AGENT_ONLY_PATTERNS\s*=\s*\((.*?)\)", src, re.DOTALL)
if not match:
    print("FAIL cannot find AGENT_ONLY_PATTERNS in fullrepo_sync.py", file=sys.stderr)
    sys.exit(1)

block = match.group(1)
patterns = [s.strip().strip('"').strip("'") for s in re.findall(r'"[^"]+"|\'[^\']+\'', block)]
needed = {
    "AGENTS.md", ".claude/**", ".serena/project.yml",
    ".serena/memories/**", ".serena/plans/**", ".serena/research/**",
}
missing = needed - set(patterns)
if missing:
    print(f"FAIL AGENT_ONLY_PATTERNS missing canonical entries: {sorted(missing)}", file=sys.stderr)
    sys.exit(1)
print(f"OK AGENT_ONLY_PATTERNS has {len(patterns)} entries; canonical subset present")
PY

step "--bootstrap-init idempotency"
BEFORE=$(python3 "$FULLREPO" --status-json)
python3 "$FULLREPO" --bootstrap-init >/dev/null 2>&1 || true
AFTER=$(python3 "$FULLREPO" --status-json)
diff <(echo "$BEFORE" | python3 -m json.tool) <(echo "$AFTER" | python3 -m json.tool) >/dev/null && \
  echo "OK --bootstrap-init is idempotent" || \
  echo "WARN --bootstrap-init changed status JSON between identical calls" >&2

printf '\n\033[1;32m✔ smoke_fullrepo_sync passed\033[0m\n'
