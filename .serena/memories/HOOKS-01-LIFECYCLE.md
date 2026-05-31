<!-- Memory Metadata
Last updated: 2026-05-31
Last verified: 2026-05-31
Last commit: 9d56a5fadabc6afe8f0311e6524bfa85c462b7ca chore(release): claude 1.1.15 (other)
Scope: deterministic hook lifecycle behavior
Area: HOOKS
-->

# HOOKS-01-LIFECYCLE

## Scope
deterministic hook lifecycle behavior

## Current source of truth
- `path:plugins/rldyour-flow/hooks`
- `path:scripts/smoke_hooks.sh`


## Source Of Truth
- `path:plugins/rldyour-flow/hooks`
- `path:scripts/smoke_hooks.sh`

## Last verified
- date: 2026-05-31
- commit: `9d56a5fadabc6afe8f0311e6524bfa85c462b7ca`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Hook memories record bounded, deterministic lifecycle behavior and the authoritative Stop owner.
- `plugins/rldyour-flow/hooks/stop_post_task_sync.sh` is an advisory gate:
  it may block with `exit 2`, but if Claude sends `stop_hook_active=true` and
  `.serena/.flow_sync_marker` already matches the current fingerprint, it
  exits `0` with a system message to avoid a Stop-hook loop.
- `plugins/rldyour-flow/scripts/flow_post_task_state.py` resolves sibling
  installed plugin scripts from its own `__file__` path before repo-relative
  fallbacks, so direct installed-script diagnostics and real hook execution use
  the same Serena/fullrepo state sources.
- Stop hook state sets `RLDYOUR_FLOW_STATE_LOCAL_ONLY=1` and
  `RLDYOUR_FULLREPO_STATUS_LOCAL_ONLY=1`; fullrepo status avoids fetch/network
  checks in the hot path and reports `network_checked=false`.

## Evidence
- `commit:9d56a5fadabc6afe8f0311e6524bfa85c462b7ca`
- `path:plugins/rldyour-flow/hooks`
- `path:plugins/rldyour-flow/scripts/flow_post_task_state.py`
- `path:plugins/rldyour-flow/scripts/fullrepo_sync.py`
- `path:scripts/smoke_hooks.sh`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `FLOW-01-SDLC.md`
- `SERENA-01-MEMORY-SYNC.md`
- `TESTS-01-VALIDATION-GATES.md`

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
