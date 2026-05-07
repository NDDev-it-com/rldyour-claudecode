# Source-Backed Design Notes

Primary sources used for this plugin (verified May 2026):

## Specifications & Standards

- Conventional Commits v1.0.0: https://www.conventionalcommits.org/en/v1.0.0/
- Semantic Versioning: https://semver.org/
- MADR (Markdown Architectural Decision Records) 4.0.0: https://adr.github.io/madr/
- Architectural Decision Records: https://adr.github.io/

## Architecture

- Feature-Sliced Design: https://feature-sliced.design/
- Vertical Slice Architecture (Jimmy Bogard): https://www.jimmybogard.com/vertical-slice-architecture/
- Hexagonal Architecture (Alistair Cockburn): https://alistair.cockburn.us/hexagonal-architecture/
- Clean Architecture (Robert C. Martin): https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Modular Monolith (Kamil Grzybek): https://www.kamilgrzybek.com/architecture/modular-monolith-primer/
- C4 model: https://c4model.com/
- arc42: https://arc42.org/overview

## Code Review

- Google Engineering Practices, what to look for in code review: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Google Engineering Practices, small CLs: https://google.github.io/eng-practices/review/developer/small-cls.html
- Martin Fowler Design Stamina Hypothesis: https://martinfowler.com/bliki/DesignStaminaHypothesis.html

## Supply Chain Security (May 2026)

- OWASP Top 10 2025: https://owasp.org/Top10/2025/
- OWASP Secure Coding Practices: https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/
- SLSA framework: https://slsa.dev/
- Sigstore project: https://www.sigstore.dev/
- SPDX SBOM: https://spdx.dev/
- CycloneDX SBOM: https://cyclonedx.org/
- GitHub Actions attestations: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations

## Tooling Defaults (May 2026)

- pyright: https://github.com/microsoft/pyright
- ruff (Astral): https://docs.astral.sh/ruff/
- ty (Astral, Python type-checker): https://github.com/astral-sh/ty
- ESLint v9: https://eslint.org/
- Biome: https://biomejs.dev/
- Oxlint (OXC): https://oxc-project.github.io/
- Vitest: https://vitest.dev/
- pytest: https://docs.pytest.org/
- pnpm: https://pnpm.io/
- uv (Astral, Python): https://docs.astral.sh/uv/

## Claude Code references

- Claude Code memory: https://code.claude.com/docs/en/memory
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Claude Code plugins reference: https://code.claude.com/docs/en/plugins-reference
- Claude Code skills: https://code.claude.com/docs/en/skills

## Engineering conclusions

- Keep rules as focused skills with references for progressive disclosure.
- Use `AGENTS.md` for durable Codex instructions; `.claude/CLAUDE.md` for first-class Claude Code memory; do not reduce one to a thin import of the other.
- Use FSD (frontend) and VSA + Hexagonal + Modular Monolith (backend) as defaults for new areas, not as forced rewrites of coherent existing projects.
- Treat FSD `processes` layer as deprecated by default.
- Mandate SLSA Level 2 + SBOM + Sigstore for new releases (May 2026 baseline).
- Prefer pyright + ruff for Python; ESLint v9 (established) or Biome (greenfield) for TS/JS; Vitest for new TS.
- Use MADR 4.0.0 ADR format for decisions future agents must preserve.
- Prefer advisory-first automatic guidance over blocking hooks for general quality rules.
- Keep hard bans explicit and non-negotiable inside touched scope.
