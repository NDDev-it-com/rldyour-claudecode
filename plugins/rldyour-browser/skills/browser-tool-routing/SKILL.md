---
name: browser-tool-routing
description: "Маршрутизация браузерных задач: Playwright vs Chrome DevTools vs оба. Используй для: выбор браузерного MCP, проверь в браузере, скриншот vs дебаг, validation vs diagnosis, какой инструмент запустить, что использовать для UI."
---

# Browser Tool Routing

## Purpose

Choose the right browser MCP workflow before acting. Playwright MCP and Chrome DevTools MCP overlap, but they are not interchangeable.

User-facing conversation stays in Russian unless requested otherwise. Repository documentation and committed files stay in English.

## When To Use

Use this skill without waiting for explicit invocation when the task asks to:

- Check or verify something in a browser, visually, interactively, functionally, or pixel-perfect.
- Decide whether Playwright, Chrome DevTools, or both should be used.
- Capture screenshots, inspect rendered UI, validate responsive behavior, or test a browser user flow.
- Debug console errors, network failures, runtime exceptions, hydration, layout, performance, or Lighthouse issues.
- Provide browser evidence before final delivery.

For implementation tasks, after routing select the concrete skill: `browser-validation` for proof and `browser-debug` for diagnosis.

## Default Routing

Use Playwright MCP first (`mcp__playwright__*`) for:

- User-flow reproduction: navigation, forms, clicks, keyboard, dialogs, tabs, uploads, waits.
- Functional validation: feature behavior, business rules, form values, visible state, route transitions, error states.
- Pixel-perfect checks: screenshots, responsive viewport checks, visual comparison against provided design/context.
- Accessibility-tree based interaction and assertions.
- Storage/network/testing workflows enabled through `--caps=network,storage,testing,devtools`.
- Final re-validation after code changes.

Use Chrome DevTools MCP first (`mcp__chrome-devtools__*`) for:

- Console errors, warnings, thrown exceptions, source maps, runtime stack traces.
- Network diagnosis: failing requests, status codes, payload shapes, timing, caching, CORS, redirects.
- DOM/runtime debugging when accessibility snapshots are insufficient.
- Layout/computed style investigation, rendering issues, hydration/runtime behavior.
- Lighthouse, Core Web Vitals, performance trace, CPU/network throttling, and memory snapshots.

Use both when:

- The task says the UI is broken but the cause is unknown.
- Playwright can reproduce the issue and Chrome DevTools can explain it.
- A fix requires browser validation plus console/network/performance evidence.
- The task requires pixel-perfect confidence and runtime correctness.

## Recommended Sequence

For unknown browser bugs:

1. Playwright: navigate, reproduce, take screenshot into `browser/`, capture accessibility snapshot.
2. Chrome DevTools: inspect console, network, DOM/runtime, layout, and performance only as needed.
3. Implement the fix using repo-native tools (Edit/Write or Serena symbol editing).
4. Playwright: re-run the user flow and assertions.
5. Chrome DevTools: confirm console/network/performance regressions are absent when relevant.

For planned UI implementation:

1. Implement the UI.
2. Playwright: check desktop and mobile viewports, business flow, interaction states, screenshots, and visible assertions.
3. Chrome DevTools: inspect console/network if UI uses client runtime, external data, hydration, or performance-sensitive rendering.
4. Report evidence and residual risks.

## Artifact Rule

All browser MCP screenshots, videos, traces, PDFs, HAR-like exports, and temporary browser evidence must be written under `browser/`.

Do not commit browser artifacts. Delete them after the task unless the user explicitly asks to preserve evidence. If evidence must be kept, prefer a text summary with paths and observations over committing binary files.

## Safety Boundary

The agent may decide how to interact with browser flows when the environment is local, test, staging, or clearly non-destructive. For production, payments, account settings, data deletion, credential changes, irreversible submissions, or external sites with real-world side effects, follow Claude Code safety and confirmation rules.

Do not store real credentials or sensitive session state in the repository. Use test accounts or user-provided temporary credentials only when needed.

## Output

When routing is the main task, answer in Russian with:

- `Chosen workflow`: Playwright, Chrome DevTools, or both.
- `Why`: concrete reason based on the task.
- `Evidence to collect`: screenshots, snapshots, console, network, trace, Lighthouse, or manual checks.
- `Risks`: side effects, auth/session needs, unavailable browser context, or production safety concerns.

## Anti-patterns

- Использовать Chrome DevTools для simple validation когда Playwright достаточен.
- Запускать Playwright для console/network debug без воспроизведения user flow.
- Использовать оба МCP когда задача чисто validation OR чисто debug.
- Запускать на production / live site без явного разрешения.
- Игнорировать accessibility snapshot — это часто быстрее DOM inspection.
