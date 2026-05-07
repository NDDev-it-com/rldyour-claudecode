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
- `disallowedTools: [Edit, Write, NotebookEdit]` to enforce read-only review.
- `model: sonnet` for cost-efficiency on read-only inspection work.
- `effort: medium-high` per track complexity.
- `color: yellow` for visibility in the agent task list.

Orchestrators (`ry-start`, `ry-review`) invoke them via prose body delegation in their workflow steps.
