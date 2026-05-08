# rldyour-security

Defensive security workflows: implementation guidance + Mythos-style review.

## What's inside

- `2` skills:
  - `owasp-top-10-implementation` — non-blocking OWASP Top 10 2025 secure coding guidance during implementation (auth/authz, secrets, injection, XSS, SSRF, supply chain, crypto, headers, CORS).
  - `ry-sec-review` — defensive review for diff/PR/scope. Hypothesis-driven, variant-aware (searches sibling files for the same root cause once a finding lands), source-to-sink tracing. **`disable-model-invocation: true`** — slash-only, audit operations are deliberate.
- `1` slash command: `/rldyour-security:ry-sec-review`.

## Defensive-only

Never produces weaponized exploits, persistence steps, credential extraction, or destructive commands. Redacts any secrets surfaced during analysis — reports only file path, variable name, and exposure class.

## Coordination

The `flow-security-review` subagent in `rldyour-flow` is the orchestrated security track invoked from `ry-start` / `ry-review` review phase (`maxTurns: 42` — the +6 turns over standard reviewers reserved for variant-hunt sweep). This plugin's `ry-sec-review` skill is the user-facing slash command.

## Dependencies

`rldyour-mcps` (semgrep MCP server lives there).
