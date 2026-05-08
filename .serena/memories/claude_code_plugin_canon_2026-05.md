# Claude Code Plugin Canon — verified May 2026

Source-backed facts cross-validated against `code.claude.com/docs/en/plugins-reference`,
`code.claude.com/docs/en/mcp`, `code.claude.com/docs/en/changelog`, and Anthropic's own
`claude-plugins-official` repo. Last refresh 2026-05-08 via ry-explore deep research.

Last commit: 2ace4a0 (feat/auto-stop-pipeline, 2026-05-08). Verification range: v2.1.111-v2.1.135.

## plugin.json schema

Top-level fields documented in canonical schema (`plugins-reference#metadata-fields`):
- Required: `name` (kebab-case).
- Metadata: `$schema`, `version`, `description`, `author{name,email,url}`, `homepage`, `repository`, `license`, `keywords`.
- Component overrides: `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`.
- Experimental: `experimental.themes`, `experimental.monitors`.
- Other: `userConfig`, `channels`, **`dependencies`**.

`dependencies` is an array. Mixed forms allowed:
```json
"dependencies": ["helper-lib", { "name": "secrets-vault", "version": "~2.1.0" }]
```
Anthropic docs link: `code.claude.com/docs/en/plugin-dependencies`.

`$schema` URL — both forms accepted: `https://anthropic.com/claude-code/plugin.schema.json`
(Anthropic-internal) and `https://json.schemastore.org/claude-code-plugin-manifest.json`
(SchemaStore — **canonical per docs example**, used in this repo since 2631322).
Claude Code ignores `$schema` at load time; recognized by `claude plugin validate`
since v2.1.120.

`experimental.themes` and `experimental.monitors` — top-level still works but
`claude plugin validate` warns since v2.1.129; future release will require
the `experimental` wrapper.

If both marketplace entry and `plugin.json` set `version`, plugin.json wins.

## .mcp.json schema (per-server)

stdio: `command` (required), `args[]`, `env{}`, `cwd`, optional `type: "stdio"`.
HTTP: `type: "http"`, `url`, `headers{}`, `oauth{}`.
SSE: `type: "sse"`, `url`, `headers{}`. Documented as deprecated; prefer HTTP.

`startup_timeout_sec` and `tool_timeout_sec` are NOT in the documented Claude Code
.mcp.json schema. Silently ignored; do not add them. Verified by:
- `code.claude.com/docs/en/mcp` (no mention)
- `code.claude.com/docs/en/plugins-reference` (no mention)
- Anthropic's own plugin manifests in `claude-plugins-official` (do not use them)
- DeepWiki on `anthropics/claude-code` (confirms not honored)

Canonical timeout/output env vars:
- `MCP_TIMEOUT` — server startup timeout (e.g. `MCP_TIMEOUT=10000 claude`).
- `MCP_TOOL_TIMEOUT` — per-tool-call timeout.
- `MAX_MCP_OUTPUT_TOKENS` — raises 10k-token tool-output warning.
- `MCP_CONNECTION_NONBLOCKING=1` — non-blocking startup; per-server `alwaysLoad: true`
  (v2.1.121+) opts back into blocking with a 5s connect cap.

Reconnection: 5 attempts exponential backoff (1s start, doubling) for HTTP/SSE.
Initial connection: 3 retries on transient errors (5xx / connection refused / timeout)
since v2.1.121.

## Skills (SKILL.md frontmatter)

- `name` (max 64 chars, kebab-case; defaults to directory name).
- `description` — combined with `when_to_use` and truncated at **1,536 chars** in the listing.
- `when_to_use` — appended to description; counts toward the 1,536 cap.
- `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`,
  `allowed-tools`, `model`, `effort`, `context: fork`, `agent`, `hooks`, `paths`, `shell`.

Triggering budget: defaults to 1% of context window with 8,000-char fallback,
overridable via `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var (raw chars).

Settings.json keys (v2.1.129+):
- `skillListingBudgetFraction` — decimal `(0..1]`, validator rejects integers/`>1`.
  Default 0.01. Recommended: 0.02 for 25-50 skills, 0.03 for 50-75, 0.05 for 75-125.
- `skillListingMaxDescChars` — per-entry cap. Default **1,536** (raised from 250 in v2.1.128).

`skillOverrides` map (v2.1.129+ stable) — 4 states: `"on" | "name-only" |
"user-invocable-only" | "off"`. **Does not affect plugin-shipped skills** —
manage those through `/plugin` instead.

After auto-compaction: 5,000 tokens kept per skill, 25,000 tokens combined budget
for re-attached skills (filled most-recent-first; older skills can be dropped).

Custom commands have been merged into skills: `.claude/commands/foo.md` and
`.claude/skills/foo/SKILL.md` both create `/foo`. New code should use skills.

## Subagents

Required: `name`, `description`. Optional: `tools`, `disallowedTools`, `model`,
`permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`,
`background`, `effort`, `isolation`, `color`, `initialPrompt`.

`model` accepts: `sonnet`, `opus`, `haiku`, `inherit`, full IDs like
`claude-opus-4-7`, plus the `[1m]` bracket suffix (`opus[1m]`, `claude-opus-4-7[1m]`)
for the 1M-token context window. Requires Claude Code **v2.1.111+**.

`effort`: `low|medium|high|xhigh|max`. Opus 4.7 supports all five; Opus 4.6 / Sonnet 4.6
silently downgrade `xhigh` to `high`.

`color`: `red|blue|green|yellow|purple|orange|pink|cyan`.

**Plugin-shipped subagents** silently ignore `hooks`, `mcpServers`, `permissionMode`
for security. Use `.claude/agents/` or `~/.claude/agents/` if you need them.

`isolation: "worktree"` creates a temporary git worktree for the agent.

## Slash commands

Same frontmatter as SKILL.md (commands have been merged into skills).

Production caveat (verified in `move-hoon/claude-pro-minmax`): `model:` field
in slash command frontmatter only takes effect when paired with `context: fork`.
A bare `model: opus[1m]` without `context: fork` is silently ignored. Either
pair them or use `agent: <name>` and let the named agent's `model:` win.

## Hooks events (May 2026 canonical, 30 events)

Session: `SessionStart`, `Setup`, `SessionEnd`.
Per-turn: `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`.
Tool loop: `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`,
`PostToolUseFailure`, `PostToolBatch`.
Subagents/tasks: `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`,
`TeammateIdle`.
Config/env: `ConfigChange`, `InstructionsLoaded`, `CwdChanged`, `FileChanged`.
Context: `PreCompact`, `PostCompact`.
Worktree: `WorktreeCreate`, `WorktreeRemove`.
MCP: `Elicitation`, `ElicitationResult`.
Notifications: `Notification`.

Hook handler types: `command`, `http`, `mcp_tool` (v2.1.118+), `prompt`, `agent`.
Universal fields: `type`, `command|url|server+tool|prompt`, `if` (only on tool
events), `timeout` (defaults: command 600s, prompt 30s, agent 60s), `statusMessage`,
`once`. Command hooks add `async`, `asyncRewake`, `shell`. Prompt/agent handlers
spawn LLM evaluation or full subagent verification.

Hierarchy precedence (highest → lowest): managed policy → plugin hooks (force-enabled
exempt from `allowManagedHooksOnly`) → `.claude/settings.json` → `.claude/settings.local.json`
→ `~/.claude/settings.json` → skill/agent frontmatter.

Matchers: `*`/`""`/omitted match all; alphanumeric+`_`+`|` matches exact or list;
otherwise JS regex. Events without matcher support: `UserPromptSubmit`,
`PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`,
`WorktreeCreate`, `WorktreeRemove`, `CwdChanged`.

Exit codes: `0` success (stdout parsed for hookSpecificOutput JSON);
`2` blocking error (stderr fed to Claude); other = non-blocking error.

## Reserved marketplace names

`claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`,
`anthropic-marketplace`, `anthropic-plugins`, `agent-skills`,
`knowledge-work-plugins`, `life-sciences`. `rldyour-claude` is not reserved.

## CLI

`claude plugin validate <path>` — canonical CI command. Anthropic-recommended
pattern in CI: `npm install -g @anthropic-ai/claude-code` then
`claude plugin validate .` and per-plugin `claude plugin validate ./plugins/<name>/`.

Other CLI commands: `plugin install`, `uninstall` (`--keep-data`, `--prune`),
`enable`, `disable`, `update`, `list` (`--json`, `--available`), `prune` (v2.1.121+),
`tag` (v2.1.119+, `--push` validates plugin.json/marketplace agreement, refuses
dirty worktree or pre-existing tag), `marketplace add`. `/reload-plugins` (v2.1.116+)
reinstalls missing dependencies whose marketplace is configured.

Range-conflict reporting (4 error types): `dependency-unsatisfied`, `range-conflict`,
`dependency-version-unsatisfied`, `no-matching-tag`. Visible in `claude plugin list`,
`/plugin`, `/doctor`.

## Changelog highlights v2.1.111-v2.1.135

- v2.1.111 — `xhigh` effort for Opus 4.7; Auto mode for Max
- v2.1.115 — `MCP_CONNECTION_NONBLOCKING=true` for `-p` mode
- v2.1.116 — `/reload-plugins`; auto-update auto-installs missing deps
- v2.1.117 — fork mode; `plugin install` resolves missing deps
- v2.1.118 — `mcp_tool` hook handler; PreCompact block support; plugin themes
- v2.1.119 — `claude plugin tag --push`; `${ENV_VAR}` headers fix; `${CLAUDE_EFFORT}`
- v2.1.120 — `claude plugin validate` accepts `$schema`/`version`/`description` top-level
- v2.1.121 — `claude plugin prune`; MCP `alwaysLoad`; transient-error retry up to 3x
- v2.1.126 — Plugin force-enabled hooks respect `allowManagedHooksOnly`
- v2.1.128 — Skill listing per-entry cap raised 250 → 1,536 chars; truncation warning
- v2.1.129 — `skillOverrides` 4-state stable; `themes`/`monitors` → `experimental`;
  `effort.level` JSON for hooks
- v2.1.131 — Mantle endpoint auth fix
- v2.1.133 — `worktree.baseRef`; `parentSettingsBehavior`; `sandbox.bwrapPath`/`socatPath`

## Sources

- code.claude.com/docs/en/plugins-reference
- code.claude.com/docs/en/plugin-marketplaces
- code.claude.com/docs/en/skills
- code.claude.com/docs/en/sub-agents
- code.claude.com/docs/en/hooks
- code.claude.com/docs/en/mcp
- code.claude.com/docs/en/model-config
- github.com/anthropics/claude-plugins-official (verified production examples)
- DeepWiki Q&A on anthropics/claude-code (2026-05-07)
- Grep on github (`model: opus[1m]`, `context: fork`, etc. — production patterns)
