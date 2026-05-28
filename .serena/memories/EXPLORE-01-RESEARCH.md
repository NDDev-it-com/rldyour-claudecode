<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ece8d844c2696c92d7a938601258340cab91147b chore(release): claude 1.0.5
Scope: source-backed research workflow
Area: EXPLORE
-->

# EXPLORE-01-RESEARCH

## Scope
source-backed research workflow

## Current source of truth
- `path:plugins/rldyour-explore`
- `path:README.md`


## Source Of Truth
- `path:plugins/rldyour-explore`
- `path:README.md`

## Last verified
- date: 2026-05-28
- commit: `ece8d844c2696c92d7a938601258340cab91147b`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- Explore memories record when current source-backed research is required before implementation.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- `path:plugins/rldyour-explore`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `MCP-01-TRANSPORT.md`
- `RULES-01-POLICY.md`
- `SECURITY-01-OWASP.md`
