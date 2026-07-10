<!-- Memory Metadata
Last updated: 2026-07-10
Last verified: 2026-07-10
Last commit: 7c944516ba17ce1ea498b5f87cbd3fc0c36b4bfb feat(browser): enforce managed CloakBrowser skill boundary
Scope: release readiness, versioning, and artifact hygiene
Area: RELEASE
-->

# Release Validation

## Scope
release readiness, versioning, and artifact hygiene

## Current source of truth
- `path:VERSION`
- `path:CHANGELOG.md`
- `path:.github/workflows/release.yml`

## Last verified
- date: 2026-07-10
- commit: `7c944516ba17ce1ea498b5f87cbd3fc0c36b4bfb`
- checked by: Claude adapter 1.8.7 browser boundary release preparation

## Facts
- Current rldyour-claudecode adapter VERSION is `1.8.8`; the release workflow
  publishes only a pre-existing signed numeric tag created by root automation
  after exact-SHA branch CI is stable green.
- Release `1.8.8` retires the Webwright runtime and enforces the exact
  health-gated two-provider browser boundary across every browser skill while
  preserving Claude Code `2.1.206`, MCP pins, and reusable CI `0.5.1`.
- The local release evidence is 122 passing pytest tests plus the complete
  marketplace, schema, routing, hook, contract, runtime-pin, Ruff, Pyright, and
  release-state gates.
- Release memories record numeric versioning, tags, CI gates, and clean artifact hygiene.

## Evidence
- `commit:7324c1faa4fe2f79bd832333d2cfd520f374d2f9`
- `commit:7c944516ba17ce1ea498b5f87cbd3fc0c36b4bfb`
- `path:VERSION`
- `path:CHANGELOG.md`
- `path:.github/workflows/release.yml`

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
