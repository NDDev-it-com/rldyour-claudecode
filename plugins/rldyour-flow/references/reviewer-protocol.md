# Reviewer Protocol

Reviewer tracks are designed to run as parallel subagents when `ry-start` or `ry-review` explicitly invokes the review phase. They live as `agents/flow-*-review.md` (not skills) per Claude Code May-2026 best practice for orchestrated-only review tracks.

## Subagent Permission

The user explicitly approved subagent usage when invoking `/ry-start` or `/ry-review`. Each spawned subagent must receive a self-contained prompt with task, scope, diff, constraints, expected output, and read-only status.

## Tracks

| Track | Agent | Focus |
| --- | --- | --- |
| Architecture | `flow-architecture-review` | boundaries, dependencies, module shape, data flow |
| Quality | `flow-quality-review` | correctness, hacks, tech debt, edge cases, error handling |
| Consistency | `flow-consistency-review` | conventions, naming, style, file placement, public API shape |
| Integration | `flow-integration-review` | cross-module synchronization, contracts, migrations, configs |
| Verification | `flow-verification-review` | tests, manual checks, browser/server evidence, quality gates |
| Security | `flow-security-review` | security-sensitive paths, OWASP, secrets, auth/authz, unsafe flows |

## Finding Format

Each finding must include:

- Severity: `critical`, `high`, `medium`, `low`.
- Confidence: `0-100`.
- Location: file and line when possible.
- Evidence: concrete code or behavior.
- Impact: what fails or becomes harder.
- Fix: actionable correction.
- Disposition: `must-fix`, `should-fix`, `defer`, or `false-positive`.

Do not report confidence below 30. Validate confidence 30-49 in the parent workflow before acting.

## Parent Integration

The parent workflow (`ry-start` or `ry-review`) consolidates all findings, resolves contradictions with code evidence, fixes accepted findings, then reruns only the reviewer tracks that found problems.

## Why agents, not skills

As of May 2026, `disable-model-invocation: true` on plugin skills has known limitations (cannot be invoked by user via slash command either when installed in a plugin — issue #26251). The canonical pattern from `anthropics/claude-plugins-official/plugins/pr-review-toolkit` is reviewer **agents**, not skills. Reviewer agents have:

- Short orchestration-focused descriptions (no "use when..." trigger phrases) to discourage implicit invocation.
- `tools: [Read, Grep, Glob, Bash, mcp__plugin_rldyour-mcps_serena__*, mcp__plugin_rldyour-mcps_context7__*, mcp__plugin_rldyour-mcps_deepwiki__*, mcp__plugin_rldyour-mcps_grep__*]` explicit allowlist to enforce read-only review with future-proof safety. `flow-security-review` adds `WebFetch`, `WebSearch`, and `mcp__plugin_rldyour-mcps_semgrep__*` for CVE lookups and SAST. Pattern follows canonical `anthropics/claude-plugins-official/plugins/pr-review-toolkit/agents/code-reviewer` (explicit allowlist), not the older `disallowedTools` denylist — explicit positive intent is stronger than denying a finite list.
- `model: sonnet` for cost-efficiency on read-only inspection work.
- `effort: high` (uniform across all 6 tracks).
- `maxTurns: 36` for all tracks; `42` for `flow-security-review` (extra +6 turns reserved for variant-hunt sweep — searching sibling files and repeated helpers for the same root cause once an issue is found). Generous limits compensate for MCP-rich toolsets (Serena + Context7 + DeepWiki + Grep) consuming turns on tool plumbing — tight 12-14 caps left only 4-7 effective reasoning turns. When adding a new reviewer track, default to `maxTurns: 36` unless the track requires variant-hunting beyond the single finding.
- Distinct `color` per track for visual differentiation in the task list:
  - `flow-architecture-review`: `blue`
  - `flow-quality-review`: `green`
  - `flow-consistency-review`: `purple`
  - `flow-integration-review`: `orange`
  - `flow-verification-review`: `pink`
  - `flow-security-review`: `red`

Orchestrators (`ry-start`, `ry-review`) invoke them via prose body delegation in their workflow steps.
