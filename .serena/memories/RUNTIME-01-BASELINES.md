<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ece8d844c2696c92d7a938601258340cab91147b chore(release): claude 1.0.5
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
- date: 2026-05-28
- commit: `ece8d844c2696c92d7a938601258340cab91147b`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- Runtime memories record pinned CLI/package baselines and freshness checks.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
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
