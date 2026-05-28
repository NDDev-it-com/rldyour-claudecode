<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: cf5b25eb348ff012a2bcbbd2e4e61308207d674e test: avoid brittle Claude sync claim count
Scope: validation gates and test suites
Area: TESTS
-->

# Validation Gates

## Scope
validation gates and test suites

## Current source of truth
- `path:scripts`
- `path:.github/workflows`
- `path:README.md`


## Source Of Truth
- `path:scripts`
- `path:.github/workflows`
- `path:README.md`

## Last verified
- date: 2026-05-28
- commit: `cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- Test memories record which suites and smoke tests prove the touched behavior.
- Current `tests/test_validate_instruction_docs.py` and `tests/test_validate_instruction_sync.py` cover Claude active instruction runtime-pin checks, fixture runtime baseline sources, and non-brittle sync claim counts.
- `uv run --with pytest python -m pytest` passed locally with 143 passed and 1 skipped after the Claude instruction validator stabilization.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- `path:scripts`
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
