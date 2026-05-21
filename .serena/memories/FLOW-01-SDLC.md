<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: 9330d026c96dcf7fd24ea9d6e70aebf063415511 feat(flow): align stop lifecycle and numeric releases
Scope: rldyour SDLC command lifecycle
Area: FLOW
-->

# FLOW-01-SDLC

## Scope
rldyour SDLC command lifecycle

## Current source of truth
- `path:plugins/rldyour-flow`

## Last verified
- date: 2026-05-22
- commit: `9330d026c96dcf7fd24ea9d6e70aebf063415511`
- checked by: Codex ry-start memory-domain normalization

## Facts
- Flow memories record ry-init, ry-start, ry-newp, ry-review, ry-repair, ry-deploy, and ry-sync behavior.

## Evidence
- `commit:9330d026c96dcf7fd24ea9d6e70aebf063415511`
- `path:plugins/rldyour-flow`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
