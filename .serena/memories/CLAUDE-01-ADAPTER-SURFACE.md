<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: cf5b25eb348ff012a2bcbbd2e4e61308207d674e test: avoid brittle Claude sync claim count
Scope: Claude Code adapter implementation surface
Area: CLAUDE
-->

# Claude Adapter Surface

## Scope
Claude Code adapter implementation surface

## Current source of truth
- `path:config/rldyour-contract.json`
- `path:.claude-plugin/marketplace.json`


## Source Of Truth
- `path:config/rldyour-contract.json`
- `path:.claude-plugin/marketplace.json`

## Last verified
- date: 2026-05-28
- commit: `cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- Claude memories describe the Claude Code plugin marketplace, command, skill, hook, MCP, and LSP surfaces.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- `path:config/rldyour-contract.json`
- `path:.claude-plugin/marketplace.json`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `MCP-01-TRANSPORT.md`
- `FLOW-01-SDLC.md`
- `RUNTIME-01-BASELINES.md`
