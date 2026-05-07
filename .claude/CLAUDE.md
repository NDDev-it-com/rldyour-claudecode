# Claude Code Project Memory — rldyour-claude

Personal Claude Code plugin marketplace authored by `rldyourmnd`. This file is project memory for Claude Code sessions working inside this repository. It is agent-only and lives on the `fullrepo` branch; it must not be committed to `main`.

## What This Repo Is

- A Claude Code marketplace (`./.claude-plugin/marketplace.json`, name `rldyour-claude`, `pluginRoot: ./plugins`).
- Nine first-party plugins all at `version: 0.1.0`, source form `./plugins/<name>`.
- No application runtime, no test suite, no build step. Every artifact is plugin metadata, skills, agents, slash commands, hooks, scripts, or references.
- `AGENTS.md` at repo root is the concise cross-tool root project-instruction file (https://agents.md/); this `.claude/CLAUDE.md` is the Claude Code-native deep memory complement. Both are agent-only and live on the `fullrepo` branch.

## Plugins And Components

```
rldyour-mcps         transport     0 skills • 0 cmds • 0 agents • 0 hooks  • .mcp.json (13 pinned servers)
rldyour-serena-mcp   semantic      2 skills • 0 cmds • 0 agents • 4 hooks
rldyour-flow         SDLC          7 skills • 5 cmds • 6 agents • 3 hooks  • 7 scripts • 7 references
rldyour-explore      research      2 skills • 1 cmd  • 1 agent  • 0 hooks
rldyour-security     security      2 skills • 1 cmd  • 0 agents • 0 hooks
rldyour-browser      browser       3 skills • 0 cmds • 0 agents • 0 hooks
rldyour-design       design        5 skills • 1 cmd  • 0 agents • 0 hooks
rldyour-lsps         lsp           4 skills • 0 cmds • 0 agents • 0 hooks  • 2 scripts • 3 references
rldyour-rules        rules         7 skills • 1 cmd  • 0 agents • 0 hooks  • 6 references
```

Total: 32 skills, 9 slash commands, 7 subagents.

## Slash Commands

| Command | Plugin | Purpose |
|---|---|---|
| `/rldyour-flow:ry-init` | flow | read-only scope discovery and context pack |
| `/rldyour-flow:ry-start` | flow | full task lifecycle (init→research→plan→implement→gates→review→sync) |
| `/rldyour-flow:ry-newp` | flow | new-project design with skeptical questions and architecture docs |
| `/rldyour-flow:ry-review` | flow | report-only deep review with reviewer tracks |
| `/rldyour-flow:ry-deploy` | flow | deploy with local↔GitHub↔server sync and fix-forward |
| `/rldyour-explore:ry-explore` | explore | deep multi-source research via `ry-explore` agent (opus[1m], max effort, `context: fork`) |
| `/rldyour-security:ry-sec-review` | security | defensive Mythos-style security review |
| `/rldyour-design:ry-design` | design | end-to-end Figma→code→tokens→FSD→shadcn/ui→ReactBits→browser validation |
| `/rldyour-rules:ry-rules-review` | rules | audit implementation against rldyour rules |

## Subagents

`plugins/rldyour-flow/agents/flow-*-review.md` — six reviewer subagents invoked from `ry-start` and `ry-review`:

- `flow-architecture-review` — boundaries, dependency direction, public API surface, data flow.
- `flow-quality-review` — correctness, edge cases, error handling, resource lifecycle.
- `flow-consistency-review` — naming, style, imports, project conventions.
- `flow-integration-review` — cross-module sync, contracts, schemas, migrations.
- `flow-verification-review` — test coverage, LSP, type/lint, browser/server evidence.
- `flow-security-review` — defensive-only auth/authz, validation, secrets, deploy/rollback safety.

All reviewer subagents: `model: sonnet`, `effort: high`, `maxTurns: 12-14`, `disallowedTools: [Edit, Write, NotebookEdit]`.

`plugins/rldyour-explore/agents/ry-explore.md` — single research agent with `model: opus[1m]`, `effort: max`, `maxTurns: 30`, `disallowedTools: [Edit, Write, NotebookEdit]`, `color: cyan`. Triggered by the `/rldyour-explore:ry-explore` slash command (`context: fork`).

## Hooks Lifecycle

Two plugins own hooks. Coordination contract: `flow.stop_post_task_sync.sh` waits for `serena_current=true` reported by Serena's Stop hook before running.

| Event | Owner | Script |
|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | `hooks/user_prompt_submit.sh` |
| PreToolUse:Bash | rldyour-serena-mcp | `hooks/prepare_auto_sync.sh` |
| PostToolUse:Bash | rldyour-serena-mcp | `hooks/mark_sync_required.sh` |
| PostToolUse:Bash | rldyour-flow | `hooks/post_tool_use_commit_advice.sh` |
| SessionStart | rldyour-flow | `hooks/session_start_context.sh` |
| Stop | rldyour-serena-mcp | `hooks/stop_memory_sync.sh` |
| Stop | rldyour-flow | `hooks/stop_post_task_sync.sh` |

All hooks are advisory: they emit `hookSpecificOutput.additionalContext` and exit `0` on internal errors. They never block tool use. Skip flags during local debugging: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT=1`, `RLDYOUR_SKIP_STOP_GATES=1`, `RLDYOUR_SKIP_FLOW_SYNC=1`.

Loop guard: `flow.stop_post_task_sync.sh` writes `.serena/.flow_sync_marker` with a fingerprint of (HEAD, dirty files, ahead/behind, branch, Serena freshness). If `stop_hook_active=true` and the same fingerprint is in the marker, the hook allows stop.

## MCP Transport

`plugins/rldyour-mcps/.mcp.json` is the single source of MCP servers for the whole marketplace. Run `/mcp` to inspect status. Pinned servers:

- `serena` — `uvx serena-agent==1.2.0` with `--context=agent` (canonical for generic CLI agents like Claude Code; exposes 45 of 46 Serena tools, only excludes the redundant `initial_instructions` tool). Web dashboard disabled.
- `sequential-thinking` — `bunx @modelcontextprotocol/server-sequential-thinking@2025.12.18`.
- `playwright` — `bunx @playwright/mcp@0.0.74 --headless --caps=network,storage,testing,devtools`.
- `chrome-devtools` — `bunx chrome-devtools-mcp@0.25.0 --headless --isolated`.
- `context7` — `bunx @upstash/context7-mcp@2.2.4`. Requires `CONTEXT7_API_KEY`.
- `deepwiki` — HTTP `https://mcp.deepwiki.com/mcp`.
- `grep` — HTTP `https://mcp.grep.app`.
- `semgrep` — `uvx semgrep==1.161.0 mcp`.
- `shadcn` — `bunx shadcn@4.7.0 mcp`.
- `dart-flutter` — `dart mcp-server --force-roots-fallback`.
- `figma` — HTTP `https://mcp.figma.com/mcp`.
- `openai-docs` — HTTP `https://developers.openai.com/mcp`.
- `github` — `github-mcp-server stdio`. Requires `GITHUB_PERSONAL_ACCESS_TOKEN`.

Timeouts are controlled by Claude Code env vars (canonical per `code.claude.com/docs/en/mcp`):
- `MCP_TIMEOUT` — startup timeout for any MCP server (e.g. `MCP_TIMEOUT=10000`).
- `MCP_TOOL_TIMEOUT` — per-tool-call timeout.
- `MAX_MCP_OUTPUT_TOKENS` — increases the 10k-token tool-output warning threshold.
- `MCP_CONNECTION_NONBLOCKING=1` — non-blocking startup for slow servers (per-server `alwaysLoad: true` opts back into blocking).

Per-server `startup_timeout_sec`/`tool_timeout_sec` keys are NOT in the documented `.mcp.json` schema. Do not re-add them — they are silently ignored.

## Architecture Layers

1. Transport — `rldyour-mcps`.
2. Semantic code — `rldyour-serena-mcp` (depends on `rldyour-mcps`).
3. SDLC orchestrator — `rldyour-flow` (depends on `rldyour-mcps`, `rldyour-serena-mcp`).
4. Domain plugins — `rldyour-explore`, `rldyour-security`, `rldyour-browser`, `rldyour-design`, `rldyour-lsps` (each depends on `rldyour-mcps`).
5. Engineering rules — `rldyour-rules` (depends on `rldyour-mcps`).

Dependencies are declared in each `plugin.json` under `"dependencies": ["..."]` (array form per docs at `code.claude.com/docs/en/plugins-reference#metadata-fields`). `claude plugin install <plugin>` resolves transitive installs and reports conflicts.

Hard boundaries:

- Only `rldyour-mcps` declares `.mcp.json`.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`.
- One domain per plugin; cross-plugin overlap is forbidden.
- `rldyour-browser` and `rldyour-design` are skills-only consumers of the transport layer.

## Fullrepo Branch Policy

`fullrepo` is the portable AI-context branch. It carries the normal tree plus agent-only files. `main` never carries agent-only files. Patterns are defined in `plugins/rldyour-flow/scripts/fullrepo_sync.py` (`AGENT_ONLY_PATTERNS`):

- root `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, `QWEN.md`;
- `.cursorrules`, `.windsurfrules`, `.aider*`;
- `.claude/**`, `.cursor/rules/**`, `.gemini/**`, `.roo/**`, `.windsurf/**`, `.openhands/**`;
- `.github/copilot-instructions.md`, `.github/instructions/**`, `.github/prompts/**`;
- `.agents/skills/**`, `.agents/commands/**`, `.agents/hooks/**`;
- `.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`, `.serena/research/**`, `.serena/newproj/**`, `.serena/deploy/**`.

Runtime markers (never published, ignored by git): `.serena/cache/`, `.serena/.gitignore`, `.serena/project.local.yml`, `.serena/.sync_marker`, `.serena/.serena_sync_state.json`, `.serena/.auto_sync_head`, `.serena/.active_workflow_intent.json`, `.serena/.dirty_stop_ack`, `.serena/.flow_sync_marker`, `.serena/.flow_post_task_state.json`.

Common operations:

- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init` — first-time setup on a new machine.
- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json` — machine-readable sync state.
- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish` — refresh `fullrepo` after agent-only changes (`--force-with-lease`).
- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --restore` — restore agent-only files from `origin/fullrepo`.
- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --migrate-main` — `git rm --cached` agent-only files left in the index.

## Validation And Diagnostics

- `claude plugin validate <path>` — run from repo root after editing any `marketplace.json` or `plugin.json`. CI mirrors this in `.github/workflows/validate.yml` on every PR.
- Minimum Claude Code version: **v2.1.111+** for the `model: opus[1m]` bracketed syntax in agent frontmatter (`ry-explore`). Earlier versions silently ignore it.
- `bash plugins/rldyour-flow/scripts/git_sync_audit.sh` — branch, upstream, ahead/behind, worktrees, merged-branch cleanup candidates.
- `python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json` — whether `AGENTS.md` and `.claude/CLAUDE.md` need review.
- `python3 plugins/rldyour-flow/scripts/flow_post_task_state.py` — fingerprint of dirty state, Serena freshness, branch cleanup candidates.
- `bash plugins/rldyour-flow/scripts/detect_project_checks.sh` — detect available product-side quality checks (this repo has none by design).
- `bash plugins/rldyour-lsps/scripts/check_lsps.sh` — LSP health check across supported languages (used in consumer projects, not here).

Useful Claude Code slash commands during work in this repo: `/mcp` (transport status), `/doctor` (env health), `/status` (session state), `/context` (current context), `/hooks` (active hooks), `/memory` (memory status).

## Engineering Conventions

- Russian user-facing communication; English repository artifacts. Skill `description` fields are Russian-leading.
- Skill frontmatter: `name`, `description`. Agent frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `disallowedTools`, `color`.
- `model: opus[1m]` is the canonical bracketed form for Opus 4.7 1M context (used by `ry-explore`).
- `model: sonnet` is the canonical short form for reviewer subagents.
- Slash command frontmatter: `description`, `argument-hint`, optional `context: fork` and `agent: <name>`.
- Conventional Commits with separate commits for source / docs / Serena knowledge when it improves history clarity.
- Never commit secrets, runtime markers, browser artifacts, local env files. `SECRET_RE` in `fullrepo_sync.py` blocks publishes containing `ctx7sk-*`, `ghp_*`, `github_pat_*`, `sk-*`, `xox[baprs]-*`, private-key headers, or `Bearer *`.
- All MCP server versions are pinned (stdio with `==X.Y.Z`; HTTP servers by URL).

## Don't

- Don't add a new plugin without confirming domain boundary against existing plugins.
- Don't add `.mcp.json` outside `rldyour-mcps`.
- Don't add `hooks.json` outside `rldyour-flow` or `rldyour-serena-mcp`.
- Don't commit `AGENTS.md`, `.claude/**`, `.serena/project.yml`, `.serena/memories/**` to `main` — fullrepo only.
- Don't write Serena memories from `ry-init` unless the user explicitly asked or the Stop hook required it.
- Don't force-push `main`; `--force-with-lease` is allowed only for `fullrepo`.
- Don't reduce this file to `@AGENTS.md` import; it must stay independently useful for Claude Code.

## Done Criteria

- All touched manifests pass `claude plugin validate`.
- `git status` clean of non-agent files; agent-only paths excluded via `.git/info/exclude` block (`# >>> rldyour fullrepo agent-only files >>>`).
- `fullrepo_sync.py --status-json` shows `tracked_agent_paths: []` on `main`.
- `fullrepo` is republished after any agent-only change.
- Plugin component cross-references (skills referencing scripts/agents/references) actually exist on disk.
- Reviewer subagents (when invoked) produce read-only findings, never edit files.
