---
name: ry-rules-review
description: "Аудит реализации против rldyour rules. Используй для: /ry-rules-review, проверь по правилам, аудит правил, hard rules review, качество по правилам, rules audit."
disable-model-invocation: true
---

# ry-rules-review

## Purpose

Review a diff, PR, branch, file scope, or implementation against `rldyour-rules`.

## Workflow

1. Determine target: current diff, branch vs `main`, PR, file scope, or user-provided scope.
2. Use Serena-first code inspection for affected symbols and integration paths (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`).
3. Apply rule skills:
   - `quality-first-engineering` — hard bans, semantic entropy, scope policy.
   - `architecture-boundaries` — FSD/VSA/Hexagonal placement, ADR triggers.
   - `implementation-discipline` — integration sync, reuse, error handling.
   - `dependency-compatibility-policy` — compatibility, supply chain, lockfile discipline.
   - `verification-quality-gates` — required checks per change type.
   - `project-instructions-policy` — AGENTS.md/.claude/CLAUDE.md/REVIEW.md/ADR durability.
4. Use `rldyour-explore` (`tech-research`, `web-research`) when the review depends on current technology behavior, dependency versions, or architecture best practices.
5. Report findings in Russian, ordered by severity and confidence.
6. Default mode is report-only. Modify files only if the user explicitly asks to fix findings.

## Finding Format

- Severity: `critical`, `high`, `medium`, `low`.
- Confidence: `0-100`.
- Location: exact file and line when possible.
- Rule: which rldyour rule is violated.
- Evidence: concrete code, config, test, or docs evidence.
- Impact: what becomes incorrect, fragile, unscalable, insecure, or harder to maintain.
- Fix: actionable correction.
- Disposition: `must-fix`, `should-fix`, `ask-user`, or `defer`.

Drop confidence <30. Validate confidence 30-49 against extra evidence before reporting.

Read `${CLAUDE_PLUGIN_ROOT}/references/rules-policy.md` first; load other references only when they match the reviewed issue.

## Anti-patterns

- Report-only violation: edit files без user'ского explicit fix request.
- Report personal preferences as rule violations.
- Confidence <30 как finding (drop его).
- Skip Serena-first symbol mapping для changed code.
- Generic "improve code" findings без exact path/line/rule citation.
