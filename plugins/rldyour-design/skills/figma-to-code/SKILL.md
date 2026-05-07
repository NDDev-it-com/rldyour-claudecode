---
name: figma-to-code
description: "Перенос Figma макетов в код pixel-perfect через Figma MCP, токены, FSD, shadcn/ui, ReactBits + browser-валидация. Используй для: перенеси из Figma, сверстай макет, реализуй frame, ссылка на Figma, design handoff."
---

# Figma To Code

## Purpose

Transfer designer-provided Figma layouts into production frontend code as accurately as possible while preserving architecture, design-system consistency, and runtime behavior.

User-facing conversation stays in Russian unless requested otherwise. Repository documentation, code comments, commit messages, and design-token files stay in English.

## When To Use

Use this skill without waiting for explicit invocation when the task is about:

- Implementing, copying, transferring, or recreating a Figma frame, component, layout, selection, or designer mockup.
- Matching a visual reference pixel-perfect or as close as possible in a browser.
- Extracting Figma variables, styles, components, assets, dimensions, or Code Connect hints into code.
- Turning design handoff material into React/frontend implementation.

Do not use it for design-system-only refactors that have no Figma source; use `design-system-implementation` instead.

## Source Of Truth

Figma MCP (`mcp__figma__*`) is the source of truth for:

- Selected frames, components, variants, variables, styles, layout data, dimensions, constraints, and assets.
- Figma screenshots or visual references used for pixel comparison.
- Code Connect hints when available; prefer connected project components over inventing new components.

If Figma MCP is unavailable, say so and use only explicitly provided fallback assets such as screenshots or specs. Do not pretend a design was inspected.

## Workflow

1. Read the Figma context for the selected frame/component through Figma MCP.
2. Capture or request a visual reference for pixel comparison when possible.
3. Extract design facts: layout grid, spacing, typography, colors, radii, shadows, assets, variants, states, breakpoints, and interaction notes.
4. Map Figma variables/styles to centralized design tokens before hardcoding values.
5. Inspect the existing codebase with Serena-first workflow to find architecture, existing design system, shadcn setup, and component placement.
6. Choose FSD placement before writing code: `shared`, `entities`, `features`, `widgets`, `pages`, or `app`.
7. Use shadcn/ui MCP (`mcp__shadcn__*`) for primitives and registry blocks when they fit the design.
8. Use ReactBits.dev only for purposeful animation or interactive effects that match the design and do not harm performance or accessibility.
9. Implement the design by adapting Figma context into project-native code. Do not paste generated code blindly.
10. Validate in browser through `browser-validation`: desktop, mobile, key states, screenshots under `browser/`, functional flow, and runtime health.
11. Iterate until the result is visually and functionally aligned, or report the exact blocker.

## Pixel-Perfect Requirements

Match:

- Layout: frame size, grid, alignment, spacing, containers, breakpoints, overflow, and scroll behavior.
- Typography: font family, size, line height, weight, letter spacing, text transform, truncation, and responsive scaling.
- Visual tokens: colors, opacity, gradients, borders, radius, shadows, blur, z-index, and elevation.
- Assets: icons, images, illustrations, masks, aspect ratios, object fit, and exported file quality.
- States: hover, focus, active, disabled, selected, loading, error, empty, modal, drawer, and validation states.
- Interactions: navigation, transitions, motion, form behavior, dialogs, menus, and any designer-specified behavior.

## Asset Rule

Extract or copy all required design assets when possible. Place reusable assets in the FSD-appropriate location, usually `shared/assets` or the owning slice when the asset is domain-specific.

Do not use placeholders if Figma assets are available. If an asset cannot be extracted, mark it as a blocker or unresolved gap.

## Output

For implementation work, report in Russian:

- `Figma scope`: inspected frame/component and source context.
- `Design system updates`: tokens/components/assets created or changed.
- `FSD placement`: where code was placed and why.
- `Browser validation`: screenshots/checks performed through `rldyour-browser`.
- `Mismatches fixed`: visual or functional gaps corrected.
- `Residual gaps`: missing assets, unavailable Figma context, unavailable credentials, or untested states.

## Anti-patterns

- Paste generated Figma code as-is без FSD-адаптации и tokenization.
- Использовать placeholder assets когда Figma source даёт реальные.
- Hardcode raw color/spacing values вместо semantic tokens.
- Пропустить mobile/responsive проверку при Figma frame с mobile variant.
- Объявить done без visual evidence из браузера.
