<!-- Memory Metadata
Last updated: 2026-05-30
Last verified: 2026-05-30
Last commit: 30610a53cdab6d0308e41358dc379a41e14e69ca chore(release): claude 1.1.5
Scope: language-server setup and diagnostic proof
Area: LSP
-->

# Language Server Quality Gates

## Scope
language-server setup and diagnostic proof

## Current source of truth
- `path:plugins/rldyour-lsps`
- `path:README.md`


## Source Of Truth
- `path:plugins/rldyour-lsps`
- `path:README.md`

## Last verified
- date: 2026-05-30
- commit: `30610a53cdab6d0308e41358dc379a41e14e69ca`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- LSP memories record language-server coverage and diagnostic proof requirements.

## Evidence
- `commit:30610a53cdab6d0308e41358dc379a41e14e69ca`
- `path:plugins/rldyour-lsps`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `SERENA-01-MEMORY-SYNC.md`
- `TESTS-01-VALIDATION-GATES.md`
- `MCP-01-TRANSPORT.md`

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
