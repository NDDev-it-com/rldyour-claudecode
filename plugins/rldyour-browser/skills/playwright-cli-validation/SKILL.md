---
name: playwright-cli-validation
description: "Низкоуровневая browser automation через Playwright CLI. Используй для: screenshots, snapshots, headed sessions, traces, responsive, UI flow proof. EN triggers: Playwright CLI validation, screenshots, snapshots, headed browser, traces, responsive."
---

# Playwright CLI Validation

Use Playwright CLI for low-level browser control and deterministic UI evidence.

Required rules:

- Use named sessions with `PLAYWRIGHT_CLI_SESSION` or `playwright-cli -s=<session>`.
- Store screenshots, snapshots, traces, and temporary browser evidence under `browser/`.
- Capture before/after or state-specific screenshots when visual behavior changed.
- Use `playwright-cli show --annotate` for human-visible inspection in headed or cmux workflows when useful.
- Mark unavailable runtime as `NOT_PROVEN`; do not invent browser evidence.

Common commands:

```bash
playwright-cli --help
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" open "$URL"
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" snapshot --filename browser/snapshot.yaml
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" screenshot --filename browser/ui.png
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" tracing-start
playwright-cli -s="${RY_PROJECT_SLUG:-rldyour}" tracing-stop
```
