<!-- Memory Metadata
Last updated: 2026-06-11
Last verified: 2026-06-11
Last commit: 3e3d0372bcccb8574676579083f134cff67a580a docs(claude): sync runtime issue template (docs)
Scope: verified current technical debt
Area: TECHDEBT
-->

# TECHDEBT-01-NOW

## Scope
verified current technical debt

## Current source of truth
- `path:README.md`
- `path:CHANGELOG.md`


## Source Of Truth
- `path:README.md`
- `path:CHANGELOG.md`

## Last verified
- date: 2026-06-11
- commit: `3e3d0372bcccb8574676579083f134cff67a580a`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Technical debt memories record verified open debt only when it has code/config evidence.

## Evidence
- `commit:3e3d0372bcccb8574676579083f134cff67a580a`
- `path:README.md`
- `path:CHANGELOG.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `ISSUES-01-VERIFIED-PROBLEMS.md`
- `TESTS-01-VALIDATION-GATES.md`
- `FUTURE-01-VISION.md`

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
