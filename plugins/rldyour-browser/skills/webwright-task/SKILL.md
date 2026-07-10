---
name: webwright-task
description: "Совместимый маршрут legacy Webwright task intent в управляемые Playwright CLI и Chrome DevTools MCP; Webwright runtime не запускается. Используй для: найти, сравнить, выгрузить, повторить, reusable workflow. EN triggers: Webwright task, long-horizon web task, RPA, extraction, reusable workflow."
allowed-tools:
  - Bash
  - mcp__plugin_rldyour-mcps_chrome-devtools__*
---

# Webwright Task Compatibility Workflow

## Mandatory CloakBrowser Boundary

This boundary applies before every browser action:

1. Run exactly:

   ```bash
   $HOME/.local/bin/cloakbrowser-cdp-health
   ```

   If the command is missing or exits nonzero, stop immediately and report `NOT_PROVEN`.
2. Browser execution is permitted only through:
   - the exact `$HOME/.local/bin/playwright-cli` executable; `run-code` and `--filename` are forbidden;
   - the approved Chrome DevTools MCP transport, exactly `/bin/sh -c 'exec "$HOME/.local/bin/chrome-devtools-mcp" --headless --isolated --no-usage-statistics --no-performance-crux'`.
3. Never execute the Webwright Python runtime, stock/raw/in-app Browser, `browser_agent`, `node_repl`, computer-use, Playwright MCP, raw Playwright, `bunx`, `npx`, direct package invocations, alternate CDP endpoints, alternate browser executables, alternate browser configs, or any fallback. No fallback is allowed.

This skill name is retained only for routing compatibility. Execute long-horizon search, comparison, extraction, export, and repeatable workflows stepwise through the health-gated exact managed Playwright CLI. Use the health-gated approved Chrome DevTools MCP transport only for specialist diagnostics. Never install, import, or execute `webwright` Python code.

Expected outputs:

- A bounded plan for the requested steps.
- Exact managed-provider actions and emitted evidence paths.
- A reproducible command transcript that preserves the mandatory health check before each browser action.
- `NOT_PROVEN` for any state the managed boundary cannot verify.
