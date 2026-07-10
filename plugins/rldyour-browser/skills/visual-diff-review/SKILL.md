---
name: visual-diff-review
description: "Проводит visual QA для Figma, screenshots и reference images через управляемые browser providers. Используй для: pixel-perfect, сравни с Figma, сравни с фото, diff. EN triggers: visual diff, pixel-perfect, compare Figma, reference image."
allowed-tools:
  - Bash
  - mcp__plugin_rldyour-mcps_chrome-devtools__*
---

# Visual Diff Review

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

Required evidence:

- A reference source: Figma frame export, user-provided image, screenshot, or accepted product reference.
- An actual screenshot captured after a successful health check through the exact managed CLI.
- A diff or measured element-level deviation report.
- Responsive viewport evidence when layout is responsive.
- Health-gated managed Chrome DevTools MCP diagnosis when computed layout, network, runtime, performance, or memory explains a deviation.

If the managed providers cannot prove a required state, report `NOT_PROVEN`.
