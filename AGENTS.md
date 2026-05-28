# AGENTS.md - rldyour-claude

Claude Code plugin marketplace for rldyour SDLC flows: MCP/LSP, Serena memory, security review, browser/design workflows, and reviewer agents. The repository ships nine plugins that compose an opinionated SDLC, semantic-code, MCP transport, security, browser, design, LSP, and rules layer for Claude Code. There is no runtime application code - every artifact in this repo is plugin metadata, skills, slash commands, agents, hooks, scripts, and references.

This `AGENTS.md` is the concise root project-instruction file for any AI agent working in this repository - cross-tool standard governed by the Linux Foundation Agentic AI Foundation (AAIF) since 2025-12-09 (see https://agents.md/). The deep Claude Code-native memory lives in `./.claude/CLAUDE.md` and contains subagent matrix, hook canon, skill-listing budget, frontmatter conventions, and Don't/Done rules that other AI tools don't need.

<!-- Maintainer note (HTML comments are not parsed by most AI tools): Anthropic's claude-plugins-official marketplace ships `.claude-plugin/marketplace.json` + 30+ first-party plugins (pr-review-toolkit, feature-dev, hookify, ralph-loop, security-guidance, plugin-dev + LSP set + more, live snapshot 2026-05-17) but no root AGENTS.md or CLAUDE.md. Our two-file split is justified by cross-tool ambition (AGENTS.md is read by 30+ tools / 60k+ repos per agents.md spec, May 2026) plus Claude Code-deep specifics. Both files dual-purpose: full information for each agent class, no `@import` redirection. Keep this file under 200 lines. -->

<!-- sync_contract:
claims:
  mcp_owner: rldyour-mcps
  hook_owners: [rldyour-flow, rldyour-serena-mcp]
  lsp_owner: rldyour-lsps
  reviewer_transport_marker: RLDYOUR_REPORT_EOF
  reviewer_report_dir_template: ".serena/reviews/<run_id>/"
  reviewer_run_id_format: "<UTC-ISO-compact>-<git-short-sha>"
  claude_code_runtime_pin: "2.1.153"
  claude_code_feature_floor: "2.1.146"
  skill_listing_budget_fraction: 0.04
  max_skill_description_chars: 1536
  fullrepo_branch: fullrepo
  plugin_count: 9
  skill_count: 33
  command_count: 11
  subagent_count: 8
-->

## Source Of Truth

- `./.claude-plugin/marketplace.json` - marketplace manifest with per-entry relative sources (`source: "./plugins/<name>"`); `metadata.pluginRoot` is intentionally absent.
- `./plugins/<name>/.claude-plugin/plugin.json` - per-plugin manifest. Required: `$schema`, `name`, `version` (per-plugin values can differ), `description`, `author`, `license`, `homepage`, `repository`, `keywords`.
- `./plugins/rldyour-mcps/.mcp.json` - single-owner MCP transport for the whole marketplace.
- `./plugins/rldyour-flow/hooks/hooks.json` and `./plugins/rldyour-serena-mcp/hooks/hooks.json` - only two plugins ever own hooks.
- `./plugins/rldyour-flow/references/*.md` - durable contracts for `ry-init`, `ry-start`, `ry-newp`, `ry-review`, `ry-deploy`, post-task sync, reviewer protocol, and source citations.
- `./plugins/rldyour-rules/references/*.md` - engineering rules: architecture, dependency, quality gates, project instructions and ADRs.
- `./config/rldyour-contract.json` + `./docs/contract-matrix.md` - machine-readable cross-tool business contract and generated matrix; `./.serena/memories/CORE-01-INDEX.md` maps numbered project memories.

## Repository Layout

```
.claude-plugin/marketplace.json
plugins/
  rldyour-mcps/        # transport - 13 pinned MCP servers (.mcp.json)
  rldyour-serena-mcp/  # Serena code workflow + memory sync + lifecycle hooks
  rldyour-flow/        # SDLC skills (ry-*) + reviewer subagents + hooks + scripts
  rldyour-explore/     # ry-explore agent + tech/web research skills
  rldyour-security/    # OWASP impl skill + /ry-sec-review
  rldyour-browser/     # browser validation/debug/tool-routing
  rldyour-design/      # ry-design + figma-to-code + design-system + fsd
  rldyour-lsps/        # lsp routing/health-check/setup + Serena LSP integration
  rldyour-rules/       # quality-first + architecture/dep/verification + /ry-rules-review
```

## Plugin Boundaries (hard rules)

- `rldyour-mcps` is the single owner of any `.mcp.json`. Other plugins consume MCP transport from it; they never declare MCP servers themselves.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`. No other plugin attaches Claude Code lifecycle hooks.
- One domain per plugin. No catch-all plugins. Cross-plugin overlap is forbidden.
- `rldyour-design` and `rldyour-browser` are skills-only and use Figma/shadcn/Playwright/Chrome DevTools transport from `rldyour-mcps`; `rldyour-design` also depends on `rldyour-browser` for validation routing.

## Codex CLI Compatibility

OpenAI Codex CLI reads `AGENTS.md` before starting work and runs commands listed in **Validation And Setup**. No nested `AGENTS.md` files exist. Specs: `https://agents.md/` (Linux Foundation AAIF, 2025-12-09) and `https://developers.openai.com/codex/guides/agents-md`.

## Validation And Setup

- Manifests: `claude plugin validate <path>` after editing any `marketplace.json` or `plugin.json`. CI runs on every PR via `.github/workflows/validate.yml`.
- Tag releases: `claude plugin tag --push` (v2.1.118+). Convention: `<plugin-name>--v<version>` and `marketplace--v<version>`.
- Inspect plugin inventory + projected context cost: `claude plugin details <name>` (v2.1.139+; v2.1.142 adds LSP).
- Cross-tool contract gate: `python3 scripts/validate_contract.py && python3 scripts/generate_contract_matrix.py --check`.
- **Claude Code runtime pin: v2.1.153. Feature compatibility floor: v2.1.146+.** The package pin in `package.json`, `references/claude-baseline.json`, and `config/mcp-runtime-versions.env` is the release/runtime source of truth. The floor covers every feature used by the marketplace: `opus[1m]` (v2.1.111+, account-gated), `alwaysLoad` (v2.1.121+), hook `if` filter (v2.1.118+), exec-form `args` (v2.1.139+), marketplace `displayName` support (v2.1.143+), Stop/SubagentStop `background_tasks` and `session_crons` input fields (v2.1.145+), Auto mode `AskUserQuestion` behavior needed by decision gates (v2.1.146+), `disallowed-tools`, `SessionStart.reloadSkills`, `MessageDisplay`, `skipLfs`, status-line terminal-size env, and `claude agents` native command/bundled skill autocomplete through v2.1.153.
- Bootstrap a fresh checkout: `bash scripts/bootstrap_check.sh` (fullrepo restore + claude validate + required env + dart SDK + pre-push hook advisory).
- Audit git/branch/worktree: `bash plugins/rldyour-flow/scripts/git_sync_audit.sh`.
- Quality checks for consumer projects: `bash plugins/rldyour-flow/scripts/detect_project_checks.sh`. LSP health: `bash plugins/rldyour-lsps/scripts/check_lsps.sh`. This repository has no runtime test suite by design.
- Required env: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN` (see `docs/runtime-env.md`).

## SDLC Workflow

Five orchestrated lifecycle skills plus one explicit sync command (Russian-leading descriptions) live in `rldyour-flow`:

- `/rldyour-flow:ry-init` - read-only scope discovery and context pack.
- `/rldyour-flow:ry-start` - full task lifecycle: init → research → plan → implement → quality gates → reviewers → post-task sync.
- `/rldyour-flow:ry-newp` - new project: skeptical intake → research → architecture docs → optional scaffold.
- `/rldyour-flow:ry-review` - report-only deep review with 6 reviewer tracks.
- `/rldyour-flow:ry-deploy` - deploy with local ↔ GitHub ↔ server sync, log checks, fix-forward.
- `/rldyour-flow:ry-sync` - public slash-command wrapper for `flow-post-task-sync` finalization: Serena freshness, instruction docs, checks, commits, push, `fullrepo`, cleanup.

Reviewer subagents in `plugins/rldyour-flow/agents/flow-*-review.md`: all `model: sonnet`, `effort: high`, `maxTurns: 90` (security `100`), explicit `tools:` allowlist (`Read`, `Grep`, `Glob`, `Bash` + Serena/Context7/DeepWiki/Grep MCP; security track adds `WebFetch`, `WebSearch`, Semgrep). Distinct colors: blue/green/purple/orange/pink/red. Reviewer protocol details in `plugins/rldyour-flow/references/reviewer-protocol.md`.

Reviewer output uses a **file-first transport contract** (full text in `references/reviewer-protocol.md` "Output Transport") to work around the Claude Code 2.0.77+ `task.output` regression (Anthropic issues [`#16789`](https://github.com/anthropics/claude-code/issues/16789), [`#20531`](https://github.com/anthropics/claude-code/issues/20531), [`#23463`](https://github.com/anthropics/claude-code/issues/23463)). Each reviewer writes the full report to `<report_dir>/<reviewer-name>.md` via `Bash` heredoc with marker `RLDYOUR_REPORT_EOF` and returns a compact summary ≤ 4 KB. 6 tracks × ≤ 4 KB = ≤ 24 KB; structurally prevents the overflow class. Orchestrator MUST `Read` per-reviewer report for every `critical`/`high` finding before disposition.

## Hooks Lifecycle

Two plugins coordinate hooks. `rldyour-flow` owns the single registered Claude Stop hook through `hooks/stop_lifecycle_dispatcher.sh`; the dispatcher runs the Serena memory child check before the Flow post-task child check. `flow.stop_post_task_sync.sh` derives `serena_current` by calling `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`; it does not depend on a separate Serena hook registration.

| Event | Owner | Script | Timeout |
|---|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | `hooks/user_prompt_submit.sh` | 5s |
| PreToolUse:Bash | rldyour-serena-mcp | `hooks/prepare_auto_sync.sh` | 5s |
| PostToolUse:Bash | rldyour-serena-mcp | `hooks/mark_sync_required.sh` | 5s |
| PostToolUse:Bash | rldyour-flow | `hooks/post_tool_use_commit_advice.sh` | 5s |
| SessionStart | rldyour-flow | `hooks/session_start_worktree_bootstrap.sh` | 30s |
| SessionStart | rldyour-flow | `hooks/session_start_context.sh` | 5s |
| Stop | rldyour-flow | `hooks/stop_lifecycle_dispatcher.sh` | 45s |

Most hooks are advisory and exit `0`; the registered Stop dispatcher is an advisory enforcement gate that writes guidance to stderr and blocks with `exit 2` when memory or post-task sync is required. Flow Stop state is local-only in the hook hot path (`RLDYOUR_FLOW_STATE_LOCAL_ONLY=1`) and repeated `stop_hook_active=true` fingerprints are allowed to stop with a system message instead of looping. The dispatcher also writes `.serena/.stop_lifecycle_timeout_marker` so a repeated identical child timeout cannot loop forever. The single hook that performs a bounded worktree mutation is `session_start_worktree_bootstrap.sh` - it runs `fullrepo_sync.py --restore` (never `--publish`, never touches origin) only when an agent-only marker is missing in the active worktree. Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE`, `RLDYOUR_SKIP_STOP_GATES`, `RLDYOUR_SKIP_FLOW_SYNC`, `RLDYOUR_SKIP_SERENA_SYNC`, `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP`.

## Worktree Workflow

Multiple git worktrees can run in parallel - one worktree per feature, each driving its own Claude Code session. All worktrees share the main `.git` database but each gets its own working tree, its own per-worktree `.git/info/exclude` block, and its own copy of agent-only files. Per-worktree `.serena/memories/` prevents concurrent sessions from stomping on each other; reconciliation happens via `flow-post-task-sync` publishing to `fullrepo`.

```bash
scripts/worktree_add.sh <branch> [path]                          # create worktree + bootstrap agent-only context
RLDYOUR_DRY_RUN=1 scripts/worktree_add.sh <branch>               # preview
RLDYOUR_WORKTREE_BASE_REF=HEAD scripts/worktree_add.sh <branch>  # branch from local HEAD instead of origin/main
git worktree remove <path>                                       # tear down
```

The helper invokes `fullrepo_sync.py --restore` (never `--publish`) and aborts with a clear error if `origin/fullrepo` does not yet exist - publishing is reserved for the orchestrator (`flow-post-task-sync` skill or explicit `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish` from the main worktree).

Automatic bootstrap on `claude` startup: `hooks/session_start_worktree_bootstrap.sh` runs `fullrepo_sync.py --restore` (never `--publish`) when an agent-only marker is missing. Skip flag: `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1`.

Relevant Claude Code settings (in `~/.claude/settings.json`): `worktree.baseRef` (`"fresh"` default, or `"head"` to preserve unpushed commits), `worktree.symlinkDirectories` (keep `.serena/` and `.claude/` OUT), `worktree.sparsePaths` (large monorepos only).

Trust model: agent-only files restored into a fresh worktree come from `origin/fullrepo`. A compromised origin would inject attacker files on next `claude` startup. Mitigations: 2FA on GitHub, branch protection on `fullrepo`, optional `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1` disable switch. Same trust boundary as manual `fullrepo_sync.py --bootstrap-init`.

## Fullrepo Branch Policy

Agent-only files live on the `fullrepo` branch only. Patterns are defined in `plugins/rldyour-flow/scripts/fullrepo_sync.py` (`AGENT_ONLY_PATTERNS`) and include: root `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.claude/**`, `.codex/**`, `.cursor/rules/**`, `.gemini/**`, `.roo/**`, `.windsurf/**`, `.openhands/**`, `.aider*`, `.agents/skills/**`, `.agents/commands/**`, `.agents/hooks/**`, `.github/copilot-instructions.md`, `.github/instructions/**`, `.github/prompts/**`, `.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`, `.serena/research/**`, `.serena/newproj/**`, `.serena/deploy/**`.

Subcommands:

- `--bootstrap-init` - install excludes, restore remote `fullrepo`, publish first snapshot when missing, migrate tracked agent-only files out of the index.
- `--restore` - fetch and restore agent-only files from `origin/fullrepo` and install excludes.
- `--migrate-main` - `git rm --cached` tracked agent-only files; worktree files survive.
- `--publish` - push snapshot tree to `fullrepo` with `--force-with-lease`.
- `--status-json` - machine-readable state.

`main` must never carry agent-only files. `fullrepo` is regenerated on every meaningful change.

## MCP Transport (`rldyour-mcps/.mcp.json`)

13 pinned servers (full pin source: `config/mcp-runtime-versions.env`): `serena-agent==1.5.3` with `alwaysLoad: true` (v2.1.121+), `@modelcontextprotocol/server-sequential-thinking@2025.12.18`, `@playwright/mcp@0.0.75`, `chrome-devtools-mcp@1.1.1`, `@upstash/context7-mcp@2.2.5`, `semgrep==1.164.0`, `shadcn@4.8.2`, host binaries `github-mcp-server` (1.0.5) + `dart` (3.12.0); HTTP: `deepwiki`, `grep`, `figma`, `openai-docs`. Required env: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`. GitHub MCP uses local stdio (not Copilot-gated HTTP).

Timeout knobs are env-only: `MCP_TIMEOUT`, `MCP_TOOL_TIMEOUT` (v2.1.142+ for HTTP/SSE). Per-server `startup_timeout_sec`/`tool_timeout_sec` keys are NOT documented and silently ignored - do not add them.

## Cross-Plugin Dependencies

Each consumer plugin declares its dependency on `rldyour-mcps` (and `rldyour-serena-mcp` for `rldyour-flow`) in `plugin.json` under `"dependencies": ["..."]`. This array of plugin names lets `claude plugin install` resolve transitive installs and surface conflicts. Schema source: https://code.claude.com/docs/en/plugins-reference#metadata-fields.

Current dependency graph:

| Plugin | Depends on |
|---|---|
| rldyour-mcps | (none) |
| rldyour-serena-mcp | rldyour-mcps |
| rldyour-flow | rldyour-mcps, rldyour-serena-mcp |
| rldyour-explore | rldyour-mcps |
| rldyour-security | rldyour-mcps |
| rldyour-browser | rldyour-mcps |
| rldyour-design | rldyour-mcps, rldyour-browser |
| rldyour-lsps | rldyour-mcps |
| rldyour-rules | rldyour-mcps |

## Tool Routing

- Code understanding: prefer Serena MCP tools (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `search_for_pattern`) over raw text reads. See `plugins/rldyour-serena-mcp/skills/serena-code-workflow/SKILL.md`.
- Memory writes: use `flow-memory-sync` subagent when Stop/post-task sync requires it; use the `serena-memory-sync` skill as the manual/fallback workflow. Memories are fact-only, use `CORE-01-INDEX.md` as the map, new topics use `AREA-01-SLUG.md`, and broad files must be split instead of expanded indefinitely.
- LSP / diagnostics / refactoring: route through `plugins/rldyour-lsps/skills/lsp-routing/SKILL.md`.
- Browser validation, debugging, performance: `plugins/rldyour-browser/skills/*`.
- Figma → code: `plugins/rldyour-design/skills/figma-to-code/SKILL.md`.
- Deep research: `/rldyour-explore:ry-explore` slash command runs `agents/ry-explore.md` (opus[1m], max effort, isolated context).
- Defensive security review: `/rldyour-security:ry-sec-review`.
- Architecture/quality/consistency/integration/verification/security review for an existing diff: `/rldyour-flow:ry-review`.

## Engineering Constraints

- Russian user-facing language; English repository artifacts. Skill descriptions are Russian-leading with `EN triggers:` appended; budget set via `skillListingBudgetFraction: 0.04` in `./.claude/CLAUDE.md`.
- Quality-first: no hacks, no fake checks, no swallowed errors. See `plugins/rldyour-rules/skills/quality-first-engineering/SKILL.md`.
- Plugin boundary + dependency policy (SLSA L2 + SBOM + lockfile): `plugins/rldyour-rules/skills/architecture-boundaries/SKILL.md`, `plugins/rldyour-rules/references/dependency-policy.md`.
- Conventional Commits for all changes; atomic commits per logical unit; ≤ 72-char subject.
- Keep history logical and inspectable: split unrelated implementation, tests/validators, docs/instructions, license/metadata, generated artifacts, and Serena/fullrepo sync when independently reviewable. Do not rewrite already-pushed history without explicit owner approval.
- Never commit secrets, runtime markers, browser artifacts, local env files. All MCP versions pinned.
- CI workflows run on explicit user request only (`workflow_dispatch` + PR gates); see `.github/workflows/README.md`.
- **Always Read a file before Edit/Write** (Claude Code Edit/Write track per-session Read state). For batch updates use `sed -i` via Bash (bypasses the tracker).

## Done Criteria

- All touched manifests pass `claude plugin validate`.
- `git status` is clean of non-agent files; `.serena/` and other agent-only paths are excluded via `.git/info/exclude`.
- `fullrepo_sync.py --status-json` shows `tracked_agent_paths: []` on `main`.
- `fullrepo` is republished after any agent-only change.
- Conventional commits for source/docs/Serena knowledge are kept separate when it improves history clarity.
- Pre-existing reviewer subagents and skills referenced by new components actually exist on disk.

## Cross-Tool Support

`AGENTS.md` is the cross-tool agent-instruction standard (Linux Foundation AAIF; 60k+ repos, 30+ tools per `https://agents.md/`). Claude Code-specific deep memory (subagent matrix, hook canon, skill budgets, CC changelog adoption, Don't/Done rules) lives in `./.claude/CLAUDE.md`. Both files are dual-source (no `@import` redirection); split verified by `python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json` + `instruction-docs-sync` skill.
