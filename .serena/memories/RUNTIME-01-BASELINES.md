<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: 63abf7d4084cd892fea40e126d71cdd2ddf6d80e chore(release): claude 1.1.0
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
- commit: `63abf7d4084cd892fea40e126d71cdd2ddf6d80e`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Runtime memories record pinned CLI/package baselines and freshness checks.

## Evidence
- `commit:63abf7d4084cd892fea40e126d71cdd2ddf6d80e`
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
