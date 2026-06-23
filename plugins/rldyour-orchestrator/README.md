# rldyour cmux Orchestrator Projection

This directory contains generated native skill projections for rldyour cmux orchestration.

- Source: root `config/cmux-adapter-projections.json`.
- Protocol: root cmux orchestration protocol `3.0.0`.
- Do not edit generated projection files manually.

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

The stable contract uses immutable task envelopes and schema-valid reports. Completion authority is the root schema-valid report; terminal input is only a wake-up channel and never carries task text or write scopes.
