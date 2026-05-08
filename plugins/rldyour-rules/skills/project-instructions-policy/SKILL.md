---
name: project-instructions-policy
description: "Политика project-инструкций: AGENTS.md, .claude/CLAUDE.md, REVIEW.md, ADRs (MADR 4.0.0). Используй для: правила проекта, инструкции, документация, ADR, долгоживущая документация. EN triggers: project rules, project instructions, ADR, MADR, write durable docs, update AGENTS.md, update CLAUDE.md, instruction policy."
---

# Project Instructions Policy

## Purpose

Keep durable project instructions useful for future Claude Code sessions without turning them into chat history or generic advice.

## Rules

- Create or update `AGENTS.md` when durable root-level project rules, setup commands, quality gates, architecture constraints, deploy contracts, or workflow guidance change. `AGENTS.md` is the cross-tool standard root project-instruction file (see https://agents.md/).
- Keep `AGENTS.md` concise; it is loaded as a high-signal entry point and instruction size matters.
- Create or update `.claude/CLAUDE.md` for fullrepo-managed projects so Claude Code has first-class project memory.
- Keep `.claude/CLAUDE.md` optimized for Claude Code, not as a thin `@AGENTS.md` import. Reference Claude-specific locations when relevant: `.claude/settings.json`, `.claude/skills/`, `.claude-plugin/`, `/memory`, `/context`, `/hooks`, `/mcp`, `/permissions`, `/doctor`, `/status`.
- Do not create root `CLAUDE.md` by default; `.claude/CLAUDE.md` is the rldyour project memory path.
- Create or update `REVIEW.md` when review-specific rules are durable and materially help future review agents.
- Create ADRs (MADR 4.0.0 format) for important architecture, technology, dependency, deployment, security, or irreversible design decisions.
- Repository docs, instructions, ADRs, memories, plans, comments, and commits are English. User-facing conversation with the user is Russian.
- Do not store secrets, personal tokens, local-only credentials, private cookies, or chat transcripts in docs.

## Agent-Only Files And Fullrepo

In normal product repositories, instruction files (`AGENTS.md`, `.claude/CLAUDE.md`, `REVIEW.md`) are agent-only context. They should be:

- Restored locally from `fullrepo` branch via `python3 ${CLAUDE_PLUGIN_ROOT}/../rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init`.
- Ignored through `.git/info/exclude` (`fullrepo` block installed automatically).
- Published to `fullrepo` branch via `flow-post-task-sync`.
- Never committed to normal product branches (`main`, feature branches).

Repositories that are themselves agent tooling (like `rldyour-claude` itself) may intentionally track selected instruction templates as product files — for example a `system/CLAUDE.md` template that gets installed into user projects.

Read `${CLAUDE_PLUGIN_ROOT}/references/project-instructions-and-adrs.md` before creating or updating durable instruction files.

## Anti-patterns

- Reduce `.claude/CLAUDE.md` к thin `@AGENTS.md` import (нарушает rldyour rule).
- Create root `CLAUDE.md` для new projects (`.claude/CLAUDE.md` — preferred path).
- Commit `AGENTS.md`/`CLAUDE.md`/`REVIEW.md` в нормальные продуктовые ветки (use fullrepo).
- Store secrets / tokens / chat history в instruction docs.
- Skip ADR для irreversible decisions (architecture, framework, DB choice).
- Update instruction docs для mechanical formatting changes (только durable facts).
