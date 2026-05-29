<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: f78a246df180e912fd4090f89f25f8b74b16e80c chore(runtime): bump claude code baseline to 2.1.156
Scope: Serena memory, fullrepo, and knowledge sync policy
Area: SERENA
-->

# SERENA-01-MEMORY-SYNC

## Scope
Serena memory, fullrepo, and knowledge sync policy

## Current source of truth
- `path:plugins/rldyour-serena-mcp`
- `path:.serena/project.yml`
- `path:README.md`


## Source Of Truth
- `path:plugins/rldyour-serena-mcp`
- `path:.serena/project.yml`
- `path:README.md`

## Last verified
- date: 2026-05-29
- commit: `f78a246df180e912fd4090f89f25f8b74b16e80c`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Serena memories record memory format, evidence, freshness, fullrepo, and runtime marker policy.

## Evidence
- `commit:f78a246df180e912fd4090f89f25f8b74b16e80c`
- `path:plugins/rldyour-serena-mcp`
- `path:.serena/project.yml`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `FLOW-01-SDLC.md`
- `DOCS-01-INSTRUCTIONS.md`
- `CONTEXT-01-CORE.md`
