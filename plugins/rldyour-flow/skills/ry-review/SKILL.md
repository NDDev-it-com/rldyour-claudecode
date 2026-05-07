---
name: ry-review
description: "Report-only глубокое ревью diff/PR/scope с reviewer tracks. Используй для: /ry-review, проверь реализацию, сделай ревью, найди проблемы, audit diff, code review, инспекция кода."
---

# ry-review

## Purpose

Find real issues before merge or deploy. Default mode is report-only: do not edit files unless the user explicitly asks after seeing findings.

## Workflow

1. Determine review target: current diff, branch vs main, PR, file scope, or prompt scope.
2. Initialize missing context with `ry-init` if needed.
3. Use Serena to map changed symbols and affected integration graph (`get_symbols_overview`, targeted `find_symbol`, `find_referencing_symbols`).
4. Use `rldyour-explore` for current implementation best practices when the review depends on external technology behavior.
5. Run reviewer tracks. Use parallel subagents when the review request or `ry-start` review phase calls for parallel review.
6. Consolidate findings by severity and confidence. Validate uncertain findings with code evidence.
7. Output Russian report with exact paths, impact, suggested fixes, and whether each finding is must-fix.

## Reviewer Tracks

Read `${CLAUDE_PLUGIN_ROOT}/references/reviewer-protocol.md`. These tracks are orchestrated by `ry-review` or `ry-start`; they are not broad implicit-entry skills.

- `flow-architecture-review` — boundary, dependency, module shape, data flow.
- `flow-quality-review` — correctness, edge cases, error handling, hacks, tech debt.
- `flow-consistency-review` — naming, style, imports, public APIs.
- `flow-integration-review` — contracts, schemas, configs, generated types, migrations.
- `flow-verification-review` — tests, quality gates, browser/server evidence.
- `flow-security-review` — auth, secrets, OWASP, injection, SSRF/XSS — when sensitive or requested.

## Anti-patterns

- Edit files в default mode без user'ского explicit ask после findings.
- Reporting confidence <30 без validation.
- Run reviewer agents implicitly (без ry-start или ry-review trigger) — ломает orchestration intent.
- Skip Serena symbol/reference mapping для changed code.
