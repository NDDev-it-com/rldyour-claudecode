# rldyour Flow Lifecycle

This reference defines the executable workflow behind `ry-init`, `ry-start`, `ry-newp`, `ry-review`, and `ry-deploy`.

## Global Rules

- User-facing conversation is Russian by default.
- Repository documentation, code comments, commit messages, Serena memories, plans, and research archives are English.
- Code is the source of truth. Memories and docs must be verified against code, git diff, tests, and runtime evidence.
- Serena-first inspection applies before raw file reads for supported languages.
- Research-heavy technical decisions use `rldyour-explore`.
- LSP and project checks use `rldyour-lsps`.
- UI/browser-visible changes use `rldyour-browser`.
- Security-sensitive changes use `rldyour-security` and `flow-security-review`.
- Implementation favors quality, consistency, maintainability, and scale over speed.

## ry-init

Purpose: build a reliable model of a project, module, backend/frontend/mobile area, or feature scope. The output is a scoped context pack, not a shallow file list.

Core order:

1. Git sync audit: dirty state, current branch, upstream ahead/behind, worktrees, local/remote branches.
2. If uncommitted, unmerged, or stale merged branch/worktree state exists, deeply review it. If correct and consistent, synchronize it into `main`, merge safe branches, push, and remove merged worktrees/branches. If risky, ask the user with concrete options.
3. Read tracked agent context directly from the checked-out tree. `AGENTS.md`, `CLAUDE.md`, `.serena/*`, `.claude/*`, `.codex/*`, and similar files are ordinary tracked source on `main`; there is no bootstrap, restore, or migrate step for them.
4. Serena readiness: `initial_instructions`, `list_memories`, relevant `read_memory`, and `onboarding` only when no usable project context exists.
5. Scope detection: project, module, sphere, or feature. For a sphere such as backend, inspect the whole sphere and its integration points.
6. Semantic map: `get_symbols_overview`, targeted `find_symbol`, `find_referencing_symbols`, `search_for_pattern` only when needed.
7. Data and contract map: database tables/fields, schemas, migrations, API contracts, generated artifacts, configuration keys, environment variables, and integration boundaries that affect the scope.
8. Pattern map: established project patterns for naming, layering, validation, errors, tests, state management, and dependency usage.
9. External enrichment only for unclear architecture, framework behavior, or current best practices.
10. Synthesis in Russian, with exact source-of-truth paths, symbols, contracts, checks, known gaps, and `Memory candidates (not written)` when useful durable facts were found.

`ry-init` must not write Serena memories by default. It may report candidate memory updates, but it runs `serena-memory-sync` only when the user explicitly requested memory synchronization or a Stop/stale-memory hook requires it.

## ry-start

Purpose: complete feature or fix lifecycle from prompt to reviewed, synchronized state.

Core order:

1. If context is missing, run a scoped `ry-init`.
2. Understand prompt and affected scope.
3. Research project code through Serena and project memories.
4. Research current best practices and libraries through `rldyour-explore`.
5. Pass the context sufficiency gate before editing: code paths, symbols, data contracts, integration points, existing patterns, checks, and research evidence must be known or explicitly marked as unknown.
6. Produce a detailed implementation plan.
7. Verify the plan against real code and adjust until coherent.
8. Create or select branch/worktree and implement through atomic commits.
9. Run progress checkpoints after meaningful milestones or every 2-3 plan groups: compare implementation against the plan, context pack, existing patterns, and touched integration path.
10. Run quality gates and fix all issues in touched scope plus integration path.
11. Run reviewer workflow only when the user explicitly asks for review, audit, security review, rules review, or `ry-review`. Use subagents only for that explicit review path.
12. Run browser/security/design/LSP workflows when triggered by the change type.
13. Synchronize Serena memories, AGENTS.md/CLAUDE.md when present, git, GitHub, and worktree cleanup through `flow-post-task-sync`. Agent context is committed as ordinary tracked source on `main`.

## Session Context

The SessionStart hook is advisory, fast, offline, and read-only. It adds compact startup state so Codex knows whether local repository markers, docs, tracked dirty files, or worktrees need attention. Deep Serena freshness and branch cleanup are handled by `ry-init`, Stop, doctor, or explicit validation rather than SessionStart.

The PostToolUse commit advice hook is advisory and read-only. It checks recently created commits for conventional commit format, suspicious sensitive paths, runtime markers, browser evidence, and broad commit scope. It informs the next model step without rejecting the command.

The PreToolUse cwd guard blocks Bash commands that would rename or remove the active Codex session directory or repository root. This is a runtime safety boundary: Codex hook commands run with the session cwd, so a manually renamed or deleted cwd can prevent future hook processes from starting with `No such file or directory` before any hook script can recover.

The Stop lifecycle dispatcher drains stdin before any early exit, runs Serena and Flow children with bounded process-group timeouts, and uses local repository status for the hook hot path. Stop must not fetch or push; those operations belong to explicit `flow-post-task-sync`, doctor, or validation commands.

## Agent Context Standard

Agent context - `.serena/memories/`, `.serena/project.yml`, `.serena/plans/`, `.serena/research/`, `.serena/newproj/`, `.serena/deploy/`, `AGENTS.md`, and `.claude/` - is tracked normally on `main` as ordinary source. There is no separate agent-context branch and no agent-only overlay; tooling reads the checked-out tree directly. A repository may opt into stricter handling with `.rldyour/project-policy.json`: `normal_branch_policy.agent_files=strict` keeps configured AI files out of pushes.

Tracked agent-context examples:

- root `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, and `QWEN.md`;
- `.serena/project.yml`, `.serena/memories/`, `.serena/plans/`, `.serena/research/`, `.serena/newproj/`, and `.serena/deploy/`;
- `.claude/`, `.codex/`, `.cursor/rules/`, `.agents/skills/`, `.agents/commands/`, `.agents/hooks/`, `.github/instructions/`, and `.github/prompts/`.

Runtime-local state stays gitignored and must never be committed: `.serena/cache/`, `.serena/reviews/`, `.serena/diagnostics/`, `.serena/project.local.yml`, the `.serena/.*` markers/state/locks, secrets, caches, local env files, browser artifacts, tokens, cookies, and credentials.

Never force-push `main`.

## Local Git Pre-Push Guard

Use `scripts/install_local_git_hooks.sh --apply` in product repositories that need local protection before pushes. The installer writes a managed `.git/hooks/pre-push` wrapper and delegates policy to `plugins/rldyour-flow/scripts/local_git_ai_guard.sh`.

The guard reads Git pre-push stdin per ref. For normal product refs it blocks runtime/local-only paths, definite secrets, and, by default, agent-only paths plus AI-marker additions. If project policy allows tracked agent files, those paths are allowed while runtime markers, browser artifacts, local env files, and definite secrets remain blocked. Mixed pushes are evaluated per ref.

## ry-newp

Purpose: design a new project before or alongside initial scaffold.

Output location: `.serena/newproj/<project>/`.

Default artifacts:

- `01_HLO.md`
- `02_REQUIREMENTS.md`
- `03_ARCHITECTURE.md`
- `04_ADRS.md`
- `05_TECH_STACK.md`
- `06_API.md`
- `07_DATA.md`
- `08_INFRA.md`
- `09_SECURITY.md`
- `10_TESTING.md`
- `11_PROJECT_STRUCTURE.md`
- `12_CONVENTIONS.md`
- `13_DELIVERY_PLAN.md`

Scaffold policy: documents first. Minimal scaffold is allowed only after the user approves it and only when it activates a useful Serena project structure without creating junk.

## ry-review

Purpose: review a diff, branch, PR, scope, or prompt with code evidence.

Review target: diff plus affected integration graph via Serena. Report-only by default.

Reviewer tracks:

- Architecture
- Implementation quality
- Consistency
- Integration synchronization
- Verification and manual tests
- Security when sensitive or explicitly requested

## ry-deploy

Purpose: synchronize local repo, GitHub, and server, then deploy and verify.

Deploy order:

1. Read deploy contract from `AGENTS.md`, `CLAUDE.md`, or `.serena/deploy/*.md` in that priority.
2. Verify local branch, PR, quality gates, Serena memories, docs, and GitHub sync.
3. Inspect server baseline: git status, current SHA, logs before restart, disk space, process manager.
4. Pull or sync code to server.
5. Run migrations only after readiness checks and backup/rollback contract verification.
6. Restart/build services.
7. Verify logs, health, tests, and business-critical flows.
8. If deployment fails, perform RCA through logs, code, and internet research, then fix-forward. Ask the user with options for risky operations.
9. DB rollback only when an explicit rollback contract and backup/restore point are verified.
