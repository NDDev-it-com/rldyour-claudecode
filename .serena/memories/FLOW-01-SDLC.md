<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ece8d844c2696c92d7a938601258340cab91147b chore(release): claude 1.0.5
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
- date: 2026-05-28
- commit: `ece8d844c2696c92d7a938601258340cab91147b`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- Flow memories record ry-init, ry-start, ry-newp, ry-review, ry-repair, ry-deploy, and ry-sync behavior.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
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
