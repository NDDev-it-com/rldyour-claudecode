<!-- Memory Metadata
Last updated: 2026-06-09
Last verified: 2026-06-09
Last commit: 8aebb293feac6e02cd180ee0656cdc7df0a02787 chore(release): claude 1.1.45 (other)
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
- date: 2026-06-09
- commit: `8aebb293feac6e02cd180ee0656cdc7df0a02787`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Docs memories record which instruction and operator docs must change after durable behavior changes.
- `scripts/validate_instruction_docs.py` validates active Claude runtime-pin claims against `package.json`, `references/claude-baseline.json`, and `config/mcp-runtime-versions.env`.
- `scripts/validate_instruction_sync.py` accepts both nested `claims` and top-level sync-contract keys, while still failing semantic drift for shared keys.

## Evidence
- `commit:8aebb293feac6e02cd180ee0656cdc7df0a02787`
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

## Applies to
- The scope declared in this memory and the source-of-truth paths listed below.

## Invariants
- Code, configuration, tests, and git state override this memory when they disagree.

## Current State
- See `Facts` for current durable facts. Do not treat `Historical evidence` or old commit notes as current state.

## Do Not Infer
- Do not infer runtime versions, product versions, commits, permissions, release state, or tool behavior from this memory without checking the source of truth.

## Update Triggers
- Update after verified changes to the source-of-truth files, runtime baselines, release tuple, validation gates, or durable agent workflow contracts.

## Validation Commands
- `python3 scripts/validate_serena_memory_schema.py --scope all --strict-mode strict-all`
- `python3 scripts/validate_serena_memory_semantics.py --scope all --strict-current-facts`
- `python3 scripts/validate_memory_freshness.py --scope all`

## Repair Procedure
- Re-read source-of-truth files, update only verified current facts, move stale facts to historical evidence, then rerun the validation commands.
