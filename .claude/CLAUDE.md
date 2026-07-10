# Claude Code Project Memory - rldyour-claudecode

This is the Claude Code-native deep memory for the rldyour Claude adapter.
Cross-tool overview lives in `AGENTS.md`; this file keeps Claude-specific
runtime, hook, subagent, and skill-budget facts concise.

<!-- sync_contract:
claims:
  mcp_owner: rldyour-mcps
  hook_owners: [rldyour-flow, rldyour-serena-mcp, rldyour-rtk]
  lsp_owner: rldyour-lsps
  reviewer_transport_marker: RLDYOUR_REPORT_EOF
  reviewer_report_dir_template: ".serena/reviews/<run_id>/"
  reviewer_run_id_format: "<UTC-ISO-compact>-<git-short-sha>"
  claude_code_runtime_pin: "2.1.206"
  claude_code_feature_floor: "2.1.146"
  managed_model_default: "opus[1m]"
  managed_env_defaults: "ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-8, BASH_DEFAULT_TIMEOUT_MS=600000, BASH_MAX_TIMEOUT_MS=1200000, CLAUDE_CODE_MAX_OUTPUT_TOKENS=80000"
  skill_listing_budget_fraction: 0.04
  max_skill_description_chars: 1536
  plugin_count: 11
  skill_count: 39
  command_count: 12
  subagent_count: 8
-->

## Runtime

Claude Code runtime pin is `2.1.206`. The compatibility floor is `2.1.146`.
The pin sources are `package.json`, `references/claude-baseline.json`, and
`config/mcp-runtime-versions.env`.

The current exact package pins are Sequential Thinking MCP `2026.7.4` and
Context7 MCP `3.2.3`. Claude reads their canonical stdio transports from
`plugins/rldyour-mcps/.mcp.json`; the env file is the CI parity companion.

## Plugin Inventory

- `rldyour-mcps`: MCP transport owner for 11 active MCP servers.
- `rldyour-serena-mcp`: Serena code workflow, memory sync, and lifecycle hooks.
- `rldyour-flow`: SDLC commands, reviewer agents, post-task sync, and Stop
  lifecycle dispatcher.
- `rldyour-orchestrator`: macOS cmux orchestrator/worker role skills only.
- `rldyour-explore`, `rldyour-security`, `rldyour-browser`, `rldyour-design`,
  `rldyour-lsps`, and `rldyour-rules`: domain plugins.
- `rldyour-rtk`: rtk token-economy core - guaranteed PreToolUse Bash hook,
  `token-economy` skill, and `/rtk-gain`.

Current inventory: 11 plugins, 39 skills, 12 slash commands, and 8 subagents.

## Hook Canon

`rldyour-flow`, `rldyour-serena-mcp`, and `rldyour-rtk` own hooks. Stop hooks are advisory
enforcement gates: they compute state and block with guidance, while the main
workflow performs memory sync, tests, commits, pushes, and release synchronization.
The single registered Claude Stop hook is the Flow dispatcher. `rldyour-rtk` owns a
`PreToolUse` Bash hook that rewrites supported commands through rtk for token-economy.

| Event | Owner | Script | Timeout |
|---|---|---|---|
| Stop | rldyour-flow | `hooks/stop_lifecycle_dispatcher.sh` | 45s |

## Reviewer Contract

Reviewer subagents use file-first output. Full reports go to
`.serena/reviews/<run_id>/<reviewer-name>.md`; parent-visible output stays
compact. The heredoc marker is `RLDYOUR_REPORT_EOF`.

## Skill Budget

Use `skillListingBudgetFraction: 0.04` and `maxSkillDescriptionChars: 1536` in
user Claude settings so bilingual skill descriptions remain discoverable.

## Boundaries

Claude subagents are not cmux orchestrators. Before every browser action they
must run exact `$HOME/.local/bin/cloakbrowser-cdp-health`; missing or nonzero
health stops the task as `NOT_PROVEN`. Browser execution is limited to exact
`$HOME/.local/bin/playwright-cli` and the adapter-configured managed Chrome
DevTools MCP transport. `webwright-task` is a compatibility route only; the
Webwright runtime and every alternate browser path or fallback are forbidden.
