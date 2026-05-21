<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 84c28c2 fix(bootstrap): resolve git paths in submodules
Scope: plugins/rldyour-design/skills/ry-design/SKILL.md, plugins/rldyour-design/skills/figma-to-code/SKILL.md, plugins/rldyour-design/skills/design-system-implementation/SKILL.md, plugins/rldyour-design/skills/fsd-frontend-architecture/SKILL.md, plugins/rldyour-design/skills/design-validation/SKILL.md, plugins/rldyour-design/commands/ry-design.md, plugins/rldyour-mcps/.mcp.json (figma + shadcn entries)
Area: DESIGN
-->

# DESIGN-01-WORKFLOW

## Purpose

End-to-end design implementation workflow for `rldyour-design`: Figma source of truth → centralized tokens → strict Feature-Sliced Design placement → shadcn/ui primitives → ReactBits (purposeful motion only) → browser validation. Quality-first contract ([[PHILOSOPHY-01-QUALITY-FIRST]]): no pixel-perfect claim without browser evidence; no hardcoded values when tokens should exist; no Figma code paste without architecture cleanup.

`rldyour-design` is **skills-only** (5 skills + 1 slash command, 0 agents, 0 hooks). MCP transport from `rldyour-mcps`. Plugin dependencies: `rldyour-mcps` + `rldyour-browser` (for validation routing).

## Source Of Truth

- `plugins/rldyour-design/skills/ry-design/SKILL.md`: end-to-end orchestration skill (slash-only via `/rldyour-design:ry-design`).
- `plugins/rldyour-design/skills/figma-to-code/SKILL.md`: Figma handoff to production code.
- `plugins/rldyour-design/skills/design-system-implementation/SKILL.md`: W3C DTCG 2025.10 tokens + Tailwind v4 CSS-vars + shadcn/ui + ReactBits.
- `plugins/rldyour-design/skills/fsd-frontend-architecture/SKILL.md`: strict FSD layers + import rule + public APIs.
- `plugins/rldyour-design/skills/design-validation/SKILL.md`: browser-validation handoff (delegates to `rldyour-browser`).
- `plugins/rldyour-design/commands/ry-design.md`: slash command entry point.
- `plugins/rldyour-mcps/.mcp.json`:
  - `figma`: HTTP `https://mcp.figma.com/mcp` (design source of truth).
  - `shadcn`: `bunx shadcn@4.7.0 mcp` (registry primitives).

## End-to-End Workflow (`ry-design` orchestration)

1. **Scope**: establish target page/component, Figma source, required states, responsive frames, business behavior, acceptance criteria.
2. **Figma context** (`figma-to-code` skill): read selected frame/component via Figma MCP (`mcp__plugin_rldyour-mcps_figma__*`). Extract layout, spacing, typography, colors, radii, shadows, assets, variants, states, breakpoints, interaction notes. **Figma MCP is the source of truth, not generated code paste**.
3. **Tokens** (`design-system-implementation` skill): map Figma variables/styles to centralized tokens **before** scattering raw values. Use W3C DTCG 2025.10 format for vendor-neutral exchange; Tailwind CSS v4 `@theme` directive for CSS-vars-first delivery.
4. **FSD placement** (`fsd-frontend-architecture` skill): decide layer **before** writing code:
   - `app` (routing/providers/root layouts/global styles)
   - `pages` (route-level screens)
   - `widgets` (large self-contained UI blocks combining features/entities/shared)
   - `features` (user actions providing business value)
   - `entities` (domain entities + UI/model/api)
   - `shared` (reusable UI primitives, assets, tokens, config, libs without business logic)
5. **Implementation**: use shadcn/ui MCP (`mcp__plugin_rldyour-mcps_shadcn__*`) for primitives + registry blocks. Use ReactBits.dev **only** for purposeful motion / interactive effects. Use Serena-first inspection (`get_symbols_overview` → `find_symbol` → `find_referencing_symbols`).
6. **Validation** (`design-validation` → delegates to `rldyour-browser`): pixel-perfect + functional + business + runtime + accessibility + responsive checks. Browser evidence under `browser/` ([[BROWSER-01-WORKFLOW]] Artifact Rule).
7. **Iteration**: fix mismatches → revalidate → done when correct or blocker explicit.
8. **Memory sync**: if durable architecture/design-system facts were created, route through `serena-memory-sync` or `flow-memory-sync` ([[SERENA-01-MEMORY-SYNC]]).

## Token System Categories

All of these must have centralized tokens when used (no raw values scattered):

| Category | Examples |
|---|---|
| Color | primitive palette, semantic colors, text/background/border/surface, state, brand, destructive, success, warning, info |
| Typography | font families, sizes, line heights, weights, letter spacing, headings, body, captions, buttons |
| Spacing | scale, layout gaps, section spacing, component padding, density |
| Radius | base radius, component radius, pill/full radius |
| Shadow/elevation | shadow levels, overlays, popovers, dialogs, focus rings |
| Border | widths, styles, semantic border colors |
| Layout | containers, max widths, columns, gutters, page padding |
| Breakpoints | responsive thresholds and naming |
| Z-index | dropdowns, sticky bars, modals, toasts, tooltips |
| Motion | duration, easing, delay, stagger, reduced-motion behavior |
| Opacity/blur | overlays, disabled states, glass effects |
| Component states | hover, focus, active, disabled, selected, loading, error |

Color space: prefer **OKLCH** when supported (perceptually consistent).

## Format Standards (May 2026)

- **W3C Design Tokens Format Module 2025.10** - first stable vendor-neutral exchange format. Use for cross-tool JSON.
- **Tailwind CSS v4** - current production standard: CSS-first via `@theme` directive, all tokens exposed as native CSS variables, theme switching at selector level without rebuild, OKLCH support.
- **Style Dictionary** - typical pipeline if project ships tokens to multiple platforms.

## FSD Placement Defaults

| What | Where |
|---|---|
| Design tokens | `shared/config/theme` or existing centralized theme location |
| shadcn primitives | `shared/ui` |
| ReactBits primitives/effects (generic) | `shared/ui` |
| ReactBits effects (specific) | owning widget/feature |
| Reusable icons/assets | `shared/assets` |
| Domain-specific assets | owning entity/feature/widget/page slice |
| Page-specific layout | `pages/<page>/ui` |
| Large reusable page sections | `widgets/<widget>/ui` |
| User actions | `features/<feature>/{ui,model,api}` |
| Domain UI/data | `entities/<entity>/{ui,model,api}` |

## Import Rule (strict FSD)

Files import only from lower layers:

- `app` → all lower layers
- `pages` → `widgets, features, entities, shared`
- `widgets` → `features, entities, shared`
- `features` → `entities, shared`
- `entities` → `shared`
- `shared` → internal shared segments or external libraries only

**Same-layer slices must not import each other's internals. Use public APIs (`index.ts`).**

- Good: `import { UserCard } from "@/entities/user"`.
- Bad: `import { UserCard } from "@/entities/user/ui/UserCard"`.

The deprecated `processes` layer is **forbidden** - route responsibilities into `app`/`pages`/`widgets`.

## Pixel-Perfect Requirements

Match against Figma source:

- **Layout**: frame size, grid, alignment, spacing, containers, breakpoints, overflow, scroll.
- **Typography**: font family, size, line height, weight, letter spacing, transform, truncation, responsive scaling.
- **Visual tokens**: colors, opacity, gradients, borders, radius, shadows, blur, z-index, elevation.
- **Assets**: icons, images, illustrations, masks, aspect ratios, object fit, export quality.
- **States**: hover, focus, active, disabled, selected, loading, error, empty, modal, drawer, validation.
- **Interactions**: navigation, transitions, motion, form behavior, dialogs, menus, designer-specified behavior.

Extract real assets from Figma when available. **Never use placeholders if Figma assets are available**. If asset can't be extracted, mark as blocker.

## shadcn/ui Rules

- Search/browse existing registry items before writing common primitives from scratch (`mcp__plugin_rldyour-mcps_shadcn__*`).
- Install only components/blocks needed for the task.
- Keep shadcn primitives in `shared/ui` (or existing project-specific UI-kit location).
- Adapt generated components to centralized tokens.
- Do not keep unused variants, demo-only code, or registry leftovers.
- Preserve accessibility behaviour from shadcn primitives.

## ReactBits Rules

- Use **only** for purposeful motion and interactive effects matching the design.
- Prefer TypeScript + Tailwind variants when project uses both.
- Prefer shadcn-compatible install URLs; fallback to manually adapting source.
- Inspect dependencies before adding (no heavy deps for minor effects).
- Normalize styling to project tokens + FSD placement.
- Respect reduced-motion users + performance budgets.
- **Never** treat ReactBits as a parallel design system - it's a source component library, not project source of truth.

## Generated Code Cleanup

Before committing Figma/shadcn/ReactBits generated or copied code:

1. Remove demo-only code, unused props, unused variants, placeholder assets, unrelated styles.
2. Replace raw design values with centralized tokens.
3. Split code into FSD-appropriate slices and segments.
4. Add or update public APIs (`index.ts`).
5. Preserve existing project conventions.
6. Validate in browser.

## Invariants

- `rldyour-design` plugin: skills-only (5 skills + 1 slash command, 0 agents, 0 hooks). Dependencies: `rldyour-mcps` + `rldyour-browser`.
- Figma MCP is design source of truth; generated code is starting material, not final code.
- Centralized design-system first (tokens before scattering raw values).
- Strict FSD (no `processes` layer, no cross-slice internals, public APIs required).
- shadcn/ui = primary UI primitive source; ReactBits = purposeful motion only.
- Browser validation = mandatory for meaningful frontend work ([[BROWSER-01-WORKFLOW]]).
- Browser artifacts under `browser/`, never committed.
- Do not break business logic to match visuals.

## Change Rules

- New design skill: Russian-leading description ([[PATTERNS-01-CANONICAL]]).
- Bump Figma MCP / shadcn MCP version: update `plugins/rldyour-mcps/.mcp.json` + `config/mcp-runtime-versions.env` + run `bash scripts/smoke_mcp_capabilities.sh --server <name>`.
- Update design tokens: prefer extending existing convention over creating parallel system.
- New FSD layer or deviation from default: requires ADR ([[RULES-01-POLICY]] `architecture-boundaries`).

## Verification

- `bash scripts/smoke_mcp_capabilities.sh --server figma`: proves Figma MCP responds (session-based - may SKIP if not authenticated).
- `bash scripts/smoke_mcp_capabilities.sh --server shadcn`: proves shadcn MCP initializes.
- Browser validation evidence in `browser/` (per [[BROWSER-01-WORKFLOW]] Artifact Rule).
- Visual comparison against Figma source frame (Figma MCP `get_screenshot`).
- Reviewer subagents: `flow-architecture-review` (FSD placement), `flow-quality-review` (correctness), `flow-consistency-review` (token usage uniformity), `flow-verification-review` (browser evidence).

## Cross-References

- Browser validation delegate: [[BROWSER-01-WORKFLOW]].
- FSD layer policy: [[RULES-01-POLICY]] `architecture-boundaries` skill.
- Quality-first verification gates: [[PHILOSOPHY-01-QUALITY-FIRST]] + [[RULES-01-POLICY]] `verification-quality-gates`.
- MCP transport for figma/shadcn/playwright/chrome-devtools: [[MCP-01-TRANSPORT]].
- Canonical agent/skill frontmatter pattern: [[PATTERNS-01-CANONICAL]].
