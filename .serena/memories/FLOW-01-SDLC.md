<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: f78a246df180e912fd4090f89f25f8b74b16e80c chore(runtime): bump claude code baseline to 2.1.156
Scope: rldyour SDLC command lifecycle
Area: FLOW
-->

# FLOW-01-SDLC

## Scope
rldyour SDLC command lifecycle

## Current source of truth
- `path:plugins/rldyour-flow`


## Source Of Truth
- `path:plugins/rldyour-flow`

## Last verified
- date: 2026-05-29
- commit: `f78a246df180e912fd4090f89f25f8b74b16e80c`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Flow memories record ry-init, ry-start, ry-newp, ry-review, ry-repair, ry-deploy, and ry-sync behavior.

## Evidence
- `commit:f78a246df180e912fd4090f89f25f8b74b16e80c`
- `path:plugins/rldyour-flow`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `HOOKS-01-LIFECYCLE.md`
- `SERENA-01-MEMORY-SYNC.md`
- `TESTS-01-VALIDATION-GATES.md`
