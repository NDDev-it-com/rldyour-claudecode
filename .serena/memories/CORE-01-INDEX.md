<!-- Memory Metadata
Last updated: 2026-05-18
Last commit: 66ef8f4 chore(release): bump VERSION + 9 plugins to 0.6.1
Scope: .serena/memories/**, plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py, plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md, plugins/rldyour-serena-mcp/agents/flow-memory-sync.md, scripts/smoke_serena_memory_taxonomy.sh, AGENTS.md, .claude/CLAUDE.md
Area: CORE
-->

# CORE-01-INDEX

## Purpose

Navigation map for the project knowledge base - the **brain** for any Claude Code session working on this marketplace, on a downstream project consuming this marketplace, or on a new project initialized via `/rldyour-flow:ry-newp`. Future Claude Code / Codex / GPT agents start here, then read only the topic memories relevant to the task.

Memories are the **source of durable knowledge**: vision, philosophy, patterns, business logic, domain knowledge, dependencies, technologies, errors + solutions, technical debt. Code and committed configuration are the **source of truth**; memories distill the durable facts that don't live in any single file.

## Source Of Truth

- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: emits `analysis.schema_version = 2`, `analysis.memory_taxonomy`, and scoped `analysis.memory_targets`.
- `plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md`: canonical memory naming, metadata, body template, sync workflow, and split rules.
- `plugins/rldyour-serena-mcp/agents/flow-memory-sync.md`: canonical writer contract for `.serena/memories` updates.
- `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh`: Stop advisory that passes taxonomy guidance to the orchestrator.
- `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: freshness scanner for `.serena/memories/**/*.md`.
- `scripts/smoke_serena_memory_taxonomy.sh`: targeted smoke for analyzer schema/targets, instruction sync, nested memories, Stop advisory, and fullrepo-managed acknowledgement.

## Active Memory Map (18 memories)

### Foundations - read first when joining the project

- [[CORE-01-INDEX]] (`CORE-01-INDEX.md`): this map and taxonomy contract.
- [[CORE-02-MARKETPLACE]] (`CORE-02-MARKETPLACE.md`): marketplace business logic, plugin boundaries, dependency graph, active catalog.
- [[PHILOSOPHY-01-QUALITY-FIRST]] (`PHILOSOPHY-01-QUALITY-FIRST.md`): distilled development vision - quality + scalability first, no hacks, no debt, May 2026 architecture + tooling defaults; **universal applicability** for any project.
- [[PATTERNS-01-CANONICAL]] (`PATTERNS-01-CANONICAL.md`): copy-from-here implementation patterns - file naming, identifier conventions, SKILL/agent/command/hook frontmatter, cross-plugin paths, input validation, sanitization markers, memory file pattern, commit message pattern.

### Infrastructure - Claude Code platform integration

- [[CLAUDECODE-01-PLUGIN-CANON]] (`CLAUDECODE-01-PLUGIN-CANON.md`): verified Claude Code plugin, skill, agent, hook, CLI, and MCP canon used by this repo.
- [[MCP-01-TRANSPORT]] (`MCP-01-TRANSPORT.md`): MCP transport ownership, 13 pinned servers, runtime/version smoke contracts.
- [[SERENA-01-MEMORY-SYNC]] (`SERENA-01-MEMORY-SYNC.md`): Serena memory freshness, analyzer schema, sync markers, canonical writer flow.
- [[HOOKS-01-LIFECYCLE]] (`HOOKS-01-LIFECYCLE.md`): Claude Code hook lifecycle, Stop gates, skip flags, coordination between Serena and flow.

### Plugin Domains - one memory per consumer-facing domain

- [[BROWSER-01-WORKFLOW]] (`BROWSER-01-WORKFLOW.md`): `rldyour-browser` - Playwright vs Chrome DevTools routing, validation + debug workflows, artifact rules.
- [[DESIGN-01-WORKFLOW]] (`DESIGN-01-WORKFLOW.md`): `rldyour-design` - end-to-end Figma → tokens → FSD → shadcn/ui → ReactBits → browser validation.
- [[EXPLORE-01-RESEARCH]] (`EXPLORE-01-RESEARCH.md`): `rldyour-explore` - tech-research (Context7/DeepWiki/Grep MCP-first), web-research (dated cited sources), `ry-explore` deep research subagent (opus[1m], max effort, 90 maxTurns).
- [[LSPS-01-LANGUAGE-SERVERS]] (`LSPS-01-LANGUAGE-SERVERS.md`): `rldyour-lsps` - 16 language areas via 15 `.lsp.json` runtime entries (Python/TS/Rust/Dart/Go/C/C++/Qt/QML/YAML/Docker/HTML/CSS/Bash/JSON/TOML/Markdown; `typescript_vts` optional, matrix-only), Serena integration policy.
- [[RULES-01-POLICY]] (`RULES-01-POLICY.md`): `rldyour-rules` - 7 rule areas (quality-first, architecture-boundaries, dependency-compatibility, implementation-discipline, verification-quality-gates, project-instructions-policy, ry-rules-review) + 6 references.
- [[SECURITY-01-OWASP]] (`SECURITY-01-OWASP.md`): `rldyour-security` - OWASP Top 10 2025 implementation guidance + Mythos-style defensive `ry-sec-review`.
- [[FLOW-01-SDLC]] (`FLOW-01-SDLC.md`): `rldyour-flow` - ry-init/start/newp/review/deploy + 6 reviewer subagents + fullrepo lifecycle + worktree contract + post-task sync.

### Process - release, instructions, technical debt

- [[DOCS-01-INSTRUCTIONS]] (`DOCS-01-INSTRUCTIONS.md`): AGENTS.md and .claude/CLAUDE.md policy, line budgets, sync rules, agent-only fullrepo lifecycle.
- [[RELEASE-01-VALIDATION]] (`RELEASE-01-VALIDATION.md`): versioning, changelog, validation harness, plugin tagging.
- [[TECHDEBT-01-NOW]] (`TECHDEBT-01-NOW.md`): open risks (R1-R4; R5 closed as D19), closed debt patterns (D1-D80), anti-regression guidance.

## Memory Map by Reading Intent

**"Joining the project, need orientation"** → [[CORE-01-INDEX]] (this) → [[CORE-02-MARKETPLACE]] → [[PHILOSOPHY-01-QUALITY-FIRST]] → [[PATTERNS-01-CANONICAL]].

**"Need to write a new skill / agent / command / hook"** → [[PATTERNS-01-CANONICAL]] → [[CLAUDECODE-01-PLUGIN-CANON]] → relevant domain memory.

**"Need to understand what `rldyour-X` plugin does"** → [[CORE-02-MARKETPLACE]] (plugin boundaries) → corresponding domain memory ([[BROWSER-01-WORKFLOW]] / [[DESIGN-01-WORKFLOW]] / [[EXPLORE-01-RESEARCH]] / [[LSPS-01-LANGUAGE-SERVERS]] / [[RULES-01-POLICY]] / [[SECURITY-01-OWASP]] / [[FLOW-01-SDLC]]).

**"Need to validate a change"** → [[RULES-01-POLICY]] (`verification-quality-gates`) → relevant domain memory → [[CLAUDECODE-01-PLUGIN-CANON]] (validation commands).

**"Need to release"** → [[RELEASE-01-VALIDATION]] → [[FLOW-01-SDLC]] (`flow-post-task-sync`) → [[DOCS-01-INSTRUCTIONS]] (instruction-doc sync).

**"Need to fix tech debt or understand past issue"** → [[TECHDEBT-01-NOW]] (open + closed).

**"Need to understand a hook / lifecycle / Stop gate"** → [[HOOKS-01-LIFECYCLE]] → [[FLOW-01-SDLC]] (post-task sync).

**"Need to do research"** → [[EXPLORE-01-RESEARCH]] → [[RULES-01-POLICY]] (`dependency-compatibility-policy` for May 2026 standards).

**"Need MCP transport facts"** → [[MCP-01-TRANSPORT]] → relevant domain memory ([[BROWSER-01-WORKFLOW]] / [[DESIGN-01-WORKFLOW]] / [[EXPLORE-01-RESEARCH]] / [[SECURITY-01-OWASP]] / [[SERENA-01-MEMORY-SYNC]]).

## Contracts And Data

- **File naming**: `AREA-NN-SLUG.md` on disk and `AREA-NN-SLUG` as Serena memory name (e.g., `PHILOSOPHY-01-QUALITY-FIRST.md` → `PHILOSOPHY-01-QUALITY-FIRST`).
- **`CORE-01-INDEX.md` must be updated** whenever a memory is added, deleted, renamed, or split.
- **Numbering is stable**: add the next number in an area; do not renumber existing memories unless task is explicit taxonomy migration.
- **Memories are durable facts only**: exact paths, entry points, behaviour, contracts, invariants, change rules, verification commands, known gaps.
- **Forbidden in memories**: chat history, speculation, secrets, raw tokens, runtime snapshots, raw logs, credentials, broad TODO lists, "likely" / "probably" statements (exception: severity-class descriptive terms in [[SECURITY-01-OWASP]] Mythos-style review guidance).
- **Cross-references** via `[[AREA-NN-SLUG]]` (double-bracket form; resolves via Serena memory listing). Example: `[[CORE-01-INDEX]]` in another memory points back to this index.
- **Source of truth hierarchy**: code at HEAD > committed tests > git diff > existing memory content. Memories are input to verify, not facts to trust blindly.

## Change Rules

- For any meaningful code, plugin, workflow, config, architecture, validation, release, hook, or docs change: run the memory sync flow before final delivery.
- Prefer splitting broad memories over appending unrelated facts. A future agent should be able to read one topic file for one scoped question.
- Technical debt and implementation mistakes belong in [[TECHDEBT-01-NOW]] unless the area grows large enough to split into `TECHDEBT-02-*`.
- Long source-backed research belongs in `.serena/research/`; active implementation facts distilled from research belong in the relevant numbered memory.
- Areas (CORE, CLAUDECODE, MCP, SERENA, HOOKS, FLOW, DOCS, RELEASE, TECHDEBT, PHILOSOPHY, PATTERNS, BROWSER, DESIGN, EXPLORE, LSPS, RULES, SECURITY) are stable. Add new areas only when a genuinely new scope emerges that doesn't fit existing taxonomy.

## Cross-References

All 18 active memories are catalogued in the Active Memory Map above. This index IS the cross-reference graph entry point; each `[[AREA-NN-SLUG]]` link in the Active Memory Map resolves to an individual topic memory.

- Memory sync contract: [[SERENA-01-MEMORY-SYNC]] (includes ADR-0011 agent-instruction knowledge-equivalence, 0.5.2).
- Implementation patterns: [[PATTERNS-01-CANONICAL]].
- Technical debt and risk register: [[TECHDEBT-01-NOW]].
- Release and versioning: [[RELEASE-01-VALIDATION]].

## Verification

- `python3 plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py --from-ref HEAD --to-ref HEAD`: proves empty diffs produce no memory targets while still exposing the taxonomy.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: proves analyzer schema/targets, agent-instruction sync relevance, nested memory freshness, Stop advisory taxonomy, fullrepo-managed acknowledgement.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: proves freshness state and recursive memory scanning. Should report `memory_count: 18`, `is_current: True`, `memory_match_reason: direct-head-reference` at HEAD `b468c21`.
- `python3 scripts/validate_instruction_docs.py --require-agent-docs`: proves AGENTS.md and `.claude/CLAUDE.md` are present and within policy.
- `python3 scripts/validate_agent_tools.py`: proves agent `tools:` allowlist invariants ([[TECHDEBT-01-NOW]] R4 mitigation).
- `bash scripts/validate_marketplace.sh`: full harness covering all of the above plus frontmatter/JSON/Python/shell syntax checks and MCP runtime drift.
