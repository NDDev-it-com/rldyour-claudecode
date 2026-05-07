---
description: "Запустить аудит реализации против rldyour rules через ry-rules-review (report-only по умолчанию)."
argument-hint: <scope>
---

Аудит против rldyour rules для: **$ARGUMENTS**

Use the `ry-rules-review` skill to audit the specified scope (diff, PR, branch, file, or prompt scope) against `rldyour-rules`.

The skill applies all 6 rule skills:

1. `quality-first-engineering` — hard bans (no hacks / swallowed errors / fake checks / secrets / unrelated destructive ops), semantic entropy, scope policy.
2. `architecture-boundaries` — FSD (frontend), VSA + Hexagonal + Modular Monolith (backend) placement, ADR triggers.
3. `implementation-discipline` — integration sync (routes/clients/schemas/DTOs/migrations/types/configs/tests/docs), reuse, error handling, naming.
4. `dependency-compatibility-policy` — latest-compatible versioning, lockfile discipline, SLSA Level 2 + SBOM (May 2026 standards).
5. `verification-quality-gates` — pyright/ruff for Python, ESLint v9/Biome for TS/JS, Vitest for new TS, no fake green.
6. `project-instructions-policy` — AGENTS.md / .claude/CLAUDE.md / REVIEW.md / MADR 4.0.0 ADRs.

**Default mode: report-only.** Findings format: Severity / Confidence / Location / Rule / Evidence / Impact / Fix / Disposition. Drop confidence <30.

Modify files only if the user explicitly asks after seeing findings.

Reply in Russian.
