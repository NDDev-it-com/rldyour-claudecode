---
name: ry-design
description: "Сквозной дизайн-воркфлоу: Figma → код → токены → FSD → shadcn/ui → ReactBits → browser validation. Используй для: /rldyour-design:ry-design, сделай дизайн, реализуй UI, сверстай страницу, перенеси Figma макет, лендинг, дашборд, редизайн. EN triggers: end-to-end design, build UI, ship landing page, ship dashboard, redesign feature, production-ready UI, pixel-perfect implementation, design workflow."
allowed-tools:
  - mcp__plugin_rldyour-mcps_figma__*
  - mcp__plugin_rldyour-mcps_shadcn__*
  - mcp__plugin_rldyour-mcps_playwright__*
  - mcp__plugin_rldyour-mcps_chrome-devtools__*
  - mcp__plugin_rldyour-mcps_serena__*
  - Read
  - Write
  - Edit
  - Bash
---

# ry-design

## Purpose

Run the full rldyour design implementation workflow from source design to browser-validated code.

User-facing communication stays in Russian unless requested otherwise. Code, docs, tokens, comments, and commits stay in English.

## When To Use

Use this skill without waiting for explicit invocation when the user asks for an end-to-end design result rather than a narrow subtask:

- Implement a Figma design, designer mockup, page, component, landing, dashboard, widget, feature UI, or redesign.
- Create UI that requires tokens, architecture placement, shadcn/ui or ReactBits components, and browser validation.
- Make frontend design work "pixel-perfect", "production-ready", "according to design", or visually and functionally complete.
- Coordinate multiple design skills in one task.

For very narrow tasks, prefer the matching subskill directly. Use `design-validation` after any meaningful visible implementation even when `/ry-design` is not selected.

## Workflow

1. Establish scope: target page/component, Figma source, required states, responsive frames, business behavior, and acceptance criteria.
2. Use `figma-to-code` if Figma context exists. Figma MCP (`mcp__plugin_rldyour-mcps_figma__*`) is the design source of truth.
3. Use `design-system-implementation` to create or update centralized tokens before scattering raw design values.
4. Use `fsd-frontend-architecture` to place code into strict FSD layers and public APIs.
5. Use shadcn/ui MCP (`mcp__plugin_rldyour-mcps_shadcn__*`) for primitives, blocks, and registry-based components.
6. Use ReactBits.dev only for purposeful motion or interactive effects that match the design.
7. Implement code with Serena-first local code inspection when available (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`).
8. Use `design-validation` and `rldyour-browser` to verify pixel-perfect layout, functionality, business logic, accessibility, desktop/mobile, screenshots, and runtime health.
9. Fix mismatches and revalidate until the result is correct or the blocker is explicit.
10. If durable architecture/design-system facts were created, update Serena memories through `serena-memory-sync`.

## Rules

- Centralized design system first: tokens, theme, primitives, variants, and shared assets must have a single source of truth.
- Figma context is source material, not copy-paste code. Adapt to architecture and existing project conventions.
- Strict FSD by default: no deprecated `processes`, no cross-slice internals, public APIs required.
- shadcn/ui is the primary UI primitive source.
- ReactBits is for controlled motion and standout interactive details, not broad architecture.
- Browser validation is mandatory for meaningful frontend design work.
- Browser artifacts go under `browser/` and are not committed.
- Do not use placeholders when real Figma assets are available.
- Do not break business logic to match visuals.

## Output

For a completed design task, answer in Russian with:

- `Scope`: design/page/component implemented.
- `Figma`: source frame/context and assets used.
- `Design system`: tokens/components/assets changed.
- `FSD`: placement decisions and public APIs.
- `Validation`: browser screenshots/checks and cleanup status.
- `Residual gaps`: any unresolved visual, asset, responsive, runtime, or business-logic gaps.

## Anti-patterns

- Делать дизайн "почти готов" без browser-validation evidence.
- Раскидывать raw color/spacing/typography values вместо токенов.
- Pasting generated Figma/shadcn/ReactBits code as-is без FSD адаптации.
- Использовать ReactBits для broad architecture вместо точечных motion-эффектов.
- Использовать deprecated FSD `processes` слой.
- Ломать business-logic ради визуального match'а.
