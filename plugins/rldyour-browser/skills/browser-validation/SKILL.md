---
name: browser-validation
description: "Валидация UI и пользовательских сценариев в браузере через Playwright CLI evidence. Используй для: проверь UI, проверь в браузере, скриншот, регрессия, адаптив, бизнес-логика, визуально. EN triggers: validate UI, browser check, regression test, responsive check, business logic in browser, screenshot, visual QA."
---

# Browser Validation

## Purpose

Validate browser-facing work with repeatable evidence. Use Playwright CLI as the primary low-level provider for browser flow validation and screenshots. Store artifacts under `browser/` and do not commit them.

## Workflow

1. Pick a named session such as `PLAYWRIGHT_CLI_SESSION="${RY_PROJECT_SLUG:-rldyour}"`.
2. Open the target URL with `playwright-cli` and a deterministic viewport.
3. Capture a snapshot and screenshot under `browser/`.
4. Exercise the changed flow: navigation, forms, buttons, dialogs, modals, tabs, loading/error/empty states, and business rules.
5. Capture desktop and mobile screenshots when layout or responsive behavior changed.
6. Check console and requests with Playwright CLI for ordinary validation.
7. Hand off to `browser-debug` when console/network/runtime/performance/memory/Lighthouse diagnosis is required.
8. Re-run the same Playwright CLI commands after fixes.

Useful command shape:

```bash
PLAYWRIGHT_CLI_SESSION="${RY_PROJECT_SLUG:-rldyour}" playwright-cli open "$URL"
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" snapshot --filename browser/snapshot.yaml
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" screenshot --filename browser/ui-desktop.png
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" console error
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" requests
```

## Evidence Contract

Report the exact evidence paths and residual risk. A browser-visible change is not done until the relevant screenshot, snapshot, flow result, and runtime-health checks are proven or explicitly marked `NOT_PROVEN` with a bounded reason.
