# AGENTS.md — rldyour-claude

Personal Claude Code plugin marketplace by `rldyourmnd`. The repository ships nine plugins that compose an opinionated SDLC, semantic-code, MCP transport, security, browser, design, LSP, and rules layer for Claude Code. There is no runtime application code — every artifact in this repo is plugin metadata, skills, slash commands, agents, hooks, scripts, and references.

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

- Validate manifests: `claude plugin validate` (run from repo root after editing any `marketplace.json` or `plugin.json`).
- Bootstrap a fresh checkout: `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init` — installs `.git/info/exclude` block for agent-only files and restores or publishes `fullrepo`.
- Audit git/branch/worktree state: `bash plugins/rldyour-flow/scripts/git_sync_audit.sh`.
- Quality checks for product repositories that consume this marketplace: `bash plugins/rldyour-flow/scripts/detect_project_checks.sh`. This repository has no runtime test suite by design.
- LSP health for consumer projects: `bash plugins/rldyour-lsps/scripts/check_lsps.sh`.

## SDLC Workflow

Five orchestrated lifecycle skills live in `rldyour-flow`. Each has a Russian-leading skill description and an English `description` slash-command frontmatter.

- `/rldyour-flow:ry-init` — read-only scope discovery and context pack, mandatory before non-trivial work.
- `/rldyour-flow:ry-start` — full task lifecycle: init → research → plan → implement → quality gates → reviewer subagents → post-task sync.
- `/rldyour-flow:ry-newp` — design new project: skeptical questions → research → architecture docs → optional scaffold.
- `/rldyour-flow:ry-review` — report-only deep review with reviewer tracks (architecture/quality/consistency/integration/verification/security).
- `/rldyour-flow:ry-deploy` — deploy with local↔GitHub↔server sync, log checks, fix-forward, docs/git finalization.

Reviewer subagents live in `plugins/rldyour-flow/agents/flow-*-review.md`. All run on `model: sonnet`, `effort: high`, `maxTurns: 12-14`, with `disallowedTools: Edit, Write, NotebookEdit`. They are read-only and self-contained.

## Hooks Lifecycle

Two plugins coordinate hooks. The `flow.stop_post_task_sync.sh` hook waits for `serena_current=true` from the Serena Stop hook before running.

| Event | Owner plugin | Script |
|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | `hooks/user_prompt_submit.sh` |
| PreToolUse:Bash | rldyour-serena-mcp | `hooks/prepare_auto_sync.sh` |
| PostToolUse:Bash | rldyour-serena-mcp | `hooks/mark_sync_required.sh` |
| PostToolUse:Bash | rldyour-flow | `hooks/post_tool_use_commit_advice.sh` |
| SessionStart | rldyour-flow | `hooks/session_start_context.sh` |
| Stop | rldyour-serena-mcp | `hooks/stop_memory_sync.sh` |
| Stop | rldyour-flow | `hooks/stop_post_task_sync.sh` |

All hooks are advisory (informational `additionalContext`) and exit `0` on errors. Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_STOP_GATES`, `RLDYOUR_SKIP_FLOW_SYNC`.

## Fullrepo Branch Policy

Agent-only files live on the `fullrepo` branch only. Patterns are defined in `plugins/rldyour-flow/scripts/fullrepo_sync.py` (`AGENT_ONLY_PATTERNS`) and include: root `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.claude/**`, `.codex/**`, `.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`, `.serena/research/**`, `.serena/newproj/**`, `.serena/deploy/**`.

Subcommands:

- `--bootstrap-init` — install excludes, restore remote `fullrepo`, publish first snapshot when missing, migrate tracked agent-only files out of the index.
- `--restore` — fetch and restore agent-only files from `origin/fullrepo` and install excludes.
- `--migrate-main` — `git rm --cached` tracked agent-only files; worktree files survive.
- `--publish` — push snapshot tree to `fullrepo` with `--force-with-lease`.
- `--status-json` — machine-readable state.

`main` must never carry agent-only files. `fullrepo` is regenerated on every meaningful change.

## MCP Transport (`rldyour-mcps/.mcp.json`)

13 pinned servers: `serena-agent==1.2.0`, `@modelcontextprotocol/server-sequential-thinking@2025.12.18`, `@playwright/mcp@0.0.74`, `chrome-devtools-mcp@0.25.0`, `@upstash/context7-mcp@2.2.4`, `deepwiki` (HTTP `mcp.deepwiki.com`), `grep` (HTTP `mcp.grep.app`), `semgrep==1.161.0`, `shadcn@4.7.0`, `dart mcp-server`, `figma` (HTTP `mcp.figma.com`), `openai-docs` (HTTP), `github-mcp-server`. Required env: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`.

## Tool Routing For Codex

- Code understanding: prefer Serena MCP tools (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `search_for_pattern`) over raw `rg` and full-file reads. See `plugins/rldyour-serena-mcp/skills/serena-code-workflow/SKILL.md`.
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
