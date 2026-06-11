<!-- Memory Metadata
Last updated: 2026-06-11
Last verified: 2026-06-11
Last commit: 7938cd1af4dda513d3e1c8ccc8b35266b3f5e061 chore(release): claude 1.1.55 (other)
Scope: security posture and blocking/warning policy
Area: SECURITY
-->

# SECURITY-01-OWASP

## Scope
security posture and blocking/warning policy

## Current source of truth
- `path:plugins/rldyour-security`
- `path:README.md`


## Source Of Truth
- `path:plugins/rldyour-security`
- `path:README.md`

## Last verified
- date: 2026-06-11
- commit: `7938cd1af4dda513d3e1c8ccc8b35266b3f5e061`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Security memories record block/warn/review classes and defensive-only review policy.

## Evidence
- `commit:7938cd1af4dda513d3e1c8ccc8b35266b3f5e061`
- `path:plugins/rldyour-security`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `RULES-01-POLICY.md`
- `MCP-01-TRANSPORT.md`
- `CI-01-ACTIONS.md`

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
