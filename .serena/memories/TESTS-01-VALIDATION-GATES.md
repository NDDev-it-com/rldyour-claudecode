<!-- Memory Metadata
Last updated: 2026-05-30
Last verified: 2026-05-30
Last commit: 65095d0dea64d267500877189faf22c7850ba2c2 chore(release): claude 1.1.8
Scope: validation gates and test suites
Area: TESTS
-->

# Validation Gates

## Scope
validation gates and test suites

## Current source of truth
- `path:scripts`
- `path:tests/test_flow_stop_state.py`
- `path:.github/workflows`
- `path:README.md`


## Source Of Truth
- `path:scripts`
- `path:.github/workflows`
- `path:README.md`

## Last verified
- date: 2026-05-30
- commit: `65095d0dea64d267500877189faf22c7850ba2c2`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Test memories record which suites and smoke tests prove the touched behavior.
- Current `tests/test_validate_instruction_docs.py` and `tests/test_validate_instruction_sync.py` cover Claude active instruction runtime-pin checks, fixture runtime baseline sources, and non-brittle sync claim counts.
- `tests/test_flow_stop_state.py` covers direct installed `flow_post_task_state.py`
  invocation without `CLAUDE_PLUGIN_ROOT`, `fullrepo_sync.py --status-json
  --local-only`, and Stop hook loop-guard behavior from a subdirectory.
- `uv run --with pytest python -m pytest` passed locally with 146 passed and
  1 skipped after the Stop hook loop-guard hardening.

## Evidence
- `commit:65095d0dea64d267500877189faf22c7850ba2c2`
- `path:scripts`
- `path:tests/test_flow_stop_state.py`
- `path:.github/workflows`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `CI-01-ACTIONS.md`
- `RELEASE-01-VALIDATION.md`
- `RUNTIME-01-BASELINES.md`

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
