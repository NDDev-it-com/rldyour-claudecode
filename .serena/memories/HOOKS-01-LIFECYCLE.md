<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: cbab06d96f803f0a819b9aaa6f3bdfc2b42f4708 chore(release): claude 1.1.1
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
- date: 2026-05-29
- commit: `cbab06d96f803f0a819b9aaa6f3bdfc2b42f4708`
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
- `commit:cbab06d96f803f0a819b9aaa6f3bdfc2b42f4708`
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
