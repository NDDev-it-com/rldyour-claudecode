<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ad97d9deb65b76cea82052322b9e6cee86af0407 fix(installer): guard report markdown printf
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
- date: 2026-05-28
- commit: `ad97d9deb65b76cea82052322b9e6cee86af0407`
- checked by: Codex system sync after Claude installer report fix

## Facts
- Hook memories record bounded, deterministic lifecycle behavior and the authoritative Stop owner.

## Evidence
- `commit:ad97d9deb65b76cea82052322b9e6cee86af0407`
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
