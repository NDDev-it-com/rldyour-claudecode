# rldyour-claude marketplace state

Last commit: bbb934b (main, 2026-05-07).
Marketplace name: `rldyour-claude`. Repo: github.com/rldyourmnd/rldyour-claude (private).

## Layered architecture (verified)

1. Transport — `rldyour-mcps` (single owner of `.mcp.json`, 13 pinned servers).
2. Semantic code — `rldyour-serena-mcp` (depends on `rldyour-mcps`).
3. SDLC orchestrator — `rldyour-flow` (depends on `rldyour-mcps`, `rldyour-serena-mcp`).
4. Domain — `rldyour-explore`, `rldyour-security`, `rldyour-browser`, `rldyour-design`,
   `rldyour-lsps` (each depends on `rldyour-mcps`).
5. Engineering rules — `rldyour-rules` (depends on `rldyour-mcps`).

Cross-plugin `dependencies` declared in plugin.json `dependencies: [...]` array.

## Hard boundaries

- Only `rldyour-mcps` declares `.mcp.json`.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`.
- One domain per plugin; cross-plugin overlap forbidden.
- `rldyour-browser`/`rldyour-design` are skills-only consumers of transport.

## Hooks lifecycle (coordination contract)

| Event | Owner | Script |
|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | hooks/user_prompt_submit.sh |
| PreToolUse:Bash | rldyour-serena-mcp | hooks/prepare_auto_sync.sh |
| PostToolUse:Bash | rldyour-serena-mcp | hooks/mark_sync_required.sh |
| PostToolUse:Bash | rldyour-flow | hooks/post_tool_use_commit_advice.sh |
| SessionStart | rldyour-flow | hooks/session_start_context.sh |
| Stop | rldyour-serena-mcp | hooks/stop_memory_sync.sh |
| Stop | rldyour-flow | hooks/stop_post_task_sync.sh |

`flow.stop_post_task_sync.sh` waits for `serena_current=true` from the Serena Stop hook
before running. Loop guard: `.serena/.flow_sync_marker` fingerprint of (HEAD, dirty,
ahead/behind, branch, Serena freshness). If `stop_hook_active=true` and same fingerprint,
hook allows stop.

All hooks advisory: emit `hookSpecificOutput.additionalContext`, exit 0 on errors.
Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_STOP_GATES`,
`RLDYOUR_SKIP_FLOW_SYNC`.

## Subagent matrix

Reviewer (rldyour-flow/agents/flow-*-review.md): `model: sonnet`, `effort: high`,
`maxTurns: 12-14`, `disallowedTools: [Edit, Write, NotebookEdit]`. 6 agents:
architecture, quality, consistency, integration, verification, security.

Research (rldyour-explore/agents/ry-explore.md): `model: opus[1m]`, `effort: max`,
`maxTurns: 30`, `disallowedTools: [Edit, Write, NotebookEdit]`, `color: cyan`.
Triggered via `/rldyour-explore:ry-explore` slash command (`context: fork`).

## MCP transport (rldyour-mcps/.mcp.json)

13 pinned servers; all dead `startup_timeout_sec`/`tool_timeout_sec` keys removed
(commit 0d78443).

- serena: `serena-agent==1.2.0`, `--context=agent`, web dashboard disabled.
- sequential-thinking: `@modelcontextprotocol/server-sequential-thinking@2025.12.18`.
- playwright: `@playwright/mcp@0.0.74` headless.
- chrome-devtools: `chrome-devtools-mcp@0.25.0` headless isolated.
- context7: `@upstash/context7-mcp@2.2.4`. Requires `CONTEXT7_API_KEY`.
- deepwiki: HTTP `mcp.deepwiki.com/mcp`.
- grep: HTTP `mcp.grep.app`.
- semgrep: `semgrep==1.161.0`.
- shadcn: `shadcn@4.7.0`.
- dart-flutter: `dart mcp-server --force-roots-fallback`.
- figma: HTTP `mcp.figma.com/mcp`.
- openai-docs: HTTP `developers.openai.com/mcp`.
- github: `github-mcp-server stdio`. Requires `GITHUB_PERSONAL_ACCESS_TOKEN`.

Timeouts via env: `MCP_TIMEOUT`, `MCP_TOOL_TIMEOUT`, `MAX_MCP_OUTPUT_TOKENS`,
`MCP_CONNECTION_NONBLOCKING`.

## Serena MCP context

`--context=agent` is canonical for Claude Code in Serena 1.2.0 (commit 482c421
switched from previous `codex` value). Exposes 45 of 46 Serena tools (only excludes
the redundant `initial_instructions` tool that Claude Code loads via ToolSearch).

Serena 1.2.0 has no `claude-code` context. The `serena prompts print-cc-system-prompt-override`
command prints a Claude Code-specific system prompt that maps Read/Edit/Glob/Grep
to Serena's symbolic tools as PRIMARY — used when running Claude Code with
`--system-prompt` flag.

Serena memory location: project-level via `.serena/memories/` (managed by
`rldyour-serena-mcp`).

## Fullrepo branch policy

Agent-only files live on `fullrepo` only. `AGENT_ONLY_PATTERNS` in
`plugins/rldyour-flow/scripts/fullrepo_sync.py`:

- root: AGENTS.md, CLAUDE.md, REVIEW.md, GEMINI.md, QWEN.md, .cursorrules,
  .windsurfrules, .aider*
- directories: .claude/**, .cursor/rules/**, .gemini/**, .roo/**, .windsurf/**,
  .openhands/**, .agents/{skills,commands,hooks}/**
- .github: copilot-instructions.md, instructions/**, prompts/**
- .serena: project.yml, memories/**, plans/**, research/**, newproj/**, deploy/**

`.codex/**` was removed from this list in commit 5feae39 (this marketplace targets
Claude Code only).

`fullrepo_sync.py` subcommands: `--bootstrap-init`, `--restore`, `--migrate-main`,
`--publish` (uses `--force-with-lease`), `--status-json`.

## CI

`.github/workflows/validate.yml` (commit bbb934b) runs on push, pull_request, and
workflow_dispatch:
1. `claude plugin validate .` + per-plugin validation via `npm install -g @anthropic-ai/claude-code`.
2. Syntax checks: JSON manifests, Python AST, bash -n, frontmatter presence.

## Conventions

- User-facing Russian; English repo artifacts.
- Skill `description` Russian-leading.
- Conventional Commits, ≤72 chars, single scope `(scope):`.
- Atomic commits; secrets/runtime/browser artifacts never committed.
- All MCP server versions pinned (stdio `==X.Y.Z`; HTTP by URL).
- Min Claude Code: **v2.1.111+** for `model: opus[1m]` bracket syntax in agents.

## Recent commit history (a115b86..bbb934b)

- 482c421 feat(mcps): switch Serena MCP --context to agent
- 5feae39 refactor(flow,serena-mcp): drop .codex/ globs and rename CODEX_DOC constant
- 131c57b docs: reframe AGENTS.md as cross-tool root file
- 0d78443 chore(mcps): drop unsupported timeout fields from .mcp.json
- bcfa726 feat: declare cross-plugin dependencies in plugin.json
- bbb934b ci: add claude plugin validate workflow
