<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: 0ff613d chore(release): cut 0.2.2 (wave-2 reviewer transport hardening)
Scope: plugins/rldyour-browser/skills/browser-tool-routing/SKILL.md, plugins/rldyour-browser/skills/browser-validation/SKILL.md, plugins/rldyour-browser/skills/browser-debug/SKILL.md, plugins/rldyour-mcps/.mcp.json (playwright + chrome-devtools entries)
Area: BROWSER
-->

# BROWSER-01-WORKFLOW

## Purpose

Browser-domain workflow contract for `rldyour-browser`. Two complementary MCP servers — Playwright MCP and Chrome DevTools MCP — cover the entire browser-automation surface; this memory documents when to use which and how to produce browser evidence that is acceptable to the quality-first policy ([[PHILOSOPHY-01-QUALITY-FIRST]] "no fake green checks").

`rldyour-browser` is **skills-only** (no agents, no hooks, no slash commands). MCP transport comes from `rldyour-mcps`. Plugin depends only on `rldyour-mcps`.

## Source Of Truth

- `plugins/rldyour-browser/skills/browser-tool-routing/SKILL.md`: Playwright vs Chrome DevTools decision tree.
- `plugins/rldyour-browser/skills/browser-validation/SKILL.md`: Playwright workflow for UI/functional/business-logic proof.
- `plugins/rldyour-browser/skills/browser-debug/SKILL.md`: Chrome DevTools workflow for diagnosis (console/network/runtime/layout/performance).
- `plugins/rldyour-mcps/.mcp.json`:
  - `playwright`: `bunx @playwright/mcp@0.0.75 --headless --caps=network,storage,testing,devtools`
  - `chrome-devtools`: `bunx chrome-devtools-mcp@0.26.0 --headless --isolated --no-usage-statistics --no-performance-crux`

## Tool Routing Decision Tree

| Task type | Primary MCP | Reason |
|---|---|---|
| User flow reproduction (navigate, forms, clicks, keyboard, dialogs, tabs, uploads, waits) | Playwright | Designed for interaction; accessibility-tree based |
| Functional validation (feature behaviour, business rules, route transitions, error states) | Playwright | Assertions + visible state checks |
| Pixel-perfect / responsive checks (screenshots, viewport sizing, visual comparison) | Playwright | `browser_take_screenshot`, viewport emulation |
| Accessibility-tree interaction & assertions | Playwright | Built-in accessibility snapshot |
| Final re-validation after code changes | Playwright | Deterministic flow re-run |
| Console errors / warnings / runtime exceptions | Chrome DevTools | `list_console_messages`, source maps |
| Network failures / status codes / payload / timing / CORS / cache | Chrome DevTools | `list_network_requests`, `get_network_request` |
| DOM / runtime debugging when accessibility snapshot is insufficient | Chrome DevTools | `evaluate_script`, DOM-level access |
| Layout / computed style / responsive breakage diagnosis | Chrome DevTools | Computed-style inspection |
| Lighthouse / Core Web Vitals / performance trace | Chrome DevTools | `lighthouse_audit`, `performance_start_trace` |
| Memory snapshots / leak diagnosis | Chrome DevTools | `take_memory_snapshot` |
| Browser bug with unknown cause | **Both** | Playwright reproduces, Chrome DevTools explains |
| Fix needing validation + console/network/perf evidence | **Both** | Coverage of both behaviour and diagnosis layers |

## Canonical Workflow

### Validation (Playwright)
1. Start from clean or explicit test state (`browser_navigate` with fresh context).
2. Navigate to changed page/flow.
3. `browser_snapshot` — accessibility snapshot to understand page structure.
4. Exercise main user flow + changed edge cases (click/fill/select_option/press_key).
5. Capture screenshots into `browser/` for key states: initial, changed, error, empty, loading, desktop, mobile, final.
6. Use testing-capability assertions (`browser_verify_element_visible`, `browser_verify_text_visible`, `browser_verify_list_visible`, `browser_verify_value`) for explicit checks.
7. Re-run after fixes.
8. Delete transient `browser/` artifacts unless user asks to keep.

### Debug (Chrome DevTools, after Playwright reproduction)
1. Reproduce with Playwright when possible (navigate, perform minimal failing flow, screenshot + snapshot).
2. Inspect with Chrome DevTools:
   - `list_console_messages` for errors/warnings/stack traces.
   - `list_network_requests` + `get_network_request` for failures, status, payload, CORS, redirects.
   - `evaluate_script` for DOM/runtime state inspection.
   - `lighthouse_audit` for Core Web Vitals.
   - `performance_start_trace` + `performance_analyze_insight` for runtime profiling.
3. Classify failure: code bug, data/API issue, config issue, environment issue, flaky timing, browser compatibility, design mismatch, or test expectation issue.
4. Trace to source files with Serena (`get_symbols_overview` → `find_symbol` → `find_referencing_symbols`).
5. Implement smallest correct fix.
6. Re-run Playwright validation for the affected flow.
7. Re-check Chrome DevTools evidence if issue involved console/network/runtime/layout/performance.
8. Clean `browser/` artifacts.

## Artifact Rule

All browser MCP outputs (screenshots, snapshots, traces, videos, PDFs, HAR-like exports) go to `browser/` (gitignored). Use descriptive names:

- `browser/<feature>-desktop-before.png`
- `browser/<feature>-desktop-after.png`
- `browser/<feature>-mobile.png`
- `browser/<feature>-error-state.png`
- `browser/<feature>-figma-reference.png`
- `browser/<feature>-trace.zip`

**Never commit browser artifacts.** Delete after task unless user explicitly asks to keep. If evidence must persist, prefer text summary with paths and observations over binary commits.

## Pixel-Perfect Standard (validation skill)

Do not declare UI done if:

- Important content overflows, clips, jumps, or is misaligned.
- Mobile layout is broken for a changed responsive surface.
- Loading / error / empty / disabled / hover / focus / modal states are visibly inconsistent when they are part of the feature.
- Typography, spacing, contrast are visibly inconsistent with the local design language.
- Page works only by accident because a business rule or state transition was not tested.

Compare against design reference when one exists; against existing product style and nearby components otherwise.

## Safety Boundary

- Local / test / staging / clearly-non-destructive environments: agent decides interactions freely.
- Production / payments / account settings / data deletion / credential changes / irreversible submissions / external sites with real-world side effects: follow Claude Code safety + confirmation rules.
- Never store real credentials or sensitive session state in repository. Use test accounts or user-provided temporary credentials only when needed.

## Invariants

- `rldyour-browser` is skills-only (3 skills, 0 agents, 0 hooks, 0 commands). Transport from `rldyour-mcps`. Plugin dependency: `rldyour-mcps` only.
- Browser validation is **mandatory** for any meaningful frontend change ([[PHILOSOPHY-01-QUALITY-FIRST]] verification gate). Do not call UI done without browser evidence or an explicit blocker.
- Console / network errors during validation must be treated as signal — hand off to `browser-debug`.
- Real production interactions require explicit user confirmation.
- All artifacts under `browser/`, never committed.

## Change Rules

- Adding a new browser skill: must follow Russian-leading description ([[PATTERNS-01-CANONICAL]] Frontmatter rules).
- Adding a new browser MCP server: update `plugins/rldyour-mcps/.mcp.json` (only that plugin owns transport) and pin via `config/mcp-runtime-versions.env`.
- Bumping Playwright or Chrome DevTools MCP version: update `.mcp.json` pin, `config/mcp-runtime-versions.env`, run `bash scripts/smoke_mcp_capabilities.sh --server <name>`, verify tool surface unchanged.

## Verification

- `bash scripts/smoke_mcp_capabilities.sh --server playwright`: proves Playwright MCP initializes and lists tools.
- `bash scripts/smoke_mcp_capabilities.sh --server chrome-devtools`: same for Chrome DevTools.
- `python3 scripts/check_mcp_runtime_versions.py`: proves `.mcp.json` ↔ `config/mcp-runtime-versions.env` pin parity for both.

## Cross-References

- Design implementation uses browser validation: [[DESIGN-01-WORKFLOW]] (skill `design-validation` delegates here).
- Quality-first verification gates: [[PHILOSOPHY-01-QUALITY-FIRST]] "No Fake Green" + [[RULES-01-POLICY]] `verification-quality-gates`.
- MCP transport for Playwright/Chrome DevTools: [[MCP-01-TRANSPORT]].
- Canonical agent/skill frontmatter pattern: [[PATTERNS-01-CANONICAL]].
