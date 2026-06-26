# Claude Code Project Memory - rldyour-claudecode

This is the Claude Code-native deep memory for the rldyour Claude adapter.
Cross-tool overview lives in `AGENTS.md`; this file keeps Claude-specific
runtime, hook, subagent, and skill-budget facts concise.

<!-- sync_contract:
claims:
  mcp_owner: rldyour-mcps
  hook_owners: [rldyour-flow, rldyour-serena-mcp]
  lsp_owner: rldyour-lsps
  reviewer_transport_marker: RLDYOUR_REPORT_EOF
  reviewer_report_dir_template: ".serena/reviews/<run_id>/"
  reviewer_run_id_format: "<UTC-ISO-compact>-<git-short-sha>"
  claude_code_runtime_pin: "2.1.193"
  claude_code_feature_floor: "2.1.146"
  skill_listing_budget_fraction: 0.04
  max_skill_description_chars: 1536
  plugin_count: 10
  skill_count: 38
  command_count: 11
  subagent_count: 8
-->

## Runtime

Claude Code runtime pin is `2.1.193`. The compatibility floor is `2.1.146`.
The pin sources are `package.json`, `references/claude-baseline.json`, and
`config/mcp-runtime-versions.env`.

## Plugin Inventory

- `rldyour-mcps`: MCP transport owner for 11 active MCP servers.
- `rldyour-serena-mcp`: Serena code workflow, memory sync, and lifecycle hooks.
- `rldyour-flow`: SDLC commands, reviewer agents, post-task sync, and Stop
  lifecycle dispatcher.
- `rldyour-orchestrator`: macOS cmux orchestrator/worker role skills only.
- `rldyour-explore`, `rldyour-security`, `rldyour-browser`, `rldyour-design`,
  `rldyour-lsps`, and `rldyour-rules`: domain plugins.

Current inventory: 10 plugins, 38 skills, 11 slash commands, and 8 subagents.

## Hook Canon

Only `rldyour-flow` and `rldyour-serena-mcp` own hooks. Stop hooks are advisory
enforcement gates: they compute state and block with guidance, while the main
workflow performs memory sync, tests, commits, pushes, and release synchronization.
The single registered Claude Stop hook is the Flow dispatcher.

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

Claude subagents are not cmux orchestrators. Webwright, Playwright CLI, and
Chrome DevTools MCP keep their global browser-provider roles. Configure only
providers listed in the approved active inventory and avoid tool-specific
negative validator tombstones.
