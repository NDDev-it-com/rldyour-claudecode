<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: be48d065a841ae95f762177a7b70002ad93470fc docs: refresh generated inventory
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
- date: 2026-05-22
- commit: `be48d065a841ae95f762177a7b70002ad93470fc`
- checked by: Codex ry-start sync audit

## Facts
- Runtime memories record pinned CLI/package baselines and freshness checks.

## Evidence
- `commit:be48d065a841ae95f762177a7b70002ad93470fc`
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
