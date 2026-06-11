# rldyour-design

End-to-end design workflows: Figma → tokens → FSD → shadcn/ui → ReactBits → browser validation. Skills-only consumer of MCP transport.

## What's inside

- `5` skills:
  - `figma-to-code` - pixel-perfect Figma frame transfer with Figma/shadcn MCP, Playwright CLI browser evidence, Chrome DevTools MCP diagnosis, and Read/Write/Edit.
  - `design-system-implementation` - centralized tokens (W3C DTCG / Tailwind v4 CSS-vars), shadcn/ui, ReactBits.
  - `fsd-frontend-architecture` - strict Feature-Sliced Design layers, public APIs, import boundaries (pure reference skill - no `allowed-tools` by design).
  - `design-validation` - browser validation of design implementation (Playwright CLI + Chrome DevTools MCP).
  - `ry-design` - full pipeline orchestrator: `disable-model-invocation: false` (auto-trigger on "сверстай UI / реализуй дизайн / pixel-perfect").
- `1` slash command: `/rldyour-design:ry-design`.

## Pipeline stages

1. **Read Figma** via Figma MCP - `get_design_context` returns code + screenshot + hints (Code Connect mappings, design tokens, design annotations).
2. **Tokens** - map Figma variables to repo design tokens (CSS variables / Tailwind theme).
3. **FSD placement** - components by layer (`shared` → `entities` → `features` → `widgets` → `pages`). Strict public API only.
4. **shadcn/ui + ReactBits** - primitives via `shadcn` MCP.
5. **Browser validation** - Playwright CLI evidence plus Chrome DevTools MCP diagnosis for pixel-perfect/responsive/business-logic checks; screenshots under `browser/`. Use Webwright only for long-horizon reusable web tasks when design work includes end-to-end web exploration.

## Dependencies

`rldyour-mcps` provides Figma, shadcn, and Chrome DevTools MCP. Browser flow automation is delegated to `rldyour-browser` through Playwright CLI and Webwright according to browser-provider policy.
