<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: cf5b25eb348ff012a2bcbbd2e4e61308207d674e test: avoid brittle Claude sync claim count
Scope: GitHub Actions and local CI policy
Area: CI
-->

# CI Actions

## Scope
GitHub Actions and local CI policy

## Current source of truth
- `path:.github/workflows`
- `path:README.md`


## Source Of Truth
- `path:.github/workflows`
- `path:README.md`

## Last verified
- date: 2026-05-28
- commit: `cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- CI memories record which checks prove repository integrity and which checks are intentionally lightweight.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- `path:.github/workflows`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `TESTS-01-VALIDATION-GATES.md`
- `RELEASE-01-VALIDATION.md`
- `SECURITY-01-OWASP.md`
