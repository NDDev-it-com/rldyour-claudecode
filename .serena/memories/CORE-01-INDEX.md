<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: bf54d02 chore(release): cut 0.1.6 with agent + shell + docs changes
Scope: .serena/memories/**, plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py, plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md, plugins/rldyour-serena-mcp/agents/flow-memory-sync.md, scripts/smoke_serena_memory_taxonomy.sh, AGENTS.md, .claude/CLAUDE.md
Area: CORE
-->

# CORE-01-INDEX

## Purpose

Navigation map for the project knowledge base. Future GPT, Codex, and Claude Code agents should start here, then read only the topic memories relevant to the task.

## Source Of Truth

- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: emits `analysis.schema_version = 2`, `analysis.memory_taxonomy`, and scoped `analysis.memory_targets`.
- `plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md`: canonical memory naming, metadata, body template, sync workflow, and split rules.
- `plugins/rldyour-serena-mcp/agents/flow-memory-sync.md`: canonical writer contract for `.serena/memories` updates.
- `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh`: Stop advisory that passes taxonomy guidance to the orchestrator.
- `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: freshness scanner for `.serena/memories/**/*.md`.
- `scripts/smoke_serena_memory_taxonomy.sh`: targeted smoke for analyzer schema/targets, instruction sync, nested memories, Stop advisory, and fullrepo-managed acknowledgement.

## Active Memory Map

- `CORE-01-INDEX.md`: this map and taxonomy contract.
- `CORE-02-MARKETPLACE.md`: marketplace business logic, plugin boundaries, dependency graph, active catalog.
- `CLAUDECODE-01-PLUGIN-CANON.md`: verified Claude Code plugin, skill, agent, hook, CLI, and MCP canon used by this repo.
- `MCP-01-TRANSPORT.md`: MCP transport ownership, pinned servers, runtime/version smoke contracts.
- `SERENA-01-MEMORY-SYNC.md`: Serena memory freshness, analyzer schema, sync markers, canonical writer flow.
- `HOOKS-01-LIFECYCLE.md`: Claude Code hook lifecycle, Stop gates, skip flags, coordination between Serena and flow.
- `FLOW-01-SDLC.md`: rldyour-flow SDLC workflows, fullrepo, worktrees, branch/publish sequence.
- `DOCS-01-INSTRUCTIONS.md`: AGENTS.md and .claude/CLAUDE.md policy, line budgets, sync rules.
- `RELEASE-01-VALIDATION.md`: versioning, changelog, validation and release checks.
- `TECHDEBT-01-NOW.md`: open risks, closed error patterns, anti-regression guidance.

## Contracts And Data

- File naming contract: `AREA-01-SLUG.md` on disk and `AREA-01-SLUG` as the Serena memory name.
- `CORE-01-INDEX.md` must be updated whenever a memory is added, deleted, renamed, or split.
- Numbering is stable. Add the next number in an area; do not renumber existing memories unless the task is an explicit taxonomy migration.
- Memories are durable facts only: exact paths, entry points, behavior, contracts, invariants, change rules, verification commands, and known gaps.
- Do not store chat history, speculation, secrets, runtime snapshots, raw logs, credentials, or broad TODO lists in memories.
- Code and committed configuration are the source of truth. Existing memories are input to verify, not facts to trust.

## Change Rules

- For any meaningful code, plugin, workflow, config, architecture, validation, release, hook, or docs change, run the memory sync flow before final delivery.
- Prefer splitting broad memories over appending unrelated facts. A future agent should be able to read one topic file for one scoped question.
- Technical debt and implementation mistakes belong in `TECHDEBT-01-NOW.md` unless the area grows large enough to split into `TECHDEBT-02-*`.
- Long source-backed research belongs in `.serena/research/`; active implementation facts distilled from research belong in the relevant memory.

## Verification

- `python3 plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py --from-ref HEAD --to-ref HEAD`: proves empty diffs produce no memory targets while still exposing the taxonomy.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: proves analyzer schema/targets, agent-instruction sync relevance, nested memory freshness, Stop advisory taxonomy, and fullrepo-managed acknowledgement behavior.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: proves freshness state and recursive memory scanning.
- `python3 scripts/validate_instruction_docs.py --require-agent-docs`: proves AGENTS.md and `.claude/CLAUDE.md` are present and within policy.
