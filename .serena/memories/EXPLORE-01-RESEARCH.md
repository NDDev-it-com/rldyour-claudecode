<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 065d6a4 fix(security): close 6 findings from flow-security-review (F-1..F-6)
Scope: plugins/rldyour-explore/skills/tech-research/SKILL.md, plugins/rldyour-explore/skills/web-research/SKILL.md, plugins/rldyour-explore/agents/ry-explore.md, plugins/rldyour-explore/commands/ry-explore.md, plugins/rldyour-mcps/.mcp.json (context7 + deepwiki + grep entries)
Area: EXPLORE
-->

# EXPLORE-01-RESEARCH

## Purpose

Research workflow contract for `rldyour-explore`. Three MCP transports - Context7 (official docs), DeepWiki (repo architecture), grep.app (production code at scale) - cover authoritative technical research; WebSearch + WebFetch cover dated, source-cited general web research; `ry-explore` agent handles deep multi-source research (opus[1m], max effort, 90 maxTurns) with cross-validation requirement.

Quality-first invariant ([[PHILOSOPHY-01-QUALITY-FIRST]]): **single-source claims for critical decisions are not acceptable**. Cross-validate against at least one independent source for non-trivial conclusions.

## Source Of Truth

- `plugins/rldyour-explore/skills/tech-research/SKILL.md`: routing between Context7 / DeepWiki / Grep MCP-first.
- `plugins/rldyour-explore/skills/web-research/SKILL.md`: WebSearch + WebFetch with dated, cited authoritative sources.
- `plugins/rldyour-explore/agents/ry-explore.md`: deep-research specialist (opus[1m], max effort, 90 maxTurns, color cyan, explicit `tools:` allowlist for read-only research).
- `plugins/rldyour-explore/commands/ry-explore.md`: slash command `/rldyour-explore:ry-explore <topic>` (uses `context: fork` + `agent: ry-explore`).
- `plugins/rldyour-mcps/.mcp.json`:
  - `context7`: `bunx @upstash/context7-mcp@2.2.5` - official docs / API reference. Requires `CONTEXT7_API_KEY` env.
  - `deepwiki`: HTTP `https://mcp.deepwiki.com/mcp` - repo architecture, design rationale.
  - `grep`: HTTP `https://mcp.grep.app` - production code patterns at scale across GitHub.

## Tool Routing Decision Tree

### `tech-research` (MCP-first, authoritative)

| Question type | Primary MCP | Tool |
|---|---|---|
| Library / framework API lookup | **Context7** | `resolve-library-id` → `query-docs` |
| Version-specific behavior, breaking changes, migration | **Context7** | `query-docs` with version anchor |
| Open-source repo architecture / design notes / module layout | **DeepWiki** | `ask_question`, `read_wiki_structure`, `read_wiki_contents` |
| Real-world code patterns at scale across GitHub | **grep.app** | `searchGitHub` |
| Comparing implementation approaches across libraries | Both + Grep | DeepWiki for design rationale + Grep for production patterns |
| Verifying potentially-stale docs against current code | **Grep** | `searchGitHub` for actual usage |

### `web-research` (dated, source-cited)

| Question type | When |
|---|---|
| Current industry trends, recent releases (≤6 months) | News-velocity topics |
| Security advisories, CVEs, vendor announcements | Date-sensitive security signals |
| Comparative product / framework evaluation | Reputable sources only |
| Standards updates (RFCs, language specs, official changelogs) | Authoritative bodies |

Use `tech-research` (MCP) when authoritative answer exists in docs/code. Use `web-research` when topic is news / current events / advisories.

### `ry-explore` (deep multi-source, opus[1m])

Escalate to `ry-explore` agent (via `/rldyour-explore:ry-explore <topic>` slash command, OR by spawning subagent) when:

- Question requires synthesis across **multiple authoritative sources** with cross-validation.
- Decision must be backed by exact citations (vendor docs SHA, version, section anchor, repo path).
- Topic spans technical + industry + production-usage dimensions.
- Verification depth matters more than speed.

Agent runs in **forked context** (`context: fork` in slash command) - isolated context window per invocation prevents polluting main session.

## ry-explore Agent Workflow (strict order)

### Phase 1 - MCP-first (Context7 → DeepWiki → Grep)

1. **Context7** for official docs and API reference. `resolve-library-id` to map name → library, then `query-docs` for content. Pull exact section anchors and version numbers.
2. **DeepWiki** for open-source repo architecture, module layout, design rationale, evolution. Use whenever question is "how does project X organize / approach Y".
3. **Grep** (grep.app) for real-world code patterns at scale across GitHub. Use when question is "how do production codebases actually do this", or to find idiomatic vs obsolete patterns.

Pull exact quotes, file paths, version numbers, section anchors. Track which source said what - every claim must cite.

### Phase 2 - Web validation (only if MCP gaps remain)

WebFetch / WebSearch with dated, version-qualified queries. Prefer authoritative domains (vendor blogs, RFCs, security advisories, official changelogs, standards bodies). Cross-reference dated info between independent sources.

### Phase 3 - Synthesis

- Tag every finding with confidence: **Confirmed** / **Strongly supported** / **Inferred**.
- Cite exact source - `<library>@<version>`, repo path + SHA, doc section anchor, URL with publication date.
- Distinguish documentation claims from real-world code observations.
- Flag version-specific behaviour with explicit version numbers.
- Reply in Russian when user wrote in Russian; citations stay in original language.

## Cross-Validation Rule

For **critical claims** (architecture decisions, dependency choices, security implications, breaking changes), require **≥2 independent sources** confirming the claim. Surface contradictions when they appear - do not hide them.

Examples of critical claims:
- "Library X's API changed in version Y" → confirm via Context7 + Grep production code samples.
- "Anthropic plugins use pattern Z" → confirm via DeepWiki repo architecture + Grep cross-check.
- "v2.1.139 added feature W" → confirm via Anthropic changelog + plugin example.

## Agent Frontmatter Highlights

```yaml
name: ry-explore
model: opus[1m]              # canonical bracketed form for Opus 4.7 1M context (CC v2.1.111+)
effort: max
maxTurns: 90                 # generous for MCP-rich research
tools:                       # explicit allowlist (no wildcards for write-capable servers)
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - WebSearch
  - mcp__plugin_rldyour-mcps_serena__find_symbol
  - mcp__plugin_rldyour-mcps_serena__find_referencing_symbols
  - mcp__plugin_rldyour-mcps_serena__find_implementations
  - mcp__plugin_rldyour-mcps_serena__find_declaration
  - mcp__plugin_rldyour-mcps_serena__get_symbols_overview
  - mcp__plugin_rldyour-mcps_serena__search_for_pattern
  - mcp__plugin_rldyour-mcps_serena__read_file
  - mcp__plugin_rldyour-mcps_serena__list_dir
  - mcp__plugin_rldyour-mcps_serena__find_file
  - mcp__plugin_rldyour-mcps_serena__list_memories
  - mcp__plugin_rldyour-mcps_serena__read_memory
  - mcp__plugin_rldyour-mcps_serena__get_current_config
  - mcp__plugin_rldyour-mcps_serena__get_diagnostics_for_file
  - mcp__plugin_rldyour-mcps_serena__check_onboarding_performed
  - mcp__plugin_rldyour-mcps_context7__*
  - mcp__plugin_rldyour-mcps_deepwiki__*
  - mcp__plugin_rldyour-mcps_grep__*
color: cyan
```

## Slash Command

```
/rldyour-explore:ry-explore <topic>
```

Frontmatter uses `context: fork` + `agent: ry-explore` so each invocation gets a fresh isolated context window. Pass full self-contained prompt (the subagent has no access to main session history).

## Anti-Patterns

- Single-source claims for critical decisions (mandatory cross-validation).
- Mixing inferences with confirmed facts without explicit labels.
- Ignoring contradictions between docs and code - surface them, don't hide.
- Using `web-research` when an MCP server has the authoritative answer.
- Generic "best practice" lists without dated, named sources.
- Treating opinionated blogs as facts - cite as opinion explicitly.
- Old information without flagging publication date if older than 6 months.

## Invariants

- `rldyour-explore` plugin: 2 skills + 1 agent + 1 slash command, 0 hooks. Dependencies: `rldyour-mcps` only.
- `tech-research` and `web-research` are auto-invokable (no `disable-model-invocation`).
- `ry-explore` agent uses `context: fork` for context isolation.
- Every critical claim cites exact source (library@version, repo+SHA, doc section, URL+date).
- `ry-explore` is the **only** rldyour agent on `model: opus[1m]` + `effort: max` + `maxTurns: 90`.

## Change Rules

- Bump Context7 / DeepWiki / Grep MCP version: update `plugins/rldyour-mcps/.mcp.json` + `config/mcp-runtime-versions.env` + run `bash scripts/smoke_mcp_capabilities.sh --server <name>`.
- Modify `ry-explore` agent: requires plugin version bump (frontmatter change triggers cache refresh) per [[CLAUDECODE-01-PLUGIN-CANON]].
- Update `READ_ONLY_BY_DESIGN_MCPS` set in `scripts/validate_agent_tools.py` if context7/deepwiki/grep upstream adds write-class tools ([[TECHDEBT-01-NOW]] R4 prevention).

## Verification

- `bash scripts/smoke_mcp_capabilities.sh --server context7` (skipped if `CONTEXT7_API_KEY` unset).
- `bash scripts/smoke_mcp_capabilities.sh --server deepwiki` (HTTP, no env needed).
- `bash scripts/smoke_mcp_capabilities.sh --server grep` (HTTP, no env needed).
- `python3 scripts/validate_agent_tools.py`: proves `ry-explore` allowlist enforces read-only-by-design invariant.
- Manual: invoke `/rldyour-explore:ry-explore <small test topic>` and verify subagent produces dated, cited findings.

## Cross-References

- Quality-first verification gates: [[PHILOSOPHY-01-QUALITY-FIRST]] (cross-validation rule).
- MCP transport for context7/deepwiki/grep: [[MCP-01-TRANSPORT]].
- Canonical agent frontmatter pattern: [[PATTERNS-01-CANONICAL]] (tools allowlist).
- Subagent matrix: [[CLAUDECODE-01-PLUGIN-CANON]] Subagent Frontmatter Matrix.
- Open risk R4 (read-only-by-design MCP wildcards): [[TECHDEBT-01-NOW]].
