# AGENTS.md — rldyour-claude

Personal Claude Code plugin marketplace by `rldyourmnd`. The repository ships nine plugins that compose an opinionated SDLC, semantic-code, MCP transport, security, browser, design, LSP, and rules layer for Claude Code. There is no runtime application code — every artifact in this repo is plugin metadata, skills, slash commands, agents, hooks, scripts, and references.

This `AGENTS.md` is the concise root project-instruction file for any AI agent working in this repository — cross-tool standard governed by the Linux Foundation Agentic AI Foundation (AAIF) since 2025-12-09 (see https://agents.md/). The deep Claude Code-native memory lives in `./.claude/CLAUDE.md` and contains subagent matrix, hook canon, skill-listing budget, frontmatter conventions, and Don't/Done rules that other AI tools don't need.

<!-- Maintainer note (HTML comments are not parsed by most AI tools): Anthropic's claude-plugins-official ships only a 53-line README.md — no CLAUDE.md, no AGENTS.md. Our two-file split is justified by cross-tool ambition (AGENTS.md is read by 25+ tools as of May 2026) plus Claude Code-deep specifics. Keep this file under 150 lines. -->


## Source Of Truth

- `./.claude-plugin/marketplace.json` — marketplace manifest, `pluginRoot: ./plugins`, source form `./plugins/<name>`.
- `./plugins/<name>/.claude-plugin/plugin.json` — per-plugin manifest. Required: `$schema`, `name`, `version` (`0.1.0` everywhere), `description`, `author`, `license`, `homepage`, `repository`, `keywords`.
- `./plugins/rldyour-mcps/.mcp.json` — single-owner MCP transport for the whole marketplace.
- `./plugins/rldyour-flow/hooks/hooks.json` and `./plugins/rldyour-serena-mcp/hooks/hooks.json` — only two plugins ever own hooks.
- `./plugins/rldyour-flow/references/*.md` — durable contracts for `ry-init`, `ry-start`, `ry-newp`, `ry-review`, `ry-deploy`, post-task sync, reviewer protocol, and source citations.
- `./plugins/rldyour-rules/references/*.md` — engineering rules: architecture, dependency, quality gates, project instructions and ADRs.

## Repository Layout

```
.claude-plugin/marketplace.json
plugins/
  rldyour-mcps/        # transport — 13 pinned MCP servers (.mcp.json)
  rldyour-serena-mcp/  # Serena workflow + memory sync + 4 lifecycle hooks
  rldyour-flow/        # ry-init/start/newp/review/deploy + 6 reviewer agents + 3 hooks + 7 scripts
  rldyour-explore/     # ry-explore agent (opus[1m], max effort) + tech/web research skills
  rldyour-security/    # owasp-top-10-implementation + ry-sec-review
  rldyour-browser/     # browser-validation/debug/tool-routing (skills-only)
  rldyour-design/      # ry-design + figma-to-code + design-system + fsd + design-validation
  rldyour-lsps/        # lsp-routing/health-check/setup + serena-lsp-integration
  rldyour-rules/       # quality-first + architecture/dependency/implementation/verification + ry-rules-review
.serena/               # agent-only Serena project state (fullrepo-managed)
.gitignore             # blocks secrets, runtime markers, browser artifacts
```

## Plugin Boundaries (hard rules)

- `rldyour-mcps` is the single owner of any `.mcp.json`. Other plugins consume MCP transport from it; they never declare MCP servers themselves.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`. No other plugin attaches Claude Code lifecycle hooks.
- One domain per plugin. No catch-all plugins. Cross-plugin overlap is forbidden.
- `rldyour-design` and `rldyour-browser` are skills-only and use Figma/shadcn/Playwright/Chrome DevTools transport from `rldyour-mcps`.

## Validation And Setup

- Validate manifests: `claude plugin validate <path>` from repo root after editing any `marketplace.json` or `plugin.json`. CI runs this on every PR via `.github/workflows/validate.yml`.
- Tag releases: `claude plugin tag --push` (v2.1.119+) validates that `plugin.json` and marketplace entry agree on version, refuses dirty worktrees and pre-existing tags. Tag convention: `<plugin-name>--v<version>`.
- Prune orphaned dependencies: `claude plugin prune` (v2.1.121+); `claude plugin uninstall <plugin> --prune` cascades.
- Inspect a plugin's component inventory and projected per-session token cost: `claude plugin details <name>` (v2.1.139+).
- Minimum Claude Code version: **v2.1.111+** for `model: opus[1m]` bracketed extended-context model syntax used by the `ry-explore` agent. Earlier versions silently ignore the bracket suffix. Current local: **v2.1.139** (verification range v2.1.111-v2.1.139, May 2026).
- Bootstrap a fresh checkout: `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init` — installs `.git/info/exclude` block for agent-only files and restores or publishes `fullrepo`.
- Audit git/branch/worktree state: `bash plugins/rldyour-flow/scripts/git_sync_audit.sh`.
- Quality checks for product repositories that consume this marketplace: `bash plugins/rldyour-flow/scripts/detect_project_checks.sh`. This repository has no runtime test suite by design.
- LSP health for consumer projects: `bash plugins/rldyour-lsps/scripts/check_lsps.sh`.

## SDLC Workflow

Five orchestrated lifecycle skills live in `rldyour-flow`. Each has a Russian-leading skill description.

- `/rldyour-flow:ry-init` — read-only scope discovery and context pack, mandatory before non-trivial work.
- `/rldyour-flow:ry-start` — full task lifecycle: init → research → plan → implement → quality gates → reviewer subagents → post-task sync.
- `/rldyour-flow:ry-newp` — design new project: skeptical questions → research → architecture docs → optional scaffold.
- `/rldyour-flow:ry-review` — report-only deep review with reviewer tracks (architecture/quality/consistency/integration/verification/security).
- `/rldyour-flow:ry-deploy` — deploy with local↔GitHub↔server sync, log checks, fix-forward, docs/git finalization.

Reviewer subagents live in `plugins/rldyour-flow/agents/flow-*-review.md`. All run on `model: sonnet`, `effort: high`, `maxTurns: 36` (security: `42`), with `disallowedTools: [Edit, Write, NotebookEdit]` and distinct colors (architecture: blue, quality: green, consistency: purple, integration: orange, verification: pink, security: red). They are read-only and self-contained. Generous `maxTurns` is intentional — MCP-heavy toolsets consume turns on tool plumbing.

## Hooks Lifecycle

Two plugins coordinate hooks. The `flow.stop_post_task_sync.sh` hook waits for `serena_current=true` from the Serena Stop hook before running.

| Event | Owner | Script |
|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | `hooks/user_prompt_submit.sh` |
| PreToolUse:Bash | rldyour-serena-mcp | `hooks/prepare_auto_sync.sh` |
| PostToolUse:Bash | rldyour-serena-mcp | `hooks/mark_sync_required.sh` |
| PostToolUse:Bash | rldyour-flow | `hooks/post_tool_use_commit_advice.sh` |
| SessionStart | rldyour-flow | `hooks/session_start_context.sh` |
| Stop | rldyour-serena-mcp | `hooks/stop_memory_sync.sh` |
| Stop | rldyour-flow | `hooks/stop_post_task_sync.sh` |

All hooks are advisory (informational `additionalContext`) and exit `0` on errors. Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE`, `RLDYOUR_SKIP_STOP_GATES`, `RLDYOUR_SKIP_FLOW_SYNC`, `RLDYOUR_SKIP_SERENA_SYNC`.

## Fullrepo Branch Policy

Agent-only files live on the `fullrepo` branch only. Patterns are defined in `plugins/rldyour-flow/scripts/fullrepo_sync.py` (`AGENT_ONLY_PATTERNS`) and include: root `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.claude/**`, `.cursor/rules/**`, `.gemini/**`, `.roo/**`, `.windsurf/**`, `.openhands/**`, `.aider*`, `.agents/skills/**`, `.agents/commands/**`, `.agents/hooks/**`, `.github/copilot-instructions.md`, `.github/instructions/**`, `.github/prompts/**`, `.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`, `.serena/research/**`, `.serena/newproj/**`, `.serena/deploy/**`.

Subcommands:

- `--bootstrap-init` — install excludes, restore remote `fullrepo`, publish first snapshot when missing, migrate tracked agent-only files out of the index.
- `--restore` — fetch and restore agent-only files from `origin/fullrepo` and install excludes.
- `--migrate-main` — `git rm --cached` tracked agent-only files; worktree files survive.
- `--publish` — push snapshot tree to `fullrepo` with `--force-with-lease`.
- `--status-json` — machine-readable state.

`main` must never carry agent-only files. `fullrepo` is regenerated on every meaningful change.

## MCP Transport (`rldyour-mcps/.mcp.json`)

13 pinned servers: `serena-agent==1.3.0` (with `--context=agent` for generic CLI agents like Claude Code, **`alwaysLoad: true`** since v2.1.121+ — eager startup because Serena drives every UserPromptSubmit hook; 1.3.0 mode-selection refactor scopes the tool surface to 28 tools under `agent` context, all workflow tools we use present), `@modelcontextprotocol/server-sequential-thinking@2025.12.18`, `@playwright/mcp@0.0.75`, `chrome-devtools-mcp@0.25.0`, `@upstash/context7-mcp@2.2.5`, `deepwiki` (HTTP `mcp.deepwiki.com`), `grep` (HTTP `mcp.grep.app`), `semgrep==1.162.0`, `shadcn@4.7.0`, `dart mcp-server`, `figma` (HTTP `mcp.figma.com`), `openai-docs` (HTTP), `github` (HTTP `api.githubcopilot.com/mcp/`). Required env: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`.

MCP timeouts are controlled by Claude Code env vars (per official docs at `code.claude.com/docs/en/mcp`): `MCP_TIMEOUT` (server startup, default depends on Claude Code version) and `MCP_TOOL_TIMEOUT` (per-tool-call). Per-server `startup_timeout_sec`/`tool_timeout_sec` keys in `.mcp.json` are NOT documented and silently ignored — do not add them.

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
| rldyour-design | rldyour-mcps |
| rldyour-lsps | rldyour-mcps |
| rldyour-rules | rldyour-mcps |

## Tool Routing

- Code understanding: prefer Serena MCP tools (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `search_for_pattern`) over raw text reads. See `plugins/rldyour-serena-mcp/skills/serena-code-workflow/SKILL.md`.
- Memory writes: only via `serena-memory-sync` skill (fact-only, no chat history).
- LSP / diagnostics / refactoring: route through `plugins/rldyour-lsps/skills/lsp-routing/SKILL.md`.
- Browser validation, debugging, performance: `plugins/rldyour-browser/skills/*`.
- Figma → code: `plugins/rldyour-design/skills/figma-to-code/SKILL.md`.
- Deep research: `/rldyour-explore:ry-explore` slash command runs `agents/ry-explore.md` (opus[1m], max effort, isolated context).
- Defensive security review: `/rldyour-security:ry-sec-review`.
- Architecture/quality/consistency/integration/verification/security review for an existing diff: `/rldyour-flow:ry-review`.

## Engineering Constraints

- Russian user-facing language; English repository artifacts (skill descriptions are Russian-leading).
- Quality-first: no hacks, no fake checks, no swallowed errors. See `plugins/rldyour-rules/skills/quality-first-engineering/SKILL.md`.
- Plugin boundary discipline: see `plugins/rldyour-rules/skills/architecture-boundaries/SKILL.md`.
- Dependency policy: latest-compatible, source-backed, SLSA Level 2, SBOM and lockfile discipline. See `plugins/rldyour-rules/references/dependency-policy.md`.
- Conventional Commits for all changes. Atomic commits per logical unit.
- Never commit secrets, runtime markers, browser artifacts, local env files.
- All MCP server versions are pinned (stdio servers with `==X.Y.Z`; HTTP servers by URL).

## Done Criteria

- All touched manifests pass `claude plugin validate`.
- `git status` is clean of non-agent files; `.serena/` and other agent-only paths are excluded via `.git/info/exclude`.
- `fullrepo_sync.py --status-json` shows `tracked_agent_paths: []` on `main`.
- `fullrepo` is republished after any agent-only change.
- Conventional commits for source/docs/Serena knowledge are kept separate when it improves history clarity.
- Pre-existing reviewer subagents and skills referenced by new components actually exist on disk.

<!-- Living-doc note: when discovering a non-obvious project fact during work that another AI tool would also need (cross-tool concern), propose an AGENTS.md edit in the same change. Don't auto-generate. Claude Code-specific facts (skill listing, hook canon, subagent matrix) belong in ./.claude/CLAUDE.md instead. -->

