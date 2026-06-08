---
name: visual-diff-review
description: "Проводит surgical visual QA для Figma, screenshots и reference images. Используй для: pixel-perfect, сравни с Figma, сравни с фото, diff, deviation report. EN triggers: visual diff, pixel-perfect, compare with Figma, compare with reference image."
---

# Visual Diff Review

Use this workflow when the user asks for pixel-perfect quality, Figma parity, screenshot comparison, or photo/reference-image comparison.

Required evidence:

- Reference source: Figma frame export, user-provided photo, screenshot, or accepted product reference.
- actual screenshot captured with Playwright CLI under `browser/`.
- Diff or measured deviation report with element-level issues.
- Responsive viewport evidence when layout is responsive.
- Chrome DevTools MCP diagnosis for computed styles, layout, network, runtime, performance, or memory when deviations require debugging.

Use Webwright only for multi-page or reusable visual workflows. Do not use it as the default pixel-diff engine.
