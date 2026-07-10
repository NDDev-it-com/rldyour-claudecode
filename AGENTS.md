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
  tracked-context_branch: tracked-context
  plugin_count: 11
  skill_count: 39
  command_count: 12
  subagent_count: 8
-->

## Source Of Truth

- `.claude-plugin/marketplace.json` is the marketplace manifest.
- `plugins/*/.claude-plugin/plugin.json` are per-plugin manifests.
- `plugins/rldyour-mcps/.mcp.json` is the single MCP transport owner and
  currently pins Sequential Thinking MCP `2026.7.4` and Context7 MCP `3.2.3`.
- `plugins/rldyour-flow/hooks/hooks.json`,
  `plugins/rldyour-serena-mcp/hooks/hooks.json`, and
  `plugins/rldyour-rtk/hooks/hooks.json` are the only hook owners.
- `config/rldyour-contract.json` and `docs/contract-matrix.md` define the
  cross-tool contract.
- `references/claude-baseline.json`, `package.json`, and
  `config/mcp-runtime-versions.env` pin Claude Code `2.1.206`.

## Native Boundaries

- Use Claude Code plugin, skill, slash-command, subagent, hook, MCP, and LSP
  surfaces only.
- Do not copy Codex, OpenCode, or Gemini-native command/config syntax into this
  adapter except as explicitly marked comparison notes.
- Every browser action first runs exact
  `$HOME/.local/bin/cloakbrowser-cdp-health` and fails closed as `NOT_PROVEN`.
  Execution is limited to exact `$HOME/.local/bin/playwright-cli` and the
  adapter-configured managed Chrome DevTools MCP transport. `webwright-task`
  is compatibility routing only; the Webwright runtime and all browser
  fallbacks are forbidden.
- cmux orchestration is terminal-session-only. Claude subagents are not cmux
  orchestrators.

## Hook Lifecycle

| Event | Owner | Script | Timeout |
|---|---|---|---|
| Stop | rldyour-flow | `hooks/stop_lifecycle_dispatcher.sh` | 45s |

The single registered Claude Stop hook is the Flow dispatcher above. Stop hooks
are advisory enforcement gates. They compute sync state and block with guidance;
the main workflow performs memory sync, validation, commits, pushes, and
git synchronization. `rldyour-rtk` additionally owns a `PreToolUse` Bash hook
(`hooks/rtk_rewrite.sh` -> `rtk hook claude`, 10s) that transparently rewrites
supported shell commands through rtk for token-economy and degrades to a no-op
passthrough when rtk is absent.

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
