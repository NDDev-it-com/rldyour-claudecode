<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: fa1a49c refactor(policy): track claude agent context on main
Scope: validation gates and test suites
Area: TESTS
-->

# Validation Gates

## Scope
validation gates and test suites

## Current source of truth
- `path:scripts`
- `path:.github/workflows`
- `path:README.md`

## Last verified
- date: 2026-05-22
- commit: `fa1a49c`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Test memories record which suites and smoke tests prove the touched behavior.

## Evidence
- `commit:fa1a49c`
- `path:scripts`
- `path:.github/workflows`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
