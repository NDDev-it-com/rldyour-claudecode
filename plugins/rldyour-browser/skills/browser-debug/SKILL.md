---
name: browser-debug
description: "Debug browser-only failures через Chrome DevTools MCP и Playwright CLI reproduction. Используй для: консоль, сеть, runtime, hydration, layout, memory, performance, Lighthouse. EN triggers: browser debug, console errors, network, runtime, layout, memory, performance, Lighthouse."
allowed-tools:
  - mcp__plugin_rldyour-mcps_chrome-devtools__*
---

# Browser Debug

## Purpose

Diagnose browser-only failures with runtime evidence. Chrome DevTools MCP is the primary provider for console/network/runtime/performance/memory/Lighthouse and live Chrome inspection. Webwright does not replace Chrome DevTools MCP.

## Workflow

1. Reproduce with Playwright CLI when a deterministic user flow or screenshot is needed.
2. Use Chrome DevTools MCP for DevTools evidence: console messages, network requests, DOM/runtime state, computed layout, performance traces, Lighthouse, and memory/heap diagnostics.
3. Fix the root cause in code/config.
4. Revalidate with Playwright CLI, then repeat Chrome DevTools MCP checks when the defect involved runtime, network, performance, or memory.

Do not route long-horizon web tasks to DevTools by default. Use Webwright for reusable multi-step web tasks and keep DevTools for diagnosis.
