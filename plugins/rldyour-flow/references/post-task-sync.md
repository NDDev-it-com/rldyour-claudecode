# Post-Task Synchronization

Post-task sync is the last phase of meaningful work. It prevents forgotten changes, stale project knowledge, and mismatched local/GitHub/server state.

## Order

1. Serena memory freshness first.
2. Project instruction docs second: `AGENTS.md` and `.claude/CLAUDE.md`.
3. Quality checks and manual evidence third.
4. Atomic commits fourth.
5. GitHub sync fifth.
6. Fullrepo branch sync sixth.
7. Merged branch/worktree cleanup last.

## Session And Commit Advice

The flow SessionStart hook gives Claude Code a compact repository state packet before work starts or resumes. Treat it as an input to planning: inspect dirty files, ahead/behind state, worktree count, docs, and Serena freshness before making assumptions.

The flow PostToolUse hook emits commit advice after Bash `git commit` commands via `hookSpecificOutput.additionalContext`. Advice is informational and should be reviewed before pushing or final delivery, but it must not be treated as a hard failure by itself.

## Serena Interaction

`rldyour-serena-mcp` owns `.serena/memories`, `.serena/plans`, and `.serena/research`. The flow Stop hook must not duplicate that work. It waits until the Serena state script reports current knowledge (`serena_current=true`), then asks for `flow-post-task-sync`.

In fullrepo-managed projects, Serena knowledge is not committed to normal branches. The Serena commit helper may acknowledge current knowledge and clear runtime sync markers without committing when `.serena` knowledge paths are untracked/ignored. Flow then publishes the complete snapshot to `fullrepo`.

## AGENTS.md And .claude/CLAUDE.md

`AGENTS.md` is the cross-tool root project-instruction file (see https://agents.md/). Update it when the task changes durable project rules, setup commands, quality gates, deploy contracts, architecture constraints, or agent workflow guidance. Keep it concise and practical: repository layout, commands, checks, constraints, tool routing, and done criteria.

Claude Code reads project memory from `.claude/CLAUDE.md` in rldyour fullrepo-managed projects. Create and update it for every such project, optimized for Claude Code rather than as a thin copy of `AGENTS.md`: commands, architecture, workflow, conventions, Claude Code diagnostics, and Claude-specific settings/hooks/skills locations.

Both files must contain verified facts, not chat history or speculative plans.

For normal projects, root `AGENTS.md`, `.claude/CLAUDE.md`, and `REVIEW.md` are agent-only files and should be restored from `fullrepo`, ignored through `.git/info/exclude`, and excluded from normal branch history. Repositories that are themselves agent tooling may intentionally track selected instruction templates as product files (such as `system/CLAUDE.md` if the project ships a Claude Code template).

Use `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/instruction_docs_state.py --json` to decide whether review is needed.

## Fullrepo Branch

`fullrepo` is the portable complete-state branch. It lets a new machine initialize with the same agent-only project context while keeping `main` and feature branches free of AI workflow files.

Post-task flow:

1. Commit and push normal source/test/docs/config changes to the current upstream branch.
2. Ensure `.git/info/exclude` has the rldyour fullrepo block.
3. If the project is ready to clean its main branch, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --migrate-main` once and commit that index cleanup.
4. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --publish` after the normal branch is at its final `HEAD`.
5. Verify `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --status-json` and branch refs before final delivery.

Initialization flow:

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --bootstrap-init` before relying on missing agent-only context.
2. If `origin/fullrepo` exists, restore its agent-only files and install excludes.
3. If `origin/fullrepo` does not exist but local agent-only files exist, publish the initial generated `fullrepo` snapshot.
4. If the current branch tracks agent-only files, remove them from the index and commit that cleanup on the normal branch before final delivery.

`fullrepo` uses safe force updates because it is a generated snapshot branch. Use `--force-with-lease`, not a blind `--force`, so an unexpected remote update cannot be silently overwritten.

## Loop Prevention

The Stop hook writes `.serena/.flow_sync_marker` with a fingerprint of HEAD, dirty files, ahead/behind, branch, and Serena freshness. If `stop_hook_active=true` from Claude Code stdin AND the same fingerprint is already in the marker, the hook allows stop to avoid an infinite loop.

Runtime markers are ignored by git:

- `.serena/.flow_sync_marker`
- `.serena/.flow_post_task_state.json`
- `.serena/.stop_lifecycle_timeout_marker`

## Commit Rules

- Commit source changes by logical feature/fix/refactor units.
- Commit Serena/docs sync separately when it improves history clarity.
- Never commit secrets, runtime markers, browser artifacts, local env files, or accidental generated junk.
- Use Conventional Commits.
- Push to upstream when configured. If upstream is missing, ask before setting it.

## Cleanup Rules

- Remove merged worktrees and branches only after verifying they are merged into `main` and pushed if needed.
- `flow_post_task_state.py` exposes `branch_cleanup_state`; merged local branches, merged remote branches, and merged workflow worktree candidates keep `needs_flow_sync` true until cleaned or reported as blockers.
- Delete remote branches after merge when the branch was created for this workflow and no open PR depends on it. Protected branches such as `main` and `fullrepo` are never cleanup candidates.
- Ask the user if branch ownership, merge status, or remote state is unclear.
