# rldyour-flow

SDLC orchestrator. The biggest plugin in the marketplace — owns slash commands, reviewer subagents, lifecycle hooks, scripts, and references.

## What's inside

- `7` skills: `ry-init`, `ry-start`, `ry-newp`, `ry-review`, `ry-deploy`, `flow-post-task-sync`, `instruction-docs-sync`.
- `5` slash commands: `/rldyour-flow:ry-init`, `/rldyour-flow:ry-start`, `/rldyour-flow:ry-newp`, `/rldyour-flow:ry-review`, `/rldyour-flow:ry-deploy`.
- `6` reviewer subagents (all `model: sonnet`, `effort: high`, `disallowedTools: [Edit, Write, NotebookEdit]`):

  | Agent | maxTurns | color | track |
  |---|---|---|---|
  | `flow-architecture-review` | 36 | blue | boundaries, dependency direction, public API |
  | `flow-quality-review` | 36 | green | correctness, edge cases, lifecycle |
  | `flow-consistency-review` | 36 | purple | naming, style, project conventions |
  | `flow-integration-review` | 36 | orange | cross-module sync, contracts |
  | `flow-verification-review` | 36 | pink | tests, LSP, browser/server evidence |
  | `flow-security-review` | 42 | red | defensive auth/authz/secrets/injection (+6 turns for variant-hunt) |

- `3` hooks: `SessionStart` (state advisory), `PostToolUse:Bash` (commit advice — Conventional Commits, sensitive paths, agent-only paths), `Stop` (post-task-sync gate).
- `7` scripts: `fullrepo_sync.py`, `flow_post_task_state.py`, `instruction_docs_state.py`, `git_sync_audit.sh`, `detect_project_checks.sh`, `deploy_readiness.sh`, `local_git_ai_guard.sh`.
- `7` references: `flow-lifecycle.md`, `init-context-pack.md`, `context-sufficiency-gate.md`, `reviewer-protocol.md`, `post-task-sync.md`, `deploy-contract.md`, `sources.md`.

## Pattern

Stop hooks are **advisory enforcement gates**, not executors. They block Stop with `exit 2` while work remains and emit machine-readable state via `flow_post_task_state.py`. The `flow-post-task-sync` skill is the executor of merge/push/fullrepo-publish/cleanup under model judgement — `ry-start`, `ry-deploy`, and explicit user invocation drive the actual high-blast-radius operations.

## Dependencies

`rldyour-mcps` + `rldyour-serena-mcp` (waits for Serena `is_current=true` before running git/docs/fullrepo state checks).
