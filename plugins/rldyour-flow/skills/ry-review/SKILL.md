---
name: ry-review
description: "Отчётное (report-only) глубокое ревью diff/PR/scope с reviewer tracks. Используй для: /rldyour-flow:ry-review, проверь реализацию, сделай ревью, найди проблемы, инспекция кода, проанализируй diff. EN triggers: review diff, review PR, code review, audit changes, find issues, deep review, report-only review, multi-track review."
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

## Output Transport

Reviewer subagents follow the file-first output contract in `${CLAUDE_PLUGIN_ROOT}/references/reviewer-protocol.md` (section "Output Transport"). The orchestrator (this skill body, executed by the main session model) coordinates the wave:

1. **Generate one `run_id` per review wave** in the form `<UTC ISO compact>-<git short sha>`. Example: `2026-05-16T18Z-91cc276`. Use the same `run_id` for all reviewers in the wave.
2. **Compute `report_dir = .serena/reviews/<run_id>/`** (relative to repo root, gitignored runtime artefact).
3. **Inject `run_id` and `report_dir` into every reviewer prompt** alongside scope, diff, constraints, expected reviewer-protocol citation, and read-only reminder.
4. **After all reviewers complete**, read each compact summary from the agent result. Aggregate counts across tracks.
5. **Read per-reviewer report files via `Read`** for findings that require full evidence — critical/high first, medium on demand. Avoid reading all 6 reports for trivial cases.
6. **Resolve contradictions** between reviewer tracks against code evidence.
7. **Write a consolidated `<report_dir>/_summary.md`** with cross-track findings, severity ranking, and disposition (must-fix / should-fix / defer / false-positive).
8. **Report in Russian** with exact paths, impact, suggested fixes, and disposition. Report-only mode by default: edit files only when the user explicitly asks after seeing findings.

Rationale: Claude Code 2.0.77+ has a confirmed `task.output` regression (Anthropic issues `#16789`, `#20531`, `#23463`, all closed as "not planned") that can deliver 200-500 KB of JSONL transcript per subagent to the parent session and overflow the parent context. Capping each reviewer at a 4 KB summary while keeping full evidence on disk prevents that failure mode.

## Anti-patterns

- Edit files в default mode без user'ского explicit ask после findings.
- Reporting confidence <30 без validation.
- Run reviewer agents implicitly (без ry-start или ry-review trigger) — ломает orchestration intent.
- Skip Serena symbol/reference mapping для changed code.
- Dispatch reviewer subagents without `run_id` / `report_dir` in the prompt — reviewers fall back to defaults, but explicit values keep wave artefacts consistent and inspectable.
- Return long-form findings from a reviewer inline instead of via the report file — triggers the Claude Code 2.0.77+ task.output truncation regression.
