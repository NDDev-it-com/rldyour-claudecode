# rldyour-mcps

MCP transport layer for the `rldyour-claudecode` marketplace. Single-owner of `.mcp.json` - no other plugin declares MCP servers.

## What's inside

- `0` skills, `0` slash commands, `0` agents, `0` hooks.
- `.mcp.json` - 10 pinned MCP servers covering Serena, Sequential Thinking, Chrome DevTools, Context7, DeepWiki, Grep, shadcn, Dart/Flutter, Figma, OpenAI Docs. Browser actions are health-gated and restricted to exact managed Playwright CLI plus this file's exact managed Chrome DevTools transport; the Webwright runtime is forbidden.
- `.env.example` - required env vars: `CONTEXT7_API_KEY`.

## Pinning policy

stdio servers pinned with `==X.Y.Z` (uvx) or `@X.Y.Z` (bunx). HTTP servers pinned by URL. Dual source of truth:

- `plugins/rldyour-mcps/.mcp.json` - primary, read by Claude Code.
- `config/mcp-runtime-versions.env` - companion env file for scripts/CI.

`scripts/check_mcp_runtime_versions.py` enforces parity. CI `dependency-check.yml` runs the same check on a weekly schedule.

Current verified package pins are Sequential Thinking MCP `2026.7.4` and
Context7 MCP `3.2.3`. Both continue to use their existing `bunx` stdio entry
points; changing either transport requires a separate compatibility decision.

## Runtime SDK requirements

- **Dart SDK 3.9+** required by `dart-flutter` MCP (`dart mcp-server` is a Dart SDK 3.9+ feature; toolchain pinning lives in `pubspec.yaml`, not `.mcp.json`). The SDK is provisioned by `macos-ubuntu-bootstrap` contract `2.3.0` and later (Ubuntu: tracked SDK archive `3.12.2`; macOS: Homebrew `dart-sdk`), and both of that adapter's verifiers gate on `dart mcp-server --version` responding - not merely on `dart` resolving. `scripts/bootstrap_check.sh` does **not** gate this; it checks only `python3`, `git`, and `node`. Source: `https://docs.flutter.dev/ai/mcp-server` (2026-05).

## Special notes

- `serena` server has `alwaysLoad: true` (CC v2.1.121+) - eager startup because Serena drives every UserPromptSubmit hook. Other servers are deferred until first tool call.
- Per-server `startup_timeout_sec` / `tool_timeout_sec` keys are NOT in the documented Claude Code `.mcp.json` schema - silently ignored. Use env vars `MCP_TIMEOUT`, `MCP_TOOL_TIMEOUT`, `MCP_CONNECTION_NONBLOCKING` instead.
- The `github` server was **removed** by owner decision. It required a `github-mcp-server` host binary that no bootstrap path installed on Ubuntu (the pin recorded `brew install github-mcp-server`, a macOS-only route) plus a `GITHUB_PERSONAL_ACCESS_TOKEN` that was never provisioned, so it could not start on a provisioned Linux desktop. Repository, issue, and pull-request work goes through the `gh` CLI, which the bootstrap does install. Do not reintroduce the server without a host-binary install path for every supported platform.
- Since CC v2.1.142, stdio MCP servers receive `${CLAUDE_PROJECT_DIR}` in their environment. No server in this manifest currently consumes it; reference it in `env` or `args` only when a future server genuinely needs the active project root.

## Dependencies

This is the base transport layer. Has no dependencies; every other plugin depends on `rldyour-mcps` (and `rldyour-flow` additionally depends on `rldyour-serena-mcp`).
