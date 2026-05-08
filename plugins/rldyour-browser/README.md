# rldyour-browser

Browser workflows over Playwright MCP and Chrome DevTools MCP. Skills-only consumer of MCP transport.

## What's inside

- `3` skills:
  - `browser-validation` — UI/scenarios validation via Playwright MCP (pixel-perfect, e2e, business logic, screenshots).
  - `browser-debug` — runtime debugging via Chrome DevTools MCP (console, network, hydration, performance, Lighthouse).
  - `browser-tool-routing` — picks Playwright vs Chrome DevTools vs both for a given task.
- `0` agents, `0` commands, `0` hooks.

## `allowed-tools`

All three skills declare explicit MCP wildcards:

- `browser-validation`: `mcp__plugin_rldyour-mcps_playwright__*`
- `browser-debug`: `mcp__plugin_rldyour-mcps_chrome-devtools__* + mcp__plugin_rldyour-mcps_playwright__*`

This pre-approves the relevant MCP tool sets so consumers don't get permission prompts during validation/debug runs.

## Browser artifacts

Screenshots, traces, and recordings belong under `browser/` in consumer projects (per `.gitignore` patterns: `.playwright-mcp/`, `playwright-report/`, `test-results/`). Never commit them.

## Dependencies

`rldyour-mcps` (Playwright + Chrome DevTools MCP servers live there).
