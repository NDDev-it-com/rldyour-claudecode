---
name: verification-quality-gates
description: "Гейты качества перед delivery: тесты, lint (ruff/ESLint v9/Biome), types (pyright), LSP, browser/security/design. Используй для: проверки, тесты, линтер, типы, качество, доказательства. EN triggers: quality gates, run tests, run linter, type check, run LSP checks, run all checks, verify before delivery, evidence-based pass."
---

# Verification Quality Gates

## Purpose

Finish work with real evidence, not assumptions. Verification should match the change type and risk.

## Gate Selection

- Run project-native tests, type checks, linters, format checks, and build checks that apply to touched code.
- Use `rldyour-lsps` for language-server routing and diagnostics when language support matters.
- Use `rldyour-browser` for frontend, UI-visible, browser behavior, responsive, visual, and business-flow changes.
- Use `rldyour-security` for auth, authorization, input/output handling, secrets, file handling, dependency/config, payment, admin, or external integration changes.
- Use `rldyour-design` for Figma, shadcn/ui, ReactBits, design tokens, FSD frontend placement, and design-system changes.
- Use `rldyour-flow` `flow-post-task-sync` when changes should be committed, pushed, documented, or memory-synchronized.

## May 2026 Tooling Defaults

**Python:**

- Type-checker: **pyright** (default - best speed/spec-conformance ratio, 2-5x faster than mypy with 98% spec coverage). Optionally **ty** (Astral, 10-60x faster, 53% spec) for greenfield speed-first projects. Avoid mypy for new projects.
- Lint: **ruff** (canonical - replaces flake8/isort/black/pylint).
- Test: **pytest** (canonical, no change).

**JavaScript/TypeScript:**

- Lint:
  - **ESLint v9** with flat config - universal default for established codebases (largest plugin ecosystem).
  - **Biome** - recommended for greenfield projects (24x faster than ESLint+Prettier, ESM-native).
  - **Oxlint (OXC)** - emerging, 50-100x faster but linting-only and immature ecosystem; use as CI speed layer, not primary.
- Test:
  - **Vitest** - default for new TS/ESM projects (faster, ESM-native).
  - **Jest** - only if Webpack/CRA constraints exist.
- Type-check: `tsc --noEmit` or `tsgo` (TypeScript Go) when available.

**Rust:** `cargo check`, `cargo clippy -- -D warnings`, `cargo test`.

**Go:** `go vet ./...`, `go test ./...`, `golangci-lint run`.

**Dart/Flutter:** `dart analyze` / `flutter analyze`, `dart test` / `flutter test`.

## No Fake Green

- If a check passes, report the exact command or evidence.
- If a check fails, fix root cause or report the blocker.
- If a check cannot run, state why and what risk remains.
- Do not replace missing verification with confidence language.

Read `${CLAUDE_PLUGIN_ROOT}/references/quality-gates.md` for the full checklist.

## Anti-patterns

- Claim "tests pass" без exact command + output.
- Skip type-check для TypeScript/Python changes.
- Replace failing check с ignored warning.
- Use confidence language ("should work") вместо actual verification.
- Skip browser-validation для UI-visible changes (use rldyour-browser).
- Use mypy для new Python projects в 2026 (pyright is default).
