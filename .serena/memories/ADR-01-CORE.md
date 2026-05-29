<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: 6c432ca58735319802d7511b7e0c8493f76675f3 fix(flow): preserve ry-start command skill delegation
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
- date: 2026-05-29
- commit: `6c432ca58735319802d7511b7e0c8493f76675f3`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- ADR memories record decisions and policy shape. Meaning changes require explicit owner approval.

## Evidence
- `commit:6c432ca58735319802d7511b7e0c8493f76675f3`
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
