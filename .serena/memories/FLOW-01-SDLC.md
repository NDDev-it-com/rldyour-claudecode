<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: 0ff613d chore(release): cut 0.2.2 (wave-2 reviewer transport hardening)
Scope: plugins/rldyour-flow/**, scripts/worktree_add.sh, AGENTS.md, .claude/CLAUDE.md, plugins/rldyour-flow/scripts/fullrepo_sync.py
Area: FLOW
-->

# FLOW-01-SDLC

## Purpose

rldyour-flow orchestration contracts for init/start/review/deploy workflows, reviewer agents, fullrepo, worktrees, and post-task synchronization.

## Source Of Truth

- `plugins/rldyour-flow/skills/ry-init/SKILL.md`: scoped read-only context discovery.
- `plugins/rldyour-flow/skills/ry-start/SKILL.md`: full task lifecycle and reviewer phase.
- `plugins/rldyour-flow/skills/flow-post-task-sync/SKILL.md`: final checks/git/fullrepo synchronization.
- `plugins/rldyour-flow/references/context-sufficiency-gate.md`: evidence gate before editing.
- `plugins/rldyour-flow/scripts/fullrepo_sync.py`: agent-only branch restore/publish/migrate policy.
- `scripts/worktree_add.sh`: one-step worktree creation plus fullrepo restore.
- `plugins/rldyour-flow/hooks/stop_post_task_sync.sh`: post-task Stop gate.

## Current Behavior

- `ry-init` is read-only for memories by default. It may report memory candidates but must not write `.serena` unless explicitly requested or a stale-memory gate requires it.
- `ry-start` lifecycle: init/context, research, plan, implement, verify, reviewer phase when applicable, and post-task sync.
- `flow-post-task-sync` finalizes by refreshing memories/docs, running checks, committing/pushing normal branch changes, publishing `fullrepo`, and cleaning safe merged branches/worktrees. Step 1 (Serena memory freshness check) uses `python3 "$(git rev-parse --show-toplevel)"/plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` — cwd-independent path required because the skill lives in `rldyour-flow` but the script is in `rldyour-serena-mcp`; `${CLAUDE_PLUGIN_ROOT}` is the wrong root here and `${CLAUDE_PROJECT_DIR}` is documented only for hook commands and stdio MCP env. Verified at `plugins/rldyour-flow/skills/flow-post-task-sync/SKILL.md` line 19 at HEAD.
- Reviewer agents live in `plugins/rldyour-flow/agents/flow-*-review.md`; they are read-only and use an explicit `tools:` allowlist containing built-in read tools (`Read`, `Grep`, `Glob`, `Bash`) plus an explicit 14-tool read-only Serena subset and MCP wildcards for context7/deepwiki/grep. `flow-security-review` additionally allows `WebFetch`, `WebSearch`, and `mcp__plugin_rldyour-mcps_semgrep__*`. The previous `disallowedTools: [Edit, Write, NotebookEdit]` denylist is removed from reviewer agents; `flow-memory-sync` is the only agent retaining it as defence-in-depth (verified at `plugins/rldyour-flow/agents/flow-architecture-review.md` HEAD). Reviewer contracts now require `run_id = <UTC-ISO-compact>-<git-short-sha>` and `.serena/reviews/<run_id>/` report directories.
- `reviewer-protocol.md` is the shared contract for subagent result transport: full reports are written to `<report_dir>/<reviewer-name>.md` with heredoc marker `RLDYOUR_REPORT_EOF`, and parent summaries include count + capped one-liner findings with `info` severity support; 6-track output is compacted to prevent Claude Code parent-context overflow.
- `ry-start` and `ry-review` must read each full report file for every `critical` and `high` finding before disposition because `flow-security-review` carries `Category`, `Attack path`, and `Verification` fields only in the report body.
- Fullrepo-managed repositories keep agent-only files out of `main` and publish them to `origin/fullrepo`.

## Fullrepo Contract

- Agent-only paths include `AGENTS.md`, `.claude/**`, root `CLAUDE.md`, `REVIEW.md`, `.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`, `.serena/research/**`, `.agents/**`, `.cursor/rules/**`, `.github/instructions/**`, `.github/prompts/**`, and similar AI context files.
- `fullrepo_sync.py` runtime exclude set includes `.serena/diagnostics/**` and `.serena/reviews/**` to prevent runtime review artifacts from affecting artifact policy for restore/publish operations.
- `fullrepo_sync.py --bootstrap-init`: installs excludes, restores remote `fullrepo`, publishes first snapshot when missing, and migrates tracked agent-only files out of the normal branch index.
- `fullrepo_sync.py --restore`: fetches/restores agent-only files and installs excludes; no publish.
- `fullrepo_sync.py --publish`: regenerates `fullrepo` snapshot with `--force-with-lease`.
- `fullrepo_sync.py --status-json`: machine-readable status for tracked agent paths and dirty state.

## Worktree Contract

- `scripts/worktree_add.sh <branch> [path]` creates a worktree and then runs `fullrepo_sync.py --restore` in that worktree. Branch name validation uses two gates: conservative regex `^[A-Za-z0-9._/-]{1,255}$` first, then `git check-ref-format --branch "${BRANCH}"` as a second gate to reject refs the regex accepts but git refuses (e.g., `-/foo`, double slash, path traversal). Verified at `scripts/worktree_add.sh` lines 75-80 at HEAD.
- `RLDYOUR_WORKTREE_BASE_REF=HEAD` starts from local HEAD; default behavior follows origin/main freshness.
- New worktrees must not symlink `.serena/` or `.claude/`; each worktree gets its own agent-only context copy.
- SessionStart bootstrap restores from `origin/fullrepo` when canonical markers are missing.

## Invariants

- Do not force-push `main`.
- `--force-with-lease` is allowed only for `fullrepo` publish.
- Do not revert user changes unless explicitly requested.
- Do not commit agent-only files to `main` in fullrepo-managed repos.
- Run Serena memory sync before final flow post-task sync when durable behavior changed.

## Verification

- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json`: verifies tracked agent paths and fullrepo state.
- `bash scripts/sync_fullrepo_branch.sh --status`: wrapper status check.
- `bash plugins/rldyour-flow/scripts/git_sync_audit.sh`: branch/worktree audit.
- `python3 plugins/rldyour-flow/scripts/flow_post_task_state.py`: Stop gate state.
- `bash scripts/smoke_hooks.sh`: hook integration dry-run.

## Cross-References

- Quality philosophy and May 2026 defaults: [[PHILOSOPHY-01-QUALITY-FIRST]].
- Canonical implementation patterns (frontmatter, paths, hook templates, sanitization): [[PATTERNS-01-CANONICAL]].
- Hook lifecycle details and Stop gate coordination: [[HOOKS-01-LIFECYCLE]].
- Memory freshness contract (consumed by `flow-post-task-sync` step 1): [[SERENA-01-MEMORY-SYNC]].
- Rules enforcement during `ry-start` quality gates: [[RULES-01-POLICY]] (`verification-quality-gates` skill).
- Security review track invoked from `ry-start`/`ry-review`: [[SECURITY-01-OWASP]] (`flow-security-review` parallel reviewer subagent).
- Browser validation track for UI-visible changes: [[BROWSER-01-WORKFLOW]].
- Design workflow track for Figma/FSD/shadcn changes: [[DESIGN-01-WORKFLOW]].
- LSP routing for type-check / lint gates: [[LSPS-01-LANGUAGE-SERVERS]].
- Research escalation when implementation requires authoritative sources: [[EXPLORE-01-RESEARCH]].
- Release boundary, plugin version bumps, CHANGELOG conventions: [[RELEASE-01-VALIDATION]].
- Instruction-doc sync (AGENTS.md, .claude/CLAUDE.md, REVIEW.md): [[DOCS-01-INSTRUCTIONS]].
- Marketplace boundaries and per-plugin domain pointers: [[CORE-02-MARKETPLACE]].
- Open / closed technical debt: [[TECHDEBT-01-NOW]].
