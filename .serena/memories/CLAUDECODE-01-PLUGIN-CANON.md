<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 065d6a4 fix(security): close 6 findings from flow-security-review (F-1..F-6)
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
- Plugin-shipped subagents use frontmatter for `model`, `effort`, `maxTurns 90 (security 100, ry-explore 90)` in user settings. `0.04` (4%) is chosen over the Anthropic/claudekit-cli baseline `0.03` to accommodate bilingual Russian-leading + English-triggers descriptions averaging ~400 chars per entry across 32 skills (verified in `.claude/CLAUDE.md` line 82 at HEAD).
- `claude plugin tag --push` uses `<plugin-name>--v<version>` tag convention and refuses dirty worktrees or pre-existing tags. Available from v2.1.118+. Verified at `AGENTS.md` line 70 at HEAD `a506526`.
- `claude plugin details <name>` is available from v2.1.139+; v2.1.142 adds LSP visibility.
- Hook `if` filter (v2.1.118+) scopes Bash lifecycle hooks to specific git command patterns. Used in both `plugins/rldyour-flow/hooks/hooks.json` and `plugins/rldyour-serena-mcp/hooks/hooks.json` to avoid firing on every Bash call. Verified at both `hooks.json` files at HEAD `a506526` (commit `perf(hooks): scope Bash lifecycle hooks with if filters (v2.1.118+)`).
- JSON schema validation: 5 schemas in `config/schemas/` (`hooks.json`, `lsp.json`, `marketplace.json`, `mcp.json`, `plugin.json`). Enforced by `scripts/validate_json_schemas.py` (104 lines), wired into `scripts/validate_marketplace.sh`. Verified at HEAD `a506526` (commit `feat(config): add 5 JSON schemas + cc-canon + marketplace-policy`).
- `sync_contract` YAML block added to both `AGENTS.md` (line 9) and `.claude/CLAUDE.md` (line 5) at HEAD `a506526`. 14 shared claims enforced by `scripts/validate_instruction_sync.py` (reports 0 drift). Verified via `python3 scripts/validate_instruction_sync.py` at HEAD `a506526`.
- Additional validators wired into `scripts/validate_marketplace.sh`: `validate_docs_canon.py` (0 drift across 46 target files), `validate_text_hygiene.py`, `validate_skill_allowed_tools.py`, `validate_release_state.py`, `validate_instruction_sync.py`. `generate_inventory.py` is a standalone reporting script. Verified at HEAD `a506526` (commit `test(harness): add 6 validators`).
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
