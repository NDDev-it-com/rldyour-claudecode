<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: fa1a49c refactor(policy): track claude agent context on main
Scope: verified current technical debt
Area: TECHDEBT
-->

# Current Technical Debt

## Scope
verified current technical debt

## Current source of truth
- `path:README.md`
- `path:CHANGELOG.md`

## Last verified
- date: 2026-05-22
- commit: `fa1a49c`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Technical debt memories record verified open debt only when it has code/config evidence.

## Evidence
- `commit:fa1a49c`
- `path:README.md`
- `path:CHANGELOG.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
