---
name: browser-tool-routing
description: "Маршрутизирует browser tasks только через управляемые Playwright CLI и Chrome DevTools MCP. Используй для: проверь в браузере, UI, визуально, скриншот, Figma, консоль, сеть, перфоманс. EN triggers: browser routing, UI validation, screenshots, visual QA, console, network, performance."
allowed-tools:
  - Bash
  - mcp__plugin_rldyour-mcps_chrome-devtools__*
---

# Browser Tool Routing

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

## Routing

- Use the health-gated exact managed Playwright CLI for navigation, state transitions, screenshots, snapshots, traces, responsive matrices, visual evidence, and long-horizon stepwise workflows.
- Use the health-gated approved Chrome DevTools MCP transport for console, network, runtime, DOM/layout, performance, Lighthouse, memory, and live DevTools inspection.
- `webwright-task` is a compatibility workflow name. Route it to these same two managed providers; it never authorizes the Webwright runtime.
- For unknown defects, reproduce with the managed CLI and add managed DevTools evidence only when needed.
