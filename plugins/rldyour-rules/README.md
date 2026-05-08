# rldyour-rules

Quality-first engineering rules. Every other plugin defers to these for hard policy.

## What's inside

- `7` skills:
  - `quality-first-engineering` — non-negotiable: no hacks, no fake green checks, no swallowed errors, no hidden technical debt.
  - `architecture-boundaries` — FSD/VSA/Hexagonal patterns, layer discipline, public APIs, import direction.
  - `implementation-discipline` — code, API, schemas, configs, tests, naming, error handling, reuse, integration sync.
  - `dependency-compatibility-policy` — latest-compatible, source-backed, SLSA Level 2, SBOM, lockfile discipline.
  - `verification-quality-gates` — quality gates before delivery: tests, lint (ruff/ESLint v9/Biome), types (pyright), LSP, browser/security/design.
  - `project-instructions-policy` — AGENTS.md, `.claude/CLAUDE.md`, REVIEW.md, MADR 4.0.0 ADR policy.
  - `ry-rules-review` — audit implementation against rldyour rules (**`disable-model-invocation: true`** — slash-only, audit operations are deliberate).
- `1` slash command: `/rldyour-rules:ry-rules-review`.
- `6` references: `quality-gates.md`, `architecture-policy.md`, `implementation-discipline.md` (implicit through skill body), `dependency-policy.md`, `project-instructions-and-adrs.md`, `rules-policy.md`, `sources.md`.

## Hard rules surfaced from this plugin

- **Quality-first**: code is the source of truth. No "looks fine" — proof via tests/types/LSP/browser/security evidence.
- **Plugin boundary discipline**: one domain per plugin, no catch-all, no overlap, no duplicate MCP transports.
- **Conventional Commits**: ≤72 char subjects, single-token scope, atomic per logical unit.
- **No secrets / runtime markers / browser artifacts** in commits.
- **All MCP server versions pinned** (stdio `==X.Y.Z`, HTTP by URL).

## Dependencies

`rldyour-mcps` (this plugin doesn't directly use MCP transport but inherits via the dependency graph).
