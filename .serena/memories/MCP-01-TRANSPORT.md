<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: a519d10eb604bfb6c7988aa1fda43b3aeecc46e5 test: align Claude baseline fixture
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
- commit: `a519d10eb604bfb6c7988aa1fda43b3aeecc46e5`
- checked by: Codex ry-start baseline fixture sync

## Facts
- MCP memories record server ownership, transports, versions, and toolset constraints.

## Evidence
- `commit:a519d10eb604bfb6c7988aa1fda43b3aeecc46e5`
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
