---
name: browser-validation
description: "Валидация UI и пользовательских сценариев через управляемый Playwright CLI. Используй для: проверь UI, проверь в браузере, визуально, скриншот, регрессия, адаптив, бизнес-логика. EN triggers: validate UI, browser check, regression, responsive, business logic, screenshot."
allowed-tools:
  - Bash
  - mcp__plugin_rldyour-mcps_chrome-devtools__*
---

# Browser Validation

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

1. Choose a named session and run the mandatory health command.
2. Open the target through the exact managed CLI and exercise navigation, forms, buttons, dialogs, tabs, loading/error/empty states, responsive behavior, and business rules.
3. Rerun the health command immediately before every subsequent browser action.
4. Capture CLI-emitted snapshot, screenshot, trace, console, and request evidence without using custom filename flags.
5. For deep diagnosis, rerun health and use only the approved managed Chrome DevTools MCP transport.
6. Repeat the same health-gated actions after fixes.

```bash
$HOME/.local/bin/cloakbrowser-cdp-health
PLAYWRIGHT_CLI_SESSION="${RY_PROJECT_SLUG:-rldyour}" $HOME/.local/bin/playwright-cli open "$URL"
$HOME/.local/bin/cloakbrowser-cdp-health
$HOME/.local/bin/playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" snapshot
$HOME/.local/bin/cloakbrowser-cdp-health
$HOME/.local/bin/playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" screenshot
```

Report the exact emitted evidence paths and residual risk. If any required action cannot run inside this boundary, report `NOT_PROVEN`.
