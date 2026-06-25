# rldyour-flow

SDLC orchestrator. The biggest plugin in the marketplace - owns slash commands, reviewer subagents, lifecycle hooks, scripts, and references.

## What's inside

- `7` skills: `ry-init`, `ry-start`, `ry-newp`, `ry-review`, `ry-deploy`, `flow-post-task-sync`, `instruction-docs-sync`.
- `6` slash commands: `/rldyour-flow:ry-init`, `/rldyour-flow:ry-start`, `/rldyour-flow:ry-newp`, `/rldyour-flow:ry-review`, `/rldyour-flow:ry-deploy`, `/rldyour-flow:ry-sync`.
- `6` reviewer subagents (all `model: sonnet`, `effort: high`, explicit `tools:` allowlist with only read-only Serena tools + Read/Grep/Glob/Bash + Context7/DeepWiki/Grep MCPs - no Edit/Write/NotebookEdit, no Serena write tools):

  | Agent | maxTurns | color | track |
  |---|---|---|---|
  | `flow-architecture-review` | 90 | blue | boundaries, dependency direction, public API |
  | `flow-quality-review` | 90 | green | correctness, edge cases, lifecycle |
  | `flow-consistency-review` | 90 | purple | naming, style, project conventions |
  | `flow-integration-review` | 90 | orange | cross-module sync, contracts |
  | `flow-verification-review` | 90 | pink | tests, LSP, browser/server evidence |
  | `flow-security-review` | 100 | red | defensive auth/authz/secrets/injection (+10 turns for variant-hunt) |

- `4` hook events / `6` hook scripts: `SessionStart` (worktree bootstrap + state advisory - two registered scripts), `PreToolUse:Bash` (manual-first CI advisory), `PostToolUse:Bash` (commit advice - Conventional Commits, sensitive paths, agent-only paths), `Stop` (ordered Serena memory gate then post-task-sync gate).
- `7` scripts: `flow_post_task_state.py`, `flow_post_task_state.py`, `instruction_docs_state.py`, `git_sync_audit.sh`, `detect_project_checks.sh`, `deploy_readiness.sh`, `local_git_ai_guard.sh`.
- `7` references: `flow-lifecycle.md`, `init-context-pack.md`, `context-sufficiency-gate.md`, `reviewer-protocol.md`, `post-task-sync.md`, `deploy-contract.md`, `sources.md`.

## Pattern

Stop hooks are **advisory enforcement gates**, not executors. The registered Flow Stop hook is `stop_lifecycle_dispatcher.sh`: it drains Claude stdin, runs Serena memory freshness first, then runs `flow_post_task_state.py` through the Flow gate, with bounded child process timeouts. The `flow-post-task-sync` skill is the executor of merge/push/tracked-context-publish/cleanup under model judgement - `ry-start`, `ry-deploy`, and explicit user invocation drive the actual high-blast-radius operations.

## Dependencies

`rldyour-mcps` + `rldyour-serena-mcp` (waits for Serena `is_current=true` before running git/docs/tracked-context state checks).
