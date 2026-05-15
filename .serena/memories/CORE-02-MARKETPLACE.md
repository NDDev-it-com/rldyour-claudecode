<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: aaaa0dd feat(serena-mcp): standardize memory taxonomy
Scope: .claude-plugin/marketplace.json, plugins/*/.claude-plugin/plugin.json, README.md, AGENTS.md
Area: CORE
-->

# CORE-02-MARKETPLACE

## Purpose

Current business logic and architecture of the `rldyour-claude` marketplace. The repo is a controlled personal Claude Code plugin marketplace, not runtime application code and not a generic preset.

## Source Of Truth

- `.claude-plugin/marketplace.json`: marketplace manifest with `pluginRoot: ./plugins` and nine first-party plugin entries.
- `plugins/<plugin>/.claude-plugin/plugin.json`: per-plugin manifest and dependency declaration.
- `README.md`: owner-facing catalog, control model, install/check commands, and active per-plugin versions.
- `AGENTS.md`: concise cross-tool project rules and boundaries.

## Current Behavior

- The active catalog has nine plugins, verified from `.claude-plugin/marketplace.json` at HEAD: `rldyour-mcps`, `rldyour-explore`, `rldyour-serena-mcp`, `rldyour-security`, `rldyour-browser`, `rldyour-design`, `rldyour-lsps`, `rldyour-flow`, `rldyour-rules`.
- Current per-plugin versions at HEAD: `rldyour-mcps` `0.1.3`; `rldyour-serena-mcp` `0.1.5`; all other plugins `0.1.2`.
- Component counts verified at HEAD: 32 skills, 9 slash commands, 8 subagents, and 2 plugin hook manifests.
- The owner decides what is enabled. Repository docs state that nothing is treated as enabled or correct unless explicitly decided by the owner.

## Plugin Boundaries

- `rldyour-mcps`: single owner of MCP transport through `plugins/rldyour-mcps/.mcp.json`.
- `rldyour-serena-mcp`: Serena-first code workflow, memory sync, and four lifecycle hooks.
- `rldyour-flow`: SDLC orchestration, reviewer agents, post-task sync, fullrepo/worktree flow, and three hooks.
- `rldyour-explore`: technical and web research workflows.
- `rldyour-security`: OWASP-oriented implementation guidance and defensive security review.
- `rldyour-browser`: browser validation/debug/routing skills.
- `rldyour-design`: Figma/design-system/FSD workflows and depends on `rldyour-browser` for validation routing.
- `rldyour-lsps`: LSP routing, setup, health checks, and Serena LSP integration.
- `rldyour-rules`: quality, architecture, implementation, dependency, verification, docs, and review rules.

## Contracts And Data

- Cross-plugin dependencies are declared in `plugin.json` as a `dependencies` array of plugin names.
- `rldyour-flow` depends on both `rldyour-mcps` and `rldyour-serena-mcp`.
- All consumer plugins depend on `rldyour-mcps`; `rldyour-design` also depends on `rldyour-browser`.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`.
- Only `rldyour-mcps` declares `.mcp.json`.
- One plugin owns one domain. Cross-plugin overlap and catch-all plugins are forbidden.

## Change Rules

- When plugin manifests or marketplace entries change, update `.claude-plugin/marketplace.json`, the relevant `plugin.json`, `README.md`, `CHANGELOG.md`, and this memory if behavior or versions changed.
- Do not introduce another `.mcp.json` owner or another hook-owning plugin without changing the architecture contract.
- Keep per-plugin version bumps scoped to the plugin whose runtime cache must refresh.

## Verification

- `python3 scripts/validate_plugin_versions.py`: verifies marketplace entry versions match `plugin.json` versions.
- `bash scripts/validate_marketplace.sh`: validates marketplace, per-plugin manifests, frontmatter, shell/Python syntax, routing policy, and MCP version drift.
- `claude plugin validate .` and `claude plugin validate plugins/<name>`: canonical Claude Code manifest validation.
