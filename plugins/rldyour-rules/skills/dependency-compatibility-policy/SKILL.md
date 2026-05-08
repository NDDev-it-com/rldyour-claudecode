---
name: dependency-compatibility-policy
description: "Политика зависимостей: latest-compatible, source-backed, SLSA Level 2, SBOM, lockfile discipline. Используй для: зависимости, версии, обнови пакет, миграция версий, совместимость, цепочка поставок. EN triggers: bump dependencies, package version policy, latest-compatible, lockfile discipline, supply chain check, SLSA level 2, SBOM."
---

# Dependency Compatibility Policy

## Purpose

Use current, compatible, secure, and maintainable technology choices without blindly chasing `latest`. Treat dependencies as supply chain risk that requires discipline.

## Selection Rules

- Prefer latest compatible stable versions, not unverified latest versions.
- Check official docs, release notes, migration guides, compatibility matrices, and project constraints before changing technology or dependencies.
- Use `rldyour-explore` (`tech-research` + `web-research`) for technical research when compatibility or current best practice matters.
- Respect lockfiles and package manager conventions. Do not manually edit generated lockfile content unless that is the project-standard workflow.
- SemVer is a signal, not proof. Verify breaking changes against actual public API and runtime behavior.
- Major upgrades require an explicit migration plan, affected-scope analysis, and rollback or fix-forward strategy.
- New production dependencies must have a clear purpose, maintenance signal, license acceptability, security posture, and integration plan.
- Do not add dependencies to avoid writing small project-specific code unless the dependency materially reduces risk or complexity.

## May 2026 Supply Chain Standards

- **SBOM** (Software Bill of Materials): attach SPDX or CycloneDX SBOM to every release artifact. Operational, not experimental.
- **SLSA Level 2** is the minimum for new repositories: verifiable build provenance via GitHub Actions + cosign / slsa-github-generator. Achievable in one day.
- **Sigstore / cosign** for signing release artifacts. Verify upstream signatures when consuming critical dependencies.
- **OWASP Top 10 2025 — A03 Software Supply Chain Failures** is a top-tier concern (jumped to #3). Top threats: dependency confusion, upstream infrastructure compromise, code signing cert theft, CI/CD exploitation, typosquatting.
- **Lockfile discipline**: `--frozen-lockfile` / `--immutable` / `npm ci` in CI to enforce exact version matching.

## Package Manager Defaults (May 2026)

- **JavaScript/TypeScript**: pnpm is the recommended default for new projects (faster, better disk usage, ecosystem support).
- **Python**: uv (Astral) for environments and dependency resolution; pip-tools or uv for lockfiles.
- **Rust**: cargo with Cargo.lock committed for binaries, optional for libraries.
- **Go**: go mod tidy, go.sum committed.
- **Dart/Flutter**: pubspec.lock committed for application projects.

## Compatibility Checks

Check compatibility across runtime version, framework version, language version, build tool/bundler, type system + generated types, peer dependencies, plugin ecosystem, deployment environment, and security scanners.

## Rejection Criteria

Reject or ask before using a dependency when:

- It is abandoned or poorly maintained (no commits in 12+ months without explanation).
- It duplicates a stable project utility.
- It requires broad architecture changes unrelated to the task.
- It hides critical behavior behind magic that is hard to debug.
- Its license or security posture is unclear.

Read `${CLAUDE_PLUGIN_ROOT}/references/dependency-policy.md` for detailed dependency selection and upgrade rules.

## Anti-patterns

- Использовать `latest` без verification compatibility (chasing unverified versions).
- Manually edit generated lockfile content (corrupts integrity).
- Mix unrelated dependency upgrades с feature work — separate commit/PR.
- Add dependency для exact 5 строк project-specific code когда self-write проще.
- Skip SLSA Level 2 / SBOM для new releases в 2026.
- Adopt prerelease/canary/0.x в production без explicit project acceptance.
