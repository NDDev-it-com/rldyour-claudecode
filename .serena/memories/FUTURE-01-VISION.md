<!-- Memory Metadata
Last updated: 2026-06-11
Last verified: 2026-06-11
Last commit: a16466172149789807afe373e202a4e4d3f2dd0b chore(release): claude 1.1.54 (other)
Scope: future architecture direction and scalability gravity
Area: FUTURE
-->

# Future Vision

## Scope
future architecture direction and scalability gravity

## Current source of truth
- `path:README.md`
- `path:config/rldyour-contract.json`


## Source Of Truth
- `path:README.md`
- `path:config/rldyour-contract.json`

## Last verified
- date: 2026-06-11
- commit: `a16466172149789807afe373e202a4e4d3f2dd0b`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Future memories record architectural trajectory and scale direction, not transient task queues.

## Evidence
- `commit:a16466172149789807afe373e202a4e4d3f2dd0b`
- `path:README.md`
- `path:config/rldyour-contract.json`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update only for durable architectural trajectory and scalability direction, not transient queues.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `CORE-01-INDEX.md`
- `ADR-01-CORE.md`
- `TECHDEBT-01-NOW.md`

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
