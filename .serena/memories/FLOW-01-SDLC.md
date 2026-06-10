<!-- Memory Metadata
Last updated: 2026-06-10
Last verified: 2026-06-10
Last commit: 785cdae480195d88a496523241f1a0854fc16957 chore(release): claude 1.1.52 (other)
Scope: rldyour SDLC command lifecycle
Area: FLOW
-->

# FLOW-01-SDLC

## Scope
rldyour SDLC command lifecycle

## Current source of truth
- `path:plugins/rldyour-flow`


## Source Of Truth
- `path:plugins/rldyour-flow`

## Last verified
- date: 2026-06-10
- commit: `785cdae480195d88a496523241f1a0854fc16957`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- `/ry-repair` has two modes: authoring repair for work projects, and
  consumer system sync for the control plane and adapter config repos
  (update the checkout FROM GitHub with ff-only pull plus submodule
  update, run check/apply-system, and never author changes into the
  repository; drift escalates to authoring repair only on explicit owner
  instruction). Machine-readable: root ry-repair-sync contract
  `repair_modes`.
- The cmux-orchestrator and cmux-worker skills live in the dedicated
  macOS-only `rldyour-orchestrator` surface; installers skip it on
  Linux/WSL/Windows. Orchestrator activation is declarative: the user
  states the role during `ry-init` (macOS + cmux session + installed
  surface preconditions), there is no orchestrator env switch, and auto
  role resolution treats non-worker terminals as standalone. Workers stay
  machine-identified through the worker launcher/layout environment.
- The rldyour-orchestrator plugin cmux-orchestrator and cmux-worker skills define cmux
  delegation mechanics: per-task `RLDYOUR_TASK_ID` and
  `RLDYOUR_WORKER_ALLOWED_PATHS` exported via `cmux send --surface`,
  observation via `cmux read-screen`/`cmux events`, and a mandatory
  report-plus-`cmux notify` completion signal (cmux emits no per-command
  exit-code event; verified against manaflow-ai/cmux v0.64.14).
- Flow memories record ry-init, ry-start, ry-newp, ry-review, ry-repair, ry-deploy, and ry-sync behavior.

## Evidence
- `commit:785cdae480195d88a496523241f1a0854fc16957`
- `path:plugins/rldyour-flow`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `HOOKS-01-LIFECYCLE.md`
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
