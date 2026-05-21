<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: a519d10eb604bfb6c7988aa1fda43b3aeecc46e5 test: align Claude baseline fixture
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
- commit: `a519d10eb604bfb6c7988aa1fda43b3aeecc46e5`
- checked by: Codex ry-start baseline fixture sync

## Facts
- Runtime memories record pinned CLI/package baselines and freshness checks.

## Evidence
- `commit:a519d10eb604bfb6c7988aa1fda43b3aeecc46e5`
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
