# AGENTS.md - rldyour-claudecode

rldyour AI CLI configuration for Claude Code: plugin marketplace, MCP/LSP,
Serena memory, SDLC flow, browser/design workflows, security review, and
reviewer agents. This repository contains Claude Code-native plugin metadata,
skills, slash commands, subagents, hooks, scripts, docs, and references; it has
no runtime application service.

This file is a system file for the Claude Code install surface. It is
tracked on `main` so that `git clone` followed by the Claude install
script (or Claude Code's own `.claude/CLAUDE.md` discovery) picks it up
without depending on the `tracked-context` overlay. The companion file
`.claude/CLAUDE.md` is also tracked on main for the same reason.

Canonical public description: rldyour AI CLI configuration for Claude Code: plugin marketplace, MCP/LSP, Serena memory, security review, browser/design workflows, and reviewer agents.

<!-- sync_contract:
claims:
  mcp_owner: rldyour-mcps
  hook_owners: [rldyour-flow, rldyour-serena-mcp]
  lsp_owner: rldyour-lsps
  reviewer_transport_marker: RLDYOUR_REPORT_EOF
  reviewer_report_dir_template: ".serena/reviews/<run_id>/"
  reviewer_run_id_format: "<UTC-ISO-compact>-<git-short-sha>"
  claude_code_runtime_pin: "2.1.195"
  claude_code_feature_floor: "2.1.146"
  skill_listing_budget_fraction: 0.04
  max_skill_description_chars: 1536
  tracked-context_branch: tracked-context
  plugin_count: 10
  skill_count: 38
  command_count: 11
  subagent_count: 8
-->

## Source Of Truth

- `.claude-plugin/marketplace.json` is the marketplace manifest.
- `plugins/*/.claude-plugin/plugin.json` are per-plugin manifests.
- `plugins/rldyour-mcps/.mcp.json` is the single MCP transport owner.
- `plugins/rldyour-flow/hooks/hooks.json` and
  `plugins/rldyour-serena-mcp/hooks/hooks.json` are the only hook owners.
- `config/rldyour-contract.json` and `docs/contract-matrix.md` define the
  cross-tool contract.
- `references/claude-baseline.json`, `package.json`, and
  `config/mcp-runtime-versions.env` pin Claude Code `2.1.195`.

## Native Boundaries

- Use Claude Code plugin, skill, slash-command, subagent, hook, MCP, and LSP
  surfaces only.
- Do not copy Codex, OpenCode, or Gemini-native command/config syntax into this
  adapter except as explicitly marked comparison notes.
- Browser routing stays global: Webwright for long-horizon workflows,
  Playwright CLI for low-level screenshots/snapshots/traces, and Chrome
  DevTools MCP for DevTools/performance/network/console/memory/Lighthouse.
- cmux orchestration is terminal-session-only. Claude subagents are not cmux
  orchestrators.

## Hook Lifecycle

| Event | Owner | Script | Timeout |
|---|---|---|---|
| Stop | rldyour-flow | `hooks/stop_lifecycle_dispatcher.sh` | 45s |

The single registered Claude Stop hook is the Flow dispatcher above. Stop hooks
are advisory enforcement gates. They compute sync state and block with guidance;
the main workflow performs memory sync, validation, commits, pushes, and
git synchronization.

## Validation

Run after changes:

```bash
python3 scripts/validate_plugin_versions.py
python3 scripts/validate_contract.py
python3 scripts/validate_release_state.py
python3 scripts/validate_instruction_docs.py --require-agent-docs
python3 scripts/validate_claude_surface_adoption.py
uv run --with pytest --with pyyaml python -m pytest -q
```

## Tracked context Policy

`.serena/project.yml` and the rest of the `.serena/` agent context are restored
and published through `tracked-context`. `AGENTS.md` and `.claude/CLAUDE.md` are tracked
system instruction files on `main` (see the top of this file); only the
`.serena/` durable AI context is excluded from `main`.
