<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: f4510fb feat(serena-mcp): add scoped memory sync analysis
Scope: plugins/rldyour-serena-mcp/hooks/*.sh, plugins/rldyour-serena-mcp/scripts/*.py, plugins/rldyour-serena-mcp/skills/*.md, plugins/rldyour-serena-mcp/agents/flow-memory-sync.md, .serena/.serena_sync_state.json
Area: CORE
-->

# Serena Memory Sync Protocol 2026-05

## Purpose

Provide one durable, machine-readable protocol for when Serena memories are stale,
what changed scope should be analyzed, and where memory updates should be written after
project/marketplace behavior changes.

## Source Of Truth

- `plugins/rldyour-serena-mcp/hooks/prepare_auto_sync.sh` — writes `.serena/.auto_sync_head`
  before commit-like Bash tool calls.
- `plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh` — computes changed scope and writes
  `.serena/.serena_sync_state.json` when non-knowledge files changed.
- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py` — maps changed paths into stable
  impact areas and memory targets. Empty commit ranges produce empty memory targets.
- `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` — checks freshness against HEAD
  and sync marker, and emits `analysis` + `analysis_source` for downstream memory-sync planning.
- `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh` — blocking gate on Stop when memories are stale.
- `plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh` — acknowledges cleared sync state.
- `plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md` and
  `plugins/rldyour-serena-mcp/agents/flow-memory-sync.md` — execution contract for AI-driven memory writes.

## Entry Points

- `git commit`/`git merge`/`git cherry-pick`/`git rebase`/`git am` command inside Bash.
- `Stop` event in Claude Code lifecycle.

## Current Behavior

1. `prepare_auto_sync.sh` stores current `HEAD` in `.serena/.auto_sync_head` when the
   detected Bash command is commit-like.
2. After the commit-like command finishes, `mark_sync_required.sh`:
  - runs `analyze_sync_scope.py --from-ref <pre_head> --to-ref <head>`,
  - stores `analysis` payload into `.serena/.serena_sync_state.json`,
  - computes `analysis.changed_files`,
  - computes `non_knowledge_changed_files` with the same agent-only path families used by fullrepo
    policy (`.claude/`, `.cursor/rules/`, `.agents/**`, `.gemini/`, `.roo/`, `.windsurf/`,
    `.openhands/`, `.github/instructions/**`, `.github/prompts/**`, `.aider*`, and `.serena`
    knowledge/runtime paths),
  - sets `required=true` only when `non_knowledge_changed_files` is non-empty.
3. If there are no non-knowledge changes, `mark_sync_required.sh` exits early and no stale marker is required.
4. On Stop, `serena_memory_state.py` is evaluated:
   - if memory is stale, `stop_memory_sync.sh` blocks with `exit 2`,
   - prints analysis-derived focus (risk profile, high-priority areas, candidate memory targets, analysis source).
5. `flow-memory-sync` subagent is the canonical writer and should use:
   - `sync_state.changed_files`,
   - `analysis.areas`,
   - `analysis.memory_targets`
   to bound edit surface to durable contracts.
6. Sync concludes via `commit_serena_knowledge.sh`, which clears runtime markers
   (`.serena/.sync_marker`, `.serena/.serena_sync_state.json`, `.serena/.auto_sync_head`)
   and updates `serena_memory_state` via direct HEAD mention in edited memories.

## Contracts

- `.serena/.serena_sync_state.json` structure:
  - `required` (`bool`)
  - `previous_head_full`
  - `head_full`
  - `head_sha`
  - `changed_files` (`list[str]`)
  - `non_knowledge_changed_files` (`list[str]`)
  - `analysis` (object from `analyze_sync_scope.py`)
    - `analysis.schema_version` (`1`) is the payload contract version.
    - `analysis.areas` and `analysis.memory_targets` are primary for focused scope.
    - `analysis.risk_profile.sync_focus` and `analysis.areas_summary` are advisory only.
  - `serena_memory_state.py` also emits `analysis_source` (`sync_marker`, `sync_marker_ref_range:*`, `newest_sync_ref_range:*`, `path_list`, or `none`) so downstream guidance can explain how the scope was derived.
- `serena_memory_state.py` treats memory freshness by:
  - explicit `Last commit: <sha>` reference in memory files (`sync_state`),
  - freshest synced memory commit,
  - sync marker files when present.

## Change Rules

- Any change to `hooks/*.sh`, `scripts/serena_memory_state.py`, `plugins/rldyour-serena-mcp/README.md`,
  `.serena` marker handling, or `flow-memory-sync` execution contract must also update this memory.
- If the analyzer output format changes, bump plugin version and adjust both
  `flow-memory-sync` / `serena-memory-sync` instructions.
- If analyzer classification changes, keep `mark_sync_required.sh`, `serena_memory_state.py`,
  `serena-memory-sync/SKILL.md`, and `flow-memory-sync.md` in lockstep.
- If `.serena/.serena_sync_state.json` structure changes, update any hardcoded key assumptions
  in `stop_memory_sync.sh` and `serena-memory-sync` instructions in the same change.
- Marker payloads are advisory until the `flow-memory-sync` subagent completes a commit/state-sync run; do not treat stale-analysis output as final source-of-truth.

## Invariants

- Marker-driven workflow stays in hooks; no hook performs high-blast-radius git operations.
- Large state JSON is read from files/stdin, not passed as a command-line JSON blob, so large diffs
  do not hit shell argument limits.
- `flow-memory-sync` is the only automated writer for durable `.serena/memories` updates.
- Memory updates must remain fact-only; claims must be code- or test-verified at `HEAD`.
- `.serena` runtimes are excluded from tracked project knowledge commits when fullrepo sync handles them.

## Verification

- `python3 plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py --from-ref <a> --to-ref <b>`
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`
- `bash plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh` with commit-like hook input payload shape
- `bash plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh` from stale state
- `bash plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`

## Known Gaps

- `analyze_sync_scope.py` risk scoring is heuristic; high-impact classification is a best-effort
  guide and must be validated against explicit source-of-truth files in the same sync pass.
- `flow-memory-sync` remains the writer; hooks intentionally only compute scope and block Stop.
