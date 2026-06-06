---
name: flow-post-task-sync
description: "Финализация задачи: Serena memories, agent-only files, fullrepo, git/GitHub, branches, worktrees. Используй после ry-start/review/deploy/newp. Используй для: заверши задачу, синхронизируй, финализируй, обнови git и docs, очисти ветки. EN triggers: post-task sync, Stop hook advisory, fullrepo publish, ff-merge to main, branch cleanup, finalize task, end-of-task sync."
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

# Flow Post-Task Sync

## Purpose

Leave the project in a synchronized, documented, committed state. This skill runs after Serena memory sync, not instead of it.

## Workflow

1. Confirm Serena memories are current via `python3 "$(git rev-parse --show-toplevel)"/plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` (use `git rev-parse --show-toplevel` rather than `${CLAUDE_PLUGIN_ROOT}` because the script lives in a different plugin; `${CLAUDE_PROJECT_DIR}` is documented only for hook commands and stdio MCP env, not skill execution context). If `is_current=false`, **invoke the `rldyour-serena-mcp:flow-memory-sync` subagent** through the Agent tool - pass HEAD SHA, newest synced SHA, and the changed-files list as `prompt` context. The subagent has narrow tool access (Serena memory tools + read-only Bash/Read/Grep/Glob; Edit/Write/NotebookEdit are disallowed in its frontmatter), enforces fact-only updates, runs `commit_serena_knowledge.sh` itself, and emits a JSON report. Do **not** edit `.serena/memories/*.md` from the main session - keep all memory mutations in the dedicated subagent so anti-hallucination guards apply.
2. If `flow_post_task_state.py` reports `execution.agent_role=worker`, do not run global sync. Return the worker JSON report to the orchestrator. Workers must not publish fullrepo, delete branches, push, install system configs, mutate project policy, or run final sync unless the orchestrator explicitly delegated that exact action.
3. Read `.serena/.flow_post_task_state.json` if present and run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/flow_post_task_state.py`. Inspect `branch_cleanup_state` and run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/git_sync_audit.sh` when branch/worktree cleanup is not obviously complete.
4. Inspect uncommitted changes deeply. Separate source changes, docs, Serena knowledge, generated junk, runtime markers, and secrets.
5. Run `instruction-docs-sync` when durable project instructions may have changed and `project_flow_policy.py` reports `instruction_docs.mode` is not `disabled`. Keep `AGENTS.md` as the concise root project-instruction file and `.claude/CLAUDE.md` as the Claude Code-native deep project memory according to policy.
6. Run applicable quality checks from project scripts and `bash ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_checks.sh`.
7. Commit atomically with Conventional Commits. Use separate commits for
   implementation, tests/validators, docs/instructions, license/metadata,
   generated artifacts, and Serena/fullrepo sync when that improves history
   clarity or reviewability.
8. Push to upstream when configured. If no upstream exists, ask before creating one.
9. Follow the effective `.rldyour/project-policy.json` / local / env policy before touching fullrepo or agent files. In `fullrepo.mode=disabled`, do not restore, migrate, publish, create, or install fullrepo excludes. In `normal_branch_policy.agent_files=allowed`, tracked AI instruction files are normal project files.
10. Publish `fullrepo` only when policy requires/allows it through `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --publish`. Missing fullrepo creation requires explicit policy (`create_if_missing=true`) or explicit current user instruction.
11. Remove merged local and remote branches/worktrees only when policy allows cleanup, the branch is not protected (`main`, `dev`, `fullrepo`, etc.), the branch was created for this workflow, and no open PR depends on it. Advisory cleanup is reported, not forced.
12. Remove `.serena/.flow_sync_marker`, `.serena/.flow_post_task_state.json`, `.serena/.flow_blocker_ack.json`, and `.serena/.stop_lifecycle_timeout_marker` only after `flow_post_task_state.py` reports no policy-allowed blocking reasons.

## Loop Guard

Do not edit runtime marker files except to remove them after sync. If the Stop hook repeats for the same fingerprint (`stop_hook_active=true` + same SYNC_MARKER content), allow stop instead of forcing new commits.

## Fullrepo Branch

`fullrepo` is the default portable AI-context branch for rldyour-managed projects. Project policy may set `fullrepo.mode=disabled|advisory|auto|required` and may allow tracked instruction/AI files in normal branches. Runtime markers, caches, local env files, browser artifacts, and secrets remain forbidden in every mode.

## Anti-patterns

- Duplicate Serena memory sync (Serena owns its own freshness; this skill waits for it).
- Force-push `main` (only `--force-with-lease` on `fullrepo`).
- Commit secrets / runtime markers / browser artifacts / accidental junk.
- Auto-edit runtime marker files except to remove them after success.
- Delete branches without verifying merged state (use branch_cleanup_state from flow_post_task_state.py).
