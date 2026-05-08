# rldyour-mcps

MCP transport layer for the `rldyour-claude` marketplace. Single-owner of `.mcp.json` — no other plugin declares MCP servers.

## What's inside

- `0` skills, `0` slash commands, `0` agents, `0` hooks.
- `.mcp.json` — 13 pinned MCP servers covering Serena, Sequential Thinking, Playwright, Chrome DevTools, Context7, DeepWiki, Grep, Semgrep, shadcn, Dart/Flutter, Figma, OpenAI Docs, GitHub.
- `.env.example` — required env vars: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`.

## Pinning policy

stdio servers pinned with `==X.Y.Z` (uvx) or `@X.Y.Z` (bunx). HTTP servers pinned by URL. Dual source of truth:

- `plugins/rldyour-mcps/.mcp.json` — primary, read by Claude Code.
- `config/mcp-runtime-versions.env` — companion env file for scripts/CI.

`scripts/check_mcp_runtime_versions.py` enforces parity. CI `dependency-check.yml` runs the same check on a weekly schedule.

## Special notes

- `serena` server has `alwaysLoad: true` (CC v2.1.121+) — eager startup because Serena drives every UserPromptSubmit hook. Other servers are deferred until first tool call.
- Per-server `startup_timeout_sec` / `tool_timeout_sec` keys are NOT in the documented Claude Code `.mcp.json` schema — silently ignored. Use env vars `MCP_TIMEOUT`, `MCP_TOOL_TIMEOUT`, `MCP_CONNECTION_NONBLOCKING` instead.

## Dependencies

This is the base transport layer. Has no dependencies; every other plugin depends on `rldyour-mcps` (and `rldyour-flow` additionally depends on `rldyour-serena-mcp`).
