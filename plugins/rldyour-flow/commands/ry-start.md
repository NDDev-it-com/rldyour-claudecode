---
description: "Запустить полный lifecycle задачи через ry-start: init → research → plan → implement → quality gates → reviewer subagents → post-task sync. Run the full SDLC lifecycle from prompt to reviewed and synchronized state."
argument-hint: <task>
---

Полный lifecycle задачи: **$ARGUMENTS**

This command is the stable front door for the rldyour lifecycle. On Claude Code
`2.1.156+`, route workflow-worthy work to the project workflow command
`ry-start-workflow` when a saved `.claude/workflows/` projection is present.
The official Claude workflow runtime saves reusable workflows through the
interactive `/workflows` view, so do not invent an undocumented workflow file
format from this Markdown command.

If `ry-start-workflow` is unavailable, use the `ry-start skill` for this
request. The skill body is the fallback source of truth for workflow phases,
quality gates, reviewer phase, and post-task sync; invoking `/ry-start` is also
explicit permission for parallel reviewer subagents.

Reply in Russian.
