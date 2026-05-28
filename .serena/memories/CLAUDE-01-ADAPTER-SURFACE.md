<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ad97d9deb65b76cea82052322b9e6cee86af0407 fix(installer): guard report markdown printf
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
- commit: `ad97d9deb65b76cea82052322b9e6cee86af0407`
- checked by: Codex system sync after Claude installer report fix

## Facts
- Claude memories describe the Claude Code plugin marketplace, command, skill, hook, MCP, and LSP surfaces.

## Evidence
- `commit:ad97d9deb65b76cea82052322b9e6cee86af0407`
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
