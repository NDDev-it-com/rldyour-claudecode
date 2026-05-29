<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: 30610a53cdab6d0308e41358dc379a41e14e69ca chore(release): claude 1.1.5
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
- date: 2026-05-29
- commit: `30610a53cdab6d0308e41358dc379a41e14e69ca`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Docs memories record which instruction and operator docs must change after durable behavior changes.
- `scripts/validate_instruction_docs.py` validates active Claude runtime-pin claims against `package.json`, `references/claude-baseline.json`, and `config/mcp-runtime-versions.env`.
- `scripts/validate_instruction_sync.py` accepts both nested `claims` and top-level sync-contract keys, while still failing semantic drift for shared keys.

## Evidence
- `commit:30610a53cdab6d0308e41358dc379a41e14e69ca`
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
