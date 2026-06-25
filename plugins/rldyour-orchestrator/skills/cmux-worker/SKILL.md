---
name: cmux-worker
description: "Воркер cmux v3 для Claude Code: cmux worker role, typed task envelope, heartbeat, scoped JSON report, no push/final sync. Используй для: cmux worker, worker report. EN triggers: cmux v3 worker. EN: cmux v3 worker."
---

# cmux-worker

Generated from root `config/cmux-adapter-projections.json`. Do not edit manually.

Use this skill only when Claude Code is assigned as a visible cmux worker terminal. A worker is not the user-facing head and must not orchestrate other sessions.

## Native Adapter Notes

- Claude Code may be a visible head or a visible worker when the root run manifest assigns that role.
- Native Stop hooks must not create another global sync loop in worker mode; the head owns final sync.

## Current Implementation Status

- `typed-task-report-protocol`: `IMPLEMENTED`.
- `live-start-fail-closed`: `IMPLEMENTED`.
- `compact-template`: `IMPLEMENTED`.
- `workspace-group-topology`: `PLANNED`.
- `delegation-command`: `PLANNED`.
- `worktree-scheduler`: `PLANNED`.
- `adapter-native-projections`: `IMPLEMENTED`.
- `stop-finalization-receipt`: `PLANNED`.

Treat `PLANNED` and `NOT_PROVEN` entries as unavailable in production.

## Required Runtime Identity

- `RLDYOUR_EXECUTION_MODE=orchestrator`.
- `RLDYOUR_AGENT_ROLE=worker`.
- `RLDYOUR_WORKER_ID` matches the immutable task assignment.
- `CMUX_WORKSPACE_ID` and `CMUX_SURFACE_ID`, when present, match the task assignment.

## Task Authority

- Task content lives in the root-owned immutable task envelope and task-local instructions file.
- Allowed paths are a JSON array in the task envelope, not shell text.
- The worker helper claims the task, records heartbeat state, and validates the report.
- Completion authority is a schema-valid report at `$(git rev-parse --git-common-dir)/rldyour/cmux/<run-id>/tasks/<task-id>/report.json` with `report_digest`.
- `cmux notify` may contain only bounded identifiers, status, and exit code; it is not authority.

## Worker Duties

1. Accept only the assigned run/task through the worker helper.
2. Work only inside the assigned repository/worktree and scope.
3. Stop and report `blocked` or `not_proven` when scope, identity, or evidence is ambiguous.
4. Record commands and checks in the report.
5. Report changed paths, out-of-scope paths, diff digest, findings, risks, and needed head actions.

## Forbidden Actions

- Do not push, force-push, tag, delete branches, mutate project policy, run system install, or run final sync.
- Do not delegate nested visible workers.
- Do not create hidden or daemon-style orchestration processes.
- Do not treat native subagents, compose jobs, hooks, or background tasks as rldyour cmux workers.
- Do not claim success when the report was not written and validated.
