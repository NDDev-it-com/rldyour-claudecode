---
name: quality-first-engineering
description: "Качественно-первый подход: чистый код, масштабируемость, консистентность, без хаков и скрытого техдолга. Используй для: качество кода, чистый код, костыли, техдолг, масштабируемость, жесткие запреты. EN triggers: code quality, clean code, no hacks, no tech debt, scalable code, consistent code, hard bans, quality-first engineering."
---

# Quality-First Engineering

## Purpose

Apply the user's default engineering standard: correctness, clean architecture, long-term scalability, low semantic entropy, and consistency over speed.

User-facing conversation stays Russian unless requested otherwise. Repository documentation, code comments, commit messages, Serena memories, plans, and research archive files are written in English.

## Core Rules

- Code is the source of truth. Verify rules, memories, docs, and plans against actual code, diffs, tests, and runtime evidence.
- Quality has priority over delivery speed. Do not choose a shortcut just because it is faster.
- Use Sequential Thinking MCP (`mcp__sequential-thinking__*`) for non-trivial decisions when available, with at least 3 thoughts before committing to an approach.
- Prefer consistency with existing project patterns. If existing patterns are harmful, explain the risk and ask before widening scope.
- Keep semantic entropy low: one concept should have one clear home, one naming style, one contract, and one implementation pattern unless there is a documented reason.
- Reuse stable code where it already exists. Extract reusable code only after real repeated need is clear.
- Optimize for future change without speculative over-engineering.

## Hard Bans

- No hacks, temporary workarounds, fake implementations, or knowingly deferred debt in the touched scope.
- No swallowed errors. Handle errors at boundaries with meaningful typed or structured messages.
- No secrets, tokens, cookies, private keys, or credentials in code, docs, memories, logs, prompts, screenshots, or commits.
- No fake checks. Never claim tests, lint, type checks, browser checks, security checks, or deploy checks passed unless they were actually run or evidence was collected.
- No unrelated destructive git or filesystem operations.

## Scope Policy

Fix quality issues inside the touched scope and affected integration path. If serious technical debt is found outside scope, stop expanding and ask the user in Russian with 2-3 concrete options.

## Conventional Commits

Use [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — stable as of May 2026. Eleven canonical types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. Subject ≤72 chars. Scope optional in parentheses. Use `!` after type/scope or `BREAKING CHANGE:` footer for breaking changes.

Read `${CLAUDE_PLUGIN_ROOT}/references/rules-policy.md` when a task requires the full policy.

## Anti-patterns

- Hacks / temporary workarounds в touched scope (нарушает hard ban).
- Swallowed errors / generic exception traps без meaningful messages.
- Fake green checks (claim что test passed без запуска).
- Secrets в commits/logs/docs/memories — non-negotiable.
- Speculative абстракции для одного hypothetical future case.
