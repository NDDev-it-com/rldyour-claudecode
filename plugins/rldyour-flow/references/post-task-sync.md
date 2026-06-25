# Post-Task Synchronization

Post-task sync is the last phase of meaningful work. It prevents forgotten changes, stale project knowledge, and mismatched local/GitHub/server state.

## Order

1. Serena memory freshness first.
2. Project instruction docs second: `AGENTS.md` and `.claude/CLAUDE.md`.
3. Quality checks and manual evidence third.
4. Atomic commits fourth.
5. GitHub sync fifth.
6. Merged branch/worktree cleanup last.

## Session And Commit Advice

The flow SessionStart hook gives Codex a compact offline repository state packet before work starts or resumes. Treat it as an input to planning: inspect tracked dirty files, local ahead/behind state, worktree count, docs, and Serena sync-marker state before making assumptions. Deep Serena freshness and branch cleanup are intentionally left to `ry-init`, Stop, doctor, or explicit validation.

The flow PreToolUse cwd guard blocks Bash commands that would rename or remove the active Codex session directory or repository root. The flow PostToolUse hook emits commit advice after Bash `git commit` commands. Advice is informational and should be reviewed before pushing or final delivery, but it must not be treated as a hard failure by itself.

## Serena Interaction

`rldyour-serena-mcp` owns `.serena/memories`, `.serena/plans`, and `.serena/research`. The flow hook must not duplicate that work. It waits until the Serena state script reports current knowledge, then asks for `flow-post-task-sync`.

Serena knowledge is tracked normally on the `main` branch as ordinary source. The Serena commit helper creates the knowledge-only commit directly and clears runtime sync markers.

## AGENTS.md And .claude/CLAUDE.md

Codex reads `AGENTS.md` as project instructions. Update it when the task changes durable project rules, setup commands, quality gates, deploy contracts, architecture constraints, or agent workflow guidance. Keep it Codex-native and practical: repository layout, commands, checks, constraints, tool routing, and done criteria.

Claude Code reads project memory from `.claude/CLAUDE.md`. Create and update it for every project, optimized for Claude Code rather than as a thin copy of `AGENTS.md`: commands, architecture, workflow, conventions, Claude Code diagnostics, and Claude-specific settings/hooks/skills locations.

Both files must contain verified facts, not chat history or speculative plans.

Root `AGENTS.md`, `.claude/CLAUDE.md`, and `REVIEW.md` are tracked normally on the `main` branch as ordinary source. Project policy in `.rldyour/project-policy.json`, `.rldyour/project-policy.local.json`, or `RLDYOUR_PROJECT_POLICY` may still set `instruction_docs.mode` and related options.

Use `plugins/rldyour-flow/scripts/instruction_docs_state.py --json` to decide whether review is needed and `python3 scripts/validate_instruction_docs.py --require-agent-docs` to validate the tracked instruction docs.

## Agent Context

Agent context - `.serena/memories/`, `.serena/project.yml`, `.serena/plans/`, `.serena/research/`, `.serena/newproj/`, `.serena/deploy/`, `AGENTS.md`, `.claude/` - is tracked normally on the `main` branch as ordinary source. There is no separate agent-context branch and no agent-only overlay; a new machine gets the full context simply by checking out `main`. Commit agent-context changes like any other source change. Runtime-local state stays gitignored: `.serena/cache/`, `.serena/reviews/`, `.serena/diagnostics/`, `.serena/project.local.yml`, and `.serena/.*` markers.

## Loop Prevention

The Stop hook writes `.serena/.flow_sync_marker` with a fingerprint of HEAD, dirty files, ahead/behind, branch, policy, and blocking/advisory reasons. If the same fingerprint already requested a continuation during active Stop processing, the hook writes `.serena/.flow_blocker_ack.json` and allows stop to avoid a loop. Stop-state checks stay local-only; network fetch/push checks belong to explicit sync and validation commands.

Bootstrap-only `.serena` runtime files created by tool startup, such as cache entries plus runtime markers, are not meaningful work by themselves and must not trigger a post-task sync continuation.

Runtime markers are ignored by git:

- `.serena/.flow_sync_marker`
- `.serena/.flow_post_task_state.json`
- `.serena/.flow_blocker_ack.json`

## Commit Rules

- Commit source changes by logical feature/fix/refactor units.
- Commit Serena/docs sync separately when it improves history clarity.
- Never commit secrets, runtime markers, browser artifacts, local env files, or accidental generated junk.
- Use Conventional Commits.
- Push to upstream when configured. If upstream is missing, ask before setting it.

## Cleanup Rules

- Remove merged worktrees and branches only after verifying they are merged into `main` and pushed if needed.
- `flow_post_task_state.py` exposes `branch_cleanup_state.blocking_candidates` and `advisory_candidates`; only policy-allowed blocking candidates keep `needs_flow_sync` true.
- Delete remote branches after merge only when policy allows it, the branch was created for this workflow, and no open PR depends on it. Protected branches such as `main` and `dev` are never cleanup candidates.
- Ask the user if branch ownership, merge status, or remote state is unclear.
