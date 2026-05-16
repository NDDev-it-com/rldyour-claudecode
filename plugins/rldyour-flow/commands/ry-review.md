---
description: "Сделать report-only глубокое ревью через ry-review с reviewer tracks (architecture/quality/consistency/integration/verification/security). Run a report-only deep review with parallel reviewer tracks."
argument-hint: <scope>
---

Report-only глубокое ревью для: **$ARGUMENTS**

Use the `ry-review` skill to find real issues before merge or deploy. Default mode is **report-only** - no file edits unless the user explicitly asks after seeing findings.

The skill enforces:

1. Determine review target: current diff, branch vs main, PR, file scope, or prompt scope.
2. Initialize missing context with `ry-init` if needed.
3. Use Serena to map changed symbols and the affected integration graph.
4. `rldyour-explore` for current implementation best practices when external technology behavior matters.
5. **Reviewer tracks** (parallel subagents per `${CLAUDE_PLUGIN_ROOT}/references/reviewer-protocol.md`):
   - `flow-architecture-review` - boundary, dependency, module shape, data flow.
   - `flow-quality-review` - correctness, edge cases, error handling, hacks, tech debt.
   - `flow-consistency-review` - naming, style, imports, public APIs.
   - `flow-integration-review` - contracts, schemas, configs, generated types.
   - `flow-verification-review` - tests, quality gates, browser/server evidence.
   - `flow-security-review` - auth, secrets, OWASP, injection - when sensitive or requested.
6. Consolidate findings by severity and confidence. Validate uncertain findings (confidence 30-49) with code evidence. Drop confidence <30.
7. Russian report: exact paths, impact, suggested fixes, must-fix flag per finding.

Reply in Russian.
