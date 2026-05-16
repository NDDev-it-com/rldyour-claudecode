#!/usr/bin/env bash
# validate_marketplace.sh — primary validation harness for the rldyour-claude marketplace.
#
# Runs claude plugin validate (marketplace + every plugin), JSON parse for all
# manifest files, Python AST and shell syntax checks, frontmatter presence on
# skills/agents/commands, plugin-version consistency, instruction-docs presence,
# skill-routing policy, and MCP runtime version drift.
#
# This is the canonical "did I break the marketplace" command. CI mirrors most
# of these checks via .github/workflows/validate.yml; running it locally before
# commits keeps PR validation fast.
#
# Exit codes: 0 on success, non-zero on first failure.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

step() {
  printf '\n\033[1;36m== %s ==\033[0m\n' "$1"
}

step "claude plugin validate (marketplace)"
claude plugin validate .

step "claude plugin validate (per-plugin)"
for p in plugins/*/; do
  printf '%s: ' "$(basename "$p")"
  claude plugin validate "$p" 2>&1 | tail -1
done

step "JSON manifests parse"
python3 - <<'PY'
import glob, json, sys
paths = (
    [".claude-plugin/marketplace.json"]
    + sorted(glob.glob("plugins/*/.claude-plugin/plugin.json"))
    + sorted(glob.glob("plugins/*/.mcp.json"))
    + sorted(glob.glob("plugins/*/hooks/hooks.json"))
)
fail = 0
for p in paths:
    try:
        with open(p, "r", encoding="utf-8") as fp:
            json.load(fp)
        print(f"OK {p}")
    except Exception as exc:
        print(f"FAIL {p}: {exc}", file=sys.stderr)
        fail = 1
sys.exit(fail)
PY

step "Python AST"
python3 - <<'PY'
import ast, glob, sys
fail = 0
for p in sorted(glob.glob("plugins/*/scripts/*.py")) + sorted(glob.glob("plugins/*/hooks/*.py")) + sorted(glob.glob("scripts/*.py")):
    try:
        with open(p, "r", encoding="utf-8") as fp:
            ast.parse(fp.read())
        print(f"OK {p}")
    except SyntaxError as e:
        print(f"FAIL {p}: {e}", file=sys.stderr)
        fail = 1
sys.exit(fail)
PY

step "Shell syntax"
fail=0
# Use NUL-delimited find + read pair (shellcheck SC2044) so paths with spaces,
# newlines, or shell metacharacters are handled safely.
while IFS= read -r -d '' f; do
  if bash -n "$f"; then
    echo "OK $f"
  else
    echo "FAIL $f" >&2
    fail=1
  fi
done < <(find plugins scripts -type f -name '*.sh' -print0 2>/dev/null)
test "$fail" -eq 0

step "Frontmatter on SKILL.md / agents / commands"
fail=0
while IFS= read -r -d '' f; do
  if head -1 "$f" | grep -q '^---$'; then
    echo "OK $f"
  else
    echo "MISSING-FRONTMATTER $f" >&2
    fail=1
  fi
done < <(find plugins -type f \( -name 'SKILL.md' -o -path '*/agents/*.md' -o -path '*/commands/*.md' \) -print0)
test "$fail" -eq 0

step "Plugin version consistency (plugin.json vs marketplace entry)"
if [ -f scripts/validate_plugin_versions.py ]; then
  python3 scripts/validate_plugin_versions.py
else
  echo "SKIP scripts/validate_plugin_versions.py not yet present"
fi

step "Instruction docs presence"
if [ -f scripts/validate_instruction_docs.py ]; then
  python3 scripts/validate_instruction_docs.py --require-agent-docs
else
  echo "SKIP scripts/validate_instruction_docs.py not yet present"
fi

step "Skill routing policy"
if [ -f scripts/validate_skill_routing.py ]; then
  python3 scripts/validate_skill_routing.py
else
  echo "SKIP scripts/validate_skill_routing.py not yet present"
fi

step "Agent tools allowlist validation"
python3 scripts/validate_agent_tools.py

step "MCP runtime version drift"
if [ -f scripts/check_mcp_runtime_versions.py ]; then
  python3 scripts/check_mcp_runtime_versions.py
else
  echo "SKIP scripts/check_mcp_runtime_versions.py not yet present"
fi

step "Serena memory taxonomy smoke"
if [ -f scripts/smoke_serena_memory_taxonomy.sh ]; then
  bash scripts/smoke_serena_memory_taxonomy.sh
else
  echo "SKIP scripts/smoke_serena_memory_taxonomy.sh not yet present"
fi

printf '\n\033[1;32m✔ marketplace validation passed\033[0m\n'
