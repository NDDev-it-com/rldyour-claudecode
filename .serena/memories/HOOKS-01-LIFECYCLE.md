<!-- Memory Metadata
Last updated: 2026-08-04
Last verified: 2026-08-04
Last commit: 6d64f43 feat(rtk)!: remove the rldyour-rtk plugin and every rtk declaration
Scope: deterministic hook lifecycle behavior
Area: HOOKS
-->

# Hook Lifecycle

## Scope
deterministic hook lifecycle behavior

## Current source of truth
- `path:plugins/rldyour-flow/hooks`
- `path:scripts/smoke_hooks.sh`

## Last verified
- date: 2026-08-04
- commit: `6d64f43`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Hook memories record bounded, deterministic lifecycle behavior and the authoritative Stop owner.
- No plugin owns a `PreToolUse` hook. That event observes every shell command in a session, so registering one there is an explicit owner decision rather than a routine change. Hook owners are `rldyour-flow` (the single registered Stop dispatcher) and `rldyour-serena-mcp`.

## Evidence
- `commit:fa1a49c`
- `path:plugins/rldyour-flow/hooks`
- `path:scripts/smoke_hooks.sh`

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
