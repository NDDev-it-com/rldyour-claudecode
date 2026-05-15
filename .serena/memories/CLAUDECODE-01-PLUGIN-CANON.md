<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: 70c8d91 fix(serena-mcp): harden memory taxonomy gates
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
- Plugin manifests use SchemaStore `$schema` URLs, but Claude Code validates actual fields through its own plugin validator.
- `dependencies` in `plugin.json` are plugin names. The repo enforces marketplace/manifest version alignment through `scripts/validate_plugin_versions.py`.
- Skills are the primary routing surface; descriptions are Russian-leading with English triggers appended.
- Plugin-shipped subagents use frontmatter for `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, and `color`.
- Hook exit code `2` is the blocking advisory path. Stop hooks in this repo use `exit 2` to force orchestrator action while avoiding direct high-blast-radius operations.
- `analyze_sync_scope.py` targets `CLAUDECODE-01-PLUGIN-CANON.md` for plugin manifest, hook, skill, command, agent, marketplace-support, and agent-instruction changes.

## Contracts And Data

- Minimum Claude Code compatibility floor is `v2.1.111+` for the `opus[1m]` extended-context syntax used by `ry-explore`; `[1m]` availability remains account/plan dependent.
- Local verified Claude Code range in project instructions is `v2.1.111-v2.1.142`.
- Claude Code hook canon recorded in `.claude/CLAUDE.md`: 29 events, five handler types (`command`, `http`, `mcp_tool`, `prompt`, `agent`), and hook hierarchy precedence.
- Skill listing mitigation recorded in `.claude/CLAUDE.md`: `skillListingBudgetFraction: 0.03` and `skillListingMaxDescChars: 1536` in user settings.
- `claude plugin tag --push` uses `<plugin-name>--v<version>` tag convention and refuses dirty worktrees or pre-existing tags.
- `claude plugin details <name>` is available from v2.1.139+; v2.1.142 adds LSP visibility.
- Official Claude Code MCP docs still show the GitHub remote MCP endpoint as an example; this repository uses stdio `github-mcp-server` as a local policy because live verification found Copilot entitlement 403 for the owner account class.

## Invariants

- Keep Claude Code-deep facts in `.claude/CLAUDE.md`; keep cross-tool concise rules in `AGENTS.md`.
- Do not reduce `.claude/CLAUDE.md` to only `@AGENTS.md`; both are first-class and optimized for different CLIs.
- Do not add undocumented `.mcp.json` keys such as `startup_timeout_sec` or `tool_timeout_sec`; use documented env vars where needed.
- When current Claude Code behavior changes, update `.claude/CLAUDE.md`, relevant plugin docs, and this memory from verified docs or runtime evidence.

## Verification

- `bash scripts/validate_marketplace.sh`: validates plugin manifests, skill/agent/command frontmatter, and the Serena taxonomy smoke.
- `python3 scripts/validate_instruction_docs.py --require-agent-docs`: validates `AGENTS.md` and `.claude/CLAUDE.md` presence and line budgets.
- `claude plugin validate .`: validates marketplace manifest through the Claude Code CLI.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies that plugin component and agent-instruction changes target this memory.
