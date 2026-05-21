<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: be48d065a841ae95f762177a7b70002ad93470fc docs: refresh generated inventory
Scope: MCP runtime transport and pin policy
Area: MCP
-->

# MCP-01-TRANSPORT

## Scope
MCP runtime transport and pin policy

## Current source of truth
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:README.md`


## Source Of Truth
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:README.md`

## Last verified
- date: 2026-05-22
- commit: `be48d065a841ae95f762177a7b70002ad93470fc`
- checked by: Codex ry-start sync audit

## Facts
- MCP memories record server ownership, transports, versions, and toolset constraints.

## Evidence
- `commit:be48d065a841ae95f762177a7b70002ad93470fc`
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `RUNTIME-01-BASELINES.md`
- `SECURITY-01-OWASP.md`
- `EXPLORE-01-RESEARCH.md`
