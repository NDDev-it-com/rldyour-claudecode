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
2. Read `.serena/.flow_post_task_state.json` if present and run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/flow_post_task_state.py`. Inspect `branch_cleanup_state` and run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/git_sync_audit.sh` when branch/worktree cleanup is not obviously complete.
3. Inspect uncommitted changes deeply. Separate source changes, docs, Serena knowledge, generated junk, runtime markers, and secrets.
4. Run `instruction-docs-sync` when durable project instructions may have changed. Keep `AGENTS.md` as the concise root project-instruction file and `.claude/CLAUDE.md` as the Claude Code-native deep project memory in fullrepo-managed projects.
5. Run applicable quality checks from project scripts and `bash ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_checks.sh`.
6. Commit atomically with Conventional Commits. Use separate commits for
   implementation, tests/validators, docs/instructions, license/metadata,
   generated artifacts, and Serena/fullrepo sync when that improves history
   clarity or reviewability.
7. Push to upstream when configured. If no upstream exists, ask before creating one.
8. Keep normal branch history clean from agent-only files. Ensure `.git/info/exclude` contains the rldyour fullrepo block and move tracked agent-only files out of the current branch with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --migrate-main` only when the project is ready for that migration.
9. Publish the complete project snapshot to `fullrepo` through `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --publish`. This uses safe `--force-with-lease`, not a blind force push.
10. Remove merged local and remote branches/worktrees only after verifying they are merged into `main` and no open PR depends on them. Leave protected branches such as `main` and `fullrepo`; report any ambiguous branch ownership instead of deleting silently.
11. Remove `.serena/.flow_sync_marker`, `.serena/.flow_post_task_state.json`, and `.serena/.stop_lifecycle_timeout_marker` after successful sync.

## Loop Guard

Do not edit runtime marker files except to remove them after sync. If the Stop hook repeats for the same fingerprint (`stop_hook_active=true` + same SYNC_MARKER content), allow stop instead of forcing new commits.

## Fullrepo Branch

`fullrepo` is the portable AI-context branch. It contains the normal branch tree plus agent-only files such as project `AGENTS.md`, `.claude/CLAUDE.md`, `REVIEW.md`, `.serena` knowledge, `.claude`, `.cursor/rules`, `.agents/skills`, and similar agent workflow files. The main branch should not track those files in normal projects; they should be restored locally from `fullrepo` and ignored through `.git/info/exclude`.

## Anti-patterns

- Duplicate Serena memory sync (Serena owns its own freshness; this skill waits for it).
- Force-push `main` (only `--force-with-lease` on `fullrepo`).
- Commit secrets / runtime markers / browser artifacts / accidental junk.
- Auto-edit runtime marker files except to remove them after success.
- Delete branches without verifying merged state (use branch_cleanup_state from flow_post_task_state.py).
