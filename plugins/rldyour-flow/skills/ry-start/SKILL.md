---
name: ry-start
description: "Полный lifecycle задачи: init→research→plan→implement→quality gates→reviewer subagents→post-task sync. Используй для: /rldyour-flow:ry-start, реализуй, доработай, исправь качественно, сделай задачу, реализуй фичу. EN triggers: full SDLC, end-to-end task, ship feature, implement task, complete a task, build feature, run full lifecycle."
argument-hint: "<task description>"
---

# ry-start

## Purpose

Implement a task to a high-quality, scalable, synchronized state. Speed is secondary to correctness, consistency, maintainability, and clean git history.

## Workflow

1. If context is missing, run a scoped `ry-init` automatically.
2. Understand the prompt. For ambiguity, ask concise Russian questions with options.
3. Research code through Serena memories and semantic tools.
4. Research current docs, patterns, and alternatives through `rldyour-explore`.
5. Read `${CLAUDE_PLUGIN_ROOT}/references/context-sufficiency-gate.md` and pass the gate before editing code.
6. Write a detailed plan. Verify each plan item against code using Serena before editing.
7. Create or use a feature branch/worktree. Use stacked PRs only when the task naturally splits into independent logical PRs.
8. Implement strictly by plan, adapting only after code evidence. Make frequent atomic Conventional Commits.
9. Provide progress checkpoints after meaningful milestones or every 2-3 completed plan groups.
10. Fix all issues in touched scope plus affected integration path. If wider technical debt is found, ask whether to expand scope.
11. Run quality gates using project scripts, `rldyour-lsps`, and detected stack checks.
12. Trigger browser validation for UI/browser-visible work unless auth blocks it; if auth blocks, report the limitation and use available evidence.
13. Trigger security review for security-sensitive changes or explicit user request.
14. Run review phase with reviewer subagents (`flow-architecture-review`, `flow-quality-review`, `flow-consistency-review`, `flow-integration-review`, `flow-verification-review`, `flow-security-review`) when applicable.
15. Run `flow-post-task-sync` before final response.

## Automatic Helper Routing

The user normally invokes only `rldyour-flow` commands and writes prompts in Russian. `ry-start` must route helper skills automatically instead of waiting for explicit helper skill names:

- Repository/code scope: use `serena-code-workflow`, `lsp-routing`, `quality-first-engineering`, and `implementation-discipline` for изучи код, посмотри проект, реализуй, доработай, исправь, рефакторинг, ревью, архитектура, файлы, директории, symbols, or implementation scope.
- Internet or best-practice research: for technical prompts such as исследуй интернет, изучи в интернете, посмотри документацию, best practices, migration, API behavior, framework/library setup, or MCP/tool sources, use `tech-research` first with Context7, DeepWiki, and Grep by Vercel. Add `web-research` when the prompt asks for internet/current/latest/source-backed information or when sources beyond the three MCPs are needed.
- Browser-visible work: use `browser-tool-routing` and `browser-validation` for проверь в браузере, визуально, UI, адаптив, скриншот, pixel-perfect, user flow, or business-logic checks. Use `browser-debug` for console, network, runtime, layout, hydration, Lighthouse, performance, and browser-only failures.
- Design/frontend UI work: use `ry-design`, `figma-to-code`, `design-system-implementation`, `fsd-frontend-architecture`, and `design-validation` when the task mentions Figma, дизайн, UI, верстка, дизайн-система, shadcn/ui, ReactBits, FSD, tokens, or pixel-perfect design.
- Security-sensitive work: use `owasp-top-10-implementation` during auth/authz/API/input/file/dependency/config/secrets/payment/admin/external-integration work. Use `ry-sec-review` for explicit security-review requests and orchestrate `flow-security-review` in the review phase when the touched scope is sensitive.
- Verification and finish: use `verification-quality-gates`, `flow-verification-review`, `serena-memory-sync`, and `flow-post-task-sync` before final delivery when the task produced durable code, config, docs, plugin, memory, hook, or workflow changes.

## Context Sufficiency

Do not implement from a shallow prompt. Before editing, the model must know the relevant architecture, files, symbols, DB/schema/API/config contracts, tests, integration paths, current project patterns, and current external API/framework guidance needed for the task.

If the model cannot answer the gate questions in `${CLAUDE_PLUGIN_ROOT}/references/context-sufficiency-gate.md`, it must gather more evidence through Serena, LSP, `rldyour-explore`, browser/security/design workflows, or ask the user with options. This is a quality guard, not a hard blocker: the correct response is to enrich context until implementation is safe.

## Subagent Permission

Invoking `ry-start` is the user's explicit permission to use parallel reviewer subagents during the review phase. Reviewer agents (`flow-architecture-review`, `flow-quality-review`, `flow-consistency-review`, `flow-integration-review`, `flow-verification-review`, `flow-security-review`) are orchestrated by this command, not broad implicit-entry skills. Prompts must be self-contained and read-only for reviewers.

## Review Phase Output Transport

Reviewer subagents follow the file-first output contract in `${CLAUDE_PLUGIN_ROOT}/references/reviewer-protocol.md` (section "Output Transport"). The orchestrator (this skill body, executed by the main session model) is responsible for the run-level coordination:

1. **Generate one `run_id` per review wave** in the form `<UTC-ISO-compact>-<git-short-sha>`. Example: `2026-05-16T1433Z-91cc276` (minute-precision timestamp prevents collisions when two waves run in the same hour). Use the same `run_id` for all reviewers in the wave so their reports land in the same directory.
2. **Compute `report_dir = .serena/reviews/<run_id>/`** (relative to repo root). `.serena/reviews/` is gitignored by repo policy and treated as runtime artefact (`.serena/cache/`, `.serena/diagnostics/` follow the same pattern). Create it once with `mkdir -p` before dispatching reviewers, or let the first reviewer create it - both are safe because `mkdir -p` is idempotent.
3. **Inject `run_id` and `report_dir` into every reviewer prompt**, alongside scope, diff, constraints, expected reviewer-protocol citation, and read-only reminder. Without these fields each reviewer derives safe defaults, but explicit values keep the wave consistent.
4. **After all reviewers complete**, read each compact summary from the agent result. Aggregate `Counts:` across tracks. Identify the critical/high findings that need synthesis.
5. **Must read each per-reviewer report file via `Read`** for every `critical` and `high` finding before deciding disposition; `flow-security-review` carries `Category` (OWASP/ASVS), `Attack path`, and `Verification` fields that exist only in the report file. Medium and low findings may be read on demand when consolidation requires deeper evidence; reports without any findings can be skipped.
6. **Resolve contradictions** between reviewer tracks against code evidence (Serena `find_symbol`, `find_referencing_symbols`).
7. **Write a consolidated `<report_dir>/_summary.md`** with cross-track findings, plan disposition (must-fix / should-fix / defer / false-positive), and the chosen fix order. Required whenever any track reported one or more findings. This file is the durable wave artefact - useful for the user to inspect and for `flow-post-task-sync` to reference.
8. **Report back to the user in Russian**. List the report-file paths so the user can inspect full findings on disk. Quote no more than the top critical/high entries inline; everything else stays in the files.

Rationale: Claude Code 2.0.77+ has a confirmed `task.output` regression (Anthropic issues [`#16789`](https://github.com/anthropics/claude-code/issues/16789), [`#20531`](https://github.com/anthropics/claude-code/issues/20531), [`#23463`](https://github.com/anthropics/claude-code/issues/23463), all closed as "not planned") that can deliver up to 200-500 KB of JSONL transcript per subagent to the parent session, with combined subagent results capable of overflowing the parent context and crashing the session. Capping each reviewer at a 4 KB summary while preserving full evidence on disk structurally prevents that failure mode.

## Non-Negotiables

- No hacks, temporary workarounds, or untracked debt in touched scope.
- No fake green checks. If a check cannot run, say why.
- No silent destructive git actions. Branch/worktree cleanup requires verified merged state.
- No secrets in commits, logs, docs, memories, or prompts.

## Anti-patterns

- Implement без passing context-sufficiency gate.
- Skip reviewer phase для security-sensitive или user-visible changes.
- Skip browser validation для UI changes без явного auth-blocker reasoning.
- Force-push продуктовых веток.
- Commit без Conventional Commits format.
- Final delivery без `flow-post-task-sync`.
