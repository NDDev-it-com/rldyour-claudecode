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

Decision tree:

1. If the user asks for a long-horizon web task, extraction, comparison, booking/search flow, export, or reusable script, use Webwright.
2. If the user asks to validate UI, reproduce clicks/forms, capture screenshots, compare Figma/photo/screenshot, or prove final UI state, use Playwright CLI.
3. If the user asks for console, network, runtime exception, computed style, layout debug, Lighthouse, performance, memory, or live Chrome inspection, use Chrome DevTools MCP.
4. If the browser issue is unknown, reproduce with Playwright CLI first, then diagnose with Chrome DevTools MCP when runtime evidence is relevant.
5. Never use Webwright as a DevTools replacement.
6. Never use a browser-control MCP surface for Playwright; the approved provider is Playwright CLI.

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
