<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: a519d10eb604bfb6c7988aa1fda43b3aeecc46e5 test: align Claude baseline fixture
Scope: instruction docs and durable operator documentation
Area: DOCS
-->

# DOCS-01-INSTRUCTIONS

## Scope
instruction docs and durable operator documentation

## Current source of truth
- `path:AGENTS.md`
- `path:.claude/CLAUDE.md`
- `path:README.md`


## Source Of Truth
- `path:AGENTS.md`
- `path:.claude/CLAUDE.md`
- `path:README.md`

## Last verified
- date: 2026-05-22
- commit: `a519d10eb604bfb6c7988aa1fda43b3aeecc46e5`
- checked by: Codex ry-start baseline fixture sync

## Facts
- Docs memories record which instruction and operator docs must change after durable behavior changes.

## Evidence
- `commit:a519d10eb604bfb6c7988aa1fda43b3aeecc46e5`
- `path:AGENTS.md`
- `path:.claude/CLAUDE.md`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `CORE-01-INDEX.md`
- `CLAUDE-01-ADAPTER-SURFACE.md`
- `SERENA-01-MEMORY-SYNC.md`
