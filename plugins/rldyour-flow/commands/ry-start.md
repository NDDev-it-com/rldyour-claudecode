---
description: "Запустить полный lifecycle задачи через ry-start: init → research → plan → implement → quality gates → reviewer subagents → post-task sync. Run the full SDLC lifecycle from prompt to reviewed and synchronized state."
argument-hint: <task>
---

Полный lifecycle задачи: **$ARGUMENTS**

Use the `ry-start` skill for this request. The skill body is the single source of truth for workflow, quality gates, reviewer phase, and post-task sync; invoking `/ry-start` is also explicit permission for parallel reviewer subagents.

Reply in Russian.
