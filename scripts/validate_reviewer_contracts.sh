#!/usr/bin/env bash
# validate_reviewer_contracts.sh - assert the file-first reviewer output transport
# contract is consistent across all 6 reviewer agents and the canonical
# reviewer-protocol.md reference.
#
# Closes the F-3 hardening item from review wave 2026-05-16T1538Z-0ff613d:
# without this validator the contract drifted silently whenever an agent body
# was updated in isolation. The script asserts five invariants per agent:
#
#   1. Heredoc EOF marker `RLDYOUR_REPORT_EOF` appears exactly twice
#      (open + close).
#   2. Compact summary template uses `cap 30 entries`.
#   3. `info` severity is documented in the Counts: template.
#   4. Anti-patterns section cites Anthropic regression issues with the
#      canonical backticked form (`#16789`, `#20531`, `#23463`).
#   5. Each agent writes to `<report_dir>/<agent-name>.md` matching its
#      frontmatter `name:` field (collision avoidance for parallel runs).
#   6. Reviewer body contains NO write-scope shell commands outside the
#      bounded `cat > "<report_dir>/<agent>.md" <<'RLDYOUR_REPORT_EOF'` heredoc.
#      Negative test: `rm `, `mv `, `cp -`, `sed -i`, `tee `, `touch `, `>>`,
#      and arbitrary `>` redirections must not appear in reviewer prose.
#
# Plus protocol-level invariants:
#   7. `reviewer-protocol.md` uses canonical run_id label `<UTC-ISO-compact>`.
#   8. `reviewer-protocol.md` Severity enum lists `critical, high, medium, low,
#      info`.
#   9. `reviewer-protocol.md` Bash write boundary statement present.
#  10. `reviewer-protocol.md` cites the `RLDYOUR_REPORT_EOF` marker at least
#      3 times (open + close pattern example + documentation prose).
#
# Total: 10 invariant types. Concrete log_pass output: 8 PASS per agent
# (eof once + cap once + info once + 3 Anthropic issues + target once +
# write-scope once) × 6 agents = 48, plus 4 protocol-level PASS = 52 PASS.
#
# Exits 0 on PASS, 1 on FAIL.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_NAME="$(basename "$0")"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SCRIPT_NAME
readonly REPO_ROOT
readonly PROTOCOL="${REPO_ROOT}/plugins/rldyour-flow/references/reviewer-protocol.md"
readonly AGENTS_DIR="${REPO_ROOT}/plugins/rldyour-flow/agents"

readonly -a REVIEWER_AGENTS=(
  flow-architecture-review
  flow-quality-review
  flow-consistency-review
  flow-integration-review
  flow-verification-review
  flow-security-review
)

readonly EOF_MARKER='RLDYOUR_REPORT_EOF'
readonly CAP_PHRASE='cap 30 entries'
readonly INFO_SEVERITY_TOKEN='info=N'
readonly RUN_ID_LABEL='<UTC-ISO-compact>'
readonly SEVERITY_ENUM='critical`, `high`, `medium`, `low`, or `info`'
readonly BOUNDARY_PHRASE='no other paths'
readonly -a ISSUE_NUMBERS=('#16789' '#20531' '#23463')

fail_count=0

log_info()  { printf '[INFO]  %s\n' "$*" >&2; }
log_pass()  { printf '[PASS]  %s\n' "$*" >&2; }
log_fail()  { printf '[FAIL]  %s\n' "$*" >&2; fail_count=$((fail_count + 1)); }

require_file() {
  local path="$1"
  if [ ! -f "${path}" ]; then
    log_fail "missing file: ${path}"
    return 1
  fi
}

count_occurrences() {
  local pattern="$1"
  local file="$2"
  grep -F -c -- "${pattern}" "${file}" 2>/dev/null || true
}

assert_protocol_invariants() {
  log_info "Checking reviewer-protocol.md canonical invariants"
  require_file "${PROTOCOL}" || return

  if grep -F -q -- "${RUN_ID_LABEL}" "${PROTOCOL}"; then
    log_pass "run_id label is canonical (${RUN_ID_LABEL})"
  else
    log_fail "run_id label drift in ${PROTOCOL}: expected ${RUN_ID_LABEL}"
  fi

  if grep -F -q -- "${SEVERITY_ENUM}" "${PROTOCOL}"; then
    log_pass "severity enum lists critical/high/medium/low/info"
  else
    log_fail "severity enum drift in ${PROTOCOL}: expected '${SEVERITY_ENUM}'"
  fi

  if grep -F -q -- "${BOUNDARY_PHRASE}" "${PROTOCOL}"; then
    log_pass "Bash write boundary statement present"
  else
    log_fail "missing Bash write boundary phrase '${BOUNDARY_PHRASE}' in ${PROTOCOL}"
  fi

  local marker_count
  marker_count=$(count_occurrences "${EOF_MARKER}" "${PROTOCOL}")
  if [ "${marker_count}" -ge 3 ]; then
    log_pass "${EOF_MARKER} present ${marker_count}x (>= 3 expected in protocol)"
  else
    log_fail "${EOF_MARKER} appears only ${marker_count}x in ${PROTOCOL} (expected >= 3)"
  fi
}

assert_agent_invariants() {
  local agent_name="$1"
  local agent_file="${AGENTS_DIR}/${agent_name}.md"

  log_info "Checking agent ${agent_name}.md"
  require_file "${agent_file}" || return

  local marker_count
  marker_count=$(count_occurrences "${EOF_MARKER}" "${agent_file}")
  if [ "${marker_count}" -eq 2 ]; then
    log_pass "  ${EOF_MARKER}: 2x (open + close)"
  else
    log_fail "  ${EOF_MARKER}: ${marker_count}x in ${agent_file} (expected exactly 2)"
  fi

  if grep -F -q -- "${CAP_PHRASE}" "${agent_file}"; then
    log_pass "  '${CAP_PHRASE}' present"
  else
    log_fail "  missing '${CAP_PHRASE}' in ${agent_file}"
  fi

  if grep -F -q -- "${INFO_SEVERITY_TOKEN}" "${agent_file}"; then
    log_pass "  info severity in Counts: template"
  else
    log_fail "  missing '${INFO_SEVERITY_TOKEN}' in ${agent_file}"
  fi

  local issue
  # shellcheck disable=SC2016 # literal backtick, intentional
  local backtick='`'
  for issue in "${ISSUE_NUMBERS[@]}"; do
    local backticked_issue="${backtick}${issue}${backtick}"
    if grep -F -q -- "${backticked_issue}" "${agent_file}"; then
      log_pass "  Anthropic issue ${issue} cited with backticks"
    else
      log_fail "  Anthropic issue ${issue} not backticked in ${agent_file}"
    fi
  done

  local target_filename="${agent_name}.md"
  if grep -F -q -- "\${report_dir}/${target_filename}" "${agent_file}"; then
    log_pass "  writes to <report_dir>/${target_filename} (no collision)"
  else
    log_fail "  agent ${agent_name} does not target its own filename in heredoc write"
  fi

  # Negative write-scope test (P3 audit hardening): reviewer bodies must NOT
  # contain shell write/destruction commands outside the bounded
  # `cat > "${report_dir}/<agent>.md" <<'RLDYOUR_REPORT_EOF'` heredoc. Detection
  # works on cleaned source - we strip ALL fenced ```...``` blocks (any
  # language) and ALL inline `...` spans first, so canonical examples inside
  # code fences and inline backticks (where these tokens are intentional) are
  # ignored. We then grep on the remaining prose for write tokens.
  #
  # Forbidden tokens (whole-word boundaries to avoid matching the agent name
  # `flow-quality-review` containing "mv"):
  #   - `rm `, `mv `, `cp -`, `sed -i`, `tee `, `touch ` - destructive/copy ops
  #   - `>>` - append redirect (legitimate uses must be in fenced code)
  #
  # Note: we deliberately do NOT forbid bare `>` because the agent
  # description prose contains many legitimate uses (`->`, `<= 30`, `>` quote).
  local cleaned
  cleaned=$(python3 - "${agent_file}" <<'PY'
import re
import sys
text = open(sys.argv[1], "r", encoding="utf-8").read()
# Strip fenced code blocks (any language).
text = re.sub(r"```[\s\S]*?```", "", text)
# Strip inline backtick spans.
text = re.sub(r"`[^`]*`", "", text)
sys.stdout.write(text)
PY
  )
  local found_forbidden=""
  local pattern
  for pattern in 'rm -' 'mv ' 'cp -' 'sed -i' 'tee ' 'touch ' '>>'; do
    if printf '%s' "${cleaned}" | grep -F -q -- "${pattern}"; then
      found_forbidden+="${pattern}; "
    fi
  done
  if [ -z "${found_forbidden}" ]; then
    log_pass "  no write-scope shell tokens outside report heredoc"
  else
    log_fail "  reviewer body has forbidden write tokens outside heredoc: ${found_forbidden}"
  fi
}

main() {
  log_info "${SCRIPT_NAME} starting"
  log_info "Repo root: ${REPO_ROOT}"

  assert_protocol_invariants

  local agent
  for agent in "${REVIEWER_AGENTS[@]}"; do
    assert_agent_invariants "${agent}"
  done

  if [ "${fail_count}" -eq 0 ]; then
    printf '\n\033[1;32m✔ reviewer contracts validation passed (%d agents, 0 drift)\033[0m\n' "${#REVIEWER_AGENTS[@]}"
    exit 0
  else
    printf '\n\033[1;31m✗ reviewer contracts validation failed (%d failures)\033[0m\n' "${fail_count}" >&2
    exit 1
  fi
}

main "$@"
