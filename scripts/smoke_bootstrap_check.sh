#!/usr/bin/env bash
# smoke_bootstrap_check.sh — verifies the R5 agent-only divergence guard in
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
#      and runs it in a subshell with RLDYOUR_FORCE_BOOTSTRAP=1 — must exit 0
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

step "AGENT_ONLY_PATHS bash ⊆ AGENT_ONLY_PATTERNS python (count drift)"
# shellcheck disable=SC2016 # the awk and grep patterns are intentional literals
BASH_COUNT=$(awk '/AGENT_ONLY_PATHS=\(/,/^  \)$/' "$GUARD_FILE" | grep -c '^[[:space:]]*"' || true)
# shellcheck disable=SC2016
PY_COUNT=$(awk '/AGENT_ONLY_PATTERNS = \(/,/^\)$/' plugins/rldyour-flow/scripts/fullrepo_sync.py \
  | grep -c '^[[:space:]]*"' || true)
if [ "$BASH_COUNT" -lt 20 ] || [ "$PY_COUNT" -lt 20 ]; then
  fail "agent-only path arrays look truncated (bash=$BASH_COUNT, py=$PY_COUNT)"
fi
# Bash array is allowed to be slightly smaller because `.aider*` is expanded at
# runtime instead of stored as a glob. Tolerance: BASH within 5 of PY.
DRIFT=$(( PY_COUNT - BASH_COUNT ))
DRIFT_ABS=${DRIFT#-}
if [ "$DRIFT_ABS" -gt 5 ]; then
  fail "agent-only path count drift too large (bash=$BASH_COUNT vs py=$PY_COUNT, drift=$DRIFT)"
fi
echo "OK path arrays in sync (bash=$BASH_COUNT, py=$PY_COUNT, drift=$DRIFT)"

step "runtime path (a): extracted guard block honors RLDYOUR_FORCE_BOOTSTRAP=1"
TMP_GUARD=$(mktemp /tmp/smoke_bootstrap_guard.XXXXXX.sh)
trap 'rm -f "$TMP_GUARD"' EXIT
# Extract the guard block: from `step "agent-only divergence guard"` up to the
# next `step "fullrepo bootstrap"`. Prepend the header (strict mode + cd) so
# the block runs identically in isolation.
awk '
  /^step\(\) \{/ {print; in_step=1; next}
  /^fail\(\) \{/ {print; in_fail=1; next}
  in_step && /^\}/ {print; in_step=0; next}
  in_fail && /^\}/ {print; in_fail=0; next}
  in_step || in_fail {print; next}
' "$GUARD_FILE" > "$TMP_GUARD"
{
  # Strict-mode prelude — heredoc preserves literal $'\n\t' without escape
  # mangling that printf/echo would apply.
  cat <<'PRELUDE'

set -euo pipefail
IFS=$'\n\t'
unset CDPATH
PRELUDE
  awk '/^step "agent-only divergence guard/,/^step "fullrepo bootstrap"/' "$GUARD_FILE" \
    | sed '$d'
  printf '%s\n' 'echo "RUNTIME-PATH-A-OK"'
} >> "$TMP_GUARD"
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
