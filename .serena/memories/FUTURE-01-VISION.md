<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: fa1a49c refactor(policy): track claude agent context on main
Scope: future architecture direction and scalability gravity
Area: FUTURE
-->

# Future Vision

## Scope
future architecture direction and scalability gravity

## Current source of truth
- `path:README.md`
- `path:config/rldyour-contract.json`

## Last verified
- date: 2026-05-22
- commit: `fa1a49c`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Future memories record architectural trajectory and scale direction, not transient task queues.

## Evidence
- `commit:fa1a49c`
- `path:README.md`
- `path:config/rldyour-contract.json`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update only for durable architectural trajectory and scalability direction, not transient queues.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
