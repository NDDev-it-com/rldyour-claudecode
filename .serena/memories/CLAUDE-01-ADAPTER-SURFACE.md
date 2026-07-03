<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: fa1a49c refactor(policy): track claude agent context on main
Scope: Claude Code adapter implementation surface
Area: CLAUDE
-->

# Claude Adapter Surface

## Scope
Claude Code adapter implementation surface

## Current source of truth
- `path:config/rldyour-contract.json`
- `path:.claude-plugin/marketplace.json`

## Last verified
- date: 2026-05-22
- commit: `fa1a49c`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Claude memories describe the Claude Code plugin marketplace, command, skill, hook, MCP, and LSP surfaces.

## Evidence
- `commit:fa1a49c`
- `path:config/rldyour-contract.json`
- `path:.claude-plugin/marketplace.json`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
