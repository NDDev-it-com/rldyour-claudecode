# Verification And Quality Gates

## General Gates

Run the checks that match the touched stack and risk:

- Type checking.
- Linting.
- Unit tests.
- Integration tests.
- E2E tests.
- Build.
- Formatting checks when project-standard.
- Generated artifact checks.
- Migration checks.
- Security checks (Semgrep MCP, project security scripts).
- Browser checks for UI-visible work (Playwright + Chrome DevTools MCP).
- Deploy checks for server changes.

## May 2026 Tooling Defaults

### Python

- **Type-checker**: `pyright` (default — best speed/spec-conformance ratio). Microsoft-maintained, 98% spec coverage, 2-5x faster than mypy.
- **Lint**: `ruff` (canonical — replaces flake8/isort/black/pylint).
- **Test**: `pytest`.
- Optional **ty** (Astral) for greenfield speed-first projects (10-60x faster than mypy/pyright but only ~53% spec conformance).
- Avoid `mypy` for new projects unless legacy constraints demand it.

### JavaScript / TypeScript

- **Type-check**: `tsc --noEmit` (or `tsgo` when available).
- **Lint**:
  - **ESLint v9** with flat config — universal default for established codebases.
  - **Biome** — recommended for greenfield projects (24x faster, ESM-native).
  - **Oxlint (OXC)** — emerging, 50-100x faster but linting-only and immature ecosystem; CI speed layer only.
- **Test**:
  - **Vitest** — default for new TS/ESM projects.
  - **Jest** — only if Webpack/CRA constraints exist.
- **Format**: Prettier or Biome formatter.

### Rust

- `cargo check`, `cargo clippy -- -D warnings`, `cargo test`.

### Go

- `go vet ./...`, `go test ./...`, `golangci-lint run`.

### Dart / Flutter

- `dart analyze` / `flutter analyze`, `dart test` / `flutter test`, `dart format`.

### C / C++ / Qt

- `clangd` requires `compile_commands.json`. CMake projects: enable `CMAKE_EXPORT_COMPILE_COMMANDS=ON`.
- `clang-tidy` for static analysis.

## Evidence Rules

- Report exact commands and outcomes.
- If checks cannot run, report the blocker and residual risk.
- Do not claim confidence as a substitute for checks.
- Do not ignore warnings that indicate broken contracts, stale generated files, missing migrations, or unsafe behavior.

## Review Focus

Before finalizing, verify:

- Design fits the system.
- Functionality satisfies user and developer needs.
- Complexity is not higher than necessary.
- Tests would fail if behavior breaks.
- Names communicate domain meaning.
- Comments explain why, not what.
- Style follows project standards.
- Changed docs match changed behavior.
- Every human-written line in the touched scope is understood.
- The change improves or preserves overall code health.
