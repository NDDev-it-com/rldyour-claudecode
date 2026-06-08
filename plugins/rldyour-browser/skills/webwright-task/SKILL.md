---
name: webwright-task
description: "Запускает Webwright для длинных web tasks, RPA и воспроизводимых browser workflows. Используй для: найти, сравнить, выгрузить, повторить, reusable script. EN triggers: Webwright task, long-horizon web task, RPA, extraction, final_script.py."
---

# Webwright Task

Use Webwright for high-level long-horizon browser tasks and reusable workflows. The required install path is a pinned Webwright checkout from Microsoft GitHub, not a blind package-name install.

Expected outputs:

- `plan.md` for task intent and steps.
- Logs and screenshots for evidence-first progress.
- `final_script.py` as the rerunnable result when the task is reusable.
- A bounded `NOT_PROVEN` report if the pinned Webwright checkout or browser runtime is unavailable.

Use Playwright CLI only when low-level browser control or screenshots are needed. Use Chrome DevTools MCP only when runtime, network, performance, memory, or Lighthouse debugging is required.
