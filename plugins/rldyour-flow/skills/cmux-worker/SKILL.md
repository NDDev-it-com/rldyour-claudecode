---
name: cmux-worker
description: "Описывает worker role внутри macOS cmux orchestrator: scoped work, JSON report, без push/fullrepo/system install/project policy mutation. EN: cmux worker role."
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
