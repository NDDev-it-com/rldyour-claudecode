<!-- Memory Metadata
Last updated: 2026-06-02
Last verified: 2026-06-02
Last commit: c4f9ed55eba393526d04e4a49b2c61122da9efd5 chore(release): claude 1.1.24
Scope: GitHub Actions and local CI policy
Area: CI
-->

# CI Actions

## Scope
GitHub Actions and local CI policy

## Current source of truth
- `path:.github/workflows`
- `path:README.md`


## Source Of Truth
- `path:.github/workflows`
- `path:README.md`

## Last verified
- date: 2026-06-02
- commit: `c4f9ed55eba393526d04e4a49b2c61122da9efd5`
- checked by: Codex ry-start docs/memory consistency audit

## Facts
- CI memories record which checks prove repository integrity and which checks are intentionally lightweight.
- Public adapter CI follows the root public/free policy: standard
  GitHub-hosted Ubuntu, Windows, and macOS runner labels are allowed for
  public repository smoke coverage, while paid/larger/private runner surfaces
  are forbidden.
- `cross-platform.yml` covers lightweight portability across
  `ubuntu-latest`, `windows-latest`, and `macos-latest`; runtime-heavy Claude
  and release checks remain on Ubuntu when the underlying validation is
  OS-independent.

## Evidence
- `commit:c4f9ed55eba393526d04e4a49b2c61122da9efd5`
- `path:.github/workflows`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `TESTS-01-VALIDATION-GATES.md`
- `RELEASE-01-VALIDATION.md`
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
