<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: f78a246df180e912fd4090f89f25f8b74b16e80c chore(runtime): bump claude code baseline to 2.1.156
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
- date: 2026-05-29
- commit: `f78a246df180e912fd4090f89f25f8b74b16e80c`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- MCP memories record server ownership, transports, versions, and toolset constraints.
- Dart/Flutter MCP is provided by the local Dart SDK. The Claude adapter now
  pins the owner host runtime to Dart SDK `3.12.0` in
  `config/mcp-runtime-versions.env`.

## Evidence
- `commit:f78a246df180e912fd4090f89f25f8b74b16e80c`
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:config/mcp-runtime-versions.env`
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
