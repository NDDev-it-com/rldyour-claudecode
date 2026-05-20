#!/usr/bin/env bash
# smoke_bootstrap_check.sh - verifies the R5 agent-only divergence guard in
# scripts/bootstrap_check.sh covers its four documented code paths:
#   (a) RLDYOUR_FORCE_BOOTSTRAP=1 → WARN to stderr + bypass
#   (b) origin/fullrepo missing → INFO + skip (initial-publish flow)
#   (c) clean match → "OK agent-only files match origin/fullrepo"
#   (d) divergence detected → WARN list + fail() exit 1
#
# This is a behavioral smoke that DOES NOT execute `fullrepo_sync.py
# --bootstrap-init` (which would overwrite agent-only files). Instead it
# performs four assertions:
#   1. Static: each of the four documented code paths is present in the script
#      source (regex anchors on the literal log strings).
#   2. Static: AGENT_ONLY_PATHS bash array and AGENT_ONLY_PATTERNS python tuple
#      contain comparable entry counts (drift detector).
#   3. Static: `.aider*` glob expansion is wired (closes Wave 4 quality F-1).
#   4. Runtime: extracts just the divergence-guard block from bootstrap_check.sh
#      (lines from `step "agent-only divergence guard"` up to the next `step`)
#      and runs it in a subshell with RLDYOUR_FORCE_BOOTSTRAP=1 - must exit 0
#      with WARN bypass message to stderr.
#
# Wired into scripts/validate_marketplace.sh and .github/workflows/validate.yml.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1;36m== %s ==\033[0m\n' "$1"; }
fail() { printf '\033[1;31m%s\033[0m\n' "$1" >&2; exit 1; }

GUARD_FILE="scripts/bootstrap_check.sh"
test -f "$GUARD_FILE" || fail "missing $GUARD_FILE"

step "static path (a): RLDYOUR_FORCE_BOOTSTRAP=1 bypass branch"
grep -q 'RLDYOUR_FORCE_BOOTSTRAP:-0' "$GUARD_FILE" \
  || fail "path (a) missing RLDYOUR_FORCE_BOOTSTRAP env check"
grep -q 'WARN RLDYOUR_FORCE_BOOTSTRAP=1.*BYPASSED' "$GUARD_FILE" \
  || fail "path (a) missing WARN bypass message"
echo "OK path (a) static branch present"

step "static path (b): origin/fullrepo missing branch"
grep -q "origin/fullrepo does not exist yet" "$GUARD_FILE" \
  || fail "path (b) missing initial-publish branch"
grep -q "git ls-remote --exit-code origin fullrepo" "$GUARD_FILE" \
  || fail "path (b) missing remote-existence probe"
echo "OK path (b) static branch present"

step "static path (c): clean-match success branch"
grep -q "OK agent-only files match origin/fullrepo" "$GUARD_FILE" \
  || fail "path (c) missing clean-match success message"
echo "OK path (c) static branch present"

step "static path (d): divergence fail branch"
grep -q "Running --bootstrap-init now would silently overwrite" "$GUARD_FILE" \
  || fail "path (d) missing divergence fail message"
grep -q 'cmp -s "\$file"' "$GUARD_FILE" \
  || fail "path (d) missing byte-equality content comparison"
echo "OK path (d) static branch present"

step ".aider* glob expansion wired (Wave 4 quality F-1 closure)"
grep -q "shopt -s nullglob" "$GUARD_FILE" \
  || fail ".aider* glob expansion missing nullglob"
grep -q "for aider_path in \.aider\*" "$GUARD_FILE" \
  || fail ".aider* glob expansion loop missing"
echo "OK .aider* expansion present"

step "AGENT_ONLY_PATHS bash mirrors AGENT_ONLY_PATTERNS python"
python3 - <<'PY' || fail "AGENT_ONLY_PATHS drift from fullrepo_sync.AGENT_ONLY_PATTERNS"
import re
import sys
from pathlib import Path

guard = Path("scripts/bootstrap_check.sh").read_text(encoding="utf-8")
sync = Path("plugins/rldyour-flow/scripts/fullrepo_sync.py").read_text(encoding="utf-8")

bash_match = re.search(r"AGENT_ONLY_PATHS=\(\n(.*?)\n  \)", guard, re.DOTALL)
py_match = re.search(r"AGENT_ONLY_PATTERNS = \(\n(.*?)\n\)", sync, re.DOTALL)
if not bash_match or not py_match:
    print("missing AGENT_ONLY_PATHS or AGENT_ONLY_PATTERNS block", file=sys.stderr)
    raise SystemExit(1)

bash_paths = set(re.findall(r'^\s*"([^"]+)"', bash_match.group(1), re.MULTILINE))
py_patterns = set(re.findall(r'^\s*"([^"]+)"', py_match.group(1), re.MULTILINE))

def normalize(pattern: str) -> str | None:
    if pattern == ".aider*":
        # bootstrap_check.sh expands this glob at runtime when matching files exist.
        return None
    if pattern.endswith("/**"):
        return pattern[:-3]
    return pattern

py_paths = {p for item in py_patterns if (p := normalize(item)) is not None}
missing = sorted(py_paths - bash_paths)
extra = sorted(bash_paths - py_paths)
if missing or extra:
    if missing:
        print(f"missing in bootstrap_check.sh: {missing}", file=sys.stderr)
    if extra:
        print(f"extra in bootstrap_check.sh: {extra}", file=sys.stderr)
    raise SystemExit(1)

print(f"OK exact static mirror: {len(bash_paths)} bash roots, {len(py_patterns)} python patterns")
PY

step "runtime path (a): extracted guard block honors RLDYOUR_FORCE_BOOTSTRAP=1"
TMP_GUARD=$(mktemp /tmp/smoke_bootstrap_guard.XXXXXX.sh)
trap 'rm -f "$TMP_GUARD"' EXIT
# Build a minimal harness:
#   1. Strict mode prelude.
#   2. Inline step()/fail() helpers (bootstrap_check.sh defines them on a
#      single line each; extracting them via awk function-body regex would
#      misbehave for one-line `step() { ...; }` form because `^}` never
#      matches as a separate line - the resulting awk would dump the entire
#      remainder of the file).
#   3. Just the divergence-guard step extracted via awk range, with the
#      trailing `step "fullrepo bootstrap"` line stripped via `sed '$d'`.
#   4. Sentinel echo to confirm bypass branch falls through cleanly.
{
  cat <<'PRELUDE'
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH
step() { printf '\n\033[1;36m== %s ==\033[0m\n' "$1"; }
fail() { printf '\033[1;31m%s\033[0m\n' "$1" >&2; exit 1; }
PRELUDE
  awk '/^step "agent-only divergence guard/,/^step "fullrepo bootstrap"/' "$GUARD_FILE" \
    | sed '$d'
  printf '%s\n' 'echo "RUNTIME-PATH-A-OK"'
} > "$TMP_GUARD"
# Run extracted block. Path (a) should print WARN to stderr + RUNTIME-PATH-A-OK to stdout.
output_stderr=$(RLDYOUR_FORCE_BOOTSTRAP=1 bash "$TMP_GUARD" 2>&1 >/dev/null || true)
output_stdout=$(RLDYOUR_FORCE_BOOTSTRAP=1 bash "$TMP_GUARD" 2>/dev/null || true)
if ! echo "$output_stderr" | grep -q "WARN RLDYOUR_FORCE_BOOTSTRAP=1.*BYPASSED"; then
  echo "--- stderr ---" >&2
  echo "$output_stderr" >&2
  fail "runtime path (a) did not emit WARN bypass to stderr"
fi
if ! echo "$output_stdout" | grep -q "RUNTIME-PATH-A-OK"; then
  echo "--- stdout ---" >&2
  echo "$output_stdout" >&2
  fail "runtime path (a) did not reach end-of-guard sentinel (bypass branch broke flow)"
fi
echo "OK runtime path (a) bypassed cleanly with WARN to stderr"

printf '\n\033[1;32m✔ smoke_bootstrap_check passed\033[0m\n'
