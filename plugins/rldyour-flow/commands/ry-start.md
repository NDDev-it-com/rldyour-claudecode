---
description: "Запустить полный lifecycle задачи через ry-start: init→research→plan→implement→quality gates→reviewer subagents→post-task sync."
argument-hint: <task>
---

Полный lifecycle задачи: **$ARGUMENTS**

Use the `ry-start` skill to run the full task lifecycle from prompt to reviewed, synchronized state. Speed is secondary to correctness, consistency, maintainability, and clean git history.

The skill enforces:

1. Scoped `ry-init` if context is missing.
2. Research: Serena memories + `tech-research` (Context7/DeepWiki/Grep) + `web-research` for unclear technology.
3. Pass `${CLAUDE_PLUGIN_ROOT}/references/context-sufficiency-gate.md` before editing.
4. Detailed plan verified against code via Serena.
5. Branch/worktree, atomic Conventional Commits, progress checkpoints every 2-3 plan groups.
6. Quality gates: project scripts + `lsp-routing` + detected stack checks.
7. Trigger workflows by change type: `browser-validation` for UI, `ry-sec-review` for security-sensitive, `ry-design` for design.
8. **Review phase** — parallel reviewer subagents: `flow-architecture-review`, `flow-quality-review`, `flow-consistency-review`, `flow-integration-review`, `flow-verification-review`, `flow-security-review`. Invoking `/ry-start` is the user's explicit permission for parallel reviewers.
9. Final: `flow-post-task-sync` synchronizes Serena memories, agent-only files, AGENTS.md/CLAUDE.md, git, GitHub, fullrepo, branch/worktree cleanup.

Non-negotiables: no hacks, no fake green checks, no silent destructive git actions, no secrets in commits/logs/docs/memories.

Reply in Russian.
