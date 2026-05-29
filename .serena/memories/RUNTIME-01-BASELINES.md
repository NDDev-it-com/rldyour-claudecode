<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: cbab06d96f803f0a819b9aaa6f3bdfc2b42f4708 chore(release): claude 1.1.1
Scope: CLI runtime and package baselines
Area: RUNTIME
-->

# Runtime Baselines

## Scope
CLI runtime and package baselines

## Current source of truth
- `path:references/claude-baseline.json`


## Source Of Truth
- `path:references/claude-baseline.json`

## Last verified
- date: 2026-05-29
- commit: `cbab06d96f803f0a819b9aaa6f3bdfc2b42f4708`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Runtime memories record pinned CLI/package baselines and freshness checks.

## Evidence
- `commit:cbab06d96f803f0a819b9aaa6f3bdfc2b42f4708`
- `path:references/claude-baseline.json`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `RELEASE-01-VALIDATION.md`
- `MCP-01-TRANSPORT.md`
- `CI-01-ACTIONS.md`
