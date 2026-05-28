<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: cf5b25eb348ff012a2bcbbd2e4e61308207d674e test: avoid brittle Claude sync claim count
Scope: architecture decisions and owner-approved policy changes
Area: ADR
-->

# ADR Core

## Scope
architecture decisions and owner-approved policy changes

## Current source of truth
- `path:docs/adr`


## Source Of Truth
- `path:docs/adr`

## Last verified
- date: 2026-05-28
- commit: `cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- ADR memories record decisions and policy shape. Meaning changes require explicit owner approval.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- `path:docs/adr`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
ADR meaning changes require explicit owner approval; format-only normalization may be done without changing the decision.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `CORE-01-INDEX.md`
- `DOCS-01-INSTRUCTIONS.md`
- `RULES-01-POLICY.md`
