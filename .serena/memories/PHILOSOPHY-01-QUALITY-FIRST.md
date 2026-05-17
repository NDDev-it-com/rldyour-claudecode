<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: cc742d5 ci(release): restore fullrepo agent-only files before harness
Scope: plugins/rldyour-rules/skills/quality-first-engineering/SKILL.md, plugins/rldyour-rules/skills/architecture-boundaries/SKILL.md, plugins/rldyour-rules/skills/dependency-compatibility-policy/SKILL.md, plugins/rldyour-rules/skills/implementation-discipline/SKILL.md, plugins/rldyour-rules/skills/verification-quality-gates/SKILL.md, plugins/rldyour-rules/references/rules-policy.md, plugins/rldyour-rules/references/quality-gates.md
Area: PHILOSOPHY
-->

# PHILOSOPHY-01-QUALITY-FIRST

## Purpose

The development philosophy that every project consumed by this Claude Code marketplace must follow. The owner's explicit vision (recorded as a development style invariant for any future session, regardless of repository): **quality and easy scalability take priority over delivery speed**. Time is not the constraint. Correctness, consistency, long-term maintainability, and clean architecture are the constraints.

Use this memory as the **decision filter** when picking between approaches. If an option is faster but introduces a hack, technical debt, swallowed error, ambiguous naming, or speculative abstraction - reject it and pick the more durable alternative. If an option is slower but consistent with project patterns and free of debt - pick it.

## Source Of Truth

- `plugins/rldyour-rules/skills/quality-first-engineering/SKILL.md`: hard bans, semantic-entropy rules, scope policy, Conventional Commits v1.0.0 anchor.
- `plugins/rldyour-rules/skills/architecture-boundaries/SKILL.md`: May 2026 architecture defaults - FSD frontend, VSA + Hexagonal + Modular Monolith backend, MADR 4.0.0 ADRs.
- `plugins/rldyour-rules/skills/dependency-compatibility-policy/SKILL.md`: May 2026 supply-chain - SBOM (SPDX/CycloneDX), SLSA Level 2 minimum, Sigstore/cosign signing, OWASP A03 supply-chain top-tier concern, lockfile discipline.
- `plugins/rldyour-rules/skills/implementation-discipline/SKILL.md`: Serena-first inspection, integration tracing, atomic changes, no premature abstraction.
- `plugins/rldyour-rules/skills/verification-quality-gates/SKILL.md`: per-language May 2026 tooling defaults - pyright + ruff for Python, ESLint v9 / Biome for TS, Vitest for tests, no fake green checks.
- `plugins/rldyour-rules/references/rules-policy.md`: full policy text.
- `plugins/rldyour-rules/references/quality-gates.md`: full quality-gates checklist.

## Core Drivers (in order)

1. **Correctness** - the change does what it claims, verified by evidence, not confidence language.
2. **Consistency** - the change matches existing project patterns (naming, layering, error handling, contracts, public APIs). Drift is documented or rejected.
3. **Scalability** - the change does not block future growth: layer boundaries respected, public APIs explicit, no shadow state, no global singletons, no hidden coupling.
4. **Maintainability** - a future Claude Code session reading the diff can answer "why" without spelunking commit history.
5. **Speed** - last. Never the reason to accept a hack.

## Hard Bans (non-negotiable across every touched scope)

- **No hacks**, temporary workarounds, fake implementations, or knowingly deferred debt.
- **No swallowed errors**. Handle at boundaries with meaningful typed messages.
- **No secrets** in code, docs, memories, logs, prompts, screenshots, or commits.
- **No fake green checks**. Never claim tests/lint/types/browser/security/deploy passed without running them and recording exact evidence.
- **No unrelated destructive git or filesystem operations**.
- **No `latest` pin chasing** without verifying compatibility against actual public API and runtime behavior.
- **No prerelease / canary / 0.x** in production without explicit project acceptance.
- **No mypy for new Python projects in 2026** (pyright is the default; ty optionally for greenfield speed).
- **No deprecated FSD `processes` layer**; route responsibilities into `app`/`pages`/`widgets`.
- **No `@AGENTS.md` thin import** for `.claude/CLAUDE.md` (both files are first-class and dual-source).

## Default Architecture (May 2026)

- **Frontend / Client UI** (web, mobile, desktop): Feature-Sliced Design - layers `app`, `pages`, `widgets`, `features`, `entities`, `shared`. Imports flow only to lower layers (with `app` and `shared` exceptions). Public APIs for slices; no deep slice-internal imports. `shared` stays business-agnostic.
- **Backend**: Vertical Slice Architecture (organized around use cases / commands / queries / routes / handlers) + Hexagonal (Ports & Adapters - domain core isolated from infrastructure) + Modular Monolith (module boundaries form the outer container). Avoid generic pass-through service/repository layers.
- **MVP exception**: pure Layered architecture is acceptable only for MVPs / small projects where speed materially matters more than sustainability.
- **Existing architecture is the source of truth**. Never rewrite coherent existing architecture just to satisfy a generic rule. Document deviations via ADR.

## Default Tooling (May 2026, by language)

| Language | Type-check | Lint | Test | Package mgr |
|---|---|---|---|---|
| Python | **pyright** (default) - 2-5× faster than mypy, 98% spec | **ruff** | **pytest** | **uv** |
| TS/JS | `tsc --noEmit` or `tsgo` | **ESLint v9** (established) / **Biome** (greenfield, 24× faster) / Oxlint (CI speed layer) | **Vitest** (default) / Jest (Webpack/CRA only) | **pnpm** |
| Rust | `cargo check` | `cargo clippy -- -D warnings` | `cargo test` | cargo |
| Go | `go vet ./...` | `golangci-lint run` | `go test ./...` | go mod |
| Dart/Flutter | `dart analyze` / `flutter analyze` | (built into analyze) | `dart test` / `flutter test` | pub |

## Decision Patterns

- **Speed vs quality**: pick quality. Always. Time is not the constraint.
- **Consistency vs novelty**: pick consistency. If existing pattern is harmful, document the risk and ask before widening scope.
- **Reuse vs duplication**: reuse stable utilities. Extract reusable code only after real repeated need is clear - not on speculation.
- **Abstraction vs concreteness**: stay concrete. Three similar lines is better than a premature abstraction.
- **Breaking change vs preserving contract**: preserve. Break only when task explicitly requires it and an ADR captures the rationale.
- **Optimize now vs measure first**: measure first. No speculative optimization.

## Supply Chain Discipline (May 2026)

- **SBOM** attached to every release artifact (SPDX or CycloneDX format).
- **SLSA Level 2** minimum for new repos: verifiable build provenance via GitHub Actions + cosign / slsa-github-generator.
- **Sigstore / cosign** signing on release artifacts. Verify upstream signatures for critical dependencies.
- **Lockfile discipline**: `--frozen-lockfile` / `--immutable` / `npm ci` in CI.
- **Reject** abandoned (12+ months no commits without explanation), unclear-license, unclear-security-posture, magic-behavior dependencies.

## Universal Applicability

This philosophy is **project-agnostic**. It applies to:

- This marketplace (`rldyour-claude`) - Claude Code plugin metadata, scripts, hooks.
- Any future product repository using this marketplace - Python, TS, Rust, Go, Dart, mixed.
- Any new project initialized via `/rldyour-flow:ry-newp`.
- Any review run via `/rldyour-rules:ry-rules-review`.

When a project deviates from this philosophy (e.g., chooses mypy over pyright), the deviation must be documented (ADR or `AGENTS.md` exception clause) and justified. Inheriting deviations without justification is itself a hard-ban violation (fake green check class - accepting drift without verification).

## Change Rules

- Update this memory when May 2026 architecture or tooling defaults change (e.g., new Python type-checker overtakes pyright; FSD spec adds a layer; SLSA standard moves to Level 3 minimum).
- Update when a new **hard ban** is added or removed.
- Update when the **universal applicability** scope changes (e.g., new project class - embedded, mobile-first, AI agent - joins the supported set).
- When rule semantics change, update [[RULES-01-POLICY]] catalog (per-area pointers) and [[PATTERNS-01-CANONICAL]] canonical examples in parallel.
- Tooling defaults table changes also require updating [[RULES-01-POLICY]] `verification-quality-gates` skill citation and [[LSPS-01-LANGUAGE-SERVERS]] default decisions if a language LSP/type-checker default shifts.

## Verification

### For this marketplace (`rldyour-claude`)

- `python3 scripts/validate_agent_tools.py` - proves explicit-allowlist invariant (D15 closure + R4 mitigation).
- `bash scripts/validate_marketplace.sh` - proves frontmatter, version, MCP, and skill-routing invariants.
- `python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json` - proves instruction-doc presence (DOCS-01).
- Manual verification: every implementation wave runs the 6-track reviewer pipeline (`flow-architecture-review`, `flow-quality-review`, `flow-consistency-review`, `flow-integration-review`, `flow-verification-review`, `flow-security-review`) - see `plugins/rldyour-flow/references/reviewer-protocol.md`.

### For downstream projects (universal applicability)

The marketplace scripts above are marketplace-specific. Downstream projects consuming this philosophy should run the **language-native** verification commands documented in [[RULES-01-POLICY]] `verification-quality-gates` skill - for example:

- Python: `pyright`, `ruff check`, `pytest`.
- TypeScript/JavaScript: `tsc --noEmit` (or `tsgo`), `eslint .` (or `biome check .`), `vitest run`.
- Rust: `cargo check`, `cargo clippy -- -D warnings`, `cargo test`.
- Go: `go vet ./...`, `go test ./...`, `golangci-lint run`.
- Dart/Flutter: `dart analyze` / `flutter analyze`, `dart test` / `flutter test`.

Plus: project-specific manual / browser / security / design / LSP checks routed through the corresponding `rldyour-*` plugin (see [[BROWSER-01-WORKFLOW]], [[DESIGN-01-WORKFLOW]], [[SECURITY-01-OWASP]], [[LSPS-01-LANGUAGE-SERVERS]]) - these plugins work in any project that installs them, not just this marketplace.

ADR (MADR 4.0.0) for any deviation from May 2026 defaults - see [[RULES-01-POLICY]] `project-instructions-policy` skill.

## Cross-References

- Implementation-level rules: [[RULES-01-POLICY]] (per-area catalog).
- Canonical implementation patterns: [[PATTERNS-01-CANONICAL]].
- Architecture/code/style invariants: [[CLAUDECODE-01-PLUGIN-CANON]], [[DOCS-01-INSTRUCTIONS]].
- Open / closed technical debt: [[TECHDEBT-01-NOW]].
