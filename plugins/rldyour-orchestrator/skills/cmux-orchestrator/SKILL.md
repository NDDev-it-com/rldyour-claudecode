---
name: cmux-orchestrator
description: "Оркестратор cmux на macOS: один user-facing терминал делегирует задачи worker-терминалам, собирает JSON-отчёты с notify-сигналом завершения и владеет финальной валидацией и синком. Используй для: cmux orchestrator, оркестрация терминалов, делегируй воркерам, multi-agent terminal workflow. EN triggers: cmux orchestrator, multi-agent terminal workflow, delegate workers, collect worker reports."
---

# cmux-orchestrator

Use this skill only when project policy enables `execution.mode = "orchestrator"` and `cmux.enabled = true` on macOS. Linux, WSL, and Windows remain in `standard` mode.

The orchestrator talks to the user, reads project policy, creates bounded worker tasks, collects JSON worker reports, reviews diffs, runs final validation, and owns commits/push/fullrepo/Serena sync when policy allows those actions.

Workers must receive explicit file/command scope and must not push, delete branches, publish fullrepo, install system configs, mutate project policy, run final sync, or commit unless delegated for the task ID.

Stable cmux setup uses project-local `.cmux/cmux.json` `commands` and workspace layout. Do not rely on nightly-only `actions` for the required path.

Delegation mechanics: send each task into the worker surface with per-task scope
(`cmux send --surface <surface-id> "export RLDYOUR_TASK_ID=<task-id> RLDYOUR_WORKER_ALLOWED_PATHS=<colon-separated-paths>; <task instruction>\n"`),
observe workers with `cmux read-screen --workspace <workspace-id> --surface <surface-id> --scrollback --lines <n>`
or `cmux events --cursor-file <file> --reconnect`, and treat a task as finished only after both
completion signals: the JSON report and the worker's
`cmux notify --title "worker <worker-id>" --body "task <task-id> exit <code>"`.
cmux emits no per-command exit-code event on its own.
