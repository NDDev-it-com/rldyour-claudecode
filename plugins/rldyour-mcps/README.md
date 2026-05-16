# rldyour-mcps

MCP transport layer for the `rldyour-claudecode` marketplace. Single-owner of `.mcp.json` - no other plugin declares MCP servers.

## What's inside

- `0` skills, `0` slash commands, `0` agents, `0` hooks.
- `.mcp.json` - 13 pinned MCP servers covering Serena, Sequential Thinking, Playwright, Chrome DevTools, Context7, DeepWiki, Grep, Semgrep, shadcn, Dart/Flutter, Figma, OpenAI Docs, GitHub.
- `.env.example` - required env vars: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`.

## Pinning policy

stdio servers pinned with `==X.Y.Z` (uvx) or `@X.Y.Z` (bunx). HTTP servers pinned by URL. Dual source of truth:

- `plugins/rldyour-mcps/.mcp.json` - primary, read by Claude Code.
- `config/mcp-runtime-versions.env` - companion env file for scripts/CI.

`scripts/check_mcp_runtime_versions.py` enforces parity. CI `dependency-check.yml` runs the same check on a weekly schedule.

## Runtime SDK requirements

- **Dart SDK 3.9+** required by `dart-flutter` MCP (`dart mcp-server` is a Dart SDK 3.9+ feature; toolchain pinning lives in `pubspec.yaml`, not `.mcp.json`). `scripts/bootstrap_check.sh` enforces this gate on bootstrap. Source: `https://docs.flutter.dev/ai/mcp-server` (2026-05).

## Special notes

- `serena` server has `alwaysLoad: true` (CC v2.1.121+) - eager startup because Serena drives every UserPromptSubmit hook. Other servers are deferred until first tool call.
- Per-server `startup_timeout_sec` / `tool_timeout_sec` keys are NOT in the documented Claude Code `.mcp.json` schema - silently ignored. Use env vars `MCP_TIMEOUT`, `MCP_TOOL_TIMEOUT`, `MCP_CONNECTION_NONBLOCKING` instead.
- `github` server uses local stdio transport (`github-mcp-server stdio --toolsets=repos,issues,pull_requests,users,context`) with `GITHUB_PERSONAL_ACCESS_TOKEN` in env. This keeps the marketplace self-contained without dependence on the `api.githubcopilot.com/mcp/` HTTP endpoint and works with a standard GitHub PAT (`repo` + `read:org` scopes are sufficient; no Copilot subscription required).
- Since CC v2.1.142, stdio MCP servers receive `${CLAUDE_PROJECT_DIR}` in their environment. No server in this manifest currently consumes it; reference it in `env` or `args` only when a future server genuinely needs the active project root.

## Dependencies

This is the base transport layer. Has no dependencies; every other plugin depends on `rldyour-mcps` (and `rldyour-flow` additionally depends on `rldyour-serena-mcp`).
