<!-- Memory Metadata
Last updated: 2026-08-10
Last verified: 2026-08-10
Last commit: fa1a49c refactor(policy): track claude agent context on main
Scope: GitHub Actions and local CI policy
Area: CI
-->

# CI Actions

## Scope
GitHub Actions and local CI policy

## Current source of truth
- `path:.github/workflows`
- `path:README.md`

## Last verified
- date: 2026-08-10
- commit: `fa1a49c`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Every caller of a `ci-workflows` reusable that exposes a `runner` input passes `runner: ubuntu-latest` explicitly. This repository is public, so `pull_request` executes untrusted fork code; the reusable's `runner` default is a property of the **pinned commit**, and on current ci-workflows main 39 of 46 reusables default it to the estate's self-hosted `amsterdam` label. At the pin in use the default is still `ubuntu-latest`, so the explicit value is currently a no-op and becomes load-bearing at the next pin bump. On any pin bump, diff `inputs.runner.default` between the old and new commit.
- `ci-workflows` enforces the same rule for its own self-calls and its published examples, but nothing extends it to external consumers, so the constraint lives in this repository's `AGENTS.md` and `.claude/CLAUDE.md`.
- CI memories record which checks prove repository integrity and which checks are intentionally lightweight.

## Evidence
- `commit:123f862` explicit hosted runner in ci-workflows callers
- `commit:fa1a49c`
- `path:.github/workflows`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Applies to

- The scope and source-of-truth paths declared in this memory.

## Source of truth

- The `Current source of truth` entries above, plus current code, configuration, tests, git state, and live GitHub state where this memory references live release or repository surfaces.

## Invariants

- Current code, configuration, tests, validators, git state, and live GitHub state override this memory whenever they disagree.

## Current State

- Treat the `Facts` section as the current durable state. Do not treat historical evidence, superseded notes, or previous release entries as current.

## Do Not Infer

- Do not infer runtime versions, product versions, commits, permissions, release state, security posture, or tool behavior from this memory without checking the source of truth.

## Update Triggers

- Update after verified changes to the source-of-truth files, runtime baselines, release tuple, validation gates, live release state, or durable agent-workflow contracts.

## Validation Commands

- Run the rldyour control-plane Serena memory validators in strict mode: `validate_serena_memory_schema` (`--strict-mode strict-all`) and `validate_serena_memory_semantics` (`--strict-current-facts --strict-metadata-dates --strict-evidence-commits`).

## Repair Procedure

1. Re-read the source-of-truth files listed above.
2. Update only verified current facts; move stale facts into historical evidence.
3. Rerun the validation commands until green.
