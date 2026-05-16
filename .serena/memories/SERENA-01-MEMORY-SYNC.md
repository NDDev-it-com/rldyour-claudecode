<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: e5a7694 docs(flow): align reviewer-protocol terminology and flow-lifecycle
Scope: plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py, plugins/rldyour-serena-mcp/scripts/serena_memory_state.py, plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh, plugins/rldyour-serena-mcp/hooks/*.sh, plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md, plugins/rldyour-serena-mcp/agents/flow-memory-sync.md, scripts/smoke_serena_memory_taxonomy.sh
Area: SERENA
-->

# SERENA-01-MEMORY-SYNC

## Purpose

Durable contract for Serena memory freshness, impact analysis, scoped sync, and fact-only memory writing.

## Source Of Truth

- `plugins/rldyour-serena-mcp/hooks/prepare_auto_sync.sh`: records `.serena/.auto_sync_head` before commit-like Bash commands.
- `plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh`: writes `.serena/.serena_sync_state.json` after commit-like commands when sync-relevant files changed.
- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: classifies changed paths, emits schema v2 analysis, memory taxonomy, areas, risk profile, and memory targets.
- `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: computes memory freshness against HEAD and exposes `analysis` + `analysis_source`.
- `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh`: Stop gate that blocks with `exit 2` when memories are stale.
- `plugins/rldyour-serena-mcp/agents/flow-memory-sync.md`: canonical memory writer contract.
- `plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md`: main-session fallback workflow and memory template.
- `plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`: acknowledges successful sync and clears runtime markers.
- `scripts/smoke_serena_memory_taxonomy.sh`: focused regression smoke for this memory contract.

## Current Behavior

- Analyzer output uses `analysis.schema_version = 2` and always includes `analysis.memory_taxonomy`.
- Memory taxonomy at HEAD: `filename_pattern = AREA-01-SLUG.md`, `index_memory = CORE-01-INDEX.md`, stable areas `CORE`, `CLAUDECODE`, `MCP`, `SERENA`, `HOOKS`, `FLOW`, `DOCS`, `RELEASE`, `TECHDEBT`.
- Empty commit ranges produce empty `memory_targets` and `candidate_memory_focus`, while still exposing taxonomy.
- Agent-instruction-only commits are sync-relevant. `AGENTS.md`, `.claude/**`, `.agents/**`, `.cursor/rules/**`, `.github/instructions/**`, `.github/prompts/**`, `.aider*`, and similar instruction paths are not treated as Serena knowledge no-ops.
- Only `.serena/memories/`, `.serena/plans/`, `.serena/research/`, `.serena/newproj/`, `.serena/deploy/`, and explicit runtime markers are excluded from sync-required path calculation.
- Analyzer targets include `CLAUDECODE-01-PLUGIN-CANON.md` for plugin component contracts and Claude Code instruction context.
- Docs/references changes under `rldyour-serena-mcp` target `SERENA-01-MEMORY-SYNC.md`, `HOOKS-01-LIFECYCLE.md`, and `CORE-02-MARKETPLACE.md`, so docs-only contract edits do not fall back to broad baseline memories.
- `serena_memory_state.py` scans `.serena/memories/**/*.md` so nested memories remain freshness-aware if future taxonomy uses subdirectories.
- `commit_serena_knowledge.sh` uses `git status --porcelain -uall`, filters runtime marker files, clears markers only when memory state matches HEAD, and refuses fullrepo-managed stale memories even when the normal branch has no tracked knowledge diff.

## Contracts And Data

- `.serena/.serena_sync_state.json` contains: `version`, `required`, `reason`, `created_at`, `previous_head_full`, `head_full`, `head_sha`, `changed_files`, `non_knowledge_changed_files`, and `analysis`.
- `analysis.memory_targets` is advisory scope, not final truth. The writer must verify each claim against code/config/tests at HEAD.
- `analysis_source` emitted by `serena_memory_state.py` can be `sync_marker`, `sync_marker_ref_range:*`, `newest_sync_ref_range:*`, `path_list`, or `none`.
- A memory counts as current when it directly mentions `Last commit: <HEAD_SHA>` or when the newest synced memory commit equals HEAD; marker state can force stale.
- `flow-memory-sync` is the only automated writer for `.serena/memories`. Hooks compute scope and block Stop; they do not write durable facts.
- `.serena/plans/` and `.serena/research/` are written by the main `serena-memory-sync` workflow only when a reusable plan or source-backed research archive is explicitly needed.

## Invariants

- Do not pass large analyzer or state JSON as shell argv. `mark_sync_required.sh` uses a temp file and `stop_memory_sync.sh` reads state JSON through stdin to avoid shell limits.
- Do not write memories from `ry-init` unless explicitly requested or a Stop/stale-memory hook requires it.
- Do not store runtime observations as snapshot memories. Distill durable contracts into topic files.
- Every touched memory must contain a metadata block with `Last commit: <sha> <message>`.
- Existing memory content must be verified before preservation; stale claims are corrected or removed.

## Change Rules

- Any change to analyzer schema, memory taxonomy, marker payloads, Stop hook parsing, `serena_memory_state.py`, `commit_serena_knowledge.sh`, `serena-memory-sync` skill, or `flow-memory-sync` agent must update this memory and `CORE-01-INDEX.md` if the taxonomy/map changes.
- If analyzer output shape changes, bump plugin version and update `CHANGELOG.md`.
- If a new durable area is introduced, add it to `analysis.memory_taxonomy`, create/rename the numbered memory, and update `CORE-01-INDEX.md`.
- Add a targeted case to `scripts/smoke_serena_memory_taxonomy.sh` for every new analyzer target family or freshness edge case.

## Verification

- `python3 plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py --from-ref HEAD --to-ref HEAD`: verifies empty-diff/no-target behavior and taxonomy emission.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies schema v2, analyzer target routing, instruction-only sync marker behavior, recursive memory scanning, Stop advisory taxonomy, Stop loop guard, and fullrepo-managed acknowledgement/refusal.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: verifies freshness, memory count, `analysis`, and `analysis_source`.
- `bash -n plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`: verifies shell syntax.
- `bash scripts/smoke_hooks.sh`: verifies static hook registration, skip flags, and defensive guards.
- `bash scripts/validate_marketplace.sh`: includes `scripts/smoke_serena_memory_taxonomy.sh` at HEAD.

## Known Gaps

- Analyzer area/risk classification is heuristic and must remain advisory. The memory writer must verify exact facts from source files before writing.
- Hooks intentionally do not write memories; skipping the `flow-memory-sync` pass can still leave memories stale until Stop is handled.

## Cross-References

- Memory taxonomy map: [[CORE-01-INDEX]] (18 memories, area definitions, file naming contract).
- Hook coordination: [[HOOKS-01-LIFECYCLE]] (Stop gate, loop guard, skip flags).
- R5 divergence guard (bootstrap footgun): [[TECHDEBT-01-NOW]] R5 / D19.
- R2 (explicit sync pass requirement): [[TECHDEBT-01-NOW]] R2.
- Memory file pattern and metadata template: [[PATTERNS-01-CANONICAL]] Memory File Pattern.
- Agent tools allowlist (flow-memory-sync): [[CLAUDECODE-01-PLUGIN-CANON]] Subagent Matrix.
- Post-task sync workflow: [[FLOW-01-SDLC]].
- MCP transport (serena server): [[MCP-01-TRANSPORT]].
