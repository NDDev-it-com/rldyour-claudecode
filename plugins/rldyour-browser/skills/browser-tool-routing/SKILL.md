---
name: browser-tool-routing
description: "Маршрутизирует browser tasks между Webwright, Playwright CLI и Chrome DevTools MCP. Используй для: проверь в браузере, браузер, UI, визуально, скриншот, Figma, фото, консоль, сеть, перфоманс, Lighthouse. EN triggers: browser tool routing, UI validation, screenshots, visual QA, console, network, performance."
---

# Browser Tool Routing

## Purpose

Choose the browser provider before acting. The current provider model is:

- Webwright: high-level long-horizon web tasks, reusable scripts, RPA, extraction, comparison, and evidence-first workflows.
- Playwright CLI: low-level browser flow validation, deterministic screenshots, snapshots, headed sessions, traces, console/request checks, and final UI proof.
- Chrome DevTools MCP: console/network/runtime/performance/memory/Lighthouse debugging and live Chrome inspection.

RU triggers: проверь UI, проверь в браузере, визуально, pixel-perfect, сравни с Figma, сравни с фото, скриншот, консоль, сеть, перфоманс, Lighthouse.
EN triggers: validate UI, browser check, visual QA, pixel-perfect, compare with Figma, compare with reference image, screenshot, console, network, performance, Lighthouse.

## Routing

Use Webwright first for:

- Long-horizon web task execution: search, filter, compare, extract, upload, export, repeat.
- Reusable RPA or web workflow creation where `plan.md`, logs, screenshots, and `final_script.py` are expected.
- Multi-page evidence-first workflows where the result must be rerunnable.

Use Playwright CLI first for:

- Low-level browser flow validation, route navigation, forms, clicks, keyboard, dialogs, modals, tabs, uploads, waits, and state transitions.
- Screenshot capture under `browser/`, accessibility snapshots, responsive viewport matrices, traces, videos when needed, and post-fix revalidation.
- Figma/photo/reference-image visual QA when paired with `visual-diff-review`.

Use Chrome DevTools MCP first for:

- Console and source-map debugging, thrown exceptions, hydration/runtime failures, and DOM/runtime inspection.
- Network failures, request/response payloads, cache/CORS/redirect diagnosis, performance traces, Lighthouse, memory/heap diagnostics, and live Chrome inspection.

For unknown browser bugs, reproduce with Playwright CLI, then diagnose with Chrome DevTools MCP when runtime evidence is needed.
