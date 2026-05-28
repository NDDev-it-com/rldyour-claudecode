<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: 2528040d67a5341d7b7feb2b447ebe9523713318
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
- date: 2026-05-28
- commit: `2528040d67a5341d7b7feb2b447ebe9523713318`
- checked by: Codex ry-start Claude Stop hook loop-guard hardening

## Facts
- Test memories record which suites and smoke tests prove the touched behavior.
- Current `tests/test_validate_instruction_docs.py` and `tests/test_validate_instruction_sync.py` cover Claude active instruction runtime-pin checks, fixture runtime baseline sources, and non-brittle sync claim counts.
- `tests/test_flow_stop_state.py` covers direct installed `flow_post_task_state.py`
  invocation without `CLAUDE_PLUGIN_ROOT`, `fullrepo_sync.py --status-json
  --local-only`, and Stop hook loop-guard behavior from a subdirectory.
- `uv run --with pytest python -m pytest` passed locally with 146 passed and
  1 skipped after the Stop hook loop-guard hardening.

## Evidence
- `commit:2528040d67a5341d7b7feb2b447ebe9523713318`
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
