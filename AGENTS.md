# AGENTS.md - rldyour-claudecode

rldyour AI CLI configuration for Claude Code: plugin marketplace, MCP/LSP,
Serena memory, SDLC flow, browser/design workflows, security review, and
reviewer agents. This repository contains Claude Code-native plugin metadata,
skills, slash commands, subagents, hooks, scripts, docs, and references; it has
no runtime application service.

This file is agent-only context. It is published through `fullrepo`, excluded
from normal `main`, and remains subordinate to current source files, tests,
configuration, git state, and live GitHub state.

<!-- sync_contract:
claims:
  mcp_owner: rldyour-mcps
  hook_owners: [rldyour-flow, rldyour-serena-mcp]
  lsp_owner: rldyour-lsps
  reviewer_transport_marker: RLDYOUR_REPORT_EOF
  reviewer_report_dir_template: ".serena/reviews/<run_id>/"
  reviewer_run_id_format: "<UTC-ISO-compact>-<git-short-sha>"
  claude_code_runtime_pin: "2.1.175"
  claude_code_feature_floor: "2.1.146"
  skill_listing_budget_fraction: 0.04
  max_skill_description_chars: 1536
  fullrepo_branch: fullrepo
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
  `config/mcp-runtime-versions.env` pin Claude Code `2.1.175`.

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

## Fullrepo Policy

`AGENTS.md`, `.claude/CLAUDE.md`, and `.serena/project.yml` are restored and
published through `fullrepo`. Normal `main` must not track these agent-only
files.
