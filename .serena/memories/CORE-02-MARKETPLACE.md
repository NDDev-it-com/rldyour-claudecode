<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 6b59af7 fix(security): explicit https/http scheme guard in fetch_json
Scope: .claude-plugin/marketplace.json, plugins/*/.claude-plugin/plugin.json, README.md, AGENTS.md
Area: CORE
-->

# CORE-02-MARKETPLACE

## Purpose

Current business logic and architecture of the `rldyour-claude` marketplace. The repo is a controlled personal Claude Code plugin marketplace, **not** runtime application code and **not** a generic preset. It distributes the Claude Code settings, skills, agents, hooks, scripts, and references that encode the owner's quality-first development style ([[PHILOSOPHY-01-QUALITY-FIRST]]).

## Source Of Truth

- `.claude-plugin/marketplace.json`: marketplace manifest with `pluginRoot: ./plugins` and nine first-party plugin entries.
- `plugins/<plugin>/.claude-plugin/plugin.json`: per-plugin manifest and dependency declaration.
- `VERSION`: marketplace release boundary.
- `README.md`: owner-facing catalog, control model, install/check commands, active per-plugin versions.
- `AGENTS.md`: concise cross-tool project rules and boundaries.

## Current State (HEAD `a506526`)

- **VERSION**: `0.3.0` (release boundary, verified at `VERSION` file at HEAD `a506526`).
- **9 plugins** verified at HEAD from `.claude-plugin/marketplace.json`: `rldyour-mcps`, `rldyour-explore`, `rldyour-serena-mcp`, `rldyour-security`, `rldyour-browser`, `rldyour-design`, `rldyour-lsps`, `rldyour-flow`, `rldyour-rules`.
- **Per-plugin versions** (verified via `python3 scripts/validate_plugin_versions.py` at HEAD `a506526`): all 9 plugins at `0.3.0`.
- **Component totals**: 32 skills, 9 slash commands, 8 subagents, 8 hook scripts in 2 hook manifests, 12 plugin-owned scripts, 16 references.
- The owner decides what is enabled. Repository docs state nothing is treated as enabled or correct unless explicitly decided by the owner.

## Plugin Boundaries + Domain Memory Pointers

| Plugin | Domain | Components | Hook owner | Domain memory |
|---|---|---|---|---|
| `rldyour-mcps` | Transport - 13 pinned MCP servers | 0 skills, 0 cmds, 0 agents, 0 hooks, `.mcp.json` | No | [[MCP-01-TRANSPORT]] |
| `rldyour-serena-mcp` | Serena-first code workflow + fact-only memory sync | 2 skills, 0 cmds, 1 agent, 4 hooks, 3 scripts | **Yes** | [[SERENA-01-MEMORY-SYNC]] + [[HOOKS-01-LIFECYCLE]] |
| `rldyour-flow` | SDLC orchestration + 6 reviewer subagents + fullrepo/worktree | 7 skills, 5 cmds, 6 agents, 4 hooks, 7 scripts, 7 references | **Yes** | [[FLOW-01-SDLC]] + [[HOOKS-01-LIFECYCLE]] |
| `rldyour-explore` | Deep research (tech + web + `ry-explore` opus[1m]) | 2 skills, 1 cmd, 1 agent, 0 hooks | No | [[EXPLORE-01-RESEARCH]] |
| `rldyour-security` | OWASP Top 10 2025 + Mythos-style `ry-sec-review` | 2 skills, 1 cmd, 0 agents, 0 hooks | No | [[SECURITY-01-OWASP]] |
| `rldyour-browser` | Playwright + Chrome DevTools validation/debug routing | 3 skills, 0 cmds, 0 agents, 0 hooks | No | [[BROWSER-01-WORKFLOW]] |
| `rldyour-design` | Figma → tokens → FSD → shadcn/ui → ReactBits → validation | 5 skills, 1 cmd, 0 agents, 0 hooks | No | [[DESIGN-01-WORKFLOW]] |
| `rldyour-lsps` | 16 LSP servers + Serena integration + health-check + install | 4 skills, 0 cmds, 0 agents, 0 hooks, 2 scripts, 3 references | No | [[LSPS-01-LANGUAGE-SERVERS]] |
| `rldyour-rules` | 7 rule areas + 6 references + `ry-rules-review` auditor | 7 skills, 1 cmd, 0 agents, 0 hooks, 6 references | No | [[RULES-01-POLICY]] |

## Dependency Graph

```
rldyour-mcps (base; no dependencies)
├── rldyour-serena-mcp
│   └── rldyour-flow
├── rldyour-explore
├── rldyour-security
├── rldyour-browser
│   └── rldyour-design
├── rldyour-lsps
└── rldyour-rules
```

Cross-plugin dependencies declared in `plugin.json` `dependencies` array of plugin names. All consumer plugins depend on `rldyour-mcps` (base transport layer). `rldyour-flow` additionally depends on `rldyour-serena-mcp` (memory sync). `rldyour-design` additionally depends on `rldyour-browser` (validation routing).

## Hard Architectural Invariants

- **One domain per plugin**. Cross-plugin overlap and catch-all plugins are forbidden.
- **Only `rldyour-mcps` declares `.mcp.json`**. No other plugin owns MCP transport.
- **Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`**. No other plugin attaches Claude Code lifecycle hooks.
- **Skills-only plugins**: `rldyour-browser`, `rldyour-design`, `rldyour-lsps`, `rldyour-security`, `rldyour-rules`. They consume transport from `rldyour-mcps` and do not introduce their own.
- **`rldyour-design` depends on `rldyour-browser`** for validation routing.
- **`rldyour-flow` depends on `rldyour-serena-mcp`** for memory sync coordination.

## Workflow Chains (Business Logic)

### `ry-init` (read-only scope discovery)
1. `bash plugins/rldyour-flow/scripts/git_sync_audit.sh` - git/branch/worktree state.
2. `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init` - restore agent-only context from `fullrepo`.
3. Serena-first inspection: `check_onboarding_performed` → `list_memories` → `read_memory` → `get_symbols_overview` → `find_symbol` → `find_referencing_symbols` → `search_for_pattern`.
4. Russian context-pack report per `plugins/rldyour-flow/references/init-context-pack.md`.

### `ry-start` (full task lifecycle)
1. Scoped `ry-init` if context missing.
2. Research via `rldyour-explore` ([[EXPLORE-01-RESEARCH]]) for unclear technology.
3. Pass `context-sufficiency-gate.md` before editing.
4. Detailed plan verified against code via Serena.
5. Branch/worktree, atomic Conventional Commits, progress checkpoints every 2-3 plan groups.
6. Quality gates via `rldyour-rules/skills/verification-quality-gates` ([[RULES-01-POLICY]]).
7. Trigger workflows by change type: `browser-validation` for UI, `ry-sec-review` for security-sensitive, `ry-design` for design.
8. **Review phase**: parallel reviewer subagents (`flow-architecture-review`, `flow-quality-review`, `flow-consistency-review`, `flow-integration-review`, `flow-verification-review`, `flow-security-review`).
9. **Finalize**: `flow-post-task-sync` synchronizes Serena memories ([[SERENA-01-MEMORY-SYNC]]) → agent-only files → AGENTS.md/CLAUDE.md → git → GitHub → fullrepo → branch/worktree cleanup → optional `claude plugin tag --push`.

### Memory sync lifecycle ([[SERENA-01-MEMORY-SYNC]] + [[HOOKS-01-LIFECYCLE]])
1. `prepare_auto_sync.sh` (PreToolUse:Bash) - record `.serena/.auto_sync_head` before commit-like Bash.
2. `mark_sync_required.sh` (PostToolUse:Bash) - write `.serena/.serena_sync_state.json` after commit-like commands when sync-relevant files changed.
3. `stop_memory_sync.sh` (Stop, exit 2) - block stop if memories stale; advisory points at `flow-memory-sync` subagent (canonical writer).
4. `flow-memory-sync` subagent - fact-only memory updates with anti-hallucination contract.
5. `commit_serena_knowledge.sh` - clear runtime markers when memories match HEAD.

### Fullrepo lifecycle ([[FLOW-01-SDLC]])
1. `fullrepo_sync.py --bootstrap-init` - install excludes, restore remote `fullrepo`, publish first snapshot when missing, migrate tracked agent-only files.
2. `fullrepo_sync.py --restore` - fetch and restore agent-only files from `origin/fullrepo`.
3. `fullrepo_sync.py --migrate-main` - `git rm --cached` tracked agent-only files; worktree files survive.
4. `fullrepo_sync.py --publish` - push snapshot tree to `fullrepo` with `--force-with-lease`.
5. `fullrepo_sync.py --status-json` - machine-readable state.

Agent-only paths (not in `main`, only in `fullrepo`): `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `.claude/**`, `.cursor/rules/**`, `.gemini/**`, `.roo/**`, `.windsurf/**`, `.openhands/**`, `.aider*`, `.agents/skills/**`, `.agents/commands/**`, `.agents/hooks/**`, `.github/copilot-instructions.md`, `.github/instructions/**`, `.github/prompts/**`, `.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`, `.serena/research/**`, `.serena/newproj/**`, `.serena/deploy/**`.

## Change Rules

- When plugin manifests or marketplace entries change: update `.claude-plugin/marketplace.json` + relevant `plugin.json` + `README.md` + `CHANGELOG.md` + this memory if behaviour or versions changed.
- Do not introduce another `.mcp.json` owner or another hook-owning plugin without changing the architecture contract.
- Keep per-plugin version bumps scoped to the plugin whose runtime cache must refresh (SKILL.md/agent.md/hooks.json/.mcp.json changes trigger refresh; script body changes do not).
- Adding new plugin: confirm domain boundary, declare dependencies in `plugin.json`, add marketplace entry, write or extend domain memory.

## Verification

- `python3 scripts/validate_plugin_versions.py`: verifies marketplace entry versions match `plugin.json` versions.
- `python3 scripts/validate_agent_tools.py`: verifies agent `tools:` allowlists ([[TECHDEBT-01-NOW]] R4 mitigation).
- `bash scripts/validate_marketplace.sh`: validates marketplace, per-plugin manifests, frontmatter, shell/Python syntax, routing policy, MCP version drift, agent tools allowlist, Serena memory taxonomy smoke.
- `claude plugin validate .` and `claude plugin validate plugins/<name>`: canonical Claude Code manifest validation.

## Cross-References

- Vision and philosophy: [[PHILOSOPHY-01-QUALITY-FIRST]].
- Canonical implementation patterns: [[PATTERNS-01-CANONICAL]].
- Memory taxonomy and reading intent map: [[CORE-01-INDEX]].
- Claude Code-specific frontmatter / hook / changelog facts: [[CLAUDECODE-01-PLUGIN-CANON]].
- Release process and CHANGELOG conventions: [[RELEASE-01-VALIDATION]].
- Open and closed technical debt: [[TECHDEBT-01-NOW]].
