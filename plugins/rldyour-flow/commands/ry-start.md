---
description: "Запустить полный lifecycle задачи через ry-start: init → research → plan → implement → quality gates → post-task sync; review only when explicitly requested. Run the full SDLC lifecycle from prompt to synchronized state."
argument-hint: <task>
---

Полный lifecycle задачи: **$ARGUMENTS**

This command is the stable front door for the rldyour lifecycle. On Claude Code
`2.1.168+`, route workflow-worthy work to the project workflow command
`ry-start-workflow` when a saved `.claude/workflows/` projection is present.

If `ry-start-workflow` is unavailable, Use the `ry-start` skill for this
request. The skill is the fallback source of truth for workflow phases, quality
gates, explicit-review routing, and post-task sync. Invoking `/ry-start` alone
is not permission for parallel reviewer subagents; run reviewer tracks only when
the user explicitly asks for review, audit, security review, rules review, or
`ry-review`.

Reply in Russian.
