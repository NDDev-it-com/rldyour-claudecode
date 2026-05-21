<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: be48d065a841ae95f762177a7b70002ad93470fc docs: refresh generated inventory
Scope: deterministic hook lifecycle behavior
Area: HOOKS
-->

# HOOKS-01-LIFECYCLE

## Scope
deterministic hook lifecycle behavior

## Current source of truth
- `path:plugins/rldyour-flow/hooks`
- `path:scripts/smoke_hooks.sh`


## Source Of Truth
- `path:plugins/rldyour-flow/hooks`
- `path:scripts/smoke_hooks.sh`

## Last verified
- date: 2026-05-22
- commit: `be48d065a841ae95f762177a7b70002ad93470fc`
- checked by: Codex ry-start sync audit

## Facts
- Hook memories record bounded, deterministic lifecycle behavior and the authoritative Stop owner.

## Evidence
- `commit:be48d065a841ae95f762177a7b70002ad93470fc`
- `path:plugins/rldyour-flow/hooks`
- `path:scripts/smoke_hooks.sh`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `FLOW-01-SDLC.md`
- `SERENA-01-MEMORY-SYNC.md`
- `TESTS-01-VALIDATION-GATES.md`
