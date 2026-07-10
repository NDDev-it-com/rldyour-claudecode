---
name: browser-debug
description: "Отлаживает browser-only failures через управляемые Chrome DevTools MCP и Playwright CLI. Используй для: консоль, сеть, runtime, hydration, layout, memory, performance, Lighthouse. EN triggers: browser debug, console errors, network, runtime, layout, memory, performance, Lighthouse."
allowed-tools:
  - Bash
  - mcp__plugin_rldyour-mcps_chrome-devtools__*
---

# Browser Debug

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

## Workflow

1. Run the mandatory health command, then reproduce with the exact managed Playwright CLI when deterministic flow evidence or a screenshot is needed.
2. Before every Chrome DevTools MCP action, rerun the mandatory health command. Use only the adapter-configured managed transport for console, network, DOM/runtime, computed layout, performance, Lighthouse, and memory evidence.
3. Fix the root cause in code or configuration.
4. Revalidate through the same health-gated managed providers and report exact evidence or `NOT_PROVEN`.
