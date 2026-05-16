<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: e5a7694 docs(flow): align reviewer-protocol terminology and flow-lifecycle
Scope: .claude/CLAUDE.md, AGENTS.md, plugins/*/.claude-plugin/plugin.json, plugins/rldyour-mcps/.mcp.json, plugins/*/skills/*/SKILL.md, plugins/*/agents/*.md, plugins/*/hooks/hooks.json, plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py
Area: CLAUDECODE
-->

# CLAUDECODE-01-PLUGIN-CANON

## Purpose

Current Claude Code plugin/runtime facts that this marketplace relies on. These facts are source-backed by Claude Code documentation and encoded in repository manifests, hooks, and instruction docs.

## Source Of Truth

- `.claude/CLAUDE.md`: Claude Code-native project memory with hook canon, subagent matrix, skill-listing budget, and changelog adoption notes.
- `AGENTS.md`: cross-tool project instructions and current Claude Code compatibility floor.
- `plugins/*/.claude-plugin/plugin.json`: plugin metadata and dependency declarations.
- `plugins/*/skills/*/SKILL.md`: skill frontmatter and trigger descriptions.
- `plugins/*/agents/*.md`: subagent frontmatter and tool permissions.
- `plugins/rldyour-flow/hooks/hooks.json` and `plugins/rldyour-serena-mcp/hooks/hooks.json`: hook declarations.
- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: analyzer mapping that targets this memory for plugin component and Claude Code instruction contract changes.

## Current Behavior

- `claude plugin validate` is the canonical manifest validator and is run through `scripts/validate_marketplace.sh`.
- Agent `tools:` allowlist invariants are enforced by `scripts/validate_agent_tools.py` (added Wave 2, commit `b4234c2`), wired unconditionally into `scripts/validate_marketplace.sh` at line 117. The script enforces: (1) built-in tool names in `KNOWN_BUILTIN_TOOLS`; (2) MCP pattern `mcp__plugin_<plugin>_<server>__<tool>` references real plugins and servers; (3) wildcards (`__*`) for non-Serena MCP servers must be in `READ_ONLY_BY_DESIGN_MCPS` (`context7`, `deepwiki`, `grep`, `semgrep`); (4) `SERVERS_WITH_WRITE_TOOLS` (`serena`) must use explicit tool lists, not wildcards, in read-only agent frontmatter. This is the canonical deterministic enforcement point for the TECHDEBT-01-NOW R4 invariant.
- Plugin manifests use SchemaStore `$schema` URLs, but Claude Code validates actual fields through its own plugin validator.
- `dependencies` in `plugin.json` are plugin names. The repo enforces marketplace/manifest version alignment through `scripts/validate_plugin_versions.py`.
- Skills are the primary routing surface; descriptions are Russian-leading with English triggers appended.
- Plugin-shipped subagents use frontmatter for `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, and `color`. The canonical pattern (per `anthropics/claude-plugins-official/plugins/pr-review-toolkit/agents/code-reviewer`) is an explicit `tools:` allowlist; `disallowedTools:` remains as defence-in-depth legacy (used by `flow-memory-sync` only). Verified at `plugins/rldyour-flow/agents/flow-architecture-review.md` and `plugins/rldyour-serena-mcp/agents/flow-memory-sync.md` at HEAD.
- Hook exit code `2` is the blocking advisory path. Stop hooks in this repo use `exit 2` to force orchestrator action while avoiding direct high-blast-radius operations.
- `analyze_sync_scope.py` targets `CLAUDECODE-01-PLUGIN-CANON.md` for plugin manifest, hook, skill, command, agent, marketplace-support, and agent-instruction changes.
- Reviewer output transport in `plugins/rldyour-flow` is file-first: every `flow-*` reviewer writes a full markdown report to `<report_dir>/<reviewer-name>.md` using heredoc marker `RLDYOUR_REPORT_EOF`, then returns a compact summary (counts + capped one-liners) to avoid Claude Code `task.output` truncation/overflow regressions documented in Anthropic issues [#16789](https://github.com/anthropics/claude-code/issues/16789), [#20531](https://github.com/anthropics/claude-code/issues/20531), [#23463](https://github.com/anthropics/claude-code/issues/23463).
- `plugins/rldyour-flow/fullrepo_sync.py` keeps `.serena/diagnostics/**` and `.serena/reviews/**` in `RUNTIME_EXCLUDE_PATTERNS` to keep reviewer runtime artifacts from entering restore/publish workflows that use this pattern set.

## Contracts And Data

- Minimum Claude Code compatibility floor is `v2.1.111+` for the `opus[1m]` extended-context syntax used by `ry-explore`; `[1m]` availability remains account/plan dependent.
- Local verified Claude Code range in project instructions is `v2.1.111-v2.1.143`.
- Claude Code hook canon recorded in `.claude/CLAUDE.md`: 29 events, five handler types (`command`, `http`, `mcp_tool`, `prompt`, `agent`), and hook hierarchy precedence.
- Skill listing mitigation recorded in `.claude/CLAUDE.md`: `skillListingBudgetFraction: 0.04` and `skillListingMaxDescChars: 1536` in user settings. `0.04` (4%) is chosen over the Anthropic/claudekit-cli baseline `0.03` to accommodate bilingual Russian-leading + English-triggers descriptions averaging ~400 chars per entry across 32 skills (verified in `.claude/CLAUDE.md` line 82 at HEAD).
- `claude plugin tag --push` uses `<plugin-name>--v<version>` tag convention and refuses dirty worktrees or pre-existing tags.
- `claude plugin details <name>` is available from v2.1.139+; v2.1.142 adds LSP visibility.
- Official Claude Code MCP docs still show the GitHub remote MCP endpoint as an example; this repository uses local stdio `github-mcp-server` to keep the marketplace self-contained without dependence on `api.githubcopilot.com/mcp/`. A standard GitHub PAT with `repo` + `read:org` scopes is sufficient; no Copilot subscription is required. Rationale source: `plugins/rldyour-mcps/README.md` line 28 at HEAD.
- Repository transferred from `rldyourmnd/rldyour-claude` to `NDDev-it-com/rldyour-claudecode` (private) in Wave 5. Marketplace slug renamed from `rldyour-claude` to `rldyour-claudecode` in `.claude-plugin/marketplace.json`. All 9 plugin `plugin.json` files updated with new `homepage` and `repository` URLs pointing to `github.com/nddev-it-com/rldyour-claudecode`. Local origin remote is now `git@github.com:NDDev-it-com/rldyour-claudecode.git`. Verified at `.claude-plugin/marketplace.json` and `plugins/rldyour-mcps/.claude-plugin/plugin.json` at HEAD `334fe09`.

## Invariants

- Keep Claude Code-deep facts in `.claude/CLAUDE.md`; keep cross-tool concise rules in `AGENTS.md`.
- Do not reduce `.claude/CLAUDE.md` to only `@AGENTS.md`; both are first-class and optimized for different CLIs.
- Do not add undocumented `.mcp.json` keys such as `startup_timeout_sec` or `tool_timeout_sec`; use documented env vars where needed.
- When current Claude Code behavior changes, update `.claude/CLAUDE.md`, relevant plugin docs, and this memory from verified docs or runtime evidence.
- Reviewer protocol hardening is treated as a compatibility-sensitive convention: any change to marker text, report directory paths, severity enums, or required orchestrator reads must update `reviewer-protocol.md`, `flow-*` skills, and this memory atomically.

## Cross-References

- Marketplace plugin boundaries and dependency graph: [[CORE-02-MARKETPLACE]].
- MCP server registry (13 pinned servers): [[MCP-01-TRANSPORT]].
- Hook lifecycle canon: [[HOOKS-01-LIFECYCLE]].
- Memory sync agent (flow-memory-sync frontmatter): [[SERENA-01-MEMORY-SYNC]].
- Instruction docs policy: [[DOCS-01-INSTRUCTIONS]].
- Agent tools patterns (explicit allowlist): [[PATTERNS-01-CANONICAL]] Agent Frontmatter.
- Open risks (R4 wildcard, R5 divergence): [[TECHDEBT-01-NOW]].
- Release validation (validate_marketplace.sh): [[RELEASE-01-VALIDATION]].

## Verification

- `bash scripts/validate_marketplace.sh`: validates plugin manifests, skill/agent/command frontmatter, and the Serena taxonomy smoke.
- `python3 scripts/validate_instruction_docs.py --require-agent-docs`: validates `AGENTS.md` and `.claude/CLAUDE.md` presence and line budgets.
- `claude plugin validate .`: validates marketplace manifest through the Claude Code CLI.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies that plugin component and agent-instruction changes target this memory.
