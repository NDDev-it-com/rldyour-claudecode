# rldyour-browser

Browser workflows fail closed through CloakBrowser. Before every browser action,
run exact `$HOME/.local/bin/cloakbrowser-cdp-health`; missing or nonzero health
means stop and report `NOT_PROVEN`.

## Skills

- `browser-tool-routing`: choose the provider.
- `browser-validation`: UI and flow validation with Playwright CLI evidence.
- `playwright-cli-validation`: low-level screenshot, snapshot, trace, and headed-session workflow.
- `webwright-task`: compatibility route for long-horizon intent; it uses only the managed providers and never the Webwright runtime.
- `visual-diff-review`: Figma/photo/reference-image deviation workflow.
- `browser-debug`: Chrome DevTools MCP diagnosis for console, network, runtime, performance, memory, Lighthouse, and live Chrome inspection.

## Provider Roles

- Exact `$HOME/.local/bin/playwright-cli`: browser flow validation and evidence;
  `run-code` and `--filename` are forbidden.
- Exact managed Chrome DevTools MCP wrapper: DevTools, performance, memory,
  Lighthouse, network, console, and runtime diagnosis.

The Webwright Python runtime, stock/raw/in-app Browser, `browser_agent`,
`node_repl`, computer-use, Playwright MCP/raw Playwright, package runners,
alternate CDP/executable/config paths, and all fallbacks are forbidden.

Store temporary browser evidence under `browser/` and do not commit it.
