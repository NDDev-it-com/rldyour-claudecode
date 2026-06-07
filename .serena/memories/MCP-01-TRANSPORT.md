<!-- Memory Metadata
Last updated: 2026-06-07
Last verified: 2026-06-07
Last commit: c680802c9b3554b1f00e479ecc27cafc719d6264 chore(release): claude 1.1.33 (other)
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
- date: 2026-06-07
- commit: `c680802c9b3554b1f00e479ecc27cafc719d6264`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- MCP memories record server ownership, transports, versions, and toolset constraints.
- Dart/Flutter MCP is provided by the local Dart SDK. The Claude adapter now
  pins the owner host runtime to Dart SDK `3.12.0` in
  `config/mcp-runtime-versions.env`.

## Evidence
- `commit:c680802c9b3554b1f00e479ecc27cafc719d6264`
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
