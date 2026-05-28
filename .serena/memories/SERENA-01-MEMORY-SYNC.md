<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ad97d9deb65b76cea82052322b9e6cee86af0407 fix(installer): guard report markdown printf
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
- date: 2026-05-28
- commit: `ad97d9deb65b76cea82052322b9e6cee86af0407`
- checked by: Codex system sync after Claude installer report fix

## Facts
- Serena memories record memory format, evidence, freshness, fullrepo, and runtime marker policy.

## Evidence
- `commit:ad97d9deb65b76cea82052322b9e6cee86af0407`
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
