---
name: cmux-orchestrator
description: "Оркестратор cmux v3 для Claude Code: macOS cmux orchestrator, multi-agent terminal workflow, видимый head terminal, typed task envelopes, report-authoritative completion. Используй для: cmux orchestrator, делегируй воркерам. EN triggers: cmux v3 head, visible-terminal orchestration. EN: cmux v3 head."
---

# cmux-orchestrator

Generated from root `config/cmux-adapter-projections.json`. Do not edit manually.

Use this skill only when Claude Code is the machine-identified visible head terminal for rldyour macOS cmux orchestrator mode.

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

## Authority

- Root `config/cmux-orchestrator-policy.json` owns the protocol and safety rules.
- Root `config/cmux-task.schema.json` owns immutable task envelopes.
- Root `config/cmux-worker-report.schema.json` owns worker reports.
- Root `config/cmux-implementation-status.json` separates implemented behavior from planned target architecture.
- Runtime state belongs under `$(git rev-parse --git-common-dir)/rldyour/cmux/<run-id>/`.
- Worker completion authority is `$(git rev-parse --git-common-dir)/rldyour/cmux/<run-id>/tasks/<task-id>/report.json` with a valid digest; notifications are UI hints only.

## Head Duties

1. Verify exactly one visible head terminal is active for the run.
2. Use `ry-cmux start` only through the root implementation; live starts must fail closed when caller workspace, surface, socket, or doctor evidence is missing.
3. Create immutable task envelopes and task-local instructions; never put task text into cmux terminal input.
4. Wake workers with a bounded helper command containing only run/task identifiers.
5. Collect schema-valid worker reports, verify task/attempt/worker/scope binding, then integrate changes as the head.
6. Own final validation, commits, push, fullrepo publication, Serena sync, and owner-facing summary.

## Forbidden Delegation Patterns

- Do not send arbitrary task prose through cmux input.
- Do not pass write scopes through shell environment snippets.
- Do not treat `read-screen`, event streams, or notifications as completion authority.
- Do not let workers push, publish fullrepo, mutate project policy, run system install, delete branches, or run final sync.
- Do not claim Workspace Groups, isolated worktree scheduling, retry materialization, or durable Stop receipts unless the status registry marks them `IMPLEMENTED`.

## Worker Wake-Up Shape

The only terminal input sent to a worker is a helper wake-up command with safe identifiers. The task envelope and instructions file remain on disk and are validated by the worker helper before work starts.
