<!-- Memory Metadata
Last updated: 2026-06-25
Last verified: 2026-06-25
Last commit: e56ecf05f68969cac2f1ec6ee8f25d44a463d12d chore(release): claude 1.6.1
Scope: MCP runtime transport and pin policy
Area: MCP
-->

# MCP Transport

## Scope
MCP runtime transport and pin policy

## Current source of truth
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:README.md`

## Last verified
- date: 2026-06-25
- commit: `e56ecf05f68969cac2f1ec6ee8f25d44a463d12d`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- MCP memories record server ownership, transports, versions, and toolset constraints.

## Evidence
- `commit:e56ecf05f68969cac2f1ec6ee8f25d44a463d12d`
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Applies to
- The scope declared in this memory and the source-of-truth paths listed below.

## Source of truth
- The `Current source of truth` section above, plus current code, configuration, tests, git state, and live GitHub state where the memory explicitly references live release or repository surfaces.

## Invariants
- Code, configuration, tests, validators, git state, and live GitHub state override this memory when they disagree.

## Current State
- See `Facts` for current durable facts. Do not treat `Historical evidence`, old commit notes, or previous release entries as current state.

## Do Not Infer
- Do not infer runtime versions, product versions, commits, permissions, release state, security posture, or tool behavior from this memory without checking the source of truth.

## Update Triggers
- Update after verified changes to the source-of-truth files, runtime baselines, release tuple, validation gates, live release state, or durable agent workflow contracts.

## Validation Commands
- `python3 scripts/validate_serena_memory_schema.py --scope all --strict-mode strict-all`
- `python3 scripts/validate_serena_memory_semantics.py --scope all --strict-current-facts`
- `python3 scripts/validate_memory_freshness.py --scope all`

## Repair Procedure
- Re-read source-of-truth files, update only verified current facts, move stale facts to historical evidence, then rerun the validation commands.
