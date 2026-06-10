---
name: cmux-worker
description: "Роль worker внутри macOS cmux orchestrator: scoped-задача в выделенном скоупе, JSON-отчёт плюс обязательный notify-сигнал с exit-кодом, без push/fullrepo/system install/policy mutation. Используй для: cmux worker, воркер-задача, scoped report, выполнение делегата. EN triggers: cmux worker role, scoped worker task, worker JSON report."
---

# cmux-worker

Use this skill only inside a cmux orchestrator session with `RLDYOUR_EXECUTION_MODE=orchestrator` and `RLDYOUR_AGENT_ROLE=worker`.

Worker rules:

- Work only inside the assigned file/directory scope.
- Do not talk to the user as the primary respondent.
- Do not push, force-push, delete branches, publish fullrepo, install system configs, mutate project policy, or run final flow sync.
- Do not commit unless explicitly delegated by the orchestrator.
- Return a JSON report with `status`, `files_changed`, `commands_run`, `findings`, `risks`, and `needs_orchestrator_action`.

Runtime worker report files belong under `.serena/cache/cmux-orchestrator/<workspace-id>/<task-id>.json` and must not be committed.

Completion signal: the orchestrator exports `RLDYOUR_TASK_ID` and
`RLDYOUR_WORKER_ALLOWED_PATHS` at delegation time (empty allowed-paths means no
delegated write scope). Finish every task with both signals: the JSON report and
`cmux notify --title "worker ${RLDYOUR_WORKER_ID}" --body "task ${RLDYOUR_TASK_ID} exit <code>"`
with the real exit code, because cmux emits no per-command exit-code event.
