<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: fa1a49c refactor(policy): track claude agent context on main
Scope: always-needed repository context
Area: CONTEXT
-->

# Core Context

## Scope
always-needed repository context

## Current source of truth
- `path:README.md`
- `path:config/rldyour-contract.json`

## Last verified
- date: 2026-05-22
- commit: `fa1a49c`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Context memories hold stable facts that agents need before planning or editing.

## Evidence
- `commit:fa1a49c`
- `path:README.md`
- `path:config/rldyour-contract.json`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
