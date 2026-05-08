---
description: "Запустить защитный security review через ry-sec-review. Run defensive Mythos-style security review of a diff, PR, or scope."
argument-hint: <scope>
---

Защитный security review для: **$ARGUMENTS**

Use the `ry-sec-review` skill to perform a defensive Mythos-style security review of the specified scope (diff, PR, file, module, or feature).

Workflow the skill enforces:

1. Recon — map changed files, entry points, trust boundaries, data flows. Use Serena first (`get_symbols_overview`, targeted `find_symbol`, `find_referencing_symbols`, `search_for_pattern`) when available.
2. Baseline scan — Semgrep MCP (`mcp__plugin_rldyour-mcps_semgrep__*`) and local security scripts when useful. Never the only evidence.
3. Hypothesize against OWASP Top 10 2025 + ASVS 5.0.0 + project-specific threat boundaries.
4. Trace source-to-sink for high-risk hypotheses; prove or reject with code evidence.
5. Variant hunt — repeated patterns, sibling bugs, copied logic.
6. Rank by severity + confidence; prefer fewer high-confidence findings over broad speculation.
7. Remediate — propose precise fixes, tests, verification commands.
8. Report findings first (severity-ordered), then rejected hypotheses, residual risks, verification, recommended fixes.

Output finding format: Severity, Category, Confidence (0-100), Location (`path:line`), Evidence, Attack path (defensive), Impact, Fix, Verification.

Defensive-only — never produce weaponized exploits, persistence, credential extraction, or destructive commands. Redact any secret values found.

Reply in Russian when the scope is described in Russian.
