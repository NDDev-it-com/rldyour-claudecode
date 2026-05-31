<!-- Memory Metadata
Last updated: 2026-05-31
Last verified: 2026-05-31
Last commit: 2594a00cf9b23c237e4008bbfe47925fa8528ea9 chore(release): claude 1.1.17 (other)
Scope: deploy and rollout verification contracts
Area: DEPLOY
-->

# Deploy Runtime

## Scope
deploy and rollout verification contracts

## Current source of truth
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-deploy`


## Source Of Truth
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-deploy`

## Last verified
- date: 2026-05-31
- commit: `2594a00cf9b23c237e4008bbfe47925fa8528ea9`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Deploy memories record preflight, rollout, postflight, rollback, and sync requirements.

## Evidence
- `commit:2594a00cf9b23c237e4008bbfe47925fa8528ea9`
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-deploy`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `RELEASE-01-VALIDATION.md`
- `TESTS-01-VALIDATION-GATES.md`
- `SECURITY-01-OWASP.md`

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
