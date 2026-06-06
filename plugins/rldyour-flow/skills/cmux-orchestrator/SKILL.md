---
name: cmux-orchestrator
description: "Запускает macOS cmux orchestrator workflow: один user-facing orchestrator делегирует worker terminals, собирает отчеты, валидирует и синхронизирует. EN: cmux orchestrator, multi-agent terminal workflow."
---

# cmux-orchestrator

Use this skill only when project policy enables `execution.mode = "orchestrator"` and `cmux.enabled = true` on macOS. Linux, WSL, and Windows remain in `standard` mode.

The orchestrator talks to the user, reads project policy, creates bounded worker tasks, collects JSON worker reports, reviews diffs, runs final validation, and owns commits/push/fullrepo/Serena sync when policy allows those actions.

Workers must receive explicit file/command scope and must not push, delete branches, publish fullrepo, install system configs, mutate project policy, run final sync, or commit unless delegated for the task ID.

Stable cmux setup uses project-local `.cmux/cmux.json` `commands` and workspace layout. Do not rely on nightly-only `actions` for the required path.
